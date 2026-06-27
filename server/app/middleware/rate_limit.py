"""
Rate Limiting Middleware
Implement rate limiting and throttling
"""
from typing import Dict, Tuple
from datetime import datetime, timedelta
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """Rate limiter for API endpoints"""

    def __init__(self, requests_per_minute: int = 60):
        """Initialize rate limiter

        Args:
            requests_per_minute: Max requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.client_requests: Dict[str, list] = {}

    def is_allowed(self, client_id: str) -> Tuple[bool, Dict]:
        """Check if client is allowed to make request

        Args:
            client_id: Client identifier (IP, user ID, etc)

        Returns:
            Tuple of (allowed, info)
        """
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=1)

        # Clean old requests
        if client_id in self.client_requests:
            self.client_requests[client_id] = [
                req_time
                for req_time in self.client_requests[client_id]
                if req_time > cutoff_time
            ]
        else:
            self.client_requests[client_id] = []

        # Check limit
        request_count = len(self.client_requests[client_id])

        if request_count >= self.requests_per_minute:
            return False, {
                "remaining": 0,
                "reset_in_seconds": 60,
                "limit": self.requests_per_minute,
            }

        # Add current request
        self.client_requests[client_id].append(now)

        return True, {
            "remaining": self.requests_per_minute - request_count - 1,
            "limit": self.requests_per_minute,
            "reset_in_seconds": 60,
        }


class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts based on system load"""

    def __init__(self, base_requests_per_minute: int = 60):
        """Initialize adaptive rate limiter

        Args:
            base_requests_per_minute: Base request limit
        """
        super().__init__(base_requests_per_minute)
        self.system_load = 0.0  # 0.0 to 1.0

    def set_system_load(self, load: float):
        """Set current system load

        Args:
            load: System load (0.0-1.0)
        """
        self.system_load = max(0.0, min(1.0, load))

    def is_allowed(self, client_id: str) -> Tuple[bool, Dict]:
        """Check if client is allowed with adaptive limits

        Args:
            client_id: Client identifier

        Returns:
            Tuple of (allowed, info)
        """
        # Adjust limit based on system load
        if self.system_load > 0.8:
            adjusted_limit = int(self.requests_per_minute * 0.5)
        elif self.system_load > 0.6:
            adjusted_limit = int(self.requests_per_minute * 0.75)
        else:
            adjusted_limit = self.requests_per_minute

        # Temporarily adjust for this check
        original_limit = self.requests_per_minute
        self.requests_per_minute = adjusted_limit

        result = super().is_allowed(client_id)

        # Restore original limit
        self.requests_per_minute = original_limit

        return result


# Global rate limiters
_general_limiter: RateLimiter = None
_agent_limiter: RateLimiter = None
_tool_limiter: RateLimiter = None


def get_general_rate_limiter() -> RateLimiter:
    """Get general rate limiter"""
    global _general_limiter
    if _general_limiter is None:
        _general_limiter = AdaptiveRateLimiter(100)  # 100 req/min
    return _general_limiter


def get_agent_rate_limiter() -> RateLimiter:
    """Get agent rate limiter"""
    global _agent_limiter
    if _agent_limiter is None:
        _agent_limiter = RateLimiter(50)  # 50 req/min
    return _agent_limiter


def get_tool_rate_limiter() -> RateLimiter:
    """Get tool rate limiter"""
    global _tool_limiter
    if _tool_limiter is None:
        _tool_limiter = RateLimiter(200)  # 200 req/min
    return _tool_limiter
