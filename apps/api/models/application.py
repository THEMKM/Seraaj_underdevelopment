from typing import Optional, List, TYPE_CHECKING
from datetime import date
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON, Relationship, UniqueConstraint
from pydantic import validator, model_validator

from .types import (
    TimestampMixin, id_field,
    VolunteerRef, OpportunityRef, UserRef
)

if TYPE_CHECKING:
    from .volunteer import Volunteer
    from .opportunity import Opportunity
    from .review import Review
    from .conversation import Conversation
    from .user import User


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    RECOMMENDED = "recommended"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWING = "interviewing"
    INTERVIEW_COMPLETED = "interview_completed"
    BACKGROUND_CHECK = "background_check"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ApplicationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ApplicationBase(SQLModel):
    # Relationships
    vol_id: int = Field(foreign_key="volunteers.id", index=True)
    opp_id: int = Field(foreign_key="opportunities.id", index=True)
    
    # Application Status
    status: ApplicationStatus = Field(default=ApplicationStatus.DRAFT, index=True)
    priority: ApplicationPriority = Field(default=ApplicationPriority.MEDIUM)
    
    # Application Content
    cover_letter: Optional[str] = None
    motivation: Optional[str] = None
    relevant_experience: Optional[str] = None
    
    # Multi-step Application Data
    application_responses: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    uploaded_documents: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Matching and Scoring
    match_score: float = Field(default=0.0, ge=0.0, le=100.0)
    compatibility_factors: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Timeline
    submitted_at: Optional[str] = None  # ISO format datetime string
    reviewed_at: Optional[str] = None  # ISO format datetime string
    interview_scheduled_at: Optional[str] = None  # ISO format datetime string
    decision_made_at: Optional[str] = None  # ISO format datetime string
    
    # Review and Feedback
    reviewer_id: Optional[int] = Field(default=None, foreign_key="users.id")
    review_notes: Optional[str] = None
    feedback_to_volunteer: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    # Interview Details
    interview_type: Optional[str] = None  # "phone", "video", "in-person"
    interview_date: Optional[str] = None  # ISO format datetime string
    interview_notes: Optional[str] = None
    interview_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    
    # Background Check
    background_check_required: bool = Field(default=False)
    background_check_status: Optional[str] = None
    background_check_notes: Optional[str] = None
    
    # References
    references: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    references_contacted: bool = Field(default=False)
    
    # Communication
    last_contact_date: Optional[str] = None  # ISO format datetime string
    contact_attempts: int = Field(default=0)
    
    # Additional application data (flexible for future features)
    app_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Validation methods
    @validator('status')
    def validate_status_transitions(cls, v, values):
        """Validate application status transitions"""
        # Define valid status transitions
        valid_transitions = {
            ApplicationStatus.DRAFT: [ApplicationStatus.SUBMITTED, ApplicationStatus.WITHDRAWN],
            ApplicationStatus.SUBMITTED: [ApplicationStatus.UNDER_REVIEW, ApplicationStatus.WITHDRAWN],
            ApplicationStatus.UNDER_REVIEW: [ApplicationStatus.RECOMMENDED, ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.REJECTED],
            ApplicationStatus.RECOMMENDED: [ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED],
            ApplicationStatus.INTERVIEW_SCHEDULED: [ApplicationStatus.INTERVIEWING, ApplicationStatus.REJECTED],
            ApplicationStatus.INTERVIEWING: [ApplicationStatus.INTERVIEW_COMPLETED, ApplicationStatus.REJECTED],
            ApplicationStatus.INTERVIEW_COMPLETED: [ApplicationStatus.BACKGROUND_CHECK, ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED],
            ApplicationStatus.BACKGROUND_CHECK: [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED],
            ApplicationStatus.ACCEPTED: [ApplicationStatus.WITHDRAWN],  # Only withdrawal allowed after acceptance
            ApplicationStatus.REJECTED: [],  # Final state
            ApplicationStatus.WITHDRAWN: [],  # Final state
            ApplicationStatus.EXPIRED: []  # Final state
        }
        
        # For new applications, any status is allowed
        # For updates, this validation would need to be done at the router level
        # where we have access to the current status
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_business_rules(cls, values):
        """Validate business rules and constraints"""
        vol_id = values.get('vol_id')
        opp_id = values.get('opp_id')
        
        # Check for required fields
        if not vol_id:
            raise ValueError('volunteer_id is required for applications')
        if not opp_id:
            raise ValueError('opportunity_id is required for applications')
        
        # Note: Duplicate prevention is enforced at database level with unique constraint
        # Database will raise IntegrityError which should be caught at router level
        # and converted to appropriate HTTP 409 Conflict response
        
        return values
    
    
class Application(ApplicationBase, TimestampMixin, table=True):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint('vol_id', 'opp_id', name='unique_volunteer_opportunity'),
    )
    
    id: Optional[int] = id_field()
    
    # Relationships
    volunteer: "Volunteer" = Relationship(back_populates="applications")
    opportunity: "Opportunity" = Relationship(back_populates="applications")
    review: Optional["Review"] = Relationship(back_populates="related_application")
    conversations: List["Conversation"] = Relationship(back_populates="related_application")


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationRead(ApplicationBase):
    id: int
    created_at: str  # ISO format datetime string
    updated_at: Optional[str] = None  # ISO format datetime string


class ApplicationUpdate(SQLModel):
    status: Optional[ApplicationStatus] = None
    priority: Optional[ApplicationPriority] = None
    cover_letter: Optional[str] = None
    motivation: Optional[str] = None
    relevant_experience: Optional[str] = None
    application_responses: Optional[List[dict]] = None
    uploaded_documents: Optional[List[dict]] = None
    match_score: Optional[float] = None
    compatibility_factors: Optional[dict] = None
    reviewer_id: Optional[int] = None
    review_notes: Optional[str] = None
    feedback_to_volunteer: Optional[str] = None
    rejection_reason: Optional[str] = None
    interview_type: Optional[str] = None
    interview_date: Optional[str] = None  # ISO format datetime string
    interview_notes: Optional[str] = None
    interview_rating: Optional[float] = None
    background_check_status: Optional[str] = None
    background_check_notes: Optional[str] = None
    references: Optional[List[dict]] = None
    entity_metadata: Optional[dict] = None