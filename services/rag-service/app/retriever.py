# FILE: services/rag-service/app/retriever.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models import DocumentChunk
from app.config import settings
import httpx
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class VectorRetriever:
    """Retrieve relevant document chunks using vector similarity search."""

    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for the query using LLM Proxy.

        Args:
            query: Query text

        Returns:
            Query embedding vector
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.LLM_PROXY_URL}/llm/embeddings",
                    json={
                        "texts": [query],
                        "model": "text-embedding-3-small"
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["embeddings"][0]
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    async def search_similar_chunks(
        self,
        user_id: str,
        query_embedding: List[float],
        top_k: int = None,
        document_ids: Optional[List[str]] = None,
        db: AsyncSession = None
    ) -> List[dict]:
        """
        Search for similar chunks using cosine similarity.

        Args:
            user_id: User ID (for filtering)
            query_embedding: Query embedding vector
            top_k: Number of results to return
            document_ids: Optional list of document IDs to filter
            db: Database session

        Returns:
            List of similar chunks with similarity scores
        """
        top_k = top_k or settings.TOP_K_RESULTS

        # Build query with pgvector cosine similarity
        # Pass the embedding as a list - asyncpg will handle the conversion
        if document_ids:
            doc_filter = "AND document_id = ANY(:doc_ids)"
            params = {
                "user_id": user_id,
                "embedding": query_embedding,  # Pass as list
                "top_k": top_k,
                "threshold": settings.SIMILARITY_THRESHOLD,
                "doc_ids": document_ids
            }
        else:
            doc_filter = ""
            params = {
                "user_id": user_id,
                "embedding": query_embedding,  # Pass as list
                "top_k": top_k,
                "threshold": settings.SIMILARITY_THRESHOLD
            }

        query = text(f"""
            SELECT
                id,
                document_id,
                chunk_text,
                chunk_index,
                1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM document_chunks
            WHERE user_id = :user_id
            {doc_filter}
            AND embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
        """)

        logger.info(f"Executing vector search query with params: user_id={user_id}, top_k={top_k}, threshold={settings.SIMILARITY_THRESHOLD}, doc_ids={document_ids}")

        result = await db.execute(query, params)
        rows = result.fetchall()

        logger.info(f"Vector search returned {len(rows)} rows")

        chunks = []
        for row in rows:
            similarity = float(row[4])
            logger.info(f"Chunk {row[0][:8]}... similarity: {similarity} (threshold: {settings.SIMILARITY_THRESHOLD})")
            if similarity >= settings.SIMILARITY_THRESHOLD:
                chunks.append({
                    "chunk_id": row[0],
                    "document_id": row[1],
                    "chunk_text": row[2],
                    "chunk_index": row[3],
                    "similarity_score": similarity
                })

        logger.info(f"Returning {len(chunks)} chunks after threshold filtering")
        return chunks


# Singleton instance
vector_retriever = VectorRetriever()
