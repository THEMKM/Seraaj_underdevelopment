"""
Authentication API Tests
"""

from fastapi.testclient import TestClient
from sqlmodel import Session
from models import User


class TestAuthenticationEndpoints:
    """Test authentication and authorization endpoints"""

    def test_user_registration_volunteer_success(
        self, client: TestClient, session: Session
    ):
        """Test successful volunteer registration"""
        registration_data = {
            "email": "newvolunteer@test.com",
            "password": "strongpassword123",
            "first_name": "New",
            "last_name": "Volunteer",
            "role": "volunteer",
        }

        response = client.post("/v1/auth/register", json=registration_data)
        assert response.status_code == 201

        data = response.json()
        assert data["email"] == registration_data["email"]
        assert data["role"] == "volunteer"
        assert "access_token" in data
        assert "user_id" in data

        # Verify user was created in database
        user = (
            session.query(User).filter(User.email == registration_data["email"]).first()
        )
        assert user is not None
        assert user.role == "volunteer"
        assert not user.verified  # Should require email verification

    def test_user_registration_organization_success(
        self, client: TestClient, session: Session
    ):
        """Test successful organization registration"""
        registration_data = {
            "email": "neworg@test.com",
            "password": "strongpassword123",
            "first_name": "New",
            "last_name": "Organization",
            "role": "organization",
        }

        response = client.post("/v1/auth/register", json=registration_data)
        assert response.status_code == 201

        data = response.json()
        assert data["role"] == "organization"

    def test_user_registration_duplicate_email(
        self, client: TestClient, test_user_volunteer: User
    ):
        """Test registration with duplicate email fails"""
        registration_data = {
            "email": test_user_volunteer.email,
            "password": "password123",
            "first_name": "Duplicate",
            "last_name": "User",
            "role": "volunteer",
        }

        response = client.post("/v1/auth/register", json=registration_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_user_registration_invalid_email(self, client: TestClient):
        """Test registration with invalid email format"""
        registration_data = {
            "email": "invalid-email",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "role": "volunteer",
        }

        response = client.post("/v1/auth/register", json=registration_data)
        assert response.status_code == 422  # Validation error

    def test_user_registration_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        registration_data = {
            "email": "test@example.com",
            "password": "123",  # Too weak
            "first_name": "Test",
            "last_name": "User",
            "role": "volunteer",
        }

        response = client.post("/v1/auth/register", json=registration_data)
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_user_login_success(self, client: TestClient, test_user_volunteer: User):
        """Test successful user login"""
        login_data = {"username": test_user_volunteer.email, "password": "testpassword"}

        response = client.post("/v1/auth/login", data=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == test_user_volunteer.id
        assert data["role"] == test_user_volunteer.role

    def test_user_login_invalid_credentials(
        self, client: TestClient, test_user_volunteer: User
    ):
        """Test login with invalid credentials"""
        login_data = {
            "username": test_user_volunteer.email,
            "password": "wrongpassword",
        }

        response = client.post("/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert "credentials" in response.json()["detail"].lower()

    def test_user_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        login_data = {"username": "nonexistent@test.com", "password": "password123"}

        response = client.post("/v1/auth/login", data=login_data)
        assert response.status_code == 401

    def test_get_current_user_authenticated(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting current user when authenticated"""
        response = client.get("/v1/auth/me", headers=auth_headers_volunteer)
        assert response.status_code == 200

        data = response.json()
        assert "email" in data
        assert "role" in data
        assert "first_name" in data
        assert "last_name" in data

    def test_get_current_user_unauthenticated(self, client: TestClient):
        """Test getting current user when unauthenticated"""
        response = client.get("/v1/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_refresh_token_success(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test successful token refresh"""
        response = client.post("/v1/auth/refresh", headers=auth_headers_volunteer)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_logout_success(self, client: TestClient, auth_headers_volunteer: dict):
        """Test successful user logout"""
        response = client.post("/v1/auth/logout", headers=auth_headers_volunteer)
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    def test_change_password_success(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test successful password change"""
        password_change_data = {
            "current_password": "testpassword",
            "new_password": "newstrongpassword123",
        }

        response = client.post(
            "/v1/auth/change-password",
            json=password_change_data,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 200
        assert "password updated" in response.json()["message"].lower()

    def test_change_password_wrong_current(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test password change with wrong current password"""
        password_change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        }

        response = client.post(
            "/v1/auth/change-password",
            json=password_change_data,
            headers=auth_headers_volunteer,
        )
        assert response.status_code == 400
        assert "current password" in response.json()["detail"].lower()

    def test_password_reset_request(
        self, client: TestClient, test_user_volunteer: User
    ):
        """Test password reset request"""
        reset_data = {"email": test_user_volunteer.email}

        response = client.post("/v1/auth/forgot-password", json=reset_data)
        assert response.status_code == 200
        assert "reset instructions" in response.json()["message"].lower()

    def test_password_reset_request_nonexistent_email(self, client: TestClient):
        """Test password reset request for non-existent email"""
        reset_data = {"email": "nonexistent@test.com"}

        response = client.post("/v1/auth/forgot-password", json=reset_data)
        # Should return 200 to prevent email enumeration
        assert response.status_code == 200

    def test_verify_email_success(self, client: TestClient, session: Session):
        """Test successful email verification"""
        # Create unverified user
        user = User(
            email="unverified@test.com",
            first_name="Unverified",
            last_name="User",
            password_hash="$2b$12$test_hash",
            role="volunteer",
            verified=False,
            is_active=True,
        )
        session.add(user)
        session.commit()

        # Mock verification token
        verification_data = {"token": f"mock_verification_token_{user.id}"}

        response = client.post("/v1/auth/verify-email", json=verification_data)
        assert response.status_code == 200
        assert "verified" in response.json()["message"].lower()

        # Check user is now verified
        session.refresh(user)
        assert user.verified

    def test_verify_email_invalid_token(self, client: TestClient):
        """Test email verification with invalid token"""
        verification_data = {"token": "invalid_token"}

        response = client.post("/v1/auth/verify-email", json=verification_data)
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()


class TestAuthorizationMiddleware:
    """Test role-based authorization"""

    def test_admin_only_endpoint_as_admin(
        self, client: TestClient, auth_headers_admin: dict
    ):
        """Test admin-only endpoint access as admin"""
        response = client.get("/v1/admin/users", headers=auth_headers_admin)
        # Should be successful (or return appropriate admin response)
        assert response.status_code in [200, 404]  # 404 if no users yet

    def test_admin_only_endpoint_as_volunteer(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test admin-only endpoint access as volunteer"""
        response = client.get("/v1/admin/users", headers=auth_headers_volunteer)
        assert response.status_code == 403

    def test_organization_only_endpoint_as_organization(
        self, client: TestClient, auth_headers_organization: dict
    ):
        """Test organization-only endpoint access as organization"""
        opportunity_data = {
            "title": "Test Opportunity",
            "description": "Test description",
            "skills_required": ["Programming"],
            "location": "Test City",
            "time_commitment": "5 hours/week",
            "volunteers_needed": 3,
        }

        response = client.post(
            "/v1/opportunities",
            json=opportunity_data,
            headers=auth_headers_organization,
        )
        assert response.status_code in [201, 400]  # 400 if validation fails

    def test_organization_only_endpoint_as_volunteer(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test organization-only endpoint access as volunteer"""
        opportunity_data = {
            "title": "Test Opportunity",
            "description": "Test description",
            "skills_required": ["Programming"],
            "location": "Test City",
            "time_commitment": "5 hours/week",
            "volunteers_needed": 3,
        }

        response = client.post(
            "/v1/opportunities", json=opportunity_data, headers=auth_headers_volunteer
        )
        assert response.status_code == 403


class TestSecurityFeatures:
    """Test security-related features"""

    def test_rate_limiting_login_attempts(
        self, client: TestClient, test_user_volunteer: User
    ):
        """Test rate limiting on login attempts"""
        login_data = {
            "username": test_user_volunteer.email,
            "password": "wrongpassword",
        }

        # Make multiple failed login attempts
        responses = []
        for _ in range(6):  # Assuming 5 attempts limit
            response = client.post("/v1/auth/login", data=login_data)
            responses.append(response.status_code)

        # Last attempts should be rate limited
        assert 429 in responses  # Too Many Requests

    def test_jwt_expiration(self, client: TestClient):
        """Test JWT token expiration handling"""
        # This would require mocking time or creating expired tokens
        # For now, test with obviously invalid token format
        headers = {"Authorization": "Bearer expired.token.here"}
        response = client.get("/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_password_hashing(self, session: Session):
        """Test that passwords are properly hashed"""
        user = session.query(User).first()
        if user:
            # Password should be hashed, not stored in plain text
            assert user.password_hash != "testpassword"
            assert user.password_hash.startswith("$2b$")  # bcrypt format
