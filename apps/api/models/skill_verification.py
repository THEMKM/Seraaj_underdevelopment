from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, JSON, Column


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


class VerificationMethod(str, Enum):
    DOCUMENT = "document"  # Certificate, diploma, etc.
    REFERENCE = "reference"  # Reference from supervisor/colleague
    TEST = "test"  # Online skill test
    PORTFOLIO = "portfolio"  # Work samples
    INTERVIEW = "interview"  # Skill assessment interview
    EXPERIENCE = "experience"  # Verified work experience


class SkillVerificationBase(SQLModel):
    # Ownership
    volunteer_id: int = Field(foreign_key="volunteers.id", index=True)

    # Skill Information
    skill_name: str = Field(index=True)
    skill_category: Optional[str] = None
    skill_level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE)

    # Verification Details
    verification_method: VerificationMethod
    status: VerificationStatus = Field(default=VerificationStatus.PENDING, index=True)

    # Evidence and Documentation
    supporting_documents: List[dict] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    portfolio_links: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Reference Information (if verification_method is REFERENCE)
    reference_name: Optional[str] = None
    reference_email: Optional[str] = None
    reference_organization: Optional[str] = None
    reference_position: Optional[str] = None
    reference_contacted: bool = Field(default=False)

    # Experience Details (if verification_method is EXPERIENCE)
    experience_description: Optional[str] = None
    experience_duration: Optional[str] = None
    experience_organization: Optional[str] = None

    # Test Results (if verification_method is TEST)
    test_score: Optional[float] = None
    test_provider: Optional[str] = None
    test_certificate_url: Optional[str] = None

    # Review Process
    reviewer_id: Optional[int] = Field(default=None, foreign_key="users.id")
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    # Validity
    valid_from: date = Field(default_factory=date.today)
    valid_until: Optional[date] = None
    auto_expire: bool = Field(default=False)

    # Public Display
    is_public: bool = Field(default=True)
    featured: bool = Field(default=False)

    # Additional metadata
    entity_metadata: Optional[dict] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class SkillVerification(SkillVerificationBase, table=True):
    __tablename__ = "skill_verifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class SkillVerificationCreate(SQLModel):
    skill_name: str
    skill_category: Optional[str] = None
    skill_level: SkillLevel = SkillLevel.INTERMEDIATE
    verification_method: VerificationMethod
    supporting_documents: List[dict] = []
    portfolio_links: List[str] = []
    reference_name: Optional[str] = None
    reference_email: Optional[str] = None
    reference_organization: Optional[str] = None
    reference_position: Optional[str] = None
    experience_description: Optional[str] = None
    experience_duration: Optional[str] = None
    experience_organization: Optional[str] = None
    test_score: Optional[float] = None
    test_provider: Optional[str] = None
    test_certificate_url: Optional[str] = None
    valid_until: Optional[date] = None
    is_public: bool = True


class SkillVerificationRead(SkillVerificationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class SkillVerificationUpdate(SQLModel):
    skill_level: Optional[SkillLevel] = None
    status: Optional[VerificationStatus] = None
    reviewer_id: Optional[int] = None
    review_notes: Optional[str] = None
    valid_until: Optional[date] = None
    is_public: Optional[bool] = None
    featured: Optional[bool] = None
    entity_metadata: Optional[dict] = None


# Badge System
class BadgeType(str, Enum):
    SKILL = "skill"
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    RECOGNITION = "recognition"
    CERTIFICATION = "certification"


class BadgeBase(SQLModel):
    # Badge Information
    name: str = Field(index=True)
    name_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None

    # Visual
    icon_url: Optional[str] = None
    color: str = Field(default="#FFD749")  # Default to Seraaj primary color

    # Badge Type and Category
    badge_type: BadgeType
    category: Optional[str] = None

    # Requirements
    requirements: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Rarity and Value
    rarity: str = Field(default="common")  # common, uncommon, rare, epic, legendary
    points_value: int = Field(default=10)

    # Visibility
    is_active: bool = Field(default=True)
    is_public: bool = Field(default=True)

    # Additional data
    entity_metadata: Optional[dict] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )


class Badge(BadgeBase, table=True):
    __tablename__ = "badges"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# User Badge Assignments
class UserBadgeBase(SQLModel):
    user_id: int = Field(foreign_key="users.id", index=True)
    badge_id: int = Field(foreign_key="badges.id", index=True)

    # Award Details
    awarded_by: Optional[int] = Field(default=None, foreign_key="users.id")
    reason: Optional[str] = None

    # Evidence
    evidence_data: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Display
    is_featured: bool = Field(default=False)
    is_public: bool = Field(default=True)

    # Validity
    valid_until: Optional[date] = None
    revoked: bool = Field(default=False)
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[int] = Field(default=None, foreign_key="users.id")
    revoked_reason: Optional[str] = None


class UserBadge(UserBadgeBase, table=True):
    __tablename__ = "user_badges"

    id: Optional[int] = Field(default=None, primary_key=True)
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
