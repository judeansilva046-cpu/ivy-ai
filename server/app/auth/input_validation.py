"""
Input Validation and Sanitization for Ivy AI
Data validation and security
"""
import re
from typing import Any, Dict, List, Optional
from app.utils.logger import setup_logger
from app.security.config import InputValidationConfig

logger = setup_logger(__name__)


class ValidationError(Exception):
    """Validation error"""
    pass


class InputValidator:
    """Input validation and sanitization"""

    def __init__(self):
        self.config = InputValidationConfig()

    def validate_string(
        self,
        value: str,
        field_name: str = "field",
        max_length: Optional[int] = None,
    ) -> str:
        """Validate and sanitize string"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")

        if max_length is None:
            max_length = self.config.MAX_STRING_LENGTH

        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} exceeds maximum length of {max_length}"
            )

        # Check for forbidden patterns
        sanitized = self._sanitize_string(value)

        return sanitized

    def validate_email(self, email: str) -> str:
        """Validate email address"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")

        return email

    def validate_password(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < self.config.MIN_PASSWORD_LENGTH:
            raise ValidationError(
                f"Password must be at least {self.config.MIN_PASSWORD_LENGTH} characters"
            )

        if self.config.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain uppercase letters")

        if self.config.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain lowercase letters")

        if self.config.REQUIRE_NUMBERS and not re.search(r'\d', password):
            raise ValidationError("Password must contain numbers")

        if self.config.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain special characters")

        return True

    def validate_array(
        self,
        value: List,
        field_name: str = "field",
        max_length: Optional[int] = None,
    ) -> List:
        """Validate array/list"""
        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be an array")

        if max_length is None:
            max_length = self.config.MAX_ARRAY_LENGTH

        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} exceeds maximum length of {max_length}"
            )

        return value

    def validate_dict(
        self,
        value: Dict,
        field_name: str = "field",
        max_depth: Optional[int] = None,
    ) -> Dict:
        """Validate dictionary/object"""
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be an object")

        if max_depth is None:
            max_depth = self.config.MAX_OBJECT_DEPTH

        if self._get_dict_depth(value) > max_depth:
            raise ValidationError(
                f"{field_name} exceeds maximum depth of {max_depth}"
            )

        return value

    def validate_file(
        self,
        filename: str,
        file_type: str = "documents",
    ) -> bool:
        """Validate file extension and type"""
        allowed_exts = self.config.ALLOWED_EXTENSIONS.get(file_type, [])

        ext = filename.split('.')[-1].lower()

        if ext not in allowed_exts:
            raise ValidationError(
                f"File type .{ext} not allowed. Allowed types: {', '.join(allowed_exts)}"
            )

        return True

    def sanitize_input(self, data: Any) -> Any:
        """Sanitize any input data"""
        if isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        else:
            return data

    def _sanitize_string(self, value: str) -> str:
        """Sanitize string for XSS and injection attacks"""
        for pattern in self.config.FORBIDDEN_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potentially dangerous pattern detected: {pattern}")
                raise ValidationError("Input contains forbidden patterns")

        # Remove null bytes
        value = value.replace('\x00', '')

        # Remove control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')

        return value

    @staticmethod
    def _get_dict_depth(d: Dict, current_depth: int = 1) -> int:
        """Get maximum depth of nested dictionary"""
        if not isinstance(d, dict):
            return current_depth

        max_depth = current_depth
        for value in d.values():
            if isinstance(value, dict):
                depth = InputValidator._get_dict_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)

        return max_depth


# Singleton instance
_validator = None


def get_input_validator() -> InputValidator:
    """Get input validator singleton"""
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator


def validate_and_sanitize(data: Any) -> Any:
    """Validate and sanitize input data"""
    validator = get_input_validator()
    return validator.sanitize_input(data)
