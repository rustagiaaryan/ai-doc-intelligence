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


@patch('app.routes.openai_client.embeddings.create')
async def test_generate_embeddings(mock_openai):
    """Test embedding generation"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.data = [MagicMock()]
    mock_response.data[0].embedding = [0.1] * 1536
    mock_openai.return_value = mock_response

    response = client.post(
        "/llm/embeddings",
        json={"texts": ["Test text"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert "embeddings" in data
    assert len(data["embeddings"]) == 1
    assert len(data["embeddings"][0]) == 1536


@patch('app.routes.openai_client.chat.completions.create')
async def test_generate_completion(mock_openai):
    """Test chat completion"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test answer"
    mock_openai.return_value = mock_response

    response = client.post(
        "/llm/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-3.5-turbo"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "choices" in data


def test_embeddings_empty_list():
    """Test embedding generation with empty list"""
    response = client.post(
        "/llm/embeddings",
        json={"texts": []}
    )

    assert response.status_code == 422
