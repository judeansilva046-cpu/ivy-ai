"""
Distributed Caching Layer
Redis-based distributed cache with clustering support
"""
import json
import asyncio
from typing import Optional, Any, List
from datetime import datetime, timedelta
import aioredis
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DistributedCache:
    """Distributed cache using Redis"""

    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.local_cache: dict = {}
        self.ttl_map: dict = {}

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
            logger.info("Connected to Redis cache")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Try Redis first
            if self.redis:
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)

            # Fall back to local cache
            if key in self.local_cache:
                return self.local_cache[key]

            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600  # seconds
    ):
        """Set value in cache"""
        try:
            json_value = json.dumps(value)

            # Set in Redis
            if self.redis:
                await self.redis.setex(
                    key,
                    ttl,
                    json_value
                )

            # Set in local cache
            self.local_cache[key] = value
            self.ttl_map[key] = datetime.utcnow() + timedelta(seconds=ttl)

            logger.debug(f"Cache set: {key}")
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str):
        """Delete value from cache"""
        try:
            if self.redis:
                await self.redis.delete(key)

            if key in self.local_cache:
                del self.local_cache[key]

            if key in self.ttl_map:
                del self.ttl_map[key]

            logger.debug(f"Cache delete: {key}")
            return True

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def invalidate_pattern(self, pattern: str):
        """Invalidate keys matching pattern"""
        try:
            if self.redis:
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)

            # Invalidate local cache
            matching_keys = [k for k in self.local_cache.keys() if pattern in k]
            for key in matching_keys:
                del self.local_cache[key]
                if key in self.ttl_map:
                    del self.ttl_map[key]

            logger.debug(f"Cache invalidated: {pattern}")
            return True

        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return False

    async def clear_local(self):
        """Clear local cache"""
        self.local_cache.clear()
        self.ttl_map.clear()
        logger.info("Local cache cleared")

    async def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            info = {"local_keys": len(self.local_cache)}

            if self.redis:
                redis_info = await self.redis.info()
                info.update({
                    "redis_used_memory": redis_info.get("used_memory", 0),
                    "redis_connected_clients": redis_info.get("connected_clients", 0),
                    "redis_total_commands": redis_info.get("total_commands_processed", 0),
                })

            return info

        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}

    async def set_distributed_lock(
        self,
        lock_key: str,
        ttl: int = 10
    ) -> bool:
        """Set distributed lock"""
        try:
            if self.redis:
                # Use SET with NX (only if not exists)
                result = await self.redis.set(
                    lock_key,
                    "1",
                    expire=ttl,
                    exist=False
                )
                return result is True

            return True

        except Exception as e:
            logger.error(f"Lock error: {e}")
            return False

    async def release_distributed_lock(self, lock_key: str):
        """Release distributed lock"""
        try:
            if self.redis:
                await self.redis.delete(lock_key)
            return True

        except Exception as e:
            logger.error(f"Unlock error: {e}")
            return False

    async def increment_counter(
        self,
        counter_key: str,
        increment: int = 1,
        ttl: int = 3600
    ) -> int:
        """Increment counter with TTL"""
        try:
            if self.redis:
                value = await self.redis.incr(counter_key)
                await self.redis.expire(counter_key, ttl)
                return value

            # Fallback to local counter
            if counter_key not in self.local_cache:
                self.local_cache[counter_key] = 0

            self.local_cache[counter_key] += increment
            self.ttl_map[counter_key] = datetime.utcnow() + timedelta(seconds=ttl)
            return self.local_cache[counter_key]

        except Exception as e:
            logger.error(f"Counter error: {e}")
            return 0

    async def warm_cache(self, data: dict):
        """Pre-warm cache with data"""
        try:
            for key, value in data.items():
                await self.set(key, value, ttl=3600)

            logger.info(f"Cache warmed with {len(data)} entries")
            return True

        except Exception as e:
            logger.error(f"Warm cache error: {e}")
            return False


# Singleton instance
_cache = None


async def get_distributed_cache() -> DistributedCache:
    """Get distributed cache singleton"""
    global _cache
    if _cache is None:
        _cache = DistributedCache()
        await _cache.connect()
    return _cache
