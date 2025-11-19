# FILE: services/llm-proxy/app/routes.py

from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse
)
from app.llm_clients import openai_client, anthropic_client
from app.config import settings

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """
    Generate chat completion using specified LLM provider.

    Supports OpenAI and Anthropic models.
    """
    provider = request.provider or settings.DEFAULT_PROVIDER

    # Convert messages to dict format
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    try:
        if provider == "openai":
            response = await openai_client.chat_completion(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            return ChatCompletionResponse(
                content=response["content"],
                model=response["model"],
                provider="openai",
                usage=response["usage"],
                finish_reason=response["finish_reason"]
            )

        elif provider == "anthropic":
            response = await anthropic_client.chat_completion(
                messages=messages,
                model=request.model or "claude-3-sonnet-20240229",
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            return ChatCompletionResponse(
                content=response["content"],
                model=response["model"],
                provider="anthropic",
                usage=response["usage"],
                finish_reason=response["finish_reason"]
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider}. Use 'openai' or 'anthropic'."
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM API error: {str(e)}"
        )


@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    """
    Generate embeddings for text using OpenAI.

    Currently only supports OpenAI embedding models.
    """
    try:
        embeddings = await openai_client.create_embeddings(
            texts=request.texts,
            model=request.model
        )

        return EmbeddingResponse(
            embeddings=embeddings,
            model=request.model or settings.DEFAULT_EMBEDDING_MODEL,
            num_embeddings=len(embeddings)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding API error: {str(e)}"
        )
