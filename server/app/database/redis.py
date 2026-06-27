"""
Redis cache connection and operations
"""
import json
from typing import Any, Optional
import redis
from config.settings import get_settings
from app.utils.logger import setup_logger
from app.utils.errors import RedisException

logger = setup_logger(__name__)
settings = get_settings()


class RedisCache:
    """Redis cache wrapper"""

    def __init__(self):
        """Initialize Redis client"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info(
                f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise RedisException(f"Redis connection failed: {str(e)}")

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            if ttl:
                self.client.setex(key, ttl, value)
            else:
                self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {str(e)}")
            raise RedisException(f"Set operation failed: {str(e)}")

    def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        try:
            value = self.client.get(key)
            if value is None:
                return None

            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Error getting key {key}: {str(e)}")
            raise RedisException(f"Get operation failed: {str(e)}")

    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key}: {str(e)}")
            raise RedisException(f"Delete operation failed: {str(e)}")

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking key {key}: {str(e)}")
            raise RedisException(f"Exists operation failed: {str(e)}")

    def ttl(self, key: str) -> int:
        """Get time to live for key"""
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for key {key}: {str(e)}")
            raise RedisException(f"TTL operation failed: {str(e)}")

    def flush_db(self) -> bool:
        """Flush entire database"""
        try:
            self.client.flushdb()
            logger.info("Flushed Redis database")
            return True
        except Exception as e:
            logger.error(f"Error flushing database: {str(e)}")
            raise RedisException(f"Flush operation failed: {str(e)}")

    def keys(self, pattern: str = "*") -> list:
        """Get keys matching pattern"""
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Error getting keys: {str(e)}")
            raise RedisException(f"Keys operation failed: {str(e)}")


# Global instance
_redis_cache = None


def get_redis_cache() -> RedisCache:
    """Get or create Redis cache instance"""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache
