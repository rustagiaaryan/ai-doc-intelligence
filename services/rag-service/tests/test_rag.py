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


@patch('app.routes.get_current_user')
@patch('app.routes.retriever.search_chunks')
@patch('app.routes.llm_client.generate_answer')
async def test_ask_question(mock_llm, mock_search, mock_user):
    """Test asking a question"""
    mock_user.return_value = {"user_id": "user-123"}

    # Mock chunk retrieval
    mock_chunk = MagicMock()
    mock_chunk.content = "Test content"
    mock_chunk.document_id = "doc-123"
    mock_chunk.chunk_index = 0
    mock_chunk.similarity_score = 0.95
    mock_search.return_value = [mock_chunk]

    # Mock LLM response
    mock_llm.return_value = "This is the answer"

    response = client.post(
        "/rag/ask",
        json={"question": "What is this about?"},
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "retrieved_chunks" in data


@patch('app.routes.get_current_user')
def test_ask_question_no_question(mock_user):
    """Test asking without a question"""
    mock_user.return_value = {"user_id": "user-123"}

    response = client.post(
        "/rag/ask",
        json={},
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 422


def test_ask_question_no_auth():
    """Test asking without authentication"""
    response = client.post(
        "/rag/ask",
        json={"question": "What is this about?"}
    )

    assert response.status_code in [401, 403]
