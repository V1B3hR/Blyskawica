"""
Multi-User Workspaces
Manages collaborative workspaces for team-based security operations
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class WorkspaceVisibility(Enum):
    """Workspace visibility levels"""

    PRIVATE = "private"
    TEAM = "team"
    ORGANIZATION = "organization"
    PUBLIC = "public"


@dataclass
class Workspace:
    """Collaborative workspace"""

    workspace_id: UUID
    name: str
    description: str
    owner_id: UUID
    visibility: WorkspaceVisibility
    created_at: datetime
    updated_at: datetime
    member_ids: list[UUID]
    settings: dict[str, Any]
    tags: list[str]


@dataclass
class WorkspaceMember:
    """Workspace member with role"""

    user_id: UUID
    workspace_id: UUID
    role: str  # owner, admin, member, viewer
    joined_at: datetime
    permissions: list[str]


class WorkspaceManager:
    """
    Manages collaborative workspaces for security teams

    Features:
    - Workspace creation and management
    - Member management
    - Access control
    - Resource sharing
    """

    def __init__(self):
        """Initialize workspace manager"""
        self._workspaces: dict[UUID, Workspace] = {}
        self._members: dict[UUID, list[WorkspaceMember]] = {}

    def create_workspace(
        self,
        name: str,
        owner_id: UUID,
        description: str = "",
        visibility: WorkspaceVisibility = WorkspaceVisibility.TEAM,
        settings: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> Workspace:
        """
        Create a new workspace

        Args:
            name: Workspace name
            owner_id: User ID of workspace owner
            description: Workspace description
            visibility: Workspace visibility level
            settings: Custom workspace settings
            tags: Workspace tags

        Returns:
            Created workspace
        """
        workspace_id = uuid4()
        now = datetime.now()

        workspace = Workspace(
            workspace_id=workspace_id,
            name=name,
            description=description,
            owner_id=owner_id,
            visibility=visibility,
            created_at=now,
            updated_at=now,
            member_ids=[owner_id],
            settings=settings or {},
            tags=tags or [],
        )

        self._workspaces[workspace_id] = workspace

        # Add owner as member with full permissions
        owner_member = WorkspaceMember(
            user_id=owner_id,
            workspace_id=workspace_id,
            role="owner",
            joined_at=now,
            permissions=["*"],  # All permissions
        )
        self._members[workspace_id] = [owner_member]

        return workspace

    def add_member(
        self, workspace_id: UUID, user_id: UUID, role: str = "member", permissions: list[str] | None = None
    ) -> WorkspaceMember:
        """
        Add a member to a workspace

        Args:
            workspace_id: Workspace ID
            user_id: User ID to add
            role: Member role
            permissions: Specific permissions (optional)

        Returns:
            Workspace member object
        """
        if workspace_id not in self._workspaces:
            raise ValueError(f"Workspace {workspace_id} not found")

        workspace = self._workspaces[workspace_id]

        # Check if already a member
        if user_id in workspace.member_ids:
            raise ValueError(f"User {user_id} is already a member")

        # Default permissions by role
        if permissions is None:
            permissions = self._get_default_permissions(role)

        member = WorkspaceMember(
            user_id=user_id, workspace_id=workspace_id, role=role, joined_at=datetime.now(), permissions=permissions
        )

        # Update workspace
        workspace.member_ids.append(user_id)
        workspace.updated_at = datetime.now()

        # Add to members list
        if workspace_id not in self._members:
            self._members[workspace_id] = []
        self._members[workspace_id].append(member)

        return member

    def remove_member(self, workspace_id: UUID, user_id: UUID) -> bool:
        """
        Remove a member from a workspace

        Args:
            workspace_id: Workspace ID
            user_id: User ID to remove

        Returns:
            True if removed, False otherwise
        """
        if workspace_id not in self._workspaces:
            return False

        workspace = self._workspaces[workspace_id]

        # Cannot remove owner
        if user_id == workspace.owner_id:
            raise ValueError("Cannot remove workspace owner")

        if user_id in workspace.member_ids:
            workspace.member_ids.remove(user_id)
            workspace.updated_at = datetime.now()

            # Remove from members list
            if workspace_id in self._members:
                self._members[workspace_id] = [m for m in self._members[workspace_id] if m.user_id != user_id]

            return True

        return False

    def get_workspace(self, workspace_id: UUID) -> Workspace | None:
        """Get workspace by ID"""
        return self._workspaces.get(workspace_id)

    def list_workspaces(
        self, user_id: UUID | None = None, visibility: WorkspaceVisibility | None = None, tags: list[str] | None = None
    ) -> list[Workspace]:
        """
        List workspaces with optional filtering

        Args:
            user_id: Filter by user membership
            visibility: Filter by visibility level
            tags: Filter by tags

        Returns:
            List of matching workspaces
        """
        workspaces = list(self._workspaces.values())

        # Filter by user
        if user_id:
            workspaces = [w for w in workspaces if user_id in w.member_ids]

        # Filter by visibility
        if visibility:
            workspaces = [w for w in workspaces if w.visibility == visibility]

        # Filter by tags
        if tags:
            workspaces = [w for w in workspaces if any(tag in w.tags for tag in tags)]

        return workspaces

    def get_members(self, workspace_id: UUID) -> list[WorkspaceMember]:
        """Get all members of a workspace"""
        return self._members.get(workspace_id, [])

    def update_member_role(self, workspace_id: UUID, user_id: UUID, new_role: str) -> bool:
        """Update a member's role in a workspace"""
        if workspace_id not in self._members:
            return False

        for member in self._members[workspace_id]:
            if member.user_id == user_id:
                member.role = new_role
                member.permissions = self._get_default_permissions(new_role)

                workspace = self._workspaces[workspace_id]
                workspace.updated_at = datetime.now()

                return True

        return False

    def _get_default_permissions(self, role: str) -> list[str]:
        """Get default permissions for a role"""
        permissions_map = {
            "owner": ["*"],
            "admin": [
                "workspace.read",
                "workspace.write",
                "members.read",
                "members.write",
                "findings.read",
                "findings.write",
                "findings.delete",
                "scans.read",
                "scans.write",
                "scans.execute",
                "reports.read",
                "reports.generate",
            ],
            "member": [
                "workspace.read",
                "findings.read",
                "findings.write",
                "scans.read",
                "scans.execute",
                "reports.read",
            ],
            "viewer": ["workspace.read", "findings.read", "reports.read"],
        }
        return permissions_map.get(role, permissions_map["viewer"])

    def check_permission(self, workspace_id: UUID, user_id: UUID, permission: str) -> bool:
        """
        Check if a user has a specific permission in a workspace

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            permission: Permission to check

        Returns:
            True if user has permission
        """
        if workspace_id not in self._members:
            return False

        for member in self._members[workspace_id]:
            if member.user_id == user_id:
                # Check for wildcard permission
                if "*" in member.permissions:
                    return True
                # Check for specific permission
                return permission in member.permissions

        return False
