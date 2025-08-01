"""
Base Model Definitions
Provides core model functionality and common patterns for the entire application.
"""

from .enums import EnumBase
from .timestamps import IdentifierModel, TimestampedModel


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
    "EnumBase",
]
