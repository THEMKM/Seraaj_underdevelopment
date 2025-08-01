from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func, and_, or_
from typing import Annotated, List, Optional
from datetime import datetime

from database import get_session
from models import (
    Review,
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
    ReviewVote,
    ReviewFlag,
    User,
    Volunteer,
    Organisation,
    Application,
    Opportunity,
)
from routers.auth import get_current_user

router = APIRouter(prefix="/v1/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewRead)
async def create_review(
    review_data: ReviewCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new review"""
    # Verify the reviewer has permission to review
    if review_data.volunteer_id:
        # Organization reviewing a volunteer
        if current_user.role != "organization":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organizations can review volunteers",
            )

        # Verify the organization has worked with this volunteer
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization profile not found",
            )

        # Check if there's a completed application between them
        completed_application = session.exec(
            select(Application)
            .join(Opportunity, Application.opp_id == Opportunity.id)
            .where(
                and_(
                    Application.volunteer_id == review_data.volunteer_id,
                    Opportunity.org_id == organization.id,
                    Application.status == "completed",
                )
            )
        ).first()

        if not completed_application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only review volunteers you have worked with",
            )

    elif review_data.organisation_id:
        # Volunteer reviewing an organization
        if current_user.role != "volunteer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only volunteers can review organizations",
            )

        # Verify the volunteer has worked with this organization
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()

        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Volunteer profile not found",
            )

        # Check if there's a completed application between them
        completed_application = session.exec(
            select(Application)
            .join(Opportunity, Application.opp_id == Opportunity.id)
            .where(
                and_(
                    Application.volunteer_id == volunteer.id,
                    Opportunity.org_id == review_data.organisation_id,
                    Application.status == "completed",
                )
            )
        ).first()

        if not completed_application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only review organizations you have worked with",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify either volunteer_id or organisation_id",
        )

    # Check if review already exists
    existing_review = session.exec(
        select(Review).where(
            and_(
                Review.reviewer_id == current_user.id,
                or_(
                    and_(
                        Review.volunteer_id == review_data.volunteer_id,
                        review_data.volunteer_id.is_not(None),
                    ),
                    and_(
                        Review.organisation_id == review_data.organisation_id,
                        review_data.organisation_id.is_not(None),
                    ),
                ),
            )
        )
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this user",
        )

    # Create review
    db_review = Review(**review_data.model_dump(), reviewer_id=current_user.id)

    session.add(db_review)
    session.commit()
    session.refresh(db_review)

    # Update average rating
    await update_average_rating(
        session, review_data.volunteer_id, review_data.organisation_id
    )

    return ReviewRead.model_validate(db_review)


@router.get("/", response_model=List[ReviewRead])
async def get_reviews(
    session: Annotated[Session, Depends(get_session)],
    volunteer_id: Optional[int] = Query(None),
    organisation_id: Optional[int] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
):
    """Get reviews with filtering"""
    query = select(Review)

    # Apply filters
    if volunteer_id:
        query = query.where(Review.volunteer_id == volunteer_id)

    if organisation_id:
        query = query.where(Review.organisation_id == organisation_id)

    if reviewer_id:
        query = query.where(Review.reviewer_id == reviewer_id)

    if min_rating:
        query = query.where(Review.rating >= min_rating)

    # Order by creation date
    query = query.order_by(Review.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    reviews = session.exec(query).all()
    return [ReviewRead.model_validate(review) for review in reviews]


@router.get("/{review_id}", response_model=ReviewRead)
async def get_review(review_id: int, session: Annotated[Session, Depends(get_session)]):
    """Get a specific review"""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    return ReviewRead.model_validate(review)


@router.put("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Update a review (only by original reviewer)"""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    # Check if user is the original reviewer or admin
    if review.reviewer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the original reviewer can update this review",
        )

    # Update review
    update_data = review_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    review.updated_at = datetime.now(datetime.timezone.utc)
    session.add(review)
    session.commit()
    session.refresh(review)

    # Update average rating if rating changed
    if "rating" in update_data:
        await update_average_rating(
            session, review.volunteer_id, review.organisation_id
        )

    return ReviewRead.model_validate(review)


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Delete a review"""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    # Check permissions
    if review.reviewer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the original reviewer or admin can delete this review",
        )

    volunteer_id = review.volunteer_id
    organisation_id = review.organisation_id

    session.delete(review)
    session.commit()

    # Update average rating
    await update_average_rating(session, volunteer_id, organisation_id)

    return {"message": "Review deleted successfully"}


@router.post("/{review_id}/vote")
async def vote_on_review(
    review_id: int,
    helpful: bool,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Vote on a review (helpful/not helpful)"""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    # Check if user already voted
    existing_vote = session.exec(
        select(ReviewVote).where(
            and_(
                ReviewVote.review_id == review_id, ReviewVote.user_id == current_user.id
            )
        )
    ).first()

    if existing_vote:
        # Update existing vote
        existing_vote.helpful = helpful
        existing_vote.updated_at = datetime.now(datetime.timezone.utc)
        session.add(existing_vote)
    else:
        # Create new vote
        vote = ReviewVote(review_id=review_id, user_id=current_user.id, helpful=helpful)
        session.add(vote)

    session.commit()

    # Update review vote counts
    helpful_votes = session.exec(
        select(func.count(ReviewVote.id)).where(
            and_(ReviewVote.review_id == review_id, ReviewVote.helpful == True)
        )
    ).first()

    unhelpful_votes = session.exec(
        select(func.count(ReviewVote.id)).where(
            and_(ReviewVote.review_id == review_id, ReviewVote.helpful == False)
        )
    ).first()

    review.helpful_votes = helpful_votes or 0
    review.unhelpful_votes = unhelpful_votes or 0
    session.add(review)
    session.commit()

    return {"message": "Vote recorded successfully"}


@router.post("/{review_id}/flag")
async def flag_review(
    review_id: int,
    reason: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Flag a review for moderation"""
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    # Check if user already flagged this review
    existing_flag = session.exec(
        select(ReviewFlag).where(
            and_(
                ReviewFlag.review_id == review_id,
                ReviewFlag.flagger_id == current_user.id,
            )
        )
    ).first()

    if existing_flag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already flagged this review",
        )

    # Create flag
    flag = ReviewFlag(review_id=review_id, flagger_id=current_user.id, reason=reason)

    session.add(flag)

    # Mark review as flagged
    review.flagged = True
    session.add(review)

    session.commit()

    return {"message": "Review flagged for moderation"}


@router.get("/stats/summary")
async def get_review_statistics(
    session: Annotated[Session, Depends(get_session)],
    volunteer_id: Optional[int] = Query(None),
    organisation_id: Optional[int] = Query(None),
):
    """Get review statistics"""
    base_query = select(Review)

    if volunteer_id:
        base_query = base_query.where(Review.volunteer_id == volunteer_id)
    elif organisation_id:
        base_query = base_query.where(Review.organisation_id == organisation_id)

    # Total reviews
    total_reviews = session.exec(
        select(func.count(Review.id)).select_from(base_query.subquery())
    ).first()

    # Average rating
    avg_rating = session.exec(
        select(func.avg(Review.rating)).select_from(base_query.subquery())
    ).first()

    # Rating distribution
    rating_distribution = session.exec(
        select(Review.rating, func.count(Review.id))
        .select_from(base_query.subquery())
        .group_by(Review.rating)
    ).all()

    # Recent reviews (last 30 days)
    thirty_days_ago = datetime.now(datetime.timezone.utc) - timedelta(days=30)
    recent_reviews = session.exec(
        select(func.count(Review.id)).select_from(
            base_query.where(Review.created_at >= thirty_days_ago).subquery()
        )
    ).first()

    return {
        "total_reviews": total_reviews or 0,
        "average_rating": round(float(avg_rating), 2) if avg_rating else 0,
        "rating_distribution": dict(rating_distribution),
        "recent_reviews": recent_reviews or 0,
        "volunteer_id": volunteer_id,
        "organisation_id": organisation_id,
    }


async def update_average_rating(
    session: Session, volunteer_id: Optional[int], organisation_id: Optional[int]
):
    """Update the average rating for a volunteer or organization"""
    if volunteer_id:
        # Update volunteer rating
        avg_rating = session.exec(
            select(func.avg(Review.rating)).where(Review.volunteer_id == volunteer_id)
        ).first()

        volunteer = session.get(Volunteer, volunteer_id)
        if volunteer and avg_rating:
            volunteer.rating = float(avg_rating)
            session.add(volunteer)

    elif organisation_id:
        # Update organization rating
        avg_rating = session.exec(
            select(func.avg(Review.rating)).where(
                Review.organisation_id == organisation_id
            )
        ).first()

        organisation = session.get(Organisation, organisation_id)
        if organisation and avg_rating:
            organisation.rating = float(avg_rating)
            session.add(organisation)

    session.commit()


from datetime import timedelta
