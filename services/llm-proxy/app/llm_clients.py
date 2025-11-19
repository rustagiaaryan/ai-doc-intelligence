# FILE: services/llm-proxy/app/llm_clients.py

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from app.config import settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI API client."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using OpenAI API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to settings)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI API parameters

        Returns:
            Response dict with 'content', 'model', 'usage' keys
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        try:
            response = await self.client.chat.completions.create(
                model=model or settings.DEFAULT_MODEL,
                messages=messages,
                temperature=temperature or settings.DEFAULT_TEMPERATURE,
                max_tokens=max_tokens or settings.DEFAULT_MAX_TOKENS,
                **kwargs
            )

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            logger.error(f"OpenAI chat completion error: {e}")
            raise

    async def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API.

        Args:
            texts: List of text strings to embed
            model: Embedding model name

        Returns:
            List of embedding vectors
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        try:
            response = await self.client.embeddings.create(
                model=model or settings.DEFAULT_EMBEDDING_MODEL,
                input=texts
            )

            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {e}")
            raise


class AnthropicClient:
    """Wrapper for Anthropic API client."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-sonnet-20240229",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Anthropic API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Anthropic API parameters

        Returns:
            Response dict with 'content', 'model', 'usage' keys
        """
        if not self.client:
            raise ValueError("Anthropic API key not configured")

        try:
            # Anthropic requires system message separately
            system_message = None
            filtered_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    filtered_messages.append(msg)

            kwargs_with_system = kwargs.copy()
            if system_message:
                kwargs_with_system["system"] = system_message

            response = await self.client.messages.create(
                model=model,
                messages=filtered_messages,
                temperature=temperature or settings.DEFAULT_TEMPERATURE,
                max_tokens=max_tokens or settings.DEFAULT_MAX_TOKENS,
                **kwargs_with_system
            )

            return {
                "content": response.content[0].text,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                "finish_reason": response.stop_reason
            }
        except Exception as e:
            logger.error(f"Anthropic chat completion error: {e}")
            raise


# Singleton instances
openai_client = OpenAIClient()
anthropic_client = AnthropicClient()
