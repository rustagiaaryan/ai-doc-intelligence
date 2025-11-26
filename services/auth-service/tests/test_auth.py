import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "auth-service"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "auth-service"


@patch('app.routes.google.oauth2.id_token.verify_oauth2_token')
@patch('app.routes.crud.get_user_by_email')
@patch('app.routes.crud.create_user')
def test_google_auth_new_user(mock_create_user, mock_get_user, mock_verify_token):
    """Test Google OAuth with new user"""
    # Mock Google token verification
    mock_verify_token.return_value = {
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': 'https://example.com/pic.jpg',
        'sub': 'google-123'
    }

    # Mock user doesn't exist
    mock_get_user.return_value = None

    # Mock user creation
    mock_user = MagicMock()
    mock_user.id = 'user-123'
    mock_user.email = 'test@example.com'
    mock_user.name = 'Test User'
    mock_create_user.return_value = mock_user

    response = client.post("/auth/google", json={"token": "fake-google-token"})

    # Should create new user and return token
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@patch('app.routes.google.oauth2.id_token.verify_oauth2_token')
def test_google_auth_invalid_token(mock_verify_token):
    """Test Google OAuth with invalid token"""
    # Mock token verification failure
    mock_verify_token.side_effect = ValueError("Invalid token")

    response = client.post("/auth/google", json={"token": "invalid-token"})

    assert response.status_code == 401


def test_verify_token_no_token():
    """Test verify endpoint without token"""
    response = client.get("/auth/verify")
    assert response.status_code == 403


@patch('app.routes.jwt.decode')
def test_verify_token_valid(mock_decode):
    """Test verify endpoint with valid token"""
    mock_decode.return_value = {"sub": "user-123", "email": "test@example.com"}

    response = client.get(
        "/auth/verify",
        headers={"Authorization": "Bearer fake-jwt-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@patch('app.routes.jwt.decode')
def test_verify_token_invalid(mock_decode):
    """Test verify endpoint with invalid token"""
    mock_decode.side_effect = Exception("Invalid token")

    response = client.get(
        "/auth/verify",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
