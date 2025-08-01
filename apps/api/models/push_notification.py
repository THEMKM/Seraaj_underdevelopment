"""
Push notification models for Seraaj
"""
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
import uuid

if TYPE_CHECKING:
    from .user import User


class NotificationType(str, Enum):
    """Types of push notifications"""
    OPPORTUNITY_MATCH = "opportunity_match"
    APPLICATION_UPDATE = "application_update"
    MESSAGE_RECEIVED = "message_received"
    DEADLINE_REMINDER = "deadline_reminder"
    SCHEDULE_UPDATE = "schedule_update"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    DONATION_RECEIVED = "donation_received"
    VOLUNTEER_JOINED = "volunteer_joined"
    REVIEW_REQUEST = "review_request"
    SKILL_VERIFIED = "skill_verified"


class NotificationPriority(str, Enum):
    """Priority levels for notifications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Status of notification delivery"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CLICKED = "clicked"
    DISMISSED = "dismissed"


class PlatformType(str, Enum):
    """Push notification platforms"""
    WEB_PUSH = "web_push"
    FCM_ANDROID = "fcm_android"
    APNS_IOS = "apns_ios"
    WEB_SOCKET = "web_socket"


class PushSubscription(SQLModel, table=True):
    """Push notification subscriptions for users"""
    __tablename__ = "push_subscriptions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # User relationship
    user_id: int = Field(foreign_key="users.id", index=True)
    user: "User" = Relationship(back_populates="push_subscriptions")
    
    # Platform and subscription details
    platform: PlatformType
    endpoint: str = Field(index=True)
    p256dh_key: Optional[str] = None
    auth_key: Optional[str] = None
    
    # Device information
    device_type: str = Field(default="unknown")  # browser, mobile, tablet
    device_name: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Subscription settings
    is_active: bool = Field(default=True)
    notifications_enabled: bool = Field(default=True)
    
    # Notification preferences
    notification_types: List[NotificationType] = Field(default_factory=list, sa_column=Column(JSON))
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "08:00"
    timezone: str = Field(default="UTC")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None
    
    # Relationships - Note: List type should not be used for table relationships in SQLModel
    notifications: List["PushNotification"] = Relationship(back_populates="subscription")


class PushNotification(SQLModel, table=True):
    """Push notifications sent to users"""
    __tablename__ = "push_notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # User and subscription
    user_id: int = Field(foreign_key="users.id", index=True)
    user: "User" = Relationship(back_populates="push_notifications")
    
    subscription_id: Optional[int] = Field(foreign_key="push_subscriptions.id")
    subscription: Optional["PushSubscription"] = Relationship(back_populates="notifications")
    
    # Notification content
    title: str
    body: str
    icon: Optional[str] = Field(default="/static/icons/notification-icon.png")
    image: Optional[str] = None
    badge: Optional[str] = Field(default="/static/icons/badge-icon.png")
    
    # Notification metadata
    notification_type: NotificationType
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)
    
    # Action buttons
    actions: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    
    # Delivery settings
    click_action: Optional[str] = None  # URL to open when clicked
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Scheduling
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Status tracking
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    
    # Error tracking
    error_message: Optional[str] = None
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationTemplate(SQLModel, table=True):
    """Templates for different types of notifications"""
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: str = Field(unique=True, index=True)
    
    # Template details
    notification_type: NotificationType
    name: str
    description: Optional[str] = None
    
    # Template content (supports variables like {user_name}, {opportunity_title})
    title_template: str
    body_template: str
    icon: Optional[str] = None
    
    # Default settings
    default_priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)
    default_actions: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    
    # Personalization
    variables: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Status
    is_active: bool = Field(default=True)
    
    # Metadata  
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationSettings(SQLModel, table=True):
    """User notification preferences"""
    __tablename__ = "notification_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User relationship
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    user: "User" = Relationship(back_populates="notification_settings")
    
    # Global settings
    push_notifications_enabled: bool = Field(default=True)
    email_notifications_enabled: bool = Field(default=True)
    in_app_notifications_enabled: bool = Field(default=True)
    
    # Notification type preferences
    opportunity_matches: bool = Field(default=True)
    application_updates: bool = Field(default=True)
    messages: bool = Field(default=True)
    deadlines: bool = Field(default=True)
    schedule_changes: bool = Field(default=True)
    system_announcements: bool = Field(default=True)
    donations: bool = Field(default=True)
    volunteer_activity: bool = Field(default=True)
    reviews: bool = Field(default=True)
    skill_verifications: bool = Field(default=True)
    
    # Timing preferences
    quiet_hours_enabled: bool = Field(default=False)
    quiet_hours_start: str = Field(default="22:00")
    quiet_hours_end: str = Field(default="08:00")
    timezone: str = Field(default="UTC")
    
    # Frequency settings
    digest_enabled: bool = Field(default=False)
    digest_frequency: str = Field(default="weekly")  # daily, weekly, monthly
    digest_day: Optional[str] = None  # monday, tuesday, etc.
    digest_time: str = Field(default="09:00")
    
    # Platform preferences
    mobile_notifications: bool = Field(default=True)
    desktop_notifications: bool = Field(default=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationDeliveryLog(SQLModel, table=True):
    """Log of notification delivery attempts"""
    __tablename__ = "notification_delivery_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Notification reference
    notification_id: int = Field(foreign_key="push_notifications.id", index=True)
    
    # Delivery details
    platform: PlatformType
    attempt_number: int = Field(default=1)
    status: NotificationStatus
    
    # Response details
    response_code: Optional[int] = None
    response_message: Optional[str] = None
    delivery_time_ms: Optional[int] = None
    
    # Error information
    error_type: Optional[str] = None
    error_details: Optional[str] = None
    
    # Metadata
    attempted_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationAnalytics(SQLModel, table=True):
    """Analytics data for notification performance"""
    __tablename__ = "notification_analytics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Time period
    date: datetime = Field(index=True)
    hour: int = Field(default=0)  # 0-23
    
    # Notification details
    notification_type: NotificationType
    platform: PlatformType
    priority: NotificationPriority
    
    # Metrics
    sent_count: int = Field(default=0)
    delivered_count: int = Field(default=0)
    clicked_count: int = Field(default=0)
    dismissed_count: int = Field(default=0)
    failed_count: int = Field(default=0)
    
    # Performance metrics
    avg_delivery_time_ms: Optional[float] = None
    click_through_rate: Optional[float] = None
    delivery_rate: Optional[float] = None
    
    # User engagement
    unique_users_reached: int = Field(default=0)
    new_subscriptions: int = Field(default=0)
    unsubscriptions: int = Field(default=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Create indexes for better query performance
def create_push_notification_indexes():
    """Create database indexes for push notifications"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_push_subscription_user_platform ON push_subscriptions(user_id, platform);",
        "CREATE INDEX IF NOT EXISTS idx_push_notification_user_type ON push_notifications(user_id, notification_type);",
        "CREATE INDEX IF NOT EXISTS idx_push_notification_status_created ON push_notifications(status, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_notification_settings_user ON notification_settings(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_notification_analytics_date_type ON notification_analytics(date, notification_type);",
        "CREATE INDEX IF NOT EXISTS idx_delivery_log_notification_platform ON notification_delivery_logs(notification_id, platform);"
    ]
    return indexes


# Export commonly used types
NotificationTypeChoices = [choice.value for choice in NotificationType]
NotificationPriorityChoices = [choice.value for choice in NotificationPriority]
PlatformTypeChoices = [choice.value for choice in PlatformType]