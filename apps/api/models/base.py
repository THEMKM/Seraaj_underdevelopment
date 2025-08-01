"""
Base models and mixins for all SQLModel classes
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class CreatedUpdatedMixin(SQLModel):
    """Mixin for created_at and updated_at fields"""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
