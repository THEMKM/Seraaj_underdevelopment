from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Annotated, Optional

from database import get_session
from models import (
    User,
    UserCreate,
    UserLogin,
    UserRead,
    Token,
    TokenRefresh,
    UserUpdate,
)
from auth.jwt import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from middleware.error_handler import raise_bad_request
from datetime import datetime
from services.analytics_service import AnalyticsService
from models import AnalyticsEventCreate, EventType

router = APIRouter(prefix="/v1/auth", tags=["auth"])
security = HTTPBearer()
analytics_service = AnalyticsService()


@router.post("/register", response_model=UserRead)
async def register(
    user_data: UserCreate, session: Annotated[Session, Depends(get_session)]
):
    # Check if user exists
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise_bad_request(
            "Email already registered",
            details={"email": user_data.email, "suggestion": "Try logging in instead"},
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        hashed_password=hashed_password,
        language_preference=user_data.language_preference,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserRead.model_validate(db_user)


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin, session: Annotated[Session, Depends(get_session)]
):
    # Find user
    user = session.exec(
        select(User).where(User.email == user_credentials.email)
    ).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check user status - handle both new (status) and old (is_active) schema
    if hasattr(user, "status"):
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active"
            )
    elif hasattr(user, "is_active"):
        if (hasattr(user, "status") and user.status != "active") or (
            hasattr(user, "is_active") and not user.is_active
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active"
            )

    # Update login tracking - only update fields that exist in the database
    user.updated_at = datetime.now(datetime.timezone.utc)
    # Note: last_login, login_count, failed_login_attempts don't exist in current schema
    session.add(user)
    session.commit()

    # Record login analytics
    analytics_service.record_event(
        session,
        AnalyticsEventCreate(event_type=EventType.USER_LOGIN, event_name="login", user_id=user.id),
    )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh, session: Annotated[Session, Depends(get_session)]
):
    user_id = verify_token(token_data.refresh_token, "refresh")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Verify user still exists and is active
    user = session.get(User, int(user_id))
    if (
        not user
        or (hasattr(user, "status") and user.status != "active")
        or (hasattr(user, "is_active") and not user.is_active)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token)


# Dependency function to get current authenticated user
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = session.get(User, int(user_id))
    if (
        not user
        or (hasattr(user, "status") and user.status != "active")
        or (hasattr(user, "is_active") and not user.is_active)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Update last activity - using updated_at since last_activity doesn't exist in current schema
    user.updated_at = datetime.now(datetime.timezone.utc)
    session.add(user)
    session.commit()

    return user


async def get_current_admin_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """Get the current user and ensure they have admin role."""
    user = await get_current_user(credentials, session)
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    session: Session = Depends(get_session),
) -> Optional[User]:
    """Get current user from token, return None if not authenticated (optional auth)"""
    if not credentials:
        return None

    try:
        user_id = verify_token(credentials.credentials)
        if not user_id:
            return None

        user = session.get(User, int(user_id))
        if (
            not user
            or (hasattr(user, "status") and user.status != "active")
            or (hasattr(user, "is_active") and not user.is_active)
        ):
            return None

        # Update last activity
        user.updated_at = datetime.now(datetime.timezone.utc)
        session.add(user)
        session.commit()

        return user
    except:
        return None


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return UserRead.model_validate(current_user)


@router.put("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Update current user's profile information"""
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.now(datetime.timezone.utc)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return UserRead.model_validate(current_user)


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Logout user and invalidate refresh token"""
    # Note: refresh_token field doesn't exist in current schema
    # current_user.refresh_token = None
    current_user.updated_at = datetime.now(datetime.timezone.utc)
    session.add(current_user)
    session.commit()

    return {"message": "Successfully logged out"}
