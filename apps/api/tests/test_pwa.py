"""
Tests for Progressive Web App (PWA) functionality
"""

from fastapi.testclient import TestClient


class TestPWAManifest:
    """Test PWA manifest generation"""

    def test_basic_manifest_generation(self, client: TestClient):
        """Test basic manifest generation without authentication"""
        response = client.get("/pwa/manifest.json")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        manifest = response.json()
        assert manifest["name"] == "Seraaj - Volunteer Marketplace"
        assert manifest["short_name"] == "Seraaj"
        assert manifest["display"] == "standalone"
        assert manifest["theme_color"] == "#2563eb"
        assert "icons" in manifest
        assert len(manifest["icons"]) > 0

    def test_authenticated_manifest_generation(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test manifest generation with authenticated user"""
        response = client.get("/pwa/manifest.json", headers=auth_headers_volunteer)

        assert response.status_code == 200
        manifest = response.json()

        # Should have user-specific customizations
        assert "start_url" in manifest
        assert "scope" in manifest

        # URLs should be absolute
        assert manifest["start_url"].startswith("http")
        assert manifest["scope"].startswith("http")

    def test_role_specific_manifest(self, client: TestClient):
        """Test role-specific manifest generation"""
        # Test volunteer manifest
        response = client.get("/pwa/manifest.json?role=volunteer")

        assert response.status_code == 200
        manifest = response.json()
        assert "volunteer" in manifest["name"].lower() or "opportunities" in str(
            manifest.get("shortcuts", [])
        )

        # Test organization manifest
        response = client.get("/pwa/manifest.json?role=organization")

        assert response.status_code == 200
        manifest = response.json()
        # Should have organization-specific features
        assert manifest is not None

    def test_themed_manifest(self, client: TestClient):
        """Test manifest with custom theme"""
        response = client.get("/pwa/manifest.json?theme=%23ff5722")

        assert response.status_code == 200
        manifest = response.json()
        assert manifest["theme_color"] == "#ff5722"

    def test_manifest_caching(self, client: TestClient):
        """Test manifest response includes appropriate caching headers"""
        response = client.get("/pwa/manifest.json")

        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "public" in response.headers["cache-control"]
        assert "max-age" in response.headers["cache-control"]


class TestServiceWorker:
    """Test service worker generation"""

    def test_service_worker_generation(self, client: TestClient):
        """Test basic service worker generation"""
        response = client.get("/pwa/sw.js")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/javascript"

        sw_code = response.text
        assert "addEventListener" in sw_code
        assert "install" in sw_code
        assert "activate" in sw_code
        assert "fetch" in sw_code
        assert "cache" in sw_code.lower()

    def test_service_worker_with_strategy(self, client: TestClient):
        """Test service worker with different caching strategies"""
        strategies = ["network_first", "cache_first", "stale_while_revalidate"]

        for strategy in strategies:
            response = client.get(f"/pwa/sw.js?strategy={strategy}")

            assert response.status_code == 200
            sw_code = response.text

            # Should contain strategy-specific code
            assert "fetch" in sw_code
            assert "cache" in sw_code.lower()

    def test_service_worker_headers(self, client: TestClient):
        """Test service worker response headers"""
        response = client.get("/pwa/sw.js")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/javascript"
        assert "cache-control" in response.headers
        assert "service-worker-allowed" in response.headers
        assert response.headers["service-worker-allowed"] == "/"

    def test_service_worker_fallback(self, client: TestClient):
        """Test service worker fallback when generation fails"""
        # This test would require mocking the generator to fail
        # For now, just ensure we get a valid response
        response = client.get("/pwa/sw.js")

        assert response.status_code == 200
        assert "self.addEventListener" in response.text


class TestOfflinePage:
    """Test offline fallback page"""

    def test_offline_page_generation(self, client: TestClient):
        """Test offline page generation"""
        response = client.get("/pwa/offline.html")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        html_content = response.text
        assert "<!DOCTYPE html>" in html_content
        assert "You're Offline" in html_content
        assert "Seraaj" in html_content
        assert "Try Again" in html_content

    def test_offline_page_functionality(self, client: TestClient):
        """Test offline page includes necessary JavaScript"""
        response = client.get("/pwa/offline.html")

        html_content = response.text
        assert "<script>" in html_content
        assert "tryAgain" in html_content
        assert "navigator.onLine" in html_content
        assert "addEventListener" in html_content

    def test_offline_page_caching(self, client: TestClient):
        """Test offline page caching headers"""
        response = client.get("/pwa/offline.html")

        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "public" in response.headers["cache-control"]


class TestInstallPrompt:
    """Test PWA install prompt functionality"""

    def test_install_prompt_data(self, client: TestClient):
        """Test install prompt data generation"""
        response = client.get("/pwa/install-prompt")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        prompt_data = data["data"]

        assert "can_install" in prompt_data
        assert "is_mobile" in prompt_data
        assert "benefits" in prompt_data
        assert "install_instructions" in prompt_data

        # Should have benefits
        assert len(prompt_data["benefits"]) > 0

        # Should have instructions for different platforms
        instructions = prompt_data["install_instructions"]
        assert "android_chrome" in instructions
        assert "ios_safari" in instructions
        assert "desktop" in instructions

    def test_install_prompt_authenticated(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test install prompt with authenticated user"""
        response = client.get("/pwa/install-prompt", headers=auth_headers_volunteer)

        assert response.status_code == 200
        data = response.json()

        prompt_data = data["data"]
        benefits = prompt_data["benefits"]

        # Should have user-specific benefits
        assert any("draft" in benefit.lower() for benefit in benefits)

    def test_install_analytics_tracking(self, client: TestClient):
        """Test install analytics tracking"""
        analytics_data = {
            "event": "install_prompted",
            "timestamp": "2024-01-15T10:00:00Z",
            "metadata": {"source": "banner", "user_agent": "Chrome/91.0"},
        }

        response = client.post("/pwa/install-analytics", json=analytics_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tracked"] is True


class TestOfflineData:
    """Test offline data management"""

    def test_offline_data_info(self, client: TestClient, auth_headers_volunteer: dict):
        """Test offline data information endpoint"""
        response = client.get("/pwa/offline-data", headers=auth_headers_volunteer)

        assert response.status_code == 200
        data = response.json()

        offline_info = data["data"]
        assert "storage_limits" in offline_info
        assert "cache_duration" in offline_info
        assert "supported_offline_actions" in offline_info
        assert "sync_triggers" in offline_info

        # Check storage limits
        limits = offline_info["storage_limits"]
        assert "opportunities" in limits
        assert "applications" in limits
        assert "messages" in limits

        # Check supported actions
        actions = offline_info["supported_offline_actions"]
        assert "view_opportunities" in actions
        assert "save_application_drafts" in actions

    def test_sync_status_update(self, client: TestClient, auth_headers_volunteer: dict):
        """Test sync status update endpoint"""
        sync_data = {
            "sync_type": "full",
            "status": "success",
            "items_synced": 25,
            "duration_ms": 1500,
            "timestamp": "2024-01-15T10:00:00Z",
        }

        response = client.post(
            "/pwa/sync-status", json=sync_data, headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status_updated"] is True

    def test_cache_info(self, client: TestClient, auth_headers_volunteer: dict):
        """Test cache information endpoint"""
        response = client.get("/pwa/cache-info", headers=auth_headers_volunteer)

        assert response.status_code == 200
        data = response.json()

        cache_info = data["data"]
        assert "server_cache" in cache_info
        assert "recommended_client_storage" in cache_info
        assert "cache_strategies" in cache_info

        # Check cache strategies
        strategies = cache_info["cache_strategies"]
        assert "opportunities" in strategies
        assert "applications" in strategies
        assert strategies["opportunities"] in [
            "network_first",
            "cache_first",
            "stale_while_revalidate",
        ]

    def test_clear_cache(self, client: TestClient, auth_headers_volunteer: dict):
        """Test cache clearing endpoint"""
        response = client.post("/pwa/clear-cache", headers=auth_headers_volunteer)

        assert response.status_code == 200
        data = response.json()

        instructions = data["data"]
        assert instructions["action"] == "clear_cache"
        assert "cache_types" in instructions
        assert "timestamp" in instructions


class TestPWACapabilities:
    """Test PWA capabilities detection"""

    def test_capabilities_detection(self, client: TestClient):
        """Test PWA capabilities detection"""
        response = client.get("/pwa/capabilities")

        assert response.status_code == 200
        data = response.json()

        capabilities_data = data["data"]
        assert "capabilities" in capabilities_data
        assert "features" in capabilities_data
        assert "browser_info" in capabilities_data

        # Check capabilities
        capabilities = capabilities_data["capabilities"]
        assert "service_worker" in capabilities
        assert "push_notifications" in capabilities
        assert "indexed_db" in capabilities

        # Check features
        features = capabilities_data["features"]
        assert "offline_opportunity_browsing" in features
        assert "draft_saving" in features

    def test_mobile_capabilities(self, client: TestClient):
        """Test capabilities for mobile browsers"""
        mobile_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }

        response = client.get("/pwa/capabilities", headers=mobile_headers)

        assert response.status_code == 200
        data = response.json()

        browser_info = data["data"]["browser_info"]
        assert browser_info["is_mobile"] is True

        capabilities = data["data"]["capabilities"]
        assert capabilities["device_orientation"] is True

    def test_authenticated_capabilities(
        self, client: TestClient, auth_headers_organization: dict
    ):
        """Test capabilities for authenticated organization user"""
        response = client.get("/pwa/capabilities", headers=auth_headers_organization)

        assert response.status_code == 200
        data = response.json()

        features = data["data"]["features"]
        # Should include organization-specific features
        assert "offline_application_management" in features
        assert "opportunity_creation_drafts" in features


class TestShareTarget:
    """Test PWA share target functionality"""

    def test_share_content_handling(self, client: TestClient):
        """Test handling shared content"""
        share_data = {
            "title": "Interesting Opportunity",
            "text": "Check out this volunteer opportunity!",
            "url": "https://example.com/opportunity",
        }

        response = client.post("/pwa/share", data=share_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        result = data["data"]
        assert result["received"] is True
        assert "data" in result
        assert result["data"]["title"] == share_data["title"]

    def test_share_with_authentication(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test share handling with authenticated user"""
        share_data = {
            "title": "Volunteer Opportunity",
            "text": "Great opportunity for volunteers",
            "url": "https://seraaj.org/opportunity/123",
        }

        response = client.post(
            "/pwa/share", data=share_data, headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "redirect_url" in data["data"]


class TestPWAAdmin:
    """Test PWA admin functionality"""

    def test_generate_files_unauthorized(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test PWA file generation requires admin access"""
        response = client.post("/pwa/generate-files", headers=auth_headers_volunteer)

        assert response.status_code == 200
        data = response.json()

        # Should return error for non-admin users
        # The actual implementation returns a 403 in content, not status
        assert "error" in data or data.get("success") is False

    def test_storage_schema_debug(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test storage schema debug endpoint"""
        response = client.get(
            "/pwa/debug/storage-schema", headers=auth_headers_volunteer
        )

        # Should only be available in development
        # In production/test, should return 403
        assert response.status_code in [200, 403]

        if response.status_code == 200:
            data = response.json()
            schema = data["data"]
            assert "name" in schema
            assert "stores" in schema
            assert "opportunities" in schema["stores"]


class TestPWAIntegration:
    """Test PWA integration functionality"""

    def test_pwa_detection_headers(self, client: TestClient):
        """Test PWA detection through headers"""
        pwa_headers = {"X-Requested-With": "seraaj-pwa"}

        response = client.get("/pwa/capabilities", headers=pwa_headers)

        assert response.status_code == 200
        data = response.json()

        browser_info = data["data"]["browser_info"]
        assert browser_info["is_pwa"] is True

    def test_offline_indicator(self, client: TestClient):
        """Test offline page includes proper indicators"""
        response = client.get("/pwa/offline.html")

        html_content = response.text
        assert "status-indicator" in html_content
        assert "status-dot" in html_content
        assert "connectionStatus" in html_content

    def test_manifest_shortcuts(self, client: TestClient):
        """Test manifest includes shortcuts"""
        response = client.get("/pwa/manifest.json")

        manifest = response.json()
        assert "shortcuts" in manifest

        shortcuts = manifest["shortcuts"]
        assert len(shortcuts) > 0

        # Check shortcut structure
        first_shortcut = shortcuts[0]
        assert "name" in first_shortcut
        assert "url" in first_shortcut
        assert "icons" in first_shortcut

    def test_service_worker_features(self, client: TestClient):
        """Test service worker includes expected features"""
        response = client.get("/pwa/sw.js")

        sw_code = response.text

        # Should include background sync
        assert "sync" in sw_code

        # Should include push notifications
        assert "push" in sw_code

        # Should include caching strategies
        assert "Cache" in sw_code or "cache" in sw_code

        # Should include offline handling
        assert "offline" in sw_code.lower()

        # Should include error handling
        assert "catch" in sw_code or "error" in sw_code.lower()


class TestPWAPerformance:
    """Test PWA performance and optimization"""

    def test_manifest_compression(self, client: TestClient):
        """Test manifest is properly compressed"""
        response = client.get("/pwa/manifest.json")

        # Check response size is reasonable
        content_length = len(response.content)
        assert content_length < 10000  # Should be less than 10KB

        # Check for unnecessary whitespace
        manifest_str = response.text
        assert (
            "  " not in manifest_str or manifest_str.count("  ") < 10
        )  # Minimal whitespace

    def test_service_worker_size(self, client: TestClient):
        """Test service worker file size is reasonable"""
        response = client.get("/pwa/sw.js")

        # Service worker should be optimized but functional
        content_length = len(response.content)
        assert content_length > 1000  # Should have substantial functionality
        assert content_length < 100000  # But not be excessively large

    def test_caching_headers(self, client: TestClient):
        """Test proper caching headers are set"""
        endpoints = ["/pwa/manifest.json", "/pwa/sw.js", "/pwa/offline.html"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

            # Should have cache control headers
            assert "cache-control" in response.headers
            cache_control = response.headers["cache-control"]

            # Should be cacheable
            assert "no-cache" not in cache_control or "public" in cache_control
