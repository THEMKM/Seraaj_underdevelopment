"""
Tests for Push Notification functionality
"""

from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session

from models import User
from models.push_notification import (
    PushSubscription,
    PushNotification,
    NotificationSettings,
    NotificationTemplate,
    NotificationType,
    NotificationPriority,
    NotificationStatus,
    PlatformType,
)
from services.push_notification_service import get_push_notification_service


class TestPushNotificationSubscription:
    """Test push notification subscription management"""

    def test_subscribe_to_notifications(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test subscribing to push notifications"""
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint",
            "keys": {"p256dh": "test-p256dh-key", "auth": "test-auth-key"},
            "device_type": "mobile",
            "device_name": "Test Device",
            "user_agent": "Test User Agent",
        }

        response = client.post(
            "/push-notifications/subscribe",
            json=subscription_data,
            headers=auth_headers_volunteer,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "subscription_id" in data["data"]
        assert data["data"]["platform"] == "fcm_android"

    def test_get_vapid_public_key(self, client: TestClient):
        """Test getting VAPID public key"""
        response = client.get("/push-notifications/vapid-public-key")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "public_key" in data["data"]
        assert len(data["data"]["public_key"]) > 0

    def test_get_user_subscriptions(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        session: Session,
        test_user_volunteer: User,
    ):
        """Test getting user's push subscriptions"""
        # Create a subscription first
        subscription = PushSubscription(
            user_id=test_user_volunteer.id,
            platform=PlatformType.WEB_PUSH,
            endpoint="https://test.endpoint.com",
            p256dh_key="test-key",
            auth_key="test-auth",
            device_type="desktop",
        )
        session.add(subscription)
        session.commit()

        response = client.get(
            "/push-notifications/subscriptions", headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] >= 1
        assert len(data["data"]["subscriptions"]) >= 1

    def test_unsubscribe_from_notifications(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        session: Session,
        test_user_volunteer: User,
    ):
        """Test unsubscribing from push notifications"""
        # Create a subscription first
        endpoint = "https://test.unsubscribe.endpoint.com"
        subscription = PushSubscription(
            user_id=test_user_volunteer.id,
            platform=PlatformType.WEB_PUSH,
            endpoint=endpoint,
            p256dh_key="test-key",
            auth_key="test-auth",
        )
        session.add(subscription)
        session.commit()

        response = client.delete(
            f"/push-notifications/unsubscribe?endpoint={endpoint}",
            headers=auth_headers_volunteer,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["unsubscribed"] is True


class TestPushNotificationSending:
    """Test push notification sending functionality"""

    def test_send_notification_admin(
        self, client: TestClient, auth_headers_admin: dict, test_user_volunteer: User
    ):
        """Test sending notification as admin"""
        notification_data = {
            "title": "Test Notification",
            "body": "This is a test notification",
            "notification_type": NotificationType.SYSTEM_ANNOUNCEMENT.value,
            "priority": NotificationPriority.NORMAL.value,
            "data": {"test": True},
        }

        response = client.post(
            f"/push-notifications/send?target_user_id={test_user_volunteer.id}",
            json=notification_data,
            headers=auth_headers_admin,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notifications_created" in data["data"]

    def test_send_notification_non_admin(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        test_user_volunteer: User,
    ):
        """Test that non-admin users cannot send notifications"""
        notification_data = {
            "title": "Test Notification",
            "body": "This should fail",
            "notification_type": NotificationType.SYSTEM_ANNOUNCEMENT.value,
        }

        response = client.post(
            f"/push-notifications/send?target_user_id={test_user_volunteer.id}",
            json=notification_data,
            headers=auth_headers_volunteer,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Admin access required" in data["message"]

    def test_send_bulk_notification(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        test_user_volunteer: User,
        test_user_organization: User,
    ):
        """Test sending bulk notifications"""
        notification_data = {
            "title": "Bulk Test Notification",
            "body": "This is a bulk test notification",
            "notification_type": NotificationType.SYSTEM_ANNOUNCEMENT.value,
            "user_ids": [test_user_volunteer.id, test_user_organization.id],
            "priority": NotificationPriority.NORMAL.value,
        }

        response = client.post(
            "/push-notifications/send-bulk",
            json=notification_data,
            headers=auth_headers_admin,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["bulk_send_started"] is True
        assert data["data"]["target_users"] == 2

    def test_send_test_notification(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test sending test notification to current user"""
        response = client.post(
            "/push-notifications/test", headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["test_sent"] is True


class TestNotificationSettings:
    """Test notification settings management"""

    def test_get_notification_settings(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting user notification settings"""
        response = client.get(
            "/push-notifications/settings", headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        settings = data["data"]

        # Check default settings
        assert settings["push_notifications_enabled"] is True
        assert settings["opportunity_matches"] is True
        assert settings["application_updates"] is True
        assert "quiet_hours_start" in settings
        assert "quiet_hours_end" in settings

    def test_update_notification_settings(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test updating user notification settings"""
        update_data = {
            "push_notifications_enabled": False,
            "opportunity_matches": False,
            "quiet_hours_enabled": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
        }

        response = client.put(
            "/push-notifications/settings",
            json=update_data,
            headers=auth_headers_volunteer,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["updated"] is True

        # Verify settings were updated
        response = client.get(
            "/push-notifications/settings", headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        settings = response.json()["data"]
        assert settings["push_notifications_enabled"] is False
        assert settings["opportunity_matches"] is False
        assert settings["quiet_hours_enabled"] is True


class TestNotificationHistory:
    """Test notification history and tracking"""

    def test_get_notification_history(
        self,
        client: TestClient,
        auth_headers_volunteer: dict,
        session: Session,
        test_user_volunteer: User,
    ):
        """Test getting user's notification history"""
        # Create some test notifications
        notification = PushNotification(
            user_id=test_user_volunteer.id,
            title="Test Notification",
            body="Test body",
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            status=NotificationStatus.SENT,
            sent_at=datetime.now(datetime.timezone.utc),
        )
        session.add(notification)
        session.commit()

        response = client.get(
            "/push-notifications/history", headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] >= 1
        assert len(data["data"]["notifications"]) >= 1

    def test_get_notification_history_with_filters(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test getting notification history with filters"""
        response = client.get(
            "/push-notifications/history?status=sent&notification_type=system_announcement&limit=10",
            headers=auth_headers_volunteer,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["limit"] == 10

    def test_track_notification_click(
        self, client: TestClient, session: Session, test_user_volunteer: User
    ):
        """Test tracking notification clicks"""
        # Create a notification
        notification = PushNotification(
            user_id=test_user_volunteer.id,
            title="Clickable Notification",
            body="Click me!",
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            status=NotificationStatus.SENT,
        )
        session.add(notification)
        session.commit()
        session.refresh(notification)

        response = client.post(
            f"/push-notifications/click/{notification.notification_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tracked"] is True


class TestNotificationTemplates:
    """Test notification templates (admin functionality)"""

    def test_get_notification_templates(
        self, client: TestClient, auth_headers_admin: dict, session: Session
    ):
        """Test getting notification templates"""
        # Create a test template
        template = NotificationTemplate(
            template_id="test_template",
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            name="Test Template",
            title_template="Hello {user_name}",
            body_template="You have a new {item_type}: {item_title}",
            variables=["user_name", "item_type", "item_title"],
        )
        session.add(template)
        session.commit()

        response = client.get(
            "/push-notifications/templates", headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] >= 1

    def test_get_notification_templates_non_admin(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test that non-admin users cannot access templates"""
        response = client.get(
            "/push-notifications/templates", headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Admin access required" in data["message"]

    def test_send_templated_notification(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        session: Session,
        test_user_volunteer: User,
    ):
        """Test sending templated notifications"""
        # Create a template
        template = NotificationTemplate(
            template_id="welcome_template",
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            name="Welcome Template",
            title_template="Welcome {user_name}!",
            body_template="Thanks for joining {platform_name}. Get started by {action}!",
            variables=["user_name", "platform_name", "action"],
        )
        session.add(template)
        session.commit()

        notification_data = {
            "template_id": "welcome_template",
            "variables": {
                "user_name": test_user_volunteer.first_name,
                "platform_name": "Seraaj",
                "action": "browsing opportunities",
            },
            "priority": NotificationPriority.NORMAL.value,
        }

        response = client.post(
            f"/push-notifications/send-templated?target_user_id={test_user_volunteer.id}",
            json=notification_data,
            headers=auth_headers_admin,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notifications_created" in data["data"]


class TestNotificationStatistics:
    """Test notification statistics and analytics"""

    def test_get_notification_statistics(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        session: Session,
        test_user_volunteer: User,
    ):
        """Test getting notification statistics"""
        # Create some test notifications
        notifications = [
            PushNotification(
                user_id=test_user_volunteer.id,
                title="Test 1",
                body="Body 1",
                notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                status=NotificationStatus.SENT,
                priority=NotificationPriority.NORMAL,
            ),
            PushNotification(
                user_id=test_user_volunteer.id,
                title="Test 2",
                body="Body 2",
                notification_type=NotificationType.OPPORTUNITY_MATCH,
                status=NotificationStatus.CLICKED,
                priority=NotificationPriority.HIGH,
            ),
        ]

        for notification in notifications:
            session.add(notification)
        session.commit()

        response = client.get(
            "/push-notifications/statistics?days=7", headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        stats = data["data"]

        assert "total_sent" in stats
        assert "total_clicked" in stats
        assert "click_through_rate" in stats
        assert "by_type" in stats
        assert "by_priority" in stats

    def test_get_notification_statistics_non_admin(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test that non-admin users cannot access statistics"""
        response = client.get(
            "/push-notifications/statistics", headers=auth_headers_volunteer
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Admin access required" in data["message"]


class TestPushNotificationService:
    """Test push notification service functionality"""

    def test_subscribe_user(self, session: Session, test_user_volunteer: User):
        """Test subscribing a user to push notifications"""
        service = get_push_notification_service(session)

        subscription_data = {
            "endpoint": "https://test.service.endpoint.com",
            "keys": {"p256dh": "test-p256dh", "auth": "test-auth"},
        }

        device_info = {"device_type": "mobile", "device_name": "Test Device"}

        import asyncio

        subscription = asyncio.run(
            service.subscribe_user(
                user_id=test_user_volunteer.id,
                subscription_data=subscription_data,
                device_info=device_info,
            )
        )

        assert subscription is not None
        assert subscription.user_id == test_user_volunteer.id
        assert subscription.endpoint == subscription_data["endpoint"]
        assert subscription.device_type == "mobile"
        assert subscription.is_active is True

    def test_send_notification(self, session: Session, test_user_volunteer: User):
        """Test sending a push notification"""
        service = get_push_notification_service(session)

        # First subscribe the user
        subscription_data = {
            "endpoint": "https://test.send.endpoint.com",
            "keys": {"p256dh": "test-key", "auth": "test-auth"},
        }

        import asyncio

        asyncio.run(
            service.subscribe_user(
                user_id=test_user_volunteer.id, subscription_data=subscription_data
            )
        )

        # Send notification
        notifications = asyncio.run(
            service.send_notification(
                user_id=test_user_volunteer.id,
                notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                title="Service Test",
                body="Testing notification service",
                data={"test": True},
            )
        )

        assert len(notifications) > 0
        notification = notifications[0]
        assert notification.title == "Service Test"
        assert notification.body == "Testing notification service"
        assert notification.user_id == test_user_volunteer.id

    def test_user_notification_settings(
        self, session: Session, test_user_volunteer: User
    ):
        """Test user notification settings"""
        service = get_push_notification_service(session)

        import asyncio

        settings = asyncio.run(
            service._get_user_notification_settings(test_user_volunteer.id)
        )

        # Should create default settings if none exist
        if not settings:
            settings = NotificationSettings(user_id=test_user_volunteer.id)
            session.add(settings)
            session.commit()

        # Test notification filtering
        should_send = service._should_send_notification(
            settings, NotificationType.SYSTEM_ANNOUNCEMENT
        )
        assert should_send is True  # Default should allow

        # Disable system announcements
        settings.system_announcements = False
        session.add(settings)
        session.commit()

        should_send = service._should_send_notification(
            settings, NotificationType.SYSTEM_ANNOUNCEMENT
        )
        assert should_send is False


class TestPushNotificationIntegration:
    """Test push notification integration features"""

    def test_notification_with_pwa_context(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test push notifications work with PWA context"""
        # Subscribe with PWA headers
        pwa_headers = {**auth_headers_volunteer, "X-Requested-With": "seraaj-pwa"}

        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/pwa-test",
            "keys": {"p256dh": "pwa-p256dh-key", "auth": "pwa-auth-key"},
            "device_type": "pwa",
            "user_agent": "Seraaj PWA",
        }

        response = client.post(
            "/push-notifications/subscribe", json=subscription_data, headers=pwa_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_notification_error_handling(
        self, client: TestClient, auth_headers_volunteer: dict
    ):
        """Test notification error handling"""
        # Try to subscribe with invalid data
        invalid_subscription = {
            "endpoint": "",  # Empty endpoint should fail
            "keys": {},
        }

        response = client.post(
            "/push-notifications/subscribe",
            json=invalid_subscription,
            headers=auth_headers_volunteer,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_notification_security(self, client: TestClient):
        """Test notification security - unauthenticated access"""
        subscription_data = {
            "endpoint": "https://test.security.endpoint.com",
            "keys": {"p256dh": "key", "auth": "auth"},
        }

        # Should require authentication
        response = client.post("/push-notifications/subscribe", json=subscription_data)

        assert response.status_code == 401
