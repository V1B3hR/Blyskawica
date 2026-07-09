"""
Role-Based Access Control (RBAC)
Fine-grained access control for Nethical Recon resources
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class ResourceType(Enum):
    """Types of resources that can be protected"""

    WORKSPACE = "workspace"
    FINDING = "finding"
    SCAN = "scan"
    REPORT = "report"
    TARGET = "target"
    EVIDENCE = "evidence"


class Action(Enum):
    """Actions that can be performed on resources"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SHARE = "share"


@dataclass
class Permission:
    """Permission linking role to resource and action"""

    permission_id: UUID
    role_id: UUID
    resource_type: ResourceType
    action: Action
    conditions: dict[str, Any]  # Additional conditions (e.g., ownership)


@dataclass
class Role:
    """Role with set of permissions"""

    role_id: UUID
    name: str
    description: str
    permissions: list[Permission]
    is_system_role: bool
    created_at: datetime


class RBACManager:
    """
    Role-Based Access Control manager

    Features:
    - Role management
    - Permission assignment
    - Access control checks
    - Audit logging
    """

    def __init__(self):
        """Initialize RBAC manager with default roles"""
        self._roles: dict[UUID, Role] = {}
        self._user_roles: dict[UUID, list[UUID]] = {}  # user_id -> role_ids
        self._initialize_system_roles()

    def _initialize_system_roles(self):
        """Create default system roles"""
        from uuid import uuid4

        # Admin role
        admin_role = Role(
            role_id=uuid4(),
            name="admin",
            description="Full system access",
            permissions=[],
            is_system_role=True,
            created_at=datetime.now(),
        )
        self._roles[admin_role.role_id] = admin_role

        # Analyst role
        analyst_role = Role(
            role_id=uuid4(),
            name="analyst",
            description="Security analyst with read/write access",
            permissions=[],
            is_system_role=True,
            created_at=datetime.now(),
        )
        self._roles[analyst_role.role_id] = analyst_role

        # Viewer role
        viewer_role = Role(
            role_id=uuid4(),
            name="viewer",
            description="Read-only access",
            permissions=[],
            is_system_role=True,
            created_at=datetime.now(),
        )
        self._roles[viewer_role.role_id] = viewer_role

    def create_role(self, name: str, description: str) -> Role:
        """Create a custom role"""
        from uuid import uuid4

        role = Role(
            role_id=uuid4(),
            name=name,
            description=description,
            permissions=[],
            is_system_role=False,
            created_at=datetime.now(),
        )
        self._roles[role.role_id] = role
        return role

    def add_permission_to_role(
        self, role_id: UUID, resource_type: ResourceType, action: Action, conditions: dict[str, Any] | None = None
    ) -> Permission:
        """Add a permission to a role"""
        from uuid import uuid4

        if role_id not in self._roles:
            raise ValueError(f"Role {role_id} not found")

        role = self._roles[role_id]

        if role.is_system_role:
            raise ValueError("Cannot modify system roles")

        permission = Permission(
            permission_id=uuid4(),
            role_id=role_id,
            resource_type=resource_type,
            action=action,
            conditions=conditions or {},
        )

        role.permissions.append(permission)
        return permission

    def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Assign a role to a user"""
        if role_id not in self._roles:
            return False

        if user_id not in self._user_roles:
            self._user_roles[user_id] = []

        if role_id not in self._user_roles[user_id]:
            self._user_roles[user_id].append(role_id)
            return True

        return False

    def revoke_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Revoke a role from a user"""
        if user_id in self._user_roles and role_id in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role_id)
            return True
        return False

    def check_access(
        self, user_id: UUID, resource_type: ResourceType, action: Action, context: dict[str, Any] | None = None
    ) -> bool:
        """
        Check if user has access to perform action on resource type

        Args:
            user_id: User ID
            resource_type: Type of resource
            action: Action to perform
            context: Additional context for condition evaluation

        Returns:
            True if access is granted
        """
        if user_id not in self._user_roles:
            return False

        context = context or {}

        # Check all roles assigned to user
        for role_id in self._user_roles[user_id]:
            role = self._roles.get(role_id)
            if not role:
                continue

            # Admin role has all permissions
            if role.name == "admin":
                return True

            # Check role permissions
            for permission in role.permissions:
                if permission.resource_type == resource_type and permission.action == action:
                    # Check conditions
                    if self._evaluate_conditions(permission.conditions, context):
                        return True

        return False

    def _evaluate_conditions(self, conditions: dict[str, Any], context: dict[str, Any]) -> bool:
        """Evaluate permission conditions against context"""
        if not conditions:
            return True

        # Example condition: ownership
        if "owner" in conditions and "resource_owner" in context:
            return conditions["owner"] == context["resource_owner"]

        # Example condition: workspace membership
        if "workspace" in conditions and "workspace_id" in context:
            return conditions["workspace"] == context["workspace_id"]

        return True

    def get_user_roles(self, user_id: UUID) -> list[Role]:
        """Get all roles assigned to a user"""
        if user_id not in self._user_roles:
            return []

        return [self._roles[role_id] for role_id in self._user_roles[user_id] if role_id in self._roles]

    def get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """Get all permissions for a role"""
        role = self._roles.get(role_id)
        return role.permissions if role else []
