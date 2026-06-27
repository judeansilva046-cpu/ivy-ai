"""
RBAC (Role-Based Access Control) for Ivy AI
Role hierarchy and permission checking
"""
from typing import List, Set, Dict, Optional
from dataclasses import dataclass
from app.utils.logger import setup_logger
from app.security.config import RBACConfig

logger = setup_logger(__name__)


@dataclass
class Role:
    """Role definition"""
    name: str
    permissions: Set[str]
    description: str


@dataclass
class User:
    """User with roles"""
    user_id: str
    email: str
    roles: List[str]
    is_active: bool


class RBACManager:
    """Role-Based Access Control manager"""

    def __init__(self):
        self.config = RBACConfig()
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self._initialize_roles()

    def _initialize_roles(self):
        """Initialize default roles"""
        for role_name, role_config in self.config.ROLES.items():
            self.roles[role_name] = Role(
                name=role_name,
                permissions=set(role_config["permissions"]),
                description=role_config["description"],
            )

    def create_role(
        self,
        name: str,
        permissions: List[str],
        description: str = "",
    ) -> bool:
        """Create new role"""
        if name in self.roles:
            return False

        self.roles[name] = Role(
            name=name,
            permissions=set(permissions),
            description=description,
        )

        logger.info(f"Role created: {name}")
        return True

    def add_permission_to_role(self, role_name: str, permission: str) -> bool:
        """Add permission to role"""
        if role_name not in self.roles:
            return False

        self.roles[role_name].permissions.add(permission)
        logger.info(f"Permission added to {role_name}: {permission}")
        return True

    def remove_permission_from_role(self, role_name: str, permission: str) -> bool:
        """Remove permission from role"""
        if role_name not in self.roles:
            return False

        self.roles[role_name].permissions.discard(permission)
        logger.info(f"Permission removed from {role_name}: {permission}")
        return True

    def register_user(
        self,
        user_id: str,
        email: str,
        roles: List[str] = None,
    ) -> bool:
        """Register user with roles"""
        if user_id in self.users:
            return False

        if roles is None:
            roles = ["user"]

        self.users[user_id] = User(
            user_id=user_id,
            email=email,
            roles=roles,
            is_active=True,
        )

        logger.info(f"User registered: {user_id} with roles: {roles}")
        return True

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        if user_id not in self.users or role_name not in self.roles:
            return False

        if role_name not in self.users[user_id].roles:
            self.users[user_id].roles.append(role_name)
            logger.info(f"Role assigned to {user_id}: {role_name}")

        return True

    def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove role from user"""
        if user_id not in self.users:
            return False

        if role_name in self.users[user_id].roles:
            self.users[user_id].roles.remove(role_name)
            logger.info(f"Role removed from {user_id}: {role_name}")

        return True

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission"""
        if user_id not in self.users:
            return False

        user = self.users[user_id]

        if not user.is_active:
            return False

        # Check all user roles
        for role_name in user.roles:
            if role_name not in self.roles:
                continue

            role = self.roles[role_name]

            # Wildcard permission
            if "*" in role.permissions:
                return True

            # Direct permission
            if permission in role.permissions:
                return True

            # Check inherited permissions
            if self._check_inherited_permission(role_name, permission):
                return True

        return False

    def has_any_permission(self, user_id: str, permissions: List[str]) -> bool:
        """Check if user has any of the permissions"""
        for permission in permissions:
            if self.has_permission(user_id, permission):
                return True
        return False

    def has_all_permissions(self, user_id: str, permissions: List[str]) -> bool:
        """Check if user has all permissions"""
        for permission in permissions:
            if not self.has_permission(user_id, permission):
                return False
        return True

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for user"""
        if user_id not in self.users:
            return set()

        user = self.users[user_id]
        permissions = set()

        for role_name in user.roles:
            if role_name in self.roles:
                permissions.update(self.roles[role_name].permissions)

        return permissions

    def get_effective_roles(self, user_id: str) -> List[str]:
        """Get user's effective roles (including inherited)"""
        if user_id not in self.users:
            return []

        user = self.users[user_id]
        effective_roles = set(user.roles)

        # Add inherited roles
        for role_name in user.roles:
            inherited = self.config.ROLE_HIERARCHY.get(role_name, [])
            effective_roles.update(inherited)

        return list(effective_roles)

    def _check_inherited_permission(
        self,
        role_name: str,
        permission: str
    ) -> bool:
        """Check if permission is inherited from role hierarchy"""
        if role_name not in self.config.ROLE_HIERARCHY:
            return False

        for inherited_role in self.config.ROLE_HIERARCHY[role_name]:
            if inherited_role in self.roles:
                if permission in self.roles[inherited_role].permissions:
                    return True

        return False

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user"""
        if user_id not in self.users:
            return False

        self.users[user_id].is_active = False
        logger.info(f"User deactivated: {user_id}")
        return True

    def activate_user(self, user_id: str) -> bool:
        """Activate user"""
        if user_id not in self.users:
            return False

        self.users[user_id].is_active = True
        logger.info(f"User activated: {user_id}")
        return True


# Singleton instance
_rbac_manager = None


def get_rbac_manager() -> RBACManager:
    """Get RBAC manager singleton"""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager
