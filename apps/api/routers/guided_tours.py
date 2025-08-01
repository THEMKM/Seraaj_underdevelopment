"""
Guided Tours Router for Seraaj
Interactive tutorials and onboarding flows
"""

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing import Annotated, Dict, Any, List, Optional
from datetime import datetime

from database import get_session
from models import User
from models.guided_tour import (
    GuidedTour,
    TourStep,
    UserTourProgress,
    TourTemplate,
    TourType,
    TourStatus,
    TourUserRole,
)
from routers.auth import get_current_user  # get_current_user_optional
from services.guided_tour_service import get_guided_tour_service
from utils.response_formatter import success_with_data, JSONResponse
import logging

router = APIRouter(prefix="/v1/guided-tours", tags=["guided-tours"])
logger = logging.getLogger(__name__)


# Pydantic models for request/response
from pydantic import BaseModel, Field


class TourFeedbackRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    feedback: str
    step_id: Optional[str] = None


class TourStepAdvanceRequest(BaseModel):
    action: str = "next"  # next, prev, skip, complete
    step_number: int
    time_spent: Optional[int] = None  # seconds spent on step


class CreateTourRequest(BaseModel):
    title: str
    description: str
    tour_type: TourType
    target_role: TourUserRole = TourUserRole.ALL
    entry_url: str = "/"
    estimated_duration_minutes: int = 5
    is_mandatory: bool = False
    allow_skip: bool = True
    steps: List[Dict[str, Any]]


@router.get("/available")
async def get_available_tours(
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    include_completed: bool = Query(False, description="Include completed tours"),
    current_url: Optional[str] = Query(
        None, description="Current page URL for context"
    ),
):
    """Get tours available for the current user"""

    try:
        service = get_guided_tour_service(session)

        tours = await service.get_available_tours(
            user_id=user.id,
            user_role=TourUserRole(user.role),
            current_url=current_url,
            include_completed=include_completed,
        )

        return success_with_data(
            {"tours": tours, "total": len(tours)}, "Available tours retrieved"
        )

    except Exception as e:
        logger.error(f"Error getting available tours for user {user.id}: {e}")
        return JSONResponse("Failed to get available tours", 500)


@router.post("/start/{tour_id}")
async def start_tour(
    tour_id: str,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Start a guided tour"""

    try:
        service = get_guided_tour_service(session)

        result = await service.start_tour(user.id, tour_id)

        return success_with_data(result, "Tour started successfully")

    except ValueError as e:
        return JSONResponse(str(e), 404)
    except Exception as e:
        logger.error(f"Error starting tour {tour_id} for user {user.id}: {e}")
        return JSONResponse("Failed to start tour", 500)


@router.get("/{tour_id}/step/{step_number}")
async def get_tour_step(
    tour_id: str,
    step_number: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get a specific tour step"""

    try:
        service = get_guided_tour_service(session)

        step = await service.get_tour_step(user.id, tour_id, step_number)

        return success_with_data(step, "Tour step retrieved")

    except ValueError as e:
        return JSONResponse(str(e), 404)
    except Exception as e:
        logger.error(f"Error getting tour step: {e}")
        return JSONResponse("Failed to get tour step", 500)


@router.post("/{tour_id}/advance")
async def advance_tour_step(
    tour_id: str,
    advance_request: TourStepAdvanceRequest,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Advance to next tour step"""

    try:
        service = get_guided_tour_service(session)

        result = await service.advance_tour_step(
            user_id=user.id,
            tour_id=tour_id,
            step_number=advance_request.step_number,
            action=advance_request.action,
        )

        return success_with_data(result, "Tour step advanced")

    except ValueError as e:
        return JSONResponse(str(e), 404)
    except Exception as e:
        logger.error(f"Error advancing tour step: {e}")
        return JSONResponse("Failed to advance tour step", 500)


@router.post("/{tour_id}/skip")
async def skip_tour(
    tour_id: str,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Skip/dismiss a tour"""

    try:
        service = get_guided_tour_service(session)

        success = await service.skip_tour(user.id, tour_id)

        if success:
            return success_with_data({"skipped": True}, "Tour skipped successfully")
        else:
            return JSONResponse("Tour not found", 404)

    except Exception as e:
        logger.error(f"Error skipping tour {tour_id}: {e}")
        return JSONResponse("Failed to skip tour", 500)


@router.post("/{tour_id}/feedback")
async def submit_tour_feedback(
    tour_id: str,
    feedback_request: TourFeedbackRequest,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Submit feedback for a tour"""

    try:
        service = get_guided_tour_service(session)

        success = await service.submit_tour_feedback(
            user_id=user.id,
            tour_id=tour_id,
            rating=feedback_request.rating,
            feedback=feedback_request.feedback,
            step_id=feedback_request.step_id,
        )

        if success:
            return success_with_data(
                {"submitted": True}, "Feedback submitted successfully"
            )
        else:
            return JSONResponse("Tour not found", 404)

    except Exception as e:
        logger.error(f"Error submitting tour feedback: {e}")
        return JSONResponse("Failed to submit feedback", 500)


@router.get("/{tour_id}/progress")
async def get_tour_progress(
    tour_id: str,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get user's progress for a specific tour"""

    try:
        from sqlmodel import select, and_

        # Get tour
        tour = session.exec(
            select(GuidedTour).where(GuidedTour.tour_id == tour_id)
        ).first()

        if not tour:
            return JSONResponse("Tour not found", 404)

        # Get user progress
        progress = session.exec(
            select(UserTourProgress).where(
                and_(
                    UserTourProgress.user_id == user.id,
                    UserTourProgress.tour_id == tour.id,
                )
            )
        ).first()

        if not progress:
            return success_with_data(
                {
                    "status": TourStatus.NOT_STARTED,
                    "current_step": None,
                    "completion_percentage": 0,
                    "completed_steps": [],
                    "skipped_steps": [],
                },
                "Tour progress retrieved",
            )

        # Calculate completion percentage
        total_steps = len(
            session.exec(select(TourStep).where(TourStep.tour_id == tour.id)).all()
        )

        completion_percentage = (
            (len(progress.completed_steps) / total_steps * 100)
            if total_steps > 0
            else 0
        )

        progress_data = {
            "status": progress.status,
            "current_step": progress.current_step,
            "completion_percentage": round(completion_percentage, 2),
            "completed_steps": progress.completed_steps,
            "skipped_steps": progress.skipped_steps,
            "started_at": (
                progress.started_at.isoformat() if progress.started_at else None
            ),
            "completed_at": (
                progress.completed_at.isoformat() if progress.completed_at else None
            ),
            "total_time_spent": progress.total_time_spent,
            "rating": progress.rating,
            "feedback": progress.feedback,
        }

        return success_with_data(progress_data, "Tour progress retrieved")

    except Exception as e:
        logger.error(f"Error getting tour progress: {e}")
        return JSONResponse("Failed to get tour progress", 500)


@router.get("/templates")
async def get_tour_templates(
    session: Annotated[Session, Depends(get_session)],
    category: Optional[str] = Query(None, description="Filter by category"),
    target_role: Optional[TourUserRole] = Query(
        None, description="Filter by target role"
    ),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Get available tour templates"""

    try:
        from sqlmodel import select, and_

        query = select(TourTemplate)
        conditions = []

        if category:
            conditions.append(TourTemplate.category == category)

        if target_role:
            from sqlmodel import or_

            conditions.append(
                or_(
                    TourTemplate.target_role == target_role,
                    TourTemplate.target_role == TourUserRole.ALL,
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        templates = session.exec(
            query.order_by(
                TourTemplate.is_featured.desc(), TourTemplate.usage_count.desc()
            )
        ).all()

        template_data = []
        for template in templates:
            template_data.append(
                {
                    "template_id": template.template_id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "target_role": template.target_role,
                    "usage_count": template.usage_count,
                    "is_featured": template.is_featured,
                    "created_at": template.created_at.isoformat(),
                }
            )

        return success_with_data(
            {"templates": template_data, "total": len(template_data)},
            "Tour templates retrieved",
        )

    except Exception as e:
        logger.error(f"Error getting tour templates: {e}")
        return JSONResponse("Failed to get tour templates", 500)


@router.post("/create")
async def create_tour(
    tour_request: CreateTourRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new guided tour (admin only)"""

    # Check admin permissions
    if current_user.role != "admin":
        return JSONResponse("Admin access required", 403)

    try:
        # Create tour
        tour = GuidedTour(
            title=tour_request.title,
            description=tour_request.description,
            tour_type=tour_request.tour_type,
            target_role=tour_request.target_role,
            entry_url=tour_request.entry_url,
            estimated_duration_minutes=tour_request.estimated_duration_minutes,
            is_mandatory=tour_request.is_mandatory,
            allow_skip=tour_request.allow_skip,
            created_by=current_user.id,
        )

        session.add(tour)
        session.commit()
        session.refresh(tour)

        # Create steps
        for step_data in tour_request.steps:
            from models.guided_tour import StepType

            step = TourStep(
                tour_id=tour.id,
                step_number=step_data["step_number"],
                step_type=StepType(step_data["step_type"]),
                title=step_data["title"],
                content=step_data["content"],
                target_selector=step_data.get("target_selector"),
                target_url=step_data.get("target_url"),
                position=step_data.get("position", "bottom"),
                primary_button_text=step_data.get("primary_button_text", "Next"),
                secondary_button_text=step_data.get("secondary_button_text", "Skip"),
            )
            session.add(step)

        session.commit()

        return success_with_data(
            {"tour_id": tour.tour_id, "created": True}, "Tour created successfully"
        )

    except Exception as e:
        logger.error(f"Error creating tour: {e}")
        session.rollback()
        return JSONResponse("Failed to create tour", 500)


@router.get("/{tour_id}/analytics")
async def get_tour_analytics(
    tour_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    days: int = Query(30, description="Number of days to analyze", le=90),
):
    """Get analytics for a specific tour (admin only)"""

    # Check admin permissions
    if current_user.role != "admin":
        return JSONResponse("Admin access required", 403)

    try:
        service = get_guided_tour_service(session)

        analytics = await service.get_tour_analytics(tour_id, days)

        return success_with_data(analytics, "Tour analytics retrieved")

    except ValueError as e:
        return JSONResponse(str(e), 404)
    except Exception as e:
        logger.error(f"Error getting tour analytics: {e}")
        return JSONResponse("Failed to get tour analytics", 500)


@router.get("/analytics/overview")
async def get_tours_overview(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get overview analytics for all tours (admin only)"""

    # Check admin permissions
    if current_user.role != "admin":
        return JSONResponse("Admin access required", 403)

    try:
        from sqlmodel import select

        # Get tour statistics
        tours = session.exec(
            select(GuidedTour).where(GuidedTour.is_active == True)
        ).all()

        # Get progress statistics
        all_progress = session.exec(select(UserTourProgress)).all()

        total_tours = len(tours)
        total_users_engaged = len(set(p.user_id for p in all_progress))
        total_completions = len(
            [p for p in all_progress if p.status == TourStatus.COMPLETED]
        )
        total_skips = len([p for p in all_progress if p.status == TourStatus.SKIPPED])

        # Calculate overall completion rate
        total_attempts = len(all_progress)
        overall_completion_rate = (
            (total_completions / total_attempts * 100) if total_attempts > 0 else 0
        )

        # Get top performing tours
        tour_performance = []
        for tour in tours:
            tour_progress = [p for p in all_progress if p.tour_id == tour.id]
            completions = len(
                [p for p in tour_progress if p.status == TourStatus.COMPLETED]
            )
            attempts = len(tour_progress)
            completion_rate = (completions / attempts * 100) if attempts > 0 else 0

            tour_performance.append(
                {
                    "tour_id": tour.tour_id,
                    "title": tour.title,
                    "attempts": attempts,
                    "completions": completions,
                    "completion_rate": round(completion_rate, 2),
                }
            )

        # Sort by completion rate
        tour_performance.sort(key=lambda x: x["completion_rate"], reverse=True)

        overview = {
            "summary": {
                "total_tours": total_tours,
                "total_users_engaged": total_users_engaged,
                "total_completions": total_completions,
                "total_skips": total_skips,
                "overall_completion_rate": round(overall_completion_rate, 2),
            },
            "top_performing_tours": tour_performance[:5],
            "tour_types": {
                tour_type.value: len([t for t in tours if t.tour_type == tour_type])
                for tour_type in TourType
            },
        }

        return success_with_data(overview, "Tours overview retrieved")

    except Exception as e:
        logger.error(f"Error getting tours overview: {e}")
        return JSONResponse("Failed to get tours overview", 500)


@router.get("/my-progress")
async def get_my_tour_progress(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get current user's progress across all tours"""

    try:
        from sqlmodel import select

        progress_records = session.exec(
            select(UserTourProgress).where(UserTourProgress.user_id == user.id)
        ).all()

        progress_data = []
        for progress in progress_records:
            tour = session.get(GuidedTour, progress.tour_id)
            if tour:
                # Calculate completion percentage
                total_steps = len(
                    session.exec(
                        select(TourStep).where(TourStep.tour_id == tour.id)
                    ).all()
                )

                completion_percentage = (
                    (len(progress.completed_steps) / total_steps * 100)
                    if total_steps > 0
                    else 0
                )

                progress_data.append(
                    {
                        "tour_id": tour.tour_id,
                        "tour_title": tour.title,
                        "tour_type": tour.tour_type,
                        "status": progress.status,
                        "current_step": progress.current_step,
                        "completion_percentage": round(completion_percentage, 2),
                        "started_at": (
                            progress.started_at.isoformat()
                            if progress.started_at
                            else None
                        ),
                        "completed_at": (
                            progress.completed_at.isoformat()
                            if progress.completed_at
                            else None
                        ),
                        "rating": progress.rating,
                    }
                )

        return success_with_data(
            {
                "progress": progress_data,
                "total_tours": len(progress_data),
                "completed_tours": len(
                    [p for p in progress_data if p["status"] == TourStatus.COMPLETED]
                ),
                "in_progress_tours": len(
                    [p for p in progress_data if p["status"] == TourStatus.IN_PROGRESS]
                ),
            },
            "User tour progress retrieved",
        )

    except Exception as e:
        logger.error(f"Error getting user tour progress: {e}")
        return JSONResponse("Failed to get tour progress", 500)


@router.post("/reset/{tour_id}")
async def reset_tour_progress(
    tour_id: str,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Reset tour progress to start over"""

    try:
        from sqlmodel import select, and_

        # Get tour
        tour = session.exec(
            select(GuidedTour).where(GuidedTour.tour_id == tour_id)
        ).first()

        if not tour:
            return JSONResponse("Tour not found", 404)

        # Get existing progress
        progress = session.exec(
            select(UserTourProgress).where(
                and_(
                    UserTourProgress.user_id == user.id,
                    UserTourProgress.tour_id == tour.id,
                )
            )
        ).first()

        if progress:
            # Reset progress
            progress.status = TourStatus.NOT_STARTED
            progress.current_step = None
            progress.completed_steps = []
            progress.skipped_steps = []
            progress.started_at = None
            progress.completed_at = None
            progress.total_time_spent = 0
            progress.rating = None
            progress.feedback = None
            progress.updated_at = datetime.now(datetime.timezone.utc)

            session.add(progress)
            session.commit()

        return success_with_data({"reset": True}, "Tour progress reset successfully")

    except Exception as e:
        logger.error(f"Error resetting tour progress: {e}")
        session.rollback()
        return JSONResponse("Failed to reset tour progress", 500)
