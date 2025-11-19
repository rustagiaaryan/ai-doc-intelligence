# FILE: services/document-service/app/auth_middleware.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from app.config import settings
from typing import Optional

security = HTTPBearer(auto_error=False)


async def verify_token_with_auth_service(token: str) -> Optional[dict]:
    """
    Verify token by calling the auth service /auth/me endpoint.

    Args:
        token: JWT access token

    Returns:
        User info dict if valid, None otherwise
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            print(f"Auth service response: {response.status_code}")
            if response.status_code != 200:
                print(f"Auth service error: {response.text}")
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"Auth service exception: {e}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    FastAPI dependency to get current authenticated user.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        User info dict

    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Verify token with auth service
    user_info = await verify_token_with_auth_service(token)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_info
