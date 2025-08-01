from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON, Relationship

from .types import (
    TimestampMixin, id_field,
    ConversationRef, UserRef
)

if TYPE_CHECKING:
    from .conversation import Conversation
    from .user import User


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    NOTIFICATION = "notification"


class MessageStatus(str, Enum):
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MessageBase(SQLModel):
    # Conversation and Sender
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    sender_id: int = Field(foreign_key="users.id", index=True)
    
    # Message Content
    content: str
    message_type: MessageType = Field(default=MessageType.TEXT)
    
    # Status and Delivery
    status: MessageStatus = Field(default=MessageStatus.SENT, index=True)
    
    # Attachments and Media
    attachments: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Message Context
    reply_to_message_id: Optional[int] = Field(default=None, foreign_key="messages.id")
    thread_id: Optional[str] = Field(index=True)  # For threading messages
    
    # Rich Content
    rich_content: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # For embeds, cards, etc.
    
    # Reactions and Interactions
    reactions: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Editing and Deletion
    edited_at: Optional[str] = None  # ISO format datetime string
    deleted_at: Optional[str] = None  # ISO format datetime string
    deleted_for: List[int] = Field(default_factory=list, sa_column=Column(JSON))  # User IDs who deleted
    
    # System Messages
    system_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Message Priority (for notifications, etc.)
    priority: int = Field(default=0)  # 0 = normal, 1 = high, -1 = low
    
    # Metadata
    entity_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    
    
class Message(MessageBase, TimestampMixin, table=True):
    __tablename__ = "messages"
    
    id: Optional[int] = id_field()
    
    # Message/Conversation system relationships - restored systematically
    sender: "User" = Relationship(back_populates="sent_messages")
    conversation: "Conversation" = Relationship(back_populates="messages")
    
    # Delivery tracking
    delivered_at: Optional[str] = None  # ISO format datetime string
    read_at: Optional[str] = None  # ISO format datetime string


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    created_at: str  # ISO format datetime string
    updated_at: Optional[str] = None  # ISO format datetime string
    delivered_at: Optional[str] = None  # ISO format datetime string
    read_at: Optional[str] = None  # ISO format datetime string


class MessageUpdate(SQLModel):
    content: Optional[str] = None
    status: Optional[MessageStatus] = None
    rich_content: Optional[dict] = None
    reactions: Optional[List[dict]] = None
    entity_metadata: Optional[dict] = None


# Model for tracking message read receipts per user
class MessageReadReceipt(SQLModel, table=True):
    __tablename__ = "message_read_receipts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="messages.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    read_at: datetime = Field(default_factory=datetime.utcnow)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)