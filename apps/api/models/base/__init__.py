"""
Base Model Definitions
Provides core model functionality and common patterns for the entire application.
"""

from .timestamps import TimestampedModel, IdentifierModel
from .relationships import RelationshipModel
from .enums import EnumBase


class BaseModel(TimestampedModel, IdentifierModel):
    """
    Base model that combines common functionality.
    Use this as the base for most models that need IDs and timestamps.
    """

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


__all__ = [
    "BaseModel",
    "TimestampedModel",
    "IdentifierModel",
    "RelationshipModel",
    "EnumBase",
]
