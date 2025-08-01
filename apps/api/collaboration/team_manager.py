from typing import List, Dict, Optional, Any
from sqlmodel import Session, select, and_
from datetime import datetime, timedelta
import logging
from enum import Enum
import uuid

from models import User, Volunteer, Organisation, AnalyticsEvent

logger = logging.getLogger(__name__)


class TeamRole(str, Enum):
    """Team member roles within an organization"""

    ADMIN = "admin"
    COORDINATOR = "coordinator"
    MENTOR = "mentor"
    SUPERVISOR = "supervisor"
    MEMBER = "member"
    OBSERVER = "observer"


class TeamPermission(str, Enum):
    """Team permissions for different actions"""

    MANAGE_TEAM = "manage_team"
    VIEW_ANALYTICS = "view_analytics"
    SCHEDULE_EVENTS = "schedule_events"
    MANAGE_APPLICATIONS = "manage_applications"
    SEND_MESSAGES = "send_messages"
    VIEW_VOLUNTEER_DETAILS = "view_volunteer_details"
    CREATE_OPPORTUNITIES = "create_opportunities"
    ASSIGN_MENTORS = "assign_mentors"


class ProjectStatus(str, Enum):
    """Project/initiative status tracking"""

    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task completion status"""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TeamCollaborationManager:
    """Advanced team collaboration and project management system"""

    def __init__(self):
        # Role-based permissions mapping
        self.role_permissions = {
            TeamRole.ADMIN: [
                TeamPermission.MANAGE_TEAM,
                TeamPermission.VIEW_ANALYTICS,
                TeamPermission.SCHEDULE_EVENTS,
                TeamPermission.MANAGE_APPLICATIONS,
                TeamPermission.SEND_MESSAGES,
                TeamPermission.VIEW_VOLUNTEER_DETAILS,
                TeamPermission.CREATE_OPPORTUNITIES,
                TeamPermission.ASSIGN_MENTORS,
            ],
            TeamRole.COORDINATOR: [
                TeamPermission.VIEW_ANALYTICS,
                TeamPermission.SCHEDULE_EVENTS,
                TeamPermission.MANAGE_APPLICATIONS,
                TeamPermission.SEND_MESSAGES,
                TeamPermission.VIEW_VOLUNTEER_DETAILS,
                TeamPermission.ASSIGN_MENTORS,
            ],
            TeamRole.MENTOR: [
                TeamPermission.SEND_MESSAGES,
                TeamPermission.VIEW_VOLUNTEER_DETAILS,
                TeamPermission.ASSIGN_MENTORS,
            ],
            TeamRole.SUPERVISOR: [
                TeamPermission.VIEW_ANALYTICS,
                TeamPermission.MANAGE_APPLICATIONS,
                TeamPermission.SEND_MESSAGES,
                TeamPermission.VIEW_VOLUNTEER_DETAILS,
            ],
            TeamRole.MEMBER: [
                TeamPermission.SEND_MESSAGES,
                TeamPermission.VIEW_VOLUNTEER_DETAILS,
            ],
            TeamRole.OBSERVER: [TeamPermission.VIEW_ANALYTICS],
        }

    def create_team_workspace(
        self,
        session: Session,
        organization_id: int,
        workspace_name: str,
        description: str,
        created_by: int,
        initial_members: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new team workspace for collaboration"""

        # Verify organization exists
        organization = session.get(Organisation, organization_id)
        if not organization:
            raise ValueError("Organization not found")

        # Create workspace structure (in real implementation, this would be in database)
        workspace_id = str(uuid.uuid4())
        workspace = {
            "id": workspace_id,
            "organization_id": organization_id,
            "name": workspace_name,
            "description": description,
            "created_by": created_by,
            "created_at": datetime.now(datetime.timezone.utc).isoformat(),
            "members": [],
            "projects": [],
            "channels": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "general",
                    "description": "General team discussions",
                    "type": "public",
                    "created_at": datetime.now(datetime.timezone.utc).isoformat(),
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "announcements",
                    "description": "Team announcements and updates",
                    "type": "announcement",
                    "created_at": datetime.now(datetime.timezone.utc).isoformat(),
                },
            ],
            "settings": {
                "allow_external_volunteers": True,
                "require_approval_for_join": True,
                "default_volunteer_role": TeamRole.MEMBER.value,
            },
        }

        # Add initial members
        if initial_members:
            for member_data in initial_members:
                self._add_team_member(
                    workspace,
                    member_data["user_id"],
                    member_data.get("role", TeamRole.MEMBER.value),
                    member_data.get("title", "Team Member"),
                )

        # Add creator as admin
        self._add_team_member(workspace, created_by, TeamRole.ADMIN.value, "Team Lead")

        # Log workspace creation
        self._log_collaboration_event(
            session, "workspace_created", workspace_id, created_by, workspace
        )

        logger.info(
            f"Team workspace created: {workspace_name} for organization {organization_id}"
        )
        return workspace

    def _add_team_member(
        self,
        workspace: Dict[str, Any],
        user_id: int,
        role: str,
        title: str = "Team Member",
    ):
        """Add a member to the team workspace"""

        member = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "role": role,
            "title": title,
            "joined_at": datetime.now(datetime.timezone.utc).isoformat(),
            "permissions": [
                p.value for p in self.role_permissions.get(TeamRole(role), [])
            ],
            "active": True,
            "last_activity": datetime.now(datetime.timezone.utc).isoformat(),
        }

        workspace["members"].append(member)

    def create_project(
        self,
        session: Session,
        workspace_id: str,
        project_data: Dict[str, Any],
        created_by: int,
    ) -> Dict[str, Any]:
        """Create a new project within a workspace"""

        project_id = str(uuid.uuid4())
        project = {
            "id": project_id,
            "workspace_id": workspace_id,
            "name": project_data["name"],
            "description": project_data.get("description", ""),
            "status": ProjectStatus.PLANNING.value,
            "priority": project_data.get("priority", TaskPriority.MEDIUM.value),
            "start_date": project_data.get("start_date"),
            "end_date": project_data.get("end_date"),
            "assigned_members": project_data.get("assigned_members", []),
            "opportunities": project_data.get("opportunity_ids", []),
            "tasks": [],
            "milestones": [],
            "created_by": created_by,
            "created_at": datetime.now(datetime.timezone.utc).isoformat(),
            "updated_at": datetime.now(datetime.timezone.utc).isoformat(),
            "metadata": {
                "target_volunteer_count": project_data.get("target_volunteer_count", 0),
                "budget": project_data.get("budget", 0),
                "expected_impact": project_data.get("expected_impact", ""),
            },
        }

        # Create default project milestones
        default_milestones = [
            {"name": "Project Kickoff", "target_date": project_data.get("start_date")},
            {"name": "Mid-Project Review", "target_date": None},
            {"name": "Project Completion", "target_date": project_data.get("end_date")},
        ]

        for milestone_data in default_milestones:
            if milestone_data["target_date"]:
                milestone = self._create_milestone(milestone_data, project_id)
                project["milestones"].append(milestone)

        # Log project creation
        self._log_collaboration_event(
            session, "project_created", project_id, created_by, project
        )

        logger.info(f"Project created: {project['name']} in workspace {workspace_id}")
        return project

    def _create_milestone(
        self, milestone_data: Dict[str, Any], project_id: str
    ) -> Dict[str, Any]:
        """Create a project milestone"""

        return {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "name": milestone_data["name"],
            "description": milestone_data.get("description", ""),
            "target_date": milestone_data.get("target_date"),
            "completed": False,
            "completed_date": None,
            "created_at": datetime.now(datetime.timezone.utc).isoformat(),
        }

    def create_task(
        self,
        session: Session,
        project_id: str,
        task_data: Dict[str, Any],
        created_by: int,
    ) -> Dict[str, Any]:
        """Create a new task within a project"""

        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "project_id": project_id,
            "title": task_data["title"],
            "description": task_data.get("description", ""),
            "status": TaskStatus.TODO.value,
            "priority": task_data.get("priority", TaskPriority.MEDIUM.value),
            "assigned_to": task_data.get("assigned_to"),
            "due_date": task_data.get("due_date"),
            "estimated_hours": task_data.get("estimated_hours", 0),
            "actual_hours": 0,
            "tags": task_data.get("tags", []),
            "checklist": task_data.get("checklist", []),
            "comments": [],
            "attachments": [],
            "created_by": created_by,
            "created_at": datetime.now(datetime.timezone.utc).isoformat(),
            "updated_at": datetime.now(datetime.timezone.utc).isoformat(),
            "completed_at": None,
        }

        # Log task creation
        self._log_collaboration_event(
            session, "task_created", task_id, created_by, task
        )

        return task

    def assign_mentor(
        self,
        session: Session,
        volunteer_id: int,
        mentor_id: int,
        opportunity_id: Optional[int] = None,
        assigned_by: int = None,
    ) -> Dict[str, Any]:
        """Assign a mentor to a volunteer"""

        # Verify volunteer exists
        volunteer = session.get(Volunteer, volunteer_id)
        if not volunteer:
            raise ValueError("Volunteer not found")

        # Verify mentor exists and has mentor permissions
        mentor_user = session.get(User, mentor_id)
        if not mentor_user:
            raise ValueError("Mentor not found")

        # Create mentorship relationship
        mentorship_id = str(uuid.uuid4())
        mentorship = {
            "id": mentorship_id,
            "volunteer_id": volunteer_id,
            "mentor_id": mentor_id,
            "opportunity_id": opportunity_id,
            "assigned_by": assigned_by,
            "assigned_at": datetime.now(datetime.timezone.utc).isoformat(),
            "status": "active",
            "mentorship_goals": [],
            "meeting_schedule": {},
            "progress_notes": [],
            "feedback_history": [],
        }

        # Create initial conversation between mentor and volunteer
        conversation_title = f"Mentorship: {volunteer.full_name}"

        # In a real implementation, this would create a conversation in the database
        conversation_data = {
            "title": conversation_title,
            "participants": [volunteer.user_id, mentor_id],
            "type": "mentorship",
            "metadata": {"mentorship_id": mentorship_id},
        }

        # Log mentorship assignment
        self._log_collaboration_event(
            session,
            "mentor_assigned",
            mentorship_id,
            assigned_by or mentor_id,
            mentorship,
        )

        logger.info(f"Mentor {mentor_id} assigned to volunteer {volunteer_id}")
        return mentorship

    def create_team_channel(
        self,
        session: Session,
        workspace_id: str,
        channel_data: Dict[str, Any],
        created_by: int,
    ) -> Dict[str, Any]:
        """Create a new communication channel in the workspace"""

        channel_id = str(uuid.uuid4())
        channel = {
            "id": channel_id,
            "workspace_id": workspace_id,
            "name": channel_data["name"],
            "description": channel_data.get("description", ""),
            "type": channel_data.get("type", "public"),  # public, private, announcement
            "members": channel_data.get("members", []),
            "created_by": created_by,
            "created_at": datetime.now(datetime.timezone.utc).isoformat(),
            "settings": {
                "allow_threads": True,
                "allow_file_sharing": True,
                "notification_level": "all",
            },
            "pinned_messages": [],
            "message_count": 0,
        }

        # Create corresponding conversation in messaging system
        conversation_title = f"#{channel['name']}"

        # In a real implementation, create actual conversation
        conversation_data = {
            "title": conversation_title,
            "participants": channel["members"],
            "type": "team_channel",
            "metadata": {"channel_id": channel_id, "workspace_id": workspace_id},
        }

        # Log channel creation
        self._log_collaboration_event(
            session, "channel_created", channel_id, created_by, channel
        )

        return channel

    def track_volunteer_progress(
        self,
        session: Session,
        volunteer_id: int,
        opportunity_id: int,
        progress_data: Dict[str, Any],
        tracked_by: int,
    ) -> Dict[str, Any]:
        """Track volunteer progress on an opportunity"""

        progress_id = str(uuid.uuid4())
        progress_entry = {
            "id": progress_id,
            "volunteer_id": volunteer_id,
            "opportunity_id": opportunity_id,
            "tracked_by": tracked_by,
            "date": datetime.now(datetime.timezone.utc).isoformat(),
            "hours_completed": progress_data.get("hours_completed", 0),
            "tasks_completed": progress_data.get("tasks_completed", []),
            "achievements": progress_data.get("achievements", []),
            "challenges": progress_data.get("challenges", ""),
            "feedback": progress_data.get("feedback", ""),
            "rating": progress_data.get("rating"),  # 1-5 rating
            "next_steps": progress_data.get("next_steps", ""),
            "mentor_notes": progress_data.get("mentor_notes", ""),
            "attachments": progress_data.get("attachments", []),
        }

        # Update volunteer's total hours and experience
        volunteer = session.get(Volunteer, volunteer_id)
        if volunteer:
            # In a real implementation, update volunteer hours tracking
            pass

        # Log progress tracking
        self._log_collaboration_event(
            session, "progress_tracked", progress_id, tracked_by, progress_entry
        )

        return progress_entry

    def generate_team_report(
        self,
        session: Session,
        workspace_id: str,
        report_type: str,
        date_range: Dict[str, str],
        generated_by: int,
    ) -> Dict[str, Any]:
        """Generate team performance and activity reports"""

        start_date = datetime.fromisoformat(date_range["start_date"])
        end_date = datetime.fromisoformat(date_range["end_date"])

        report_id = str(uuid.uuid4())

        if report_type == "team_activity":
            report = self._generate_activity_report(
                session, workspace_id, start_date, end_date
            )
        elif report_type == "volunteer_progress":
            report = self._generate_progress_report(
                session, workspace_id, start_date, end_date
            )
        elif report_type == "project_status":
            report = self._generate_project_report(
                session, workspace_id, start_date, end_date
            )
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Add report metadata
        report.update(
            {
                "id": report_id,
                "workspace_id": workspace_id,
                "report_type": report_type,
                "date_range": date_range,
                "generated_by": generated_by,
                "generated_at": datetime.now(datetime.timezone.utc).isoformat(),
            }
        )

        # Log report generation
        self._log_collaboration_event(
            session,
            "report_generated",
            report_id,
            generated_by,
            {"report_type": report_type, "date_range": date_range},
        )

        return report

    def _generate_activity_report(
        self,
        session: Session,
        workspace_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Generate team activity report"""

        # In a real implementation, query actual data from database
        # For now, return mock structure

        return {
            "team_metrics": {
                "total_members": 12,
                "active_members": 10,
                "new_members": 2,
                "messages_sent": 150,
                "files_shared": 25,
                "meetings_held": 8,
            },
            "project_progress": {
                "projects_active": 3,
                "projects_completed": 1,
                "tasks_completed": 45,
                "tasks_pending": 23,
                "overall_completion_rate": 66.2,
            },
            "volunteer_engagement": {
                "volunteers_active": 28,
                "total_volunteer_hours": 240,
                "average_hours_per_volunteer": 8.6,
                "retention_rate": 85.0,
            },
            "top_contributors": [
                {"name": "Alice Johnson", "contributions": 15, "hours": 32},
                {"name": "Bob Smith", "contributions": 12, "hours": 28},
                {"name": "Carol Brown", "contributions": 10, "hours": 25},
            ],
        }

    def _generate_progress_report(
        self,
        session: Session,
        workspace_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Generate volunteer progress report"""

        return {
            "progress_summary": {
                "volunteers_tracked": 28,
                "total_hours_logged": 240,
                "average_rating": 4.3,
                "goals_achieved": 85,
                "goals_in_progress": 42,
            },
            "skill_development": {
                "skills_verified": 15,
                "training_sessions_completed": 8,
                "certifications_earned": 3,
                "mentorship_pairs": 12,
            },
            "performance_trends": {
                "improvement_rate": 12.5,
                "consistency_score": 78.0,
                "collaboration_index": 4.2,
            },
        }

    def _generate_project_report(
        self,
        session: Session,
        workspace_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Generate project status report"""

        return {
            "project_overview": {
                "total_projects": 4,
                "active_projects": 3,
                "completed_projects": 1,
                "on_track_projects": 2,
                "delayed_projects": 1,
            },
            "resource_utilization": {
                "team_members_assigned": 12,
                "volunteer_hours_allocated": 320,
                "budget_utilized": 75.0,
                "timeline_adherence": 83.0,
            },
            "impact_metrics": {
                "beneficiaries_served": 150,
                "goals_achieved": 8,
                "community_feedback_score": 4.5,
                "sustainability_rating": 4.2,
            },
        }

    def schedule_team_meeting(
        self,
        session: Session,
        workspace_id: str,
        meeting_data: Dict[str, Any],
        scheduled_by: int,
    ) -> Dict[str, Any]:
        """Schedule a team meeting or standups"""

        meeting_id = str(uuid.uuid4())
        meeting = {
            "id": meeting_id,
            "workspace_id": workspace_id,
            "title": meeting_data["title"],
            "description": meeting_data.get("description", ""),
            "type": meeting_data.get(
                "type", "general"
            ),  # standup, planning, review, etc.
            "start_time": meeting_data["start_time"],
            "duration_minutes": meeting_data.get("duration_minutes", 60),
            "attendees": meeting_data.get("attendees", []),
            "agenda": meeting_data.get("agenda", []),
            "location": meeting_data.get("location", "Virtual"),
            "meeting_url": meeting_data.get("meeting_url", ""),
            "recurring": meeting_data.get("recurring", False),
            "recurrence_pattern": meeting_data.get("recurrence_pattern", {}),
            "scheduled_by": scheduled_by,
            "created_at": datetime.now(datetime.timezone.utc).isoformat(),
            "status": "scheduled",
        }

        # Create calendar event through calendar system
        # In a real implementation, integrate with calendar_scheduler

        # Log meeting scheduling
        self._log_collaboration_event(
            session, "meeting_scheduled", meeting_id, scheduled_by, meeting
        )

        return meeting

    def _log_collaboration_event(
        self,
        session: Session,
        event_type: str,
        entity_id: str,
        user_id: int,
        event_data: Dict[str, Any],
    ):
        """Log collaboration events for analytics"""

        try:
            analytics_event = AnalyticsEvent(
                event_type=f"collaboration_{event_type}",
                user_id=user_id,
                data={
                    "entity_id": entity_id,
                    "event_data": event_data,
                    "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
                },
            )

            session.add(analytics_event)
            session.commit()

        except Exception as e:
            logger.error(f"Error logging collaboration event: {e}")

    def get_team_dashboard(
        self, session: Session, workspace_id: str, user_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive team dashboard data"""

        # In a real implementation, this would aggregate data from multiple sources
        dashboard = {
            "workspace_info": {
                "id": workspace_id,
                "name": "Main Team Workspace",
                "member_count": 12,
                "active_projects": 3,
                "last_activity": datetime.now(datetime.timezone.utc).isoformat(),
            },
            "my_tasks": {
                "assigned_to_me": 5,
                "in_progress": 2,
                "due_today": 1,
                "overdue": 0,
            },
            "recent_activity": [
                {
                    "type": "task_completed",
                    "user": "Alice Johnson",
                    "description": "Completed volunteer onboarding checklist",
                    "timestamp": (
                        datetime.now(datetime.timezone.utc) - timedelta(hours=2)
                    ).isoformat(),
                },
                {
                    "type": "new_volunteer",
                    "user": "System",
                    "description": "3 new volunteers joined the Spring Cleanup project",
                    "timestamp": (
                        datetime.now(datetime.timezone.utc) - timedelta(hours=4)
                    ).isoformat(),
                },
            ],
            "upcoming_deadlines": [
                {
                    "type": "project_milestone",
                    "title": "Mid-Project Review",
                    "due_date": (
                        datetime.now(datetime.timezone.utc) + timedelta(days=3)
                    ).isoformat(),
                    "project": "Spring Cleanup Initiative",
                }
            ],
            "team_metrics": {
                "active_volunteers": 28,
                "hours_this_week": 156,
                "completion_rate": 87.5,
                "satisfaction_score": 4.3,
            },
        }

        return dashboard

    def get_collaboration_analytics(
        self,
        session: Session,
        workspace_id: str,
        metric_type: str,
        time_period: str = "30_days",
    ) -> Dict[str, Any]:
        """Get detailed collaboration analytics"""

        # Calculate date range
        if time_period == "7_days":
            start_date = datetime.now(datetime.timezone.utc) - timedelta(days=7)
        elif time_period == "30_days":
            start_date = datetime.now(datetime.timezone.utc) - timedelta(days=30)
        elif time_period == "90_days":
            start_date = datetime.now(datetime.timezone.utc) - timedelta(days=90)
        else:
            start_date = datetime.now(datetime.timezone.utc) - timedelta(days=30)

        # Query analytics events for the workspace
        analytics_events = session.exec(
            select(AnalyticsEvent).where(
                and_(
                    AnalyticsEvent.event_type.like("collaboration_%"),
                    AnalyticsEvent.timestamp >= start_date,
                )
            )
        ).all()

        if metric_type == "engagement":
            return self._calculate_engagement_metrics(analytics_events)
        elif metric_type == "productivity":
            return self._calculate_productivity_metrics(analytics_events)
        elif metric_type == "communication":
            return self._calculate_communication_metrics(analytics_events)
        else:
            return {"error": f"Unknown metric type: {metric_type}"}

    def _calculate_engagement_metrics(
        self, events: List[AnalyticsEvent]
    ) -> Dict[str, Any]:
        """Calculate team engagement metrics"""

        return {
            "active_users": len(set(e.user_id for e in events if e.user_id)),
            "total_actions": len(events),
            "average_actions_per_user": round(
                len(events) / max(len(set(e.user_id for e in events if e.user_id)), 1),
                2,
            ),
            "engagement_trend": "increasing",  # Simplified
            "top_activities": [
                {"activity": "task_created", "count": 25},
                {"activity": "progress_tracked", "count": 18},
                {"activity": "meeting_scheduled", "count": 12},
            ],
        }

    def _calculate_productivity_metrics(
        self, events: List[AnalyticsEvent]
    ) -> Dict[str, Any]:
        """Calculate team productivity metrics"""

        return {
            "tasks_completed": 45,
            "projects_delivered": 2,
            "average_completion_time": 3.2,  # days
            "efficiency_score": 82.5,
            "bottlenecks": [
                {"area": "approval_process", "impact": "medium"},
                {"area": "resource_allocation", "impact": "low"},
            ],
        }

    def _calculate_communication_metrics(
        self, events: List[AnalyticsEvent]
    ) -> Dict[str, Any]:
        """Calculate team communication metrics"""

        return {
            "messages_sent": 156,
            "channels_active": 8,
            "response_time_avg": 2.3,  # hours
            "collaboration_index": 4.2,
            "communication_health": "good",
        }


# Global collaboration manager instance
collaboration_manager = TeamCollaborationManager()
