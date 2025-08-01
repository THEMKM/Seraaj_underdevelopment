"""
Tests for Demo Scenarios functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import User
from models.demo_scenario import (
    DemoScenario,
    DemoStep,
    DemoRun,
    DemoTemplate,
    ScenarioType,
    ScenarioStatus,
    ActionType,
    DemoUserType,
)
from services.demo_scenario_service import get_demo_scenario_service
from main import app

client = TestClient(app)


@pytest.fixture
def demo_scenario_data():
    """Sample demo scenario data for testing"""
    return {
        "name": "Test Volunteer Journey",
        "description": "Test scenario for volunteer onboarding",
        "scenario_type": ScenarioType.FULL_JOURNEY,
        "target_audience": "test",
        "duration_minutes": 5,
        "difficulty_level": "beginner",
        "steps": [
            {
                "step_number": 1,
                "action_type": ActionType.NAVIGATE,
                "title": "Navigate to Homepage",
                "description": "Go to the main page",
                "target_url": "/",
                "duration_seconds": 2,
                "annotation_text": "Welcome to our platform",
            },
            {
                "step_number": 2,
                "action_type": ActionType.CREATE_USER,
                "title": "Create Account",
                "description": "Register new volunteer",
                "demo_user_type": DemoUserType.VOLUNTEER,
                "duration_seconds": 3,
                "user_data": {"name": "Test Volunteer", "email": "test@example.com"},
            },
        ],
    }


@pytest.fixture
def demo_template_data():
    """Sample demo template data for testing"""
    return {
        "name": "Test Template",
        "description": "Template for testing",
        "category": "test",
        "scenario_type": ScenarioType.FEATURE_SHOWCASE,
        "template_data": {
            "name": "Template Scenario",
            "description": "Generated from template",
            "scenario_type": ScenarioType.FEATURE_SHOWCASE,
            "steps": [
                {
                    "step_number": 1,
                    "action_type": ActionType.LOGIN,
                    "title": "Login Step",
                    "description": "Login to account",
                    "demo_user_type": DemoUserType.VOLUNTEER,
                }
            ],
        },
    }


class TestDemoScenariosAPI:
    """Test demo scenarios API endpoints"""

    def test_get_available_scenarios(self, db_session: Session):
        """Test getting available scenarios"""
        # Create test scenario
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()

        response = client.get("/demo-scenarios/available")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["scenarios"]) >= 1

    def test_get_available_scenarios_with_filters(self, db_session: Session):
        """Test getting scenarios with filters"""
        response = client.get(
            "/demo-scenarios/available?scenario_type=full_journey&difficulty_level=beginner"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_start_demo_scenario(self, db_session: Session):
        """Test starting a demo scenario"""
        # Create test scenario with steps
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        step = DemoStep(
            scenario_id=scenario.id,
            step_number=1,
            action_type=ActionType.NAVIGATE,
            title="First Step",
            description="Navigate somewhere",
        )
        db_session.add(step)
        db_session.commit()

        response = client.post(
            f"/demo-scenarios/start/{scenario.scenario_id}",
            json={"environment_info": {"browser": "chrome"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "demo_run" in data
        assert "run_id" in data["demo_run"]

    def test_start_invalid_scenario(self):
        """Test starting non-existent scenario"""
        response = client.post("/demo-scenarios/start/invalid-id", json={})
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False

    def test_get_demo_run_status(self, db_session: Session):
        """Test getting demo run status"""
        # Create test scenario and run
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        demo_run = DemoRun(
            scenario_id=scenario.id,
            session_id="test-session",
            status="running",
            current_step=1,
        )
        db_session.add(demo_run)
        db_session.commit()
        db_session.refresh(demo_run)

        response = client.get(f"/demo-scenarios/run/{demo_run.run_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["demo_run"]["status"] == "running"

    def test_execute_demo_step(self, db_session: Session):
        """Test executing a demo step"""
        # Create test scenario, step, and run
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        step = DemoStep(
            scenario_id=scenario.id,
            step_number=1,
            action_type=ActionType.NAVIGATE,
            title="First Step",
            description="Navigate somewhere",
        )
        db_session.add(step)
        db_session.commit()

        demo_run = DemoRun(
            scenario_id=scenario.id,
            session_id="test-session",
            status="running",
            current_step=1,
        )
        db_session.add(demo_run)
        db_session.commit()
        db_session.refresh(demo_run)

        response = client.post(
            f"/demo-scenarios/run/{demo_run.run_id}/execute/1",
            json={"execution_context": {"test": "data"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data

    def test_abort_demo_run(self, db_session: Session):
        """Test aborting a demo run"""
        # Create test scenario and run
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        demo_run = DemoRun(
            scenario_id=scenario.id, session_id="test-session", status="running"
        )
        db_session.add(demo_run)
        db_session.commit()
        db_session.refresh(demo_run)

        response = client.post(
            f"/demo-scenarios/run/{demo_run.run_id}/abort",
            params={"reason": "test_abort"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_submit_demo_feedback(self, db_session: Session):
        """Test submitting demo feedback"""
        # Create test scenario
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        feedback_data = {
            "feedback_type": "general",
            "rating": 5,
            "title": "Great Demo",
            "message": "Really helpful demonstration",
        }

        response = client.post(
            f"/demo-scenarios/scenarios/{scenario.scenario_id}/feedback",
            json=feedback_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_demo_templates(self, db_session: Session):
        """Test getting demo templates"""
        # Create test template
        template = DemoTemplate(
            name="Test Template",
            description="Test description",
            category="test",
            scenario_type=ScenarioType.FEATURE_SHOWCASE,
            template_data={"test": "data"},
        )
        db_session.add(template)
        db_session.commit()

        response = client.get("/demo-scenarios/templates")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["templates"]) >= 1


class TestDemoScenarioService:
    """Test demo scenario service functionality"""

    def test_get_available_scenarios(self, db_session: Session):
        """Test service method for getting scenarios"""
        service = get_demo_scenario_service(db_session)

        # Create test scenarios
        scenario1 = DemoScenario(
            name="Scenario 1",
            description="First scenario",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
            difficulty_level="beginner",
        )
        scenario2 = DemoScenario(
            name="Scenario 2",
            description="Second scenario",
            scenario_type=ScenarioType.FEATURE_SHOWCASE,
            status=ScenarioStatus.ACTIVE,
            difficulty_level="intermediate",
        )
        db_session.add_all([scenario1, scenario2])
        db_session.commit()

        # Test without filters
        scenarios = service.get_available_scenarios()
        assert len(scenarios) >= 2

        # Test with filters
        beginner_scenarios = service.get_available_scenarios(
            difficulty_level="beginner"
        )
        assert len(beginner_scenarios) >= 1

    def test_start_demo_scenario(self, db_session: Session):
        """Test starting a demo scenario"""
        service = get_demo_scenario_service(db_session)

        # Create test scenario
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        # Add step
        step = DemoStep(
            scenario_id=scenario.id,
            step_number=1,
            action_type=ActionType.NAVIGATE,
            title="First Step",
            description="Navigate somewhere",
        )
        db_session.add(step)
        db_session.commit()

        # Start scenario
        result = service.start_demo_scenario(
            scenario_id=scenario.scenario_id,
            session_id="test-session",
            environment_info={"browser": "chrome"},
        )

        assert "run_id" in result
        assert "scenario" in result
        assert "current_step" in result

    def test_execute_demo_step(self, db_session: Session):
        """Test executing demo steps"""
        service = get_demo_scenario_service(db_session)

        # Create test scenario and run
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        step = DemoStep(
            scenario_id=scenario.id,
            step_number=1,
            action_type=ActionType.NAVIGATE,
            title="First Step",
            description="Navigate somewhere",
        )
        db_session.add(step)
        db_session.commit()

        demo_run = DemoRun(
            scenario_id=scenario.id,
            session_id="test-session",
            status="running",
            current_step=1,
        )
        db_session.add(demo_run)
        db_session.commit()
        db_session.refresh(demo_run)

        # Execute step
        result = service.execute_demo_step(run_id=demo_run.run_id, step_number=1)

        assert "step_result" in result
        assert result["step_result"]["success"] is True

    def test_create_scenario_from_template(self, db_session: Session):
        """Test creating scenario from template"""
        service = get_demo_scenario_service(db_session)

        # Create test user
        user = User(email="test@example.com", full_name="Test User", role="admin")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create template
        template = DemoTemplate(
            name="Test Template",
            description="Test description",
            category="test",
            scenario_type=ScenarioType.FEATURE_SHOWCASE,
            template_data={
                "name": "Template Scenario",
                "description": "From template",
                "scenario_type": "feature_showcase",
                "steps": [
                    {
                        "step_number": 1,
                        "action_type": "navigate",
                        "title": "Step 1",
                        "description": "First step",
                        "demo_user_type": "volunteer",
                    }
                ],
            },
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        # Create scenario from template
        scenario_id = service.create_scenario_from_template(
            template_id=template.template_id,
            customizations={"name": "Custom Scenario"},
            created_by=user.id,
        )

        assert scenario_id is not None

        # Verify scenario was created
        created_scenario = (
            db_session.query(DemoScenario)
            .filter(DemoScenario.scenario_id == scenario_id)
            .first()
        )
        assert created_scenario is not None
        assert created_scenario.name == "Custom Scenario"


class TestDemoScenarioModels:
    """Test demo scenario data models"""

    def test_demo_scenario_creation(self, db_session: Session):
        """Test creating demo scenario"""
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
            target_audience="test",
            duration_minutes=10,
            difficulty_level="beginner",
        )

        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        assert scenario.id is not None
        assert scenario.scenario_id is not None
        assert scenario.name == "Test Scenario"
        assert scenario.status == ScenarioStatus.DRAFT

    def test_demo_step_creation(self, db_session: Session):
        """Test creating demo step"""
        # First create scenario
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        # Create step
        step = DemoStep(
            scenario_id=scenario.id,
            step_number=1,
            action_type=ActionType.NAVIGATE,
            title="First Step",
            description="Navigate to homepage",
            target_url="/",
            duration_seconds=3,
        )

        db_session.add(step)
        db_session.commit()
        db_session.refresh(step)

        assert step.id is not None
        assert step.step_id is not None
        assert step.scenario_id == scenario.id
        assert step.action_type == ActionType.NAVIGATE

    def test_demo_run_creation(self, db_session: Session):
        """Test creating demo run"""
        # Create scenario first
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        # Create run
        demo_run = DemoRun(
            scenario_id=scenario.id,
            session_id="test-session-123",
            status="running",
            current_step=1,
            browser="chrome",
            device_type="desktop",
        )

        db_session.add(demo_run)
        db_session.commit()
        db_session.refresh(demo_run)

        assert demo_run.id is not None
        assert demo_run.run_id is not None
        assert demo_run.scenario_id == scenario.id
        assert demo_run.status == "running"

    def test_scenario_step_relationship(self, db_session: Session):
        """Test relationship between scenario and steps"""
        scenario = DemoScenario(
            name="Test Scenario",
            description="Test description",
            scenario_type=ScenarioType.FULL_JOURNEY,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        # Create multiple steps
        for i in range(3):
            step = DemoStep(
                scenario_id=scenario.id,
                step_number=i + 1,
                action_type=ActionType.NAVIGATE,
                title=f"Step {i + 1}",
                description=f"Step {i + 1} description",
            )
            db_session.add(step)

        db_session.commit()

        # Test relationship
        db_session.refresh(scenario)
        assert len(scenario.steps) == 3
        assert all(step.scenario_id == scenario.id for step in scenario.steps)


# Integration tests would go here
class TestDemoScenariosIntegration:
    """Integration tests for demo scenarios"""

    def test_full_demo_workflow(self, db_session: Session):
        """Test complete demo scenario workflow"""
        service = get_demo_scenario_service(db_session)

        # 1. Create scenario
        scenario = DemoScenario(
            name="Integration Test Scenario",
            description="Full workflow test",
            scenario_type=ScenarioType.FULL_JOURNEY,
            status=ScenarioStatus.ACTIVE,
        )
        db_session.add(scenario)
        db_session.commit()
        db_session.refresh(scenario)

        # 2. Add steps
        for i in range(2):
            step = DemoStep(
                scenario_id=scenario.id,
                step_number=i + 1,
                action_type=ActionType.NAVIGATE if i == 0 else ActionType.CLICK_BUTTON,
                title=f"Step {i + 1}",
                description=f"Step {i + 1} description",
            )
            db_session.add(step)
        db_session.commit()

        # 3. Start demo
        demo_result = service.start_demo_scenario(
            scenario_id=scenario.scenario_id, session_id="integration-test-session"
        )
        run_id = demo_result["run_id"]

        # 4. Execute steps
        for step_num in [1, 2]:
            step_result = service.execute_demo_step(run_id=run_id, step_number=step_num)
            assert step_result["step_result"]["success"] is True

        # 5. Submit feedback
        feedback_success = service.submit_demo_feedback(
            scenario_id=scenario.scenario_id,
            run_id=run_id,
            feedback_data={
                "rating": 5,
                "title": "Great Demo",
                "message": "Integration test feedback",
            },
        )
        assert feedback_success is True

        # 6. Check analytics
        analytics = service.get_scenario_analytics(
            scenario_id=scenario.scenario_id, days=1
        )
        assert analytics["overview"]["total_runs"] >= 1
