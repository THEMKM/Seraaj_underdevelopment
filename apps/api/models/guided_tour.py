"""
Guided Tour Models for Seraaj
Interactive tutorials for different user types

This module defines models for:
- Guided tours and their steps
- User progress tracking
- Tour templates
- Analytics and feedback
"""
from typing import Optional, Dict, Any, List, Annotated, TYPE_CHECKING
from datetime import datetime
import uuid

from sqlmodel import SQLModel, Field, Column, JSON, Relationship

from .base.enums import EnumBase
from .types import (
    id_field, created_at_field, updated_at_field, json_field, rating_field
)

if TYPE_CHECKING:
    from .user import User

class TourType(EnumBase):
    """Types of guided tours"""
    ONBOARDING = "onboarding"
    FEATURE_INTRO = "feature_intro"
    WORKFLOW_GUIDE = "workflow_guide"
    ADVANCED_FEATURES = "advanced_features"
    TROUBLESHOOTING = "troubleshooting"
    UPDATES_SHOWCASE = "updates_showcase"


class TourStatus(EnumBase):
    """Status of tour completion"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    PAUSED = "paused"


class StepType(EnumBase):
    """Types of tour steps"""
    HIGHLIGHT = "highlight"        # Highlight an element
    TOOLTIP = "tooltip"           # Show tooltip
    MODAL = "modal"              # Show modal dialog
    OVERLAY = "overlay"          # Show overlay message
    ANIMATION = "animation"      # Play animation
    INTERACTION = "interaction"  # Wait for user interaction
    NAVIGATION = "navigation"    # Navigate to different page
    FORM_FILL = "form_fill"     # Guide through form filling


class TourUserRole(EnumBase):
    """User roles for tour targeting"""
    VOLUNTEER = "volunteer"
    ORGANIZATION = "organization" 
    ADMIN = "admin"
    ALL = "all"


class GuidedTour(SQLModel, table=True):
    """Main guided tour definition"""
    __tablename__ = "guided_tours"
    
    id: Optional[int] = id_field()
    tour_id: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Tour metadata
    title: str
    description: str
    tour_type: TourType
    target_role: TourUserRole = Field(default=TourUserRole.ALL)
    
    # Tour configuration
    is_active: bool = Field(default=True)
    is_mandatory: bool = Field(default=False)
    priority: int = Field(default=1)  # Higher priority tours shown first
    
    # Targeting conditions
    min_user_level: int = Field(default=0)  # User experience level required
    required_features: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Tour flow
    entry_url: str = Field(default="/")  # Where tour starts
    estimated_duration_minutes: int = Field(default=5)
    
    # Display settings
    theme: str = Field(default="default")
    show_progress: bool = Field(default=True)
    allow_skip: bool = Field(default=True)
    auto_advance: bool = Field(default=False)
    
    # Analytics
    total_views: int = Field(default=0)
    total_completions: int = Field(default=0)
    average_completion_time: Optional[float] = None
    
    # Foreign Keys
    created_by: Optional[int] = Field(foreign_key="users.id")
    
    # Guided tour system relationships - restored systematically
    creator: Optional["User"] = Relationship(back_populates="created_tours")
    steps: List["TourStep"] = Relationship(back_populates="tour")
    user_progress: List["UserTourProgress"] = Relationship(back_populates="tour")
    feedback: List["TourFeedback"] = Relationship(back_populates="tour")


class TourStep(SQLModel, table=True):
    """Individual steps within a guided tour"""
    __tablename__ = "tour_steps"
    
    id: Optional[int] = id_field()
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Step relationship
    tour_id: int = Field(foreign_key="guided_tours.id", index=True)
    tour: "GuidedTour" = Relationship(back_populates="steps")
    feedback: List["TourFeedback"] = Relationship(back_populates="step")
    
    # Step configuration
    step_number: int  # Order within tour
    step_type: StepType
    title: str
    content: str
    
    # Target element
    target_selector: Optional[str] = None  # CSS selector for element to highlight
    target_url: Optional[str] = None       # URL this step should appear on
    
    # Positioning and display
    position: str = Field(default="bottom")  # top, bottom, left, right, center
    offset_x: int = Field(default=0)
    offset_y: int = Field(default=0)
    width: Optional[int] = None
    height: Optional[int] = None
    
    # Behavior
    auto_advance_delay: Optional[int] = None  # Auto-advance after X seconds
    required_interaction: Optional[str] = None  # Required user action to proceed
    validation_script: Optional[str] = None    # JavaScript to validate step completion
    
    # Content and media
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    animation_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Navigation
    next_step_id: Optional[str] = None  # Override default next step
    prev_step_id: Optional[str] = None  # Override default previous step
    skip_conditions: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Call-to-action buttons
    primary_button_text: str = Field(default="Next")
    primary_button_action: str = Field(default="next")
    secondary_button_text: Optional[str] = Field(default="Skip")
    secondary_button_action: Optional[str] = Field(default="skip")
    
    # Analytics
    view_count: int = Field(default=0)
    completion_count: int = Field(default=0)
    skip_count: int = Field(default=0)
    average_time_spent: Optional[float] = None
    
    # Metadata
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()


class UserTourProgress(SQLModel, table=True):
    """Track user progress through guided tours"""
    __tablename__ = "user_tour_progress"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships with type safety
    user_id: int = Field(foreign_key="users.id", index=True)
    user: "User" = Relationship(back_populates="tour_progress")
    
    tour_id: int = Field(foreign_key="guided_tours.id", index=True)
    tour: "GuidedTour" = Relationship(back_populates="user_progress")
    
    # Progress tracking
    status: TourStatus = Field(default=TourStatus.NOT_STARTED)
    current_step: Optional[int] = None
    completed_steps: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    skipped_steps: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    total_time_spent: int = Field(default=0)  # Total seconds spent
    
    # User feedback
    rating: Optional[float] = rating_field()
    feedback: Optional[str] = None
    suggested_improvements: Optional[str] = None
    
    # Context when tour was taken
    device_type: Optional[str] = None
    browser: Optional[str] = None
    user_experience_level: int = Field(default=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TourTemplate(SQLModel, table=True):
    """Reusable tour templates"""
    __tablename__ = "tour_templates"
    
    id: Optional[int] = id_field()
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Template metadata
    name: str
    description: str
    category: str = Field(default="general")
    target_role: TourUserRole = Field(default=TourUserRole.ALL)
    
    # Template structure
    template_data: dict = json_field()
    default_settings: dict = json_field()
    
    # Usage tracking
    usage_count: int = Field(default=0)
    is_featured: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()
    created_by: Optional[int] = Field(foreign_key="users.id")


class TourAnalytics(SQLModel, table=True):
    """Analytics data for guided tours"""
    __tablename__ = "tour_analytics"
    
    id: Optional[int] = id_field()
    
    # Time period
    date: datetime = Field(index=True)
    hour: int = Field(default=0)  # 0-23
    
    # Tour details
    tour_id: int = Field(foreign_key="guided_tours.id", index=True)
    step_id: Optional[int] = Field(foreign_key="tour_steps.id")
    
    # User context
    user_role: TourUserRole
    device_type: str = Field(default="unknown")
    browser: str = Field(default="unknown")
    
    # Metrics
    views: int = Field(default=0)
    starts: int = Field(default=0)
    completions: int = Field(default=0)
    skips: int = Field(default=0)
    drop_offs: int = Field(default=0)
    
    # Engagement metrics
    avg_time_per_step: Optional[float] = None
    completion_rate: Optional[float] = None
    user_satisfaction: Optional[float] = None  # Average rating
    
    # Technical metrics
    load_time_ms: Optional[int] = None
    error_count: int = Field(default=0)
    
    # Metadata
    created_at: datetime = created_at_field()


class TourFeedback(SQLModel, table=True):
    """User feedback on guided tours"""
    __tablename__ = "tour_feedback"
    
    id: Optional[int] = id_field()
    
    # Relationships
    user_id: int = Field(foreign_key="users.id", index=True)
    tour_id: int = Field(foreign_key="guided_tours.id", index=True)
    step_id: Optional[int] = Field(foreign_key="tour_steps.id")
    
    user: "User" = Relationship(back_populates="tour_feedback")
    tour: "GuidedTour" = Relationship(back_populates="feedback")
    step: Optional["TourStep"] = Relationship(back_populates="feedback")
    
    # Feedback details
    feedback_type: str = Field(default="general")  # general, bug_report, suggestion, praise
    rating: Optional[float] = rating_field()
    title: str
    message: str
    
    # Context
    user_agent: Optional[str] = None
    url: Optional[str] = None
    screenshot_url: Optional[str] = None
    
    # Status
    status: str = Field(default="open")  # open, reviewed, resolved, dismissed
    admin_response: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = Field(foreign_key="users.id")
    
    # Metadata
    created_at: datetime = created_at_field()
    updated_at: datetime = updated_at_field()


# Export commonly used types
TourTypeChoices = [choice.value for choice in TourType]
StepTypeChoices = [choice.value for choice in StepType]
TourStatusChoices = [choice.value for choice in TourStatus]
TourUserRoleChoices = [choice.value for choice in TourUserRole]