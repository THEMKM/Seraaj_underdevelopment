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
from typing import Annotated, List, Optional, Dict
from datetime import datetime

from database import get_session
from models import (
    Application,
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    User,
    Volunteer,
    Organisation,
    Opportunity,
    ApplicationStatus,
    FileUpload,
)
from routers.auth import get_current_user
from pydantic import BaseModel


# Response Models for consistent API responses
class MessageResponse(BaseModel):
    """Standard response for operations with messages"""

    message: str


router = APIRouter(prefix="/v1/applications", tags=["applications"])


@router.post("/", response_model=ApplicationRead)
async def create_application(
    application_data: ApplicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new application for an opportunity"""
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can create applications",
        )

    # Verify the volunteer profile exists
    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Volunteer profile not found",
        )

    # Verify the opportunity exists and is active
    opportunity = session.get(Opportunity, application_data.opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )

    if opportunity.state != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Opportunity is not active"
        )

    # Check if application already exists
    existing_application = session.exec(
        select(Application).where(
            and_(
                Application.volunteer_id == volunteer.id,
                Application.opportunity_id == application_data.opportunity_id,
            )
        )
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application already exists for this opportunity",
        )

    # Create the application
    db_application = Application(
        **application_data.model_dump(), volunteer_id=volunteer.id
    )

    session.add(db_application)
    session.commit()
    session.refresh(db_application)

    return ApplicationRead.model_validate(db_application)


@router.get("/", response_model=List[ApplicationRead])
async def get_my_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status_filter: Annotated[Optional[str], Query()] = None,
    opportunity_id: Annotated[Optional[int], Query()] = None,
):
    """Get current user's applications"""
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can view their applications",
        )

    # Get volunteer profile
    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Volunteer profile not found",
        )

    # Build query
    query = select(Application).where(Application.volunteer_id == volunteer.id)

    if status_filter:
        query = query.where(Application.status == status_filter)

    if opportunity_id:
        query = query.where(Application.opportunity_id == opportunity_id)

    query = query.order_by(Application.created_at.desc())
    query = query.offset(skip).limit(limit)

    applications = session.exec(query).all()
    return [ApplicationRead.model_validate(app) for app in applications]


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get a specific application by ID"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Check permissions - volunteer can see their own, organization can see applications for their opportunities
    can_view = False

    if current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()
        if volunteer and application.volunteer_id == volunteer.id:
            can_view = True

    elif current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()
        if organization:
            opportunity = session.get(Opportunity, application.opportunity_id)
            if opportunity and opportunity.org_id == organization.id:
                can_view = True

    elif current_user.role == "admin":
        can_view = True

    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this application",
        )

    return ApplicationRead.model_validate(application)


@router.put("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Update an application"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Check permissions
    can_update = False

    if current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()
        if volunteer and application.volunteer_id == volunteer.id:
            # Volunteers can only update their own applications if they're in draft or submitted status
            if application.status in ["draft", "submitted"]:
                can_update = True

    elif current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()
        if organization:
            opportunity = session.get(Opportunity, application.opportunity_id)
            if opportunity and opportunity.org_id == organization.id:
                can_update = True

    elif current_user.role == "admin":
        can_update = True

    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this application",
        )

    # Update the application
    update_data = application_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)

    application.updated_at = datetime.now(datetime.timezone.utc)
    session.add(application)
    session.commit()
    session.refresh(application)

    return ApplicationRead.model_validate(application)


@router.post("/{application_id}/submit", response_model=MessageResponse)
async def submit_application(
    application_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Submit a draft application"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Only volunteers can submit their own applications
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can submit applications",
        )

    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer or application.volunteer_id != volunteer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit this application",
        )

    if application.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft applications can be submitted",
        )

    # Validate required fields
    if not application.cover_letter or not application.cover_letter.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cover letter is required"
        )

    # Update status and submission date
    application.status = ApplicationStatus.SUBMITTED
    application.submitted_at = datetime.now(datetime.timezone.utc)
    application.updated_at = datetime.now(datetime.timezone.utc)

    session.add(application)
    session.commit()

    return MessageResponse(message="Application submitted successfully")


@router.post("/{application_id}/review", response_model=MessageResponse)
async def review_application(
    application_id: int,
    review_data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Review an application (organization only)"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Only organizations can review applications for their opportunities
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can review applications",
        )

    if current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization profile not found",
            )

        opportunity = session.get(Opportunity, application.opportunity_id)
        if not opportunity or opportunity.org_id != organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to review this application",
            )

    # Update application with review
    new_status = review_data.get("status")
    feedback = review_data.get("feedback")

    if new_status:
        try:
            application.status = ApplicationStatus(new_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
            )

    if feedback:
        application.review_feedback = feedback

    application.reviewed_at = datetime.now(datetime.timezone.utc)
    application.reviewed_by = current_user.id
    application.updated_at = datetime.now(datetime.timezone.utc)

    session.add(application)
    session.commit()

    return MessageResponse(message="Application reviewed successfully")


@router.post("/{application_id}/schedule-interview")
async def schedule_interview(
    application_id: int,
    interview_data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Schedule an interview for an application"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Only organizations can schedule interviews
    if current_user.role not in ["organization", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can schedule interviews",
        )

    if current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization profile not found",
            )

        opportunity = session.get(Opportunity, application.opportunity_id)
        if not opportunity or opportunity.org_id != organization.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to schedule interview for this application",
            )

    # Parse interview date
    try:
        interview_date = datetime.fromisoformat(interview_data["interview_date"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid interview date format",
        )

    # Update application
    application.interview_date = interview_date
    application.interview_notes = interview_data.get("notes", "")
    application.status = ApplicationStatus.INTERVIEW_SCHEDULED
    application.updated_at = datetime.now(datetime.timezone.utc)

    session.add(application)
    session.commit()

    return {"message": "Interview scheduled successfully"}


@router.delete("/{application_id}")
async def withdraw_application(
    application_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Withdraw/delete an application"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Only volunteers can withdraw their own applications or admins can delete any
    can_delete = False

    if current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()
        if volunteer and application.volunteer_id == volunteer.id:
            # Can only withdraw if not already accepted or completed
            if application.status not in ["accepted", "completed"]:
                can_delete = True

    elif current_user.role == "admin":
        can_delete = True

    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this application",
        )

    session.delete(application)
    session.commit()

    return {"message": "Application withdrawn successfully"}


@router.post("/{application_id}/documents")
async def upload_application_document(
    application_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    file: UploadFile = File(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
):
    """Upload a document for an application"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Verify user owns this application
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can upload application documents",
        )

    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer or application.volunteer_id != volunteer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload documents for this application",
        )

    # Validate document type
    valid_document_types = [
        "resume",
        "cover_letter",
        "portfolio",
        "certificate",
        "reference_letter",
        "identification",
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
            upload_category="applications",
            user_id=current_user.id,
            session=session,
            file_description=f"{document_type} for application {application_id}: {description or ''}",
            is_public=False,
        )

        # Update application documents
        documents = application.documents or []
        documents.append(
            {
                "file_id": db_file.id,
                "document_type": document_type,
                "filename": db_file.filename,
                "uploaded_at": datetime.now(datetime.timezone.utc).isoformat(),
                "description": description,
            }
        )

        application.documents = documents
        application.updated_at = datetime.now(datetime.timezone.utc)

        session.add(application)
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


@router.get("/{application_id}/documents")
async def get_application_documents(
    application_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get documents for an application"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Check permissions
    can_view = False

    if current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()
        if volunteer and application.volunteer_id == volunteer.id:
            can_view = True

    elif current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()
        if organization:
            opportunity = session.get(Opportunity, application.opportunity_id)
            if opportunity and opportunity.org_id == organization.id:
                can_view = True

    elif current_user.role == "admin":
        can_view = True

    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view documents for this application",
        )

    # Get document details
    documents = application.documents or []
    document_details = []

    for doc in documents:
        file_id = doc.get("file_id")
        if file_id:
            file_record = session.get(FileUpload, file_id)
            if file_record:
                document_details.append(
                    {
                        "file_id": file_id,
                        "document_type": doc.get("document_type"),
                        "filename": file_record.filename,
                        "file_size": file_record.file_size,
                        "uploaded_at": doc.get("uploaded_at"),
                        "description": doc.get("description"),
                    }
                )

    return {"application_id": application_id, "documents": document_details}


@router.delete("/{application_id}/documents/{file_id}")
async def delete_application_document(
    application_id: int,
    file_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Delete a document from an application"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Verify user owns this application
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can delete application documents",
        )

    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer or application.volunteer_id != volunteer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete documents from this application",
        )

    # Only allow deletion if application is still in draft or submitted status
    if application.status not in ["draft", "submitted"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete documents from applications that are being processed",
        )

    try:
        # Remove document from application
        documents = application.documents or []
        updated_documents = [doc for doc in documents if doc.get("file_id") != file_id]

        if len(updated_documents) == len(documents):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found in this application",
            )

        application.documents = updated_documents
        application.updated_at = datetime.now(datetime.timezone.utc)

        session.add(application)
        session.commit()

        # Delete the actual file
        await file_handler.delete_file(
            file_id=file_id, user_id=current_user.id, session=session
        )

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}",
        )


@router.post("/{application_id}/steps/{step_name}")
async def complete_application_step(
    application_id: int,
    step_name: str,
    step_data: Dict,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Complete a step in the multi-step application process"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Verify user owns this application
    if current_user.role != "volunteer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can complete application steps",
        )

    volunteer = session.exec(
        select(Volunteer).where(Volunteer.user_id == current_user.id)
    ).first()

    if not volunteer or application.volunteer_id != volunteer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete steps for this application",
        )

    # Validate step name
    valid_steps = [
        "basic_info",
        "motivation",
        "availability",
        "experience",
        "references",
        "background_check",
        "skills_assessment",
    ]
    if step_name not in valid_steps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid step name. Must be one of: {valid_steps}",
        )

    # Update application step data
    application_steps = application.application_steps or {}
    application_steps[step_name] = {
        "data": step_data,
        "completed_at": datetime.now(datetime.timezone.utc).isoformat(),
        "status": "completed",
    }

    application.application_steps = application_steps
    application.updated_at = datetime.now(datetime.timezone.utc)

    # Check if all required steps are completed
    required_steps = ["basic_info", "motivation", "availability"]
    completed_steps = [
        step
        for step, info in application_steps.items()
        if info.get("status") == "completed"
    ]

    all_required_completed = all(step in completed_steps for step in required_steps)

    if all_required_completed and application.status == "draft":
        # Automatically move to submitted if all required steps are done
        # and cover letter is provided
        if application.cover_letter:
            application.status = ApplicationStatus.SUBMITTED
            application.submitted_at = datetime.now(datetime.timezone.utc)

    session.add(application)
    session.commit()

    return {
        "message": f"Step '{step_name}' completed successfully",
        "completed_steps": completed_steps,
        "all_required_completed": all_required_completed,
        "application_status": application.status.value,
    }


@router.get("/{application_id}/steps")
async def get_application_steps(
    application_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get the status of all application steps"""
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Check permissions
    can_view = False

    if current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()
        if volunteer and application.volunteer_id == volunteer.id:
            can_view = True

    elif current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()
        if organization:
            opportunity = session.get(Opportunity, application.opportunity_id)
            if opportunity and opportunity.org_id == organization.id:
                can_view = True

    elif current_user.role == "admin":
        can_view = True

    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view steps for this application",
        )

    # Define all possible steps with their requirements
    all_steps = {
        "basic_info": {
            "title": "Basic Information",
            "description": "Personal and contact information",
            "required": True,
            "order": 1,
        },
        "motivation": {
            "title": "Motivation & Goals",
            "description": "Why you want to volunteer and what you hope to achieve",
            "required": True,
            "order": 2,
        },
        "availability": {
            "title": "Availability",
            "description": "When you're available to volunteer",
            "required": True,
            "order": 3,
        },
        "experience": {
            "title": "Experience & Skills",
            "description": "Relevant experience and skills for this role",
            "required": False,
            "order": 4,
        },
        "references": {
            "title": "References",
            "description": "Contact information for references",
            "required": False,
            "order": 5,
        },
        "background_check": {
            "title": "Background Check",
            "description": "Background check documentation (if required)",
            "required": False,
            "order": 6,
        },
        "skills_assessment": {
            "title": "Skills Assessment",
            "description": "Complete skills assessment test",
            "required": False,
            "order": 7,
        },
    }

    application_steps = application.application_steps or {}

    # Build step status
    steps_status = []
    for step_name, step_info in all_steps.items():
        step_status = application_steps.get(step_name, {})
        steps_status.append(
            {
                "step_name": step_name,
                "title": step_info["title"],
                "description": step_info["description"],
                "required": step_info["required"],
                "order": step_info["order"],
                "status": step_status.get("status", "pending"),
                "completed_at": step_status.get("completed_at"),
                "data": (
                    step_status.get("data")
                    if current_user.role != "organization"
                    else None
                ),  # Hide data from orgs
            }
        )

    # Sort by order
    steps_status.sort(key=lambda x: x["order"])

    # Calculate progress
    completed_steps = [s for s in steps_status if s["status"] == "completed"]
    required_steps = [s for s in steps_status if s["required"]]
    completed_required = [s for s in completed_steps if s["required"]]

    progress = {
        "total_steps": len(steps_status),
        "completed_steps": len(completed_steps),
        "required_steps": len(required_steps),
        "completed_required": len(completed_required),
        "progress_percent": round((len(completed_steps) / len(steps_status)) * 100, 1),
        "required_progress_percent": (
            round((len(completed_required) / len(required_steps)) * 100, 1)
            if required_steps
            else 100
        ),
    }

    return {
        "application_id": application_id,
        "application_status": application.status.value,
        "steps": steps_status,
        "progress": progress,
    }


@router.get("/stats/summary")
async def get_applications_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get application statistics"""
    stats = {}

    if current_user.role == "volunteer":
        volunteer = session.exec(
            select(Volunteer).where(Volunteer.user_id == current_user.id)
        ).first()

        if volunteer:
            # Get volunteer's application stats
            total = session.exec(
                select(func.count(Application.id)).where(
                    Application.volunteer_id == volunteer.id
                )
            ).first()

            # Applications by status
            status_stats = session.exec(
                select(Application.status, func.count(Application.id))
                .where(Application.volunteer_id == volunteer.id)
                .group_by(Application.status)
            ).all()

            stats = {
                "total_applications": total,
                "status_breakdown": dict(status_stats),
            }

    elif current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()

        if organization:
            # Get applications for organization's opportunities
            total = session.exec(
                select(func.count(Application.id))
                .join(Opportunity, Application.opportunity_id == Opportunity.id)
                .where(Opportunity.org_id == organization.id)
            ).first()

            # Applications by status
            status_stats = session.exec(
                select(Application.status, func.count(Application.id))
                .join(Opportunity, Application.opportunity_id == Opportunity.id)
                .where(Opportunity.org_id == organization.id)
                .group_by(Application.status)
            ).all()

            stats = {
                "total_applications": total,
                "status_breakdown": dict(status_stats),
            }

    elif current_user.role == "admin":
        # Global application stats
        total = session.exec(select(func.count(Application.id))).first()

        status_stats = session.exec(
            select(Application.status, func.count(Application.id)).group_by(
                Application.status
            )
        ).all()

        stats = {"total_applications": total, "status_breakdown": dict(status_stats)}

    return stats


@router.get("/opportunity/{opportunity_id}")
async def get_applications_for_opportunity(
    opportunity_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status_filter: Annotated[Optional[str], Query()] = None,
):
    """Get applications for a specific opportunity (organization only)"""
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found"
        )

    # Check permissions
    can_view = False

    if current_user.role == "organization":
        organization = session.exec(
            select(Organisation).where(Organisation.user_id == current_user.id)
        ).first()
        if organization and opportunity.org_id == organization.id:
            can_view = True

    elif current_user.role == "admin":
        can_view = True

    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view applications for this opportunity",
        )

    # Get applications
    query = select(Application).where(Application.opportunity_id == opportunity_id)

    if status_filter:
        query = query.where(Application.status == status_filter)

    query = query.order_by(Application.created_at.desc())
    query = query.offset(skip).limit(limit)

    applications = session.exec(query).all()

    return {
        "opportunity_id": opportunity_id,
        "applications": [ApplicationRead.model_validate(app) for app in applications],
        "total_count": len(applications),
    }
