"""
Data Warehouse for Advanced Analytics
ETL pipelines and dimensional modeling
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class EventType(str, Enum):
    """Event types for analytics"""
    USER_LOGIN = "user_login"
    CHAT_MESSAGE = "chat_message"
    AGENT_EXECUTION = "agent_execution"
    TOOL_EXECUTION = "tool_execution"
    PLUGIN_EXECUTION = "plugin_execution"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"


@dataclass
class AnalyticsEvent:
    """Analytics event"""
    event_id: str
    event_type: EventType
    user_id: str
    timestamp: datetime
    properties: Dict[str, Any]
    session_id: str = None
    duration_ms: int = None
    error_message: str = None


@dataclass
class DimensionUser:
    """User dimension"""
    user_id: str
    email: str
    role: str
    created_at: datetime
    last_active: datetime
    country: str = None
    region: str = None


@dataclass
class DimensionAgent:
    """Agent dimension"""
    agent_id: str
    agent_name: str
    agent_type: str
    version: str
    created_at: datetime


@dataclass
class FactAgentExecution:
    """Fact table for agent executions"""
    execution_id: str
    user_id: str
    agent_id: str
    timestamp: datetime
    duration_ms: int
    success: bool
    error_message: str = None
    input_tokens: int = 0
    output_tokens: int = 0


class DataWarehouse:
    """Data warehouse for analytics"""

    def __init__(self):
        self.events: List[AnalyticsEvent] = []
        self.dimensions_user: Dict[str, DimensionUser] = {}
        self.dimensions_agent: Dict[str, DimensionAgent] = {}
        self.facts_agent_execution: List[FactAgentExecution] = []
        self.event_buffer: List[AnalyticsEvent] = []
        self.buffer_size = 1000
        self.flush_interval = 60  # seconds

    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Track analytics event"""
        try:
            self.event_buffer.append(event)

            # Auto-flush if buffer full
            if len(self.event_buffer) >= self.buffer_size:
                await self.flush_events()

            return True

        except Exception as e:
            logger.error(f"Track event error: {e}")
            return False

    async def flush_events(self) -> bool:
        """Flush events to warehouse"""
        try:
            self.events.extend(self.event_buffer)
            count = len(self.event_buffer)
            self.event_buffer.clear()

            logger.info(f"Flushed {count} events to warehouse")
            return True

        except Exception as e:
            logger.error(f"Flush error: {e}")
            return False

    def add_user_dimension(self, user: DimensionUser):
        """Add user dimension"""
        self.dimensions_user[user.user_id] = user

    def add_agent_dimension(self, agent: DimensionAgent):
        """Add agent dimension"""
        self.dimensions_agent[agent.agent_id] = agent

    def record_agent_execution(self, fact: FactAgentExecution):
        """Record agent execution fact"""
        self.facts_agent_execution.append(fact)

    def get_user_metrics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)

        user_events = [
            e for e in self.events
            if e.user_id == user_id and e.timestamp >= start_date
        ]

        total_events = len(user_events)
        event_types = {}

        for event in user_events:
            event_types[event.event_type.value] = event_types.get(event.event_type.value, 0) + 1

        return {
            "user_id": user_id,
            "days": days,
            "total_events": total_events,
            "event_types": event_types,
            "avg_daily_events": total_events / max(days, 1),
        }

    def get_agent_metrics(self, agent_id: str, days: int = 30) -> Dict[str, Any]:
        """Get agent performance metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)

        executions = [
            f for f in self.facts_agent_execution
            if f.agent_id == agent_id and f.timestamp >= start_date
        ]

        if not executions:
            return {
                "agent_id": agent_id,
                "total_executions": 0,
                "success_rate": 0,
                "avg_duration_ms": 0,
            }

        successful = sum(1 for f in executions if f.success)
        total_duration = sum(f.duration_ms for f in executions)

        return {
            "agent_id": agent_id,
            "total_executions": len(executions),
            "successful_executions": successful,
            "success_rate": (successful / len(executions)) * 100,
            "avg_duration_ms": total_duration / len(executions),
            "total_tokens": sum(f.input_tokens + f.output_tokens for f in executions),
        }

    def get_top_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing agents"""
        agent_stats = {}

        for fact in self.facts_agent_execution:
            if fact.agent_id not in agent_stats:
                agent_stats[fact.agent_id] = {
                    "executions": 0,
                    "successful": 0,
                    "total_duration": 0,
                }

            agent_stats[fact.agent_id]["executions"] += 1
            if fact.success:
                agent_stats[fact.agent_id]["successful"] += 1
            agent_stats[fact.agent_id]["total_duration"] += fact.duration_ms

        # Sort by success rate
        sorted_agents = sorted(
            agent_stats.items(),
            key=lambda x: (x[1]["successful"] / max(x[1]["executions"], 1)),
            reverse=True
        )

        return [
            {
                "agent_id": agent_id,
                "executions": stats["executions"],
                "success_rate": (stats["successful"] / stats["executions"]) * 100,
                "avg_duration_ms": stats["total_duration"] / stats["executions"],
            }
            for agent_id, stats in sorted_agents[:limit]
        ]

    def get_hourly_trend(self, hours: int = 24) -> Dict[str, List[int]]:
        """Get hourly event trend"""
        now = datetime.utcnow()
        start = now - timedelta(hours=hours)

        hourly_counts = {}

        for event in self.events:
            if event.timestamp >= start:
                hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
                hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1

        return {
            "hours": hours,
            "trend": hourly_counts,
        }

    def get_error_rate(self, hours: int = 24) -> Dict[str, Any]:
        """Get error rate"""
        start = datetime.utcnow() - timedelta(hours=hours)

        recent_events = [e for e in self.events if e.timestamp >= start]
        errors = [e for e in recent_events if e.event_type == EventType.ERROR_OCCURRED]

        if not recent_events:
            return {"error_rate": 0, "total_events": 0, "error_count": 0}

        return {
            "hours": hours,
            "total_events": len(recent_events),
            "error_count": len(errors),
            "error_rate": (len(errors) / len(recent_events)) * 100,
        }

    def generate_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        start_date = datetime.utcnow() - timedelta(days=days)

        period_events = [e for e in self.events if e.timestamp >= start_date]

        return {
            "period_days": days,
            "total_events": len(period_events),
            "unique_users": len(set(e.user_id for e in period_events)),
            "event_breakdown": {
                event_type.value: sum(1 for e in period_events if e.event_type == event_type)
                for event_type in EventType
            },
            "top_agents": self.get_top_agents(limit=5),
            "error_rate": self.get_error_rate(hours=days * 24),
        }


# Singleton instance
_warehouse = None


def get_data_warehouse() -> DataWarehouse:
    """Get data warehouse singleton"""
    global _warehouse
    if _warehouse is None:
        _warehouse = DataWarehouse()
    return _warehouse
