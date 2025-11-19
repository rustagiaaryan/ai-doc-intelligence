# FILE: services/ingestion-worker/app/routes.py

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from app.database import get_db
from app.processor import document_processor
import aioboto3
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/process", tags=["Processing"])


class ProcessDocumentRequest(BaseModel):
    """Request to process a document."""
    document_id: str
    user_id: str
    s3_key: str
    file_extension: str


class ProcessDocumentResponse(BaseModel):
    """Response from document processing."""
    status: str
    document_id: str
    chunks_count: int
    total_characters: int


@router.post("/document", response_model=ProcessDocumentResponse)
async def process_document(
    request: ProcessDocumentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process a document: download from S3, extract text, chunk, embed, and store.
    """
    try:
        # Download file from S3
        logger.info(f"Downloading document {request.document_id} from S3")
        session = aioboto3.Session(
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
        )

        async with session.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            use_ssl=settings.USE_SSL
        ) as s3:
            response = await s3.get_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=request.s3_key
            )
            async with response['Body'] as stream:
                file_bytes = await stream.read()

        # Process document
        result = await document_processor.process_document(
            document_id=request.document_id,
            user_id=request.user_id,
            file_bytes=file_bytes,
            file_extension=request.file_extension,
            db=db
        )

        # Update document status in documents table (if it exists)
        try:
            await db.execute(
                text("""
                    UPDATE documents
                    SET status = 'completed',
                        processed_at = NOW()
                    WHERE id = :doc_id
                """),
                {"doc_id": request.document_id}
            )
            await db.commit()
        except Exception as e:
            logger.warning(f"Could not update document status: {e}")

        return ProcessDocumentResponse(**result)

    except Exception as e:
        logger.error(f"Error processing document {request.document_id}: {e}")

        # Update document status to failed
        try:
            await db.execute(
                text("""
                    UPDATE documents
                    SET status = 'failed',
                        processing_error = :error
                    WHERE id = :doc_id
                """),
                {"doc_id": request.document_id, "error": str(e)}
            )
            await db.commit()
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )
