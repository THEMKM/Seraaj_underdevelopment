from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from pydantic import model_validator, validator

from .types import (
    TimestampMixin, id_field,
    UserRef, OrganisationRef, VolunteerRef,
    OpportunityRef, ApplicationRef
)

if TYPE_CHECKING:
    from .user import User
    from .organisation import Organisation
    from .volunteer import Volunteer 
    from .opportunity import Opportunity
    from .application import Application


class ReviewType(str, Enum):
    VOLUNTEER_TO_ORG = "volunteer_to_org"  # Volunteer rating organization
    ORG_TO_VOLUNTEER = "org_to_volunteer"  # Organization rating volunteer
    OPPORTUNITY_REVIEW = "opportunity_review"  # Review of specific opportunity


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    HIDDEN = "hidden"
    FLAGGED = "flagged"
    DELETED = "deleted"


class ReviewBase(SQLModel):
    # Review Type and Relationships
    review_type: ReviewType = Field(index=True)
    reviewer_id: int = Field(foreign_key="users.id", index=True)
    
    # What's being reviewed
    reviewed_organization_id: Optional[int] = Field(default=None, foreign_key="organisations.id")
    reviewed_volunteer_id: Optional[int] = Field(default=None, foreign_key="volunteers.id")
    reviewed_opportunity_id: Optional[int] = Field(default=None, foreign_key="opportunities.id")
    
    # Review Content
    rating: float = Field(ge=1.0, le=5.0)  # 1-5 star rating
    title: Optional[str] = None
    content: str
    
    # Detailed Ratings (optional breakdown)
    communication_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    professionalism_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    impact_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    organization_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    
    # Review Metadata
    status: ReviewStatus = Field(default=ReviewStatus.PUBLISHED, index=True)
    anonymous: bool = Field(default=False)
    
    # Context
    related_application_id: Optional[int] = Field(default=None, foreign_key="applications.id")
    volunteer_experience_duration: Optional[str] = None  # e.g., "3 months", "1 year"
    
    # Moderation
    flagged_count: int = Field(default=0)
    verified: bool = Field(default=False)
    
    # Helpful votes
    helpful_votes: int = Field(default=0)
    total_votes: int = Field(default=0)
    
    # Response from reviewed party
    response: Optional[str] = None
    response_date: Optional[str] = None  # ISO format datetime string
    
    # Additional data
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    entity_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Validation methods
    @validator('rating', 'communication_rating', 'professionalism_rating')
    def validate_ratings(cls, v):
        """Ensure ratings are within valid range"""
        if v is not None and (v < 1.0 or v > 5.0):
            raise ValueError('Ratings must be between 1.0 and 5.0')
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_reviewed_entity(cls, values):
        """Ensure only one reviewed entity is specified"""
        reviewed_fields = [
            values.get('reviewed_organization_id'),
            values.get('reviewed_volunteer_id'), 
            values.get('reviewed_opportunity_id')
        ]
        
        # Count non-None values
        non_none_count = sum(1 for field in reviewed_fields if field is not None)
        
        if non_none_count == 0:
            raise ValueError('At least one reviewed entity must be specified')
        elif non_none_count > 1:
            raise ValueError('Only one reviewed entity can be specified per review')
            
        return values


class Review(ReviewBase, TimestampMixin, table=True):
    __tablename__ = "reviews"
    
    id: Optional[int] = id_field()
    
    # Review system relationships - restored systematically
    reviewer: "User" = Relationship(back_populates="reviews_written")
    reviewed_organisation: Optional["Organisation"] = Relationship(back_populates="reviews")
    reviewed_volunteer: Optional["Volunteer"] = Relationship(back_populates="reviews")
    reviewed_opportunity: Optional["Opportunity"] = Relationship(back_populates="reviews")
    related_application: Optional["Application"] = Relationship(back_populates="review")


class ReviewCreate(SQLModel):
    review_type: ReviewType
    reviewed_organization_id: Optional[int] = None
    reviewed_volunteer_id: Optional[int] = None
    reviewed_opportunity_id: Optional[int] = None
    rating: float
    title: Optional[str] = None
    content: str
    communication_rating: Optional[float] = None
    professionalism_rating: Optional[float] = None
    impact_rating: Optional[float] = None
    organization_rating: Optional[float] = None
    anonymous: bool = False
    related_application_id: Optional[int] = None
    volunteer_experience_duration: Optional[str] = None
    tags: List[str] = []


class ReviewRead(ReviewBase):
    id: int
    created_at: str  # ISO format datetime string
    updated_at: Optional[str] = None  # ISO format datetime string
    reviewer_name: Optional[str] = None  # Populated based on anonymous flag


class ReviewUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    rating: Optional[float] = None
    communication_rating: Optional[float] = None
    professionalism_rating: Optional[float] = None
    impact_rating: Optional[float] = None
    organization_rating: Optional[float] = None
    status: Optional[ReviewStatus] = None
    response: Optional[str] = None
    tags: Optional[List[str]] = None
    entity_metadata: Optional[dict] = None


# Model for tracking review helpfulness votes
class ReviewVote(TimestampMixin, table=True):
    __tablename__ = "review_votes"
    
    id: Optional[int] = id_field()
    review_id: int = Field(foreign_key="reviews.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    helpful: bool  # True for helpful, False for not helpful


# Model for flagging inappropriate reviews
class ReviewFlag(SQLModel, table=True):
    __tablename__ = "review_flags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    review_id: int = Field(foreign_key="reviews.id", index=True)
    flagger_id: int = Field(foreign_key="users.id", index=True)
    reason: str
    description: Optional[str] = None
    
    status: str = Field(default="pending")  # pending, reviewed, dismissed
    resolved_by: Optional[int] = Field(default=None, foreign_key="users.id")
    resolved_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)