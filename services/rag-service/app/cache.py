# FILE: services/rag-service/app/cache.py

import json
import hashlib
from typing import Optional, Any
import redis.asyncio as redis
from app.config import settings


class RedisCache:
    """Redis cache manager for RAG query results."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.ttl = 1800  # 30 minutes cache TTL for RAG results

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
            prefix: Key prefix (e.g., 'rag_query', 'vector_search')
            **kwargs: Parameters to hash

        Returns:
            Cache key string
        """
        # Sort kwargs to ensure consistent ordering
        sorted_params = json.dumps(kwargs, sort_keys=True)
        param_hash = hashlib.sha256(sorted_params.encode()).hexdigest()[:16]
        return f"{prefix}:{param_hash}"

    async def get_query_result(
        self,
        query: str,
        document_id: Optional[str],
        user_id: str
    ) -> Optional[dict]:
        """
        Retrieve cached RAG query result.

        Args:
            query: User query text
            document_id: Optional document ID filter
            user_id: User ID for access control

        Returns:
            Cached result or None if not found
        """
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(
                "rag_query",
                query=query.lower().strip(),  # Normalize query
                document_id=document_id,
                user_id=user_id
            )

            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            return None

        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set_query_result(
        self,
        query: str,
        document_id: Optional[str],
        user_id: str,
        result: dict
    ) -> bool:
        """
        Cache RAG query result.

        Args:
            query: User query text
            document_id: Optional document ID filter
            user_id: User ID for access control
            result: Query result to cache

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(
                "rag_query",
                query=query.lower().strip(),  # Normalize query
                document_id=document_id,
                user_id=user_id
            )

            await self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(result)
            )
            return True

        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def invalidate_document_cache(self, document_id: str) -> int:
        """
        Invalidate all cached queries related to a document.

        Args:
            document_id: Document ID

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0

        try:
            # Find all keys containing this document_id
            pattern = f"rag_query:*{document_id}*"
            cursor = 0
            deleted = 0

            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )

                if keys:
                    deleted += await self.redis_client.delete(*keys)

                if cursor == 0:
                    break

            return deleted

        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return 0

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
