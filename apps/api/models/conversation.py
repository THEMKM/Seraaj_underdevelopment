from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON, Relationship

from .types import (
    TimestampMixin, id_field,
    UserRef, MessageRef, OpportunityRef, ApplicationRef
)

if TYPE_CHECKING:
    from .user import User
    from .message import Message
    from .opportunity import Opportunity
    from .application import Application


class ConversationType(str, Enum):
    DIRECT = "direct"  # Between volunteer and organization
    GROUP = "group"    # Team conversations
    SUPPORT = "support"  # Customer support


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    DELETED = "deleted"


class ConversationBase(SQLModel):
    # Basic Info
    title: Optional[str] = None
    type: ConversationType = Field(default=ConversationType.DIRECT)
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE, index=True)
    
    # Participants
    participant_ids: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    created_by: int = Field(foreign_key="users.id")
    
    # Activity Tracking
    last_message_at: Optional[str] = None  # ISO format datetime string
    last_message_preview: Optional[str] = None
    last_message_sender_id: Optional[int] = None
    
    # Message Stats
    total_messages: int = Field(default=0)
    
    # Related Context
    related_opportunity_id: Optional[int] = Field(default=None, foreign_key="opportunities.id")
    related_application_id: Optional[int] = Field(default=None, foreign_key="applications.id")
    
    # Settings
    settings: dict = Field(default_factory=dict, sa_column=Column(JSON))
    entity_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))


class Conversation(ConversationBase, TimestampMixin, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = id_field()
    
    # Message/Conversation system relationships - restored systematically
    creator: "User" = Relationship(back_populates="created_conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
    related_opportunity: Optional["Opportunity"] = Relationship(back_populates="conversations")
    related_application: Optional["Application"] = Relationship(back_populates="conversations")


class ConversationCreate(ConversationBase):
    pass


class ConversationRead(ConversationBase):
    id: int
    created_at: str  # ISO format datetime string
    updated_at: Optional[str] = None  # ISO format datetime string


class ConversationUpdate(SQLModel):
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None
    settings: Optional[dict] = None
    entity_metadata: Optional[dict] = None


# Model for tracking read status per user
class ConversationParticipant(SQLModel, table=True):
    __tablename__ = "conversation_participants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Read Status
    last_read_at: Optional[str] = None  # ISO format datetime string
    last_read_message_id: Optional[int] = None
    unread_count: int = Field(default=0)
    
    # Participant Settings
    muted: bool = Field(default=False)
    notifications_enabled: bool = Field(default=True)
    
    # Activity
    joined_at: str  # ISO format datetime string
    left_at: Optional[str] = None  # ISO format datetime string
    
    # Timestamps
    created_at: str  # ISO format datetime string
    updated_at: Optional[str] = None  # ISO format datetime string