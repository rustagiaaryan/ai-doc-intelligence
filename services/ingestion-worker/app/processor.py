# FILE: services/ingestion-worker/app/processor.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import DocumentChunk
from app.text_extractor import TextExtractor
from app.chunker import TextChunker
import httpx
from app.config import settings
import logging
from typing import List

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents: extract text, chunk, and generate embeddings."""

    def __init__(self):
        self.text_extractor = TextExtractor()
        self.chunker = TextChunker()

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using LLM Proxy service.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.LLM_PROXY_URL}/llm/embeddings",
                    json={
                        "texts": texts,
                        "model": "text-embedding-3-small"
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["embeddings"]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    async def process_document(
        self,
        document_id: str,
        user_id: str,
        file_bytes: bytes,
        file_extension: str,
        db: AsyncSession
    ) -> dict:
        """
        Process a document: extract text, chunk, generate embeddings, and store.

        Args:
            document_id: Document ID
            user_id: User ID
            file_bytes: File content as bytes
            file_extension: File extension
            db: Database session

        Returns:
            Processing result dict
        """
        try:
            # 1. Extract text
            logger.info(f"Extracting text from document {document_id}")
            text = self.text_extractor.extract_text(file_bytes, file_extension)

            if not text or not text.strip():
                raise ValueError("No text content extracted from document")

            # 2. Chunk text
            logger.info(f"Chunking text for document {document_id}")
            chunks = self.chunker.chunk_text(text)

            if not chunks:
                raise ValueError("No chunks generated from document")

            logger.info(f"Generated {len(chunks)} chunks for document {document_id}")

            # 3. Generate embeddings (batch process)
            logger.info(f"Generating embeddings for document {document_id}")
            embeddings = await self.generate_embeddings(chunks)

            # 4. Store chunks with embeddings in database
            logger.info(f"Storing chunks for document {document_id}")
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    document_id=document_id,
                    user_id=user_id,
                    chunk_index=idx,
                    chunk_text=chunk_text,
                    chunk_size=len(chunk_text),
                    embedding=embedding
                )
                db.add(chunk)

            await db.commit()

            logger.info(f"Successfully processed document {document_id}")

            return {
                "status": "success",
                "document_id": document_id,
                "chunks_count": len(chunks),
                "total_characters": len(text)
            }

        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            await db.rollback()
            raise


# Singleton instance
document_processor = DocumentProcessor()
