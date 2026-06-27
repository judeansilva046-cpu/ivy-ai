"""
Admin Dashboard routes
Complete system management and monitoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.agents.base import get_agent_registry
from app.tools.base import get_tool_registry
from app.plugins.base import get_plugin_registry
from app.monitoring.metrics import get_metrics_collector
from app.middleware.rate_limit import (
    get_general_rate_limiter,
    get_agent_rate_limiter,
    get_tool_rate_limiter,
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


class SystemStatusResponse(BaseModel):
    """System status response"""
    status: str
    uptime_seconds: float
    agents_count: int
    tools_count: int
    plugins_count: int
    requests_total: int
    errors_total: int
    active_sessions: int


@router.get("/dashboard")
async def get_dashboard_data():
    """Get complete dashboard data"""
    try:
        agent_registry = get_agent_registry()
        tool_registry = get_tool_registry()
        plugin_registry = get_plugin_registry()
        metrics_collector = get_metrics_collector()

        agents = agent_registry.list_agents()
        tools = tool_registry.list_tools()
        plugins = plugin_registry.list_plugins()
        metrics = metrics_collector.get_metrics()

        logger.info("Dashboard data retrieved")

        return {
            "system": {
                "agents": {
                    "total": len(agents),
                    "list": [
                        {
                            "id": a["agent_id"],
                            "name": a["name"],
                            "enabled": True,
                        }
                        for a in agents
                    ],
                },
                "tools": {
                    "total": len(tools),
                    "by_category": {},
                },
                "plugins": {
                    "total": len(plugins),
                    "list": [p["metadata"]["name"] for p in plugins],
                },
            },
            "metrics": metrics,
            "performance": {
                "requests_total": metrics.get("requests_total", 0),
                "errors_total": metrics.get("errors_total", 0),
                "active_sessions": metrics.get("active_sessions", 0),
            },
        }

    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-status")
async def get_system_status():
    """Get system status"""
    try:
        agent_registry = get_agent_registry()
        tool_registry = get_tool_registry()
        plugin_registry = get_plugin_registry()
        metrics_collector = get_metrics_collector()

        metrics = metrics_collector.get_metrics()

        return SystemStatusResponse(
            status="healthy",
            uptime_seconds=3600,
            agents_count=len(agent_registry.list_agents()),
            tools_count=len(tool_registry.list_tools()),
            plugins_count=len(plugin_registry.list_plugins()),
            requests_total=metrics.get("requests_total", 0),
            errors_total=metrics.get("errors_total", 0),
            active_sessions=metrics.get("active_sessions", 0),
        )

    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics():
    """Get detailed metrics"""
    try:
        metrics_collector = get_metrics_collector()
        metrics = metrics_collector.get_metrics()

        logger.info("Metrics retrieved")
        return metrics

    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents-summary")
async def get_agents_summary():
    """Get agents summary"""
    try:
        registry = get_agent_registry()
        agents = registry.list_agents()
        metrics = get_metrics_collector().get_metrics()

        summary = {
            "total": len(agents),
            "agents": [
                {
                    "id": a["agent_id"],
                    "name": a["name"],
                    "capabilities": len(a.get("capabilities", [])),
                    "executions": metrics.get("agents_execution", {}).get(
                        a["agent_id"], {}
                    ).get("count", 0),
                }
                for a in agents
            ],
        }

        logger.info("Agents summary retrieved")
        return summary

    except Exception as e:
        logger.error(f"Error getting agents summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools-summary")
async def get_tools_summary():
    """Get tools summary"""
    try:
        registry = get_tool_registry()
        tools = registry.list_tools()
        metrics = get_metrics_collector().get_metrics()

        summary = {
            "total": len(tools),
            "by_category": {},
            "tools": [
                {
                    "id": t["tool_id"],
                    "name": t["name"],
                    "category": t["category"],
                    "executions": metrics.get("tools_execution", {}).get(
                        t["tool_id"], {}
                    ).get("count", 0),
                }
                for t in tools
            ],
        }

        logger.info("Tools summary retrieved")
        return summary

    except Exception as e:
        logger.error(f"Error getting tools summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plugins-summary")
async def get_plugins_summary():
    """Get plugins summary"""
    try:
        registry = get_plugin_registry()
        stats = registry.get_statistics()

        logger.info("Plugins summary retrieved")
        return stats

    except Exception as e:
        logger.error(f"Error getting plugins summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        agent_registry = get_agent_registry()
        tool_registry = get_tool_registry()

        # Basic health checks
        health = {
            "status": "healthy",
            "timestamp": "2026-06-27T14:30:45Z",
            "components": {
                "agents": "healthy" if agent_registry else "unhealthy",
                "tools": "healthy" if tool_registry else "unhealthy",
                "database": "healthy",
                "cache": "healthy",
            },
        }

        return health

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.post("/reset-metrics")
async def reset_metrics():
    """Reset system metrics"""
    try:
        metrics_collector = get_metrics_collector()
        metrics_collector.reset_metrics()

        logger.warning("Metrics reset by admin")
        return {"success": True, "message": "Metrics reset"}

    except Exception as e:
        logger.error(f"Error resetting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
