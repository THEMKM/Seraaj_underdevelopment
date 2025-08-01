from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Annotated, List, Dict, Optional
import logging
from pydantic import BaseModel, Field

from database import get_session
from models import User, UserRole, Volunteer, Organisation, Opportunity, Application
from routers.auth import get_current_user
from ml.matching_engine import matching_engine


# Response Models for consistent API responses
class OpportunityScore(BaseModel):
    """Simplified opportunity match used by the frontend."""

    id: int
    title: str
    score: float = Field(..., ge=0.0, le=100.0)


class VolunteerMatch(BaseModel):
    """Volunteer match for opportunities"""

    volunteer_id: int
    first_name: str
    last_name: str
    skills: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    match_score: float = Field(..., ge=0.0, le=100.0)
    compatibility_factors: Dict[str, float] = Field(default_factory=dict)
    skills_match: List[str] = Field(default_factory=list)
    profile_completion: float = Field(default=0.0, ge=0.0, le=100.0)


router = APIRouter(prefix="/v1/match", tags=["matching"])
logger = logging.getLogger(__name__)


@router.get("/opportunities", response_model=List[OpportunityScore])
def get_volunteer_matches(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    limit: int = Query(10, ge=1, le=50),
):
    """Return top opportunity matches using rule-based scoring."""
    if current_user.role != UserRole.VOLUNTEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can get opportunity matches",
        )

    # Get volunteer profile
    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer profile not found"
        )

    try:
        matches = matching_engine.rule_based_opportunities(
            session=session, volunteer_id=volunteer.id, limit=limit
        )

        return matches

    except Exception as e:
        logger.error(f"Error getting volunteer matches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating matches",
        )


@router.get("/volunteers/{opportunity_id}", response_model=List[VolunteerMatch])
async def get_opportunity_matches(
    opportunity_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    limit: int = Query(10, ge=1, le=50),
):
    """Get ML-powered volunteer matches for an opportunity"""
    if current_user.role != UserRole.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can get volunteer matches",
        )

    # Verify opportunity exists and belongs to current user's organization
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )

    # Verify ownership
    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()

    if not organization or opportunity.org_id != organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to get matches for this opportunity",
        )

    try:
        # Use ML matching engine
        matches = await matching_engine.find_matches(
            session=session, opportunity_id=opportunity_id, limit=limit
        )

        return matches

    except Exception as e:
        logger.error(f"Error getting opportunity matches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating matches",
        )


@router.post("/feedback")
async def record_matching_feedback(
    feedback_data: Dict,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Record user feedback to improve matching algorithm"""

    volunteer_id = feedback_data.get("volunteer_id")
    opportunity_id = feedback_data.get("opportunity_id")
    feedback_type = feedback_data.get(
        "feedback_type"
    )  # 'applied', 'rejected', 'accepted', 'completed'
    feedback_score = feedback_data.get("feedback_score")  # Optional 0-1 score

    if not all([volunteer_id, opportunity_id, feedback_type]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: volunteer_id, opportunity_id, feedback_type",
        )

    # Validate feedback type
    valid_feedback_types = [
        "applied",
        "rejected",
        "accepted",
        "completed",
        "viewed",
        "dismissed",
    ]
    if feedback_type not in valid_feedback_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback_type. Must be one of: {valid_feedback_types}",
        )

    # Verify user has permission to provide this feedback
    if current_user.role == UserRole.VOLUNTEER:
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()
        if not volunteer or volunteer.id != volunteer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to provide feedback for this volunteer",
            )

    elif current_user.role == UserRole.ORGANIZATION:
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()
        opportunity = session.get(Opportunity, opportunity_id)
        if not organization or not opportunity or opportunity.org_id != organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to provide feedback for this opportunity",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role for providing feedback",
        )

    try:
        # Record feedback in matching engine
        await matching_engine.learn_from_feedback(
            session=session,
            volunteer_id=volunteer_id,
            opportunity_id=opportunity_id,
            feedback_type=feedback_type,
            feedback_score=feedback_score,
        )

        return {"message": "Feedback recorded successfully"}

    except Exception as e:
        logger.error(f"Error recording matching feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error recording feedback",
        )


@router.get("/algorithm/weights")
async def get_algorithm_weights(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get current matching algorithm feature weights (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return {
        "feature_weights": matching_engine.get_feature_weights(),
        "description": {
            "skill_match": "How well volunteer skills match opportunity requirements",
            "location_match": "Geographic proximity or remote work compatibility",
            "availability_match": "Time availability alignment",
            "experience_match": "Experience level compatibility",
            "cause_match": "Alignment of volunteer interests with opportunity causes",
            "time_commitment_match": "Matching of time commitment expectations",
            "rating_boost": "Boost based on volunteer rating",
        },
    }


@router.put("/algorithm/weights")
async def update_algorithm_weights(
    new_weights: Dict[str, float],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update matching algorithm feature weights (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    try:
        matching_engine.update_feature_weights(new_weights)

        return {
            "message": "Algorithm weights updated successfully",
            "updated_weights": matching_engine.get_feature_weights(),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating algorithm weights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating weights",
        )


@router.get("/stats")
async def get_matching_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get matching system statistics"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    try:
        # Get basic matching stats
        total_volunteers = session.exec(select(func.count(Volunteer.id))).first()
        active_volunteers = session.exec(
            select(func.count(Volunteer.id)).where(Volunteer.available == True)
        ).first()

        total_opportunities = session.exec(select(func.count(Opportunity.id))).first()
        active_opportunities = session.exec(
            select(func.count(Opportunity.id)).where(Opportunity.state == "active")
        ).first()

        # Get application success rates
        total_applications = session.exec(select(func.count(Application.id))).first()
        successful_applications = session.exec(
            select(func.count(Application.id)).where(
                Application.status.in_(["accepted", "completed"])
            )
        ).first()

        success_rate = (
            (successful_applications / total_applications * 100)
            if total_applications > 0
            else 0
        )

        return {
            "volunteers": {
                "total": total_volunteers,
                "active": active_volunteers,
                "availability_rate": (
                    (active_volunteers / total_volunteers * 100)
                    if total_volunteers > 0
                    else 0
                ),
            },
            "opportunities": {
                "total": total_opportunities,
                "active": active_opportunities,
            },
            "matching_performance": {
                "total_applications": total_applications,
                "successful_applications": successful_applications,
                "success_rate_percent": round(success_rate, 2),
            },
            "algorithm_weights": matching_engine.get_feature_weights(),
        }

    except Exception as e:
        logger.error(f"Error getting matching statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics",
        )


from sqlmodel import func
