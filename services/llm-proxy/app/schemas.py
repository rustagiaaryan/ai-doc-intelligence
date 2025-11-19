# FILE: services/llm-proxy/app/schemas.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Message(BaseModel):
    """Chat message schema."""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """Request schema for chat completion."""
    messages: List[Message]
    provider: Optional[str] = Field(None, description="LLM provider: openai or anthropic")
    model: Optional[str] = Field(None, description="Model name")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)


class ChatCompletionResponse(BaseModel):
    """Response schema for chat completion."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    finish_reason: str


class EmbeddingRequest(BaseModel):
    """Request schema for embeddings."""
    texts: List[str] = Field(..., description="List of texts to embed")
    model: Optional[str] = Field(None, description="Embedding model name")


class EmbeddingResponse(BaseModel):
    """Response schema for embeddings."""
    embeddings: List[List[float]]
    model: str
    num_embeddings: int
