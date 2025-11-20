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
from app.cache import cache

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """
    Generate chat completion using specified LLM provider.

    Supports OpenAI and Anthropic models.
    Caches deterministic responses (temperature=0).
    """
    provider = request.provider or settings.DEFAULT_PROVIDER

    # Convert messages to dict format
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    # Determine model
    model = request.model or (settings.DEFAULT_MODEL if provider == "openai" else "claude-3-sonnet-20240229")

    # Check cache for deterministic responses
    cached_response = await cache.get_chat_completion(
        messages=messages,
        model=model,
        temperature=request.temperature or settings.DEFAULT_TEMPERATURE,
        max_tokens=request.max_tokens
    )

    if cached_response:
        return ChatCompletionResponse(**cached_response, cached=True)

    try:
        if provider == "openai":
            response = await openai_client.chat_completion(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            result = ChatCompletionResponse(
                content=response["content"],
                model=response["model"],
                provider="openai",
                usage=response["usage"],
                finish_reason=response["finish_reason"],
                cached=False
            )

            # Cache the response
            await cache.set_chat_completion(
                messages=messages,
                model=response["model"],
                temperature=request.temperature or settings.DEFAULT_TEMPERATURE,
                max_tokens=request.max_tokens,
                response=result.model_dump(exclude={"cached"})
            )

            return result

        elif provider == "anthropic":
            response = await anthropic_client.chat_completion(
                messages=messages,
                model=request.model or "claude-3-sonnet-20240229",
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            result = ChatCompletionResponse(
                content=response["content"],
                model=response["model"],
                provider="anthropic",
                usage=response["usage"],
                finish_reason=response["finish_reason"],
                cached=False
            )

            # Cache the response
            await cache.set_chat_completion(
                messages=messages,
                model=response["model"],
                temperature=request.temperature or settings.DEFAULT_TEMPERATURE,
                max_tokens=request.max_tokens,
                response=result.model_dump(exclude={"cached"})
            )

            return result

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
    Embeddings are cached for performance.
    """
    try:
        model = request.model or settings.DEFAULT_EMBEDDING_MODEL
        embeddings = []
        cache_hits = 0

        # Check cache for each text
        for text in request.texts:
            cached_embedding = await cache.get_embedding(text=text, model=model)
            if cached_embedding:
                embeddings.append(cached_embedding)
                cache_hits += 1
            else:
                # Generate embedding via API
                text_embeddings = await openai_client.create_embeddings(
                    texts=[text],
                    model=model
                )
                embedding = text_embeddings[0]
                embeddings.append(embedding)

                # Cache the embedding
                await cache.set_embedding(text=text, model=model, embedding=embedding)

        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            num_embeddings=len(embeddings),
            cache_hits=cache_hits
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


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics.

    Returns information about cache hits, misses, and total keys.
    """
    return await cache.get_cache_stats()
