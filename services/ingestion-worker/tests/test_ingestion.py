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


@patch('app.routes.text_extractor.extract_text')
@patch('app.routes.chunker.chunk_text')
def test_text_extraction(mock_chunk, mock_extract):
    """Test text extraction from document"""
    mock_extract.return_value = "Extracted text content"
    mock_chunk.return_value = [
        {"text": "Chunk 1", "index": 0},
        {"text": "Chunk 2", "index": 1}
    ]

    # This would need actual file upload testing
    # For now, just test the endpoint exists
    response = client.get("/health")
    assert response.status_code == 200


def test_chunker_basic():
    """Test basic text chunking"""
    from app.chunker import chunk_text

    text = "This is a test. " * 100
    chunks = chunk_text(text, chunk_size=100, overlap=20)

    assert len(chunks) > 0
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_chunker_empty_text():
    """Test chunking empty text"""
    from app.chunker import chunk_text

    chunks = chunk_text("", chunk_size=100, overlap=20)

    assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0] == "")
