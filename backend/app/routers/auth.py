"""Authentication endpoints for registration, login, logout, and session check."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

INVALID_CREDENTIALS_MSG = "Invalid email or password"


def set_auth_cookie(response: Response, token: str) -> None:
    """Helper to attach the JWT token in an httpOnly SameSite cookie."""
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
@limiter.limit("10/minute")
async def register(
    request: Request,
    response: Response,
    payload: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new user account, hash password with Argon2, and set cookie."""
    # Enforce case-insensitive email uniqueness
    normalized_email = payload.email.lower()
    stmt = select(User).where(func.lower(User.email) == normalized_email)
    existing_user = (await db.execute(stmt)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Hash password with Argon2id and create user
    hashed_pwd = hash_password(payload.password)
    user = User(
        name=payload.name,
        email=normalized_email,
        password_hash=hashed_pwd,
        role=UserRole.STUDENT,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Deliver JWT via secure httpOnly cookie (never in JSON body)
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    set_auth_cookie(response, token)

    return user


@router.post(
    "/login",
    response_model=UserResponse,
    summary="Authenticate and receive session cookie",
)
@limiter.limit("20/minute")
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Verify credentials and set httpOnly authentication cookie."""
    normalized_email = payload.email.lower()
    stmt = select(User).where(func.lower(User.email) == normalized_email)
    user = (await db.execute(stmt)).scalar_one_or_none()

    # Generic error preventing account enumeration
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_CREDENTIALS_MSG,
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated. Contact your placement coordinator.",
        )

    # Deliver JWT via secure httpOnly cookie (never in JSON body)
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    set_auth_cookie(response, token)

    return user


@router.post(
    "/logout",
    summary="Invalidate session and clear cookie",
)
async def logout(response: Response):
    """Clear authentication cookie on client."""
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/",
    )
    return {"status": "ok", "message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated student profile",
)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Return the profile of the currently authenticated user."""
    return current_user
