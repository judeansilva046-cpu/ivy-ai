"""
Plugin routes - Plugin management and execution
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.plugins.base import get_plugin_registry, PluginType
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/plugin", tags=["Plugins"])


# Request/Response models
class PluginExecuteRequest(BaseModel):
    """Plugin execution request"""
    parameters: Dict[str, Any]


class PluginConfigRequest(BaseModel):
    """Plugin configuration request"""
    config: Dict[str, Any]


class PluginInfo(BaseModel):
    """Plugin information"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: str
    enabled: bool


@router.get("/list")
async def list_plugins():
    """List all registered plugins"""
    try:
        registry = get_plugin_registry()
        plugins = registry.list_plugins()

        result = [
            PluginInfo(
                name=plugin["metadata"]["name"],
                version=plugin["metadata"]["version"],
                description=plugin["metadata"]["description"],
                author=plugin["metadata"]["author"],
                plugin_type=plugin["metadata"]["plugin_type"],
                enabled=plugin["enabled"],
            )
            for plugin in plugins
        ]

        logger.info(f"Listed {len(result)} plugins")
        return result

    except Exception as e:
        logger.error(f"Error listing plugins: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list-by-type/{plugin_type}")
async def list_plugins_by_type(plugin_type: str):
    """List plugins by type"""
    try:
        registry = get_plugin_registry()

        # Convert to PluginType
        try:
            ptype = PluginType(plugin_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid plugin type: {plugin_type}",
            )

        plugins = registry.list_plugins_by_type(ptype)

        logger.info(f"Listed {len(plugins)} plugins of type {plugin_type}")
        return {"type": plugin_type, "plugins": plugins}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing plugins by type: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plugin_id}/info")
async def get_plugin_info(plugin_id: str):
    """Get plugin information"""
    try:
        registry = get_plugin_registry()
        plugin = registry.get_plugin(plugin_id)

        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

        logger.info(f"Retrieved info for plugin: {plugin_id}")
        return plugin.get_info()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/enable")
async def enable_plugin(plugin_id: str, request: Optional[PluginConfigRequest] = None):
    """Enable a plugin"""
    try:
        registry = get_plugin_registry()

        config = request.config if request else {}
        success = await registry.enable_plugin(plugin_id, config)

        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to enable plugin: {plugin_id}"
            )

        logger.info(f"Plugin enabled: {plugin_id}")
        return {"success": True, "message": f"Plugin enabled: {plugin_id}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling plugin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    """Disable a plugin"""
    try:
        registry = get_plugin_registry()

        success = await registry.disable_plugin(plugin_id)

        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to disable plugin: {plugin_id}"
            )

        logger.info(f"Plugin disabled: {plugin_id}")
        return {"success": True, "message": f"Plugin disabled: {plugin_id}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling plugin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/execute")
async def execute_plugin(plugin_id: str, request: PluginExecuteRequest):
    """Execute a plugin"""
    try:
        registry = get_plugin_registry()

        result = await registry.execute_plugin(plugin_id, **request.parameters)

        logger.info(f"Plugin executed: {plugin_id}")
        return result

    except Exception as e:
        logger.error(f"Error executing plugin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_plugin_statistics():
    """Get plugin registry statistics"""
    try:
        registry = get_plugin_registry()
        stats = registry.get_statistics()

        logger.info("Retrieved plugin statistics")
        return stats

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plugin_id}/metadata")
async def get_plugin_metadata(plugin_id: str):
    """Get plugin metadata"""
    try:
        registry = get_plugin_registry()
        plugin = registry.get_plugin(plugin_id)

        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")

        logger.info(f"Retrieved metadata for plugin: {plugin_id}")
        return plugin.metadata.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
