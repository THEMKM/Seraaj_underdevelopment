from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func, and_, or_
from typing import Annotated, List, Optional, Dict
from datetime import datetime, date
import time

from database import get_session
from models import (
    Opportunity, OpportunityCreate, OpportunityRead, OpportunityUpdate,
    User, Organisation, Application
)
from routers.auth import get_current_user, get_current_user_optional
from middleware.error_handler import (
    raise_bad_request, raise_not_found, raise_forbidden, BusinessLogicError
)
from middleware.loading_states import ProgressTracker, async_operation
from utils.validation import validate_opportunity_data
from utils.response_formatter import (
    APIResponse, created_resource, paginated_results, format_api_response
)
from pydantic import BaseModel, Field


# Response Models for consistent API responses
class OpportunityApplicationsResponse(BaseModel):
    """Response for opportunity applications"""
    opportunity_id: int
    applications: List[dict]  # Will be ApplicationRead when available
    total_count: int


class OpportunityStatsResponse(BaseModel):
    """Response for opportunity statistics"""
    total_opportunities: int
    active_opportunities: int
    featured_opportunities: int  
    urgency_breakdown: Dict[str, int]


class DeleteResponse(BaseModel):
    """Standard response for delete operations"""
    message: str

router = APIRouter(prefix="/v1/opportunities", tags=["opportunities"])


@router.post("/")
@format_api_response
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Create a new volunteer opportunity with enhanced validation"""
    
    # Check user permissions
    if current_user.role != "organization":
        raise_forbidden(
            "Only organizations can create opportunities",
            details={"required_role": "organization", "current_role": current_user.role}
        )
    
    # Verify the organization belongs to the current user
    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()
    
    if not organization:
        raise_not_found(
            "Organization profile not found. Please complete your organization profile first.",
            resource_type="organization",
            resource_id=str(current_user.id)
        )
    
    # Validate opportunity data
    try:
        validated_data = validate_opportunity_data(opportunity_data.model_dump())
    except Exception as e:
        raise_bad_request(
            "Opportunity data validation failed",
            details={"validation_error": str(e)}
        )
    
    # Check for duplicate opportunities (same title within 30 days)
    recent_opportunities = session.exec(
        select(Opportunity).where(
            and_(
                Opportunity.org_id == organization.id,
                Opportunity.title == validated_data["title"],
                Opportunity.created_at >= (datetime.now(datetime.timezone.utc) - timedelta(days=30))
            )
        )
    ).first()
    
    if recent_opportunities:
        raise_bad_request(
            "A similar opportunity was created recently",
            details={
                "suggestion": "Consider updating the existing opportunity instead",
                "existing_opportunity_id": recent_opportunities.id
            }
        )
    
    # Create the opportunity
    db_opportunity = Opportunity(
        **validated_data,
        org_id=organization.id
    )
    
    session.add(db_opportunity)
    session.commit()
    session.refresh(db_opportunity)
    
    # Return created response with location header
    opportunity_read = OpportunityRead.model_validate(db_opportunity)
    return created_resource(
        opportunity_read.model_dump(),
        "opportunity",
        str(db_opportunity.id)
    )


from datetime import timedelta


@router.get("/", response_model=List[OpportunityRead])
async def get_opportunities(
    session: Annotated[Session, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    state: Annotated[Optional[str], Query()] = None,
    country: Annotated[Optional[str], Query()] = None,
    causes: Annotated[Optional[List[str]], Query()] = None,
    skills: Annotated[Optional[List[str]], Query()] = None,
    remote_allowed: Annotated[Optional[bool], Query()] = None,
    urgency: Annotated[Optional[str], Query()] = None,
    featured: Annotated[Optional[bool], Query()] = None,
    search: Annotated[Optional[str], Query()] = None
):
    """Get opportunities with filtering and search"""
    query = select(Opportunity)
    
    # Apply filters
    if state:
        query = query.where(Opportunity.state == state)
    
    if country:
        query = query.where(Opportunity.country == country)
    
    if remote_allowed is not None:
        query = query.where(Opportunity.remote_allowed == remote_allowed)
    
    if urgency:
        query = query.where(Opportunity.urgency == urgency)
    
    if featured is not None:
        query = query.where(Opportunity.featured == featured)
    
    # Search in title and description
    if search:
        search_filter = or_(
            Opportunity.title.contains(search),
            Opportunity.description.contains(search),
            Opportunity.title_ar.contains(search),
            Opportunity.description_ar.contains(search)
        )
        query = query.where(search_filter)
    
    # Apply causes filtering (JSON array filtering)
    if causes:
        # For SQLite, we'll use a simple contains check for each cause
        for cause in causes:
            query = query.where(func.json_extract(Opportunity.causes, '$').contains(cause))
    
    # Apply skills filtering (JSON array filtering)  
    if skills:
        # For SQLite, we'll use a simple contains check for each skill
        for skill in skills:
            query = query.where(func.json_extract(Opportunity.skills_required, '$').contains(skill))
    
    # Order by featured first, then by creation date
    query = query.order_by(Opportunity.featured.desc(), Opportunity.created_at.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    opportunities = session.exec(query).all()
    return [OpportunityRead.model_validate(opp) for opp in opportunities]


@router.get("/search", response_model=List[OpportunityRead])
async def search_opportunities(
    session: Annotated[Session, Depends(get_session)],
    search: Annotated[Optional[str], Query()] = None,
    skills: Annotated[Optional[List[str]], Query()] = None,
    remote_allowed: Annotated[Optional[bool], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    skip: Annotated[int, Query(ge=0)] = 0
):
    """Search opportunities with basic filtering"""
    query = select(Opportunity).where(Opportunity.state == "active")
    
    # Apply search filter
    if search:
        search_filter = or_(
            Opportunity.title.contains(search),
            Opportunity.description.contains(search),
            Opportunity.title_ar.contains(search),
            Opportunity.description_ar.contains(search)
        )
        query = query.where(search_filter)
    
    # Apply remote filter (note: frontend sends 'remote' but model uses 'remote_allowed')
    if remote_allowed is not None:
        query = query.where(Opportunity.remote_allowed == remote_allowed)
    
    # Apply skills filter
    if skills:
        # For SQLite, we'll use a simple contains check for each skill
        for skill in skills:
            query = query.where(func.json_extract(Opportunity.skills_required, '$').contains(skill))
    
    # Order by creation date, apply pagination
    query = query.order_by(Opportunity.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    # Execute query with proper error handling
    try:
        opportunities = session.exec(query).all()
        return [OpportunityRead.model_validate(opp) for opp in opportunities]
    except Exception as e:
        # Log the error and raise proper HTTP exception instead of masking it
        import logging
        logging.error(f"Database error in search_opportunities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search query failed. Please try again or contact support."
        )


@router.get("/{opportunity_id}", response_model=OpportunityRead)
async def get_opportunity(
    opportunity_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get a specific opportunity by ID"""
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Increment view count
    opportunity.view_count += 1
    session.add(opportunity)
    session.commit()
    
    return OpportunityRead.model_validate(opportunity)


@router.put("/{opportunity_id}", response_model=OpportunityRead)
async def update_opportunity(
    opportunity_id: int,
    opportunity_update: OpportunityUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Update an opportunity"""
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Verify ownership
    organization = session.exec(
        select(Organisation).where(
            and_(
                Organisation.id == opportunity.org_id,
                Organisation.user_id == current_user.id
            )
        )
    ).first()
    
    if not organization and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this opportunity"
        )
    
    # Update the opportunity
    update_data = opportunity_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)
    
    opportunity.updated_at = datetime.now(datetime.timezone.utc)
    session.add(opportunity)
    session.commit()
    session.refresh(opportunity)
    
    return OpportunityRead.model_validate(opportunity)


@router.delete("/{opportunity_id}", response_model=DeleteResponse)
async def delete_opportunity(
    opportunity_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Delete an opportunity"""
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Verify ownership
    organization = session.exec(
        select(Organisation).where(
            and_(
                Organisation.id == opportunity.org_id,
                Organisation.user_id == current_user.id
            )
        )
    ).first()
    
    if not organization and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this opportunity"
        )
    
    session.delete(opportunity)
    session.commit()
    
    return DeleteResponse(message="Opportunity deleted successfully")


@router.get("/{opportunity_id}/applications", response_model=OpportunityApplicationsResponse)
async def get_opportunity_applications(
    opportunity_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status_filter: Annotated[Optional[str], Query()] = None
):
    """Get applications for a specific opportunity"""
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Verify ownership
    organization = session.exec(
        select(Organisation).where(
            and_(
                Organisation.id == opportunity.org_id,
                Organisation.user_id == current_user.id
            )
        )
    ).first()
    
    if not organization and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view applications for this opportunity"
        )
    
    # Get applications
    query = select(Application).where(Application.opp_id == opportunity_id)
    
    if status_filter:
        query = query.where(Application.status == status_filter)
    
    query = query.order_by(Application.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    applications = session.exec(query).all()
    
    return OpportunityApplicationsResponse(
        opportunity_id=opportunity_id,
        applications=[app.dict() for app in applications],
        total_count=len(applications)
    )


@router.get("/featured/list")
async def get_featured_opportunities(
    session: Annotated[Session, Depends(get_session)],
    limit: int = Query(10, ge=1, le=20)
):
    """Get featured opportunities for homepage"""
    query = select(Opportunity).where(
        and_(
            Opportunity.featured == True,
            Opportunity.state == "active"
        )
    ).order_by(Opportunity.created_at.desc()).limit(limit)
    
    opportunities = session.exec(query).all()
    return [OpportunityRead.model_validate(opp) for opp in opportunities]


@router.get("/stats/summary", response_model=OpportunityStatsResponse)
async def get_opportunities_stats(
    session: Annotated[Session, Depends(get_session)]
):
    """Get opportunities statistics"""
    # Total opportunities
    total = session.exec(select(func.count(Opportunity.id))).first()
    
    # Active opportunities
    active = session.exec(
        select(func.count(Opportunity.id)).where(Opportunity.state == "active")
    ).first()
    
    # Featured opportunities
    featured = session.exec(
        select(func.count(Opportunity.id)).where(Opportunity.featured == True)
    ).first()
    
    # Opportunities by urgency
    urgency_stats = session.exec(
        select(Opportunity.urgency, func.count(Opportunity.id))
        .group_by(Opportunity.urgency)
    ).all()
    
    return OpportunityStatsResponse(
        total_opportunities=total,
        active_opportunities=active,
        featured_opportunities=featured,
        urgency_breakdown=dict(urgency_stats)
    )


