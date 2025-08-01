from datetime import datetime
from datetime import date as DateType
from typing import Optional, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field, JSON, Column


class EventType(str, Enum):
    # User Events
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PROFILE_UPDATED = "profile_updated"
    PROFILE_VIEWED = "profile_viewed"
    
    # Opportunity Events
    OPPORTUNITY_CREATED = "opportunity_created"
    OPPORTUNITY_PUBLISHED = "opportunity_published"
    OPPORTUNITY_VIEWED = "opportunity_viewed"
    OPPORTUNITY_APPLIED = "opportunity_applied"
    OPPORTUNITY_BOOKMARKED = "opportunity_bookmarked"
    
    # Application Events
    APPLICATION_SUBMITTED = "application_submitted"
    APPLICATION_REVIEWED = "application_reviewed"
    APPLICATION_ACCEPTED = "application_accepted"
    APPLICATION_REJECTED = "application_rejected"
    APPLICATION_WITHDRAWN = "application_withdrawn"
    
    # Communication Events
    MESSAGE_SENT = "message_sent"
    MESSAGE_READ = "message_read"
    CONVERSATION_STARTED = "conversation_started"
    
    # Search Events
    SEARCH_PERFORMED = "search_performed"
    FILTER_APPLIED = "filter_applied"
    SEARCH_RESULT_CLICKED = "search_result_clicked"
    
    # Engagement Events
    REVIEW_CREATED = "review_created"
    SKILL_VERIFIED = "skill_verified"
    BADGE_EARNED = "badge_earned"
    
    # System Events
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_MEASURED = "performance_measured"


class AnalyticsEventBase(SQLModel):
    # Event Information
    event_type: EventType = Field(index=True)
    event_name: str = Field(index=True)
    
    # User Context
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    session_id: Optional[str] = Field(index=True)
    
    # Event Data
    properties: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Context
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Device and Location
    device_type: Optional[str] = None  # mobile, desktop, tablet
    browser: Optional[str] = None
    os: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    
    # A/B Testing
    experiment_id: Optional[str] = None
    variant_id: Optional[str] = None
    
    # Additional metadata
    event_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON))


class AnalyticsEvent(AnalyticsEventBase, table=True):
    __tablename__ = "analytics_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsEventCreate(SQLModel):
    event_type: EventType
    event_name: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    properties: Dict[str, Any] = {}
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    event_metadata: Dict[str, Any] = {}


# Aggregated Analytics Data
class DailyStatsBase(SQLModel):
    date: DateType = Field(index=True)
    
    # User Metrics
    new_users: int = Field(default=0)
    active_users: int = Field(default=0)
    returning_users: int = Field(default=0)
    
    # Volunteer Metrics
    new_volunteers: int = Field(default=0)
    active_volunteers: int = Field(default=0)
    
    # Organization Metrics
    new_organizations: int = Field(default=0)
    active_organizations: int = Field(default=0)
    
    # Opportunity Metrics
    opportunities_created: int = Field(default=0)
    opportunities_published: int = Field(default=0)
    opportunities_viewed: int = Field(default=0)
    opportunities_applied: int = Field(default=0)
    
    # Application Metrics
    applications_submitted: int = Field(default=0)
    applications_accepted: int = Field(default=0)
    applications_rejected: int = Field(default=0)
    
    # Engagement Metrics
    messages_sent: int = Field(default=0)
    profiles_viewed: int = Field(default=0)
    searches_performed: int = Field(default=0)
    reviews_created: int = Field(default=0)
    
    # Success Metrics
    successful_matches: int = Field(default=0)
    completed_opportunities: int = Field(default=0)
    
    # Additional metrics
    custom_data: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON))


class DailyStats(DailyStatsBase, table=True):
    __tablename__ = "daily_stats"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# User Activity Tracking
class UserActivityBase(SQLModel):
    user_id: int = Field(foreign_key="users.id", index=True)
    date: DateType = Field(index=True)
    
    # Activity Counts
    sessions: int = Field(default=0)
    page_views: int = Field(default=0)
    time_spent_minutes: int = Field(default=0)
    
    # Actions Performed
    opportunities_viewed: int = Field(default=0)
    applications_submitted: int = Field(default=0)
    messages_sent: int = Field(default=0)
    searches_performed: int = Field(default=0)
    profiles_viewed: int = Field(default=0)
    
    # Last Activity
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    last_page: Optional[str] = None
    
    # Device Information
    primary_device: Optional[str] = None
    browsers_used: Dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))


class UserActivity(UserActivityBase, table=True):
    __tablename__ = "user_activity"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# Performance Metrics
class PerformanceMetricBase(SQLModel):
    metric_name: str = Field(index=True)
    metric_type: str = Field(index=True)  # response_time, error_rate, throughput, etc.
    
    # Metric Values
    value: float
    unit: str  # ms, %, req/s, etc.
    
    # Context
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    
    # Environment
    environment: str = Field(default="production")
    version: Optional[str] = None
    
    # Additional data
    tags: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    stats_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON))


class PerformanceMetric(PerformanceMetricBase, table=True):
    __tablename__ = "performance_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)