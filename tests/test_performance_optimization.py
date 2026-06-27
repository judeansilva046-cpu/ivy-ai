"""
Tests for ETAPA 19: Performance Optimization
"""
import pytest
from app.performance.optimization import (
    DatabaseOptimizer,
    APIOptimizer,
    InfrastructureOptimizer,
    PerformanceMonitor,
    get_performance_monitor
)


class TestDatabaseOptimizer:
    """Database optimization tests"""

    def test_track_query_fast(self):
        """Test tracking fast query"""
        optimizer = DatabaseOptimizer()
        optimizer.track_query("SELECT * FROM users", 50.0)

        assert "SELECT * FROM users" in optimizer.query_stats
        assert optimizer.query_stats["SELECT * FROM users"]["avg_ms"] == 50.0

    def test_track_slow_query(self):
        """Test tracking slow query"""
        optimizer = DatabaseOptimizer()
        optimizer.track_query("SELECT * FROM large_table", 1500.0)

        slow_queries = optimizer.get_slow_queries()
        assert len(slow_queries) == 1
        assert slow_queries[0]["duration_ms"] == 1500.0

    def test_optimization_recommendations(self):
        """Test getting optimization recommendations"""
        optimizer = DatabaseOptimizer()
        optimizer.track_query("SELECT * FROM users", 600.0)
        optimizer.track_query("SELECT * FROM users", 700.0)

        recommendations = optimizer.get_optimization_recommendations()
        assert any("indexing" in r for r in recommendations)


class TestAPIOptimizer:
    """API optimization tests"""

    def test_track_endpoint(self):
        """Test tracking endpoint performance"""
        optimizer = APIOptimizer()
        optimizer.track_endpoint("/chat", "POST", 150.0, 200)

        assert "POST /chat" in optimizer.endpoint_stats
        assert optimizer.endpoint_stats["POST /chat"]["calls"] == 1
        assert optimizer.endpoint_stats["POST /chat"]["avg_ms"] == 150.0

    def test_track_multiple_calls(self):
        """Test tracking multiple calls to endpoint"""
        optimizer = APIOptimizer()
        optimizer.track_endpoint("/chat", "POST", 100.0, 200)
        optimizer.track_endpoint("/chat", "POST", 200.0, 200)

        stats = optimizer.endpoint_stats["POST /chat"]
        assert stats["calls"] == 2
        assert stats["avg_ms"] == 150.0

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation"""
        optimizer = APIOptimizer()
        optimizer.track_cache_hit("user:123", True)
        optimizer.track_cache_hit("user:123", True)
        optimizer.track_cache_hit("user:123", False)

        rates = optimizer.get_cache_hit_rate()
        assert rates["user:123"] == pytest.approx(66.67, abs=0.1)

    def test_slowest_endpoints(self):
        """Test getting slowest endpoints"""
        optimizer = APIOptimizer()
        optimizer.track_endpoint("/fast", "GET", 50.0, 200)
        optimizer.track_endpoint("/slow", "GET", 500.0, 200)

        slowest = optimizer.get_slowest_endpoints(limit=1)
        assert slowest[0][0] == "GET /slow"


class TestInfrastructureOptimizer:
    """Infrastructure optimization tests"""

    def test_resource_usage(self):
        """Test setting resource usage"""
        optimizer = InfrastructureOptimizer()
        optimizer.set_resource_usage(cpu=50.0, memory=60.0, disk=70.0)

        assert optimizer.resource_usage["cpu"] == 50.0
        assert optimizer.resource_usage["memory"] == 60.0
        assert optimizer.resource_usage["disk"] == 70.0

    def test_optimization_alerts(self):
        """Test getting optimization alerts"""
        optimizer = InfrastructureOptimizer()
        optimizer.set_resource_usage(cpu=80.0, memory=90.0, disk=90.0)

        alerts = optimizer.get_optimization_alerts()
        assert len(alerts) >= 2
        assert any("CPU" in a for a in alerts)

    def test_scaling_recommendations(self):
        """Test getting scaling recommendations"""
        optimizer = InfrastructureOptimizer()
        optimizer.set_resource_usage(cpu=85.0, memory=90.0, disk=90.0)

        recommendations = optimizer.get_scaling_recommendations()
        assert "cpu" in recommendations or "memory" in recommendations


class TestPerformanceMonitor:
    """Performance monitor tests"""

    def test_performance_report(self):
        """Test generating performance report"""
        monitor = get_performance_monitor()
        monitor.db_optimizer.track_query("SELECT * FROM users", 1500.0)
        monitor.api_optimizer.track_endpoint("/chat", "POST", 200.0, 200)
        monitor.infra_optimizer.set_resource_usage(cpu=60.0, memory=70.0, disk=80.0)

        report = monitor.get_performance_report()

        assert "database" in report
        assert "api" in report
        assert "infrastructure" in report
        assert "timestamp" in report

    def test_database_metrics_in_report(self):
        """Test database metrics in report"""
        monitor = PerformanceMonitor()
        monitor.db_optimizer.track_query("SELECT * FROM users", 1500.0)

        report = monitor.get_performance_report()
        assert len(report["database"]["slow_queries"]) > 0

    def test_api_metrics_in_report(self):
        """Test API metrics in report"""
        monitor = PerformanceMonitor()
        monitor.api_optimizer.track_endpoint("/chat", "POST", 150.0, 200)

        report = monitor.get_performance_report()
        assert "cache_hit_rates" in report["api"]
        assert "slowest_endpoints" in report["api"]

    def test_singleton_instance(self):
        """Test singleton pattern"""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        assert monitor1 is monitor2
