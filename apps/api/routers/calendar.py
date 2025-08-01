from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Annotated, List, Optional, Dict, Any
from datetime import datetime, date

from database import get_session
from models import User, Organisation, Opportunity, Application
from routers.auth import get_current_user
from calendar_module.scheduler import calendar_scheduler, CalendarEvent, EventType

router = APIRouter(prefix="/v1/calendar", tags=["calendar"])


@router.post("/events")
async def create_calendar_event(
    event_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new calendar event"""

    try:
        # Parse event data
        title = event_data.get("title", "")
        description = event_data.get("description", "")
        event_type_str = event_data.get("event_type", "meeting")
        start_datetime_str = event_data.get("start_datetime")
        end_datetime_str = event_data.get("end_datetime")
        location = event_data.get("location", "")
        virtual_meeting_url = event_data.get("virtual_meeting_url")
        participant_ids = event_data.get("participant_ids", [])
        opportunity_id = event_data.get("opportunity_id")
        application_id = event_data.get("application_id")

        if not all([title, start_datetime_str, end_datetime_str]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="title, start_datetime, and end_datetime are required",
            )

        # Parse datetime strings
        start_datetime = datetime.fromisoformat(
            start_datetime_str.replace("Z", "+00:00")
        )
        end_datetime = datetime.fromisoformat(end_datetime_str.replace("Z", "+00:00"))

        # Parse event type
        try:
            event_type = EventType(event_type_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {event_type_str}",
            )

        # Create event object
        calendar_event = CalendarEvent(
            title=title,
            description=description,
            event_type=event_type,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=location,
            virtual_meeting_url=virtual_meeting_url,
            organizer_id=current_user.id,
            participant_ids=participant_ids,
            opportunity_id=opportunity_id,
            application_id=application_id,
        )

        # Create the event
        created_event = calendar_scheduler.create_event(
            session=session, event_data=calendar_event, created_by=current_user.id
        )

        return {
            "id": created_event.id,
            "title": created_event.title,
            "event_type": created_event.event_type.value,
            "start_datetime": created_event.start_datetime.isoformat(),
            "end_datetime": created_event.end_datetime.isoformat(),
            "status": created_event.status.value,
            "participant_count": len(created_event.participant_ids),
            "created_at": created_event.created_at.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating event: {str(e)}",
        )


@router.post("/interviews/schedule")
async def schedule_interview(
    interview_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Schedule an interview for an application"""

    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can schedule interviews",
        )

    application_id = interview_data.get("application_id")
    proposed_times_str = interview_data.get("proposed_times", [])
    duration_minutes = interview_data.get("duration_minutes", 45)
    location = interview_data.get("location", "")
    virtual_meeting_url = interview_data.get("virtual_meeting_url", "")
    notes = interview_data.get("notes", "")

    if not application_id or not proposed_times_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="application_id and proposed_times are required",
        )

    # Parse proposed times
    try:
        proposed_times = [
            datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            for time_str in proposed_times_str
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {e}",
        )

    # Verify application access
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    if current_user.role == "organization":
        # Verify organization owns the opportunity
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization profile not found",
            )

        opportunity = session.get(Opportunity, application.opp_id)
        if not opportunity or opportunity.org_id != organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to schedule interviews for this application",
            )

    try:
        # Schedule the interview
        interview_event = calendar_scheduler.schedule_interview(
            session=session,
            application_id=application_id,
            interviewer_id=current_user.id,
            proposed_times=proposed_times,
            duration_minutes=duration_minutes,
            location=location,
            virtual_meeting_url=virtual_meeting_url,
            notes=notes,
        )

        return {
            "message": "Interview scheduled successfully",
            "event_id": interview_event.id,
            "scheduled_time": interview_event.start_datetime.isoformat(),
            "duration_minutes": duration_minutes,
            "location": location,
            "virtual_meeting_url": virtual_meeting_url,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling interview: {str(e)}",
        )


@router.post("/orientation/schedule")
async def schedule_orientation(
    orientation_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Schedule orientation session for volunteers"""

    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can schedule orientations",
        )

    opportunity_id = orientation_data.get("opportunity_id")
    start_time_str = orientation_data.get("start_time")
    volunteer_ids = orientation_data.get("volunteer_ids", [])
    location = orientation_data.get("location", "")
    virtual_meeting_url = orientation_data.get("virtual_meeting_url", "")

    if not all([opportunity_id, start_time_str, volunteer_ids]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="opportunity_id, start_time, and volunteer_ids are required",
        )

    # Parse start time
    try:
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {e}",
        )

    # Verify opportunity access
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )

    if current_user.role == "organization":
        # Verify organization owns the opportunity
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()

        if not organization or opportunity.org_id != organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to schedule orientations for this opportunity",
            )

    try:
        # Schedule the orientation
        orientation_event = calendar_scheduler.schedule_orientation(
            session=session,
            opportunity_id=opportunity_id,
            organizer_id=current_user.id,
            start_time=start_time,
            volunteer_ids=volunteer_ids,
            location=location,
            virtual_meeting_url=virtual_meeting_url,
        )

        return {
            "message": "Orientation scheduled successfully",
            "event_id": orientation_event.id,
            "scheduled_time": orientation_event.start_datetime.isoformat(),
            "duration_hours": 2,
            "volunteer_count": len(volunteer_ids),
            "location": location,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling orientation: {str(e)}",
        )


@router.post("/sessions/recurring")
async def schedule_recurring_sessions(
    session_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Schedule recurring volunteer sessions"""

    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can schedule recurring sessions",
        )

    opportunity_id = session_data.get("opportunity_id")
    start_date_str = session_data.get("start_date")
    end_date_str = session_data.get("end_date")
    session_times = session_data.get("session_times", [])
    volunteer_ids = session_data.get("volunteer_ids", [])
    location = session_data.get("location", "")
    virtual_meeting_url = session_data.get("virtual_meeting_url", "")

    if not all([opportunity_id, start_date_str, end_date_str, session_times]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="opportunity_id, start_date, end_date, and session_times are required",
        )

    # Parse dates
    try:
        start_date = datetime.fromisoformat(start_date_str).date()
        end_date = datetime.fromisoformat(end_date_str).date()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date format: {e}"
        )

    # Verify opportunity access
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )

    if current_user.role == "organization":
        # Verify organization owns the opportunity
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()

        if not organization or opportunity.org_id != organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to schedule sessions for this opportunity",
            )

    try:
        # Schedule recurring sessions
        created_events = calendar_scheduler.schedule_recurring_volunteer_sessions(
            session=session,
            opportunity_id=opportunity_id,
            organizer_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            session_times=session_times,
            volunteer_ids=volunteer_ids,
            location=location,
            virtual_meeting_url=virtual_meeting_url,
        )

        return {
            "message": "Recurring sessions scheduled successfully",
            "events_created": len(created_events),
            "date_range": f"{start_date} to {end_date}",
            "session_pattern": session_times,
            "volunteer_count": len(volunteer_ids),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling recurring sessions: {str(e)}",
        )


@router.get("/my-calendar")
async def get_my_calendar(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    start_date: str = Query(...),
    end_date: str = Query(...),
    event_types: Optional[List[str]] = Query(None),
):
    """Get current user's calendar events"""

    # Parse dates
    try:
        start_date_obj = datetime.fromisoformat(start_date).date()
        end_date_obj = datetime.fromisoformat(end_date).date()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date format: {e}"
        )

    # Parse event types
    event_type_filters = None
    if event_types:
        try:
            event_type_filters = [EventType(et) for et in event_types]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {e}",
            )

    try:
        # Get user's calendar events
        events = calendar_scheduler.get_user_calendar(
            session=session,
            user_id=current_user.id,
            start_date=start_date_obj,
            end_date=end_date_obj,
            event_types=event_type_filters,
        )

        return {
            "events": events,
            "date_range": f"{start_date_obj} to {end_date_obj}",
            "event_count": len(events),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving calendar: {str(e)}",
        )


@router.get("/availability")
async def get_availability_slots(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    start_date: str = Query(...),
    end_date: str = Query(...),
    participant_ids: Optional[List[int]] = Query(None),
    duration_minutes: int = Query(60),
    buffer_minutes: int = Query(15),
):
    """Get available time slots for scheduling"""

    # Parse dates
    try:
        start_date_obj = datetime.fromisoformat(start_date).date()
        end_date_obj = datetime.fromisoformat(end_date).date()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date format: {e}"
        )

    # Include current user in participant list
    all_participant_ids = [current_user.id]
    if participant_ids:
        all_participant_ids.extend(participant_ids)

    try:
        # Get availability slots
        slots = calendar_scheduler.get_availability_slots(
            session=session,
            user_ids=all_participant_ids,
            start_date=start_date_obj,
            end_date=end_date_obj,
            duration_minutes=duration_minutes,
            buffer_minutes=buffer_minutes,
        )

        return {
            "available_slots": slots,
            "date_range": f"{start_date_obj} to {end_date_obj}",
            "duration_minutes": duration_minutes,
            "participant_count": len(all_participant_ids),
            "slot_count": len(slots),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding availability: {str(e)}",
        )


@router.put("/events/{event_id}/reschedule")
async def reschedule_event(
    event_id: int,
    reschedule_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Reschedule an existing event"""

    new_start_time_str = reschedule_data.get("new_start_time")
    new_end_time_str = reschedule_data.get("new_end_time")
    reason = reschedule_data.get("reason", "")

    if not new_start_time_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="new_start_time is required"
        )

    # Parse new times
    try:
        new_start_time = datetime.fromisoformat(
            new_start_time_str.replace("Z", "+00:00")
        )
        new_end_time = None
        if new_end_time_str:
            new_end_time = datetime.fromisoformat(
                new_end_time_str.replace("Z", "+00:00")
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {e}",
        )

    try:
        # Reschedule the event
        updated_event = calendar_scheduler.reschedule_event(
            session=session,
            event_id=event_id,
            new_start_time=new_start_time,
            new_end_time=new_end_time,
            reason=reason,
            rescheduled_by=current_user.id,
        )

        return {
            "message": "Event rescheduled successfully",
            "event_id": event_id,
            "new_start_time": updated_event.start_datetime.isoformat(),
            "new_end_time": updated_event.end_datetime.isoformat(),
            "reason": reason,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rescheduling event: {str(e)}",
        )


@router.delete("/events/{event_id}")
async def cancel_event(
    event_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    cancellation_data: Optional[Dict[str, Any]] = None,
):
    """Cancel an existing event"""

    reason = ""
    if cancellation_data:
        reason = cancellation_data.get("reason", "")

    try:
        # Cancel the event
        success = calendar_scheduler.cancel_event(
            session=session,
            event_id=event_id,
            reason=reason,
            cancelled_by=current_user.id,
        )

        if success:
            return {
                "message": "Event cancelled successfully",
                "event_id": event_id,
                "reason": reason,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel event",
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling event: {str(e)}",
        )


@router.get("/upcoming")
async def get_upcoming_events(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    days_ahead: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
):
    """Get upcoming events for the current user"""

    start_date = date.today()
    end_date = start_date + timedelta(days=days_ahead)

    try:
        # Get upcoming events
        events = calendar_scheduler.get_user_calendar(
            session=session,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )

        # Sort by start time and limit results
        events.sort(key=lambda x: x["start_datetime"])
        limited_events = events[:limit]

        return {
            "upcoming_events": limited_events,
            "days_ahead": days_ahead,
            "total_events": len(limited_events),
            "period": f"{start_date} to {end_date}",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving upcoming events: {str(e)}",
        )


from datetime import timedelta
