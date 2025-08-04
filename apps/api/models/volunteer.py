from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON

from .types import TimestampMixin, id_field
from sqlmodel import Relationship

if TYPE_CHECKING:
    from .user import User
    from .application import Application
    from .review import Review


class AvailabilityType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    WEEKENDS = "weekends"
    FLEXIBLE = "flexible"


class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class VolunteerBase(SQLModel):
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)

    # Personal Information
    full_name: str = Field(index=True)
    full_name_ar: Optional[str] = None
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    avatar_url: Optional[str] = None

    # Location
    location: Optional[str] = Field(index=True)
    location_ar: Optional[str] = None
    country: Optional[str] = Field(index=True)
    country_ar: Optional[str] = None

    # Skills and Interests
    skills: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    interests: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    languages: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Availability and Experience
    availability: AvailabilityType = Field(default=AvailabilityType.FLEXIBLE)
    experience_level: ExperienceLevel = Field(default=ExperienceLevel.BEGINNER)
    time_commitment_hours: Optional[int] = None  # hours per week

    # Verification and Ratings
    verified: bool = Field(default=False)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    total_reviews: int = Field(default=0)

    # Activity Stats
    completed_opportunities: int = Field(default=0)
    active_applications: int = Field(default=0)
    total_volunteer_hours: int = Field(default=0)

    # Preferences
    notification_preferences: dict = Field(default_factory=dict, sa_column=Column(JSON))
    privacy_settings: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Additional profile data (flexible for future features)
    profile_data: dict = Field(default_factory=dict, sa_column=Column(JSON))


class Volunteer(VolunteerBase, TimestampMixin, table=True):
    __tablename__ = "volunteers"

    id: Optional[int] = id_field()

    # Relationships
    user: "User" = Relationship(back_populates="volunteer")
    applications: List["Application"] = Relationship(back_populates="volunteer")
    reviews: List["Review"] = Relationship(back_populates="reviewed_volunteer")


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerRead(VolunteerBase):
    id: int
    created_at: str  # ISO format datetime string
    updated_at: Optional[str] = None  # ISO format datetime string


class VolunteerUpdate(SQLModel):
    full_name: Optional[str] = None
    full_name_ar: Optional[str] = None
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    location_ar: Optional[str] = None
    country: Optional[str] = None
    country_ar: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    availability: Optional[AvailabilityType] = None
    experience_level: Optional[ExperienceLevel] = None
    time_commitment_hours: Optional[int] = None
    notification_preferences: Optional[dict] = None
    privacy_settings: Optional[dict] = None
    profile_data: Optional[dict] = None
