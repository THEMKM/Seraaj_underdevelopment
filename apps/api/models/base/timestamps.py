"""Base models with common functionality"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TimestampedModel(SQLModel):
    """Base model with timestamp fields"""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IdentifierModel(SQLModel):
    """Base model with ID field"""

    id: Optional[int] = Field(default=None, primary_key=True)
