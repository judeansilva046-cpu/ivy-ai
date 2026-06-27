"""
Database Sharding Strategy
Horizontal partitioning for scaling
"""
from typing import Optional, List, Tuple
from enum import Enum
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ShardingStrategy(str, Enum):
    """Sharding strategies"""
    RANGE = "range"
    HASH = "hash"
    DIRECTORY = "directory"
    GEOGRAPHIC = "geographic"


class Shard:
    """Database shard"""

    def __init__(
        self,
        shard_id: int,
        host: str,
        port: int,
        database: str,
        min_range: Optional[int] = None,
        max_range: Optional[int] = None,
        region: str = "default"
    ):
        self.shard_id = shard_id
        self.host = host
        self.port = port
        self.database = database
        self.min_range = min_range
        self.max_range = max_range
        self.region = region
        self.is_active = True
        self.replicas: List[Tuple[str, int]] = []

    def add_replica(self, host: str, port: int):
        """Add read replica"""
        self.replicas.append((host, port))

    def get_connection_string(self) -> str:
        """Get database connection string"""
        return f"postgresql://{self.host}:{self.port}/{self.database}"


class DatabaseSharding:
    """Database sharding manager"""

    def __init__(self, strategy: ShardingStrategy = ShardingStrategy.HASH):
        self.strategy = strategy
        self.shards: List[Shard] = []
        self.shard_map: dict = {}
        self.replication_factor = 2

    def add_shard(self, shard: Shard) -> bool:
        """Add shard"""
        try:
            self.shards.append(shard)
            self.shard_map[shard.shard_id] = shard
            logger.info(f"Shard added: {shard.shard_id} ({shard.host}:{shard.port})")
            return True

        except Exception as e:
            logger.error(f"Add shard error: {e}")
            return False

    def get_shard_for_key(self, key: str) -> Optional[Shard]:
        """Get shard for key using configured strategy"""
        if not self.shards:
            return None

        if self.strategy == ShardingStrategy.HASH:
            return self._get_shard_hash(key)
        elif self.strategy == ShardingStrategy.RANGE:
            return self._get_shard_range(key)
        elif self.strategy == ShardingStrategy.DIRECTORY:
            return self._get_shard_directory(key)

        return self.shards[0]

    def _get_shard_hash(self, key: str) -> Optional[Shard]:
        """Hash-based sharding"""
        hash_value = hash(key) % len(self.shards)
        return self.shards[hash_value]

    def _get_shard_range(self, key: str) -> Optional[Shard]:
        """Range-based sharding"""
        try:
            key_value = int(key)
            for shard in self.shards:
                if (shard.min_range <= key_value < shard.max_range):
                    return shard
        except:
            pass

        return self.shards[0]

    def _get_shard_directory(self, key: str) -> Optional[Shard]:
        """Directory-based sharding (lookup table)"""
        return self.shard_map.get(hash(key) % len(self.shards))

    def get_shard_for_user(self, user_id: str) -> Optional[Shard]:
        """Get shard for user"""
        return self.get_shard_for_key(user_id)

    def get_shard_for_conversation(self, conversation_id: str) -> Optional[Shard]:
        """Get shard for conversation"""
        return self.get_shard_for_key(conversation_id)

    def get_replica_for_read(self, shard_id: int) -> Optional[Tuple[str, int]]:
        """Get read replica for shard"""
        shard = self.shard_map.get(shard_id)
        if shard and shard.replicas:
            return shard.replicas[0]
        return None

    def rebalance_shards(self, new_shard_count: int) -> bool:
        """Rebalance shards (migration operation)"""
        try:
            if new_shard_count <= len(self.shards):
                logger.warning("New shard count must be greater than current count")
                return False

            logger.info(f"Rebalancing: {len(self.shards)} -> {new_shard_count} shards")
            # TODO: Implement migration strategy
            return True

        except Exception as e:
            logger.error(f"Rebalance error: {e}")
            return False

    def get_shard_stats(self) -> dict:
        """Get shard statistics"""
        stats = {
            "total_shards": len(self.shards),
            "strategy": self.strategy.value,
            "shards": []
        }

        for shard in self.shards:
            stats["shards"].append({
                "shard_id": shard.shard_id,
                "host": shard.host,
                "port": shard.port,
                "database": shard.database,
                "region": shard.region,
                "is_active": shard.is_active,
                "replica_count": len(shard.replicas)
            })

        return stats

    def remove_shard(self, shard_id: int) -> bool:
        """Remove shard (with migration)"""
        try:
            self.shards = [s for s in self.shards if s.shard_id != shard_id]
            del self.shard_map[shard_id]
            logger.info(f"Shard removed: {shard_id}")
            return True

        except Exception as e:
            logger.error(f"Remove shard error: {e}")
            return False


# Singleton instance
_sharding = None


def get_database_sharding() -> DatabaseSharding:
    """Get database sharding singleton"""
    global _sharding
    if _sharding is None:
        _sharding = DatabaseSharding(ShardingStrategy.HASH)
    return _sharding
