from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    VOLUNTEER = "volunteer"
    ORG_ADMIN = "org_admin"
    PLATFORM_MOD = "platform_mod"


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    role: UserRole = Field(default=UserRole.VOLUNTEER)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class UserCreate(UserBase):
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(SQLModel):
    refresh_token: str
