"""
Monitoring and Metrics Collection
Prometheus metrics for system monitoring
"""
from datetime import datetime
from typing import Dict, Any
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MetricsCollector:
    """Collect and track system metrics"""

    def __init__(self):
        """Initialize metrics collector"""
        self.metrics: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "requests_total": 0,
            "requests_by_endpoint": {},
            "agents_execution": {},
            "tools_execution": {},
            "errors_total": 0,
            "errors_by_type": {},
            "response_times": {},
            "active_sessions": 0,
        }
        logger.info("MetricsCollector initialized")

    def record_request(self, endpoint: str, method: str, status: int, duration_ms: float):
        """Record API request"""
        self.metrics["requests_total"] += 1

        key = f"{method} {endpoint}"
        if key not in self.metrics["requests_by_endpoint"]:
            self.metrics["requests_by_endpoint"][key] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "errors": 0,
            }

        stats = self.metrics["requests_by_endpoint"][key]
        stats["count"] += 1
        stats["total_time"] += duration_ms
        stats["avg_time"] = stats["total_time"] / stats["count"]

        if status >= 400:
            stats["errors"] += 1
            self.metrics["errors_total"] += 1

    def record_agent_execution(self, agent_id: str, duration_ms: float, success: bool):
        """Record agent execution"""
        if agent_id not in self.metrics["agents_execution"]:
            self.metrics["agents_execution"][agent_id] = {
                "count": 0,
                "success": 0,
                "failures": 0,
                "avg_time": 0,
                "total_time": 0,
            }

        stats = self.metrics["agents_execution"][agent_id]
        stats["count"] += 1
        stats["total_time"] += duration_ms
        stats["avg_time"] = stats["total_time"] / stats["count"]

        if success:
            stats["success"] += 1
        else:
            stats["failures"] += 1

    def record_tool_execution(self, tool_id: str, duration_ms: float, success: bool):
        """Record tool execution"""
        if tool_id not in self.metrics["tools_execution"]:
            self.metrics["tools_execution"][tool_id] = {
                "count": 0,
                "success": 0,
                "failures": 0,
                "avg_time": 0,
                "total_time": 0,
            }

        stats = self.metrics["tools_execution"][tool_id]
        stats["count"] += 1
        stats["total_time"] += duration_ms
        stats["avg_time"] = stats["total_time"] / stats["count"]

        if success:
            stats["success"] += 1
        else:
            stats["failures"] += 1

    def record_error(self, error_type: str):
        """Record error occurrence"""
        self.metrics["errors_total"] += 1

        if error_type not in self.metrics["errors_by_type"]:
            self.metrics["errors_by_type"][error_type] = 0

        self.metrics["errors_by_type"][error_type] += 1

    def set_active_sessions(self, count: int):
        """Set current active sessions"""
        self.metrics["active_sessions"] = count

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()

    def reset_metrics(self):
        """Reset metrics"""
        self.metrics = {
            "start_time": datetime.now().isoformat(),
            "requests_total": 0,
            "requests_by_endpoint": {},
            "agents_execution": {},
            "tools_execution": {},
            "errors_total": 0,
            "errors_by_type": {},
            "response_times": {},
            "active_sessions": 0,
        }
        logger.info("Metrics reset")


# Global metrics collector
_collector: MetricsCollector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector singleton"""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector
