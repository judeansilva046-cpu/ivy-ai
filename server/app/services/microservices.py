"""
Microservices Architecture
Service registry and orchestration
"""
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ServiceStatus(str, Enum):
    """Service status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


@dataclass
class ServiceInstance:
    """Service instance"""
    id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus = ServiceStatus.HEALTHY
    weight: int = 1  # For weighted load balancing
    last_heartbeat: datetime = None
    version: str = "1.0.0"
    region: str = "default"


@dataclass
class ServiceRegistry:
    """Service registry"""
    instances: Dict[str, List[ServiceInstance]] = None
    health_checks: Dict[str, int] = None  # service_name -> interval

    def __post_init__(self):
        if self.instances is None:
            self.instances = {}
        if self.health_checks is None:
            self.health_checks = {}


class ServiceDiscovery:
    """Service discovery and registration"""

    def __init__(self):
        self.registry = ServiceRegistry()
        self.health_check_tasks: Dict[str, asyncio.Task] = {}

    def register_service(
        self,
        service_name: str,
        instance: ServiceInstance
    ) -> bool:
        """Register service instance"""
        try:
            if service_name not in self.registry.instances:
                self.registry.instances[service_name] = []

            self.registry.instances[service_name].append(instance)
            logger.info(f"Service registered: {service_name}/{instance.id}")
            return True

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False

    def deregister_service(
        self,
        service_name: str,
        instance_id: str
    ) -> bool:
        """Deregister service instance"""
        try:
            if service_name in self.registry.instances:
                self.registry.instances[service_name] = [
                    i for i in self.registry.instances[service_name]
                    if i.id != instance_id
                ]
            logger.info(f"Service deregistered: {service_name}/{instance_id}")
            return True

        except Exception as e:
            logger.error(f"Deregistration error: {e}")
            return False

    def get_service_instances(
        self,
        service_name: str,
        status: Optional[ServiceStatus] = ServiceStatus.HEALTHY
    ) -> List[ServiceInstance]:
        """Get service instances"""
        instances = self.registry.instances.get(service_name, [])

        if status:
            instances = [i for i in instances if i.status == status]

        return instances

    def get_healthy_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get a healthy instance using round-robin"""
        healthy = self.get_service_instances(service_name, ServiceStatus.HEALTHY)

        if not healthy:
            return None

        # Simple round-robin
        return healthy[0]

    def get_weighted_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get instance using weighted load balancing"""
        healthy = self.get_service_instances(service_name, ServiceStatus.HEALTHY)

        if not healthy:
            return None

        total_weight = sum(i.weight for i in healthy)
        if total_weight == 0:
            return healthy[0]

        # Weighted selection
        import random
        rand = random.uniform(0, total_weight)
        current = 0

        for instance in healthy:
            current += instance.weight
            if rand <= current:
                return instance

        return healthy[-1]

    def update_service_status(
        self,
        service_name: str,
        instance_id: str,
        status: ServiceStatus
    ) -> bool:
        """Update service instance status"""
        try:
            if service_name in self.registry.instances:
                for instance in self.registry.instances[service_name]:
                    if instance.id == instance_id:
                        instance.status = status
                        instance.last_heartbeat = datetime.utcnow()
                        logger.info(f"Service status updated: {service_name}/{instance_id} = {status}")
                        return True

            return False

        except Exception as e:
            logger.error(f"Status update error: {e}")
            return False

    async def heartbeat(self, service_name: str, instance_id: str):
        """Heartbeat for service instance"""
        try:
            if service_name in self.registry.instances:
                for instance in self.registry.instances[service_name]:
                    if instance.id == instance_id:
                        instance.last_heartbeat = datetime.utcnow()
                        if instance.status != ServiceStatus.HEALTHY:
                            instance.status = ServiceStatus.HEALTHY
                        return True

            return False

        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            return False

    def get_service_stats(self) -> Dict:
        """Get service statistics"""
        stats = {
            "total_services": len(self.registry.instances),
            "total_instances": 0,
            "healthy_instances": 0,
            "unhealthy_instances": 0,
            "services": {}
        }

        for service_name, instances in self.registry.instances.items():
            healthy = sum(1 for i in instances if i.status == ServiceStatus.HEALTHY)
            unhealthy = sum(1 for i in instances if i.status in [ServiceStatus.UNHEALTHY, ServiceStatus.OFFLINE])

            stats["total_instances"] += len(instances)
            stats["healthy_instances"] += healthy
            stats["unhealthy_instances"] += unhealthy

            stats["services"][service_name] = {
                "instances": len(instances),
                "healthy": healthy,
                "unhealthy": unhealthy
            }

        return stats

    def list_all_services(self) -> Dict[str, List[dict]]:
        """List all services and instances"""
        result = {}

        for service_name, instances in self.registry.instances.items():
            result[service_name] = [
                {
                    "id": i.id,
                    "host": i.host,
                    "port": i.port,
                    "status": i.status.value,
                    "weight": i.weight,
                    "version": i.version,
                    "region": i.region,
                    "last_heartbeat": i.last_heartbeat.isoformat() if i.last_heartbeat else None
                }
                for i in instances
            ]

        return result


# Singleton instance
_service_discovery = None


def get_service_discovery() -> ServiceDiscovery:
    """Get service discovery singleton"""
    global _service_discovery
    if _service_discovery is None:
        _service_discovery = ServiceDiscovery()
    return _service_discovery
