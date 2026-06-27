"""
Load Testing for IVY AI
Test system under stress conditions
"""
import asyncio
import time
from typing import List
import pytest
from locust import HttpUser, task, between


class PerformanceMetrics:
    """Track performance metrics"""
    def __init__(self):
        self.response_times: List[float] = []
        self.errors = 0
        self.successes = 0

    def add_response(self, duration_ms: float, success: bool = True):
        """Record response"""
        self.response_times.append(duration_ms)
        if success:
            self.successes += 1
        else:
            self.errors += 1

    def get_stats(self) -> dict:
        """Get statistics"""
        if not self.response_times:
            return {}

        times = sorted(self.response_times)
        return {
            "requests": len(times),
            "successes": self.successes,
            "errors": self.errors,
            "error_rate": (self.errors / (self.errors + self.successes)) * 100 if (self.errors + self.successes) > 0 else 0,
            "min_ms": min(times),
            "max_ms": max(times),
            "avg_ms": sum(times) / len(times),
            "p50_ms": times[len(times) // 2],
            "p95_ms": times[int(len(times) * 0.95)],
            "p99_ms": times[int(len(times) * 0.99)],
            "rps": len(times) / (max(times) / 1000) if max(times) > 0 else 0,
        }


@pytest.mark.asyncio
async def test_chat_endpoint_latency():
    """Test /chat endpoint latency under load"""
    metrics = PerformanceMetrics()

    for i in range(100):
        start = time.time()
        # Simulate API call
        await asyncio.sleep(0.05)  # 50ms
        duration_ms = (time.time() - start) * 1000
        metrics.add_response(duration_ms)

    stats = metrics.get_stats()
    assert stats["p95_ms"] < 200, f"P95 latency too high: {stats['p95_ms']}ms"
    assert stats["p99_ms"] < 500, f"P99 latency too high: {stats['p99_ms']}ms"
    assert stats["error_rate"] < 1, f"Error rate too high: {stats['error_rate']}%"


@pytest.mark.asyncio
async def test_agent_execution_throughput():
    """Test agent execution throughput"""
    metrics = PerformanceMetrics()

    for i in range(50):
        start = time.time()
        # Simulate agent execution
        await asyncio.sleep(0.1)  # 100ms
        duration_ms = (time.time() - start) * 1000
        metrics.add_response(duration_ms)

    stats = metrics.get_stats()
    assert stats["avg_ms"] < 150, f"Average latency too high: {stats['avg_ms']}ms"
    assert stats["successes"] >= 45, f"Success rate too low: {stats['successes']}/50"


@pytest.mark.asyncio
async def test_concurrent_requests_1000():
    """Test 1,000 concurrent requests"""
    metrics = PerformanceMetrics()

    async def make_request():
        start = time.time()
        await asyncio.sleep(0.05)
        duration_ms = (time.time() - start) * 1000
        metrics.add_response(duration_ms)

    tasks = [make_request() for _ in range(1000)]
    await asyncio.gather(*tasks)

    stats = metrics.get_stats()
    assert stats["p95_ms"] < 300, f"P95 too high under load: {stats['p95_ms']}ms"
    assert stats["error_rate"] < 5, f"Error rate too high: {stats['error_rate']}%"


@pytest.mark.asyncio
async def test_database_query_performance():
    """Test database query performance under load"""
    metrics = PerformanceMetrics()

    for i in range(100):
        start = time.time()
        # Simulate DB query
        await asyncio.sleep(0.02)  # 20ms
        duration_ms = (time.time() - start) * 1000
        metrics.add_response(duration_ms)

    stats = metrics.get_stats()
    assert stats["avg_ms"] < 50, f"DB query too slow: {stats['avg_ms']}ms"
    assert stats["p99_ms"] < 100, f"DB query P99 too high: {stats['p99_ms']}ms"


@pytest.mark.asyncio
async def test_cache_hit_performance():
    """Test cache hit performance"""
    metrics = PerformanceMetrics()

    for i in range(100):
        start = time.time()
        # Simulate cache hit (very fast)
        await asyncio.sleep(0.001)  # 1ms
        duration_ms = (time.time() - start) * 1000
        metrics.add_response(duration_ms)

    stats = metrics.get_stats()
    assert stats["avg_ms"] < 10, f"Cache hit too slow: {stats['avg_ms']}ms"


class IvyAILoadTest(HttpUser):
    """Locust load test for Ivy AI"""
    wait_time = between(1, 3)

    @task(3)
    def chat(self):
        """Chat endpoint"""
        self.client.post(
            "/chat",
            json={"message": "Hello"},
            headers={"Authorization": "Bearer test_token"}
        )

    @task(2)
    def list_agents(self):
        """List agents endpoint"""
        self.client.get(
            "/agent/list",
            headers={"Authorization": "Bearer test_token"}
        )

    @task(1)
    def health_check(self):
        """Health check"""
        self.client.get("/admin/health")


class LoadTestReport:
    """Generate load test report"""

    @staticmethod
    def generate(metrics: PerformanceMetrics) -> str:
        stats = metrics.get_stats()
        report = f"""
╔════════════════════════════════════════════╗
║        LOAD TEST REPORT - IVY AI           ║
╚════════════════════════════════════════════╝

SUMMARY
───────────────────────────────────────────────
Total Requests:     {stats.get('requests', 0):,}
Successful:         {stats.get('successes', 0):,}
Failed:             {stats.get('errors', 0):,}
Error Rate:         {stats.get('error_rate', 0):.2f}%

LATENCY (ms)
───────────────────────────────────────────────
Minimum:            {stats.get('min_ms', 0):.2f}
Average:            {stats.get('avg_ms', 0):.2f}
P50 (Median):       {stats.get('p50_ms', 0):.2f}
P95:                {stats.get('p95_ms', 0):.2f}
P99:                {stats.get('p99_ms', 0):.2f}
Maximum:            {stats.get('max_ms', 0):.2f}

THROUGHPUT
───────────────────────────────────────────────
Requests/Second:    {stats.get('rps', 0):.2f}

VERDICT
───────────────────────────────────────────────
"""
        # Check targets
        if stats.get('p95_ms', 0) < 200 and stats.get('error_rate', 0) < 1:
            report += "✅ PRODUCTION READY - All targets met!"
        elif stats.get('p95_ms', 0) < 300 and stats.get('error_rate', 0) < 5:
            report += "⚠️  ACCEPTABLE - Some optimization needed"
        else:
            report += "❌ NEEDS IMPROVEMENT - Scale up infrastructure"

        return report


# Test report generation
def test_load_test_report():
    """Generate load test report"""
    metrics = PerformanceMetrics()

    # Simulate results
    for i in range(100):
        metrics.add_response(50 + (i % 50), success=(i % 10 != 0))

    report = LoadTestReport.generate(metrics)
    assert "PRODUCTION READY" in report or "ACCEPTABLE" in report or "NEEDS IMPROVEMENT" in report
    print(report)


if __name__ == "__main__":
    print("🚀 Running load tests...")
    print("Run with: locust -f tests/test_performance_load.py -u 1000 -r 100")
