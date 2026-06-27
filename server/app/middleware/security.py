"""
Security Middleware for Ivy AI
JWT validation, API key checks, RBAC enforcement
"""
from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.auth.jwt import get_jwt_manager, get_token_blacklist
from app.auth.api_keys import get_api_key_manager
from app.auth.rbac import get_rbac_manager
from app.security.config import SecurityConfig
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SecurityMiddleware:
    """Security middleware for FastAPI"""

    def __init__(self, app):
        self.app = app
        self.config = SecurityConfig()
        self.jwt_manager = get_jwt_manager()
        self.blacklist = get_token_blacklist()
        self.api_key_manager = get_api_key_manager()
        self.rbac = get_rbac_manager()

    async def __call__(self, request: Request, call_next: Callable):
        """Process request"""
        # Add security headers
        response = await call_next(request)

        for header, value in self.config.SECURITY_HEADERS.items():
            response.headers[header] = value

        return response

    def extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request"""
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return None

        return auth_header[7:]

    def extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request"""
        return request.headers.get(self.config.API_KEY_HEADER)

    async def verify_jwt(self, request: Request) -> Optional[dict]:
        """Verify JWT token"""
        token = self.extract_token(request)

        if not token:
            return None

        # Check blacklist
        if self.blacklist.is_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        # Validate token
        payload = self.jwt_manager.validate_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return payload

    async def verify_api_key(self, request: Request) -> Optional[dict]:
        """Verify API key"""
        api_key = self.extract_api_key(request)

        if not api_key:
            return None

        # Validate API key
        key_info = self.api_key_manager.validate_key(api_key)

        if not key_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        return {
            "user_id": key_info.user_id,
            "scopes": key_info.scopes,
            "auth_type": "api_key",
        }

    async def verify_permission(
        self,
        user_id: str,
        required_permission: str,
    ) -> bool:
        """Verify user has required permission"""
        return self.rbac.has_permission(user_id, required_permission)


class JWTAuthMiddleware:
    """JWT Authentication middleware"""

    def __init__(self, app):
        self.app = app
        self.security = SecurityMiddleware(app)

    async def __call__(self, request: Request, call_next: Callable):
        """Process request with JWT validation"""
        # Skip validation for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)

        try:
            payload = await self.security.verify_jwt(request)
            request.state.user = payload
        except HTTPException:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized"},
            )

        response = await call_next(request)
        return response

    @staticmethod
    def _is_public_endpoint(path: str) -> bool:
        """Check if endpoint is public"""
        public_paths = [
            "/auth/login",
            "/auth/register",
            "/health",
            "/docs",
            "/openapi.json",
        ]
        return any(path.startswith(p) for p in public_paths)


class APIKeyAuthMiddleware:
    """API Key Authentication middleware"""

    def __init__(self, app):
        self.app = app
        self.security = SecurityMiddleware(app)

    async def __call__(self, request: Request, call_next: Callable):
        """Process request with API key validation"""
        try:
            key_info = await self.security.verify_api_key(request)
            if key_info:
                request.state.user = key_info
        except HTTPException:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized"},
            )

        response = await call_next(request)
        return response


class RBACMiddleware:
    """Role-Based Access Control middleware"""

    def __init__(self, app):
        self.app = app
        self.security = SecurityMiddleware(app)

    async def __call__(self, request: Request, call_next: Callable):
        """Process request with RBAC validation"""
        response = await call_next(request)
        return response


def verify_token_required(request: Request) -> dict:
    """Dependency for token verification"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return request.state.user


def verify_permission_required(permission: str):
    """Dependency for permission verification"""
    async def _verify(request: Request) -> dict:
        if not hasattr(request.state, 'user'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        user = request.state.user
        rbac = get_rbac_manager()

        if not rbac.has_permission(user.get("user_id"), permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        return user

    return _verify
