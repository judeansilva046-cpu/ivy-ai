"""
ETAPA 19: Performance Optimization & Tuning
Database, API, and infrastructure optimization
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseOptimizer:
    """Database query optimization"""

    def __init__(self):
        self.slow_queries: List[Dict] = []
        self.query_stats: Dict[str, Dict[str, float]] = {}

    def track_query(
        self,
        query: str,
        duration_ms: float,
        rows_affected: int = 0
    ):
        """Track query performance"""
        if query not in self.query_stats:
            self.query_stats[query] = {
                "count": 0,
                "total_ms": 0,
                "avg_ms": 0,
                "max_ms": 0,
                "min_ms": float('inf'),
            }

        stats = self.query_stats[query]
        stats["count"] += 1
        stats["total_ms"] += duration_ms
        stats["avg_ms"] = stats["total_ms"] / stats["count"]
        stats["max_ms"] = max(stats["max_ms"], duration_ms)
        stats["min_ms"] = min(stats["min_ms"], duration_ms)

        if duration_ms > 1000:  # Slow query threshold
            self.slow_queries.append({
                "query": query,
                "duration_ms": duration_ms,
                "rows_affected": rows_affected,
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_slow_queries(self, limit: int = 10) -> List[Dict]:
        """Get slow queries"""
        return sorted(
            self.slow_queries,
            key=lambda x: x["duration_ms"],
            reverse=True
        )[:limit]

    def get_optimization_recommendations(self) -> List[str]:
        """Get query optimization recommendations"""
        recommendations = []

        for query, stats in self.query_stats.items():
            if stats["avg_ms"] > 500:
                recommendations.append(f"Query '{query[:50]}...' averaging {stats['avg_ms']:.0f}ms - consider indexing")

            if stats["max_ms"] > 2000:
                recommendations.append(f"Query '{query[:50]}...' peak at {stats['max_ms']:.0f}ms - may have N+1 problem")

        return recommendations


class APIOptimizer:
    """API response optimization"""

    def __init__(self):
        self.endpoint_stats: Dict[str, Dict[str, Any]] = {}
        self.cache_stats: Dict[str, Dict[str, int]] = {}

    def track_endpoint(
        self,
        endpoint: str,
        method: str,
        duration_ms: float,
        status_code: int
    ):
        """Track endpoint performance"""
        key = f"{method} {endpoint}"

        if key not in self.endpoint_stats:
            self.endpoint_stats[key] = {
                "calls": 0,
                "total_ms": 0,
                "avg_ms": 0,
                "errors": 0,
                "cached": 0,
            }

        stats = self.endpoint_stats[key]
        stats["calls"] += 1
        stats["total_ms"] += duration_ms
        stats["avg_ms"] = stats["total_ms"] / stats["calls"]

        if status_code >= 400:
            stats["errors"] += 1

    def track_cache_hit(self, key: str, hit: bool):
        """Track cache hit/miss"""
        if key not in self.cache_stats:
            self.cache_stats[key] = {"hits": 0, "misses": 0}

        if hit:
            self.cache_stats[key]["hits"] += 1
        else:
            self.cache_stats[key]["misses"] += 1

    def get_cache_hit_rate(self) -> Dict[str, float]:
        """Get cache hit rates"""
        rates = {}

        for key, stats in self.cache_stats.items():
            total = stats["hits"] + stats["misses"]
            if total > 0:
                rates[key] = (stats["hits"] / total) * 100

        return rates

    def get_slowest_endpoints(self, limit: int = 10) -> List[tuple]:
        """Get slowest endpoints"""
        return sorted(
            self.endpoint_stats.items(),
            key=lambda x: x[1]["avg_ms"],
            reverse=True
        )[:limit]


class InfrastructureOptimizer:
    """Infrastructure optimization"""

    def __init__(self):
        self.resource_usage: Dict[str, float] = {}
        self.performance_targets = {
            "cpu_usage": 70.0,
            "memory_usage": 80.0,
            "disk_usage": 85.0,
            "api_latency_p95": 200,
            "api_latency_p99": 500,
        }

    def set_resource_usage(
        self,
        cpu: float,
        memory: float,
        disk: float
    ):
        """Set resource usage metrics"""
        self.resource_usage = {
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
        }

    def get_optimization_alerts(self) -> List[str]:
        """Get optimization alerts"""
        alerts = []

        if self.resource_usage.get("cpu", 0) > self.performance_targets["cpu_usage"]:
            alerts.append("CPU usage high - consider scaling horizontally")

        if self.resource_usage.get("memory", 0) > self.performance_targets["memory_usage"]:
            alerts.append("Memory usage high - review caching strategy")

        if self.resource_usage.get("disk", 0) > self.performance_targets["disk_usage"]:
            alerts.append("Disk usage high - archive old data or expand storage")

        return alerts

    def get_scaling_recommendations(self) -> Dict[str, str]:
        """Get scaling recommendations"""
        recommendations = {}

        if self.resource_usage.get("cpu", 0) > 80:
            recommendations["cpu"] = "Add 2-3 more nodes to cluster"

        if self.resource_usage.get("memory", 0) > 85:
            recommendations["memory"] = "Increase instance type or add nodes"

        return recommendations


class PerformanceMonitor:
    """Unified performance monitoring"""

    def __init__(self):
        self.db_optimizer = DatabaseOptimizer()
        self.api_optimizer = APIOptimizer()
        self.infra_optimizer = InfrastructureOptimizer()

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "slow_queries": self.db_optimizer.get_slow_queries(limit=5),
                "recommendations": self.db_optimizer.get_optimization_recommendations(),
            },
            "api": {
                "slowest_endpoints": [
                    {
                        "endpoint": k,
                        "avg_ms": v["avg_ms"],
                        "calls": v["calls"],
                    }
                    for k, v in self.api_optimizer.get_slowest_endpoints(limit=5)
                ],
                "cache_hit_rates": self.api_optimizer.get_cache_hit_rate(),
            },
            "infrastructure": {
                "resource_usage": self.infra_optimizer.resource_usage,
                "alerts": self.infra_optimizer.get_optimization_alerts(),
                "scaling_recommendations": self.infra_optimizer.get_scaling_recommendations(),
            },
        }


# Singleton instance
_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get performance monitor singleton"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor
