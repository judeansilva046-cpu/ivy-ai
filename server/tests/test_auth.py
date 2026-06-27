"""
Tests for Authentication & Authorization
JWT, API Keys, RBAC, Input Validation
"""
import pytest
from app.auth.jwt import JWTManager, TokenBlacklist, get_jwt_manager, get_token_blacklist
from app.auth.api_keys import APIKeyManager, get_api_key_manager
from app.auth.rbac import RBACManager, get_rbac_manager
from app.auth.input_validation import InputValidator, ValidationError, get_input_validator


class TestJWTManager:
    """Test JWT management"""

    def test_jwt_manager_singleton(self):
        """Test JWT manager is singleton"""
        manager1 = get_jwt_manager()
        manager2 = get_jwt_manager()
        assert manager1 is manager2

    def test_generate_token(self):
        """Test token generation"""
        manager = get_jwt_manager()
        tokens = manager.generate_token(
            user_id="user123",
            email="test@example.com",
            roles=["user"],
        )

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "Bearer"

    def test_validate_token(self):
        """Test token validation"""
        manager = get_jwt_manager()
        tokens = manager.generate_token("user123", "test@example.com")

        payload = manager.validate_token(tokens["access_token"])
        assert payload is not None
        assert payload["user_id"] == "user123"

    def test_invalid_token(self):
        """Test invalid token"""
        manager = get_jwt_manager()
        payload = manager.validate_token("invalid.token.here")
        assert payload is None

    def test_refresh_token(self):
        """Test token refresh"""
        manager = get_jwt_manager()
        tokens = manager.generate_token("user123", "test@example.com")

        new_access = manager.refresh_access_token(tokens["refresh_token"])
        assert new_access is not None


class TestTokenBlacklist:
    """Test token blacklist"""

    def test_blacklist_token(self):
        """Test adding token to blacklist"""
        blacklist = get_token_blacklist()
        token = "test.token.123"

        blacklist.add_to_blacklist(token)
        assert blacklist.is_blacklisted(token)

    def test_clear_blacklist(self):
        """Test clearing blacklist"""
        blacklist = get_token_blacklist()
        blacklist.add_to_blacklist("token1")
        blacklist.add_to_blacklist("token2")

        blacklist.clear_blacklist()
        assert not blacklist.is_blacklisted("token1")


class TestAPIKeyManager:
    """Test API key management"""

    def test_api_key_manager_singleton(self):
        """Test API key manager is singleton"""
        manager1 = get_api_key_manager()
        manager2 = get_api_key_manager()
        assert manager1 is manager2

    def test_generate_key(self):
        """Test API key generation"""
        manager = get_api_key_manager()
        key_data = manager.generate_key(
            user_id="user123",
            name="Test Key",
            scopes=["read", "write"],
        )

        assert "api_key" in key_data
        assert "key_id" in key_data
        assert key_data["api_key"].startswith("ivy_")

    def test_validate_key(self):
        """Test API key validation"""
        manager = get_api_key_manager()
        key_data = manager.generate_key("user123", "Test Key")

        key_info = manager.validate_key(key_data["api_key"])
        assert key_info is not None
        assert key_info.user_id == "user123"

    def test_invalid_key(self):
        """Test invalid API key"""
        manager = get_api_key_manager()
        key_info = manager.validate_key("invalid_key")
        assert key_info is None

    def test_key_scope(self):
        """Test key scope validation"""
        manager = get_api_key_manager()
        key_data = manager.generate_key(
            user_id="user123",
            name="Test Key",
            scopes=["read"],
        )

        has_read = manager.has_scope(key_data["api_key"], "read")
        has_write = manager.has_scope(key_data["api_key"], "write")

        assert has_read is True
        assert has_write is False

    def test_revoke_key(self):
        """Test key revocation"""
        manager = get_api_key_manager()
        key_data = manager.generate_key("user123", "Test Key")

        manager.revoke_key(key_data["key_id"])
        key_info = manager.validate_key(key_data["api_key"])
        assert key_info is None


class TestRBACManager:
    """Test RBAC management"""

    def test_rbac_manager_singleton(self):
        """Test RBAC manager is singleton"""
        manager1 = get_rbac_manager()
        manager2 = get_rbac_manager()
        assert manager1 is manager2

    def test_register_user(self):
        """Test user registration"""
        manager = get_rbac_manager()
        success = manager.register_user(
            user_id="user123",
            email="test@example.com",
            roles=["user"],
        )
        assert success is True

    def test_assign_role(self):
        """Test role assignment"""
        manager = get_rbac_manager()
        manager.register_user("user123", "test@example.com")

        success = manager.assign_role("user123", "developer")
        assert success is True

    def test_has_permission(self):
        """Test permission checking"""
        manager = get_rbac_manager()
        manager.register_user("user123", "test@example.com", roles=["user"])

        # User role should have chat.execute
        has_perm = manager.has_permission("user123", "chat.execute")
        assert has_perm is True

    def test_admin_wildcard_permission(self):
        """Test admin wildcard permission"""
        manager = get_rbac_manager()
        manager.register_user("admin123", "admin@example.com", roles=["admin"])

        # Admin should have all permissions
        has_perm = manager.has_permission("admin123", "any.permission")
        assert has_perm is True

    def test_deactivate_user(self):
        """Test user deactivation"""
        manager = get_rbac_manager()
        manager.register_user("user123", "test@example.com")

        manager.deactivate_user("user123")
        has_perm = manager.has_permission("user123", "chat.execute")
        assert has_perm is False


class TestInputValidator:
    """Test input validation"""

    def test_validator_singleton(self):
        """Test validator is singleton"""
        val1 = get_input_validator()
        val2 = get_input_validator()
        assert val1 is val2

    def test_validate_string(self):
        """Test string validation"""
        validator = get_input_validator()
        result = validator.validate_string("test string", "test_field")
        assert result == "test string"

    def test_validate_string_too_long(self):
        """Test string length validation"""
        validator = get_input_validator()
        long_string = "x" * 15000

        with pytest.raises(ValidationError):
            validator.validate_string(long_string)

    def test_validate_email(self):
        """Test email validation"""
        validator = get_input_validator()
        email = validator.validate_email("test@example.com")
        assert email == "test@example.com"

    def test_invalid_email(self):
        """Test invalid email"""
        validator = get_input_validator()
        with pytest.raises(ValidationError):
            validator.validate_email("invalid-email")

    def test_validate_password_weak(self):
        """Test weak password"""
        validator = get_input_validator()
        with pytest.raises(ValidationError):
            validator.validate_password("short")

    def test_validate_password_strong(self):
        """Test strong password"""
        validator = get_input_validator()
        result = validator.validate_password("StrongPass123!@#")
        assert result is True

    def test_validate_array(self):
        """Test array validation"""
        validator = get_input_validator()
        arr = validator.validate_array([1, 2, 3], "test_array")
        assert arr == [1, 2, 3]

    def test_sanitize_xss(self):
        """Test XSS sanitization"""
        validator = get_input_validator()
        with pytest.raises(ValidationError):
            validator.validate_string("<script>alert('xss')</script>")

    def test_sanitize_sql_injection(self):
        """Test SQL injection sanitization"""
        validator = get_input_validator()
        with pytest.raises(ValidationError):
            validator.validate_string("'; DROP TABLE users; --")
