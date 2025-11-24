# FILE: services/rag-service/app/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QuestionRequest(BaseModel):
    """Request schema for asking a question."""
    question: str = Field(..., min_length=1, description="Question to ask about documents")
    document_ids: Optional[List[str]] = Field(None, description="Limit search to specific documents")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of chunks to retrieve")
    conversation_id: Optional[str] = Field(None, description="Conversation ID to save to")


class ChunkPosition(BaseModel):
    """Schema for chunk position data in PDF."""
    page_number: int
    bbox: dict  # {x0, y0, x1, y1}
    page_width: float
    page_height: float


class RetrievedChunk(BaseModel):
    """Schema for a retrieved document chunk."""
    chunk_id: str
    document_id: str
    chunk_text: str
    similarity_score: float
    chunk_index: int
    page_number: Optional[int] = None
    position: Optional[ChunkPosition] = None


class QuestionResponse(BaseModel):
    """Response schema for a question."""
    question: str
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    total_chunks_found: int
    cached: bool = Field(False, description="Whether response was served from cache")
    conversation_id: Optional[str] = Field(None, description="ID of conversation this was saved to")


# Chat History Schemas
class MessageSchema(BaseModel):
    """Schema for a chat message."""
    id: str
    conversation_id: str
    role: str
    content: str
    source_chunks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSchema(BaseModel):
    """Schema for a conversation."""
    id: str
    user_id: str
    document_id: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationSchema):
    """Schema for a conversation with its messages."""
    messages: List[MessageSchema] = []


class ConversationListResponse(BaseModel):
    """Response schema for listing conversations."""
    conversations: List[ConversationSchema]
    total: int


class CreateConversationRequest(BaseModel):
    """Request schema for creating a conversation."""
    document_id: Optional[str] = None
    title: Optional[str] = Field(None, max_length=500)
