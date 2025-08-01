"""
Enum base classes and utilities
Provides standard enum types and validation
"""

from enum import Enum
from typing import List, TypeVar

T = TypeVar("T", bound=Enum)


class EnumBase(str, Enum):
    """Base class for string enums with additional utilities"""

    @classmethod
    def values(cls) -> List[str]:
        """Get all possible values for the enum"""
        return [e.value for e in cls]

    @classmethod
    def contains(cls, value: str) -> bool:
        """Check if a value is valid for this enum"""
        return value in cls.values()

    def __str__(self) -> str:
        return self.value
