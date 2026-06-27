"""
API Key Management for Ivy AI
API key generation, validation, and scoping
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass
from app.utils.logger import setup_logger
from app.security.config import SecurityConfig

logger = setup_logger(__name__)


@dataclass
class APIKeyInfo:
    """API Key information"""
    key_id: str
    key_hash: str
    user_id: str
    name: str
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    is_active: bool


class APIKeyManager:
    """API key management"""

    def __init__(self):
        self.config = SecurityConfig()
        self.key_length = self.config.API_KEY_LENGTH
        self.keys_storage: Dict[str, APIKeyInfo] = {}

    def generate_key(
        self,
        user_id: str,
        name: str,
        scopes: List[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, str]:
        """Generate new API key"""
        if scopes is None:
            scopes = ["read"]

        # Generate random key
        raw_key = secrets.token_urlsafe(self.key_length)
        key_id = f"key_{secrets.token_hex(8)}"
        key_hash = self._hash_key(raw_key)

        # Create expiration date
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Store key info
        key_info = APIKeyInfo(
            key_id=key_id,
            key_hash=key_hash,
            user_id=user_id,
            name=name,
            scopes=scopes,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used=None,
            is_active=True,
        )

        self.keys_storage[key_id] = key_info
        logger.info(f"API key generated for user: {user_id}")

        return {
            "key_id": key_id,
            "api_key": f"ivy_{raw_key}",
            "name": name,
            "scopes": scopes,
            "expires_at": expires_at.isoformat() if expires_at else None,
        }

    def validate_key(self, api_key: str) -> Optional[APIKeyInfo]:
        """Validate API key"""
        if not api_key.startswith("ivy_"):
            return None

        raw_key = api_key[4:]  # Remove "ivy_" prefix
        key_hash = self._hash_key(raw_key)

        # Find key
        for key_info in self.keys_storage.values():
            if key_info.key_hash == key_hash:
                # Check expiration
                if key_info.expires_at and datetime.utcnow() > key_info.expires_at:
                    return None

                # Check if active
                if not key_info.is_active:
                    return None

                # Update last used
                key_info.last_used = datetime.utcnow()
                return key_info

        return None

    def has_scope(self, api_key: str, required_scope: str) -> bool:
        """Check if key has required scope"""
        key_info = self.validate_key(api_key)
        if not key_info:
            return False

        return required_scope in key_info.scopes or "*" in key_info.scopes

    def revoke_key(self, key_id: str) -> bool:
        """Revoke API key"""
        if key_id in self.keys_storage:
            self.keys_storage[key_id].is_active = False
            logger.info(f"API key revoked: {key_id}")
            return True
        return False

    def list_keys(self, user_id: str) -> List[APIKeyInfo]:
        """List user's API keys"""
        return [
            info for info in self.keys_storage.values()
            if info.user_id == user_id
        ]

    def rotate_key(self, key_id: str) -> Optional[Dict[str, str]]:
        """Rotate API key"""
        if key_id not in self.keys_storage:
            return None

        old_key = self.keys_storage[key_id]

        # Generate new key
        new_key_data = self.generate_key(
            user_id=old_key.user_id,
            name=f"{old_key.name} (rotated)",
            scopes=old_key.scopes,
            expires_in_days=7,  # New key expires in 7 days
        )

        # Revoke old key
        self.revoke_key(key_id)

        logger.info(f"API key rotated: {key_id}")
        return new_key_data

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash API key for storage"""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()


# Singleton instance
_api_key_manager = None


def get_api_key_manager() -> APIKeyManager:
    """Get API key manager singleton"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager
