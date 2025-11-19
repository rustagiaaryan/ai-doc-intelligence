# FILE: services/auth-service/app/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional
from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import (
    GoogleAuthRequest,
    GoogleTokenRequest,
    TokenResponse,
    TokenRefreshRequest,
    UserResponse,
    ErrorResponse
)
from app.oauth import exchange_code_for_token, get_google_user_info, verify_google_token
from app.auth_utils import create_access_token, create_refresh_token, verify_token, get_token_expiration
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    Exchange authorization code for tokens and create/update user.
    """
    # Exchange code for token
    token_data = await exchange_code_for_token(request.code, request.redirect_uri)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange authorization code"
        )

    # Get user info from Google
    user_info = await get_google_user_info(token_data['access_token'])
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch user information"
        )

    # Check if user exists
    result = await db.execute(
        select(User).where(User.oauth_provider_id == user_info['id'])
    )
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=user_info['email'],
            full_name=user_info.get('name'),
            picture=user_info.get('picture'),
            oauth_provider='google',
            oauth_provider_id=user_info['id'],
            last_login=datetime.now(timezone.utc)
        )
        db.add(user)
    else:
        # Update last login
        user.last_login = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    # Create JWT tokens
    token_payload = {"sub": user.id, "email": user.email}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    # Store refresh token in database
    refresh_token_payload = verify_token(refresh_token, token_type="refresh")
    if refresh_token_payload:
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=get_token_expiration(refresh_token)
        )
        db.add(db_refresh_token)
        await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/google/token", response_model=TokenResponse)
async def google_token_auth(
    request: GoogleTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Google JWT token authentication (from @react-oauth/google).
    Verify the JWT token and create/update user.
    """
    # Verify Google JWT token
    user_info = await verify_google_token(request.token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google token"
        )

    # Check if user exists
    result = await db.execute(
        select(User).where(User.oauth_provider_id == user_info['id'])
    )
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=user_info['email'],
            full_name=user_info.get('name'),
            picture=user_info.get('picture'),
            oauth_provider='google',
            oauth_provider_id=user_info['id'],
            last_login=datetime.now(timezone.utc)
        )
        db.add(user)
    else:
        # Update last login
        user.last_login = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    # Create JWT tokens
    token_payload = {"sub": user.id, "email": user.email}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    # Store refresh token in database
    refresh_token_payload = verify_token(refresh_token, token_type="refresh")
    if refresh_token_payload:
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=get_token_expiration(refresh_token)
        )
        db.add(db_refresh_token)
        await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Check if refresh token exists and is not revoked
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == request.refresh_token,
            RefreshToken.revoked == False
        )
    )
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or revoked"
        )

    # Check if token is expired
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    # Get user
    result = await db.execute(
        select(User).where(User.id == payload['sub'])
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    token_payload = {"sub": user.id, "email": user.email}
    new_access_token = create_access_token(token_payload)
    new_refresh_token = create_refresh_token(token_payload)

    # Revoke old refresh token
    db_token.revoked = True

    # Store new refresh token
    new_refresh_token_payload = verify_token(new_refresh_token, token_type="refresh")
    if new_refresh_token_payload:
        new_db_refresh_token = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=get_token_expiration(new_refresh_token)
        )
        db.add(new_db_refresh_token)

    await db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information from access token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token = parts[1]
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )

    result = await db.execute(
        select(User).where(User.id == payload['sub'])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.post("/logout")
async def logout(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """Logout user by revoking refresh token."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == request.refresh_token)
    )
    db_token = result.scalar_one_or_none()

    if db_token:
        db_token.revoked = True
        await db.commit()

    return {"message": "Logged out successfully"}
