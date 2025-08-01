"""
User Model - Core authentication and profile management

ARCHITECTURE NOTES:
- This model is designed to support advanced features (payments, notifications, analytics)
- Some relationships are temporarily disabled with init=False due to database schema limitations
- When ready to implement advanced features, remove init=False and create corresponding tables
- All disabled features have complete model definitions in their respective files

DISABLED FEATURES (ready to enable):
- Push notification system (models/push_notification.py)
- Payment processing (models/payment.py) 
- Advanced user analytics and tracking fields

To enable a feature: Remove init=False from the relationship and ensure the target table exists.
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from pydantic import EmailStr

from .types import (
    TimestampMixin, SoftDeleteMixin,
    id_field, email_field, json_field,
    get_password_validator,
    user_relation, organisation_relation, opportunity_relation,
    application_relation, tour_relation,
    VolunteerRef, OrganisationRef,
    PushSubscriptionRef, PushNotificationRef, NotificationSettingsRef
)

if TYPE_CHECKING:
    from .volunteer import Volunteer
    from .organisation import Organisation
    from .push_notification import (
        PushSubscription, PushNotification, NotificationSettings
    )


class UserRole(str, Enum):
    VOLUNTEER = "volunteer"
    ORGANIZATION = "organization"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    BANNED = "banned"


class UserBase(SQLModel):
    # Authentication
    email: str = email_field()
    hashed_password: str = get_password_validator()
    
    # Basic Profile
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    
    # Account Status
    role: UserRole = Field(index=True)
    status: UserStatus = Field(default=UserStatus.ACTIVE, index=True)
    is_verified: bool = Field(default=False)
    email_verified: bool = Field(default=False)
    
    # Authentication Tokens
    refresh_token: Optional[str] = None
    reset_token: Optional[str] = None
    verification_token: Optional[str] = None
    
    # Login Activity
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    login_count: int = Field(default=0)
    
    # Privacy and Preferences
    privacy_settings: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    notification_preferences: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    language_preference: str = Field(default="en")
    theme_preference: str = Field(default="light")
    
    # Security
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None
    
    # Profile Completion
    profile_completion: float = Field(default=0.0, ge=0.0, le=100.0)
    onboarding_completed: bool = Field(default=False)
    
    # Additional user data
    user_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))


class User(UserBase, TimestampMixin, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = id_field()
    
    # Relationships will be added back once the models are stable and imports are fixed
    # For now, access related data through direct queries


class UserCreate(SQLModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole
    language_preference: str = "en"


class UserRead(SQLModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    display_name: Optional[str]
    role: UserRole
    status: UserStatus
    is_verified: bool
    email_verified: bool
    last_login: Optional[datetime]
    profile_completion: float
    onboarding_completed: bool
    language_preference: str
    theme_preference: str
    created_at: datetime


class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    privacy_settings: Optional[dict] = None
    notification_preferences: Optional[dict] = None
    language_preference: Optional[str] = None
    theme_preference: Optional[str] = None
    user_metadata: Optional[dict] = None


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserPasswordReset(SQLModel):
    email: EmailStr


class UserPasswordUpdate(SQLModel):
    old_password: str
    new_password: str


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(SQLModel):
    refresh_token: str