from datetime import date
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from pydantic import model_validator, validator

from .types import (
    TimestampMixin, id_field, json_field,
    OrganisationRef, ApplicationRef, ReviewRef
)

if TYPE_CHECKING:
    from .organisation import Organisation
    from .application import Application
    from .review import Review
    from .conversation import Conversation


class OpportunityState(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    FILLED = "filled"
    CLOSED = "closed"


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeCommitmentType(str, Enum):
    ONE_TIME = "one-time"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    FLEXIBLE = "flexible"


class OpportunityBase(SQLModel):
    # Basic Information
    org_id: int = Field(foreign_key="organisations.id", index=True)
    title: str = Field(index=True)
    title_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None
    
    # Status and Visibility
    state: OpportunityState = Field(default=OpportunityState.DRAFT, index=True)
    featured: bool = Field(default=False)
    verified: bool = Field(default=False)
    
    # Location and Remote Work
    location: Optional[str] = Field(index=True)
    location_ar: Optional[str] = None
    country: Optional[str] = Field(index=True)
    country_ar: Optional[str] = None
    remote_allowed: bool = Field(default=False)
    
    # Categorization
    causes: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    skills_required: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    skills_preferred: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Time and Commitment
    time_commitment: Optional[str] = None  # e.g., "4 hours/week"
    time_commitment_type: TimeCommitmentType = Field(default=TimeCommitmentType.FLEXIBLE)
    duration: Optional[str] = None  # e.g., "6 months"
    schedule_flexibility: bool = Field(default=True)
    
    # Dates
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    application_deadline: Optional[date] = None
    
    # Capacity and Applications
    volunteers_needed: int = Field(default=1, ge=1)
    volunteers_applied: int = Field(default=0)
    volunteers_accepted: int = Field(default=0)
    
    # Priority and Urgency
    urgency: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM)
    priority_score: float = Field(default=0.0)  # For internal ranking
    
    # Requirements and Benefits
    requirements: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    benefits: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    training_provided: bool = Field(default=False)
    
    # Media and Documentation
    images: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # URLs
    documents: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # URLs
    
    # Application Process
    application_questions: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    requires_background_check: bool = Field(default=False)
    requires_interview: bool = Field(default=False)
    
    # Analytics and Performance
    view_count: int = Field(default=0)
    application_success_rate: float = Field(default=0.0)
    average_match_score: float = Field(default=0.0)
    
    # Additional opportunity data (flexible for future features)
    details: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Validation methods
    @validator('volunteers_accepted')
    def validate_volunteers_accepted(cls, v, values):
        """Ensure volunteers_accepted doesn't exceed volunteers_needed"""
        volunteers_needed = values.get('volunteers_needed', 1)
        if v > volunteers_needed:
            raise ValueError('volunteers_accepted cannot exceed volunteers_needed')
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_dates(cls, values):
        """Validate date relationships"""
        start_date = values.get('start_date')
        end_date = values.get('end_date') 
        application_deadline = values.get('application_deadline')
        
        # Validate end_date > start_date
        if start_date and end_date and end_date <= start_date:
            raise ValueError('end_date must be after start_date')
        
        # Validate application_deadline <= start_date
        if application_deadline and start_date and application_deadline > start_date:
            raise ValueError('application_deadline must be before or on start_date')
            
        # Validate dates are not in the past (for new opportunities)
        today = date.today()
        if start_date and start_date < today:
            raise ValueError('start_date cannot be in the past')
        if application_deadline and application_deadline < today:
            raise ValueError('application_deadline cannot be in the past')
            
        return values
    
    
class Opportunity(OpportunityBase, TimestampMixin, table=True):
    __tablename__ = "opportunities"
    
    id: Optional[int] = id_field()
    
    # Additional Stats and Metrics
    views_count: int = Field(default=0)
    saved_count: int = Field(default=0)  # For "favorite"/"bookmark" feature
    
    # Relationships
    organisation: "Organisation" = Relationship(back_populates="opportunities")
    applications: List["Application"] = Relationship(back_populates="opportunity")
    reviews: List["Review"] = Relationship(back_populates="reviewed_opportunity")
    conversations: List["Conversation"] = Relationship(back_populates="related_opportunity")


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityRead(OpportunityBase):
    id: int
    created_at: str  # ISO format datetime string
    updated_at: Optional[str] = None  # ISO format datetime string


class OpportunityUpdate(SQLModel):
    title: Optional[str] = None
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    state: Optional[OpportunityState] = None
    featured: Optional[bool] = None
    location: Optional[str] = None
    location_ar: Optional[str] = None
    country: Optional[str] = None
    country_ar: Optional[str] = None
    remote_allowed: Optional[bool] = None
    causes: Optional[List[str]] = None
    skills_required: Optional[List[str]] = None
    skills_preferred: Optional[List[str]] = None
    time_commitment: Optional[str] = None
    time_commitment_type: Optional[TimeCommitmentType] = None
    duration: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    application_deadline: Optional[date] = None
    volunteers_needed: Optional[int] = None
    urgency: Optional[UrgencyLevel] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    training_provided: Optional[bool] = None
    images: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    application_questions: Optional[List[dict]] = None
    requires_background_check: Optional[bool] = None
    requires_interview: Optional[bool] = None
    details: Optional[dict] = None