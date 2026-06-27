"""
N8N integration service
"""
import httpx
from typing import Dict, Any, Optional
from config.settings import get_settings
from app.utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)
settings = get_settings()


class N8NService:
    """Service for N8N integration"""

    def __init__(self):
        self.base_url = settings.N8N_URL
        self.api_key = settings.N8N_API_KEY
        self.timeout = 30

    async def trigger_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Trigger an N8N workflow
        """
        if not self.base_url:
            logger.warning("N8N URL not configured")
            return {
                "success": False,
                "error": "N8N not configured",
            }

        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/webhook/{workflow_id}"

                response = await client.post(
                    url,
                    json=data,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    logger.info(f"Workflow triggered: {workflow_id}")
                    return {
                        "success": True,
                        "workflow_id": workflow_id,
                        "response": response.json(),
                    }
                else:
                    logger.error(
                        f"Workflow trigger failed: {workflow_id} - {response.status_code}"
                    )
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                    }

        except httpx.TimeoutException:
            logger.error(f"Workflow trigger timeout: {workflow_id}")
            return {
                "success": False,
                "error": "Timeout",
            }
        except Exception as e:
            logger.error(f"Workflow trigger error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    async def list_workflows(self) -> Dict[str, Any]:
        """
        List all N8N workflows
        """
        if not self.base_url or not self.api_key:
            logger.warning("N8N not configured")
            return {"workflows": []}

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "X-N8N-API-KEY": self.api_key,
                }
                response = await client.get(
                    f"{self.base_url}/api/v1/workflows",
                    headers=headers,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to list workflows: {response.status_code}")
                    return {"workflows": []}

        except Exception as e:
            logger.error(f"Error listing workflows: {str(e)}")
            return {"workflows": []}

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow details
        """
        if not self.base_url or not self.api_key:
            return {"error": "N8N not configured"}

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "X-N8N-API-KEY": self.api_key,
                }
                response = await client.get(
                    f"{self.base_url}/api/v1/workflows/{workflow_id}",
                    headers=headers,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Error getting workflow: {str(e)}")
            return {"error": str(e)}


def get_n8n_service() -> N8NService:
    """Get N8N service instance"""
    return N8NService()
