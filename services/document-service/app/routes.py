# FILE: services/document-service/app/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.database import get_db
from app.models import Document
from app.schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentUpdateRequest,
    PresignedUrlResponse
)
from app.auth_middleware import get_current_user
from app.s3_client import s3_client
from app.config import settings
import uuid
import os

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Query(None),
    description: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document to S3 and store metadata."""

    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lstrip('.')
    if file_extension.lower() not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_extension} not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Validate file size
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
        )

    # Generate S3 key
    doc_id = str(uuid.uuid4())
    s3_key = f"{current_user['id']}/{doc_id}/{file.filename}"

    # Upload to S3
    success = await s3_client.upload_file(
        file_data=file_content,
        s3_key=s3_key,
        content_type=file.content_type
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage"
        )

    # Create database record
    document = Document(
        id=doc_id,
        user_id=current_user['id'],
        filename=file.filename,
        original_filename=file.filename,
        file_extension=file_extension,
        file_size=file_size,
        mime_type=file.content_type,
        s3_key=s3_key,
        s3_bucket=settings.S3_BUCKET_NAME,
        status="uploaded",
        title=title,
        description=description
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        file_size=document.file_size,
        status=document.status,
        s3_key=document.s3_key,
        created_at=document.created_at
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents for the current user."""

    # Get total count
    count_query = select(func.count(Document.id)).where(Document.user_id == current_user['id'])
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get documents with pagination
    offset = (page - 1) * page_size
    query = (
        select(Document)
        .where(Document.user_id == current_user['id'])
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document metadata by ID."""

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user['id']
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update document metadata."""

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user['id']
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update fields
    if update_data.title is not None:
        document.title = update_data.title
    if update_data.description is not None:
        document.description = update_data.description

    await db.commit()
    await db.refresh(document)

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and its S3 file."""

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user['id']
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete from S3
    await s3_client.delete_file(document.s3_key)

    # Delete from database
    await db.delete(document)
    await db.commit()


@router.get("/{document_id}/download", response_model=PresignedUrlResponse)
async def get_download_url(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a presigned URL for downloading a document."""

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user['id']
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Generate presigned URL (valid for 1 hour)
    url = await s3_client.generate_presigned_url(document.s3_key, expiration=3600)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )

    return PresignedUrlResponse(url=url, expires_in=3600)
