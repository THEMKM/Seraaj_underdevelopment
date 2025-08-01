"""
Demo Scenarios Router for Seraaj
Comprehensive demo scenarios and execution management
"""

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing import Annotated, Dict, Any, List, Optional
from datetime import datetime

from database import get_session
from routers.auth import get_current_user
from models import User
from models.demo_scenario import ScenarioType, ScenarioStatus, DemoUserType
from services.demo_scenario_service import get_demo_scenario_service

router = APIRouter(prefix="/v1/demo-scenarios", tags=["demo-scenarios"])

# Pydantic models for request/response
from pydantic import BaseModel, Field


class StartDemoRequest(BaseModel):
    environment_info: Optional[Dict[str, Any]] = None
    auto_play: Optional[bool] = None


class ExecuteStepRequest(BaseModel):
    execution_context: Optional[Dict[str, Any]] = None


class DemoFeedbackRequest(BaseModel):
    feedback_type: str = Field(default="general")
    rating: Optional[int] = Field(ge=1, le=5)
    title: str
    message: str
    session_info: Optional[Dict[str, Any]] = None


class CreateScenarioRequest(BaseModel):
    name: str
    description: str
    scenario_type: ScenarioType
    target_audience: str = Field(default="general")
    duration_minutes: int = Field(default=10)
    difficulty_level: str = Field(default="beginner")
    steps: List[Dict[str, Any]]
    auto_play: bool = Field(default=False)
    show_annotations: bool = Field(default=True)


class CreateFromTemplateRequest(BaseModel):
    template_id: str
    customizations: Dict[str, Any] = Field(default_factory=dict)


@router.get("/available")
async def get_available_scenarios(
    service: Annotated[any, Depends(get_demo_scenario_service)],
    scenario_type: Optional[ScenarioType] = Query(None),
    target_audience: Optional[str] = Query(None),
    difficulty_level: Optional[str] = Query(None),
):
    """Get available demo scenarios"""

    try:
        scenarios = await service.get_available_scenarios(
            scenario_type=scenario_type,
            target_audience=target_audience,
            difficulty_level=difficulty_level,
        )

        return JSONResponse(
            content={"success": True, "scenarios": scenarios, "total": len(scenarios)}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.post("/start/{scenario_id}")
async def start_demo_scenario(
    scenario_id: str,
    request_data: StartDemoRequest,
    request: Request,
    current_user: Annotated[Optional[User], Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None,
    service: Annotated[any, Depends(get_demo_scenario_service)] = None,
):
    """Start a demo scenario"""

    try:
        # Generate session ID from request
        session_id = f"demo_{datetime.now(datetime.timezone.utc).timestamp()}_{hash(str(request.headers))}"

        # Get environment info
        environment_info = request_data.environment_info or {}
        environment_info.update(
            {
                "user_agent": request.headers.get("user-agent"),
                "ip_address": request.client.host if request.client else None,
            }
        )

        demo_run = await service.start_demo_scenario(
            scenario_id=scenario_id,
            session_id=session_id,
            runner_id=current_user.id if current_user else None,
            environment_info=environment_info,
        )

        return JSONResponse(content={"success": True, "demo_run": demo_run})

    except ValueError as e:
        return JSONResponse(
            status_code=404, content={"success": False, "error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.get("/run/{run_id}")
async def get_demo_run_status(
    run_id: str, session: Annotated[Session, Depends(get_session)] = None
):
    """Get demo run status and progress"""

    try:
        from sqlmodel import select
        from models.demo_scenario import DemoRun

        demo_run = session.exec(select(DemoRun).where(DemoRun.run_id == run_id)).first()

        if not demo_run:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Demo run not found"},
            )

        return JSONResponse(
            content={
                "success": True,
                "demo_run": {
                    "run_id": demo_run.run_id,
                    "status": demo_run.status,
                    "current_step": demo_run.current_step,
                    "completed_steps": demo_run.completed_steps,
                    "failed_steps": demo_run.failed_steps,
                    "started_at": (
                        demo_run.started_at.isoformat() if demo_run.started_at else None
                    ),
                    "total_duration_seconds": demo_run.total_duration_seconds,
                    "success_rate": demo_run.success_rate,
                },
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.post("/run/{run_id}/execute/{step_number}")
async def execute_demo_step(
    run_id: str,
    step_number: int,
    request_data: ExecuteStepRequest,
    session: Annotated[Session, Depends(get_session)] = None,
    service: Annotated[any, Depends(get_demo_scenario_service)] = None,
):
    """Execute a specific demo step"""

    try:
        result = await service.execute_demo_step(
            run_id=run_id,
            step_number=step_number,
            execution_context=request_data.execution_context,
        )

        return JSONResponse(content={"success": True, "result": result})

    except ValueError as e:
        return JSONResponse(
            status_code=404, content={"success": False, "error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.post("/run/{run_id}/abort")
async def abort_demo_run(
    run_id: str,
    reason: str = "user_cancelled",
    session: Annotated[Session, Depends(get_session)] = None,
    service: Annotated[any, Depends(get_demo_scenario_service)] = None,
):
    """Abort a running demo scenario"""

    try:
        success = await service.abort_demo_run(run_id=run_id, reason=reason)

        if success:
            return JSONResponse(
                content={"success": True, "message": "Demo run aborted successfully"}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Demo run not found"},
            )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.post("/scenarios/{scenario_id}/feedback")
async def submit_demo_feedback(
    scenario_id: str,
    feedback_data: DemoFeedbackRequest,
    run_id: Optional[str] = Query(None),
    request: Request = None,
    current_user: Annotated[Optional[User], Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None,
    service: Annotated[any, Depends(get_demo_scenario_service)] = None,
):
    """Submit feedback for a demo scenario"""

    try:
        feedback_dict = feedback_data.dict()
        feedback_dict["user_agent"] = request.headers.get("user-agent")

        success = await service.submit_demo_feedback(
            scenario_id=scenario_id,
            run_id=run_id,
            feedback_data=feedback_dict,
            user_id=current_user.id if current_user else None,
        )

        if success:
            return JSONResponse(
                content={"success": True, "message": "Feedback submitted successfully"}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Scenario not found"},
            )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.get("/scenarios/{scenario_id}/analytics")
async def get_scenario_analytics(
    scenario_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None,
    service: Annotated[any, Depends(get_demo_scenario_service)] = None,
):
    """Get analytics for a specific scenario (admin only)"""

    if not current_user or current_user.role != "admin":
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "Admin access required"},
        )

    try:
        analytics = await service.get_scenario_analytics(
            scenario_id=scenario_id, days=days
        )

        return JSONResponse(content={"success": True, "analytics": analytics})

    except ValueError as e:
        return JSONResponse(
            status_code=404, content={"success": False, "error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.get("/templates")
async def get_demo_templates(
    category: Optional[str] = Query(None),
    scenario_type: Optional[ScenarioType] = Query(None),
    session: Annotated[Session, Depends(get_session)] = None,
):
    """Get available demo templates"""

    try:
        from sqlmodel import select
        from models.demo_scenario import DemoTemplate

        query = select(DemoTemplate)

        if category:
            query = query.where(DemoTemplate.category == category)

        if scenario_type:
            query = query.where(DemoTemplate.scenario_type == scenario_type)

        templates = session.exec(query.order_by(DemoTemplate.usage_count.desc())).all()

        template_list = []
        for template in templates:
            template_list.append(
                {
                    "template_id": template.template_id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "scenario_type": template.scenario_type,
                    "usage_count": template.usage_count,
                    "is_featured": template.is_featured,
                }
            )

        return JSONResponse(
            content={
                "success": True,
                "templates": template_list,
                "total": len(template_list),
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.post("/create")
async def create_demo_scenario(
    scenario_data: CreateScenarioRequest,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None,
):
    """Create a new demo scenario (admin only)"""

    if not current_user or current_user.role != "admin":
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "Admin access required"},
        )

    try:
        from models.demo_scenario import DemoScenario, DemoStep, ActionType

        # Create scenario
        scenario = DemoScenario(
            name=scenario_data.name,
            description=scenario_data.description,
            scenario_type=scenario_data.scenario_type,
            target_audience=scenario_data.target_audience,
            duration_minutes=scenario_data.duration_minutes,
            difficulty_level=scenario_data.difficulty_level,
            auto_play=scenario_data.auto_play,
            show_annotations=scenario_data.show_annotations,
            created_by=current_user.id,
        )

        session.add(scenario)
        session.commit()
        session.refresh(scenario)

        # Create steps
        for step_data in scenario_data.steps:
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
            session.add(step)

        session.commit()

        return JSONResponse(
            content={
                "success": True,
                "scenario_id": scenario.scenario_id,
                "message": "Demo scenario created successfully",
            }
        )

    except Exception as e:
        session.rollback()
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.post("/create-from-template")
async def create_scenario_from_template(
    request_data: CreateFromTemplateRequest,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None,
    service: Annotated[any, Depends(get_demo_scenario_service)] = None,
):
    """Create a scenario from a template (admin only)"""

    if not current_user or current_user.role != "admin":
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "Admin access required"},
        )

    try:
        scenario_id = await service.create_scenario_from_template(
            template_id=request_data.template_id,
            customizations=request_data.customizations,
            created_by=current_user.id,
        )

        return JSONResponse(
            content={
                "success": True,
                "scenario_id": scenario_id,
                "message": "Scenario created from template successfully",
            }
        )

    except ValueError as e:
        return JSONResponse(
            status_code=404, content={"success": False, "error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.get("/analytics/overview")
async def get_demo_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None,
):
    """Get overall demo analytics overview (admin only)"""

    if not current_user or current_user.role != "admin":
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "Admin access required"},
        )

    try:
        from sqlmodel import select, func
        from models.demo_scenario import DemoRun, DemoScenario
        from datetime import timedelta

        since_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)

        # Total runs
        total_runs = session.exec(
            select(func.count(DemoRun.id)).where(DemoRun.created_at >= since_date)
        ).first()

        # Success metrics
        from sqlmodel import and_

        successful_runs = session.exec(
            select(func.count(DemoRun.id)).where(
                and_(DemoRun.created_at >= since_date, DemoRun.status == "completed")
            )
        ).first()

        # Popular scenarios
        popular_scenarios = session.exec(
            select(DemoScenario.name, func.count(DemoRun.id).label("run_count"))
            .join(DemoRun)
            .where(DemoRun.created_at >= since_date)
            .group_by(DemoScenario.id)
            .order_by(func.count(DemoRun.id).desc())
            .limit(5)
        ).all()

        return JSONResponse(
            content={
                "success": True,
                "overview": {
                    "period_days": days,
                    "total_runs": total_runs or 0,
                    "successful_runs": successful_runs or 0,
                    "success_rate": round(
                        (successful_runs / total_runs * 100) if total_runs else 0, 2
                    ),
                    "popular_scenarios": [
                        {"name": name, "run_count": count}
                        for name, count in popular_scenarios
                    ],
                },
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.delete("/scenarios/{scenario_id}")
async def delete_demo_scenario(
    scenario_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None,
):
    """Delete a demo scenario (admin only)"""

    if not current_user or current_user.role != "admin":
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "Admin access required"},
        )

    try:
        from sqlmodel import select
        from models.demo_scenario import DemoScenario

        scenario = session.exec(
            select(DemoScenario).where(DemoScenario.scenario_id == scenario_id)
        ).first()

        if not scenario:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Scenario not found"},
            )

        # Archive instead of delete to preserve analytics
        scenario.status = ScenarioStatus.ARCHIVED
        session.add(scenario)
        session.commit()

        return JSONResponse(
            content={"success": True, "message": "Demo scenario archived successfully"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
