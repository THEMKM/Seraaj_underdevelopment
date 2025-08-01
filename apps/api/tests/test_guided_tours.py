"""
Tests for Guided Tours functionality
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session

from models import User
from models.guided_tour import (
    GuidedTour, TourStep, UserTourProgress, TourTemplate,
    TourType, TourStatus, StepType, TourUserRole
)
from services.guided_tour_service import get_guided_tour_service


class TestGuidedTourAPI:
    """Test guided tour API endpoints"""
    
    def test_get_available_tours(self, client: TestClient, auth_headers_volunteer: dict):
        """Test getting available tours for user"""
        response = client.get(
            "/guided-tours/available",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tours" in data["data"]
        assert "total" in data["data"]
    
    def test_get_available_tours_with_filters(self, client: TestClient, auth_headers_volunteer: dict):
        """Test getting available tours with filters"""
        response = client.get(
            "/guided-tours/available?include_completed=true&current_url=/dashboard",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_start_tour_not_found(self, client: TestClient, auth_headers_volunteer: dict):
        """Test starting non-existent tour"""
        response = client.post(
            "/guided-tours/start/non-existent-tour",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
    
    def test_get_tour_progress_not_started(self, client: TestClient, auth_headers_volunteer: dict):
        """Test getting progress for tour not started"""
        response = client.get(
            "/guided-tours/test-tour/progress",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        progress = data["data"]
        assert progress["status"] == TourStatus.NOT_STARTED
        assert progress["completion_percentage"] == 0
    
    def test_skip_tour(self, client: TestClient, auth_headers_volunteer: dict, session: Session, test_user_volunteer: User):
        """Test skipping a tour"""
        # Create a test tour
        tour = GuidedTour(
            title="Test Tour",
            description="Test Description",
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.VOLUNTEER,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        response = client.post(
            f"/guided-tours/skip/{tour.tour_id}",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["skipped"] is True
    
    def test_submit_tour_feedback(self, client: TestClient, auth_headers_volunteer: dict, session: Session, test_user_volunteer: User):
        """Test submitting tour feedback"""
        # Create a test tour
        tour = GuidedTour(
            title="Test Tour",
            description="Test Description", 
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.VOLUNTEER,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        feedback_data = {
            "rating": 5,
            "feedback": "Great tour! Very helpful.",
            "step_id": None
        }
        
        response = client.post(
            f"/guided-tours/{tour.tour_id}/feedback",
            json=feedback_data,
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["submitted"] is True
    
    def test_get_tour_templates(self, client: TestClient, auth_headers_volunteer: dict):
        """Test getting tour templates"""
        response = client.get(
            "/guided-tours/templates",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "templates" in data["data"]
        assert "total" in data["data"]
    
    def test_get_tour_templates_with_filters(self, client: TestClient, auth_headers_volunteer: dict):
        """Test getting tour templates with filters"""
        response = client.get(
            "/guided-tours/templates?category=onboarding&target_role=volunteer",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_create_tour_requires_admin(self, client: TestClient, auth_headers_volunteer: dict):
        """Test that creating tours requires admin access"""
        tour_data = {
            "title": "Test Tour",
            "description": "Test Description",
            "tour_type": TourType.ONBOARDING.value,
            "target_role": TourUserRole.VOLUNTEER.value,
            "entry_url": "/",
            "estimated_duration_minutes": 5,
            "is_mandatory": False,
            "allow_skip": True,
            "steps": []
        }
        
        response = client.post(
            "/guided-tours/create",
            json=tour_data,
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Admin access required" in data["message"]
    
    def test_get_tour_analytics_requires_admin(self, client: TestClient, auth_headers_volunteer: dict):
        """Test that tour analytics requires admin access"""
        response = client.get(
            "/guided-tours/test-tour/analytics",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Admin access required" in data["message"]
    
    def test_get_tours_overview_requires_admin(self, client: TestClient, auth_headers_volunteer: dict):
        """Test that tours overview requires admin access"""
        response = client.get(
            "/guided-tours/analytics/overview",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Admin access required" in data["message"]
    
    def test_get_my_tour_progress(self, client: TestClient, auth_headers_volunteer: dict):
        """Test getting user's tour progress"""
        response = client.get(
            "/guided-tours/my-progress",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        progress_data = data["data"]
        assert "progress" in progress_data
        assert "total_tours" in progress_data
        assert "completed_tours" in progress_data
        assert "in_progress_tours" in progress_data
    
    def test_reset_tour_progress(self, client: TestClient, auth_headers_volunteer: dict, session: Session, test_user_volunteer: User):
        """Test resetting tour progress"""
        # Create a test tour
        tour = GuidedTour(
            title="Reset Test Tour",
            description="Test Description",
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.VOLUNTEER,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        # Create some progress
        progress = UserTourProgress(
            user_id=test_user_volunteer.id,
            tour_id=tour.id,
            status=TourStatus.IN_PROGRESS,
            current_step=3,
            completed_steps=[1, 2],
            started_at=datetime.now()
        )
        session.add(progress)
        session.commit()
        
        response = client.post(
            f"/guided-tours/reset/{tour.tour_id}",
            headers=auth_headers_volunteer
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["reset"] is True


class TestGuidedTourService:
    """Test guided tour service functionality"""
    
    def test_get_available_tours_empty(self, session: Session, test_user_volunteer: User):
        """Test getting available tours when none exist"""
        service = get_guided_tour_service(session)
        
        import asyncio
        tours = asyncio.run(service.get_available_tours(
            user_id=test_user_volunteer.id,
            user_role=TourUserRole.VOLUNTEER
        ))
        
        assert tours == []
    
    def test_start_tour_creates_progress(self, session: Session, test_user_volunteer: User):
        """Test starting a tour creates progress record"""
        # Create a test tour
        tour = GuidedTour(
            title="Test Service Tour",
            description="Test Description",
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.VOLUNTEER,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        # Add a step
        step = TourStep(
            tour_id=tour.id,
            step_number=1,
            step_type=StepType.MODAL,
            title="First Step",
            content="Welcome!"
        )
        session.add(step)
        session.commit()
        
        service = get_guided_tour_service(session)
        
        import asyncio
        result = asyncio.run(service.start_tour(test_user_volunteer.id, tour.tour_id))
        
        assert result is not None
        assert "tour" in result
        assert "progress" in result
        assert "current_step" in result
        assert result["progress"]["status"] == TourStatus.IN_PROGRESS
    
    def test_advance_tour_step(self, session: Session, test_user_volunteer: User):
        """Test advancing through tour steps"""
        # Create tour with multiple steps
        tour = GuidedTour(
            title="Multi-Step Tour",
            description="Test Description",
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.VOLUNTEER,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        # Add steps
        for i in range(1, 4):
            step = TourStep(
                tour_id=tour.id,
                step_number=i,
                step_type=StepType.TOOLTIP,
                title=f"Step {i}",
                content=f"Content for step {i}"
            )
            session.add(step)
        session.commit()
        
        # Create progress
        progress = UserTourProgress(
            user_id=test_user_volunteer.id,
            tour_id=tour.id,
            status=TourStatus.IN_PROGRESS,
            current_step=1,
            started_at=datetime.now()
        )
        session.add(progress)
        session.commit()
        
        service = get_guided_tour_service(session)
        
        import asyncio
        result = asyncio.run(service.advance_tour_step(
            user_id=test_user_volunteer.id,
            tour_id=tour.tour_id,
            step_number=1,
            action="next"
        ))
        
        assert result is not None
        assert result["progress"]["current_step"] == 2
        assert 1 in result["progress"]["completed_steps"]
    
    def test_skip_tour_updates_status(self, session: Session, test_user_volunteer: User):
        """Test skipping tour updates status correctly"""
        # Create tour
        tour = GuidedTour(
            title="Skip Test Tour",
            description="Test Description",
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.VOLUNTEER,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        service = get_guided_tour_service(session)
        
        import asyncio
        success = asyncio.run(service.skip_tour(test_user_volunteer.id, tour.tour_id))
        
        assert success is True
        
        # Verify progress was created with SKIPPED status
        from sqlmodel import select, and_
        progress = session.exec(
            select(UserTourProgress).where(
                and_(
                    UserTourProgress.user_id == test_user_volunteer.id,
                    UserTourProgress.tour_id == tour.id
                )
            )
        ).first()
        
        assert progress is not None
        assert progress.status == TourStatus.SKIPPED
    
    def test_submit_tour_feedback_creates_record(self, session: Session, test_user_volunteer: User):
        """Test submitting feedback creates proper records"""
        # Create tour
        tour = GuidedTour(
            title="Feedback Test Tour",
            description="Test Description",
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.VOLUNTEER,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        service = get_guided_tour_service(session)
        
        import asyncio
        success = asyncio.run(service.submit_tour_feedback(
            user_id=test_user_volunteer.id,
            tour_id=tour.tour_id,
            rating=5,
            feedback="Excellent tour!"
        ))
        
        assert success is True
        
        # Verify feedback record was created
        from sqlmodel import select
        from models.guided_tour import TourFeedback
        
        feedback_record = session.exec(
            select(TourFeedback).where(
                TourFeedback.user_id == test_user_volunteer.id
            )
        ).first()
        
        assert feedback_record is not None
        assert feedback_record.rating == 5
        assert feedback_record.message == "Excellent tour!"
    
    def test_tour_eligibility_check(self, session: Session, test_user_volunteer: User):
        """Test tour eligibility checking"""
        service = get_guided_tour_service(session)
        
        # Create tour with specific requirements
        tour = GuidedTour(
            title="Advanced Tour",
            description="For experienced users",
            tour_type=TourType.ADVANCED_FEATURES,
            target_role=TourUserRole.VOLUNTEER,
            min_user_level=5,
            created_by=1
        )
        
        import asyncio
        is_eligible = asyncio.run(service._check_tour_eligibility(
            tour=tour,
            user_id=test_user_volunteer.id,
            current_url="/dashboard"
        ))
        
        # For now, should return True as we don't have complex eligibility logic
        assert is_eligible is True


class TestTourTemplates:
    """Test tour template functionality"""
    
    def test_tour_template_creation(self, session: Session):
        """Test creating tour template"""
        template = TourTemplate(
            name="Test Template",
            description="Test template description",
            category="onboarding",
            target_role=TourUserRole.VOLUNTEER,
            template_data={
                "title": "Template Tour",
                "steps": [
                    {
                        "step_number": 1,
                        "step_type": StepType.MODAL.value,
                        "title": "Welcome",
                        "content": "Welcome message"
                    }
                ]
            }
        )
        
        session.add(template)
        session.commit()
        session.refresh(template)
        
        assert template.id is not None
        assert template.template_id is not None
        assert template.usage_count == 0
    
    def test_create_tour_from_template(self, session: Session, test_user_volunteer: User):
        """Test creating tour from template"""
        # Create template
        template = TourTemplate(
            name="Onboarding Template",
            description="Standard onboarding flow",
            category="onboarding",
            target_role=TourUserRole.VOLUNTEER,
            template_data={
                "title": "Welcome Tour",
                "description": "Get started with our platform",
                "tour_type": TourType.ONBOARDING.value,
                "entry_url": "/",
                "duration": 5,
                "steps": [
                    {
                        "step_number": 1,
                        "step_type": StepType.MODAL.value,
                        "title": "Welcome!",
                        "content": "Welcome to our platform!"
                    }
                ]
            }
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        service = get_guided_tour_service(session)
        
        customizations = {
            "title": "Custom Welcome Tour",
            "description": "Customized onboarding experience"
        }
        
        import asyncio
        tour_id = asyncio.run(service.create_tour_from_template(
            template_id=template.template_id,
            customizations=customizations,
            created_by=test_user_volunteer.id
        ))
        
        assert tour_id is not None
        
        # Verify tour was created
        from sqlmodel import select
        created_tour = session.exec(
            select(GuidedTour).where(GuidedTour.tour_id == tour_id)
        ).first()
        
        assert created_tour is not None
        assert created_tour.title == "Custom Welcome Tour"
        assert created_tour.description == "Customized onboarding experience"
        
        # Verify template usage was incremented
        session.refresh(template)
        assert template.usage_count == 1


class TestTourAnalytics:
    """Test tour analytics functionality"""
    
    def test_get_tour_analytics_empty(self, session: Session):
        """Test getting analytics for tour with no data"""
        # Create tour
        tour = GuidedTour(
            title="Analytics Test Tour",
            description="Test Description",
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.VOLUNTEER,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        service = get_guided_tour_service(session)
        
        import asyncio
        analytics = asyncio.run(service.get_tour_analytics(tour.tour_id, days=30))
        
        assert analytics is not None
        assert analytics["tour_id"] == tour.tour_id
        assert analytics["metrics"]["total_users"] == 0
        assert analytics["metrics"]["completion_rate"] == 0
    
    def test_tour_analytics_with_data(self, session: Session, test_user_volunteer: User, test_user_organization: User):
        """Test analytics calculation with sample data"""
        # Create tour
        tour = GuidedTour(
            title="Popular Tour",
            description="Well-used tour",
            tour_type=TourType.ONBOARDING,
            target_role=TourUserRole.ALL,
            created_by=1
        )
        session.add(tour)
        session.commit()
        session.refresh(tour)
        
        # Create sample progress records
        progress1 = UserTourProgress(
            user_id=test_user_volunteer.id,
            tour_id=tour.id,
            status=TourStatus.COMPLETED,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            rating=5
        )
        
        progress2 = UserTourProgress(
            user_id=test_user_organization.id,
            tour_id=tour.id,
            status=TourStatus.SKIPPED,
            started_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        session.add(progress1)
        session.add(progress2)
        session.commit()
        
        service = get_guided_tour_service(session)
        
        import asyncio
        analytics = asyncio.run(service.get_tour_analytics(tour.tour_id, days=30))
        
        assert analytics["metrics"]["total_users"] == 2
        assert analytics["metrics"]["completed_users"] == 1
        assert analytics["metrics"]["skipped_users"] == 1
        assert analytics["metrics"]["completion_rate"] == 50.0
        assert analytics["metrics"]["skip_rate"] == 50.0
        assert analytics["metrics"]["average_rating"] == 5.0