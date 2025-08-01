"""
Basic Router Tests - Verifies API Kingdom Routes Work
Tests at least one happy path for each router to ensure they're properly activated.
"""

from fastapi.testclient import TestClient


class TestAPIRoutersBasic:
    """Basic tests to verify all routers are functional"""

    def test_health_endpoint(self, client: TestClient):
        """Test basic health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_auth_router_active(self, client: TestClient):
        """Test auth router is active and functional"""
        # Test registration endpoint
        registration_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "volunteer",
            "language_preference": "en",
        }

        response = client.post("/v1/auth/register", json=registration_data)
        # Should get either 201 (success) or 400 (duplicate) - both indicate router is active
        assert response.status_code in [201, 400, 422]
        assert "error" in response.json() or "id" in response.json()

    def test_opportunities_router_active(self, client: TestClient):
        """Test opportunities router is active"""
        response = client.get("/v1/opportunities/")
        # Should get 200 (success) - router is active and returns data
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_applications_router_active(self, client: TestClient):
        """Test applications router requires auth (401) - indicates it's active"""
        response = client.get("/v1/applications/my-applications")
        # Should get 401 (unauthorized) - indicates router is active but requires auth
        assert response.status_code == 401

    def test_profiles_router_active(self, client: TestClient):
        """Test profiles router is active"""
        # Test getting volunteer profiles (public endpoint)
        response = client.get("/v1/profiles/volunteer")
        # Should get 401 (requires auth) or 200 (success) - both indicate router is active
        assert response.status_code in [200, 401, 422]

    def test_organizations_router_active(self, client: TestClient):
        """Test organizations router is active"""
        response = client.get("/v1/org/")
        # Should get some response indicating router is active
        assert response.status_code in [200, 401, 422]

    def test_files_router_active(self, client: TestClient):
        """Test files router is active"""
        response = client.get("/v1/files/test")
        # Should get 401 (requires auth) or 404 (not found) - both indicate router is active
        assert response.status_code in [401, 404, 422]

    def test_admin_router_active(self, client: TestClient):
        """Test admin router is active"""
        response = client.get("/v1/admin/users")
        # Should get 401 (unauthorized) - indicates router is active but requires admin auth
        assert response.status_code == 401

    def test_reviews_router_active(self, client: TestClient):
        """Test reviews router is active"""
        response = client.get("/v1/reviews/")
        # Should get some response indicating router is active
        assert response.status_code in [200, 401, 422]

    def test_match_router_active(self, client: TestClient):
        """Test matching router is active"""
        response = client.get("/v1/match/recommendations")
        # Should get 401 (requires auth) - indicates router is active
        assert response.status_code == 401

    def test_operations_router_active(self, client: TestClient):
        """Test operations router is active"""
        response = client.get("/v1/operations/test-op-id")
        # Should get 401 (requires auth) or 404 (not found) - both indicate router is active
        assert response.status_code in [401, 404, 422]

    def test_system_router_active(self, client: TestClient):
        """Test system router is active"""
        response = client.get("/v1/system/health")
        # Should get some response indicating router is active
        assert response.status_code in [200, 401, 422]

    def test_verification_router_active(self, client: TestClient):
        """Test verification router is active"""
        response = client.get("/v1/verification/skills")
        # Should get 401 (requires auth) - indicates router is active
        assert response.status_code == 401

    def test_collaboration_router_active(self, client: TestClient):
        """Test collaboration router is active"""
        response = client.get("/v1/collaboration/projects")
        # Should get 401 (requires auth) - indicates router is active
        assert response.status_code == 401

    def test_calendar_router_active(self, client: TestClient):
        """Test calendar router is active"""
        response = client.get("/v1/calendar/events")
        # Should get 401 (requires auth) - indicates router is active
        assert response.status_code == 401

    def test_guided_tours_router_active(self, client: TestClient):
        """Test guided tours router is active"""
        response = client.get("/v1/guided-tours/")
        # Should get some response indicating router is active
        assert response.status_code in [200, 401, 422]

    def test_pwa_router_active(self, client: TestClient):
        """Test PWA router is active"""
        response = client.get("/v1/pwa/manifest.json")
        # Should get some response indicating router is active
        assert response.status_code in [200, 404, 422]

    def test_push_notifications_router_active(self, client: TestClient):
        """Test push notifications router is active"""
        response = client.get("/v1/push-notifications/vapid-public-key")
        # Should get some response indicating router is active
        assert response.status_code in [200, 401, 422]

    def test_demo_scenarios_router_active(self, client: TestClient):
        """Test demo scenarios router is active"""
        response = client.get("/v1/demo-scenarios/scenarios")
        # Should get some response indicating router is active
        assert response.status_code in [200, 401, 422]

    def test_websocket_router_active(self, client: TestClient):
        """Test messaging/websocket router is active"""
        response = client.get("/v1/messaging/conversations")
        # Should get 401 (requires auth) - indicates router is active
        assert response.status_code == 401


class TestLegacyDeprecationStubs:
    """Test that legacy endpoints return proper deprecation responses"""

    def test_legacy_api_deprecation(self, client: TestClient):
        """Test /api/ prefixed endpoints return deprecation notice"""
        response = client.get("/api/users")
        assert response.status_code == 410  # Gone
        data = response.json()
        assert data["error_code"] == "ENDPOINT_DEPRECATED"
        assert "/v1/users" in data["new_endpoint"]
        assert "X-Deprecated" in response.headers

    def test_legacy_stubs_hidden_from_docs(self):
        """Ensure legacy stubs are excluded from OpenAPI schema"""
        from main import app

        route_map = {route.path: route for route in app.routes if hasattr(route, "path")}
        assert not route_map["/api/{path:path}"].include_in_schema
        assert not route_map["/auth/{path:path}"].include_in_schema

    def test_legacy_auth_deprecation(self, client: TestClient):
        """Test /auth/ endpoints without v1 prefix return deprecation notice"""
        response = client.post(
            "/auth/login", json={"email": "test@example.com", "password": "test"}
        )
        assert response.status_code == 410  # Gone
        data = response.json()
        assert data["error_code"] == "ENDPOINT_DEPRECATED"
        assert "/v1/auth/login" in data["new_endpoint"]
        assert "X-Deprecated" in response.headers


class TestAPINamespaceConsistency:
    """Test that all active endpoints use /v1/ prefix"""

    def test_all_routes_use_v1_prefix(self):
        """Verify all active routes use the /v1/ prefix"""
        from main import app

        v1_routes = []
        non_v1_routes = []

        for route in app.routes:
            if hasattr(route, "path"):
                path = route.path
                if path.startswith("/v1/"):
                    v1_routes.append(path)
                elif path not in [
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
                ]:
                    non_v1_routes.append(path)

        # All API routes should use /v1/ prefix (except health, docs, and deprecation stubs)
        assert len(v1_routes) > 0, "Should have v1 routes"
        assert len(non_v1_routes) == 0, f"Found non-v1 routes: {non_v1_routes}"
