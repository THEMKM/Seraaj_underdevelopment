from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, JSON, Column


class FileType(str, Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"


class FileStatus(str, Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"


class FileVisibility(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    ORGANIZATION = "organization"  # Visible to organization members
    VERIFIED_ONLY = "verified_only"  # Visible to verified users only


class UploadCategory(str, Enum):
    PROFILE_PICTURE = "profile_picture"
    ORGANIZATION_LOGO = "organization_logo"
    OPPORTUNITY_IMAGE = "opportunity_image"
    DOCUMENT = "document"
    CERTIFICATE = "certificate"
    SKILL_VERIFICATION = "skill_verification"
    APPLICATION_ATTACHMENT = "application_attachment"
    MESSAGE_ATTACHMENT = "message_attachment"
    GENERAL = "general"


class FileUploadBase(SQLModel):
    # File Information
    filename: str
    original_filename: str
    file_path: str
    file_url: Optional[str] = None
    
    # File Properties
    file_type: FileType
    mime_type: str
    file_size: int  # in bytes
    
    # Status and Processing
    status: FileStatus = Field(default=FileStatus.UPLOADING, index=True)
    processing_status: Optional[str] = None
    error_message: Optional[str] = None
    
    # Ownership and Access
    uploaded_by: int = Field(foreign_key="users.id", index=True)
    visibility: FileVisibility = Field(default=FileVisibility.PRIVATE)
    upload_category: UploadCategory = Field(default=UploadCategory.GENERAL, index=True)
    
    # Context - what this file is related to
    related_entity_type: Optional[str] = None  # user, volunteer, organization, opportunity, application
    related_entity_id: Optional[int] = None
    
    # Image-specific properties
    width: Optional[int] = None
    height: Optional[int] = None
    
    # Document-specific properties
    page_count: Optional[int] = None
    
    # Video/Audio-specific properties
    duration: Optional[float] = None  # in seconds
    
    # Thumbnails and Variants
    thumbnail_url: Optional[str] = None
    variants: List[dict] = Field(default_factory=list, sa_column=Column(JSON))  # Different sizes/formats
    
    # Security and Scanning
    virus_scanned: bool = Field(default=False)
    virus_scan_result: Optional[str] = None
    content_moderated: bool = Field(default=False)
    moderation_result: Optional[str] = None
    
    # Usage Tracking
    download_count: int = Field(default=0)
    view_count: int = Field(default=0)
    last_accessed: Optional[datetime] = None
    
    # Expiration
    expires_at: Optional[datetime] = None
    
    # Metadata
    alt_text: Optional[str] = None  # For accessibility
    caption: Optional[str] = None
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    entity_metadata: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))


class FileUpload(FileUploadBase, table=True):
    __tablename__ = "file_uploads"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class FileUploadCreate(SQLModel):
    filename: str
    original_filename: str
    file_type: FileType
    mime_type: str
    file_size: int
    upload_category: UploadCategory = UploadCategory.GENERAL
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    visibility: FileVisibility = FileVisibility.PRIVATE
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    tags: List[str] = []


class FileUploadRead(FileUploadBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class FileUploadUpdate(SQLModel):
    filename: Optional[str] = None
    status: Optional[FileStatus] = None
    file_url: Optional[str] = None
    visibility: Optional[FileVisibility] = None
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    tags: Optional[List[str]] = None
    entity_metadata: Optional[dict] = None


# Model for tracking file access/downloads
class FileAccessLog(SQLModel, table=True):
    __tablename__ = "file_access_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: int = Field(foreign_key="file_uploads.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    
    access_type: str  # view, download, thumbnail
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Model for file sharing/permissions
class FilePermission(SQLModel, table=True):
    __tablename__ = "file_permissions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    file_id: int = Field(foreign_key="file_uploads.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    organization_id: Optional[int] = Field(default=None, foreign_key="organisations.id", index=True)
    
    permission_type: str  # view, download, edit, delete
    granted_by: int = Field(foreign_key="users.id")
    
    expires_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)