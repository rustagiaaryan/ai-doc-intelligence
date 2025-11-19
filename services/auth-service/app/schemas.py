# FILE: services/auth-service/app/schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    oauth_provider: str = "google"
    oauth_provider_id: str
    picture: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    picture: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth callback."""
    code: str
    redirect_uri: str


class GoogleUserInfo(BaseModel):
    """Schema for Google user information."""
    id: str
    email: EmailStr
    verified_email: bool
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
