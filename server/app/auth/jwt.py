"""
JWT Token Management for Ivy AI
JWT generation, validation, and refresh
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from app.utils.logger import setup_logger
from app.security.config import SecurityConfig

logger = setup_logger(__name__)


class JWTManager:
    """JWT token management"""

    def __init__(self):
        self.config = SecurityConfig()
        self.algorithm = self.config.JWT_ALGORITHM
        self.secret_key = self.config.JWT_SECRET_KEY
        self.expiration_hours = self.config.JWT_EXPIRATION_HOURS
        self.refresh_expiration_days = self.config.JWT_REFRESH_EXPIRATION_DAYS

    def generate_token(
        self,
        user_id: str,
        email: str,
        roles: list = None,
        permissions: list = None,
    ) -> Dict[str, str]:
        """Generate JWT token and refresh token"""
        if roles is None:
            roles = ["user"]
        if permissions is None:
            permissions = []

        # Access token
        access_payload = {
            "user_id": user_id,
            "email": email,
            "roles": roles,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours),
            "iat": datetime.utcnow(),
            "type": "access",
        }

        access_token = jwt.encode(
            access_payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        # Refresh token
        refresh_payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(days=self.refresh_expiration_days),
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        refresh_token = jwt.encode(
            refresh_payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        logger.info(f"JWT tokens generated for user: {user_id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.expiration_hours * 3600,
        }

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        payload = self.validate_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            return None

        # Generate new access token
        access_payload = {
            "user_id": payload["user_id"],
            "email": payload["email"],
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours),
            "iat": datetime.utcnow(),
            "type": "access",
        }

        access_token = jwt.encode(
            access_payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        logger.info(f"Access token refreshed for user: {payload['user_id']}")
        return access_token

    def decode_token_unsafe(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token without validation (use carefully)"""
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False}
            )
        except jwt.InvalidTokenError:
            return None


class TokenBlacklist:
    """Token blacklist for logout and revocation"""

    def __init__(self):
        self.blacklist = set()

    def add_to_blacklist(self, token: str):
        """Add token to blacklist"""
        self.blacklist.add(token)
        logger.info("Token added to blacklist")

    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return token in self.blacklist

    def clear_blacklist(self):
        """Clear blacklist"""
        self.blacklist.clear()
        logger.info("Blacklist cleared")


# Singleton instances
_jwt_manager = None
_token_blacklist = None


def get_jwt_manager() -> JWTManager:
    """Get JWT manager singleton"""
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = JWTManager()
    return _jwt_manager


def get_token_blacklist() -> TokenBlacklist:
    """Get token blacklist singleton"""
    global _token_blacklist
    if _token_blacklist is None:
        _token_blacklist = TokenBlacklist()
    return _token_blacklist
