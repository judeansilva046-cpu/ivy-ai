"""
ETAPA 12: Security Configuration
Authentication, authorization, and encryption setup
"""
from datetime import timedelta
from typing import Optional
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SecurityConfig:
    """Security configuration for Ivy AI"""

    # JWT Configuration
    JWT_ALGORITHM = "HS256"
    JWT_SECRET_KEY = "your-secret-key-change-in-production"  # Use env var
    JWT_EXPIRATION_HOURS = 24
    JWT_REFRESH_EXPIRATION_DAYS = 7

    # API Keys
    API_KEY_HEADER = "X-API-Key"
    API_KEY_LENGTH = 32

    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = {
        "general": 100,
        "agents": 50,
        "tools": 200,
        "plugins": 100,
    }

    # Password Policy
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True

    # Session Configuration
    SESSION_TIMEOUT_MINUTES = 30
    REMEMBER_ME_DAYS = 7

    # Encryption
    ENCRYPTION_ALGORITHM = "AES-256-GCM"
    ENCRYPTION_KEY = "your-encryption-key-change-in-production"

    # OWASP Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    }

    # Audit Logging
    AUDIT_ENABLED = True
    AUDIT_LOG_SENSITIVE = True
    AUDIT_RETENTION_DAYS = 90


class RBACConfig:
    """Role-Based Access Control configuration"""

    ROLES = {
        "admin": {
            "permissions": ["*"],
            "description": "Administrator with full access",
        },
        "user": {
            "permissions": [
                "chat.execute",
                "agent.execute",
                "plugin.execute",
                "profile.read",
            ],
            "description": "Regular user",
        },
        "guest": {
            "permissions": ["chat.execute"],
            "description": "Guest user (limited access)",
        },
        "developer": {
            "permissions": [
                "agent.execute",
                "tool.execute",
                "plugin.register",
                "plugin.manage",
                "api.access",
            ],
            "description": "Plugin developer",
        },
    }

    ROLE_HIERARCHY = {
        "admin": ["developer", "user", "guest"],
        "developer": ["user", "guest"],
        "user": ["guest"],
        "guest": [],
    }


class InputValidationConfig:
    """Input validation configuration"""

    # Field length limits
    MAX_STRING_LENGTH = 10000
    MAX_ARRAY_LENGTH = 1000
    MAX_OBJECT_DEPTH = 10

    # Forbidden patterns
    FORBIDDEN_PATTERNS = [
        r"<script",  # XSS
        r"javascript:",  # XSS
        r"on\w+\s*=",  # Event handlers
        r"';.*--",  # SQL injection
        r"1'\s*or\s*'1'",  # SQL injection
    ]

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        "images": ["jpg", "jpeg", "png", "gif", "webp"],
        "audio": ["mp3", "wav", "ogg", "m4a"],
        "documents": ["pdf", "txt", "docx", "xlsx"],
    }

    MAX_FILE_SIZE_MB = 100


def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    logger.info("Security configuration loaded")
    return SecurityConfig()


def get_rbac_config() -> RBACConfig:
    """Get RBAC configuration"""
    return RBACConfig()


def get_validation_config() -> InputValidationConfig:
    """Get input validation configuration"""
    return InputValidationConfig()
