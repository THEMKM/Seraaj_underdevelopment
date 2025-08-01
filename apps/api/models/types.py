"""
Central Type Registry for Seraaj Models

This module serves as the single source of truth for:
1. Common field definitions
2. Model relationship definitions
3. Base model mixins
4. Validation constants

Architecture Notes:
- Provides reusable field definitions
- Defines standard model relationships
- Includes common model mixins
- Centralizes validation logic
"""

from typing import TYPE_CHECKING, Dict, Any, Optional, ForwardRef
from datetime import datetime
from uuid import uuid4

from pydantic import constr
from sqlmodel import SQLModel, Field, Column, JSON, Relationship

# === Forward References ===
if TYPE_CHECKING:
    # Payment imports removed - not part of MVP
    pass
    # Temporarily disable push notification imports due to relationship configuration issues
    # from .push_notification import PushSubscription, PushNotification, NotificationSettings

UserRef = ForwardRef("User")
OrganisationRef = ForwardRef("Organisation")
OpportunityRef = ForwardRef("Opportunity")
ApplicationRef = ForwardRef("Application")
ReviewRef = ForwardRef("Review")
# Payment references removed - not part of MVP
MessageRef = ForwardRef("Message")
ConversationRef = ForwardRef("Conversation")
VolunteerRef = ForwardRef("Volunteer")
GuidedTourRef = ForwardRef("GuidedTour")
TourStepRef = ForwardRef("TourStep")
UserTourProgressRef = ForwardRef("UserTourProgress")
# Temporarily disable push notification ForwardRefs due to relationship configuration issues
# PushSubscriptionRef = ForwardRef("PushSubscription")
# PushNotificationRef = ForwardRef("PushNotification")
# NotificationSettingsRef = ForwardRef("NotificationSettings")


# === Common Fields ===
def id_field() -> Any:
    return Field(default=None, primary_key=True)


def created_at_field() -> Any:
    return Field(default_factory=datetime.utcnow)


def updated_at_field() -> Any:
    return Field(default_factory=datetime.utcnow)


def json_field() -> Any:
    return Field(default_factory=dict, sa_column=Column(JSON))


def rating_field() -> Any:
    return Field(default=None, ge=1, le=5)


def email_field() -> Any:
    return Field(unique=True, index=True)


def description_field() -> Any:
    return Field(max_length=2000)


def title_field() -> Any:
    return Field(max_length=200)


def priority_field() -> Any:
    return Field(default=0, ge=0, le=100)


# === Base Model Mixins ===
class TimestampMixin(SQLModel):
    """Adds created_at and updated_at fields"""

    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()


class SoftDeleteMixin(SQLModel):
    """Adds soft delete capability"""

    deleted_at: Optional[datetime] = Field(default=None)
    is_deleted: bool = Field(default=False, index=True)


class UUIDMixin(SQLModel):
    """Adds UUID field"""

    uuid: uuid4 = Field(default_factory=uuid4, unique=True, index=True)


class UserCreatedMixin(SQLModel):
    """Tracks user who created the record"""

    created_by_id: Optional[int] = Field(
        default=None, foreign_key="users.id", index=True
    )


# === Relationship Definitions ===
def relationship_field(
    *,
    back_populates: Optional[str] = None,
    link_model: Optional[str] = None,
    sa_relationship_kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """Create a relationship field with proper configuration"""
    kwargs = {"back_populates": back_populates} if back_populates else {}
    if link_model:
        kwargs["link_model"] = link_model
    if sa_relationship_kwargs:
        kwargs["sa_relationship_kwargs"] = sa_relationship_kwargs
    return Relationship(**kwargs)


def list_relationship_field(
    *,
    back_populates: Optional[str] = None,
    link_model: Optional[str] = None,
    sa_relationship_kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """Create a relationship field for lists with proper configuration"""
    kwargs = {"back_populates": back_populates} if back_populates else {}
    if link_model:
        kwargs["link_model"] = link_model
    if sa_relationship_kwargs:
        kwargs["sa_relationship_kwargs"] = sa_relationship_kwargs
    return Field(default_factory=list, sa_relationship=Relationship(**kwargs))


# === Common Relationship Patterns ===
def one_to_many_relation(back_populates: str) -> Any:
    """Create a one-to-many relationship field"""
    return list_relationship_field(back_populates=back_populates)


def many_to_one_relation(back_populates: str) -> Any:
    """Create a many-to-one relationship field"""
    return relationship_field(
        back_populates=back_populates, sa_relationship_kwargs={"uselist": False}
    )


def many_to_many_relation(back_populates: str, link_model: str) -> Any:
    """Create a many-to-many relationship field"""
    return list_relationship_field(back_populates=back_populates, link_model=link_model)


# === Specific Relationship Patterns ===
def user_relation(back_populates: str, *, multiple: bool = False) -> Any:
    """Create a relationship to User"""
    return (one_to_many_relation if multiple else many_to_one_relation)(back_populates)


def organisation_relation(back_populates: str, *, multiple: bool = False) -> Any:
    """Create a relationship to Organisation"""
    return (one_to_many_relation if multiple else many_to_one_relation)(back_populates)


def opportunity_relation(back_populates: str, *, multiple: bool = False) -> Any:
    """Create a relationship to Opportunity"""
    return (one_to_many_relation if multiple else many_to_one_relation)(back_populates)


def application_relation(back_populates: str, *, multiple: bool = False) -> Any:
    """Create a relationship to Application"""
    return (one_to_many_relation if multiple else many_to_one_relation)(back_populates)


def tour_relation(back_populates: str, *, multiple: bool = False) -> Any:
    """Create a relationship to GuidedTour"""
    return (one_to_many_relation if multiple else many_to_one_relation)(back_populates)


# === Validation Constants ===
PASSWORD_MIN_LENGTH = 8
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
DESCRIPTION_MAX_LENGTH = 2000
TITLE_MAX_LENGTH = 200
PHONE_REGEX = r"^\+?1?\d{9,15}$"
USERNAME_REGEX = r"^[a-zA-Z0-9_-]+$"


# === Common Validators ===
def get_password_validator() -> Any:
    return constr(min_length=PASSWORD_MIN_LENGTH)


def get_phone_validator() -> Any:
    return constr(regex=PHONE_REGEX)


def get_username_validator() -> Any:
    return constr(
        regex=USERNAME_REGEX,
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
    )


# Export commonly used elements
__all__ = [
    # Forward References
    "UserRef",
    "OrganisationRef",
    "OpportunityRef",
    "ApplicationRef",
    "ReviewRef",
    "MessageRef",
    "ConversationRef",
    "VolunteerRef",
    "GuidedTourRef",
    "TourStepRef",
    "UserTourProgressRef",
    # Temporarily disabled: 'PushSubscriptionRef', 'PushNotificationRef', 'NotificationSettingsRef',
    # Field Functions
    "id_field",
    "created_at_field",
    "updated_at_field",
    "json_field",
    "rating_field",
    "email_field",
    "description_field",
    "title_field",
    "priority_field",
    # Model Mixins
    "TimestampMixin",
    "SoftDeleteMixin",
    "UUIDMixin",
    "UserCreatedMixin",
    # Relationship Functions
    "relationship_field",
    "list_relationship_field",
    "one_to_many_relation",
    "many_to_one_relation",
    "many_to_many_relation",
    "user_relation",
    "organisation_relation",
    "opportunity_relation",
    "application_relation",
    "tour_relation",
    # Validator Functions
    "get_password_validator",
    "get_phone_validator",
    "get_username_validator",
    # Constants
    "PASSWORD_MIN_LENGTH",
    "USERNAME_MIN_LENGTH",
    "USERNAME_MAX_LENGTH",
    "DESCRIPTION_MAX_LENGTH",
    "TITLE_MAX_LENGTH",
    "PHONE_REGEX",
    "USERNAME_REGEX",
]
