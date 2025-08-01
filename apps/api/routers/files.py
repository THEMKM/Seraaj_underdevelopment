from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlmodel import Session, select
from typing import Annotated, List, Optional
import mimetypes
from pathlib import Path
import logging

from database import get_session
from models import (
    User, FileUpload, FileAccessLog, FilePermission
)
from routers.auth import get_current_user
from file_management.upload_handler import FileUploadHandler
from middleware.error_handler import raise_bad_request, raise_not_found, raise_forbidden
from middleware.loading_states import (
    ProgressTracker, create_loading_response, async_operation, loading_manager
)

router = APIRouter(prefix="/v1/files", tags=["files"])
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_file(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    file: UploadFile = File(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    is_public: bool = Form(False)
):
    """Upload a file with progress tracking"""
    
    # Validate file size (example: max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise_bad_request(
            "File size exceeds maximum limit",
            details={"max_size": "10MB", "uploaded_size": f"{file.size / 1024 / 1024:.2f}MB"}
        )
    
    # Create operation ID for progress tracking
    import uuid
    operation_id = f"upload_{current_user.id}_{uuid.uuid4().hex[:8]}"
    
    # Validate category
    valid_categories = ["profiles", "applications", "organizations", "opportunities", "documents"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {valid_categories}"
        )
    
    try:
        # Upload file
        db_file = await file_handler.upload_file(
            file=file,
            upload_category=category,
            user_id=current_user.id,
            session=session,
            file_description=description,
            is_public=is_public
        )
        
        return {
            "id": db_file.id,
            "filename": db_file.filename,
            "file_size": db_file.file_size,
            "mime_type": db_file.mime_type,
            "upload_category": db_file.upload_category,
            "created_at": db_file.created_at.isoformat(),
            "metadata": db_file.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during file upload"
        )


@router.get("/")
async def list_my_files(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List user's uploaded files"""
    
    query = select(FileUpload).where(FileUpload.uploaded_by == current_user.id)
    
    if category:
        query = query.where(FileUpload.upload_category == category)
    
    query = query.order_by(FileUpload.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    files = session.exec(query).all()
    
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "file_size": f.file_size,
            "mime_type": f.mime_type,
            "upload_category": f.upload_category,
            "description": f.description,
            "is_public": f.is_public,
            "created_at": f.created_at.isoformat(),
            "metadata": f.metadata
        }
        for f in files
    ]


@router.get("/{file_id}")
async def get_file_info(
    file_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get file information"""
    
    try:
        db_file = await file_handler.get_file(
            file_id=file_id,
            user_id=current_user.id,
            session=session
        )
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return {
            "id": db_file.id,
            "filename": db_file.filename,
            "file_size": db_file.file_size,
            "mime_type": db_file.mime_type,
            "upload_category": db_file.upload_category,
            "description": db_file.description,
            "is_public": db_file.is_public,
            "uploaded_by": db_file.uploaded_by,
            "created_at": db_file.created_at.isoformat(),
            "updated_at": db_file.updated_at.isoformat() if db_file.updated_at else None,
            "metadata": db_file.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving file information"
        )


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Download a file"""
    
    try:
        db_file = await file_handler.get_file(
            file_id=file_id,
            user_id=current_user.id,
            session=session
        )
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        file_path = file_handler.get_file_path(db_file)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Return file response
        return FileResponse(
            path=str(file_path),
            filename=db_file.filename,
            media_type=db_file.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading file"
        )


@router.get("/{file_id}/thumbnail")
async def get_file_thumbnail(
    file_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    size: str = Query("medium", regex="^(small|medium|large)$")
):
    """Get file thumbnail (for images only)"""
    
    try:
        db_file = await file_handler.get_file(
            file_id=file_id,
            user_id=current_user.id,
            session=session
        )
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check if file has thumbnails
        if not db_file.mime_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thumbnails only available for images"
            )
        
        thumbnail_path = file_handler.get_thumbnail_path(db_file, size)
        
        if not thumbnail_path or not thumbnail_path.exists():
            # Return original image if thumbnail not available
            file_path = file_handler.get_file_path(db_file)
            if file_path.exists():
                return FileResponse(
                    path=str(file_path),
                    media_type=db_file.mime_type
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found on disk"
                )
        
        return FileResponse(
            path=str(thumbnail_path),
            media_type=db_file.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving thumbnail"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Delete a file"""
    
    try:
        success = await file_handler.delete_file(
            file_id=file_id,
            user_id=current_user.id,
            session=session
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file"
        )


@router.post("/{file_id}/permissions")
async def grant_file_permission(
    file_id: int,
    permission_data: dict,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Grant file access permission to another user"""
    
    user_id = permission_data.get("user_id")
    permission_type = permission_data.get("permission_type", "read")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required"
        )
    
    if permission_type not in ["read", "full"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="permission_type must be 'read' or 'full'"
        )
    
    # Verify target user exists
    target_user = session.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )
    
    try:
        await file_handler.grant_file_permission(
            session=session,
            file_id=file_id,
            user_id=current_user.id,
            granted_to_user_id=user_id,
            permission_type=permission_type
        )
        
        return {"message": "Permission granted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error granting file permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error granting permission"
        )


@router.get("/{file_id}/permissions")
async def get_file_permissions(
    file_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get file permissions (file owner or admin only)"""
    
    # Get file to check ownership
    db_file = session.get(FileUpload, file_id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if user can view permissions
    if db_file.uploaded_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view file permissions"
        )
    
    # Get permissions
    permissions = session.exec(
        select(FilePermission)
        .where(FilePermission.file_id == file_id)
    ).all()
    
    permission_list = []
    for perm in permissions:
        user = session.get(User, perm.user_id)
        permission_list.append({
            "user_id": perm.user_id,
            "user_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "permission_type": perm.permission_type,
            "granted_at": perm.granted_at.isoformat(),
            "granted_by": perm.granted_by
        })
    
    return {
        "file_id": file_id,
        "permissions": permission_list
    }


@router.get("/{file_id}/access-log")
async def get_file_access_log(
    file_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get file access log (file owner or admin only)"""
    
    # Get file to check ownership
    db_file = session.get(FileUpload, file_id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if user can view access log
    if db_file.uploaded_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view file access log"
        )
    
    # Get access log
    access_logs = session.exec(
        select(FileAccessLog)
        .where(FileAccessLog.file_id == file_id)
        .order_by(FileAccessLog.accessed_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()
    
    log_entries = []
    for log in access_logs:
        user = session.get(User, log.user_id)
        log_entries.append({
            "user_id": log.user_id,
            "user_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "action": log.action,
            "accessed_at": log.accessed_at.isoformat()
        })
    
    return {
        "file_id": file_id,
        "access_log": log_entries
    }


# Admin endpoints
@router.get("/admin/stats")
async def get_file_storage_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get file storage statistics (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        stats = file_handler.get_storage_stats(session)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving storage statistics"
        )


@router.post("/admin/cleanup")
async def cleanup_orphaned_files(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Clean up orphaned files (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        deleted_count = await file_handler.cleanup_orphaned_files(session)
        
        return {
            "message": f"Cleanup completed. {deleted_count} orphaned files removed.",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error during file cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during cleanup operation"
        )