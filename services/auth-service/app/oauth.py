# FILE: services/auth-service/app/oauth.py

from authlib.integrations.starlette_client import OAuth
from app.config import settings
import httpx
from typing import Optional, Dict, Any


# Initialize OAuth
oauth = OAuth()

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


async def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Fetch user information from Google using an access token.

    Args:
        access_token: Google OAuth access token

    Returns:
        User information dict or None if request fails
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return None


async def exchange_code_for_token(code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
    """
    Exchange authorization code for access token.

    Args:
        code: Authorization code from Google
        redirect_uri: Redirect URI used in the initial auth request

    Returns:
        Token response dict or None if exchange fails
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return None
