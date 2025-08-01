from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON, Relationship, UniqueConstraint

from .types import TimestampMixin, id_field, email_field

if TYPE_CHECKING:
    from .user import User
    from .opportunity import Opportunity
    from .review import Review


class OrganizationType(str, Enum):
    NGO = "ngo"
    NONPROFIT = "nonprofit"
    CHARITY = "charity"
    FOUNDATION = "foundation"
    SOCIAL_ENTERPRISE = "social_enterprise"


class TeamSizeRange(str, Enum):
    SMALL = "1-10"
    MEDIUM = "11-50"
    LARGE = "51-200"
    XLARGE = "200+"


class OrganisationBase(SQLModel):
    # Link to User account that manages this organization
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)

    # Basic Information
    name: str = Field(index=True)
    name_ar: Optional[str] = None
    email: str = email_field()
    website: Optional[str] = None
    phone: Optional[str] = None

    # Description and Mission
    description: Optional[str] = None
    description_ar: Optional[str] = None
    mission: Optional[str] = None
    mission_ar: Optional[str] = None

    # Visual Assets
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None

    # Location
    location: Optional[str] = Field(index=True)
    location_ar: Optional[str] = None
    country: Optional[str] = Field(index=True)
    country_ar: Optional[str] = None
    address: Optional[str] = None

    # Organization Details
    organization_type: OrganizationType = Field(default=OrganizationType.NGO)
    causes: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    established_year: Optional[int] = None
    team_size: TeamSizeRange = Field(default=TeamSizeRange.SMALL)

    # Verification and Trust
    verified: bool = Field(default=False)
    trust_score: float = Field(default=0.0, ge=0.0, le=100.0)
    verification_documents: List[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )

    # Activity Stats
    total_opportunities: int = Field(default=0)
    active_opportunities: int = Field(default=0)
    total_volunteers: int = Field(default=0)
    total_applications: int = Field(default=0)

    # Ratings and Reviews
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    total_reviews: int = Field(default=0)

    # Settings and Preferences
    notification_settings: dict = Field(default_factory=dict, sa_column=Column(JSON))
    privacy_settings: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Additional organization data (flexible for future features)
    profile_data: dict = Field(default_factory=dict, sa_column=Column(JSON))


class Organisation(OrganisationBase, TimestampMixin, table=True):
    __tablename__ = "organisations"
    __table_args__ = (
        UniqueConstraint("name", name="unique_org_name"),
    )

    id: Optional[int] = id_field()

    # Relationships
    user: "User" = Relationship(back_populates="organisation")
    opportunities: List["Opportunity"] = Relationship(back_populates="organisation")
    reviews: List["Review"] = Relationship(back_populates="reviewed_organisation")

    # Applications are accessed through opportunities.applications relationship
    # No direct relationship needed since applications belong to opportunities


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationRead(OrganisationBase):
    id: int
    created_at: str  # ISO format datetime string
    updated_at: Optional[str] = None  # ISO format datetime string


class OrganisationUpdate(SQLModel):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    mission: Optional[str] = None
    mission_ar: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    location: Optional[str] = None
    location_ar: Optional[str] = None
    country: Optional[str] = None
    country_ar: Optional[str] = None
    address: Optional[str] = None
    organization_type: Optional[OrganizationType] = None
    causes: Optional[List[str]] = None
    established_year: Optional[int] = None
    team_size: Optional[TeamSizeRange] = None
    notification_settings: Optional[dict] = None
    privacy_settings: Optional[dict] = None
    profile_data: Optional[dict] = None
