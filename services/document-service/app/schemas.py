# FILE: services/document-service/app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    id: str
    filename: str
    file_size: int
    status: str
    s3_key: str
    created_at: datetime


class DocumentResponse(BaseModel):
    """Response schema for document metadata."""
    id: str
    user_id: str
    filename: str
    original_filename: str
    file_extension: str
    file_size: int
    mime_type: Optional[str]
    s3_key: str
    s3_bucket: str
    status: str
    processing_error: Optional[str]
    title: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response schema for document list."""
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentUpdateRequest(BaseModel):
    """Request schema for updating document metadata."""
    title: Optional[str] = None
    description: Optional[str] = None


class PresignedUrlResponse(BaseModel):
    """Response schema for presigned download URL."""
    url: str
    expires_in: int
