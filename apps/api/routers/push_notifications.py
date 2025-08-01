"""
Push Notifications Router for Seraaj
Handles push notification subscriptions and management
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlmodel import Session, select, and_
from typing import Annotated, Dict, Any, List, Optional
from datetime import datetime

from database import get_session
from models import User
from models.push_notification import (
    PushSubscription,
    PushNotification,
    NotificationSettings,
    NotificationTemplate,
    NotificationType,
    NotificationPriority,
    NotificationStatus,
)
from routers.auth import get_current_user, get_current_user_optional
from services.push_notification_service import get_push_notification_service
from utils.response_formatter import success_with_data, error_response
from config.settings import settings
import logging

router = APIRouter(prefix="/v1/push-notifications", tags=["push-notifications"])
logger = logging.getLogger(__name__)


# Pydantic models for request/response
from pydantic import BaseModel


class SubscriptionRequest(BaseModel):
    endpoint: str
    keys: Dict[str, str]  # p256dh and auth keys
    device_type: Optional[str] = "unknown"
    device_name: Optional[str] = None
    user_agent: Optional[str] = None


class NotificationRequest(BaseModel):
    title: str
    body: str
    notification_type: NotificationType
    priority: Optional[NotificationPriority] = NotificationPriority.NORMAL
    click_action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    schedule_at: Optional[datetime] = None


class BulkNotificationRequest(BaseModel):
    title: str
    body: str
    notification_type: NotificationType
    user_ids: List[int]
    priority: Optional[NotificationPriority] = NotificationPriority.NORMAL
    data: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None


class TemplatedNotificationRequest(BaseModel):
    template_id: str
    variables: Dict[str, Any]
    priority: Optional[NotificationPriority] = NotificationPriority.NORMAL
    data: Optional[Dict[str, Any]] = None


class NotificationSettingsUpdate(BaseModel):
    push_notifications_enabled: Optional[bool] = None
    opportunity_matches: Optional[bool] = None
    application_updates: Optional[bool] = None
    messages: Optional[bool] = None
    deadlines: Optional[bool] = None
    schedule_changes: Optional[bool] = None
    system_announcements: Optional[bool] = None
    donations: Optional[bool] = None
    volunteer_activity: Optional[bool] = None
    reviews: Optional[bool] = None
    skill_verifications: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    digest_enabled: Optional[bool] = None
    digest_frequency: Optional[str] = None


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """Get VAPID public key for web push subscription"""

    try:
        # In development, return a demo key
        if settings.environment.value == "development":
            demo_key = "BEl62iUYgUivxIkv69yViEuiBIa40HI80NqIUHxHtjZHhr-RNZIwGKvlJ_SiuRzr3MZgJTBhOGXFu6_MmQhOhGE"
            return success_with_data(
                {"public_key": demo_key}, "VAPID public key retrieved"
            )

        # In production, get from push notification service
        service = get_push_notification_service(None)
        public_key = service._get_vapid_public_key()

        return success_with_data(
            {"public_key": public_key}, "VAPID public key retrieved"
        )

    except Exception as e:
        logger.error(f"Error getting VAPID public key: {e}")
        return error_response("Failed to get VAPID public key", 500)


@router.post("/subscribe")
async def subscribe_to_notifications(
    subscription_data: SubscriptionRequest,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Subscribe user to push notifications"""

    try:
        service = get_push_notification_service(session)

        # Prepare device info
        device_info = {
            "device_type": subscription_data.device_type,
            "device_name": subscription_data.device_name,
            "user_agent": subscription_data.user_agent,
        }

        # Create subscription
        subscription = await service.subscribe_user(
            user_id=user.id,
            subscription_data={
                "endpoint": subscription_data.endpoint,
                "keys": subscription_data.keys,
            },
            device_info=device_info,
        )

        return success_with_data(
            {
                "subscription_id": subscription.subscription_id,
                "platform": subscription.platform,
                "created_at": subscription.created_at.isoformat(),
            },
            "Successfully subscribed to push notifications",
        )

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error subscribing user {user.id} to notifications: {e}")
        return error_response("Failed to subscribe to notifications", 500)


@router.delete("/unsubscribe")
async def unsubscribe_from_notifications(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    endpoint: str = Query(..., description="Subscription endpoint to unsubscribe"),
):
    """Unsubscribe user from push notifications"""

    try:
        service = get_push_notification_service(session)

        success = await service.unsubscribe_user(user.id, endpoint)

        if success:
            return success_with_data(
                {"unsubscribed": True}, "Successfully unsubscribed from notifications"
            )
        else:
            return error_response("Subscription not found", 404)

    except Exception as e:
        logger.error(f"Error unsubscribing user {user.id}: {e}")
        return error_response("Failed to unsubscribe from notifications", 500)


@router.get("/subscriptions")
async def get_user_subscriptions(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get user's active push notification subscriptions"""

    try:
        subscriptions = session.exec(
            select(PushSubscription).where(
                and_(
                    PushSubscription.user_id == user.id,
                    PushSubscription.is_active == True,
                )
            )
        ).all()

        subscription_data = []
        for sub in subscriptions:
            subscription_data.append(
                {
                    "subscription_id": sub.subscription_id,
                    "platform": sub.platform,
                    "device_type": sub.device_type,
                    "device_name": sub.device_name,
                    "notifications_enabled": sub.notifications_enabled,
                    "created_at": sub.created_at.isoformat(),
                    "last_used_at": (
                        sub.last_used_at.isoformat() if sub.last_used_at else None
                    ),
                }
            )

        return success_with_data(
            {"subscriptions": subscription_data, "total": len(subscription_data)},
            "User subscriptions retrieved",
        )

    except Exception as e:
        logger.error(f"Error getting subscriptions for user {user.id}: {e}")
        return error_response("Failed to get subscriptions", 500)


@router.post("/send")
async def send_notification(
    notification_data: NotificationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    target_user_id: int = Query(..., description="User ID to send notification to"),
):
    """Send push notification to a specific user (admin only)"""

    # Check admin permissions
    if current_user.role != "admin":
        return error_response("Admin access required", 403)

    try:
        service = get_push_notification_service(session)

        notifications = await service.send_notification(
            user_id=target_user_id,
            notification_type=notification_data.notification_type,
            title=notification_data.title,
            body=notification_data.body,
            data=notification_data.data,
            priority=notification_data.priority,
            click_action=notification_data.click_action,
            actions=notification_data.actions,
            schedule_at=notification_data.schedule_at,
        )

        return success_with_data(
            {
                "notifications_created": len(notifications),
                "notification_ids": [n.notification_id for n in notifications],
            },
            "Notification sent successfully",
        )

    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return error_response("Failed to send notification", 500)


@router.post("/send-bulk")
async def send_bulk_notification(
    notification_data: BulkNotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Send push notification to multiple users (admin only)"""

    # Check admin permissions
    if current_user.role != "admin":
        return error_response("Admin access required", 403)

    try:
        service = get_push_notification_service(session)

        # Add background task for bulk sending
        background_tasks.add_task(
            service.send_bulk_notification,
            user_ids=notification_data.user_ids,
            notification_type=notification_data.notification_type,
            title=notification_data.title,
            body=notification_data.body,
            data=notification_data.data,
            priority=notification_data.priority,
            filters=notification_data.filters,
        )

        return success_with_data(
            {
                "bulk_send_started": True,
                "target_users": len(notification_data.user_ids),
            },
            "Bulk notification sending started",
        )

    except Exception as e:
        logger.error(f"Error starting bulk notification: {e}")
        return error_response("Failed to start bulk notification", 500)


@router.post("/send-templated")
async def send_templated_notification(
    notification_data: TemplatedNotificationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    target_user_id: int = Query(..., description="User ID to send notification to"),
):
    """Send templated push notification (admin only)"""

    # Check admin permissions
    if current_user.role != "admin":
        return error_response("Admin access required", 403)

    try:
        service = get_push_notification_service(session)

        notifications = await service.send_templated_notification(
            user_id=target_user_id,
            template_id=notification_data.template_id,
            variables=notification_data.variables,
            priority=notification_data.priority,
            data=notification_data.data,
        )

        return success_with_data(
            {
                "notifications_created": len(notifications),
                "notification_ids": [n.notification_id for n in notifications],
            },
            "Templated notification sent successfully",
        )

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error sending templated notification: {e}")
        return error_response("Failed to send templated notification", 500)


@router.get("/settings")
async def get_notification_settings(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get user's notification settings"""

    try:
        settings = session.exec(
            select(NotificationSettings).where(NotificationSettings.user_id == user.id)
        ).first()

        if not settings:
            # Create default settings
            settings = NotificationSettings(user_id=user.id)
            session.add(settings)
            session.commit()
            session.refresh(settings)

        settings_data = {
            "push_notifications_enabled": settings.push_notifications_enabled,
            "email_notifications_enabled": settings.email_notifications_enabled,
            "in_app_notifications_enabled": settings.in_app_notifications_enabled,
            "opportunity_matches": settings.opportunity_matches,
            "application_updates": settings.application_updates,
            "messages": settings.messages,
            "deadlines": settings.deadlines,
            "schedule_changes": settings.schedule_changes,
            "system_announcements": settings.system_announcements,
            "donations": settings.donations,
            "volunteer_activity": settings.volunteer_activity,
            "reviews": settings.reviews,
            "skill_verifications": settings.skill_verifications,
            "quiet_hours_enabled": settings.quiet_hours_enabled,
            "quiet_hours_start": settings.quiet_hours_start,
            "quiet_hours_end": settings.quiet_hours_end,
            "timezone": settings.timezone,
            "digest_enabled": settings.digest_enabled,
            "digest_frequency": settings.digest_frequency,
            "mobile_notifications": settings.mobile_notifications,
            "desktop_notifications": settings.desktop_notifications,
        }

        return success_with_data(settings_data, "Notification settings retrieved")

    except Exception as e:
        logger.error(f"Error getting notification settings for user {user.id}: {e}")
        return error_response("Failed to get notification settings", 500)


@router.put("/settings")
async def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Update user's notification settings"""

    try:
        settings = session.exec(
            select(NotificationSettings).where(NotificationSettings.user_id == user.id)
        ).first()

        if not settings:
            settings = NotificationSettings(user_id=user.id)

        # Update settings
        update_data = settings_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)

        settings.updated_at = datetime.now(datetime.timezone.utc)

        session.add(settings)
        session.commit()
        session.refresh(settings)

        return success_with_data({"updated": True}, "Notification settings updated")

    except Exception as e:
        logger.error(f"Error updating notification settings for user {user.id}: {e}")
        return error_response("Failed to update notification settings", 500)


@router.get("/history")
async def get_notification_history(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0),
    status: Optional[NotificationStatus] = Query(default=None),
    notification_type: Optional[NotificationType] = Query(default=None),
):
    """Get user's notification history"""

    try:
        # Build query
        query = select(PushNotification).where(PushNotification.user_id == user.id)

        if status:
            query = query.where(PushNotification.status == status)

        if notification_type:
            query = query.where(PushNotification.notification_type == notification_type)

        query = (
            query.order_by(PushNotification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        notifications = session.exec(query).all()

        history_data = []
        for notification in notifications:
            history_data.append(
                {
                    "notification_id": notification.notification_id,
                    "title": notification.title,
                    "body": notification.body,
                    "notification_type": notification.notification_type,
                    "priority": notification.priority,
                    "status": notification.status,
                    "created_at": notification.created_at.isoformat(),
                    "sent_at": (
                        notification.sent_at.isoformat()
                        if notification.sent_at
                        else None
                    ),
                    "clicked_at": (
                        notification.clicked_at.isoformat()
                        if notification.clicked_at
                        else None
                    ),
                    "click_action": notification.click_action,
                    "data": notification.data,
                }
            )

        return success_with_data(
            {
                "notifications": history_data,
                "total": len(history_data),
                "offset": offset,
                "limit": limit,
            },
            "Notification history retrieved",
        )

    except Exception as e:
        logger.error(f"Error getting notification history for user {user.id}: {e}")
        return error_response("Failed to get notification history", 500)


@router.post("/click/{notification_id}")
async def track_notification_click(
    notification_id: str,
    user: Annotated[Optional[User], Depends(get_current_user_optional)],
    session: Annotated[Session, Depends(get_session)],
):
    """Track notification click"""

    try:
        notification = session.exec(
            select(PushNotification).where(
                PushNotification.notification_id == notification_id
            )
        ).first()

        if not notification:
            return error_response("Notification not found", 404)

        # Update click status
        notification.status = NotificationStatus.CLICKED
        notification.clicked_at = datetime.now(datetime.timezone.utc)

        session.add(notification)
        session.commit()

        logger.info(
            f"Notification {notification_id} clicked by user {user.id if user else 'anonymous'}"
        )

        return success_with_data({"tracked": True}, "Notification click tracked")

    except Exception as e:
        logger.error(f"Error tracking notification click: {e}")
        return error_response("Failed to track notification click", 500)


@router.get("/templates")
async def get_notification_templates(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    notification_type: Optional[NotificationType] = Query(default=None),
):
    """Get notification templates (admin only)"""

    # Check admin permissions
    if current_user.role != "admin":
        return error_response("Admin access required", 403)

    try:
        query = select(NotificationTemplate).where(
            NotificationTemplate.is_active == True
        )

        if notification_type:
            query = query.where(
                NotificationTemplate.notification_type == notification_type
            )

        templates = session.exec(query).all()

        template_data = []
        for template in templates:
            template_data.append(
                {
                    "template_id": template.template_id,
                    "name": template.name,
                    "description": template.description,
                    "notification_type": template.notification_type,
                    "title_template": template.title_template,
                    "body_template": template.body_template,
                    "variables": template.variables,
                    "default_priority": template.default_priority,
                }
            )

        return success_with_data(
            {"templates": template_data, "total": len(template_data)},
            "Notification templates retrieved",
        )

    except Exception as e:
        logger.error(f"Error getting notification templates: {e}")
        return error_response("Failed to get notification templates", 500)


@router.get("/statistics")
async def get_notification_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    days: int = Query(default=7, le=90),
):
    """Get notification statistics (admin only)"""

    # Check admin permissions
    if current_user.role != "admin":
        return error_response("Admin access required", 403)

    try:
        from datetime import datetime, timedelta

        since_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)

        # Get basic stats
        total_notifications = session.exec(
            select(PushNotification).where(PushNotification.created_at >= since_date)
        ).all()

        stats = {
            "total_sent": len(
                [n for n in total_notifications if n.status == NotificationStatus.SENT]
            ),
            "total_delivered": len(
                [
                    n
                    for n in total_notifications
                    if n.status == NotificationStatus.DELIVERED
                ]
            ),
            "total_clicked": len(
                [
                    n
                    for n in total_notifications
                    if n.status == NotificationStatus.CLICKED
                ]
            ),
            "total_failed": len(
                [
                    n
                    for n in total_notifications
                    if n.status == NotificationStatus.FAILED
                ]
            ),
            "by_type": {},
            "by_priority": {},
            "click_through_rate": 0.0,
            "delivery_rate": 0.0,
        }

        # Calculate rates
        if stats["total_sent"] > 0:
            stats["click_through_rate"] = (
                stats["total_clicked"] / stats["total_sent"]
            ) * 100
            stats["delivery_rate"] = (
                stats["total_delivered"] / stats["total_sent"]
            ) * 100

        # Group by type and priority
        for notification in total_notifications:
            # By type
            type_key = notification.notification_type.value
            if type_key not in stats["by_type"]:
                stats["by_type"][type_key] = {"sent": 0, "clicked": 0}

            if notification.status in [
                NotificationStatus.SENT,
                NotificationStatus.DELIVERED,
            ]:
                stats["by_type"][type_key]["sent"] += 1
            if notification.status == NotificationStatus.CLICKED:
                stats["by_type"][type_key]["clicked"] += 1

            # By priority
            priority_key = notification.priority.value
            if priority_key not in stats["by_priority"]:
                stats["by_priority"][priority_key] = 0
            stats["by_priority"][priority_key] += 1

        return success_with_data(stats, f"Notification statistics for last {days} days")

    except Exception as e:
        logger.error(f"Error getting notification statistics: {e}")
        return error_response("Failed to get notification statistics", 500)


@router.post("/test")
async def send_test_notification(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Send test notification to current user"""

    try:
        service = get_push_notification_service(session)

        notifications = await service.send_notification(
            user_id=user.id,
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title="Test Notification",
            body=f"Hello {user.first_name}! This is a test notification from Seraaj.",
            data={
                "test": True,
                "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            },
            priority=NotificationPriority.NORMAL,
        )

        return success_with_data(
            {"test_sent": True, "notifications_created": len(notifications)},
            "Test notification sent",
        )

    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        return error_response("Failed to send test notification", 500)
