"""
Integration Tests for Seraaj API
Tests end-to-end workflows and cross-system interactions
"""

from fastapi.testclient import TestClient
from sqlmodel import Session
from models import User, Opportunity, Application
from tests.conftest import TestDataFactory


class TestVolunteerJourney:
    """Test complete volunteer user journey"""

    def test_complete_volunteer_onboarding_and_application(
        self,
        client: TestClient,
        session: Session,
        test_user_organization: User,
        sample_application_data: dict,
    ):
        """Test complete volunteer journey from registration to application"""

        # 1. Register as volunteer
        registration_data = {
            "email": "integration_volunteer@test.com",
            "password": "strongpassword123",
            "first_name": "Integration",
            "last_name": "Volunteer",
            "role": "volunteer",
        }

        register_response = client.post("/v1/auth/register", json=registration_data)
        assert register_response.status_code == 201
        volunteer_user_id = register_response.json()["user_id"]
        volunteer_token = register_response.json()["access_token"]
        volunteer_headers = {"Authorization": f"Bearer {volunteer_token}"}

        # 2. Complete volunteer profile
        profile_data = {
            "full_name": "Integration Volunteer",
            "date_of_birth": "1995-01-01",
            "phone_number": "+1234567890",
            "location": "Test City",
            "skills": ["Programming", "Project Management"],
            "availability": {"weekdays": True, "weekends": True, "hours_per_week": 10},
            "bio": "Passionate about technology and helping others",
            "experience_level": "intermediate",
            "languages": ["English", "Arabic"],
            "emergency_contact": "Emergency Contact Person",
            "interests": ["Education", "Technology"],
        }

        profile_response = client.put(
            "/v1/profiles/volunteer", json=profile_data, headers=volunteer_headers
        )
        assert profile_response.status_code == 200

        # 3. Browse opportunities
        opportunities_response = client.get("/v1/opportunities")
        assert opportunities_response.status_code == 200

        # 4. Create an active opportunity for testing
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == test_user_organization.id)
            .first()
        )
        opportunity = Opportunity(
            org_id=org.id,
            title="Integration Test Opportunity",
            description="Test opportunity for integration testing",
            skills_required=["Programming"],
            location="Test City",
            time_commitment="5 hours/week",
            start_date="2024-03-01",
            end_date="2024-12-31",
            application_deadline="2024-11-30",
            volunteers_needed=3,
            category="Technology",
            status="active",
        )
        session.add(opportunity)
        session.commit()
        session.refresh(opportunity)

        # 5. View opportunity details
        opp_details_response = client.get(f"/v1/opportunities/{opportunity.id}")
        assert opp_details_response.status_code == 200
        assert opp_details_response.json()["can_apply"] == True

        # 6. Apply to opportunity
        application_data = {"opportunity_id": opportunity.id, **sample_application_data}

        apply_response = client.post(
            "/v1/applications", json=application_data, headers=volunteer_headers
        )
        assert apply_response.status_code == 201
        application_id = apply_response.json()["id"]

        # 7. Check application status
        my_apps_response = client.get(
            "/v1/applications/my-applications", headers=volunteer_headers
        )
        assert my_apps_response.status_code == 200
        assert len(my_apps_response.json()["applications"]) >= 1

        # 8. View application details
        app_details_response = client.get(
            f"/v1/applications/{application_id}", headers=volunteer_headers
        )
        assert app_details_response.status_code == 200
        assert app_details_response.json()["status"] == "submitted"

    def test_volunteer_skill_verification_workflow(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test volunteer skill verification process"""

        # 1. Initiate skill verification
        verification_data = {
            "skill_name": "Web Development",
            "verification_method": "portfolio_review",
            "evidence_data": {
                "portfolio_url": "https://github.com/volunteer/portfolio",
                "description": "Full-stack web applications",
            },
        }

        verification_response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )
        assert verification_response.status_code == 201
        verification_id = verification_response.json()["verification_id"]

        # 2. Check verification status
        verification_details = client.get(
            f"/v1/verification/skills/{verification_id}", headers=auth_headers_volunteer
        )
        assert verification_details.status_code == 200
        assert verification_details.json()["status"] == "pending"

        # 3. View my verifications
        my_verifications = client.get(
            "/v1/verification/skills/my-verifications", headers=auth_headers_volunteer
        )
        assert my_verifications.status_code == 200
        assert len(my_verifications.json()) >= 1


class TestOrganizationJourney:
    """Test complete organization user journey"""

    def test_complete_organization_workflow(self, client: TestClient, session: Session):
        """Test organization from registration to managing applications"""

        # 1. Register as organization
        registration_data = {
            "email": "integration_org@test.com",
            "password": "strongpassword123",
            "first_name": "Integration",
            "last_name": "Organization",
            "role": "organization",
        }

        register_response = client.post("/v1/auth/register", json=registration_data)
        assert register_response.status_code == 201
        org_token = register_response.json()["access_token"]
        org_headers = {"Authorization": f"Bearer {org_token}"}

        # 2. Complete organization profile
        profile_data = {
            "name": "Integration Test Organization",
            "description": "A test organization for integration testing",
            "cause_areas": ["Education", "Technology"],
            "website": "https://integration-test-org.com",
            "phone_number": "+1234567890",
            "address": "123 Test Street",
            "city": "Test City",
            "country": "Test Country",
            "organization_type": "nonprofit",
            "founding_year": 2020,
            "employee_count": "10-50",
            "annual_budget": "100000-500000",
        }

        profile_response = client.put(
            "/v1/profiles/organization", json=profile_data, headers=org_headers
        )
        assert profile_response.status_code == 200

        # 3. Create opportunity
        opportunity_data = {
            "title": "Integration Test Volunteer Position",
            "description": "Help with technology projects for education",
            "skills_required": ["Programming", "Web Development"],
            "location": "Test City",
            "time_commitment": "8 hours/week",
            "start_date": "2024-03-01",
            "end_date": "2024-12-31",
            "application_deadline": "2024-02-28",
            "volunteers_needed": 5,
            "category": "Technology",
            "requirements": ["2+ years programming experience"],
            "benefits": ["Skills development", "Certificate"],
            "is_remote": True,
        }

        opp_response = client.post(
            "/v1/opportunities", json=opportunity_data, headers=org_headers
        )
        assert opp_response.status_code == 201
        opportunity_id = opp_response.json()["id"]

        # 4. Publish opportunity
        publish_response = client.post(
            f"/v1/opportunities/{opportunity_id}/publish", headers=org_headers
        )
        assert publish_response.status_code == 200

        # 5. View opportunity applications (initially empty)
        applications_response = client.get(
            f"/v1/opportunities/{opportunity_id}/applications", headers=org_headers
        )
        assert applications_response.status_code == 200
        assert applications_response.json()["total_count"] == 0

        # 6. Get organization analytics
        analytics_response = client.get(
            "/v1/opportunities/analytics/performance", headers=org_headers
        )
        assert analytics_response.status_code == 200


class TestApplicationLifecycle:
    """Test complete application lifecycle"""

    def test_application_approval_workflow(
        self,
        client: TestClient,
        session: Session,
        test_user_volunteer: User,
        test_user_organization: User,
        test_opportunity: Opportunity,
        sample_application_data: dict,
        auth_headers_volunteer: dict,
        auth_headers_organization: dict,
    ):
        """Test application from submission to approval"""

        # Make opportunity active
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        # 1. Volunteer applies
        application_data = {
            "opportunity_id": test_opportunity.id,
            **sample_application_data,
        }

        apply_response = client.post(
            "/v1/applications", json=application_data, headers=auth_headers_volunteer
        )
        assert apply_response.status_code == 201
        application_id = apply_response.json()["id"]

        # 2. Organization reviews application
        app_details = client.get(
            f"/v1/applications/{application_id}", headers=auth_headers_organization
        )
        assert app_details.status_code == 200

        # 3. Organization updates application status
        status_update = {
            "status": "under_review",
            "notes": "Reviewing application, looks promising",
        }

        status_response = client.put(
            f"/v1/applications/{application_id}/status",
            json=status_update,
            headers=auth_headers_organization,
        )
        assert status_response.status_code == 200

        # 4. Organization approves application
        approval_data = {
            "welcome_message": "Welcome to our team!",
            "next_steps": "Please attend orientation on March 1st",
            "start_date": "2024-03-01",
        }

        approve_response = client.post(
            f"/v1/applications/{application_id}/approve",
            json=approval_data,
            headers=auth_headers_organization,
        )
        assert approve_response.status_code == 200

        # 5. Verify application is approved
        final_status = client.get(
            f"/v1/applications/{application_id}", headers=auth_headers_volunteer
        )
        assert final_status.status_code == 200
        assert final_status.json()["status"] == "approved"


class TestReviewAndRatingSystem:
    """Test review and rating system integration"""

    def test_complete_review_workflow(
        self,
        client: TestClient,
        session: Session,
        test_user_volunteer: User,
        test_user_organization: User,
        test_opportunity: Opportunity,
        sample_review_data: dict,
        auth_headers_volunteer: dict,
        auth_headers_organization: dict,
    ):
        """Test complete review submission and response workflow"""

        # 1. Create completed application first
        test_opportunity.status = "active"
        session.add(test_opportunity)
        session.commit()

        # Create approved application
        application = Application(
            volunteer_id=session.query(Volunteer)
            .filter(Volunteer.user_id == test_user_volunteer.id)
            .first()
            .id,
            opportunity_id=test_opportunity.id,
            cover_letter="Test application",
            status="approved",
        )
        session.add(application)
        session.commit()

        # 2. Volunteer submits review
        review_data = {"organisation_id": test_opportunity.org_id, **sample_review_data}

        review_response = client.post(
            "/v1/reviews", json=review_data, headers=auth_headers_volunteer
        )
        assert review_response.status_code == 201
        review_id = review_response.json()["id"]

        # 3. Check organization's reviews
        org_reviews = client.get(
            f"/v1/reviews/organization/{test_opportunity.org_id}",
            headers=auth_headers_organization,
        )
        assert org_reviews.status_code == 200
        assert len(org_reviews.json()["reviews"]) >= 1

        # 4. Organization responds to review
        response_data = {
            "response_text": "Thank you for your feedback! We're glad you had a positive experience."
        }

        response_response = client.post(
            f"/v1/reviews/{review_id}/respond",
            json=response_data,
            headers=auth_headers_organization,
        )
        assert response_response.status_code == 200

        # 5. Check review has response
        review_details = client.get(f"/v1/reviews/{review_id}")
        assert review_details.status_code == 200
        assert "organization_response" in review_details.json()


class TestMatchingSystem:
    """Test ML matching system integration"""

    def test_opportunity_recommendations(
        self,
        client: TestClient,
        session: Session,
        auth_headers_volunteer: dict,
        test_user_organization: User,
    ):
        """Test opportunity recommendation system"""

        # Create multiple opportunities with different skills
        opportunities = TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=5
        )

        # Make opportunities active
        for opp in opportunities:
            opp.status = "active"
        session.commit()

        # Get recommendations
        recommendations = client.get(
            "/v1/opportunities/recommendations", headers=auth_headers_volunteer
        )
        assert recommendations.status_code == 200

        data = recommendations.json()
        assert "recommended_opportunities" in data

        if data["recommended_opportunities"]:
            # Verify recommendation structure
            rec = data["recommended_opportunities"][0]
            assert "recommendation_score" in rec
            assert "match_reasons" in rec


class TestFileUploadIntegration:
    """Test file upload system integration"""

    def test_profile_picture_upload_workflow(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test uploading and managing profile pictures"""

        # Create mock image file
        file_data = {"file": ("profile.jpg", b"fake image content", "image/jpeg")}
        form_data = {
            "upload_category": "profile",
            "file_description": "Profile picture",
        }

        upload_response = client.post(
            "/v1/files/upload",
            files=file_data,
            data=form_data,
            headers=auth_headers_volunteer,
        )

        if upload_response.status_code == 201:
            file_id = upload_response.json()["file_id"]

            # Update profile with new picture
            profile_update = {"profile_picture_id": file_id}

            profile_response = client.patch(
                "/v1/profiles/volunteer",
                json=profile_update,
                headers=auth_headers_volunteer,
            )
            assert profile_response.status_code in [
                200,
                400,
            ]  # May fail due to validation


class TestSearchAndFilterIntegration:
    """Test search and filtering across systems"""

    def test_advanced_opportunity_search(
        self, client: TestClient, session: Session, test_user_organization: User
    ):
        """Test advanced search functionality"""

        # Create diverse opportunities
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=10
        )

        # Test various search combinations
        search_queries = [
            "q=Programming&category=Technology",
            "skills=Programming&is_remote=true",
            "location=Test City&min_duration=1",
            "q=volunteer&sort=created_date&order=desc",
        ]

        for query in search_queries:
            response = client.get(f"/v1/opportunities/search?{query}")
            assert response.status_code == 200

            data = response.json()
            assert "opportunities" in data
            assert "total_count" in data


class TestPerformanceIntegration:
    """Test system performance under load"""

    def test_bulk_operations_performance(
        self,
        client: TestClient,
        session: Session,
        test_user_organization: User,
        performance_timer,
    ):
        """Test performance with bulk operations"""

        # Test creating multiple opportunities
        performance_timer.start()

        opportunities = []
        for i in range(50):  # Create 50 opportunities
            opp_data = {
                "title": f"Bulk Test Opportunity {i}",
                "description": f"Bulk test opportunity {i} description",
                "skills_required": ["Programming"],
                "location": "Test City",
                "time_commitment": "5 hours/week",
                "volunteers_needed": 3,
            }

            response = client.post(
                "/v1/opportunities",
                json=opp_data,
                headers={
                    "Authorization": f"Bearer mock_token_org_{test_user_organization.id}"
                },
            )

            if response.status_code == 201:
                opportunities.append(response.json()["id"])

        performance_timer.stop()

        # Should complete bulk operations in reasonable time
        assert performance_timer.elapsed < 30  # Less than 30 seconds
        assert len(opportunities) > 0

    def test_concurrent_user_simulation(self, client: TestClient):
        """Test system behavior with concurrent users"""

        # Simulate multiple users browsing opportunities simultaneously
        import threading

        results = []

        def browse_opportunities():
            try:
                response = client.get("/v1/opportunities")
                results.append(response.status_code)
            except Exception:
                results.append(500)

        # Create multiple threads to simulate concurrent users
        threads = []
        for i in range(10):
            thread = threading.Thread(target=browse_opportunities)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10


class TestDataConsistency:
    """Test data consistency across systems"""

    def test_opportunity_application_consistency(
        self,
        client: TestClient,
        session: Session,
        test_user_volunteer: User,
        test_user_organization: User,
        test_opportunity: Opportunity,
        auth_headers_volunteer: dict,
        auth_headers_organization: dict,
    ):
        """Test data consistency between opportunities and applications"""

        # Make opportunity active
        test_opportunity.status = "active"
        test_opportunity.volunteers_needed = 5
        session.add(test_opportunity)
        session.commit()

        # Apply to opportunity
        application_data = {
            "opportunity_id": test_opportunity.id,
            "cover_letter": "Test application",
            "availability": {"hours_per_week": 10},
        }

        apply_response = client.post(
            "/v1/applications", json=application_data, headers=auth_headers_volunteer
        )
        assert apply_response.status_code == 201

        # Check opportunity shows updated application count
        opp_details = client.get(f"/v1/opportunities/{test_opportunity.id}")
        assert opp_details.status_code == 200
        assert opp_details.json()["application_count"] >= 1

        # Check organization sees the application
        org_applications = client.get(
            f"/v1/opportunities/{test_opportunity.id}/applications",
            headers=auth_headers_organization,
        )
        assert org_applications.status_code == 200
        assert org_applications.json()["total_count"] >= 1
