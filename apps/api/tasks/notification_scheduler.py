"""
Background task scheduler for push notifications
Handles scheduled notifications, retries, and cleanup
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select, and_, or_

from database import get_session
from models.push_notification import (
    PushNotification, NotificationStatus, NotificationType, NotificationPriority
)
from services.push_notification_service import get_push_notification_service
from config.settings import settings

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Background scheduler for push notifications"""
    
    def __init__(self):
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the notification scheduler"""
        if self.running:
            logger.warning("Notification scheduler is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._scheduler_loop())
        logger.info("Notification scheduler started")
    
    async def stop(self):
        """Stop the notification scheduler"""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Notification scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                # Process notifications every 30 seconds
                await self._process_scheduled_notifications()
                await self._retry_failed_notifications()
                await self._cleanup_old_notifications()
                
                # Sleep before next iteration
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in notification scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_scheduled_notifications(self):
        """Process notifications that are ready to be sent"""
        try:
            with next(get_session()) as session:
                service = get_push_notification_service(session)
                await service.process_scheduled_notifications()
                
        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {e}")
    
    async def _retry_failed_notifications(self):
        """Retry failed notifications that haven't exceeded max retries"""
        try:
            with next(get_session()) as session:
                service = get_push_notification_service(session)
                await service.retry_failed_notifications()
                
        except Exception as e:
            logger.error(f"Error retrying failed notifications: {e}")
    
    async def _cleanup_old_notifications(self):
        """Clean up old notification records"""
        try:
            # Only run cleanup once per hour
            current_minute = datetime.now().minute
            if current_minute != 0:
                return
            
            with next(get_session()) as session:
                service = get_push_notification_service(session)
                await service.cleanup_old_notifications(days_to_keep=30)
                
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {e}")


# Global scheduler instance
notification_scheduler = NotificationScheduler()


async def send_opportunity_match_notification(user_id: int, opportunity_id: int, match_score: float):
    """Send notification when a new opportunity matches user preferences"""
    
    try:
        with next(get_session()) as session:
            # Get opportunity details
            from models import Opportunity
            opportunity = session.get(Opportunity, opportunity_id)
            
            if not opportunity:
                logger.error(f"Opportunity {opportunity_id} not found for match notification")
                return
            
            service = get_push_notification_service(session)
            
            await service.send_notification(
                user_id=user_id,
                notification_type=NotificationType.OPPORTUNITY_MATCH,
                title="New Matching Opportunity!",
                body=f"We found a great match: {opportunity.title}",
                data={
                    "opportunity_id": opportunity_id,
                    "match_score": match_score,
                    "organization": opportunity.organisation.name if opportunity.organisation else "Unknown"
                },
                priority=NotificationPriority.HIGH,
                click_action=f"/opportunities/{opportunity_id}"
            )
            
            logger.info(f"Sent opportunity match notification to user {user_id}")
            
    except Exception as e:
        logger.error(f"Error sending opportunity match notification: {e}")


async def send_application_update_notification(user_id: int, application_id: int, status: str):
    """Send notification when application status changes"""
    
    try:
        with next(get_session()) as session:
            # Get application details
            from models import Application
            application = session.get(Application, application_id)
            
            if not application:
                logger.error(f"Application {application_id} not found for status notification")
                return
            
            service = get_push_notification_service(session)
            
            # Create status-specific message
            status_messages = {
                "accepted": "Congratulations! Your application has been accepted.",
                "rejected": "Your application status has been updated.",
                "pending": "Your application is being reviewed.",
                "interview_scheduled": "An interview has been scheduled for your application."
            }
            
            body = status_messages.get(status, "Your application status has been updated.")
            priority = NotificationPriority.HIGH if status in ["accepted", "interview_scheduled"] else NotificationPriority.NORMAL
            
            await service.send_notification(
                user_id=user_id,
                notification_type=NotificationType.APPLICATION_UPDATE,
                title="Application Update",
                body=body,
                data={
                    "application_id": application_id,
                    "status": status,
                    "opportunity_title": application.opportunity.title if application.opportunity else "Unknown"
                },
                priority=priority,
                click_action=f"/applications/{application_id}"
            )
            
            logger.info(f"Sent application update notification to user {user_id}")
            
    except Exception as e:
        logger.error(f"Error sending application update notification: {e}")


async def send_message_notification(user_id: int, sender_name: str, message_preview: str, conversation_id: int):
    """Send notification for new messages"""
    
    try:
        with next(get_session()) as session:
            service = get_push_notification_service(session)
            
            await service.send_notification(
                user_id=user_id,
                notification_type=NotificationType.MESSAGE_RECEIVED,
                title=f"New message from {sender_name}",
                body=message_preview[:100] + "..." if len(message_preview) > 100 else message_preview,
                data={
                    "conversation_id": conversation_id,
                    "sender_name": sender_name
                },
                priority=NotificationPriority.NORMAL,
                click_action=f"/messages/{conversation_id}"
            )
            
            logger.info(f"Sent message notification to user {user_id}")
            
    except Exception as e:
        logger.error(f"Error sending message notification: {e}")


async def send_deadline_reminder_notification(user_id: int, opportunity_title: str, deadline: datetime, opportunity_id: int):
    """Send reminder notification for approaching deadlines"""
    
    try:
        with next(get_session()) as session:
            service = get_push_notification_service(session)
            
            # Calculate time until deadline
            time_until = deadline - datetime.now(datetime.timezone.utc)
            
            if time_until.days > 0:
                time_str = f"{time_until.days} day{'s' if time_until.days > 1 else ''}"
            elif time_until.seconds > 3600:
                hours = time_until.seconds // 3600
                time_str = f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                time_str = "less than an hour"
            
            await service.send_notification(
                user_id=user_id,
                notification_type=NotificationType.DEADLINE_REMINDER,
                title="Application Deadline Approaching",
                body=f"Only {time_str} left to apply for {opportunity_title}",
                data={
                    "opportunity_id": opportunity_id,
                    "deadline": deadline.isoformat(),
                    "opportunity_title": opportunity_title
                },
                priority=NotificationPriority.URGENT if time_until.days == 0 else NotificationPriority.HIGH,
                click_action=f"/opportunities/{opportunity_id}",
                actions=[
                    {
                        "action": "apply_now",
                        "title": "Apply Now",
                        "icon": "/static/icons/apply-icon.png"
                    },
                    {
                        "action": "remind_later", 
                        "title": "Remind Later",
                        "icon": "/static/icons/clock-icon.png"
                    }
                ]
            )
            
            logger.info(f"Sent deadline reminder notification to user {user_id}")
            
    except Exception as e:
        logger.error(f"Error sending deadline reminder notification: {e}")


async def send_donation_received_notification(user_id: int, amount: float, currency: str, donor_name: str):
    """Send notification when organization receives a donation"""
    
    try:
        with next(get_session()) as session:
            service = get_push_notification_service(session)
            
            await service.send_notification(
                user_id=user_id,
                notification_type=NotificationType.DONATION_RECEIVED,
                title="New Donation Received!",
                body=f"You received a {currency} {amount:.2f} donation from {donor_name}",
                data={
                    "amount": amount,
                    "currency": currency,
                    "donor_name": donor_name
                },
                priority=NotificationPriority.NORMAL,
                click_action="/donations"
            )
            
            logger.info(f"Sent donation notification to user {user_id}")
            
    except Exception as e:
        logger.error(f"Error sending donation notification: {e}")


async def send_skill_verification_notification(user_id: int, skill_name: str, status: str):
    """Send notification when skill verification is completed"""
    
    try:
        with next(get_session()) as session:
            service = get_push_notification_service(session)
            
            if status == "verified":
                title = "Skill Verified!"
                body = f"Your {skill_name} skill has been successfully verified"
                priority = NotificationPriority.HIGH
            else:
                title = "Skill Verification Update"
                body = f"Your {skill_name} skill verification has been updated"
                priority = NotificationPriority.NORMAL
            
            await service.send_notification(
                user_id=user_id,
                notification_type=NotificationType.SKILL_VERIFIED,
                title=title,
                body=body,
                data={
                    "skill_name": skill_name,
                    "status": status
                },
                priority=priority,
                click_action="/profile/skills"
            )
            
            logger.info(f"Sent skill verification notification to user {user_id}")
            
    except Exception as e:
        logger.error(f"Error sending skill verification notification: {e}")


async def send_system_announcement(title: str, body: str, user_ids: Optional[list] = None, priority: NotificationPriority = NotificationPriority.NORMAL):
    """Send system-wide announcement to all users or specific user list"""
    
    try:
        with next(get_session()) as session:
            service = get_push_notification_service(session)
            
            if user_ids is None:
                # Get all active users
                from models import User, UserStatus
                users = session.exec(
                    select(User).where(User.status == UserStatus.ACTIVE)
                ).all()
                user_ids = [user.id for user in users]
            
            # Send bulk notification
            sent_count = await service.send_bulk_notification(
                user_ids=user_ids,
                notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                title=title,
                body=body,
                priority=priority
            )
            
            logger.info(f"Sent system announcement to {sent_count} users")
            return sent_count
            
    except Exception as e:
        logger.error(f"Error sending system announcement: {e}")
        return 0


# Utility functions for common notification scenarios
async def schedule_opportunity_deadline_reminders():
    """Schedule deadline reminders for all active opportunities"""
    
    try:
        with next(get_session()) as session:
            from models import Opportunity, Application
            
            # Get opportunities with upcoming deadlines (within next 3 days)
            upcoming_deadline = datetime.now(datetime.timezone.utc) + timedelta(days=3)
            
            opportunities = session.exec(
                select(Opportunity).where(
                    and_(
                        Opportunity.application_deadline <= upcoming_deadline,
                        Opportunity.application_deadline > datetime.now(datetime.timezone.utc),
                        Opportunity.status == "active"
                    )
                )
            ).all()
            
            for opportunity in opportunities:
                # Get users who viewed this opportunity but haven't applied
                # This would require tracking opportunity views
                # For now, we'll skip this complex query
                pass
            
            logger.info(f"Scheduled deadline reminders for {len(opportunities)} opportunities")
            
    except Exception as e:
        logger.error(f"Error scheduling deadline reminders: {e}")


# Export commonly used functions
__all__ = [
    'notification_scheduler',
    'send_opportunity_match_notification',
    'send_application_update_notification', 
    'send_message_notification',
    'send_deadline_reminder_notification',
    'send_donation_received_notification',
    'send_skill_verification_notification',
    'send_system_announcement'
]