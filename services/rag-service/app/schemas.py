# FILE: services/rag-service/app/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional


class QuestionRequest(BaseModel):
    """Request schema for asking a question."""
    question: str = Field(..., min_length=1, description="Question to ask about documents")
    document_ids: Optional[List[str]] = Field(None, description="Limit search to specific documents")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of chunks to retrieve")


class RetrievedChunk(BaseModel):
    """Schema for a retrieved document chunk."""
    chunk_id: str
    document_id: str
    chunk_text: str
    similarity_score: float
    chunk_index: int


class QuestionResponse(BaseModel):
    """Response schema for a question."""
    question: str
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    total_chunks_found: int
    cached: bool = Field(False, description="Whether response was served from cache")
