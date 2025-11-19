# FILE: services/ingestion-worker/app/models.py

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base
import uuid


class DocumentChunk(Base):
    """Document chunk model with vector embeddings."""

    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    # Chunk information
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_size = Column(Integer, nullable=False)

    # Vector embedding (1536 dimensions for OpenAI text-embedding-3-small)
    embedding = Column(Vector(1536), nullable=True)

    # Metadata
    page_number = Column(Integer, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
