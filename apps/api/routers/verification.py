from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    UploadFile,
    File,
    Form,
)
from sqlmodel import Session, select, func, and_
from typing import Annotated, Optional, Dict, Any
from datetime import datetime

from database import get_session
from models import User, Volunteer, SkillVerification, Badge, UserBadge
from routers.auth import get_current_user
from verification.skill_verifier import (
    verification_engine,
    VerificationMethod,
    VerificationStatus,
)
from verification.trust_system import (
    trust_system,
    TrustLevel,
    VerificationBadge,
    TrustFactor,
)

router = APIRouter(prefix="/v1/verification", tags=["verification"])


@router.post("/skills")
async def initiate_skill_verification(
    verification_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Initiate skill verification process"""

    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can initiate skill verification",
        )

    # Get volunteer profile
    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer profile not found"
        )

    skill_name = verification_data.get("skill_name")
    verification_method = verification_data.get("verification_method")
    evidence_data = verification_data.get("evidence_data", {})

    if not skill_name or not verification_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skill_name and verification_method are required",
        )

    try:
        method_enum = VerificationMethod(verification_method)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification method: {verification_method}",
        )

    try:
        verification = await verification_engine.initiate_skill_verification(
            session=session,
            volunteer_id=volunteer.id,
            skill_name=skill_name,
            verification_method=method_enum,
            evidence_data=evidence_data,
            requested_by=current_user.id,
        )

        return {
            "verification_id": verification.id,
            "skill_name": verification.skill_name,
            "verification_method": verification.verification_method.value,
            "status": verification.status.value,
            "created_at": verification.created_at.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating verification: {str(e)}",
        )


@router.get("/skills/my-verifications")
async def get_my_skill_verifications(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    status_filter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get current user's skill verifications"""

    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can view skill verifications",
        )

    # Get volunteer profile
    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer profile not found"
        )

    query = select(SkillVerification).where(
        SkillVerification.volunteer_id == volunteer.id
    )

    if status_filter:
        try:
            status_enum = VerificationStatus(status_filter)
            query = query.where(SkillVerification.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}",
            )

    query = query.order_by(SkillVerification.created_at.desc())
    query = query.offset(skip).limit(limit)

    verifications = session.exec(query).all()

    return [
        {
            "id": v.id,
            "skill_name": v.skill_name,
            "verification_method": v.verification_method.value,
            "status": v.status.value,
            "verification_score": v.verification_score,
            "verification_level": v.verification_level,
            "created_at": v.created_at.isoformat(),
            "verified_at": v.verified_at.isoformat() if v.verified_at else None,
            "peer_endorsements_count": len(v.peer_endorsements or []),
        }
        for v in verifications
    ]


@router.get("/skills/{verification_id}")
async def get_skill_verification_details(
    verification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get detailed information about a skill verification"""

    verification = session.get(SkillVerification, verification_id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found"
        )

    # Check permissions
    can_view = False

    if current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()
        if volunteer and verification.volunteer_id == volunteer.id:
            can_view = True

    elif current_user.role == "admin":
        can_view = True

    # Allow viewing if user can endorse (has same skill verified)
    if not can_view and current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()

        if volunteer:
            endorser_verification = session.exec(
                select(SkillVerification).where(
                    and_(
                        SkillVerification.volunteer_id == volunteer.id,
                        SkillVerification.skill_name == verification.skill_name,
                        SkillVerification.status == VerificationStatus.VERIFIED,
                    )
                )
            ).first()

            if endorser_verification:
                can_view = True

    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this verification",
        )

    # Get volunteer info
    volunteer = session.get(Volunteer, verification.volunteer_id)

    return {
        "id": verification.id,
        "volunteer_name": volunteer.full_name if volunteer else "Unknown",
        "skill_name": verification.skill_name,
        "verification_method": verification.verification_method.value,
        "status": verification.status.value,
        "verification_score": verification.verification_score,
        "verification_level": verification.verification_level,
        "evidence_data": verification.evidence_data,
        "peer_endorsements": verification.peer_endorsements or [],
        "assessment_results": (
            verification.assessment_results if current_user.role == "admin" else None
        ),
        "created_at": verification.created_at.isoformat(),
        "verified_at": (
            verification.verified_at.isoformat() if verification.verified_at else None
        ),
        "can_endorse": (
            current_user.role == "volunteer"
            and verification.verification_method == VerificationMethod.PEER_ENDORSEMENT
            and verification.status == VerificationStatus.PENDING
            and verification.volunteer_id != volunteer.id
            if volunteer
            else False
        ),
    }


@router.post("/skills/{verification_id}/endorse")
async def endorse_skill_verification(
    verification_id: int,
    endorsement_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Provide peer endorsement for skill verification"""

    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can provide endorsements",
        )

    try:
        success = await verification_engine.process_peer_endorsement(
            session=session,
            verification_id=verification_id,
            endorser_id=current_user.id,
            endorsement_data=endorsement_data,
        )

        if success:
            return {"message": "Endorsement provided successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to provide endorsement",
            )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error providing endorsement: {str(e)}",
        )


@router.post("/skills/{verification_id}/assessment")
async def complete_assessment_test(
    verification_id: int,
    test_results: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Complete assessment test for skill verification"""

    verification = session.get(SkillVerification, verification_id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found"
        )

    # Verify ownership
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can complete assessments",
        )

    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer or verification.volunteer_id != volunteer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this assessment",
        )

    try:
        success = await verification_engine.complete_assessment_test(
            session=session, verification_id=verification_id, test_results=test_results
        )

        if success:
            return {"message": "Assessment completed successfully", "verified": True}
        else:
            return {
                "message": "Assessment completed but verification failed",
                "verified": False,
            }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing assessment: {str(e)}",
        )


@router.post("/skills/{verification_id}/documents")
async def upload_verification_document(
    verification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    file: UploadFile = File(...),
    document_type: str = Form(...),
):
    """Upload document for skill verification"""

    verification = session.get(SkillVerification, verification_id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found"
        )

    # Verify ownership
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can upload verification documents",
        )

    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer or verification.volunteer_id != volunteer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload documents for this verification",
        )

    # Validate document type
    valid_document_types = [
        "certificate",
        "transcript",
        "portfolio",
        "work_sample",
        "reference_letter",
        "project_documentation",
        "other",
    ]
    if document_type not in valid_document_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Must be one of: {valid_document_types}",
        )

    try:
        # Upload file
        db_file = await file_handler.upload_file(
            file=file,
            upload_category="verification",
            user_id=current_user.id,
            session=session,
            file_description=f"{document_type} for {verification.skill_name} verification",
            is_public=False,
        )

        # Update verification evidence
        evidence_data = verification.evidence_data or {}
        documents = evidence_data.get("documents", [])

        documents.append(
            {
                "file_id": db_file.id,
                "document_type": document_type,
                "filename": db_file.filename,
                "uploaded_at": datetime.now(datetime.timezone.utc).isoformat(),
            }
        )

        evidence_data["documents"] = documents
        verification.evidence_data = evidence_data
        verification.updated_at = datetime.now(datetime.timezone.utc)

        session.add(verification)
        session.commit()

        return {
            "message": "Document uploaded successfully",
            "file_id": db_file.id,
            "document_type": document_type,
            "filename": db_file.filename,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}",
        )


@router.get("/badges/available")
async def get_available_badges(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get all available badges and their criteria"""

    badges = session.exec(select(Badge)).all()

    badge_list = []
    for badge in badges:
        # Get criteria from verification engine
        criteria = verification_engine.badge_criteria.get(badge.code, {})

        badge_list.append(
            {
                "id": badge.id,
                "code": badge.code,
                "name": badge.name,
                "description": badge.description,
                "badge_type": badge.badge_type.value,
                "rarity": badge.rarity,
                "points_value": badge.points_value,
                "criteria": criteria.get("criteria", {}),
                "icon_url": badge.icon_url,
                "color": badge.color,
            }
        )

    return {"badges": badge_list, "total_count": len(badge_list)}


@router.get("/badges/my-badges")
async def get_my_badges(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get current user's earned badges"""

    user_badges = session.exec(
        select(UserBadge, Badge)
        .join(Badge, UserBadge.badge_id == Badge.id)
        .where(UserBadge.user_id == current_user.id)
        .order_by(UserBadge.earned_at.desc())
    ).all()

    badges = []
    total_points = 0

    for user_badge, badge in user_badges:
        badges.append(
            {
                "badge_id": badge.id,
                "code": badge.code,
                "name": badge.name,
                "description": badge.description,
                "badge_type": badge.badge_type.value,
                "rarity": badge.rarity,
                "points_value": badge.points_value,
                "earned_at": user_badge.earned_at.isoformat(),
                "icon_url": badge.icon_url,
                "color": badge.color,
            }
        )

        total_points += badge.points_value or 0

    # Calculate badge statistics
    badge_counts_by_type = {}
    badge_counts_by_rarity = {}

    for user_badge, badge in user_badges:
        badge_type = badge.badge_type.value
        rarity = badge.rarity

        badge_counts_by_type[badge_type] = badge_counts_by_type.get(badge_type, 0) + 1
        badge_counts_by_rarity[rarity] = badge_counts_by_rarity.get(rarity, 0) + 1

    return {
        "badges": badges,
        "total_badges": len(badges),
        "total_points": total_points,
        "badge_counts_by_type": badge_counts_by_type,
        "badge_counts_by_rarity": badge_counts_by_rarity,
    }


@router.get("/leaderboard")
async def get_verification_leaderboard(
    session: Annotated[Session, Depends(get_session)],
    period: str = Query("all_time", regex="^(week|month|all_time)$"),
    limit: int = Query(20, ge=1, le=100),
):
    """Get verification leaderboard"""

    # Calculate date filter
    date_filter = None
    if period == "week":
        date_filter = datetime.now(datetime.timezone.utc) - timedelta(days=7)
    elif period == "month":
        date_filter = datetime.now(datetime.timezone.utc) - timedelta(days=30)

    # Get top users by badge points
    query = (
        select(
            User.id,
            User.first_name,
            User.last_name,
            func.count(UserBadge.id).label("badge_count"),
            func.sum(Badge.points_value).label("total_points"),
        )
        .join(UserBadge, User.id == UserBadge.user_id)
        .join(Badge, UserBadge.badge_id == Badge.id)
    )

    if date_filter:
        query = query.where(UserBadge.earned_at >= date_filter)

    query = query.group_by(User.id, User.first_name, User.last_name)
    query = query.order_by(func.sum(Badge.points_value).desc())
    query = query.limit(limit)

    results = session.exec(query).all()

    leaderboard = []
    for i, (user_id, first_name, last_name, badge_count, total_points) in enumerate(
        results
    ):
        # Get user's top badges
        top_badges = session.exec(
            select(Badge.name, Badge.rarity)
            .join(UserBadge, Badge.id == UserBadge.badge_id)
            .where(UserBadge.user_id == user_id)
            .order_by(Badge.points_value.desc())
            .limit(3)
        ).all()

        leaderboard.append(
            {
                "rank": i + 1,
                "user_id": user_id,
                "user_name": f"{first_name} {last_name}",
                "badge_count": badge_count,
                "total_points": total_points or 0,
                "top_badges": [
                    {"name": name, "rarity": rarity} for name, rarity in top_badges
                ],
            }
        )

    return {
        "leaderboard": leaderboard,
        "period": period,
        "total_users": len(leaderboard),
    }


@router.get("/stats/summary")
async def get_verification_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get verification system statistics"""

    volunteer_id = None
    if current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()
        if volunteer:
            volunteer_id = volunteer.id

    try:
        stats = await verification_engine.get_verification_statistics(
            session=session, volunteer_id=volunteer_id
        )

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving verification statistics: {str(e)}",
        )


# Admin endpoints
@router.post("/admin/verify/{verification_id}")
async def admin_verify_skill(
    verification_id: int,
    verification_decision: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Admin manually verify or reject a skill verification"""

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    verification = session.get(SkillVerification, verification_id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found"
        )

    decision = verification_decision.get("decision")  # "approve" or "reject"
    score = verification_decision.get("score", 0.8)
    notes = verification_decision.get("notes", "")

    if decision not in ["approve", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be 'approve' or 'reject'",
        )

    # Update verification
    verification.status = (
        VerificationStatus.VERIFIED
        if decision == "approve"
        else VerificationStatus.REJECTED
    )
    verification.verification_score = score if decision == "approve" else 0
    verification.verified_at = datetime.now(datetime.timezone.utc)
    verification.verified_by = current_user.id
    verification.admin_notes = notes

    session.add(verification)
    session.commit()

    # Update volunteer skills if approved
    if decision == "approve":
        await verification_engine._update_volunteer_skills(session, verification)
        await verification_engine._check_badge_eligibility(
            session, verification.volunteer_id
        )

    return {
        "message": f"Verification {decision}d successfully",
        "verification_id": verification_id,
        "new_status": verification.status.value,
    }


from datetime import timedelta


# Organization Trust System Endpoints


@router.get("/organizations/{org_id}/trust-score")
async def get_organization_trust_score(
    org_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    recalculate: bool = Query(False),
):
    """Get organization's trust score and level"""

    # Verify organization exists
    organization = session.get(Organisation, org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    try:
        if recalculate or not organization.trust_score:
            # Recalculate trust score
            trust_data = await trust_system.calculate_trust_score(
                session=session, organization_id=org_id
            )
        else:
            # Return existing trust data
            trust_data = {
                "organization_id": org_id,
                "trust_score": organization.trust_score or 0,
                "trust_level": organization.trust_level or TrustLevel.UNVERIFIED.value,
                "last_updated": (
                    organization.trust_last_updated.isoformat()
                    if organization.trust_last_updated
                    else None
                ),
            }

        return trust_data

    except Exception as e:
        logger.error(f"Error getting trust score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving trust score",
        )


@router.post("/organizations/{org_id}/trust-score/recalculate")
async def recalculate_trust_score(
    org_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Recalculate organization's trust score (organization admin or admin only)"""

    # Check permissions
    can_recalculate = False

    if current_user.role == "admin":
        can_recalculate = True
    elif current_user.role == "organization":
        # Check if user owns this organization
        organization = session.exec(
            select(Organisation).where(
                and_(Organisation.id == org_id, Organisation.user_id == current_user.id)
            )
        ).first()
        if organization:
            can_recalculate = True

    if not can_recalculate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to recalculate trust score",
        )

    try:
        trust_data = await trust_system.calculate_trust_score(
            session=session, organization_id=org_id
        )

        return {"message": "Trust score recalculated successfully", **trust_data}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error recalculating trust score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error recalculating trust score",
        )


@router.get("/organizations/{org_id}/verification-badges/eligible")
async def get_eligible_verification_badges(
    org_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get verification badges the organization is eligible for"""

    # Check permissions
    can_view = False

    if current_user.role == "admin":
        can_view = True
    elif current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(
                and_(Organisation.id == org_id, Organisation.user_id == current_user.id)
            )
        ).first()
        if organization:
            can_view = True

    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view badge eligibility",
        )

    try:
        eligible_badges = await trust_system.check_badge_eligibility(
            session=session, organization_id=org_id
        )

        return {
            "organization_id": org_id,
            "eligible_badges": eligible_badges,
            "total_eligible": len(eligible_badges),
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error checking badge eligibility: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking badge eligibility",
        )


@router.post("/organizations/{org_id}/verification-badges/{badge_code}/award")
async def award_verification_badge(
    org_id: int,
    badge_code: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Award a verification badge to an organization (admin only)"""

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to award badges",
        )

    try:
        badge_award = await trust_system.award_verification_badge(
            session=session,
            organization_id=org_id,
            badge_code=badge_code,
            awarded_by=current_user.id,
        )

        return {"message": "Verification badge awarded successfully", **badge_award}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error awarding verification badge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error awarding verification badge",
        )


@router.get("/organizations/{org_id}/verification-badges")
async def get_organization_verification_badges(
    org_id: int, session: Annotated[Session, Depends(get_session)]
):
    """Get all verification badges earned by an organization (public endpoint)"""

    # Verify organization exists
    organization = session.get(Organisation, org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    try:
        # Get organization's verification badges
        badges = session.exec(
            select(UserBadge, Badge)
            .join(Badge, UserBadge.badge_id == Badge.id)
            .where(
                and_(
                    UserBadge.user_id == organization.user_id,
                    Badge.badge_type == "verification",
                )
            )
            .order_by(UserBadge.earned_at.desc())
        ).all()

        badge_list = []
        total_trust_boost = 0.0

        for user_badge, badge in badges:
            badge_info = trust_system.badge_criteria.get(badge.code, {})
            trust_boost = badge_info.get("trust_boost", 0)
            total_trust_boost += trust_boost

            badge_list.append(
                {
                    "badge_code": badge.code,
                    "name": badge.name,
                    "description": badge.description,
                    "earned_at": user_badge.earned_at.isoformat(),
                    "trust_boost": trust_boost,
                    "icon_url": badge.icon_url,
                    "color": badge.color,
                }
            )

        return {
            "organization_id": org_id,
            "organization_name": organization.name,
            "verification_badges": badge_list,
            "total_badges": len(badge_list),
            "total_trust_boost": round(total_trust_boost, 3),
            "trust_level": organization.trust_level or TrustLevel.UNVERIFIED.value,
        }

    except Exception as e:
        logger.error(f"Error getting verification badges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving verification badges",
        )


@router.get("/trust-system/stats")
async def get_trust_system_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get trust system statistics (admin only)"""

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    try:
        stats = trust_system.get_trust_system_stats(session)
        return stats

    except Exception as e:
        logger.error(f"Error getting trust system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving trust system statistics",
        )


@router.get("/organizations/top-trusted")
async def get_top_trusted_organizations(
    session: Annotated[Session, Depends(get_session)],
    limit: int = Query(20, ge=1, le=50),
):
    """Get top trusted organizations (public endpoint)"""

    try:
        # Get organizations with highest trust scores
        organizations = session.exec(
            select(Organisation)
            .where(Organisation.trust_score.is_not(None))
            .order_by(Organisation.trust_score.desc())
            .limit(limit)
        ).all()

        org_list = []
        for org in organizations:
            # Get verification badge count
            badge_count = session.exec(
                select(func.count(UserBadge.id))
                .join(Badge, UserBadge.badge_id == Badge.id)
                .where(
                    and_(
                        UserBadge.user_id == org.user_id,
                        Badge.badge_type == "verification",
                    )
                )
            ).first()

            org_list.append(
                {
                    "id": org.id,
                    "name": org.name,
                    "description": (
                        org.description[:200] + "..."
                        if len(org.description or "") > 200
                        else org.description
                    ),
                    "trust_score": round(org.trust_score, 3),
                    "trust_level": org.trust_level,
                    "verification_badge_count": badge_count or 0,
                    "verified": org.verified,
                    "country": org.country,
                    "city": org.city,
                    "cause_areas": (
                        org.cause_areas[:3] if org.cause_areas else []
                    ),  # Show top 3 causes
                }
            )

        return {"top_organizations": org_list, "total_count": len(org_list)}

    except Exception as e:
        logger.error(f"Error getting top trusted organizations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving top trusted organizations",
        )


@router.get("/trust-levels")
async def get_trust_levels(current_user: Annotated[User, Depends(get_current_user)]):
    """Get available trust levels and their thresholds"""

    trust_levels = []

    for level in TrustLevel:
        threshold = trust_system.trust_thresholds[level]
        trust_levels.append(
            {
                "level": level.value,
                "threshold": threshold,
                "description": f"Trust score >= {threshold}",
            }
        )

    return {
        "trust_levels": trust_levels,
        "trust_factors": [factor.value for factor in TrustFactor],
        "verification_badges": [badge.value for badge in VerificationBadge],
    }
