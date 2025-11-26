import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch('app.routes.get_current_user')
@patch('app.routes.crud.get_documents_by_user')
async def test_list_documents(mock_get_docs, mock_get_user):
    """Test listing documents"""
    mock_get_user.return_value = {"user_id": "user-123"}

    mock_doc = MagicMock()
    mock_doc.id = "doc-123"
    mock_doc.filename = "test.pdf"
    mock_doc.status = "completed"
    mock_get_docs.return_value = [mock_doc]

    response = client.get(
        "/documents/",
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200


@patch('app.routes.get_current_user')
@patch('app.routes.s3_client.generate_presigned_url')
@patch('app.routes.crud.get_document')
async def test_download_document(mock_get_doc, mock_presigned, mock_get_user):
    """Test downloading document"""
    mock_get_user.return_value = {"user_id": "user-123"}

    mock_doc = MagicMock()
    mock_doc.id = "doc-123"
    mock_doc.user_id = "user-123"
    mock_doc.s3_key = "documents/test.pdf"
    mock_get_doc.return_value = mock_doc

    mock_presigned.return_value = "https://example.com/presigned-url"

    response = client.get(
        "/documents/doc-123/download",
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "url" in data


@patch('app.routes.get_current_user')
@patch('app.routes.crud.get_document')
@patch('app.routes.crud.delete_document')
@patch('app.routes.s3_client.delete_file')
async def test_delete_document(mock_s3_delete, mock_delete, mock_get_doc, mock_get_user):
    """Test deleting document"""
    mock_get_user.return_value = {"user_id": "user-123"}

    mock_doc = MagicMock()
    mock_doc.id = "doc-123"
    mock_doc.user_id = "user-123"
    mock_doc.s3_key = "documents/test.pdf"
    mock_get_doc.return_value = mock_doc

    mock_s3_delete.return_value = True
    mock_delete.return_value = None

    response = client.delete(
        "/documents/doc-123",
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200


def test_upload_no_auth():
    """Test upload without authentication"""
    response = client.post("/documents/upload")
    assert response.status_code in [401, 403, 422]
