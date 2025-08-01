from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlmodel import Session, select, func, and_, or_
from typing import Annotated, List, Optional
from datetime import datetime

from database import get_session
from models import (
    User, UserRead, UserUpdate,
    Volunteer, VolunteerCreate, VolunteerRead, VolunteerUpdate,
    Organisation, OrganisationCreate, OrganisationRead, OrganisationUpdate,
    Application, Opportunity, Review
)
from routers.auth import get_current_user, get_current_user_optional

router = APIRouter(prefix="/v1/profiles", tags=["profiles"])


# Volunteer Profile Management
@router.post("/volunteer", response_model=VolunteerRead)
async def create_volunteer_profile(
    volunteer_data: VolunteerCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Create or update volunteer profile"""
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with volunteer role can create volunteer profiles"
        )
    
    # Check if profile already exists
    existing_volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()
    
    if existing_volunteer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Volunteer profile already exists"
        )
    
    # Create volunteer profile
    db_volunteer = Volunteer(
        **volunteer_data.model_dump(),
        user_id=current_user.id
    )
    
    session.add(db_volunteer)
    session.commit()
    session.refresh(db_volunteer)
    
    return VolunteerRead.model_validate(db_volunteer)


@router.get("/volunteer/me", response_model=VolunteerRead)
async def get_my_volunteer_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get current user's volunteer profile"""
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can access volunteer profiles"
        )
    
    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    return VolunteerRead.model_validate(volunteer)


@router.put("/volunteer/me", response_model=VolunteerRead)
async def update_my_volunteer_profile(
    volunteer_update: VolunteerUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Update current user's volunteer profile"""
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can update volunteer profiles"
        )
    
    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    # Update volunteer profile
    update_data = volunteer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(volunteer, field, value)
    
    volunteer.updated_at = datetime.now(datetime.timezone.utc)
    session.add(volunteer)
    session.commit()
    session.refresh(volunteer)
    
    return VolunteerRead.model_validate(volunteer)


@router.get("/volunteer/{volunteer_id}", response_model=VolunteerRead)
async def get_volunteer_profile(
    volunteer_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get a specific volunteer profile (public view with optional authentication)"""
    volunteer = session.get(Volunteer, volunteer_id)
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    return VolunteerRead.model_validate(volunteer)


# Organization Profile Management
@router.post("/organization", response_model=OrganisationRead)
async def create_organization_profile(
    org_data: OrganisationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Create organization profile"""
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with organization role can create organization profiles"
        )
    
    # Check if profile already exists
    existing_org = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()
    
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization profile already exists"
        )
    
    # Create organization profile
    db_org = Organisation(
        **org_data.model_dump(),
        user_id=current_user.id
    )
    
    session.add(db_org)
    session.commit()
    session.refresh(db_org)
    
    return OrganisationRead.model_validate(db_org)


@router.get("/organization/me", response_model=OrganisationRead)
async def get_my_organization_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get current user's organization profile"""
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can access organization profiles"
        )
    
    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found"
        )
    
    return OrganisationRead.model_validate(organization)


@router.put("/organization/me", response_model=OrganisationRead)
async def update_my_organization_profile(
    org_update: OrganisationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Update current user's organization profile"""
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can update organization profiles"
        )
    
    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found"
        )
    
    # Update organization profile
    update_data = org_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    organization.updated_at = datetime.now(datetime.timezone.utc)
    session.add(organization)
    session.commit()
    session.refresh(organization)
    
    return OrganisationRead.model_validate(organization)


@router.get("/organization/{org_id}", response_model=OrganisationRead)
async def get_organization_profile(
    org_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get a specific organization profile (public view with optional authentication)"""
    organization = session.get(Organisation, org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found"
        )
    
    return OrganisationRead.model_validate(organization)


# Profile Search and Discovery
@router.get("/volunteers", response_model=List[VolunteerRead])
async def search_volunteers(
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    skills: Optional[List[str]] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    verified: Optional[bool] = Query(None),
    available: Optional[bool] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0),
    search: Optional[str] = Query(None)
):
    """Search for volunteer profiles"""
    query = select(Volunteer)
    
    # Apply filters
    if country:
        query = query.where(Volunteer.country == country)
    
    if city:
        query = query.where(Volunteer.city == city)
    
    if verified is not None:
        query = query.where(Volunteer.verified == verified)
    
    if available is not None:
        if available:
            query = query.where(Volunteer.available == True)
    
    if min_rating is not None:
        query = query.where(Volunteer.rating >= min_rating)
    
    # Search in name and bio
    if search:
        search_filter = or_(
            Volunteer.full_name.contains(search),
            Volunteer.bio.contains(search),
            Volunteer.bio_ar.contains(search)
        )
        query = query.where(search_filter)
    
    # Order by rating and verification status
    query = query.order_by(Volunteer.verified.desc(), Volunteer.rating.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    volunteers = session.exec(query).all()
    return [VolunteerRead.model_validate(vol) for vol in volunteers]


@router.get("/organizations", response_model=List[OrganisationRead])
async def search_organizations(
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    cause_areas: Optional[List[str]] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    verified: Optional[bool] = Query(None),
    search: Optional[str] = Query(None)
):
    """Search for organization profiles"""
    query = select(Organisation)
    
    # Apply filters
    if country:
        query = query.where(Organisation.country == country)
    
    if city:
        query = query.where(Organisation.city == city)
    
    if verified is not None:
        query = query.where(Organisation.verified == verified)
    
    # Search in name and description
    if search:
        search_filter = or_(
            Organisation.name.contains(search),
            Organisation.description.contains(search),
            Organisation.description_ar.contains(search)
        )
        query = query.where(search_filter)
    
    # Order by verification status and creation date
    query = query.order_by(Organisation.verified.desc(), Organisation.created_at.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    organizations = session.exec(query).all()
    return [OrganisationRead.model_validate(org) for org in organizations]


# Profile Statistics and Analytics
@router.get("/volunteer/{volunteer_id}/stats")
async def get_volunteer_stats(
    volunteer_id: int,
    session: Annotated[Session, Depends(get_session)]
):
    """Get volunteer statistics"""
    volunteer = session.get(Volunteer, volunteer_id)
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    # Get application stats
    total_applications = session.exec(
        select(func.count(Application.id)).where(Application.volunteer_id == volunteer_id)
    ).first()
    
    accepted_applications = session.exec(
        select(func.count(Application.id)).where(
            and_(
                Application.volunteer_id == volunteer_id,
                Application.status == "accepted"
            )
        )
    ).first()
    
    completed_applications = session.exec(
        select(func.count(Application.id)).where(
            and_(
                Application.volunteer_id == volunteer_id,
                Application.status == "completed"
            )
        )
    ).first()
    
    # Get reviews count
    reviews_count = session.exec(
        select(func.count(Review.id)).where(Review.volunteer_id == volunteer_id)
    ).first()
    
    return {
        "volunteer_id": volunteer_id,
        "total_applications": total_applications,
        "accepted_applications": accepted_applications,
        "completed_applications": completed_applications,
        "completion_rate": (completed_applications / accepted_applications * 100) if accepted_applications > 0 else 0,
        "reviews_count": reviews_count,
        "average_rating": volunteer.rating,
        "verified": volunteer.verified
    }


@router.get("/organization/{org_id}/stats")
async def get_organization_stats(
    org_id: int,
    session: Annotated[Session, Depends(get_session)]
):
    """Get organization statistics"""
    organization = session.get(Organisation, org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found"
        )
    
    # Get opportunity stats
    total_opportunities = session.exec(
        select(func.count(Opportunity.id)).where(Opportunity.org_id == org_id)
    ).first()
    
    active_opportunities = session.exec(
        select(func.count(Opportunity.id)).where(
            and_(
                Opportunity.org_id == org_id,
                Opportunity.state == "active"
            )
        )
    ).first()
    
    # Get application stats for org's opportunities
    total_applications = session.exec(
        select(func.count(Application.id))
        .join(Opportunity, Application.opp_id == Opportunity.id)
        .where(Opportunity.org_id == org_id)
    ).first()
    
    accepted_volunteers = session.exec(
        select(func.count(Application.id))
        .join(Opportunity, Application.opp_id == Opportunity.id)
        .where(
            and_(
                Opportunity.org_id == org_id,
                Application.status == "accepted"
            )
        )
    ).first()
    
    return {
        "organization_id": org_id,
        "total_opportunities": total_opportunities,
        "active_opportunities": active_opportunities,
        "total_applications": total_applications,
        "accepted_volunteers": accepted_volunteers,
        "verified": organization.verified,
        "trust_score": organization.trust_score
    }


# Profile Completion and Verification
@router.post("/volunteer/complete")
async def complete_volunteer_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Mark volunteer profile as complete"""
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can complete their profiles"
        )
    
    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    # Check if profile has required fields
    required_fields = [
        volunteer.full_name,
        volunteer.bio,
        volunteer.skills,
        volunteer.country,
        volunteer.city
    ]
    
    if not all(required_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete all required profile fields"
        )
    
    # Update profile completion
    current_user.profile_completed = True
    volunteer.profile_completed = True
    volunteer.updated_at = datetime.now(datetime.timezone.utc)
    
    session.add(current_user)
    session.add(volunteer)
    session.commit()
    
    return {"message": "Profile marked as complete"}


@router.post("/organization/complete")
async def complete_organization_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Mark organization profile as complete"""
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can complete their profiles"
        )
    
    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found"
        )
    
    # Check if profile has required fields
    required_fields = [
        organization.name,
        organization.description,
        organization.cause_areas,
        organization.country,
        organization.city,
        organization.contact_email
    ]
    
    if not all(required_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete all required profile fields"
        )
    
    # Update profile completion
    current_user.profile_completed = True
    organization.profile_completed = True
    organization.updated_at = datetime.now(datetime.timezone.utc)
    
    session.add(current_user)
    session.add(organization)
    session.commit()
    
    return {"message": "Profile marked as complete"}