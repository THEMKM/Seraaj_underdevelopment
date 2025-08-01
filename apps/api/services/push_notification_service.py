"""
Push Notification Service for Seraaj
Handles sending push notifications across different platforms
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from sqlmodel import Session, select, and_, or_
# Import pywebpush only if available (for development)
try:
    import pywebpush
    from pywebpush.webpush import WebPushException
    PYWEBPUSH_AVAILABLE = True
except ImportError:
    PYWEBPUSH_AVAILABLE = False
    WebPushException = Exception
import httpx

from models.push_notification import (
    PushSubscription, PushNotification, NotificationTemplate, 
    NotificationSettings, NotificationDeliveryLog, NotificationAnalytics,
    NotificationType, NotificationPriority, NotificationStatus, PlatformType
)
from models import User
from config.settings import settings
from utils.template_renderer import render_notification_template


logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for managing push notifications"""
    
    def __init__(self, session: Session):
        self.session = session
        self.vapid_private_key = self._get_vapid_private_key()
        self.vapid_public_key = self._get_vapid_public_key()
        self.vapid_claims = {
            "sub": "mailto:notifications@seraaj.org"
        }
        
    def _get_vapid_private_key(self) -> str:
        """Get VAPID private key from settings"""
        # In production, this should come from secure environment variables
        return getattr(settings, 'vapid_private_key', 'demo-vapid-private-key-placeholder')
        
    def _get_vapid_public_key(self) -> str:
        """Get VAPID public key from settings"""
        return getattr(settings, 'vapid_public_key', 'demo-vapid-public-key-placeholder')
    
    async def subscribe_user(
        self, 
        user_id: int,
        subscription_data: Dict[str, Any],
        device_info: Optional[Dict[str, Any]] = None
    ) -> PushSubscription:
        """Subscribe a user to push notifications"""
        
        try:
            # Extract subscription details
            endpoint = subscription_data.get("endpoint")
            keys = subscription_data.get("keys", {})
            p256dh_key = keys.get("p256dh")
            auth_key = keys.get("auth")
            
            if not endpoint:
                raise ValueError("Subscription endpoint is required")
            
            # Determine platform from endpoint
            platform = self._determine_platform(endpoint)
            
            # Check if subscription already exists
            existing_subscription = self.session.exec(
                select(PushSubscription).where(
                    and_(
                        PushSubscription.user_id == user_id,
                        PushSubscription.endpoint == endpoint
                    )
                )
            ).first()
            
            if existing_subscription:
                # Update existing subscription
                existing_subscription.is_active = True
                existing_subscription.notifications_enabled = True
                existing_subscription.p256dh_key = p256dh_key
                existing_subscription.auth_key = auth_key
                existing_subscription.updated_at = datetime.now(datetime.timezone.utc)
                existing_subscription.last_used_at = datetime.now(datetime.timezone.utc)
                
                if device_info:
                    existing_subscription.device_type = device_info.get("device_type", "unknown")
                    existing_subscription.device_name = device_info.get("device_name")
                    existing_subscription.user_agent = device_info.get("user_agent")
                
                self.session.add(existing_subscription)
                self.session.commit()
                self.session.refresh(existing_subscription)
                
                logger.info(f"Updated push subscription for user {user_id}")
                return existing_subscription
            
            # Create new subscription
            subscription = PushSubscription(
                user_id=user_id,
                platform=platform,
                endpoint=endpoint,
                p256dh_key=p256dh_key,
                auth_key=auth_key,
                device_type=device_info.get("device_type", "unknown") if device_info else "unknown",
                device_name=device_info.get("device_name") if device_info else None,
                user_agent=device_info.get("user_agent") if device_info else None,
                notification_types=[t.value for t in NotificationType],  # Enable all by default
                last_used_at=datetime.now(datetime.timezone.utc)
            )
            
            self.session.add(subscription)
            self.session.commit()
            self.session.refresh(subscription)
            
            logger.info(f"Created new push subscription for user {user_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to push notifications: {e}")
            self.session.rollback()
            raise
    
    def _determine_platform(self, endpoint: str) -> PlatformType:
        """Determine platform type from endpoint URL"""
        if "fcm.googleapis.com" in endpoint:
            return PlatformType.FCM_ANDROID
        elif "web.push.apple.com" in endpoint:
            return PlatformType.APNS_IOS
        else:
            return PlatformType.WEB_PUSH
    
    async def unsubscribe_user(self, user_id: int, endpoint: str) -> bool:
        """Unsubscribe a user from push notifications"""
        
        try:
            subscription = self.session.exec(
                select(PushSubscription).where(
                    and_(
                        PushSubscription.user_id == user_id,
                        PushSubscription.endpoint == endpoint
                    )
                )
            ).first()
            
            if subscription:
                subscription.is_active = False
                subscription.notifications_enabled = False
                subscription.updated_at = datetime.now(datetime.timezone.utc)
                
                self.session.add(subscription)
                self.session.commit()
                
                logger.info(f"Unsubscribed user {user_id} from push notifications")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error unsubscribing user {user_id}: {e}")
            self.session.rollback()
            return False
    
    async def send_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        click_action: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        schedule_at: Optional[datetime] = None
    ) -> List[PushNotification]:
        """Send push notification to a user"""
        
        try:
            # Check user notification settings
            user_settings = await self._get_user_notification_settings(user_id)
            if not self._should_send_notification(user_settings, notification_type):
                logger.info(f"Notification blocked by user settings for user {user_id}")
                return []
            
            # Get active subscriptions for user
            subscriptions = self.session.exec(
                select(PushSubscription).where(
                    and_(
                        PushSubscription.user_id == user_id,
                        PushSubscription.is_active == True,
                        PushSubscription.notifications_enabled == True
                    )
                )
            ).all()
            
            if not subscriptions:
                logger.info(f"No active subscriptions found for user {user_id}")
                return []
            
            notifications = []
            
            for subscription in subscriptions:
                # Create notification record
                notification = PushNotification(
                    user_id=user_id,
                    subscription_id=subscription.id,
                    title=title,
                    body=body,
                    notification_type=notification_type,
                    priority=priority,
                    click_action=click_action,
                    actions=actions,
                    data=data or {},
                    scheduled_at=schedule_at
                )
                
                self.session.add(notification)
                notifications.append(notification)
            
            self.session.commit()
            
            # Send immediately if not scheduled
            if not schedule_at:
                for notification in notifications:
                    await self._deliver_notification(notification)
            
            logger.info(f"Created {len(notifications)} notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {e}")
            self.session.rollback()
            raise
    
    async def send_bulk_notification(
        self,
        user_ids: List[int],
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Send notification to multiple users"""
        
        sent_count = 0
        batch_size = 100
        
        try:
            # Process users in batches
            for i in range(0, len(user_ids), batch_size):
                batch_user_ids = user_ids[i:i + batch_size]
                
                # Create notification tasks
                tasks = []
                for user_id in batch_user_ids:
                    task = self.send_notification(
                        user_id=user_id,
                        notification_type=notification_type,
                        title=title,
                        body=body,
                        data=data,
                        priority=priority
                    )
                    tasks.append(task)
                
                # Execute batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successful sends
                for result in batch_results:
                    if isinstance(result, list) and result:
                        sent_count += len(result)
            
            logger.info(f"Sent bulk notification to {sent_count} users")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending bulk notification: {e}")
            raise
    
    async def send_templated_notification(
        self,
        user_id: int,
        template_id: str,
        variables: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Optional[Dict[str, Any]] = None
    ) -> List[PushNotification]:
        """Send notification using a template"""
        
        try:
            # Get template
            template = self.session.exec(
                select(NotificationTemplate).where(
                    and_(
                        NotificationTemplate.template_id == template_id,
                        NotificationTemplate.is_active == True
                    )
                )
            ).first()
            
            if not template:
                raise ValueError(f"Template {template_id} not found or inactive")
            
            # Render template
            title = render_notification_template(template.title_template, variables)
            body = render_notification_template(template.body_template, variables)
            
            # Use template defaults if not specified
            if priority == NotificationPriority.NORMAL and template.default_priority:
                priority = template.default_priority
            
            actions = template.default_actions
            
            return await self.send_notification(
                user_id=user_id,
                notification_type=template.notification_type,
                title=title,
                body=body,
                data=data,
                priority=priority,
                actions=actions
            )
            
        except Exception as e:
            logger.error(f"Error sending templated notification: {e}")
            raise
    
    async def _deliver_notification(self, notification: PushNotification) -> bool:
        """Deliver a single notification"""
        
        try:
            subscription = self.session.get(PushSubscription, notification.subscription_id)
            if not subscription or not subscription.is_active:
                notification.status = NotificationStatus.FAILED
                notification.error_message = "Subscription inactive or not found"
                self.session.add(notification)
                self.session.commit()
                return False
            
            # Check quiet hours
            if await self._is_quiet_hours(subscription):
                logger.info(f"Notification {notification.id} delayed due to quiet hours")
                notification.scheduled_at = await self._calculate_next_send_time(subscription)
                self.session.add(notification)
                self.session.commit()
                return False
            
            # Prepare notification payload
            payload = self._prepare_notification_payload(notification)
            
            # Send based on platform
            success = False
            if subscription.platform == PlatformType.WEB_PUSH:
                success = await self._send_web_push(subscription, payload)
            elif subscription.platform == PlatformType.FCM_ANDROID:
                success = await self._send_fcm_notification(subscription, payload)
            elif subscription.platform == PlatformType.APNS_IOS:
                success = await self._send_apns_notification(subscription, payload)
            
            # Update notification status
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now(datetime.timezone.utc)
                logger.info(f"Successfully sent notification {notification.id}")
            else:
                notification.status = NotificationStatus.FAILED
                notification.retry_count += 1
                logger.error(f"Failed to send notification {notification.id}")
            
            self.session.add(notification)
            self.session.commit()
            
            # Log delivery attempt
            await self._log_delivery_attempt(notification, subscription.platform, success)
            
            return success
            
        except Exception as e:
            logger.error(f"Error delivering notification {notification.id}: {e}")
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            notification.retry_count += 1
            self.session.add(notification)
            self.session.commit()
            return False
    
    async def _send_web_push(self, subscription: PushSubscription, payload: Dict[str, Any]) -> bool:
        """Send web push notification"""
        
        try:
            # In development mode, just log the notification
            if settings.environment.value == "development":
                logger.info(f"[DEV MODE] Web push notification: {payload}")
                return True
            
            # Create subscription info for pywebpush
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh_key,
                    "auth": subscription.auth_key
                }
            }
            
            # Send notification
            if PYWEBPUSH_AVAILABLE:
                response = pywebpush.webpush(
                    subscription_info=subscription_info,
                    data=json.dumps(payload),
                    vapid_private_key=self.vapid_private_key,
                    vapid_claims=self.vapid_claims
                )
                return response.status_code in [200, 201, 204]
            else:
                logger.info(f"[DEV MODE] pywebpush not available, simulating web push: {payload}")
                return True
            
        except WebPushException as e:
            logger.error(f"Web push error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in web push: {e}")
            return False
    
    async def _send_fcm_notification(self, subscription: PushSubscription, payload: Dict[str, Any]) -> bool:
        """Send FCM notification for Android"""
        
        try:
            # In development mode, just log the notification
            if settings.environment.value == "development":
                logger.info(f"[DEV MODE] FCM notification: {payload}")
                return True
            
            # This would require FCM server key and proper implementation
            # For now, fall back to web push
            return await self._send_web_push(subscription, payload)
            
        except Exception as e:
            logger.error(f"FCM notification error: {e}")
            return False
    
    async def _send_apns_notification(self, subscription: PushSubscription, payload: Dict[str, Any]) -> bool:
        """Send APNS notification for iOS"""
        
        try:
            # In development mode, just log the notification
            if settings.environment.value == "development":
                logger.info(f"[DEV MODE] APNS notification: {payload}")
                return True
            
            # This would require APNS certificates and proper implementation
            # For now, fall back to web push
            return await self._send_web_push(subscription, payload)
            
        except Exception as e:
            logger.error(f"APNS notification error: {e}")
            return False
    
    def _prepare_notification_payload(self, notification: PushNotification) -> Dict[str, Any]:
        """Prepare notification payload for delivery"""
        
        payload = {
            "title": notification.title,
            "body": notification.body,
            "icon": notification.icon,
            "badge": notification.badge,
            "tag": f"seraaj-{notification.notification_type.value}",
            "data": {
                "notification_id": notification.notification_id,
                "notification_type": notification.notification_type.value,
                "click_action": notification.click_action,
                "timestamp": notification.created_at.isoformat(),
                **notification.data
            }
        }
        
        # Add image if specified
        if notification.image:
            payload["image"] = notification.image
        
        # Add actions if specified
        if notification.actions:
            payload["actions"] = notification.actions
        
        # Add platform-specific options
        payload["options"] = {
            "requireInteraction": notification.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT],
            "silent": notification.priority == NotificationPriority.LOW
        }
        
        return payload
    
    async def _get_user_notification_settings(self, user_id: int) -> Optional[NotificationSettings]:
        """Get user notification settings"""
        
        return self.session.exec(
            select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        ).first()
    
    def _should_send_notification(self, settings: Optional[NotificationSettings], notification_type: NotificationType) -> bool:
        """Check if notification should be sent based on user settings"""
        
        if not settings:
            return True  # Default to allowing notifications
        
        if not settings.push_notifications_enabled:
            return False
        
        # Check specific notification type settings
        type_mapping = {
            NotificationType.OPPORTUNITY_MATCH: settings.opportunity_matches,
            NotificationType.APPLICATION_UPDATE: settings.application_updates,
            NotificationType.MESSAGE_RECEIVED: settings.messages,
            NotificationType.DEADLINE_REMINDER: settings.deadlines,
            NotificationType.SCHEDULE_UPDATE: settings.schedule_changes,
            NotificationType.SYSTEM_ANNOUNCEMENT: settings.system_announcements,
            NotificationType.DONATION_RECEIVED: settings.donations,
            NotificationType.VOLUNTEER_JOINED: settings.volunteer_activity,
            NotificationType.REVIEW_REQUEST: settings.reviews,
            NotificationType.SKILL_VERIFIED: settings.skill_verifications
        }
        
        return type_mapping.get(notification_type, True)
    
    async def _is_quiet_hours(self, subscription: PushSubscription) -> bool:
        """Check if current time is within user's quiet hours"""
        
        # This is a simplified implementation
        # In production, you'd need proper timezone handling
        
        if not subscription.quiet_hours_start or not subscription.quiet_hours_end:
            return False
        
        # For now, assume UTC
        current_time = datetime.now(datetime.timezone.utc).time()
        start_time = datetime.strptime(subscription.quiet_hours_start, "%H:%M").time()
        end_time = datetime.strptime(subscription.quiet_hours_end, "%H:%M").time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Quiet hours cross midnight
            return current_time >= start_time or current_time <= end_time
    
    async def _calculate_next_send_time(self, subscription: PushSubscription) -> datetime:
        """Calculate next appropriate send time outside quiet hours"""
        
        # Simplified implementation - send after quiet hours end
        now = datetime.now(datetime.timezone.utc)
        
        if subscription.quiet_hours_end:
            end_time = datetime.strptime(subscription.quiet_hours_end, "%H:%M").time()
            next_send = now.replace(
                hour=end_time.hour,
                minute=end_time.minute,
                second=0,
                microsecond=0
            )
            
            if next_send <= now:
                next_send += timedelta(days=1)
            
            return next_send
        
        return now + timedelta(minutes=30)  # Default delay
    
    async def _log_delivery_attempt(self, notification: PushNotification, platform: PlatformType, success: bool):
        """Log notification delivery attempt"""
        
        try:
            delivery_log = NotificationDeliveryLog(
                notification_id=notification.id,
                platform=platform,
                attempt_number=notification.retry_count + 1,
                status=NotificationStatus.SENT if success else NotificationStatus.FAILED
            )
            
            self.session.add(delivery_log)
            self.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging delivery attempt: {e}")
    
    async def process_scheduled_notifications(self):
        """Process notifications scheduled for sending"""
        
        try:
            # Get notifications ready to send
            now = datetime.now(datetime.timezone.utc)
            
            notifications = self.session.exec(
                select(PushNotification).where(
                    and_(
                        PushNotification.status == NotificationStatus.PENDING,
                        or_(
                            PushNotification.scheduled_at.is_(None),
                            PushNotification.scheduled_at <= now
                        )
                    )
                )
            ).all()
            
            logger.info(f"Processing {len(notifications)} scheduled notifications")
            
            # Process in batches
            batch_size = 50
            for i in range(0, len(notifications), batch_size):
                batch = notifications[i:i + batch_size]
                
                # Create delivery tasks
                tasks = [self._deliver_notification(notification) for notification in batch]
                
                # Execute batch
                await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {e}")
    
    async def retry_failed_notifications(self):
        """Retry failed notifications that haven't exceeded max retries"""
        
        try:
            # Get failed notifications eligible for retry
            failed_notifications = self.session.exec(
                select(PushNotification).where(
                    and_(
                        PushNotification.status == NotificationStatus.FAILED,
                        PushNotification.retry_count < PushNotification.max_retries,
                        PushNotification.created_at > datetime.now(datetime.timezone.utc) - timedelta(hours=24)
                    )
                )
            ).all()
            
            logger.info(f"Retrying {len(failed_notifications)} failed notifications")
            
            for notification in failed_notifications:
                await self._deliver_notification(notification)
            
        except Exception as e:
            logger.error(f"Error retrying failed notifications: {e}")
    
    async def cleanup_old_notifications(self, days_to_keep: int = 30):
        """Clean up old notification records"""
        
        try:
            cutoff_date = datetime.now(datetime.timezone.utc) - timedelta(days=days_to_keep)
            
            # Delete old notifications
            old_notifications = self.session.exec(
                select(PushNotification).where(PushNotification.created_at < cutoff_date)
            ).all()
            
            for notification in old_notifications:
                self.session.delete(notification)
            
            self.session.commit()
            
            logger.info(f"Cleaned up {len(old_notifications)} old notifications")
            
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {e}")
            self.session.rollback()


def get_push_notification_service(session: Session) -> PushNotificationService:
    """Get push notification service instance"""
    return PushNotificationService(session)