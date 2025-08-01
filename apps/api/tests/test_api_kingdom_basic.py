"""
API Kingdom Basic Tests - Verifies Backend API & Routing Kingdom Works
Tests that all routers are properly activated and accessible.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestAPIKingdomBasic:
    """Basic tests to verify API Kingdom routers are functional"""

    def test_health_endpoint_works(self, client: TestClient):
        """Test basic health endpoint works"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_auth_router_active(self, client: TestClient):
        """Test auth router responds (indicates it's active)"""
        # Test registration endpoint - should return validation error or success
        registration_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "volunteer",
            "language_preference": "en",
        }
        response = client.post("/v1/auth/register", json=registration_data)
        # Any response indicates router is active
        assert response.status_code in [200, 201, 400, 422]

    def test_opportunities_router_active(self, client: TestClient):
        """Test opportunities router is active"""
        response = client.get("/v1/opportunities/")
        # Should return 200 with empty list or actual data
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_applications_router_active(self, client: TestClient):
        """Test applications router is active (requires auth)"""
        response = client.get("/v1/applications/my-applications")
        # Should return 401 unauthorized (proves router is active)
        assert response.status_code == 401

    def test_admin_router_active(self, client: TestClient):
        """Test admin router is active (requires auth)"""
        response = client.get("/v1/admin/users")
        # Should return 401 unauthorized (proves router is active)
        assert response.status_code == 401

    def test_files_router_active(self, client: TestClient):
        """Test files router is active"""
        response = client.get("/v1/files/test-file")
        # Should return 401 or 404 (proves router is active)
        assert response.status_code in [401, 404]

    def test_reviews_router_active(self, client: TestClient):
        """Test reviews router is active"""
        response = client.get("/v1/reviews/")
        # Should return some response (proves router is active)
        assert response.status_code in [200, 401, 422]


class TestLegacyDeprecationStubs:
    """Test legacy endpoint deprecation stubs work correctly"""

    def test_legacy_api_deprecation(self, client: TestClient):
        """Test /api/ prefixed endpoints return proper deprecation"""
        response = client.get("/api/users")
        assert response.status_code == 410  # Gone
        data = response.json()
        assert data["error_code"] == "ENDPOINT_DEPRECATED"
        assert "/v1/users" in data["new_endpoint"]
        assert response.headers.get("X-Deprecated") == "true"

    def test_legacy_auth_deprecation(self, client: TestClient):
        """Test /auth/ endpoints return proper deprecation"""
        response = client.post(
            "/auth/login", json={"email": "test@example.com", "password": "test"}
        )
        assert response.status_code == 410  # Gone
        data = response.json()
        assert data["error_code"] == "ENDPOINT_DEPRECATED"
        assert "/v1/auth/login" in data["new_endpoint"]
        assert response.headers.get("X-Deprecated") == "true"


class TestAPINamespaceConsistency:
    """Test API namespace consistency"""

    def test_v1_prefix_usage(self):
        """Verify most routes use /v1/ prefix"""
        from main import app

        v1_routes = []
        allowed_non_v1 = {
            "/",
            "/health",
            "/metrics",
            "/health/detailed",
            "/health/readiness",
            "/health/liveness",
            "/admin/database/health",
            "/admin/database/optimize",
            "/api/{path:path}",
            "/auth/{path:path}",
            "/docs",
            "/redoc",
            "/openapi.json",
        }

        for route in app.routes:
            if hasattr(route, "path"):
                path = route.path
                if path.startswith("/v1/"):
                    v1_routes.append(path)
                elif path not in allowed_non_v1:
                    # This would be a problem - an active route not using v1 prefix
                    pytest.fail(
                        f"Found non-v1 route that's not in allowed list: {path}"
                    )

        # Should have many v1 routes
        assert len(v1_routes) > 50, f"Expected many v1 routes, got {len(v1_routes)}"


class TestAPIKingdomIntegration:
    """Integration tests for API Kingdom"""

    def test_full_auth_flow_works(self, client: TestClient, session: Session):
        """Test complete auth flow to ensure routers work together"""
        # Register a user
        registration_data = {
            "email": "integration@test.com",
            "password": "testpassword123",
            "first_name": "Integration",
            "last_name": "Test",
            "role": "volunteer",
            "language_preference": "en",
        }

        register_response = client.post("/v1/auth/register", json=registration_data)
        # Should succeed or fail with validation - either indicates router works
        assert register_response.status_code in [200, 201, 400, 422]

        # If registration succeeded, try login
        if register_response.status_code in [200, 201]:
            login_data = {
                "email": "integration@test.com",
                "password": "testpassword123",
            }
            login_response = client.post("/v1/auth/login", json=login_data)
            assert login_response.status_code in [200, 201, 400, 401, 422]

    def test_router_count_reasonable(self):
        """Test that we have a reasonable number of routes (indicates all routers loaded)"""
        from main import app

        total_routes = len([r for r in app.routes if hasattr(r, "path")])
        # We should have many routes if all routers are loaded
        assert (
            total_routes > 100
        ), f"Expected >100 routes, got {total_routes}. Routers may not be loading."
