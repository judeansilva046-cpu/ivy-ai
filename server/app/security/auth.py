"""
Authentication and security utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from config.settings import get_settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHandler:
    """Password hashing and verification"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return pwd_context.verify(plain_password, hashed_password)


class JWTHandler:
    """JWT token generation and validation"""

    @staticmethod
    def create_tokens(
        subject: str,
        user_id: str,
        is_admin: bool = False,
        expires_delta: Optional[timedelta] = None,
    ) -> Dict[str, str]:
        """Create access and refresh tokens"""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)

        # Access token
        access_payload = {
            "sub": subject,
            "user_id": user_id,
            "is_admin": is_admin,
            "type": "access",
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow(),
        }

        access_token = jwt.encode(
            access_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        # Refresh token (longer expiration)
        refresh_payload = {
            "sub": subject,
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
        }

        refresh_token = jwt.encode(
            refresh_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            raise JWTError("Invalid token")

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify token validity and type"""
        payload = JWTHandler.decode_token(token)

        if payload.get("type") != token_type:
            raise JWTError(f"Invalid token type. Expected {token_type}")

        return payload


# Utility functions
def get_password_hash(password: str) -> str:
    """Hash a password"""
    return PasswordHandler.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return PasswordHandler.verify_password(plain_password, hashed_password)


def create_tokens(
    subject: str,
    user_id: str,
    is_admin: bool = False,
) -> Dict[str, str]:
    """Create JWT tokens"""
    return JWTHandler.create_tokens(subject, user_id, is_admin)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT token"""
    return JWTHandler.decode_token(token)
