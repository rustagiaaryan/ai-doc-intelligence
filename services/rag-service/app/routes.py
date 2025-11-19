# FILE: services/rag-service/app/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth_middleware import get_current_user
from app.schemas import QuestionRequest, QuestionResponse, RetrievedChunk
from app.retriever import vector_retriever
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ask a question about documents using RAG.

    Steps:
    1. Generate query embedding
    2. Retrieve similar chunks via vector search
    3. Build context from retrieved chunks
    4. Generate answer using LLM with context
    """
    try:
        # 1. Generate query embedding
        logger.info(f"Generating embedding for query: {request.question[:50]}...")
        query_embedding = await vector_retriever.generate_query_embedding(request.question)

        # 2. Retrieve similar chunks
        logger.info(f"Searching for similar chunks")
        similar_chunks = await vector_retriever.search_similar_chunks(
            user_id=current_user['id'],
            query_embedding=query_embedding,
            top_k=request.top_k,
            document_ids=request.document_ids,
            db=db
        )

        if not similar_chunks:
            return QuestionResponse(
                question=request.question,
                answer="I couldn't find any relevant information in your documents to answer this question.",
                retrieved_chunks=[],
                total_chunks_found=0
            )

        # 3. Build context from retrieved chunks
        context_parts = []
        total_length = 0

        for chunk in similar_chunks:
            chunk_text = chunk["chunk_text"]
            if total_length + len(chunk_text) > settings.MAX_CONTEXT_LENGTH:
                break
            context_parts.append(chunk_text)
            total_length += len(chunk_text)

        context = "\n\n".join(context_parts)

        # 4. Generate answer using LLM
        logger.info("Generating answer with LLM")
        system_prompt = """You are a helpful assistant that answers questions based on provided document context.
Only use information from the context provided. If the context doesn't contain enough information to answer the question, say so.
Be concise and accurate."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.question}"}
        ]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.LLM_PROXY_URL}/llm/chat/completions",
                json={
                    "messages": messages,
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            llm_response = response.json()
            answer = llm_response["content"]

        # 5. Return response
        retrieved_chunks_response = [
            RetrievedChunk(
                chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                chunk_text=chunk["chunk_text"][:500] + "..." if len(chunk["chunk_text"]) > 500 else chunk["chunk_text"],
                similarity_score=chunk["similarity_score"],
                chunk_index=chunk["chunk_index"]
            )
            for chunk in similar_chunks
        ]

        return QuestionResponse(
            question=request.question,
            answer=answer,
            retrieved_chunks=retrieved_chunks_response,
            total_chunks_found=len(similar_chunks)
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )
