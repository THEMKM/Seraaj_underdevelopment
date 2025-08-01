"""
Demo Scenario Models for Seraaj
Comprehensive demo scenarios for showcasing platform features
"""

from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class ScenarioType(str, Enum):
    """Types of demo scenarios"""

    FULL_JOURNEY = "full_journey"  # Complete user journey from start to finish
    FEATURE_SHOWCASE = "feature_showcase"  # Highlight specific features
    WORKFLOW_DEMO = "workflow_demo"  # Demonstrate specific workflows
    INTEGRATION_DEMO = "integration_demo"  # Show system integrations
    PERFORMANCE_DEMO = "performance_demo"  # Showcase performance features
    ONBOARDING_DEMO = "onboarding_demo"  # New user experience


class ScenarioStatus(str, Enum):
    """Status of demo scenarios"""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    MAINTENANCE = "maintenance"


class DemoUserType(str, Enum):
    """Types of demo users"""

    VOLUNTEER = "volunteer"
    ORGANIZATION = "organization"
    ADMIN = "admin"
    VISITOR = "visitor"


class ActionType(str, Enum):
    """Types of actions in demo scenarios"""

    CREATE_USER = "create_user"
    LOGIN = "login"
    NAVIGATE = "navigate"
    FILL_FORM = "fill_form"
    CLICK_BUTTON = "click_button"
    UPLOAD_FILE = "upload_file"
    SEND_MESSAGE = "send_message"
    MAKE_PAYMENT = "make_payment"
    SUBMIT_APPLICATION = "submit_application"
    CREATE_OPPORTUNITY = "create_opportunity"
    REVIEW_APPLICATION = "review_application"
    VERIFY_SKILL = "verify_skill"
    GENERATE_REPORT = "generate_report"
    TRIGGER_NOTIFICATION = "trigger_notification"
    SIMULATE_OFFLINE = "simulate_offline"
    WAIT = "wait"
    ASSERT = "assert"


class DemoScenario(SQLModel, table=True):
    """Main demo scenario definition"""

    __tablename__ = "demo_scenarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    # Scenario metadata
    name: str
    description: str
    scenario_type: ScenarioType
    target_audience: str = Field(default="general")  # investors, clients, team, public

    # Configuration
    status: ScenarioStatus = Field(default=ScenarioStatus.DRAFT)
    duration_minutes: int = Field(default=10)
    difficulty_level: str = Field(
        default="beginner"
    )  # beginner, intermediate, advanced

    # Demo settings
    auto_play: bool = Field(default=False)
    reset_data: bool = Field(default=True)  # Reset demo data before running
    use_mock_data: bool = Field(default=True)

    # Branding and presentation
    theme: str = Field(default="default")
    show_annotations: bool = Field(default=True)
    show_metrics: bool = Field(default=True)

    # Demo environment
    base_url: str = Field(default="https://demo.seraaj.org")
    api_endpoints: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    required_features: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Analytics
    total_runs: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    average_duration: Optional[float] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(foreign_key="users.id")

    # Relationships - Note: List relationships are handled by SQLModel automatically
    steps: List["DemoStep"] = Relationship(back_populates="scenario")
    runs: List["DemoRun"] = Relationship(back_populates="scenario")


class DemoStep(SQLModel, table=True):
    """Individual steps within a demo scenario"""

    __tablename__ = "demo_steps"

    id: Optional[int] = Field(default=None, primary_key=True)
    step_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    # Step relationship
    scenario_id: int = Field(foreign_key="demo_scenarios.id", index=True)
    scenario: DemoScenario = Relationship(back_populates="steps")

    # Step configuration
    step_number: int
    action_type: ActionType
    title: str
    description: str

    # Action parameters
    target_element: Optional[str] = None  # CSS selector or element ID
    target_url: Optional[str] = None  # URL to navigate to
    form_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    expected_result: Optional[str] = None  # What should happen after this step

    # Demo user context
    demo_user_type: Optional[DemoUserType] = None
    user_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Timing and flow
    duration_seconds: int = Field(default=3)
    wait_for_condition: Optional[str] = None  # Wait for specific condition
    skip_if_condition: Optional[str] = None  # Skip step if condition met

    # Presentation
    show_highlight: bool = Field(default=True)
    annotation_text: Optional[str] = None
    annotation_position: str = Field(default="top")  # top, bottom, left, right

    # Validation
    validation_rules: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    success_criteria: Optional[str] = None

    # Error handling
    retry_on_failure: bool = Field(default=True)
    max_retries: int = Field(default=3)
    fallback_action: Optional[str] = None

    # Analytics
    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    average_execution_time: Optional[float] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DemoRun(SQLModel, table=True):
    """Individual demo scenario execution records"""

    __tablename__ = "demo_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    # Run relationship
    scenario_id: int = Field(foreign_key="demo_scenarios.id", index=True)
    scenario: DemoScenario = Relationship(back_populates="runs")

    # Run context
    runner_id: Optional[int] = Field(foreign_key="users.id")  # Who ran the demo
    session_id: str = Field(index=True)  # Browser/session identifier

    # Execution details
    status: str = Field(default="running")  # running, completed, failed, aborted
    current_step: Optional[int] = None
    completed_steps: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    failed_steps: List[int] = Field(default_factory=list, sa_column=Column(JSON))

    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_duration_seconds: Optional[int] = None

    # Environment
    browser: Optional[str] = None
    device_type: Optional[str] = None
    screen_resolution: Optional[str] = None
    user_agent: Optional[str] = None

    # Results and logs
    success_rate: Optional[float] = None
    error_logs: List[Dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    performance_metrics: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )

    # Feedback (if run by human)
    rating: Optional[int] = Field(ge=1, le=5)
    feedback: Optional[str] = None
    suggestions: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DemoTemplate(SQLModel, table=True):
    """Reusable demo scenario templates"""

    __tablename__ = "demo_templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    # Template metadata
    name: str
    description: str
    category: str = Field(default="general")
    scenario_type: ScenarioType

    # Template structure
    template_data: Dict[str, Any] = Field(sa_column=Column(JSON))
    default_settings: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )

    # Usage tracking
    usage_count: int = Field(default=0)
    is_featured: bool = Field(default=False)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(foreign_key="users.id")


class DemoAsset(SQLModel, table=True):
    """Assets used in demo scenarios (images, videos, files)"""

    __tablename__ = "demo_assets"

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), unique=True, index=True
    )

    # Asset details
    name: str
    description: Optional[str] = None
    asset_type: str  # image, video, document, data_file
    file_path: str
    file_size: int = Field(default=0)
    mime_type: str

    # Usage
    scenarios_used: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    download_count: int = Field(default=0)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(foreign_key="users.id")


class DemoAnalytics(SQLModel, table=True):
    """Analytics data for demo scenarios"""

    __tablename__ = "demo_analytics"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Time period
    date: datetime = Field(index=True)
    hour: int = Field(default=0)  # 0-23

    # Scenario details
    scenario_id: int = Field(foreign_key="demo_scenarios.id", index=True)
    step_id: Optional[int] = Field(foreign_key="demo_steps.id")

    # Metrics
    total_runs: int = Field(default=0)
    successful_runs: int = Field(default=0)
    failed_runs: int = Field(default=0)
    aborted_runs: int = Field(default=0)

    # Performance metrics
    avg_duration_seconds: Optional[float] = None
    avg_step_completion_time: Optional[float] = None
    success_rate: Optional[float] = None

    # User engagement
    unique_runners: int = Field(default=0)
    repeat_runners: int = Field(default=0)

    # Technical metrics
    browser_breakdown: Dict[str, int] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    device_breakdown: Dict[str, int] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    error_types: Dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DemoFeedback(SQLModel, table=True):
    """Feedback on demo scenarios"""

    __tablename__ = "demo_feedback"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    scenario_id: int = Field(foreign_key="demo_scenarios.id", index=True)
    run_id: Optional[int] = Field(foreign_key="demo_runs.id")
    user_id: Optional[int] = Field(foreign_key="users.id")

    # Feedback details
    feedback_type: str = Field(
        default="general"
    )  # general, bug_report, suggestion, improvement
    rating: Optional[int] = Field(ge=1, le=5)
    title: str
    message: str

    # Context
    user_agent: Optional[str] = None
    session_info: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Status
    status: str = Field(default="open")  # open, reviewed, resolved, dismissed
    admin_response: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = Field(foreign_key="users.id")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Export commonly used types
ScenarioTypeChoices = [choice.value for choice in ScenarioType]
ActionTypeChoices = [choice.value for choice in ActionType]
DemoUserTypeChoices = [choice.value for choice in DemoUserType]
ScenarioStatusChoices = [choice.value for choice in ScenarioStatus]
