"""
Organizations Router for Seraaj API
Handles organization-specific operations and dashboard functionality
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, and_
from typing import Annotated, List, Optional
from datetime import datetime

from database import get_session
from models import (
    User,
    Organisation,
    Opportunity,
    Application,
    Review,
    OrganisationRead,
    OrganisationUpdate,
    OpportunityRead,
    ApplicationRead,
)
from routers.auth import get_current_user
from middleware.error_handler import raise_not_found, raise_forbidden

router = APIRouter(prefix="/v1/org", tags=["organizations"])


@router.get("/", response_model=OrganisationRead)
async def get_my_organization(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get current user's organization profile"""
    if current_user.role != "organization":
        raise_forbidden(
            "Only organizations can access organization profiles",
            details={
                "required_role": "organization",
                "current_role": current_user.role,
            },
        )

    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()

    if not organization:
        raise_not_found(
            "Organization profile not found. Please complete your organization profile first.",
            resource_type="organization",
            resource_id=str(current_user.id),
        )

    return OrganisationRead.model_validate(organization)


@router.put("/", response_model=OrganisationRead)
async def update_my_organization(
    organization_update: OrganisationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Update current user's organization profile"""
    if current_user.role != "organization":
        raise_forbidden(
            "Only organizations can update organization profiles",
            details={
                "required_role": "organization",
                "current_role": current_user.role,
            },
        )

    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()

    if not organization:
        raise_not_found(
            "Organization profile not found. Please complete your organization profile first.",
            resource_type="organization",
            resource_id=str(current_user.id),
        )

    # Update the organization
    update_data = organization_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    organization.updated_at = datetime.now(datetime.timezone.utc)
    session.add(organization)
    session.commit()
    session.refresh(organization)

    return OrganisationRead.model_validate(organization)


@router.get("/opportunities", response_model=List[OpportunityRead])
async def get_organization_opportunities(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    state: Optional[str] = Query(None, description="Filter by opportunity state"),
):
    """Get opportunities created by current organization"""
    if current_user.role != "organization":
        raise_forbidden(
            "Only organizations can access their opportunities",
            details={
                "required_role": "organization",
                "current_role": current_user.role,
            },
        )

    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()

    if not organization:
        raise_not_found(
            "Organization profile not found",
            resource_type="organization",
            resource_id=str(current_user.id),
        )

    # Build query for organization's opportunities
    query = select(Opportunity).where(Opportunity.org_id == organization.id)

    # Apply state filter if provided
    if state:
        query = query.where(Opportunity.state == state)

    # Order by creation date (newest first) and apply pagination
    query = query.order_by(Opportunity.created_at.desc()).offset(skip).limit(limit)

    opportunities = session.exec(query).all()
    return [OpportunityRead.model_validate(opp) for opp in opportunities]


@router.get("/applications", response_model=List[ApplicationRead])
async def get_organization_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(
        None, description="Filter by application status"
    ),
    opportunity_id: Optional[int] = Query(
        None, description="Filter by specific opportunity"
    ),
):
    """Get applications received by current organization"""
    if current_user.role != "organization":
        raise_forbidden(
            "Only organizations can access their applications",
            details={
                "required_role": "organization",
                "current_role": current_user.role,
            },
        )

    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()

    if not organization:
        raise_not_found(
            "Organization profile not found",
            resource_type="organization",
            resource_id=str(current_user.id),
        )

    # Build query for applications to organization's opportunities
    query = (
        select(Application)
        .join(Opportunity)
        .where(Opportunity.org_id == organization.id)
    )

    # Apply filters
    if status_filter:
        query = query.where(Application.status == status_filter)

    if opportunity_id:
        query = query.where(Application.opp_id == opportunity_id)

    # Order by creation date (newest first) and apply pagination
    query = query.order_by(Application.created_at.desc()).offset(skip).limit(limit)

    applications = session.exec(query).all()
    return [ApplicationRead.model_validate(app) for app in applications]


@router.get("/dashboard/stats")
async def get_organization_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get dashboard statistics for current organization"""
    if current_user.role != "organization":
        raise_forbidden(
            "Only organizations can access dashboard stats",
            details={
                "required_role": "organization",
                "current_role": current_user.role,
            },
        )

    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()

    if not organization:
        raise_not_found(
            "Organization profile not found",
            resource_type="organization",
            resource_id=str(current_user.id),
        )

    # Get various statistics
    total_opportunities = (
        session.exec(
            select(func.count(Opportunity.id)).where(
                Opportunity.org_id == organization.id
            )
        ).first()
        or 0
    )

    active_opportunities = (
        session.exec(
            select(func.count(Opportunity.id)).where(
                and_(
                    Opportunity.org_id == organization.id, Opportunity.state == "active"
                )
            )
        ).first()
        or 0
    )

    total_applications = (
        session.exec(
            select(func.count(Application.id))
            .join(Opportunity)
            .where(Opportunity.org_id == organization.id)
        ).first()
        or 0
    )

    pending_applications = (
        session.exec(
            select(func.count(Application.id))
            .join(Opportunity)
            .where(
                and_(
                    Opportunity.org_id == organization.id,
                    Application.status.in_(["submitted", "under_review"]),
                )
            )
        ).first()
        or 0
    )

    accepted_applications = (
        session.exec(
            select(func.count(Application.id))
            .join(Opportunity)
            .where(
                and_(
                    Opportunity.org_id == organization.id,
                    Application.status == "accepted",
                )
            )
        ).first()
        or 0
    )

    # Get recent applications (last 5)
    recent_applications = session.exec(
        select(Application)
        .join(Opportunity)
        .where(Opportunity.org_id == organization.id)
        .order_by(Application.created_at.desc())
        .limit(5)
    ).all()

    return {
        "organization_id": organization.id,
        "organization_name": organization.name,
        "total_opportunities": total_opportunities,
        "active_opportunities": active_opportunities,
        "total_applications": total_applications,
        "pending_applications": pending_applications,
        "accepted_applications": accepted_applications,
        "recent_applications": [
            {
                "id": app.id,
                "opportunity_id": app.opp_id,
                "volunteer_id": app.vol_id,
                "status": app.status,
                "created_at": app.created_at.isoformat(),
                "match_score": app.match_score,
            }
            for app in recent_applications
        ],
    }


@router.get("/reviews", response_model=List[dict])
async def get_organization_reviews(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Get reviews for current organization"""
    if current_user.role != "organization":
        raise_forbidden(
            "Only organizations can access their reviews",
            details={
                "required_role": "organization",
                "current_role": current_user.role,
            },
        )

    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()

    if not organization:
        raise_not_found(
            "Organization profile not found",
            resource_type="organization",
            resource_id=str(current_user.id),
        )

    # Get reviews for this organization
    query = (
        select(Review)
        .where(Review.reviewed_organization_id == organization.id)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    reviews = session.exec(query).all()

    return [
        {
            "id": review.id,
            "rating": review.rating,
            "title": review.title,
            "content": review.content,
            "reviewer_type": review.review_type,
            "created_at": review.created_at.isoformat(),
            "communication_rating": review.communication_rating,
            "professionalism_rating": review.professionalism_rating,
        }
        for review in reviews
    ]
