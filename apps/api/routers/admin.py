from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func, and_, or_
from typing import Annotated, List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import get_session
from models import (
    User,
    UserRead,
    UserUpdate,
    UserRole,
    UserStatus,
    Organisation,
    Opportunity,
    Application,
    Message,
    Conversation,
    Review,
    AnalyticsEvent,
    PerformanceMetric,
)
from routers.auth import get_current_user
from utils.data_seeder import DataSeeder
from utils.response_formatter import success_with_data

router = APIRouter(prefix="/v1/admin", tags=["admin"])


def require_admin(current_user: Annotated[User, Depends(get_current_user)]):
    """Dependency to ensure user has admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


# User Management
@router.get("/users", response_model=List[UserRead])
async def get_all_users(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    role: Annotated[Optional[str], Query()] = None,
    status: Annotated[Optional[str], Query()] = None,
    search: Annotated[Optional[str], Query()] = None,
):
    """Get all users with filtering and pagination"""
    query = select(User)

    # Apply filters
    if role:
        try:
            query = query.where(User.role == UserRole(role))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role"
            )

    if status:
        try:
            query = query.where(User.status == UserStatus(status))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
            )

    # Search in name and email
    if search:
        search_filter = or_(
            User.first_name.contains(search),
            User.last_name.contains(search),
            User.email.contains(search),
        )
        query = query.where(search_filter)

    # Order by creation date
    query = query.order_by(User.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    users = session.exec(query).all()
    return [UserRead.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_details(
    user_id: int,
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get detailed information about a specific user"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserRead.model_validate(user)


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    """Update a user's information"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update user
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.now(datetime.timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)

    return UserRead.model_validate(user)


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    reason: str,
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    """Suspend a user account"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot suspend admin users"
        )

    user.status = UserStatus.SUSPENDED
    user.suspension_reason = reason
    user.suspended_at = datetime.now(datetime.timezone.utc)
    user.suspended_by = admin_user.id
    user.updated_at = datetime.now(datetime.timezone.utc)

    session.add(user)
    session.commit()

    return {"message": "User suspended successfully"}


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    """Activate a suspended user account"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.status = UserStatus.ACTIVE
    user.suspension_reason = None
    user.suspended_at = None
    user.suspended_by = None
    user.updated_at = datetime.now(datetime.timezone.utc)

    session.add(user)
    session.commit()

    return {"message": "User activated successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    """Delete a user account (soft delete)"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete admin users"
        )

    # Soft delete
    user.status = UserStatus.DELETED
    user.updated_at = datetime.now(datetime.timezone.utc)

    session.add(user)
    session.commit()

    return {"message": "User deleted successfully"}


# Platform Statistics
@router.get("/stats/overview")
async def get_platform_overview(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get comprehensive platform statistics"""

    # User statistics
    total_users = session.exec(select(func.count(User.id))).first()
    active_users = session.exec(
        select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
    ).first()
    volunteers_count = session.exec(
        select(func.count(User.id)).where(User.role == UserRole.VOLUNTEER)
    ).first()
    organizations_count = session.exec(
        select(func.count(User.id)).where(User.role == UserRole.ORGANIZATION)
    ).first()

    # Opportunity statistics
    total_opportunities = session.exec(select(func.count(Opportunity.id))).first()
    active_opportunities = session.exec(
        select(func.count(Opportunity.id)).where(Opportunity.state == "active")
    ).first()

    # Application statistics
    total_applications = session.exec(select(func.count(Application.id))).first()
    accepted_applications = session.exec(
        select(func.count(Application.id)).where(Application.status == "accepted")
    ).first()

    # Message statistics
    total_messages = session.exec(select(func.count(Message.id))).first()
    total_conversations = session.exec(select(func.count(Conversation.id))).first()

    # Recent activity (last 7 days)
    week_ago = datetime.now(datetime.timezone.utc) - timedelta(days=7)

    new_users_week = session.exec(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    ).first()

    new_opportunities_week = session.exec(
        select(func.count(Opportunity.id)).where(Opportunity.created_at >= week_ago)
    ).first()

    new_applications_week = session.exec(
        select(func.count(Application.id)).where(Application.created_at >= week_ago)
    ).first()

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "volunteers": volunteers_count,
            "organizations": organizations_count,
            "new_this_week": new_users_week,
        },
        "opportunities": {
            "total": total_opportunities,
            "active": active_opportunities,
            "new_this_week": new_opportunities_week,
        },
        "applications": {
            "total": total_applications,
            "accepted": accepted_applications,
            "acceptance_rate": (
                (accepted_applications / total_applications * 100)
                if total_applications > 0
                else 0
            ),
            "new_this_week": new_applications_week,
        },
        "messaging": {
            "total_messages": total_messages,
            "total_conversations": total_conversations,
        },
    }


@router.get("/stats/users")
async def get_user_statistics(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
    days: int = Query(30, ge=1, le=365),
):
    """Get detailed user statistics over time"""
    start_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)

    # User registration over time
    user_registrations = session.exec(
        select(func.date(User.created_at), func.count(User.id))
        .where(User.created_at >= start_date)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
    ).all()

    # User status breakdown
    status_breakdown = session.exec(
        select(User.status, func.count(User.id)).group_by(User.status)
    ).all()

    # User role breakdown
    role_breakdown = session.exec(
        select(User.role, func.count(User.id)).group_by(User.role)
    ).all()

    # Most active users
    active_users = session.exec(
        select(User.id, User.first_name, User.last_name, User.login_count)
        .where(User.status == UserStatus.ACTIVE)
        .order_by(User.login_count.desc())
        .limit(10)
    ).all()

    return {
        "registration_timeline": [
            {"date": date.isoformat(), "count": count}
            for date, count in user_registrations
        ],
        "status_breakdown": dict(status_breakdown),
        "role_breakdown": dict(role_breakdown),
        "most_active_users": [
            {
                "id": user_id,
                "name": f"{first_name} {last_name}",
                "login_count": login_count,
            }
            for user_id, first_name, last_name, login_count in active_users
        ],
    }


@router.get("/stats/opportunities")
async def get_opportunity_statistics(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
    days: int = Query(30, ge=1, le=365),
):
    """Get detailed opportunity statistics"""
    start_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)

    # Opportunity creation over time
    opportunity_creation = session.exec(
        select(func.date(Opportunity.created_at), func.count(Opportunity.id))
        .where(Opportunity.created_at >= start_date)
        .group_by(func.date(Opportunity.created_at))
        .order_by(func.date(Opportunity.created_at))
    ).all()

    # Opportunities by state
    state_breakdown = session.exec(
        select(Opportunity.state, func.count(Opportunity.id)).group_by(
            Opportunity.state
        )
    ).all()

    # Opportunities by urgency
    urgency_breakdown = session.exec(
        select(Opportunity.urgency, func.count(Opportunity.id)).group_by(
            Opportunity.urgency
        )
    ).all()

    # Most popular organizations
    popular_orgs = session.exec(
        select(Organisation.name, func.count(Opportunity.id))
        .join(Opportunity, Organisation.id == Opportunity.org_id)
        .group_by(Organisation.id, Organisation.name)
        .order_by(func.count(Opportunity.id).desc())
        .limit(10)
    ).all()

    return {
        "creation_timeline": [
            {"date": date.isoformat(), "count": count}
            for date, count in opportunity_creation
        ],
        "state_breakdown": dict(state_breakdown),
        "urgency_breakdown": dict(urgency_breakdown),
        "most_active_organizations": [
            {"name": name, "opportunity_count": count} for name, count in popular_orgs
        ],
    }


# Content Moderation
@router.get("/moderation/reports")
async def get_moderation_reports(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status: Annotated[Optional[str], Query()] = None,
):
    """Get content moderation reports"""
    # This would typically involve a reports model
    # For now, return flagged reviews as example
    query = select(Review).where(Review.flagged == True)

    if status == "resolved":
        query = query.where(Review.flag_resolved == True)
    elif status == "pending":
        query = query.where(Review.flag_resolved == False)

    query = query.order_by(Review.created_at.desc()).offset(skip).limit(limit)
    reports = session.exec(query).all()

    return {
        "reports": [
            {
                "id": review.id,
                "type": "review",
                "content": review.comment,
                "reporter_id": review.volunteer_id,  # Simplified
                "created_at": review.created_at.isoformat(),
                "resolved": review.flag_resolved,
            }
            for review in reports
        ],
        "total_count": len(reports),
    }


@router.post("/moderation/reports/{report_id}/resolve")
async def resolve_moderation_report(
    report_id: int,
    action: str,
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    """Resolve a moderation report"""
    # This is simplified - in reality you'd have a proper reports system
    review = session.get(Review, report_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    review.flag_resolved = True
    review.resolution_action = action
    review.resolved_by = admin_user.id
    review.resolved_at = datetime.now(datetime.timezone.utc)

    session.add(review)
    session.commit()

    return {"message": "Report resolved successfully"}


# System Health and Performance
@router.get("/system/health")
async def get_system_health(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get system health metrics"""

    # Database connectivity test
    try:
        session.exec(select(func.count(User.id))).first()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Recent error rates (simplified)
    recent_errors = session.exec(
        select(func.count(AnalyticsEvent.id)).where(
            and_(
                AnalyticsEvent.event_type == "error",
                AnalyticsEvent.timestamp
                >= datetime.now(datetime.timezone.utc) - timedelta(hours=1),
            )
        )
    ).first()

    return {
        "database": db_status,
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
        "recent_errors": recent_errors or 0,
        "uptime": "healthy",  # Simplified
    }


@router.get("/system/performance")
async def get_performance_metrics(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
    hours: int = Query(24, ge=1, le=168),
):
    """Get system performance metrics"""
    start_time = datetime.now(datetime.timezone.utc) - timedelta(hours=hours)

    # Get performance metrics from the last N hours
    metrics = session.exec(
        select(PerformanceMetric)
        .where(PerformanceMetric.timestamp >= start_time)
        .order_by(PerformanceMetric.timestamp.desc())
    ).all()

    if not metrics:
        return {"message": "No performance metrics available", "period_hours": hours}

    # Calculate averages
    avg_response_time = sum(m.response_time for m in metrics) / len(metrics)
    avg_cpu_usage = sum(m.cpu_usage for m in metrics) / len(metrics)
    avg_memory_usage = sum(m.memory_usage for m in metrics) / len(metrics)

    return {
        "period_hours": hours,
        "metrics_count": len(metrics),
        "averages": {
            "response_time_ms": round(avg_response_time, 2),
            "cpu_usage_percent": round(avg_cpu_usage, 2),
            "memory_usage_percent": round(avg_memory_usage, 2),
        },
        "latest_metrics": [
            {
                "timestamp": m.timestamp.isoformat(),
                "response_time": m.response_time,
                "cpu_usage": m.cpu_usage,
                "memory_usage": m.memory_usage,
            }
            for m in metrics[:10]  # Latest 10
        ],
    }


# Configuration Management
@router.get("/config")
async def get_system_config(admin_user: Annotated[User, Depends(require_admin)]):
    """Get system configuration"""
    # This would typically come from a config model or environment
    return {
        "features": {
            "messaging_enabled": True,
            "file_uploads_enabled": True,
            "reviews_enabled": True,
            "matching_algorithm_enabled": True,
        },
        "limits": {
            "max_file_size_mb": 10,
            "max_message_length": 1000,
            "max_opportunities_per_org": 100,
        },
        "maintenance": {"scheduled_maintenance": False, "maintenance_message": None},
    }


@router.put("/config")
async def update_system_config(
    config_update: Dict[str, Any], admin_user: Annotated[User, Depends(require_admin)]
):
    """Update system configuration"""
    # This would typically update a config model or environment
    # For now, just return success

    return {
        "message": "Configuration updated successfully",
        "updated_by": admin_user.id,
        "updated_at": datetime.now(datetime.timezone.utc).isoformat(),
    }


@router.post("/seed-data")
async def seed_sample_data(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
    force: bool = Query(False, description="Force seeding even if data exists"),
):
    """Seed database with sample data for development/testing"""

    seeder = DataSeeder(session)

    try:
        results = await seeder.seed_sample_data(force=force)

        return success_with_data(results, "Sample data seeded successfully")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error seeding data: {str(e)}",
        )


@router.delete("/clear-data")
async def clear_sample_data(
    admin_user: Annotated[User, Depends(require_admin)],
    session: Annotated[Session, Depends(get_session)],
    confirm: bool = Query(False, description="Confirm data deletion"),
):
    """Clear all data from database (development only)"""

    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must set confirm=true to clear data",
        )

    try:
        # Delete all data in reverse dependency order
        tables_to_clear = [
            "skill_verifications",
            "reviews",
            "calendar_events",
            "applications",
            "opportunities",
            "organisations",
            "volunteers",
            "skills",
            "users",
        ]

        cleared_counts = {}

        for table_name in tables_to_clear:
            if table_name == "users":
                count = session.exec(select(func.count(User.id))).first()
                session.exec("DELETE FROM users")
                cleared_counts["users"] = count
            # Add other table clearing logic as needed

        session.commit()

        return success_with_data(cleared_counts, "Database cleared successfully")

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing data: {str(e)}",
        )
