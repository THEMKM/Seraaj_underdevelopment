from typing import List, Dict, Optional, Any
from sqlmodel import Session, select, and_, or_
from datetime import datetime, timedelta, date, time, timezone
import logging
from enum import Enum
import uuid
from dataclasses import dataclass

from models import User, Volunteer, Opportunity, Application, AnalyticsEvent

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of calendar events"""

    INTERVIEW = "interview"
    ORIENTATION = "orientation"
    VOLUNTEER_SESSION = "volunteer_session"
    TRAINING = "training"
    MEETING = "meeting"
    DEADLINE_REMINDER = "deadline_reminder"
    FOLLOW_UP = "follow_up"


class EventStatus(str, Enum):
    """Status of calendar events"""

    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class RecurrenceType(str, Enum):
    """Event recurrence patterns"""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class CalendarEvent:
    """Calendar event data structure"""

    id: Optional[int] = None
    title: str = ""
    description: str = ""
    event_type: EventType = EventType.MEETING
    start_datetime: datetime = datetime.now(timezone.utc)
    end_datetime: datetime = datetime.now(timezone.utc) + timedelta(hours=1)
    location: str = ""
    virtual_meeting_url: Optional[str] = None
    organizer_id: int = 0
    participant_ids: List[int] = None
    opportunity_id: Optional[int] = None
    application_id: Optional[int] = None
    status: EventStatus = EventStatus.SCHEDULED
    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_data: Dict[str, Any] = None
    reminder_minutes: List[int] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self):
        if self.participant_ids is None:
            self.participant_ids = []
        if self.recurrence_data is None:
            self.recurrence_data = {}
        if self.reminder_minutes is None:
            self.reminder_minutes = [15, 60]  # Default reminders
        if self.metadata is None:
            self.metadata = {}


class CalendarScheduler:
    """Advanced calendar and scheduling system for volunteer opportunities"""

    def __init__(self):
        # Time zone handling (simplified for MVP)
        self.default_timezone = "UTC"

        # Default availability patterns
        self.business_hours = {
            "start": time(9, 0),  # 9:00 AM
            "end": time(17, 0),  # 5:00 PM
            "days": [0, 1, 2, 3, 4],  # Monday to Friday
        }

        # Event duration defaults (in minutes)
        self.default_durations = {
            EventType.INTERVIEW: 45,
            EventType.ORIENTATION: 120,
            EventType.VOLUNTEER_SESSION: 240,
            EventType.TRAINING: 180,
            EventType.MEETING: 60,
            EventType.FOLLOW_UP: 30,
        }

    def create_event(
        self, session: Session, event_data: CalendarEvent, created_by: int
    ) -> CalendarEvent:
        """Create a new calendar event"""

        # Validate event data
        self._validate_event_data(event_data)

        # Check for conflicts
        conflicts = self._check_scheduling_conflicts(
            session,
            event_data.start_datetime,
            event_data.end_datetime,
            event_data.participant_ids + [event_data.organizer_id],
        )

        if conflicts:
            raise ValueError(f"Scheduling conflicts detected: {conflicts}")

        # Generate unique event ID
        if not event_data.id:
            event_data.id = hash(
                f"{event_data.title}_{event_data.start_datetime}_{uuid.uuid4()}"
            )

        # Store event (in a real implementation, this would go to a calendar_events table)
        event_record = {
            "id": event_data.id,
            "title": event_data.title,
            "description": event_data.description,
            "event_type": event_data.event_type.value,
            "start_datetime": event_data.start_datetime.isoformat(),
            "end_datetime": event_data.end_datetime.isoformat(),
            "location": event_data.location,
            "virtual_meeting_url": event_data.virtual_meeting_url,
            "organizer_id": event_data.organizer_id,
            "participant_ids": event_data.participant_ids,
            "opportunity_id": event_data.opportunity_id,
            "application_id": event_data.application_id,
            "status": event_data.status.value,
            "recurrence_type": event_data.recurrence_type.value,
            "recurrence_data": event_data.recurrence_data,
            "reminder_minutes": event_data.reminder_minutes,
            "metadata": event_data.metadata,
            "created_by": created_by,
            "created_at": event_data.created_at.isoformat(),
            "updated_at": event_data.updated_at.isoformat(),
        }

        # Log event creation
        self._log_calendar_event(
            session, "event_created", event_data.id, created_by, event_record
        )

        # Schedule reminders
        self._schedule_reminders(session, event_data)

        # Send notifications to participants
        self._notify_participants(session, event_data, "event_created")

        logger.info(
            f"Calendar event created: {event_data.title} at {event_data.start_datetime}"
        )
        return event_data

    def _validate_event_data(self, event_data: CalendarEvent):
        """Validate calendar event data"""

        if not event_data.title.strip():
            raise ValueError("Event title is required")

        if event_data.start_datetime >= event_data.end_datetime:
            raise ValueError("End time must be after start time")

        if event_data.start_datetime < datetime.now(timezone.utc) - timedelta(
            minutes=5
        ):
            raise ValueError("Cannot schedule events in the past")

        # Validate duration (max 24 hours)
        duration = event_data.end_datetime - event_data.start_datetime
        if duration > timedelta(hours=24):
            raise ValueError("Event duration cannot exceed 24 hours")

        if (
            not event_data.participant_ids
            and event_data.event_type != EventType.DEADLINE_REMINDER
        ):
            raise ValueError("At least one participant is required")

    def _check_scheduling_conflicts(
        self,
        session: Session,
        start_time: datetime,
        end_time: datetime,
        user_ids: List[int],
    ) -> List[Dict[str, Any]]:
        """Check for scheduling conflicts with existing events"""

        conflicts = []

        # Check against business hours
        if not self._is_within_business_hours(start_time, end_time):
            conflicts.append(
                {
                    "type": "business_hours",
                    "message": "Event is outside standard business hours",
                }
            )

        # Check for user availability against existing calendar events
        from models import CalendarEvent

        for user_id in user_ids:
            # Query for overlapping events for this user
            overlapping_events = session.exec(
                select(CalendarEvent).where(
                    and_(
                        CalendarEvent.user_id == user_id,
                        or_(
                            # Event starts during existing event
                            and_(
                                CalendarEvent.start_datetime <= start_time,
                                CalendarEvent.end_datetime > start_time,
                            ),
                            # Event ends during existing event
                            and_(
                                CalendarEvent.start_datetime < end_time,
                                CalendarEvent.end_datetime >= end_time,
                            ),
                            # Event encompasses existing event
                            and_(
                                CalendarEvent.start_datetime >= start_time,
                                CalendarEvent.end_datetime <= end_time,
                            ),
                        ),
                    )
                )
            ).all()

            for event in overlapping_events:
                user = session.get(User, user_id)
                conflicts.append(
                    {
                        "type": "user_conflict",
                        "user_id": user_id,
                        "user_name": (
                            f"{user.first_name} {user.last_name}"
                            if user
                            else "Unknown User"
                        ),
                        "conflicting_event_id": event.id,
                        "conflicting_event_title": event.title,
                        "conflict_start": event.start_datetime.isoformat(),
                        "conflict_end": event.end_datetime.isoformat(),
                        "message": f"User has conflicting event: {event.title}",
                    }
                )

        return conflicts

    def _is_within_business_hours(
        self, start_time: datetime, end_time: datetime
    ) -> bool:
        """Check if event is within business hours"""

        # Check day of week
        if start_time.weekday() not in self.business_hours["days"]:
            return False

        # Check time range
        start_time_only = start_time.time()
        end_time_only = end_time.time()

        if (
            start_time_only < self.business_hours["start"]
            or end_time_only > self.business_hours["end"]
        ):
            return False

        return True

    def schedule_interview(
        self,
        session: Session,
        application_id: int,
        interviewer_id: int,
        proposed_times: List[datetime],
        duration_minutes: int = 45,
        location: str = "",
        virtual_meeting_url: str = "",
        notes: str = "",
    ) -> CalendarEvent:
        """Schedule an interview for an application"""

        application = session.get(Application, application_id)
        if not application:
            raise ValueError("Application not found")

        # Get volunteer and opportunity details
        volunteer = session.get(Volunteer, application.volunteer_id)
        opportunity = session.get(Opportunity, application.opportunity_id)

        if not volunteer or not opportunity:
            raise ValueError("Invalid application data")

        # Find best available time slot
        best_time = self._find_best_time_slot(
            session,
            proposed_times,
            duration_minutes,
            [interviewer_id, volunteer.user_id],
        )

        if not best_time:
            raise ValueError("No suitable time slot found")

        # Create interview event
        event_data = CalendarEvent(
            title=f"Interview: {opportunity.title}",
            description=f"Interview for {volunteer.full_name} - {opportunity.title}\n\nNotes: {notes}",
            event_type=EventType.INTERVIEW,
            start_datetime=best_time,
            end_datetime=best_time + timedelta(minutes=duration_minutes),
            location=location,
            virtual_meeting_url=virtual_meeting_url,
            organizer_id=interviewer_id,
            participant_ids=[volunteer.user_id],
            opportunity_id=opportunity.id,
            application_id=application_id,
            metadata={
                "volunteer_name": volunteer.full_name,
                "opportunity_title": opportunity.title,
                "interview_type": "standard",
            },
        )

        # Create the event
        event = self.create_event(session, event_data, interviewer_id)

        # Update application with interview details
        application.interview_date = best_time
        application.interview_notes = notes
        application.status = "interview_scheduled"
        application.updated_at = datetime.now(timezone.utc)

        session.add(application)
        session.commit()

        return event

    def _find_best_time_slot(
        self,
        session: Session,
        proposed_times: List[datetime],
        duration_minutes: int,
        participant_ids: List[int],
    ) -> Optional[datetime]:
        """Find the best available time slot from proposed times"""

        for proposed_time in proposed_times:
            end_time = proposed_time + timedelta(minutes=duration_minutes)

            # Check for conflicts
            conflicts = self._check_scheduling_conflicts(
                session, proposed_time, end_time, participant_ids
            )

            # Only consider business hours conflicts as warnings
            serious_conflicts = [c for c in conflicts if c["type"] != "business_hours"]

            if not serious_conflicts:
                return proposed_time

        return None

    def schedule_orientation(
        self,
        session: Session,
        opportunity_id: int,
        organizer_id: int,
        start_time: datetime,
        volunteer_ids: List[int],
        location: str = "",
        virtual_meeting_url: str = "",
    ) -> CalendarEvent:
        """Schedule orientation session for new volunteers"""

        opportunity = session.get(Opportunity, opportunity_id)
        if not opportunity:
            raise ValueError("Opportunity not found")

        # Get volunteer names for the event
        volunteers = session.exec(
            select(Volunteer).where(Volunteer.user_id.in_(volunteer_ids))
        ).all()

        volunteer_names = [v.full_name for v in volunteers]

        duration = self.default_durations[EventType.ORIENTATION]

        event_data = CalendarEvent(
            title=f"Orientation: {opportunity.title}",
            description=f"Orientation session for new volunteers\n\nVolunteers: {', '.join(volunteer_names)}\n\nOpportunity: {opportunity.title}",
            event_type=EventType.ORIENTATION,
            start_datetime=start_time,
            end_datetime=start_time + timedelta(minutes=duration),
            location=location,
            virtual_meeting_url=virtual_meeting_url,
            organizer_id=organizer_id,
            participant_ids=volunteer_ids,
            opportunity_id=opportunity_id,
            metadata={
                "volunteer_count": len(volunteer_ids),
                "opportunity_title": opportunity.title,
                "session_type": "orientation",
            },
        )

        return self.create_event(session, event_data, organizer_id)

    def schedule_recurring_volunteer_sessions(
        self,
        session: Session,
        opportunity_id: int,
        organizer_id: int,
        start_date: date,
        end_date: date,
        session_times: List[
            Dict[str, Any]
        ],  # [{"day": 1, "start_time": "09:00", "duration": 240}]
        volunteer_ids: List[int],
        location: str = "",
        virtual_meeting_url: str = "",
    ) -> List[CalendarEvent]:
        """Schedule recurring volunteer sessions"""

        opportunity = session.get(Opportunity, opportunity_id)
        if not opportunity:
            raise ValueError("Opportunity not found")

        events = []
        current_date = start_date

        while current_date <= end_date:
            for session_time in session_times:
                session_day = session_time["day"]  # 0=Monday, 6=Sunday

                if current_date.weekday() == session_day:
                    # Parse start time
                    start_time_str = session_time["start_time"]
                    start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()

                    # Create datetime
                    session_datetime = datetime.combine(current_date, start_time_obj)
                    duration = session_time.get("duration", 240)  # Default 4 hours

                    event_data = CalendarEvent(
                        title=f"Volunteer Session: {opportunity.title}",
                        description=f"Regular volunteer session\n\nOpportunity: {opportunity.title}",
                        event_type=EventType.VOLUNTEER_SESSION,
                        start_datetime=session_datetime,
                        end_datetime=session_datetime + timedelta(minutes=duration),
                        location=location,
                        virtual_meeting_url=virtual_meeting_url,
                        organizer_id=organizer_id,
                        participant_ids=volunteer_ids,
                        opportunity_id=opportunity_id,
                        recurrence_type=RecurrenceType.WEEKLY,
                        metadata={
                            "session_type": "regular_volunteer_session",
                            "opportunity_title": opportunity.title,
                            "session_day": session_day,
                        },
                    )

                    try:
                        event = self.create_event(session, event_data, organizer_id)
                        events.append(event)
                    except ValueError as e:
                        logger.warning(
                            f"Could not schedule session on {current_date}: {e}"
                        )

            current_date += timedelta(days=1)

        return events

    def get_user_calendar(
        self,
        session: Session,
        user_id: int,
        start_date: date,
        end_date: date,
        event_types: Optional[List[EventType]] = None,
    ) -> List[Dict[str, Any]]:
        """Get user's calendar events for a date range"""

        from models import CalendarEvent

        # Build query for user's calendar events in date range
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        query = select(CalendarEvent).where(
            and_(
                CalendarEvent.user_id == user_id,
                CalendarEvent.start_datetime >= start_datetime,
                CalendarEvent.start_datetime <= end_datetime,
            )
        )

        # Filter by event types if specified
        if event_types:
            query = query.where(
                CalendarEvent.event_type.in_([et.value for et in event_types])
            )

        # Order by start time
        query = query.order_by(CalendarEvent.start_datetime)

        events = session.exec(query).all()

        # Convert to response format
        return [
            {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type,
                "start_datetime": event.start_datetime.isoformat(),
                "end_datetime": event.end_datetime.isoformat(),
                "status": event.status,
                "location": event.location,
                "virtual_meeting_url": event.virtual_meeting_url,
                "organizer_id": event.organizer_id,
                "participants": event.participant_ids or [],
                "opportunity_id": event.opportunity_id,
                "reminder_minutes": event.reminder_minutes,
                "metadata": event.metadata or {},
            }
            for event in events
        ]

    def get_availability_slots(
        self,
        session: Session,
        user_ids: List[int],
        start_date: date,
        end_date: date,
        duration_minutes: int = 60,
        buffer_minutes: int = 15,
    ) -> List[Dict[str, Any]]:
        """Find available time slots for multiple users"""

        available_slots = []
        current_date = start_date

        while current_date <= end_date:
            # Only check business days
            if current_date.weekday() < 5:
                # Check business hours in 30-minute increments
                current_time = datetime.combine(
                    current_date, self.business_hours["start"]
                )
                end_of_day = datetime.combine(current_date, self.business_hours["end"])

                while current_time + timedelta(minutes=duration_minutes) <= end_of_day:
                    # Check if this slot is available for all users
                    slot_end = current_time + timedelta(minutes=duration_minutes)

                    conflicts = self._check_scheduling_conflicts(
                        session, current_time, slot_end, user_ids
                    )

                    # Only consider non-business-hour conflicts as blocking
                    blocking_conflicts = [
                        c for c in conflicts if c["type"] != "business_hours"
                    ]

                    if not blocking_conflicts:
                        available_slots.append(
                            {
                                "start_time": current_time.isoformat(),
                                "end_time": slot_end.isoformat(),
                                "duration_minutes": duration_minutes,
                                "available_for": user_ids,
                                "quality_score": self._calculate_slot_quality(
                                    current_time
                                ),
                            }
                        )

                    current_time += timedelta(minutes=30)  # 30-minute increments

            current_date += timedelta(days=1)

        # Sort by quality score (prefer mid-morning and mid-afternoon slots)
        available_slots.sort(key=lambda x: x["quality_score"], reverse=True)

        return available_slots[:20]  # Return top 20 slots

    def _calculate_slot_quality(self, slot_time: datetime) -> float:
        """Calculate quality score for a time slot (0-1, higher is better)"""

        hour = slot_time.hour

        # Prefer mid-morning (10-11 AM) and mid-afternoon (2-3 PM)
        if hour in [10, 14]:
            return 1.0
        elif hour in [9, 11, 13, 15]:
            return 0.8
        elif hour in [8, 12, 16]:
            return 0.6
        else:
            return 0.4

    def _schedule_reminders(self, session: Session, event_data: CalendarEvent):
        """Schedule reminder notifications for an event"""

        for minutes_before in event_data.reminder_minutes:
            reminder_time = event_data.start_datetime - timedelta(
                minutes=minutes_before
            )

            # In a real implementation, this would create reminder tasks
            # For now, just log the reminder scheduling
            logger.info(
                f"Reminder scheduled for {reminder_time} ({minutes_before} min before {event_data.title})"
            )

    def _notify_participants(
        self, session: Session, event_data: CalendarEvent, notification_type: str
    ):
        """Send notifications to event participants"""

        for participant_id in event_data.participant_ids:
            # In a real implementation, this would send email/push notifications
            logger.info(
                f"Notification '{notification_type}' sent to user {participant_id} for event: {event_data.title}"
            )

    def _log_calendar_event(
        self,
        session: Session,
        event_type: str,
        event_id: int,
        user_id: int,
        event_data: Dict[str, Any],
    ):
        """Log calendar events for analytics"""

        try:
            analytics_event = AnalyticsEvent(
                event_type=f"calendar_{event_type}",
                user_id=user_id,
                data={
                    "calendar_event_id": event_id,
                    "event_data": event_data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            session.add(analytics_event)
            session.commit()

        except Exception as e:
            logger.error(f"Error logging calendar event: {e}")

    def reschedule_event(
        self,
        session: Session,
        event_id: int,
        new_start_time: datetime,
        new_end_time: Optional[datetime] = None,
        reason: str = "",
        rescheduled_by: int = None,
    ) -> CalendarEvent:
        """Reschedule an existing event"""

        # In a real implementation, this would update the calendar_events table
        # For now, create a new event data structure

        if not new_end_time:
            # Keep the same duration
            duration = timedelta(hours=1)  # Default duration
            new_end_time = new_start_time + duration

        # Validate new time slot
        conflicts = self._check_scheduling_conflicts(
            session,
            new_start_time,
            new_end_time,
            [],  # Would get participant IDs from existing event
        )

        if conflicts:
            serious_conflicts = [c for c in conflicts if c["type"] != "business_hours"]
            if serious_conflicts:
                raise ValueError(
                    f"Cannot reschedule due to conflicts: {serious_conflicts}"
                )

        # Create updated event (in real implementation, update existing record)
        updated_event = CalendarEvent(
            id=event_id,
            title="Rescheduled Event",  # Would get from existing event
            start_datetime=new_start_time,
            end_datetime=new_end_time,
            status=EventStatus.RESCHEDULED,
            metadata={"reschedule_reason": reason, "rescheduled_by": rescheduled_by},
        )

        # Log the reschedule
        self._log_calendar_event(
            session,
            "event_rescheduled",
            event_id,
            rescheduled_by or 0,
            {"new_start_time": new_start_time.isoformat(), "reason": reason},
        )

        # Notify participants
        self._notify_participants(session, updated_event, "event_rescheduled")

        return updated_event

    def cancel_event(
        self,
        session: Session,
        event_id: int,
        reason: str = "",
        cancelled_by: int = None,
    ) -> bool:
        """Cancel an existing event"""

        # In a real implementation, this would update the calendar_events table

        # Log the cancellation
        self._log_calendar_event(
            session,
            "event_cancelled",
            event_id,
            cancelled_by or 0,
            {"cancellation_reason": reason},
        )

        # Create mock cancelled event for notifications
        cancelled_event = CalendarEvent(
            id=event_id,
            title="Cancelled Event",
            status=EventStatus.CANCELLED,
            metadata={"cancellation_reason": reason, "cancelled_by": cancelled_by},
        )

        # Notify participants
        self._notify_participants(session, cancelled_event, "event_cancelled")

        logger.info(f"Event {event_id} cancelled. Reason: {reason}")
        return True


# Global scheduler instance
calendar_scheduler = CalendarScheduler()
