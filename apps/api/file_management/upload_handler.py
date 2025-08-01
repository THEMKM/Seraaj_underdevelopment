import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import mimetypes
import logging

from fastapi import UploadFile, HTTPException, status
from sqlmodel import Session
from PIL import Image

from models import (
    FileUpload,
    FileAccessLog,
    FilePermission,
    User,
    FileType,
    UploadCategory,
)
from config.settings import settings
from .storage import LocalStorage, S3Storage

logger = logging.getLogger(__name__)


class FileUploadHandler:
    """Handle file uploads with security, validation, and storage management"""

    def __init__(self) -> None:
        self.base_upload_dir = Path(settings.file_storage.upload_dir)
        self.max_file_size = settings.file_storage.max_file_size_mb * 1024 * 1024
        # Only allow basic document and image types
        self.allowed_types = {
            "application/pdf",
            "image/png",
            "image/jpeg",
        }

        backend = getattr(settings, "FILE_STORAGE", "local")
        if backend == "s3":
            self.storage = S3Storage(settings)
        else:
            self.storage = LocalStorage(self.base_upload_dir)
            self._create_directories()

    def _create_directories(self):
        """Create necessary upload directories"""
        directories = [
            self.base_upload_dir,
            self.base_upload_dir / "profiles",
            self.base_upload_dir / "applications",
            self.base_upload_dir / "organizations",
            self.base_upload_dir / "opportunities",
            self.base_upload_dir / "temp",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file: UploadFile,
        upload_category: str,
        user_id: int,
        session: Session,
        file_description: Optional[str] = None,
        is_public: bool = False,
    ) -> FileUpload:
        """Upload and process a file"""
        # Validate and read file
        self._validate_file(file)
        content = await file.read()
        file_size = len(content)
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds limit",
            )

        sanitized = Path(file.filename).name
        file_extension = Path(sanitized).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"

        # Save using storage adapter
        stored_path = await self.storage.save(unique_filename, content)

        mime_type, _ = mimetypes.guess_type(sanitized)
        processed_info = {}
        if mime_type and mime_type.startswith("image/"):
            processed_info = await self._process_image(Path(stored_path), content)

        db_file = FileUpload(
            filename=unique_filename,
            original_filename=sanitized,
            file_path=stored_path,
            file_type=FileType.IMAGE
            if mime_type and mime_type.startswith("image/")
            else FileType.DOCUMENT,
            mime_type=mime_type or "application/octet-stream",
            file_size=file_size,
            upload_category=UploadCategory(upload_category),
            uploaded_by=user_id,
            metadata=processed_info,
            description=file_description,
            is_public=is_public,
        )

        try:
            session.add(db_file)
            session.commit()
            session.refresh(db_file)

            await self._log_access(session, db_file.id, user_id, "upload")

            session.add(db_file)
            session.commit()
            session.refresh(db_file)

            # Log access
            await self._log_access(session, db_file.id, user_id, "upload")

            logger.info(
                f"File uploaded successfully: {file.filename} -> {unique_filename}"
            )
            return db_file

        except Exception as e:
            # Clean up file if database operation fails
            p = Path(stored_path)
            if p.exists():
                p.unlink()

            logger.error(f"Error uploading file {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading file",
            )

    def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided"
            )

        # Sanitize filename to avoid path traversal
        sanitized = Path(file.filename).name
        file_extension = Path(sanitized).suffix.lower()
        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have an extension",
            )

        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file.filename)
        if mime_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_types)}",
            )

        # Note: File size validation happens during upload due to streaming

    async def _process_image(self, file_path: Path, content: bytes) -> Dict[str, Any]:
        """Process uploaded images (resize, create thumbnails, etc.)"""
        try:
            # Open image
            image = Image.open(file_path)

            # Get image info
            width, height = image.size
            format_name = image.format

            processed_info = {
                "width": width,
                "height": height,
                "format": format_name,
                "thumbnails": {},
            }

            # Create thumbnails
            thumbnail_sizes = [
                ("small", 150, 150),
                ("medium", 300, 300),
                ("large", 600, 600),
            ]

            for size_name, max_width, max_height in thumbnail_sizes:
                try:
                    # Create thumbnail
                    thumbnail = image.copy()
                    thumbnail.thumbnail(
                        (max_width, max_height), Image.Resampling.LANCZOS
                    )

                    # Save thumbnail
                    thumbnail_filename = (
                        f"{file_path.stem}_{size_name}{file_path.suffix}"
                    )
                    thumbnail_path = file_path.parent / thumbnail_filename

                    thumbnail.save(thumbnail_path, optimize=True, quality=85)

                    processed_info["thumbnails"][size_name] = {
                        "filename": thumbnail_filename,
                        "path": str(thumbnail_path),
                        "width": thumbnail.width,
                        "height": thumbnail.height,
                    }

                except Exception as e:
                    logger.warning(f"Error creating {size_name} thumbnail: {e}")

            return processed_info

        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            return {"error": str(e)}

    async def get_file(
        self, file_id: int, user_id: int, session: Session
    ) -> Optional[FileUpload]:
        """Get file information and check permissions"""

        db_file = session.get(FileUpload, file_id)
        if not db_file:
            return None

        # Check permissions
        if not await self._check_access_permission(session, db_file, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this file",
            )

        # Log access
        await self._log_access(session, file_id, user_id, "download")

        return db_file

    async def delete_file(self, file_id: int, user_id: int, session: Session) -> bool:
        """Delete a file and its associated data"""

        db_file = session.get(FileUpload, file_id)
        if not db_file:
            return False

        # Check permissions
        if not await self._check_delete_permission(session, db_file, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this file",
            )

        try:
            # Delete physical file
            file_path = Path(db_file.file_path)
            if file_path.exists():
                file_path.unlink()

            # Delete thumbnails if they exist
            if db_file.metadata and "thumbnails" in db_file.metadata:
                for thumbnail_info in db_file.metadata["thumbnails"].values():
                    thumbnail_path = Path(thumbnail_info["path"])
                    if thumbnail_path.exists():
                        thumbnail_path.unlink()

            # Delete database record
            session.delete(db_file)
            session.commit()

            # Log deletion
            await self._log_access(session, file_id, user_id, "delete")

            logger.info(f"File deleted: {db_file.filename}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting file",
            )

    async def _check_access_permission(
        self, session: Session, db_file: FileUpload, user_id: int
    ) -> bool:
        """Check if user has permission to access file"""

        # Public files are accessible to all
        if db_file.is_public:
            return True

        # Owner can always access
        if db_file.uploaded_by == user_id:
            return True

        # Check specific permissions
        permission = (
            session.query(FilePermission)
            .filter(
                FilePermission.file_id == db_file.id,
                FilePermission.user_id == user_id,
                FilePermission.permission_type.in_(["read", "full"]),
            )
            .first()
        )

        if permission:
            return True

        # Admin can access all files
        user = session.get(User, user_id)
        if user and user.role == "admin":
            return True

        return False

    async def _check_delete_permission(
        self, session: Session, db_file: FileUpload, user_id: int
    ) -> bool:
        """Check if user has permission to delete file"""

        # Owner can delete
        if db_file.uploaded_by == user_id:
            return True

        # Check specific permissions
        permission = (
            session.query(FilePermission)
            .filter(
                FilePermission.file_id == db_file.id,
                FilePermission.user_id == user_id,
                FilePermission.permission_type == "full",
            )
            .first()
        )

        if permission:
            return True

        # Admin can delete all files
        user = session.get(User, user_id)
        if user and user.role == "admin":
            return True

        return False

    async def _log_access(
        self, session: Session, file_id: int, user_id: int, action: str
    ):
        """Log file access for auditing"""
        try:
            log_entry = FileAccessLog(
                file_id=file_id,
                user_id=user_id,
                action=action,
                accessed_at=datetime.now(datetime.timezone.utc),
            )

            session.add(log_entry)
            session.commit()

        except Exception as e:
            logger.error(f"Error logging file access: {e}")

    async def grant_file_permission(
        self,
        session: Session,
        file_id: int,
        user_id: int,
        granted_to_user_id: int,
        permission_type: str = "read",
    ):
        """Grant file permission to another user"""

        db_file = session.get(FileUpload, file_id)
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        # Check if granter has permission to grant
        if not await self._check_delete_permission(session, db_file, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to grant permissions for this file",
            )

        # Check if permission already exists
        existing_permission = (
            session.query(FilePermission)
            .filter(
                FilePermission.file_id == file_id,
                FilePermission.user_id == granted_to_user_id,
            )
            .first()
        )

        if existing_permission:
            # Update existing permission
            existing_permission.permission_type = permission_type
            existing_permission.granted_at = datetime.now(datetime.timezone.utc)
        else:
            # Create new permission
            permission = FilePermission(
                file_id=file_id,
                user_id=granted_to_user_id,
                permission_type=permission_type,
                granted_by=user_id,
            )
            session.add(permission)

        session.commit()

    def get_file_path(self, db_file: FileUpload) -> Path:
        """Get the physical file path"""
        return Path(db_file.file_path)

    def get_thumbnail_path(
        self, db_file: FileUpload, size: str = "medium"
    ) -> Optional[Path]:
        """Get thumbnail path if available"""
        if not db_file.metadata or "thumbnails" not in db_file.metadata:
            return None

        thumbnail_info = db_file.metadata["thumbnails"].get(size)
        if not thumbnail_info:
            return None

        return Path(thumbnail_info["path"])

    async def cleanup_orphaned_files(self, session: Session):
        """Clean up files that exist on disk but not in database"""
        try:
            # Get all files from database
            db_files = session.query(FileUpload).all()
            db_file_paths = set(Path(f.file_path) for f in db_files)

            # Check each upload directory
            orphaned_files = []

            for category_dir in self.base_upload_dir.iterdir():
                if category_dir.is_dir():
                    for file_path in category_dir.iterdir():
                        if file_path.is_file() and file_path not in db_file_paths:
                            orphaned_files.append(file_path)

            # Delete orphaned files
            deleted_count = 0
            for file_path in orphaned_files:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting orphaned file {file_path}: {e}")

            logger.info(f"Cleaned up {deleted_count} orphaned files")
            return deleted_count

        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")
            return 0

    def get_storage_stats(self, session: Session) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            # Get file counts and sizes by category
            from sqlmodel import select, func

            stats = session.exec(
                select(
                    FileUpload.upload_category,
                    func.count(FileUpload.id).label("file_count"),
                    func.sum(FileUpload.file_size).label("total_size"),
                ).group_by(FileUpload.upload_category)
            ).all()

            category_stats = {}
            total_files = 0
            total_size = 0

            for category, count, size in stats:
                category_stats[category] = {
                    "file_count": count,
                    "total_size_bytes": size or 0,
                    "total_size_mb": round((size or 0) / (1024 * 1024), 2),
                }
                total_files += count
                total_size += size or 0

            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "categories": category_stats,
                "max_file_size_mb": round(self.max_file_size / (1024 * 1024), 2),
                "allowed_types": list(self.allowed_types),
            }

        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {"error": str(e)}


# Global file handler instance
file_handler = FileUploadHandler()
