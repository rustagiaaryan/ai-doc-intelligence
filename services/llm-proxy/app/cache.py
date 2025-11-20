# FILE: services/llm-proxy/app/cache.py

import json
import hashlib
from typing import Optional, Any
import redis.asyncio as redis
from app.config import settings


class RedisCache:
    """Redis cache manager for LLM responses."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.ttl = settings.CACHE_TTL_SECONDS

    async def connect(self):
        """Connect to Redis."""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()

    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """
        Generate a deterministic cache key from parameters.

        Args:
            prefix: Key prefix (e.g., 'embedding', 'chat')
            **kwargs: Parameters to hash

        Returns:
            Cache key string
        """
        # Sort kwargs to ensure consistent ordering
        sorted_params = json.dumps(kwargs, sort_keys=True)
        param_hash = hashlib.sha256(sorted_params.encode()).hexdigest()[:16]
        return f"{prefix}:{param_hash}"

    async def get_embedding(self, text: str, model: str) -> Optional[list[float]]:
        """
        Retrieve cached embedding for text.

        Args:
            text: Input text
            model: Embedding model name

        Returns:
            Cached embedding vector or None if not found
        """
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(
                "embedding",
                text=text,
                model=model
            )

            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            return None

        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set_embedding(self, text: str, model: str, embedding: list[float]) -> bool:
        """
        Cache embedding for text.

        Args:
            text: Input text
            model: Embedding model name
            embedding: Embedding vector to cache

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(
                "embedding",
                text=text,
                model=model
            )

            await self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(embedding)
            )
            return True

        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def get_chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> Optional[dict]:
        """
        Retrieve cached chat completion.

        Args:
            messages: Chat messages
            model: Model name
            temperature: Temperature parameter
            max_tokens: Max tokens parameter

        Returns:
            Cached response or None if not found
        """
        if not self.redis_client:
            return None

        # Only cache deterministic responses (temperature = 0)
        if temperature != 0:
            return None

        try:
            cache_key = self._generate_cache_key(
                "chat",
                messages=messages,
                model=model,
                max_tokens=max_tokens
            )

            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            return None

        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set_chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        response: dict
    ) -> bool:
        """
        Cache chat completion response.

        Args:
            messages: Chat messages
            model: Model name
            temperature: Temperature parameter
            max_tokens: Max tokens parameter
            response: Response to cache

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        # Only cache deterministic responses (temperature = 0)
        if temperature != 0:
            return False

        try:
            cache_key = self._generate_cache_key(
                "chat",
                messages=messages,
                model=model,
                max_tokens=max_tokens
            )

            await self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(response)
            )
            return True

        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        if not self.redis_client:
            return {"status": "disconnected"}

        try:
            info = await self.redis_client.info("stats")
            return {
                "status": "connected",
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_keys": await self.redis_client.dbsize()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global cache instance
cache = RedisCache()
