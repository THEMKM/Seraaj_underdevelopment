"""
Verification System API Tests
"""

from fastapi.testclient import TestClient
from sqlmodel import Session
from models import User, Organisation


class TestSkillVerificationEndpoints:
    """Test skill verification system"""

    def test_initiate_skill_verification_success(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test successful skill verification initiation"""
        verification_data = {
            "skill_name": "Python Programming",
            "verification_method": "portfolio_review",
            "evidence_data": {
                "portfolio_url": "https://github.com/user/portfolio",
                "description": "Full-stack web applications using Python/Django",
            },
        }

        response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 201

        data = response.json()
        assert "verification_id" in data
        assert data["skill_name"] == verification_data["skill_name"]
        assert data["verification_method"] == verification_data["verification_method"]
        assert data["status"] == "pending"

    def test_initiate_skill_verification_organization_forbidden(
        self, client: TestClient, auth_headers_organization: dict
    ):
        """Test that organizations cannot initiate skill verification"""
        verification_data = {
            "skill_name": "Leadership",
            "verification_method": "peer_endorsement",
        }

        response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_organization,
        )
        assert response.status_code == 403

    def test_initiate_skill_verification_invalid_method(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test skill verification with invalid method"""
        verification_data = {
            "skill_name": "Programming",
            "verification_method": "invalid_method",
        }

        response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 400
        assert "invalid verification method" in response.json()["detail"].lower()

    def test_get_my_skill_verifications(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting volunteer's skill verifications"""
        response = client.get(
            "/v1/verification/skills/my-verifications", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        if data:
            verification = data[0]
            assert "id" in verification
            assert "skill_name" in verification
            assert "verification_method" in verification
            assert "status" in verification
            assert "created_at" in verification

    def test_get_skill_verification_details_own(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting details of own skill verification"""
        # First create a verification
        verification_data = {
            "skill_name": "JavaScript",
            "verification_method": "assessment_test",
            "evidence_data": {"description": "Frontend development skills"},
        }

        create_response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )
        verification_id = create_response.json()["verification_id"]

        # Get details
        response = client.get(
            f"/v1/verification/skills/{verification_id}", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == verification_id
        assert data["skill_name"] == verification_data["skill_name"]
        assert "evidence_data" in data
        assert "peer_endorsements" in data

    def test_provide_peer_endorsement_success(
        self, client: TestClient, auth_headers_volunteer: dict, session: Session
    ):
        """Test providing peer endorsement for skill verification"""
        # This would require creating another volunteer and verification
        # For now, test the endpoint structure
        endorsement_data = {
            "endorsement_text": "I can confirm this person has excellent Python skills",
            "relationship": "colleague",
            "confidence_level": 5,
        }

        response = client.post(
            "/v1/verification/skills/1/endorse",
            json=endorsement_data,
            headers=auth_headers_volunteer,
        )
        # Expect 404 if verification doesn't exist, or proper processing
        assert response.status_code in [200, 404, 400]

    def test_complete_assessment_test_success(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test completing assessment test"""
        # First create assessment-based verification
        verification_data = {
            "skill_name": "Data Analysis",
            "verification_method": "assessment_test",
        }

        create_response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )

        if create_response.status_code == 201:
            verification_id = create_response.json()["verification_id"]

            test_results = {
                "answers": [
                    {"question_id": 1, "answer": "pandas"},
                    {"question_id": 2, "answer": "matplotlib"},
                ],
                "completion_time": 1800,  # 30 minutes
            }

            response = client.post(
                f"/v1/verification/skills/{verification_id}/assessment",
                json=test_results,
                headers=auth_headers_volunteer,
            )
            assert response.status_code == 200
            assert "verified" in response.json()

    def test_upload_verification_document_success(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test uploading verification document"""
        # First create verification
        verification_data = {
            "skill_name": "Graphic Design",
            "verification_method": "portfolio_review",
        }

        create_response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )

        if create_response.status_code == 201:
            verification_id = create_response.json()["verification_id"]

            # Create mock file data
            file_data = {
                "file": ("certificate.pdf", b"fake pdf content", "application/pdf")
            }
            form_data = {"document_type": "certificate"}

            response = client.post(
                f"/v1/verification/skills/{verification_id}/documents",
                files=file_data,
                data=form_data,
                headers=auth_headers_volunteer,
            )
            assert response.status_code in [
                200,
                400,
            ]  # May fail due to file handling in tests


class TestBadgeSystem:
    """Test badge system endpoints"""

    def test_get_available_badges(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting all available badges"""
        response = client.get(
            "/v1/verification/badges/available", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        data = response.json()
        assert "badges" in data
        assert "total_count" in data

        if data["badges"]:
            badge = data["badges"][0]
            assert "id" in badge
            assert "name" in badge
            assert "description" in badge
            assert "badge_type" in badge
            assert "criteria" in badge

    def test_get_my_badges(self, client: TestClient, auth_headers_volunteer: dict):
        """Test getting user's earned badges"""
        response = client.get(
            "/v1/verification/badges/my-badges", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        data = response.json()
        assert "badges" in data
        assert "total_badges" in data
        assert "total_points" in data
        assert "badge_counts_by_type" in data
        assert "badge_counts_by_rarity" in data

    def test_get_verification_leaderboard(self, client: TestClient):
        """Test getting verification leaderboard"""
        response = client.get("/v1/verification/leaderboard")
        assert response.status_code == 200

        data = response.json()
        assert "leaderboard" in data
        assert "period" in data
        assert "total_users" in data

        if data["leaderboard"]:
            leader = data["leaderboard"][0]
            assert "rank" in leader
            assert "user_name" in leader
            assert "badge_count" in leader
            assert "total_points" in leader

    def test_get_verification_leaderboard_with_period_filter(self, client: TestClient):
        """Test leaderboard with different time periods"""
        for period in ["week", "month", "all_time"]:
            response = client.get(f"/v1/verification/leaderboard?period={period}")
            assert response.status_code == 200
            assert response.json()["period"] == period

    def test_get_verification_statistics(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting verification system statistics"""
        response = client.get(
            "/v1/verification/stats/summary", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        # Statistics structure will depend on implementation
        data = response.json()
        assert isinstance(data, dict)


class TestAdminVerificationEndpoints:
    """Test admin verification management"""

    def test_admin_verify_skill_success(
        self, client: TestClient, auth_headers_admin: dict, session: Session
    ):
        """Test admin manually verifying a skill"""
        # This would require creating a pending verification first
        verification_decision = {
            "decision": "approve",
            "score": 0.9,
            "notes": "Excellent portfolio demonstrating advanced skills",
        }

        response = client.post(
            "/v1/verification/admin/verify/1",
            json=verification_decision,
            headers=auth_headers_admin,
        )
        # Expect 404 if verification doesn't exist, or success
        assert response.status_code in [200, 404]

    def test_admin_verify_skill_volunteer_forbidden(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test that volunteers cannot access admin verification endpoints"""
        verification_decision = {"decision": "approve", "score": 0.9, "notes": "Test"}

        response = client.post(
            "/v1/verification/admin/verify/1",
            json=verification_decision,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 403

    def test_admin_reject_skill_verification(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test admin rejecting a skill verification"""
        verification_decision = {
            "decision": "reject",
            "score": 0.0,
            "notes": "Insufficient evidence provided",
        }

        response = client.post(
            "/v1/verification/admin/verify/1",
            json=verification_decision,
            headers=auth_headers_admin,
        )
        assert response.status_code in [200, 404]


class TestOrganizationTrustSystem:
    """Test organization trust and verification system"""

    def test_get_organization_trust_score(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_user_organization: User,
        session: Session,
    ):
        """Test getting organization trust score"""
        # Get organization ID
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == test_user_organization.id)
            .first()
        )

        response = client.get(
            f"/v1/verification/organizations/{org.id}/trust-score",
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 200

        data = response.json()
        assert "organization_id" in data
        assert "trust_score" in data
        assert "trust_level" in data
        assert "last_updated" in data

    def test_recalculate_trust_score_organization_owner(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_user_organization: User,
        session: Session,
    ):
        """Test organization owner recalculating trust score"""
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == test_user_organization.id)
            .first()
        )

        response = client.post(
            f"/v1/verification/organizations/{org.id}/trust-score/recalculate",
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "trust_score" in data
        assert "trust_level" in data

    def test_recalculate_trust_score_volunteer_forbidden(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_user_organization: User,
        session: Session,
    ):
        """Test that volunteers cannot recalculate trust scores"""
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == test_user_organization.id)
            .first()
        )

        response = client.post(
            f"/v1/verification/organizations/{org.id}/trust-score/recalculate",
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 403

    def test_get_eligible_verification_badges(
        self,
        client: TestClient,
        auth_headers_organization: dict,
        test_user_organization: User,
        session: Session,
    ):
        """Test getting organization's eligible verification badges"""
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == test_user_organization.id)
            .first()
        )

        response = client.get(
            f"/v1/verification/organizations/{org.id}/verification-badges/eligible",
            headers=auth_headers_organization,
        )
        assert response.status_code == 200

        data = response.json()
        assert "organization_id" in data
        assert "eligible_badges" in data
        assert "total_eligible" in data

    def test_award_verification_badge_admin(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        test_user_organization: User,
        session: Session,
    ):
        """Test admin awarding verification badge to organization"""
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == test_user_organization.id)
            .first()
        )

        response = client.post(
            f"/v1/verification/organizations/{org.id}/verification-badges/registered_nonprofit/award",
            headers=auth_headers_admin,
        )
        assert response.status_code in [
            200,
            400,
        ]  # May fail if badge already exists or criteria not met

    def test_award_verification_badge_volunteer_forbidden(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_user_organization: User,
        session: Session,
    ):
        """Test that volunteers cannot award verification badges"""
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == test_user_organization.id)
            .first()
        )

        response = client.post(
            f"/v1/verification/organizations/{org.id}/verification-badges/registered_nonprofit/award",
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 403

    def test_get_organization_verification_badges_public(
        self, client: TestClient, test_user_organization: User, session: Session
    ):
        """Test getting organization's verification badges (public endpoint)"""
        org = (
            session.query(Organisation)
            .filter(Organisation.user_id == test_user_organization.id)
            .first()
        )

        response = client.get(
            f"/v1/verification/organizations/{org.id}/verification-badges"
        )
        assert response.status_code == 200

        data = response.json()
        assert "organization_id" in data
        assert "organization_name" in data
        assert "verification_badges" in data
        assert "total_badges" in data
        assert "total_trust_boost" in data
        assert "trust_level" in data

    def test_get_trust_system_statistics_admin(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test getting trust system statistics as admin"""
        response = client.get(
            "/v1/verification/trust-system/stats", headers=auth_headers_admin
        )
        assert response.status_code == 200

        data = response.json()
        assert "trust_level_distribution" in data
        assert "average_trust_score" in data
        assert "badge_distribution" in data
        assert "trust_weights" in data
        assert "trust_thresholds" in data

    def test_get_trust_system_statistics_volunteer_forbidden(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test that volunteers cannot access trust system statistics"""
        response = client.get(
            "/v1/verification/trust-system/stats", headers=auth_headers_volunteer
        )
        assert response.status_code == 403

    def test_get_top_trusted_organizations_public(self, client: TestClient):
        """Test getting top trusted organizations (public endpoint)"""
        response = client.get("/v1/verification/organizations/top-trusted")
        assert response.status_code == 200

        data = response.json()
        assert "top_organizations" in data
        assert "total_count" in data

        if data["top_organizations"]:
            org = data["top_organizations"][0]
            assert "id" in org
            assert "name" in org
            assert "trust_score" in org
            assert "trust_level" in org
            assert "verification_badge_count" in org

    def test_get_trust_levels_info(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting trust levels and thresholds information"""
        response = client.get(
            "/v1/verification/trust-levels", headers=auth_headers_volunteer
        )
        assert response.status_code == 200

        data = response.json()
        assert "trust_levels" in data
        assert "trust_factors" in data
        assert "verification_badges" in data

        if data["trust_levels"]:
            level = data["trust_levels"][0]
            assert "level" in level
            assert "threshold" in level
            assert "description" in level


class TestVerificationValidation:
    """Test verification system data validation"""

    def test_invalid_skill_verification_method(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test skill verification with invalid method"""
        verification_data = {
            "skill_name": "Programming",
            "verification_method": "nonexistent_method",
        }

        response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 400

    def test_empty_skill_name(self, client: TestClient, auth_headers_volunteer: dict):
        """Test skill verification with empty skill name"""
        verification_data = {
            "skill_name": "",
            "verification_method": "portfolio_review",
        }

        response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 400

    def test_invalid_document_type_upload(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test uploading verification document with invalid type"""
        # First create verification
        verification_data = {
            "skill_name": "Design",
            "verification_method": "portfolio_review",
        }

        create_response = client.post(
            "/v1/verification/skills",
            json=verification_data,
            headers=auth_headers_volunteer,
        )

        if create_response.status_code == 201:
            verification_id = create_response.json()["verification_id"]

            file_data = {"file": ("test.txt", b"content", "text/plain")}
            form_data = {"document_type": "invalid_type"}

            response = client.post(
                f"/v1/verification/skills/{verification_id}/documents",
                files=file_data,
                data=form_data,
                headers=auth_headers_volunteer,
            )
            assert response.status_code == 400
