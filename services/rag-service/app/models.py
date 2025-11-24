# FILE: services/rag-service/app/models.py

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base


class DocumentChunk(Base):
    """Document chunk model (read-only for RAG service)."""

    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    page_number = Column(Integer, nullable=True)
    chunk_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Conversation(Base):
    """Conversation model for chat history."""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    document_id = Column(String, nullable=True, index=True)
    title = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model for individual chat messages."""

    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    source_chunks = Column(Text, nullable=True)  # JSON string of source chunks with scores
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")
