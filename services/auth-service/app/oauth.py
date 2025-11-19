# FILE: services/auth-service/app/oauth.py

from authlib.integrations.starlette_client import OAuth
from app.config import settings
import httpx
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests


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


async def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Google JWT token (ID token from @react-oauth/google).

    Args:
        token: Google JWT token (credential)

    Returns:
        Decoded token payload or None if verification fails
    """
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Token is valid, return the decoded information
        return {
            'id': idinfo['sub'],
            'email': idinfo['email'],
            'verified_email': idinfo.get('email_verified', False),
            'name': idinfo.get('name'),
            'given_name': idinfo.get('given_name'),
            'family_name': idinfo.get('family_name'),
            'picture': idinfo.get('picture')
        }
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None
