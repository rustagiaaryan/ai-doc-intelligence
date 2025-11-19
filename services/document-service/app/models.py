# FILE: services/document-service/app/models.py

from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Document(Base):
    """Document model for storing file metadata."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)

    # File information
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_extension = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    mime_type = Column(String, nullable=True)

    # S3 storage information
    s3_key = Column(String, nullable=False, unique=True)
    s3_bucket = Column(String, nullable=False)

    # Processing status
    status = Column(String, default="uploaded")  # uploaded, processing, processed, failed
    processing_error = Column(Text, nullable=True)

    # Metadata
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
