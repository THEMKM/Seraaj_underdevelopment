"""
Demo Scenario Service for Seraaj
Manages demo scenarios, execution, and analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select, and_
from fastapi import Depends

from models.demo_scenario import (
    DemoScenario,
    DemoStep,
    DemoRun,
    DemoTemplate,
    DemoFeedback,
    ScenarioType,
    ScenarioStatus,
    ActionType,
    DemoUserType,
)
from database import get_session

logger = logging.getLogger(__name__)


class DemoScenarioService:
    """Service for managing demo scenarios"""

    def __init__(self, session: Session):
        self.session = session
        self.demo_users = {}  # Cache for demo user sessions

    async def get_available_scenarios(
        self,
        scenario_type: Optional[ScenarioType] = None,
        target_audience: Optional[str] = None,
        difficulty_level: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available demo scenarios"""

        try:
            query = select(DemoScenario).where(
                DemoScenario.status == ScenarioStatus.ACTIVE
            )

            if scenario_type:
                query = query.where(DemoScenario.scenario_type == scenario_type)

            if target_audience:
                query = query.where(DemoScenario.target_audience == target_audience)

            if difficulty_level:
                query = query.where(DemoScenario.difficulty_level == difficulty_level)

            scenarios = self.session.exec(
                query.order_by(DemoScenario.total_runs.desc())
            ).all()

            scenario_list = []
            for scenario in scenarios:
                scenario_data = {
                    "scenario_id": scenario.scenario_id,
                    "name": scenario.name,
                    "description": scenario.description,
                    "scenario_type": scenario.scenario_type,
                    "target_audience": scenario.target_audience,
                    "duration_minutes": scenario.duration_minutes,
                    "difficulty_level": scenario.difficulty_level,
                    "total_runs": scenario.total_runs,
                    "success_rate": round(scenario.success_rate, 2),
                    "auto_play": scenario.auto_play,
                    "show_annotations": scenario.show_annotations,
                    "step_count": len(scenario.steps),
                }
                scenario_list.append(scenario_data)

            return scenario_list

        except Exception as e:
            logger.error(f"Error getting available scenarios: {e}")
            return []

    async def start_demo_scenario(
        self,
        scenario_id: str,
        session_id: str,
        runner_id: Optional[int] = None,
        environment_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Start a demo scenario execution"""

        try:
            # Get scenario
            scenario = self.session.exec(
                select(DemoScenario).where(DemoScenario.scenario_id == scenario_id)
            ).first()

            if not scenario:
                raise ValueError(f"Scenario {scenario_id} not found")

            if scenario.status != ScenarioStatus.ACTIVE:
                raise ValueError(f"Scenario {scenario_id} is not active")

            # Reset demo data if required
            if scenario.reset_data:
                await self._reset_demo_data(scenario)

            # Create demo run record
            demo_run = DemoRun(
                scenario_id=scenario.id,
                runner_id=runner_id,
                session_id=session_id,
                status="running",
                current_step=1,
                browser=environment_info.get("browser") if environment_info else None,
                device_type=(
                    environment_info.get("device_type") if environment_info else None
                ),
                screen_resolution=(
                    environment_info.get("screen_resolution")
                    if environment_info
                    else None
                ),
                user_agent=(
                    environment_info.get("user_agent") if environment_info else None
                ),
            )

            self.session.add(demo_run)
            self.session.commit()
            self.session.refresh(demo_run)

            # Get first step
            first_step = await self._get_scenario_step(scenario.id, 1)

            # Update scenario analytics
            scenario.total_runs += 1
            self.session.add(scenario)
            self.session.commit()

            return {
                "run_id": demo_run.run_id,
                "scenario": await self._serialize_scenario(scenario),
                "current_step": first_step,
                "total_steps": len(scenario.steps),
                "demo_config": {
                    "auto_play": scenario.auto_play,
                    "show_annotations": scenario.show_annotations,
                    "show_metrics": scenario.show_metrics,
                    "base_url": scenario.base_url,
                },
            }

        except Exception as e:
            logger.error(f"Error starting demo scenario {scenario_id}: {e}")
            raise

    async def execute_demo_step(
        self,
        run_id: str,
        step_number: int,
        execution_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a specific demo step"""

        try:
            # Get demo run
            demo_run = self.session.exec(
                select(DemoRun).where(DemoRun.run_id == run_id)
            ).first()

            if not demo_run:
                raise ValueError(f"Demo run {run_id} not found")

            # Get step
            step = await self._get_scenario_step(demo_run.scenario_id, step_number)
            if not step:
                raise ValueError(f"Step {step_number} not found")

            # Execute step based on action type
            step_result = await self._execute_step_action(step, execution_context)

            # Update run progress
            if step_result["success"]:
                if step_number not in demo_run.completed_steps:
                    demo_run.completed_steps = demo_run.completed_steps + [step_number]
                demo_run.current_step = step_number + 1
            else:
                if step_number not in demo_run.failed_steps:
                    demo_run.failed_steps = demo_run.failed_steps + [step_number]

            demo_run.updated_at = datetime.now(datetime.timezone.utc)
            self.session.add(demo_run)
            self.session.commit()

            # Check if scenario is complete
            total_steps = len(
                self.session.exec(
                    select(DemoStep).where(DemoStep.scenario_id == demo_run.scenario_id)
                ).all()
            )

            is_complete = len(demo_run.completed_steps) >= total_steps
            if is_complete:
                await self._complete_demo_run(demo_run)

            # Get next step
            next_step = None
            if not is_complete and step_result["success"]:
                next_step = await self._get_scenario_step(
                    demo_run.scenario_id, step_number + 1
                )

            return {
                "step_result": step_result,
                "next_step": next_step,
                "is_complete": is_complete,
                "progress": {
                    "current_step": demo_run.current_step,
                    "completed_steps": demo_run.completed_steps,
                    "failed_steps": demo_run.failed_steps,
                    "completion_percentage": (
                        len(demo_run.completed_steps) / total_steps
                    )
                    * 100,
                },
            }

        except Exception as e:
            logger.error(f"Error executing demo step: {e}")
            raise

    async def abort_demo_run(self, run_id: str, reason: str = "user_cancelled") -> bool:
        """Abort a running demo scenario"""

        try:
            demo_run = self.session.exec(
                select(DemoRun).where(DemoRun.run_id == run_id)
            ).first()

            if not demo_run:
                return False

            demo_run.status = "aborted"
            demo_run.completed_at = datetime.now(datetime.timezone.utc)
            demo_run.error_logs = demo_run.error_logs + [
                {
                    "type": "abort",
                    "reason": reason,
                    "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
                }
            ]

            if demo_run.started_at:
                demo_run.total_duration_seconds = int(
                    (
                        datetime.now(datetime.timezone.utc) - demo_run.started_at
                    ).total_seconds()
                )

            self.session.add(demo_run)
            self.session.commit()

            logger.info(f"Demo run {run_id} aborted: {reason}")
            return True

        except Exception as e:
            logger.error(f"Error aborting demo run {run_id}: {e}")
            return False

    async def submit_demo_feedback(
        self,
        scenario_id: str,
        run_id: Optional[str],
        feedback_data: Dict[str, Any],
        user_id: Optional[int] = None,
    ) -> bool:
        """Submit feedback for a demo scenario"""

        try:
            scenario = self.session.exec(
                select(DemoScenario).where(DemoScenario.scenario_id == scenario_id)
            ).first()

            if not scenario:
                return False

            run_record = None
            if run_id:
                run_record = self.session.exec(
                    select(DemoRun).where(DemoRun.run_id == run_id)
                ).first()

            feedback = DemoFeedback(
                scenario_id=scenario.id,
                run_id=run_record.id if run_record else None,
                user_id=user_id,
                feedback_type=feedback_data.get("feedback_type", "general"),
                rating=feedback_data.get("rating"),
                title=feedback_data.get("title", "Demo Feedback"),
                message=feedback_data.get("message", ""),
                user_agent=feedback_data.get("user_agent"),
                session_info=feedback_data.get("session_info"),
            )

            self.session.add(feedback)
            self.session.commit()

            logger.info(f"Demo feedback submitted for scenario {scenario_id}")
            return True

        except Exception as e:
            logger.error(f"Error submitting demo feedback: {e}")
            return False

    async def get_scenario_analytics(
        self, scenario_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for a specific scenario"""

        try:
            scenario = self.session.exec(
                select(DemoScenario).where(DemoScenario.scenario_id == scenario_id)
            ).first()

            if not scenario:
                raise ValueError(f"Scenario {scenario_id} not found")

            since_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)

            # Get demo runs
            runs = self.session.exec(
                select(DemoRun).where(
                    and_(
                        DemoRun.scenario_id == scenario.id,
                        DemoRun.created_at >= since_date,
                    )
                )
            ).all()

            # Calculate metrics
            total_runs = len(runs)
            successful_runs = len([r for r in runs if r.status == "completed"])
            failed_runs = len([r for r in runs if r.status == "failed"])
            aborted_runs = len([r for r in runs if r.status == "aborted"])

            success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

            # Average duration
            completed_runs = [r for r in runs if r.total_duration_seconds is not None]
            avg_duration = None
            if completed_runs:
                avg_duration = sum(
                    r.total_duration_seconds for r in completed_runs
                ) / len(completed_runs)

            # Browser and device breakdown
            browser_stats = {}
            device_stats = {}
            for run in runs:
                if run.browser:
                    browser_stats[run.browser] = browser_stats.get(run.browser, 0) + 1
                if run.device_type:
                    device_stats[run.device_type] = (
                        device_stats.get(run.device_type, 0) + 1
                    )

            # Step-level analytics
            step_analytics = []
            for step in scenario.steps:
                step_data = {
                    "step_number": step.step_number,
                    "title": step.title,
                    "action_type": step.action_type,
                    "success_count": step.success_count,
                    "failure_count": step.failure_count,
                    "success_rate": (
                        (
                            step.success_count
                            / (step.success_count + step.failure_count)
                            * 100
                        )
                        if (step.success_count + step.failure_count) > 0
                        else 0
                    ),
                    "avg_execution_time": step.average_execution_time,
                }
                step_analytics.append(step_data)

            return {
                "scenario_id": scenario_id,
                "period_days": days,
                "overview": {
                    "total_runs": total_runs,
                    "successful_runs": successful_runs,
                    "failed_runs": failed_runs,
                    "aborted_runs": aborted_runs,
                    "success_rate": round(success_rate, 2),
                    "average_duration_seconds": (
                        round(avg_duration, 2) if avg_duration else None
                    ),
                },
                "browser_breakdown": browser_stats,
                "device_breakdown": device_stats,
                "step_analytics": step_analytics,
                "recent_feedback": await self._get_recent_feedback(
                    scenario.id, limit=5
                ),
            }

        except Exception as e:
            logger.error(f"Error getting scenario analytics: {e}")
            raise

    async def create_scenario_from_template(
        self, template_id: str, customizations: Dict[str, Any], created_by: int
    ) -> str:
        """Create a new scenario from a template"""

        try:
            template = self.session.exec(
                select(DemoTemplate).where(DemoTemplate.template_id == template_id)
            ).first()

            if not template:
                raise ValueError(f"Template {template_id} not found")

            template_data = template.template_data

            # Create scenario
            scenario = DemoScenario(
                name=customizations.get("name", template_data["name"]),
                description=customizations.get(
                    "description", template_data["description"]
                ),
                scenario_type=ScenarioType(
                    customizations.get("scenario_type", template_data["scenario_type"])
                ),
                target_audience=customizations.get(
                    "target_audience", template_data.get("target_audience", "general")
                ),
                duration_minutes=customizations.get(
                    "duration_minutes", template_data.get("duration_minutes", 10)
                ),
                difficulty_level=customizations.get(
                    "difficulty_level",
                    template_data.get("difficulty_level", "beginner"),
                ),
                auto_play=customizations.get(
                    "auto_play", template_data.get("auto_play", False)
                ),
                created_by=created_by,
            )

            self.session.add(scenario)
            self.session.commit()
            self.session.refresh(scenario)

            # Create steps from template
            for step_data in template_data.get("steps", []):
                step = DemoStep(
                    scenario_id=scenario.id,
                    step_number=step_data["step_number"],
                    action_type=ActionType(step_data["action_type"]),
                    title=step_data["title"],
                    description=step_data["description"],
                    target_element=step_data.get("target_element"),
                    target_url=step_data.get("target_url"),
                    form_data=step_data.get("form_data"),
                    expected_result=step_data.get("expected_result"),
                    demo_user_type=(
                        DemoUserType(step_data["demo_user_type"])
                        if step_data.get("demo_user_type")
                        else None
                    ),
                    duration_seconds=step_data.get("duration_seconds", 3),
                    annotation_text=step_data.get("annotation_text"),
                )
                self.session.add(step)

            self.session.commit()

            # Update template usage
            template.usage_count += 1
            self.session.add(template)
            self.session.commit()

            logger.info(
                f"Created scenario {scenario.scenario_id} from template {template_id}"
            )
            return scenario.scenario_id

        except Exception as e:
            logger.error(f"Error creating scenario from template: {e}")
            self.session.rollback()
            raise

    # Helper methods

    async def _reset_demo_data(self, scenario: DemoScenario):
        """Reset demo environment data"""

        try:
            # This would reset any demo-specific data
            # For now, just log the action
            logger.info(f"Resetting demo data for scenario {scenario.scenario_id}")

            # In a real implementation, this might:
            # - Delete demo user accounts
            # - Reset demo opportunities and applications
            # - Clear demo messages and notifications
            # - Reset demo organization data

        except Exception as e:
            logger.error(f"Error resetting demo data: {e}")

    async def _get_scenario_step(
        self, scenario_id: int, step_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get a specific scenario step"""

        step = self.session.exec(
            select(DemoStep).where(
                and_(
                    DemoStep.scenario_id == scenario_id,
                    DemoStep.step_number == step_number,
                )
            )
        ).first()

        if not step:
            return None

        return {
            "id": step.id,
            "step_id": step.step_id,
            "step_number": step.step_number,
            "action_type": step.action_type,
            "title": step.title,
            "description": step.description,
            "target_element": step.target_element,
            "target_url": step.target_url,
            "form_data": step.form_data,
            "expected_result": step.expected_result,
            "demo_user_type": step.demo_user_type,
            "user_data": step.user_data,
            "duration_seconds": step.duration_seconds,
            "wait_for_condition": step.wait_for_condition,
            "show_highlight": step.show_highlight,
            "annotation_text": step.annotation_text,
            "annotation_position": step.annotation_position,
            "validation_rules": step.validation_rules,
            "success_criteria": step.success_criteria,
            "retry_on_failure": step.retry_on_failure,
            "max_retries": step.max_retries,
            "fallback_action": step.fallback_action,
        }

    async def _execute_step_action(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a demo step action"""

        action_type = step["action_type"]
        step_start_time = datetime.now(datetime.timezone.utc)

        try:
            # Simulate step execution based on action type
            result = {
                "success": True,
                "message": f"Executed {action_type} successfully",
            }

            if action_type == ActionType.CREATE_USER:
                result = await self._simulate_create_user(step, context)
            elif action_type == ActionType.LOGIN:
                result = await self._simulate_login(step, context)
            elif action_type == ActionType.NAVIGATE:
                result = await self._simulate_navigate(step, context)
            elif action_type == ActionType.FILL_FORM:
                result = await self._simulate_fill_form(step, context)
            elif action_type == ActionType.CLICK_BUTTON:
                result = await self._simulate_click_button(step, context)
            elif action_type == ActionType.UPLOAD_FILE:
                result = await self._simulate_upload_file(step, context)
            elif action_type == ActionType.SEND_MESSAGE:
                result = await self._simulate_send_message(step, context)
            elif action_type == ActionType.MAKE_PAYMENT:
                result = await self._simulate_make_payment(step, context)
            elif action_type == ActionType.SUBMIT_APPLICATION:
                result = await self._simulate_submit_application(step, context)
            elif action_type == ActionType.CREATE_OPPORTUNITY:
                result = await self._simulate_create_opportunity(step, context)
            elif action_type == ActionType.WAIT:
                await asyncio.sleep(step.get("duration_seconds", 1))
                result = {"success": True, "message": "Wait completed"}
            else:
                result = {"success": True, "message": f"Simulated {action_type}"}

            # Calculate execution time
            execution_time = (
                datetime.now(datetime.timezone.utc) - step_start_time
            ).total_seconds()
            result["execution_time"] = execution_time

            # Update step analytics
            await self._update_step_analytics(
                step["id"], result["success"], execution_time
            )

            return result

        except Exception as e:
            logger.error(f"Error executing step action {action_type}: {e}")
            return {
                "success": False,
                "message": f"Failed to execute {action_type}: {str(e)}",
                "execution_time": (
                    datetime.now(datetime.timezone.utc) - step_start_time
                ).total_seconds(),
            }

    async def _simulate_create_user(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate user creation"""
        user_data = step.get("user_data", {})
        demo_user_type = step.get("demo_user_type")

        # Create demo user data
        demo_user = {
            "id": f"demo_{demo_user_type}_{datetime.now(datetime.timezone.utc).timestamp()}",
            "type": demo_user_type,
            "email": user_data.get("email", f"demo.{demo_user_type}@seraaj.org"),
            "name": user_data.get("name", f"Demo {demo_user_type.title()}"),
            "created_at": datetime.now(datetime.timezone.utc).isoformat(),
        }

        # Store in demo users cache
        session_id = context.get("session_id") if context else "default"
        if session_id not in self.demo_users:
            self.demo_users[session_id] = {}
        self.demo_users[session_id][demo_user_type] = demo_user

        return {
            "success": True,
            "message": f"Created demo {demo_user_type} user",
            "data": {"user": demo_user},
        }

    async def _simulate_login(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate user login"""
        demo_user_type = step.get("demo_user_type")
        session_id = context.get("session_id") if context else "default"

        # Get demo user from cache
        if (
            session_id in self.demo_users
            and demo_user_type in self.demo_users[session_id]
        ):
            user = self.demo_users[session_id][demo_user_type]
            return {
                "success": True,
                "message": f"Logged in as {user['name']}",
                "data": {"user": user, "token": f"demo_token_{user['id']}"},
            }

        return {
            "success": False,
            "message": f"Demo user {demo_user_type} not found. Create user first.",
        }

    async def _simulate_navigate(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate navigation"""
        target_url = step.get("target_url", "/")

        return {
            "success": True,
            "message": f"Navigated to {target_url}",
            "data": {"url": target_url},
        }

    async def _simulate_fill_form(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate form filling"""
        form_data = step.get("form_data", {})

        return {
            "success": True,
            "message": "Form filled successfully",
            "data": {"form_data": form_data},
        }

    async def _simulate_click_button(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate button click"""
        target_element = step.get("target_element", "button")

        return {
            "success": True,
            "message": f"Clicked {target_element}",
            "data": {"element": target_element},
        }

    async def _simulate_upload_file(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate file upload"""
        return {
            "success": True,
            "message": "File uploaded successfully",
            "data": {"file": "demo_file.pdf"},
        }

    async def _simulate_send_message(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate sending a message"""
        return {
            "success": True,
            "message": "Message sent successfully",
            "data": {
                "message_id": f"msg_{datetime.now(datetime.timezone.utc).timestamp()}"
            },
        }

    async def _simulate_make_payment(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate payment processing"""
        return {
            "success": True,
            "message": "Payment processed successfully",
            "data": {
                "transaction_id": f"txn_{datetime.now(datetime.timezone.utc).timestamp()}"
            },
        }

    async def _simulate_submit_application(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate application submission"""
        return {
            "success": True,
            "message": "Application submitted successfully",
            "data": {
                "application_id": f"app_{datetime.now(datetime.timezone.utc).timestamp()}"
            },
        }

    async def _simulate_create_opportunity(
        self, step: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulate opportunity creation"""
        return {
            "success": True,
            "message": "Opportunity created successfully",
            "data": {
                "opportunity_id": f"opp_{datetime.now(datetime.timezone.utc).timestamp()}"
            },
        }

    async def _complete_demo_run(self, demo_run: DemoRun):
        """Complete a demo run"""

        demo_run.status = "completed"
        demo_run.completed_at = datetime.now(datetime.timezone.utc)

        if demo_run.started_at:
            demo_run.total_duration_seconds = int(
                (
                    datetime.now(datetime.timezone.utc) - demo_run.started_at
                ).total_seconds()
            )

        # Calculate success rate
        total_steps = len(demo_run.completed_steps) + len(demo_run.failed_steps)
        if total_steps > 0:
            demo_run.success_rate = (len(demo_run.completed_steps) / total_steps) * 100

        self.session.add(demo_run)

        # Update scenario success rate
        scenario = self.session.get(DemoScenario, demo_run.scenario_id)
        if scenario:
            all_completed_runs = self.session.exec(
                select(DemoRun).where(
                    and_(
                        DemoRun.scenario_id == scenario.id,
                        DemoRun.status.in_(["completed", "failed"]),
                    )
                )
            ).all()

            successful_runs = len(
                [r for r in all_completed_runs if r.status == "completed"]
            )
            scenario.success_rate = (
                (successful_runs / len(all_completed_runs)) * 100
                if all_completed_runs
                else 0
            )

            self.session.add(scenario)

        self.session.commit()

    async def _update_step_analytics(
        self, step_id: int, success: bool, execution_time: float
    ):
        """Update step analytics"""

        try:
            step = self.session.get(DemoStep, step_id)
            if step:
                if success:
                    step.success_count += 1
                else:
                    step.failure_count += 1

                # Update average execution time
                total_executions = step.success_count + step.failure_count
                if step.average_execution_time is None:
                    step.average_execution_time = execution_time
                else:
                    step.average_execution_time = (
                        step.average_execution_time * (total_executions - 1)
                        + execution_time
                    ) / total_executions

                self.session.add(step)
                self.session.commit()

        except Exception as e:
            logger.error(f"Error updating step analytics: {e}")

    async def _get_recent_feedback(
        self, scenario_id: int, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent feedback for a scenario"""

        feedback_records = self.session.exec(
            select(DemoFeedback)
            .where(DemoFeedback.scenario_id == scenario_id)
            .order_by(DemoFeedback.created_at.desc())
            .limit(limit)
        ).all()

        feedback_list = []
        for feedback in feedback_records:
            feedback_list.append(
                {
                    "feedback_type": feedback.feedback_type,
                    "rating": feedback.rating,
                    "title": feedback.title,
                    "message": feedback.message,
                    "created_at": feedback.created_at.isoformat(),
                    "status": feedback.status,
                }
            )

        return feedback_list

    async def _serialize_scenario(self, scenario: DemoScenario) -> Dict[str, Any]:
        """Serialize scenario for API response"""

        return {
            "scenario_id": scenario.scenario_id,
            "name": scenario.name,
            "description": scenario.description,
            "scenario_type": scenario.scenario_type,
            "target_audience": scenario.target_audience,
            "duration_minutes": scenario.duration_minutes,
            "difficulty_level": scenario.difficulty_level,
            "auto_play": scenario.auto_play,
            "show_annotations": scenario.show_annotations,
            "show_metrics": scenario.show_metrics,
            "base_url": scenario.base_url,
            "required_features": scenario.required_features,
        }


def get_demo_scenario_service(
    session: Session = Depends(get_session),
) -> DemoScenarioService:
    """Get demo scenario service instance"""
    return DemoScenarioService(session)
