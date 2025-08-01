"""
Test configuration and fixtures for Seraaj API testing
"""

import pytest
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

# Import the main app and database setup
from main import app
from database import get_session
from models import User, Volunteer, Organisation, Opportunity


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    # Create a temporary database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency overrides"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_volunteer(session: Session) -> User:
    """Create a test volunteer user"""
    user = User(
        email="volunteer@test.com",
        first_name="Test",
        last_name="Volunteer",
        password_hash="$2b$12$test_hash",  # Mock bcrypt hash
        role="volunteer",
        verified=True,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create volunteer profile
    volunteer = Volunteer(
        user_id=user.id,
        full_name="Test Volunteer",
        date_of_birth="1990-01-01",
        phone_number="+1234567890",
        location="Test City",
        skills=["Programming", "Design"],
        availability={"weekdays": True, "weekends": False},
        bio="Test volunteer bio",
        experience_level="intermediate",
        languages=["English", "Arabic"],
        emergency_contact="Emergency Contact",
        profile_completed=True,
    )
    session.add(volunteer)
    session.commit()

    return user


@pytest.fixture
def test_user_organization(session: Session) -> User:
    """Create a test organization user"""
    user = User(
        email="org@test.com",
        first_name="Test",
        last_name="Organization",
        password_hash="$2b$12$test_hash",
        role="organization",
        verified=True,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create organization profile
    organization = Organisation(
        user_id=user.id,
        name="Test Organization",
        description="A test organization for API testing",
        cause_areas=["Education", "Health"],
        website="https://test-org.com",
        phone_number="+1234567890",
        address="123 Test Street",
        city="Test City",
        country="Test Country",
        verified=True,
        profile_completed=True,
        trust_score=0.75,
        trust_level="verified",
    )
    session.add(organization)
    session.commit()

    return user


@pytest.fixture
def test_admin_user(session: Session) -> User:
    """Create a test admin user"""
    user = User(
        email="admin@test.com",
        first_name="Test",
        last_name="Admin",
        password_hash="$2b$12$test_hash",
        role="admin",
        verified=True,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_opportunity(session: Session, test_user_organization: User) -> Opportunity:
    """Create a test opportunity"""
    # Get organization
    org = (
        session.query(Organisation)
        .filter(Organisation.user_id == test_user_organization.id)
        .first()
    )

    opportunity = Opportunity(
        org_id=org.id,
        title="Test Opportunity",
        description="A test opportunity for volunteers",
        skills_required=["Programming"],
        location="Test City",
        time_commitment="5 hours/week",
        start_date="2024-01-01",
        end_date="2024-12-31",
        application_deadline="2024-11-30",
        volunteers_needed=5,
        category="Technology",
        requirements=["Basic programming knowledge"],
        benefits=["Experience", "Certificate"],
        is_remote=True,
        status="active",
    )
    session.add(opportunity)
    session.commit()
    session.refresh(opportunity)
    return opportunity


@pytest.fixture
def auth_headers_volunteer(
    client: TestClient, test_user_volunteer: User
) -> Dict[str, str]:
    """Get authorization headers for volunteer user"""
    response = client.post(
        "/v1/auth/login",
        data={"username": test_user_volunteer.email, "password": "testpassword"},
    )
    # Mock successful login - in real implementation, you'd need proper JWT
    return {"Authorization": f"Bearer mock_token_volunteer_{test_user_volunteer.id}"}


@pytest.fixture
def auth_headers_organization(
    client: TestClient, test_user_organization: User
) -> Dict[str, str]:
    """Get authorization headers for organization user"""
    response = client.post(
        "/v1/auth/login",
        data={"username": test_user_organization.email, "password": "testpassword"},
    )
    return {"Authorization": f"Bearer mock_token_org_{test_user_organization.id}"}


@pytest.fixture
def auth_headers_admin(client: TestClient, test_admin_user: User) -> Dict[str, str]:
    """Get authorization headers for admin user"""
    response = client.post(
        "/v1/auth/login",
        data={"username": test_admin_user.email, "password": "testpassword"},
    )
    return {"Authorization": f"Bearer mock_token_admin_{test_admin_user.id}"}


@pytest.fixture
def sample_application_data() -> Dict[str, Any]:
    """Sample application data for testing"""
    return {
        "cover_letter": "I am very interested in this opportunity...",
        "availability": {
            "start_date": "2024-02-01",
            "hours_per_week": 10,
            "preferred_schedule": "weekends",
        },
        "relevant_experience": "I have 2 years of programming experience",
        "motivation": "I want to contribute to the community",
        "additional_skills": ["Python", "JavaScript"],
        "references": [
            {
                "name": "John Doe",
                "relationship": "Former Colleague",
                "contact": "john@example.com",
            }
        ],
    }


@pytest.fixture
def sample_review_data() -> Dict[str, Any]:
    """Sample review data for testing"""
    return {
        "rating": 5,
        "review_text": "Excellent organization to work with!",
        "would_recommend": True,
        "feedback_categories": {
            "communication": 5,
            "organization": 5,
            "support": 4,
            "impact": 5,
        },
    }


# Test utilities
class TestDataFactory:
    """Factory class for creating test data"""

    @staticmethod
    def create_multiple_volunteers(session: Session, count: int = 5):
        """Create multiple test volunteers"""
        volunteers = []
        for i in range(count):
            user = User(
                email=f"volunteer{i}@test.com",
                first_name=f"Volunteer{i}",
                last_name="Test",
                password_hash="$2b$12$test_hash",
                role="volunteer",
                verified=True,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            volunteer = Volunteer(
                user_id=user.id,
                full_name=f"Volunteer{i} Test",
                date_of_birth="1990-01-01",
                phone_number=f"+123456789{i}",
                location="Test City",
                skills=(
                    ["Programming", "Design"]
                    if i % 2 == 0
                    else ["Marketing", "Writing"]
                ),
                availability={"weekdays": True, "weekends": i % 2 == 0},
                bio=f"Test volunteer {i} bio",
                experience_level="intermediate" if i % 2 == 0 else "beginner",
                languages=["English"],
                emergency_contact=f"Emergency Contact {i}",
                profile_completed=True,
            )
            session.add(volunteer)
            volunteers.append(user)

        session.commit()
        return volunteers

    @staticmethod
    def create_multiple_opportunities(
        session: Session, organization: User, count: int = 3
    ):
        """Create multiple test opportunities"""
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == organization.id)
            .first()
        )
        opportunities = []

        for i in range(count):
            opportunity = Opportunity(
                org_id=org.id,
                title=f"Test Opportunity {i}",
                description=f"Test opportunity {i} description",
                skills_required=["Programming"] if i % 2 == 0 else ["Marketing"],
                location="Test City",
                time_commitment=f"{5 + i} hours/week",
                start_date="2024-01-01",
                end_date="2024-12-31",
                application_deadline="2024-11-30",
                volunteers_needed=5 + i,
                category="Technology" if i % 2 == 0 else "Marketing",
                requirements=[f"Requirement {i}"],
                benefits=["Experience", "Certificate"],
                is_remote=i % 2 == 0,
                status="active" if i < 2 else "draft",
            )
            session.add(opportunity)
            opportunities.append(opportunity)

        session.commit()
        return opportunities


# Test configuration
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up any test files created during testing"""
    yield
    # Cleanup code if needed
    pass


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return Timer()
