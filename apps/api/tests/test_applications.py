"""
Applications API Tests
"""

from fastapi.testclient import TestClient
from sqlmodel import Session
from models import User, Opportunity
from tests.conftest import TestDataFactory


class TestApplicationEndpoints:
    """Test application CRUD operations"""

    def test_create_application_success(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        session: Session,
    ):
        """Test successful application creation"""
        # Make opportunity active so applications are allowed
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        application_data = {
            "opportunity_id": test_opportunity.id,
            **sample_application_data,
        }

        response = client.post(
            "/v1/applications", json=application_data, headers=auth_headers_volunteer
        )
        assert response.status_code == 201

        data = response.json()
        assert data["opportunity_id"] == test_opportunity.id
        assert data["cover_letter"] == sample_application_data["cover_letter"]
        assert data["status"] == "submitted"
        assert "id" in data
        assert "created_at" in data
        assert "application_steps" in data

    def test_create_application_organization_forbidden(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
    ):
        """Test that organizations cannot create applications"""
        application_data = {
            "opportunity_id": test_opportunity.id,
            **sample_application_data,
        }

        response = client.post(
            "/v1/applications", json=application_data, headers=auth_headers_organization
        )
        assert response.status_code == 403

    def test_create_application_nonexistent_opportunity(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        sample_application_data: dict,
    ):
        """Test application creation for non-existent opportunity"""
        application_data = {"opportunity_id": 99999, **sample_application_data}

        response = client.post(
            "/v1/applications", json=application_data, headers=auth_headers_volunteer
        )
        assert response.status_code == 404

    def test_create_application_duplicate(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        session: Session,
    ):
        """Test creating duplicate application for same opportunity"""
        # Make opportunity active
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        application_data = {
            "opportunity_id": test_opportunity.id,
            **sample_application_data,
        }

        # Create first application
        response1 = client.post(
            "/v1/applications", json=application_data, headers=auth_headers_volunteer
        )
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = client.post(
            "/v1/applications", json=application_data, headers=auth_headers_volunteer
        )
        assert response2.status_code == 400
        assert "already applied" in response2.json()["detail"].lower()

    def test_get_my_applications_volunteer(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        session: Session,
        test_user_organization: User,
    ):
        """Test getting volunteer's own applications"""
        # Create multiple opportunities and applications
        opportunities = TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=3
        )

        response = client.get(
            "/v1/applications/my-applications", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        data = response.json()
        assert "applications" in data
        assert "total_count" in data

        if data["applications"]:
            app = data["applications"][0]
            assert "id" in app
            assert "opportunity" in app
            assert "status" in app
            assert "created_at" in app

    def test_get_opportunity_applications_organization(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
    ):
        """Test getting applications for organization's opportunity"""
        response = client.get(
            f"/v1/opportunities/{test_opportunity.id}/applications",
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        data = response.json()
        assert "applications" in data
        assert "total_count" in data

        if data["applications"]:
            app = data["applications"][0]
            assert "volunteer" in app
            assert "status" in app
            assert "created_at" in app

    def test_get_opportunity_applications_volunteer_forbidden(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
    ):
        """Test that volunteers cannot see other applications"""
        response = client.get(
            f"/v1/opportunities/{test_opportunity.id}/applications",
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 403

    def test_get_application_details_volunteer_own(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        session: Session,
    ):
        """Test getting details of volunteer's own application"""
        # Create application first
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        app_response = client.post(
            "/v1/applications",
            json={"opportunity_id": test_opportunity.id, **sample_application_data},
            headers=auth_headers_volunteer,
        )
        app_id = app_response.json()["id"]

        response = client.get(
            f"/v1/applications/{app_id}", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == app_id
        assert "opportunity" in data
        assert "status" in data
        assert "cover_letter" in data
        assert "timeline" in data

    def test_update_application_status_organization(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        auth_headers_volunteer: dict,
        session: Session,
    ):
        """Test organization updating application status"""
        # Create application first
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        app_response = client.post(
            "/v1/applications",
            json={"opportunity_id": test_opportunity.id, **sample_application_data},
            headers=auth_headers_volunteer,
        )
        app_id = app_response.json()["id"]

        # Update status
        status_update = {
            "status": "under_review",
            "notes": "Application looks promising, scheduling interview",
        }

        response = client.put(
            f"/v1/applications/{app_id}/status",
            json=status_update,
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "under_review"
        assert "updated_at" in data

    def test_approve_application_success(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        auth_headers_volunteer: dict,
        session: Session,
    ):
        """Test approving an application"""
        # Create application first
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        app_response = client.post(
            "/v1/applications",
            json={"opportunity_id": test_opportunity.id, **sample_application_data},
            headers=auth_headers_volunteer,
        )
        app_id = app_response.json()["id"]

        # Approve application
        approval_data = {
            "welcome_message": "Welcome to our team! We're excited to work with you.",
            "next_steps": "Please check your email for onboarding instructions",
            "start_date": "2024-03-01",
        }

        response = client.post(
            f"/v1/applications/{app_id}/approve",
            json=approval_data,
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "approved"
        assert "approved_at" in data

    def test_reject_application_success(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        auth_headers_volunteer: dict,
        session: Session,
    ):
        """Test rejecting an application"""
        # Create application first
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        app_response = client.post(
            "/v1/applications",
            json={"opportunity_id": test_opportunity.id, **sample_application_data},
            headers=auth_headers_volunteer,
        )
        app_id = app_response.json()["id"]

        # Reject application
        rejection_data = {
            "reason": "Unfortunately, we've decided to go with candidates with more specific experience",
            "feedback": "Your application was strong, please consider applying for future opportunities",
        }

        response = client.post(
            f"/v1/applications/{app_id}/reject",
            json=rejection_data,
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "rejected"
        assert "rejected_at" in data

    def test_withdraw_application_volunteer(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        session: Session,
    ):
        """Test volunteer withdrawing their own application"""
        # Create application first
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        app_response = client.post(
            "/v1/applications",
            json={"opportunity_id": test_opportunity.id, **sample_application_data},
            headers=auth_headers_volunteer,
        )
        app_id = app_response.json()["id"]

        # Withdraw application
        withdrawal_data = {
            "reason": "Found another opportunity that better fits my schedule"
        }

        response = client.post(
            f"/v1/applications/{app_id}/withdraw",
            json=withdrawal_data,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "withdrawn"
        assert "withdrawn_at" in data


class TestApplicationWorkflow:
    """Test multi-step application workflow"""

    def test_save_application_draft(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        session: Session,
    ):
        """Test saving application as draft"""
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        draft_data = {
            "opportunity_id": test_opportunity.id,
            "cover_letter": "Draft cover letter...",
            "save_as_draft": True,
        }

        response = client.post(
            "/v1/applications", json=draft_data, headers=auth_headers_volunteer
        )
        assert response.status_code == 201

        data = response.json()
        assert data["status"] == "draft"
        assert data["cover_letter"] == draft_data["cover_letter"]

    def test_complete_application_from_draft(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        session: Session,
    ):
        """Test completing application from draft status"""
        # Create draft first
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        draft_response = client.post(
            "/v1/applications",
            json={
                "opportunity_id": test_opportunity.id,
                "cover_letter": "Draft cover letter...",
                "save_as_draft": True,
            },
            headers=auth_headers_volunteer,
        )
        app_id = draft_response.json()["id"]

        # Complete the application
        complete_data = {**sample_application_data, "submit_application": True}

        response = client.put(
            f"/v1/applications/{app_id}",
            json=complete_data,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "submitted"
        assert "submitted_at" in data

    def test_application_step_completion(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        session: Session,
    ):
        """Test multi-step application completion"""
        # Create application
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        app_response = client.post(
            "/v1/applications",
            json={"opportunity_id": test_opportunity.id, **sample_application_data},
            headers=auth_headers_volunteer,
        )
        app_id = app_response.json()["id"]

        # Complete various steps
        steps_data = [
            {"step": "documents", "completed": True, "data": {"resume_uploaded": True}},
            {"step": "references", "completed": True, "data": {"references_count": 2}},
            {"step": "assessment", "completed": True, "data": {"score": 85}},
        ]

        for step_data in steps_data:
            response = client.post(
                f"/v1/applications/{app_id}/steps/{step_data['step']}",
                json=step_data,
                headers=auth_headers_volunteer,
            )
            assert response.status_code == 200


class TestApplicationFilters:
    """Test application filtering and search"""

    def test_filter_applications_by_status(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
    ):
        """Test filtering applications by status"""
        response = client.get(
            f"/v1/opportunities/{test_opportunity.id}/applications?status=submitted",
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        data = response.json()
        for app in data["applications"]:
            assert app["status"] == "submitted"

    def test_filter_applications_by_date_range(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
    ):
        """Test filtering applications by date range"""
        response = client.get(
            f"/v1/opportunities/{test_opportunity.id}/applications?"
            "start_date=2024-01-01&end_date=2024-12-31",
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

    def test_search_applications_by_volunteer_name(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
    ):
        """Test searching applications by volunteer name"""
        response = client.get(
            f"/v1/opportunities/{test_opportunity.id}/applications?search=Test Volunteer",
            headers=auth_headers_organization,
        )
        assert response.status_code == 200


class TestApplicationAnalytics:
    """Test application analytics endpoints"""

    def test_get_application_statistics(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
    ):
        """Test getting application statistics for opportunity"""
        response = client.get(
            f"/v1/opportunities/{test_opportunity.id}/applications/analytics",
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        data = response.json()
        assert "total_applications" in data
        assert "status_breakdown" in data
        assert "application_rate" in data
        assert "average_response_time" in data

    def test_get_volunteer_application_history(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting volunteer's application history and statistics"""
        response = client.get(
            "/v1/applications/my-statistics", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        data = response.json()
        assert "total_applications" in data
        assert "success_rate" in data
        assert "application_timeline" in data


class TestApplicationNotifications:
    """Test application-related notifications"""

    def test_application_status_change_notification(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        auth_headers_volunteer: dict,
        session: Session,
    ):
        """Test that status changes trigger notifications"""
        # Create application
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        app_response = client.post(
            "/v1/applications",
            json={"opportunity_id": test_opportunity.id, **sample_application_data},
            headers=auth_headers_volunteer,
        )
        app_id = app_response.json()["id"]

        # Update status and check for notification
        response = client.put(
            f"/v1/applications/{app_id}/status",
            json={"status": "under_review", "notes": "Reviewing application"},
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        # Check volunteer notifications
        notifications_response = client.get(
            "/v1/notifications", headers=auth_headers_volunteer
        )
        if notifications_response.status_code == 200:
            notifications = notifications_response.json()
            # Should have notification about application status change
            assert any(
                "application" in notif.get("message", "").lower()
                for notif in notifications.get("notifications", [])
            )


class TestApplicationValidation:
    """Test application data validation"""

    def test_create_application_missing_required_fields(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        session: Session,
    ):
        """Test application creation with missing required fields"""
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        incomplete_data = {
            "opportunity_id": test_opportunity.id
            # Missing cover_letter and other required fields
        }

        response = client.post(
            "/v1/applications", json=incomplete_data, headers=auth_headers_volunteer
        )
        assert response.status_code == 422  # Validation error

    def test_create_application_invalid_availability(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        session: Session,
    ):
        """Test application with invalid availability data"""
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        invalid_data = {
            **sample_application_data,
            "opportunity_id": test_opportunity.id,
            "availability": {
                "start_date": "2024-12-31",
                "end_date": "2024-01-01",  # End before start
                "hours_per_week": -5,  # Negative hours
            },
        }

        response = client.post(
            "/v1/applications", json=invalid_data, headers=auth_headers_volunteer
        )
        assert response.status_code == 400
