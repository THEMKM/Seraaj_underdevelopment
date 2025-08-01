"""
Guided Tour Service for Seraaj
Manages interactive tours and user progress
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select, and_, or_

from models.guided_tour import (
    GuidedTour, TourStep, UserTourProgress, TourTemplate, TourAnalytics,
    TourFeedback, TourType, TourStatus, StepType, TourUserRole
)
from models import User
from config.settings import settings

logger = logging.getLogger(__name__)


class GuidedTourService:
    """Service for managing guided tours"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_available_tours(
        self, 
        user_id: int, 
        user_role: TourUserRole,
        current_url: Optional[str] = None,
        include_completed: bool = False
    ) -> List[Dict[str, Any]]:
        """Get tours available for a specific user"""
        
        try:
            # Get user progress to filter tours
            user_progress = self.session.exec(
                select(UserTourProgress).where(UserTourProgress.user_id == user_id)
            ).all()
            
            completed_tour_ids = [
                p.tour_id for p in user_progress 
                if p.status == TourStatus.COMPLETED
            ]
            
            # Build query for available tours
            query = select(GuidedTour).where(
                and_(
                    GuidedTour.is_active == True,
                    or_(
                        GuidedTour.target_role == user_role,
                        GuidedTour.target_role == TourUserRole.ALL
                    )
                )
            )
            
            # Exclude completed tours unless requested
            if not include_completed and completed_tour_ids:
                query = query.where(GuidedTour.id.not_in(completed_tour_ids))
            
            tours = self.session.exec(query.order_by(GuidedTour.priority.desc())).all()
            
            available_tours = []
            for tour in tours:
                # Check if user meets requirements
                if not await self._check_tour_eligibility(tour, user_id, current_url):
                    continue
                
                # Get user progress for this tour
                progress = next(
                    (p for p in user_progress if p.tour_id == tour.id), 
                    None
                )
                
                tour_data = {
                    "tour_id": tour.tour_id,
                    "title": tour.title,
                    "description": tour.description,
                    "tour_type": tour.tour_type,
                    "estimated_duration_minutes": tour.estimated_duration_minutes,
                    "is_mandatory": tour.is_mandatory,
                    "priority": tour.priority,
                    "allow_skip": tour.allow_skip,
                    "progress": {
                        "status": progress.status if progress else TourStatus.NOT_STARTED,
                        "current_step": progress.current_step if progress else None,
                        "completion_percentage": self._calculate_completion_percentage(tour, progress)
                    }
                }
                
                available_tours.append(tour_data)
            
            return available_tours
            
        except Exception as e:
            logger.error(f"Error getting available tours for user {user_id}: {e}")
            return []
    
    async def start_tour(self, user_id: int, tour_id: str) -> Dict[str, Any]:
        """Start a guided tour for a user"""
        
        try:
            # Get tour
            tour = self.session.exec(
                select(GuidedTour).where(GuidedTour.tour_id == tour_id)
            ).first()
            
            if not tour:
                raise ValueError(f"Tour {tour_id} not found")
            
            # Check if user already has progress
            progress = self.session.exec(
                select(UserTourProgress).where(
                    and_(
                        UserTourProgress.user_id == user_id,
                        UserTourProgress.tour_id == tour.id
                    )
                )
            ).first()
            
            if not progress:
                # Create new progress record
                progress = UserTourProgress(
                    user_id=user_id,
                    tour_id=tour.id,
                    status=TourStatus.IN_PROGRESS,
                    current_step=1,
                    started_at=datetime.now(datetime.timezone.utc),
                    last_accessed_at=datetime.now(datetime.timezone.utc)
                )
                self.session.add(progress)
            else:
                # Resume existing tour
                progress.status = TourStatus.IN_PROGRESS
                progress.last_accessed_at = datetime.now(datetime.timezone.utc)
            
            self.session.commit()
            self.session.refresh(progress)
            
            # Update tour analytics
            await self._track_tour_event(tour.id, "tour_started", user_id)
            
            # Get first step
            first_step = await self._get_tour_step(tour.id, progress.current_step or 1)
            
            return {
                "tour": await self._serialize_tour(tour),
                "progress": await self._serialize_progress(progress),
                "current_step": first_step,
                "total_steps": await self._get_tour_step_count(tour.id)
            }
            
        except Exception as e:
            logger.error(f"Error starting tour {tour_id} for user {user_id}: {e}")
            self.session.rollback()
            raise
    
    async def get_tour_step(self, user_id: int, tour_id: str, step_number: int) -> Dict[str, Any]:
        """Get a specific tour step"""
        
        try:
            tour = self.session.exec(
                select(GuidedTour).where(GuidedTour.tour_id == tour_id)
            ).first()
            
            if not tour:
                raise ValueError(f"Tour {tour_id} not found")
            
            step = await self._get_tour_step(tour.id, step_number)
            if not step:
                raise ValueError(f"Step {step_number} not found in tour {tour_id}")
            
            # Track step view
            await self._track_step_event(step["id"], "step_viewed", user_id)
            
            return step
            
        except Exception as e:
            logger.error(f"Error getting tour step: {e}")
            raise
    
    async def advance_tour_step(
        self, 
        user_id: int, 
        tour_id: str, 
        step_number: int,
        action: str = "next"
    ) -> Dict[str, Any]:
        """Advance user to next tour step"""
        
        try:
            tour = self.session.exec(
                select(GuidedTour).where(GuidedTour.tour_id == tour_id)
            ).first()
            
            if not tour:
                raise ValueError(f"Tour {tour_id} not found")
            
            # Get user progress
            progress = self.session.exec(
                select(UserTourProgress).where(
                    and_(
                        UserTourProgress.user_id == user_id,
                        UserTourProgress.tour_id == tour.id
                    )
                )
            ).first()
            
            if not progress:
                raise ValueError("Tour progress not found")
            
            # Track current step completion
            if action == "next" and step_number not in progress.completed_steps:
                progress.completed_steps = progress.completed_steps + [step_number]
            elif action == "skip" and step_number not in progress.skipped_steps:
                progress.skipped_steps = progress.skipped_steps + [step_number]
            
            # Calculate next step
            total_steps = await self._get_tour_step_count(tour.id)
            
            if action == "next" and step_number < total_steps:
                next_step_number = step_number + 1
                progress.current_step = next_step_number
                next_step = await self._get_tour_step(tour.id, next_step_number)
            elif action == "prev" and step_number > 1:
                prev_step_number = step_number - 1
                progress.current_step = prev_step_number
                next_step = await self._get_tour_step(tour.id, prev_step_number)
            else:
                # Tour completed or at beginning
                if step_number >= total_steps:
                    progress.status = TourStatus.COMPLETED
                    progress.completed_at = datetime.now(datetime.timezone.utc)
                    await self._track_tour_event(tour.id, "tour_completed", user_id)
                next_step = None
            
            progress.last_accessed_at = datetime.now(datetime.timezone.utc)
            self.session.add(progress)
            self.session.commit()
            
            return {
                "progress": await self._serialize_progress(progress),
                "next_step": next_step,
                "total_steps": total_steps,
                "is_completed": progress.status == TourStatus.COMPLETED
            }
            
        except Exception as e:
            logger.error(f"Error advancing tour step: {e}")
            self.session.rollback()
            raise
    
    async def skip_tour(self, user_id: int, tour_id: str) -> bool:
        """Skip/dismiss a tour"""
        
        try:
            tour = self.session.exec(
                select(GuidedTour).where(GuidedTour.tour_id == tour_id)
            ).first()
            
            if not tour:
                return False
            
            # Update or create progress
            progress = self.session.exec(
                select(UserTourProgress).where(
                    and_(
                        UserTourProgress.user_id == user_id,
                        UserTourProgress.tour_id == tour.id
                    )
                )
            ).first()
            
            if not progress:
                progress = UserTourProgress(
                    user_id=user_id,
                    tour_id=tour.id,
                    status=TourStatus.SKIPPED,
                    started_at=datetime.now(datetime.timezone.utc)
                )
            else:
                progress.status = TourStatus.SKIPPED
            
            progress.completed_at = datetime.now(datetime.timezone.utc)
            progress.last_accessed_at = datetime.now(datetime.timezone.utc)
            
            self.session.add(progress)
            self.session.commit()
            
            await self._track_tour_event(tour.id, "tour_skipped", user_id)
            return True
            
        except Exception as e:
            logger.error(f"Error skipping tour {tour_id}: {e}")
            self.session.rollback()
            return False
    
    async def submit_tour_feedback(
        self, 
        user_id: int, 
        tour_id: str, 
        rating: int,
        feedback: str,
        step_id: Optional[str] = None
    ) -> bool:
        """Submit feedback for a tour"""
        
        try:
            tour = self.session.exec(
                select(GuidedTour).where(GuidedTour.tour_id == tour_id)
            ).first()
            
            if not tour:
                return False
            
            # Update user progress with rating and feedback
            progress = self.session.exec(
                select(UserTourProgress).where(
                    and_(
                        UserTourProgress.user_id == user_id,
                        UserTourProgress.tour_id == tour.id
                    )
                )
            ).first()
            
            if progress:
                progress.rating = rating
                progress.feedback = feedback
                progress.updated_at = datetime.now(datetime.timezone.utc)
                self.session.add(progress)
            
            # Create detailed feedback record
            tour_feedback = TourFeedback(
                user_id=user_id,
                tour_id=tour.id,
                step_id=int(step_id) if step_id else None,
                feedback_type="rating",
                rating=rating,
                title="Tour Rating",
                message=feedback
            )
            
            self.session.add(tour_feedback)
            self.session.commit()
            
            logger.info(f"Tour feedback submitted: user {user_id}, tour {tour_id}, rating {rating}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting tour feedback: {e}")
            self.session.rollback()
            return False
    
    async def get_tour_analytics(self, tour_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific tour"""
        
        try:
            tour = self.session.exec(
                select(GuidedTour).where(GuidedTour.tour_id == tour_id)
            ).first()
            
            if not tour:
                raise ValueError(f"Tour {tour_id} not found")
            
            since_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)
            
            # Get user progress stats
            all_progress = self.session.exec(
                select(UserTourProgress).where(
                    and_(
                        UserTourProgress.tour_id == tour.id,
                        UserTourProgress.created_at >= since_date
                    )
                )
            ).all()
            
            # Calculate metrics
            total_users = len(all_progress)
            completed_users = len([p for p in all_progress if p.status == TourStatus.COMPLETED])
            skipped_users = len([p for p in all_progress if p.status == TourStatus.SKIPPED])
            in_progress_users = len([p for p in all_progress if p.status == TourStatus.IN_PROGRESS])
            
            completion_rate = (completed_users / total_users * 100) if total_users > 0 else 0
            skip_rate = (skipped_users / total_users * 100) if total_users > 0 else 0
            
            # Average completion time
            completed_progress = [p for p in all_progress if p.completed_at and p.started_at]
            avg_completion_time = None
            if completed_progress:
                completion_times = [
                    (p.completed_at - p.started_at).total_seconds() / 60  # minutes
                    for p in completed_progress
                ]
                avg_completion_time = sum(completion_times) / len(completion_times)
            
            # User satisfaction
            rated_progress = [p for p in all_progress if p.rating is not None]
            avg_rating = None
            if rated_progress:
                avg_rating = sum(p.rating for p in rated_progress) / len(rated_progress)
            
            return {
                "tour_id": tour_id,
                "period_days": days,
                "metrics": {
                    "total_users": total_users,
                    "completed_users": completed_users,
                    "skipped_users": skipped_users,
                    "in_progress_users": in_progress_users,
                    "completion_rate": round(completion_rate, 2),
                    "skip_rate": round(skip_rate, 2),
                    "average_completion_time_minutes": round(avg_completion_time, 2) if avg_completion_time else None,
                    "average_rating": round(avg_rating, 2) if avg_rating else None,
                    "total_ratings": len(rated_progress)
                },
                "feedback_summary": await self._get_feedback_summary(tour.id, since_date)
            }
            
        except Exception as e:
            logger.error(f"Error getting tour analytics: {e}")
            raise
    
    async def create_tour_from_template(
        self, 
        template_id: str, 
        customizations: Dict[str, Any],
        created_by: int
    ) -> str:
        """Create a new tour from a template"""
        
        try:
            template = self.session.exec(
                select(TourTemplate).where(TourTemplate.template_id == template_id)
            ).first()
            
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Create tour from template
            template_data = template.template_data
            
            tour = GuidedTour(
                title=customizations.get("title", template_data["title"]),
                description=customizations.get("description", template_data["description"]),
                tour_type=TourType(customizations.get("tour_type", template_data["tour_type"])),
                target_role=TourUserRole(customizations.get("target_role", template.target_role)),
                entry_url=customizations.get("entry_url", template_data.get("entry_url", "/")),
                estimated_duration_minutes=customizations.get("duration", template_data.get("duration", 5)),
                created_by=created_by
            )
            
            self.session.add(tour)
            self.session.commit()
            self.session.refresh(tour)
            
            # Create steps from template
            for step_data in template_data.get("steps", []):
                step = TourStep(
                    tour_id=tour.id,
                    step_number=step_data["step_number"],
                    step_type=StepType(step_data["step_type"]),
                    title=step_data["title"],
                    content=step_data["content"],
                    target_selector=step_data.get("target_selector"),
                    target_url=step_data.get("target_url"),
                    position=step_data.get("position", "bottom")
                )
                self.session.add(step)
            
            self.session.commit()
            
            # Update template usage
            template.usage_count += 1
            self.session.add(template)
            self.session.commit()
            
            logger.info(f"Created tour {tour.tour_id} from template {template_id}")
            return tour.tour_id
            
        except Exception as e:
            logger.error(f"Error creating tour from template: {e}")
            self.session.rollback()
            raise
    
    # Helper methods
    
    async def _check_tour_eligibility(
        self, 
        tour: GuidedTour, 
        user_id: int, 
        current_url: Optional[str]
    ) -> bool:
        """Check if user is eligible for a tour"""
        
        # Check trigger conditions
        if tour.trigger_conditions:
            # Implement custom trigger logic here
            # For now, return True for all active tours
            pass
        
        # Check required features
        if tour.required_features:
            # Check if user has access to required features
            # This would integrate with feature flags or user permissions
            pass
        
        # Check URL matching if specified
        if current_url and tour.entry_url and tour.entry_url != "/":
            if not current_url.endswith(tour.entry_url):
                return False
        
        return True
    
    async def _get_tour_step(self, tour_id: int, step_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific tour step"""
        
        step = self.session.exec(
            select(TourStep).where(
                and_(
                    TourStep.tour_id == tour_id,
                    TourStep.step_number == step_number
                )
            )
        ).first()
        
        if not step:
            return None
        
        return {
            "id": step.id,
            "step_id": step.step_id,
            "step_number": step.step_number,
            "step_type": step.step_type,
            "title": step.title,
            "content": step.content,
            "target_selector": step.target_selector,
            "target_url": step.target_url,
            "position": step.position,
            "offset_x": step.offset_x,
            "offset_y": step.offset_y,
            "width": step.width,
            "height": step.height,
            "auto_advance_delay": step.auto_advance_delay,
            "required_interaction": step.required_interaction,
            "image_url": step.image_url,
            "video_url": step.video_url,
            "animation_config": step.animation_config,
            "primary_button_text": step.primary_button_text,
            "primary_button_action": step.primary_button_action,
            "secondary_button_text": step.secondary_button_text,
            "secondary_button_action": step.secondary_button_action
        }
    
    async def _get_tour_step_count(self, tour_id: int) -> int:
        """Get total number of steps in a tour"""
        
        return len(self.session.exec(
            select(TourStep).where(TourStep.tour_id == tour_id)
        ).all())
    
    def _calculate_completion_percentage(
        self, 
        tour: GuidedTour, 
        progress: Optional[UserTourProgress]
    ) -> float:
        """Calculate tour completion percentage"""
        
        if not progress or not progress.completed_steps:
            return 0.0
        
        total_steps = len(self.session.exec(
            select(TourStep).where(TourStep.tour_id == tour.id)
        ).all())
        
        if total_steps == 0:
            return 0.0
        
        return (len(progress.completed_steps) / total_steps) * 100
    
    async def _serialize_tour(self, tour: GuidedTour) -> Dict[str, Any]:
        """Serialize tour for API response"""
        
        return {
            "tour_id": tour.tour_id,
            "title": tour.title,
            "description": tour.description,
            "tour_type": tour.tour_type,
            "target_role": tour.target_role,
            "estimated_duration_minutes": tour.estimated_duration_minutes,
            "is_mandatory": tour.is_mandatory,
            "allow_skip": tour.allow_skip,
            "show_progress": tour.show_progress,
            "theme": tour.theme,
            "entry_url": tour.entry_url
        }
    
    async def _serialize_progress(self, progress: UserTourProgress) -> Dict[str, Any]:
        """Serialize progress for API response"""
        
        return {
            "status": progress.status,
            "current_step": progress.current_step,
            "completed_steps": progress.completed_steps,
            "skipped_steps": progress.skipped_steps,
            "started_at": progress.started_at.isoformat() if progress.started_at else None,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            "total_time_spent": progress.total_time_spent,
            "rating": progress.rating
        }
    
    async def _track_tour_event(self, tour_id: int, event_type: str, user_id: int):
        """Track tour analytics events"""
        
        try:
            # This would integrate with your analytics system
            logger.info(f"Tour event: {event_type} for tour {tour_id} by user {user_id}")
        except Exception as e:
            logger.error(f"Error tracking tour event: {e}")
    
    async def _track_step_event(self, step_id: int, event_type: str, user_id: int):
        """Track step analytics events"""
        
        try:
            # Update step view count
            step = self.session.get(TourStep, step_id)
            if step:
                step.view_count += 1
                self.session.add(step)
                self.session.commit()
        except Exception as e:
            logger.error(f"Error tracking step event: {e}")
    
    async def _get_feedback_summary(self, tour_id: int, since_date: datetime) -> Dict[str, Any]:
        """Get feedback summary for a tour"""
        
        feedback_records = self.session.exec(
            select(TourFeedback).where(
                and_(
                    TourFeedback.tour_id == tour_id,
                    TourFeedback.created_at >= since_date
                )
            )
        ).all()
        
        return {
            "total_feedback": len(feedback_records),
            "positive_feedback": len([f for f in feedback_records if f.rating and f.rating >= 4]),
            "negative_feedback": len([f for f in feedback_records if f.rating and f.rating <= 2]),
            "common_issues": []  # Could implement text analysis here
        }


def get_guided_tour_service(session: Session) -> GuidedTourService:
    """Get guided tour service instance"""
    return GuidedTourService(session)