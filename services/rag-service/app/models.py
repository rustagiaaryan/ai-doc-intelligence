# FILE: services/rag-service/app/models.py

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.sql import func
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
