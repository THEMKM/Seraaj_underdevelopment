from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Annotated, Dict, Any
from datetime import datetime

from database import get_session
from models import User, Volunteer, Organisation
from routers.auth import get_current_user
from collaboration.team_manager import collaboration_manager, TeamRole, TeamPermission

router = APIRouter(prefix="/v1/collaboration", tags=["collaboration"])


@router.post("/workspaces")
async def create_team_workspace(
    workspace_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new team workspace for collaboration"""

    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can create team workspaces",
        )

    # Get organization
    organization = session.exec(
        select(Organisation).where(Organisation.user_id == current_user.id)
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found",
        )

    workspace_name = workspace_data.get("name")
    description = workspace_data.get("description", "")
    initial_members = workspace_data.get("initial_members", [])

    if not workspace_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Workspace name is required"
        )

    try:
        # Create workspace
        workspace = collaboration_manager.create_team_workspace(
            session=session,
            organization_id=organization.id,
            workspace_name=workspace_name,
            description=description,
            created_by=current_user.id,
            initial_members=initial_members,
        )

        return {
            "workspace_id": workspace["id"],
            "name": workspace["name"],
            "description": workspace["description"],
            "member_count": len(workspace["members"]),
            "channel_count": len(workspace["channels"]),
            "created_at": workspace["created_at"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating workspace: {str(e)}",
        )


@router.post("/workspaces/{workspace_id}/projects")
async def create_project(
    workspace_id: str,
    project_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new project within a workspace"""

    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can create projects",
        )

    project_name = project_data.get("name")
    if not project_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Project name is required"
        )

    try:
        # Create project
        project = collaboration_manager.create_project(
            session=session,
            workspace_id=workspace_id,
            project_data=project_data,
            created_by=current_user.id,
        )

        return {
            "project_id": project["id"],
            "name": project["name"],
            "description": project["description"],
            "status": project["status"],
            "priority": project["priority"],
            "start_date": project["start_date"],
            "end_date": project["end_date"],
            "assigned_members": project["assigned_members"],
            "milestone_count": len(project["milestones"]),
            "created_at": project["created_at"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating project: {str(e)}",
        )


@router.post("/projects/{project_id}/tasks")
async def create_task(
    project_id: str,
    task_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new task within a project"""

    task_title = task_data.get("title")
    if not task_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task title is required"
        )

    try:
        # Create task
        task = collaboration_manager.create_task(
            session=session,
            project_id=project_id,
            task_data=task_data,
            created_by=current_user.id,
        )

        return {
            "task_id": task["id"],
            "title": task["title"],
            "description": task["description"],
            "status": task["status"],
            "priority": task["priority"],
            "assigned_to": task["assigned_to"],
            "due_date": task["due_date"],
            "estimated_hours": task["estimated_hours"],
            "created_at": task["created_at"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}",
        )


@router.post("/mentorship/assign")
async def assign_mentor(
    mentorship_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Assign a mentor to a volunteer"""

    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can assign mentors",
        )

    volunteer_id = mentorship_data.get("volunteer_id")
    mentor_id = mentorship_data.get("mentor_id")
    opportunity_id = mentorship_data.get("opportunity_id")

    if not all([volunteer_id, mentor_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="volunteer_id and mentor_id are required",
        )

    try:
        # Assign mentor
        mentorship = collaboration_manager.assign_mentor(
            session=session,
            volunteer_id=volunteer_id,
            mentor_id=mentor_id,
            opportunity_id=opportunity_id,
            assigned_by=current_user.id,
        )

        return {
            "mentorship_id": mentorship["id"],
            "volunteer_id": mentorship["volunteer_id"],
            "mentor_id": mentorship["mentor_id"],
            "opportunity_id": mentorship["opportunity_id"],
            "status": mentorship["status"],
            "assigned_at": mentorship["assigned_at"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning mentor: {str(e)}",
        )


@router.post("/workspaces/{workspace_id}/channels")
async def create_team_channel(
    workspace_id: str,
    channel_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new communication channel in the workspace"""

    channel_name = channel_data.get("name")
    if not channel_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Channel name is required"
        )

    try:
        # Create channel
        channel = collaboration_manager.create_team_channel(
            session=session,
            workspace_id=workspace_id,
            channel_data=channel_data,
            created_by=current_user.id,
        )

        return {
            "channel_id": channel["id"],
            "name": channel["name"],
            "description": channel["description"],
            "type": channel["type"],
            "member_count": len(channel["members"]),
            "created_at": channel["created_at"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating channel: {str(e)}",
        )


@router.post("/volunteers/{volunteer_id}/progress")
async def track_volunteer_progress(
    volunteer_id: int,
    progress_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Track volunteer progress on an opportunity"""

    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can track volunteer progress",
        )

    opportunity_id = progress_data.get("opportunity_id")
    if not opportunity_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="opportunity_id is required"
        )

    # Verify volunteer exists
    volunteer = session.get(Volunteer, volunteer_id)
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Volunteer not found"
        )

    try:
        # Track progress
        progress_entry = collaboration_manager.track_volunteer_progress(
            session=session,
            volunteer_id=volunteer_id,
            opportunity_id=opportunity_id,
            progress_data=progress_data,
            tracked_by=current_user.id,
        )

        return {
            "progress_id": progress_entry["id"],
            "volunteer_id": progress_entry["volunteer_id"],
            "opportunity_id": progress_entry["opportunity_id"],
            "hours_completed": progress_entry["hours_completed"],
            "rating": progress_entry["rating"],
            "date": progress_entry["date"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking progress: {str(e)}",
        )


@router.post("/workspaces/{workspace_id}/reports")
async def generate_team_report(
    workspace_id: str,
    report_request: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Generate team performance and activity reports"""

    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can generate reports",
        )

    report_type = report_request.get("report_type")
    date_range = report_request.get("date_range", {})

    if not report_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="report_type is required"
        )

    # Set default date range if not provided
    if not date_range:
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=30)
        date_range = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

    try:
        # Generate report
        report = collaboration_manager.generate_team_report(
            session=session,
            workspace_id=workspace_id,
            report_type=report_type,
            date_range=date_range,
            generated_by=current_user.id,
        )

        return {
            "report_id": report["id"],
            "report_type": report["report_type"],
            "date_range": report["date_range"],
            "generated_at": report["generated_at"],
            "data": report,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}",
        )


@router.post("/workspaces/{workspace_id}/meetings")
async def schedule_team_meeting(
    workspace_id: str,
    meeting_data: Dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Schedule a team meeting or standup"""

    meeting_title = meeting_data.get("title")
    start_time = meeting_data.get("start_time")

    if not all([meeting_title, start_time]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="title and start_time are required",
        )

    try:
        # Schedule meeting
        meeting = collaboration_manager.schedule_team_meeting(
            session=session,
            workspace_id=workspace_id,
            meeting_data=meeting_data,
            scheduled_by=current_user.id,
        )

        return {
            "meeting_id": meeting["id"],
            "title": meeting["title"],
            "type": meeting["type"],
            "start_time": meeting["start_time"],
            "duration_minutes": meeting["duration_minutes"],
            "attendee_count": len(meeting["attendees"]),
            "location": meeting["location"],
            "status": meeting["status"],
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling meeting: {str(e)}",
        )


@router.get("/workspaces/{workspace_id}/dashboard")
async def get_team_dashboard(
    workspace_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get comprehensive team dashboard data"""

    try:
        # Get dashboard data
        dashboard = collaboration_manager.get_team_dashboard(
            session=session, workspace_id=workspace_id, user_id=current_user.id
        )

        return dashboard

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard: {str(e)}",
        )


@router.get("/workspaces/{workspace_id}/analytics")
async def get_collaboration_analytics(
    workspace_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    metric_type: str = Query(
        "engagement", regex="^(engagement|productivity|communication)$"
    ),
    time_period: str = Query("30_days", regex="^(7_days|30_days|90_days)$"),
):
    """Get detailed collaboration analytics"""

    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can view analytics",
        )

    try:
        # Get analytics data
        analytics = collaboration_manager.get_collaboration_analytics(
            session=session,
            workspace_id=workspace_id,
            metric_type=metric_type,
            time_period=time_period,
        )

        return {
            "workspace_id": workspace_id,
            "metric_type": metric_type,
            "time_period": time_period,
            "analytics": analytics,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}",
        )


@router.get("/roles")
async def get_team_roles(current_user: Annotated[User, Depends(get_current_user)]):
    """Get available team roles and their permissions"""

    roles_info = []

    for role in TeamRole:
        permissions = collaboration_manager.role_permissions.get(role, [])
        roles_info.append(
            {
                "role": role.value,
                "permissions": [p.value for p in permissions],
                "permission_count": len(permissions),
            }
        )

    return {
        "roles": roles_info,
        "total_roles": len(roles_info),
        "available_permissions": [p.value for p in TeamPermission],
    }


@router.get("/project-templates")
async def get_project_templates(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get project templates for quick project creation"""

    templates = [
        {
            "id": "community_cleanup",
            "name": "Community Cleanup Initiative",
            "description": "Organize community cleaning and beautification projects",
            "default_duration_days": 30,
            "typical_volunteer_count": 25,
            "default_tasks": [
                {
                    "title": "Site survey and planning",
                    "priority": "high",
                    "estimated_hours": 8,
                },
                {
                    "title": "Volunteer recruitment",
                    "priority": "high",
                    "estimated_hours": 12,
                },
                {
                    "title": "Equipment and supplies procurement",
                    "priority": "medium",
                    "estimated_hours": 6,
                },
                {
                    "title": "Safety briefing preparation",
                    "priority": "high",
                    "estimated_hours": 4,
                },
                {"title": "Event execution", "priority": "high", "estimated_hours": 40},
                {
                    "title": "Impact assessment",
                    "priority": "medium",
                    "estimated_hours": 6,
                },
            ],
            "default_milestones": [
                {"name": "Planning Complete", "target_days": 7},
                {"name": "Volunteers Recruited", "target_days": 14},
                {"name": "Event Day", "target_days": 21},
                {"name": "Impact Report", "target_days": 30},
            ],
        },
        {
            "id": "education_support",
            "name": "Education Support Program",
            "description": "Provide tutoring and educational support to students",
            "default_duration_days": 90,
            "typical_volunteer_count": 15,
            "default_tasks": [
                {
                    "title": "Curriculum assessment",
                    "priority": "high",
                    "estimated_hours": 10,
                },
                {
                    "title": "Tutor recruitment and training",
                    "priority": "high",
                    "estimated_hours": 20,
                },
                {
                    "title": "Student matching",
                    "priority": "medium",
                    "estimated_hours": 8,
                },
                {
                    "title": "Progress tracking setup",
                    "priority": "medium",
                    "estimated_hours": 6,
                },
                {
                    "title": "Weekly tutoring sessions",
                    "priority": "high",
                    "estimated_hours": 180,
                },
                {
                    "title": "Progress evaluation",
                    "priority": "medium",
                    "estimated_hours": 12,
                },
            ],
        },
        {
            "id": "senior_care",
            "name": "Senior Care Assistance",
            "description": "Provide companionship and assistance to elderly community members",
            "default_duration_days": 180,
            "typical_volunteer_count": 20,
            "default_tasks": [
                {
                    "title": "Volunteer screening and background checks",
                    "priority": "high",
                    "estimated_hours": 16,
                },
                {
                    "title": "Senior needs assessment",
                    "priority": "high",
                    "estimated_hours": 12,
                },
                {
                    "title": "Training program development",
                    "priority": "medium",
                    "estimated_hours": 20,
                },
                {
                    "title": "Volunteer-senior matching",
                    "priority": "high",
                    "estimated_hours": 10,
                },
                {
                    "title": "Regular visit coordination",
                    "priority": "high",
                    "estimated_hours": 240,
                },
            ],
        },
    ]

    return {"templates": templates, "total_templates": len(templates)}


from datetime import timedelta
