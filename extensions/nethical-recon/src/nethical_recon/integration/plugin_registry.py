"""
Plugin Registry and Extension API

Manages plugin ecosystem, versioning, and community extensions.
Enhances existing marketplace functionality from phase_l.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ExtensionType(str, Enum):
    """Types of extensions"""

    SENSOR = "sensor"
    ENRICHMENT = "enrichment"
    SCANNER = "scanner"
    REPORTER = "reporter"
    ANALYZER = "analyzer"
    INTEGRATION = "integration"


class ExtensionStatus(str, Enum):
    """Status of extension"""

    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class ExtensionMetadata:
    """Extension metadata"""

    name: str
    version: str
    author: str
    description: str
    extension_type: ExtensionType
    tags: List[str] = field(default_factory=list)
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: str = "MIT"
    min_platform_version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Extension:
    """Plugin extension"""

    id: UUID = field(default_factory=uuid4)
    metadata: Optional[ExtensionMetadata] = None
    status: ExtensionStatus = ExtensionStatus.PENDING_REVIEW
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    review_notes: List[str] = field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    reviews_count: int = 0

    # Runtime attributes
    implementation: Optional[Callable] = None
    enabled: bool = False


class ExtensionInfo(BaseModel):
    """Extension information for API"""

    id: str
    name: str
    version: str
    author: str
    description: str
    extension_type: str
    status: str
    tags: List[str] = Field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    created_at: datetime
    updated_at: datetime


class PluginRegistry:
    """
    Central plugin registry managing community extensions.

    Handles extension registration, versioning, approval workflow,
    and lifecycle management.
    """

    def __init__(self):
        self.extensions: Dict[UUID, Extension] = {}
        self.name_index: Dict[str, UUID] = {}  # name -> id mapping
        self.type_index: Dict[ExtensionType, List[UUID]] = {t: [] for t in ExtensionType}

    def register_extension(
        self,
        metadata: ExtensionMetadata,
        implementation: Optional[Callable] = None,
    ) -> UUID:
        """
        Register new extension.

        Args:
            metadata: Extension metadata
            implementation: Extension implementation (callable)

        Returns:
            Extension ID
        """
        # Check if extension with same name exists
        if metadata.name in self.name_index:
            existing_id = self.name_index[metadata.name]
            existing = self.extensions[existing_id]

            # Check version to allow updates
            if metadata.version != existing.metadata.version:
                # New version - create new extension
                pass
            else:
                raise ValueError(f"Extension '{metadata.name}' version {metadata.version} already exists")

        extension = Extension(
            metadata=metadata,
            implementation=implementation,
            status=ExtensionStatus.PENDING_REVIEW,
        )

        self.extensions[extension.id] = extension
        self.name_index[metadata.name] = extension.id
        self.type_index[metadata.extension_type].append(extension.id)

        return extension.id

    def approve_extension(self, extension_id: UUID, reviewer_notes: Optional[str] = None):
        """Approve extension for marketplace"""
        if extension_id not in self.extensions:
            raise ValueError(f"Extension {extension_id} not found")

        extension = self.extensions[extension_id]
        extension.status = ExtensionStatus.APPROVED
        extension.updated_at = datetime.now(timezone.utc)

        if reviewer_notes:
            extension.review_notes.append(f"APPROVED: {reviewer_notes}")

    def reject_extension(self, extension_id: UUID, reason: str):
        """Reject extension"""
        if extension_id not in self.extensions:
            raise ValueError(f"Extension {extension_id} not found")

        extension = self.extensions[extension_id]
        extension.status = ExtensionStatus.REJECTED
        extension.updated_at = datetime.now(timezone.utc)
        extension.review_notes.append(f"REJECTED: {reason}")

    def deprecate_extension(self, extension_id: UUID, reason: str):
        """Mark extension as deprecated"""
        if extension_id not in self.extensions:
            raise ValueError(f"Extension {extension_id} not found")

        extension = self.extensions[extension_id]
        extension.status = ExtensionStatus.DEPRECATED
        extension.updated_at = datetime.now(timezone.utc)
        extension.review_notes.append(f"DEPRECATED: {reason}")

    def enable_extension(self, extension_id: UUID):
        """Enable extension for use"""
        if extension_id not in self.extensions:
            raise ValueError(f"Extension {extension_id} not found")

        extension = self.extensions[extension_id]

        if extension.status != ExtensionStatus.APPROVED:
            raise ValueError(f"Extension must be approved before enabling")

        extension.enabled = True
        extension.status = ExtensionStatus.ACTIVE

    def disable_extension(self, extension_id: UUID):
        """Disable extension"""
        if extension_id not in self.extensions:
            raise ValueError(f"Extension {extension_id} not found")

        extension = self.extensions[extension_id]
        extension.enabled = False
        extension.status = ExtensionStatus.INACTIVE

    def get_extension(self, extension_id: UUID) -> Optional[Extension]:
        """Get extension by ID"""
        return self.extensions.get(extension_id)

    def get_extension_by_name(self, name: str) -> Optional[Extension]:
        """Get extension by name"""
        extension_id = self.name_index.get(name)
        if extension_id:
            return self.extensions.get(extension_id)
        return None

    def list_extensions(
        self,
        extension_type: Optional[ExtensionType] = None,
        status: Optional[ExtensionStatus] = None,
        enabled_only: bool = False,
    ) -> List[Extension]:
        """
        List extensions with filters.

        Args:
            extension_type: Filter by extension type
            status: Filter by status
            enabled_only: Only return enabled extensions

        Returns:
            List of matching extensions
        """
        if extension_type:
            extension_ids = self.type_index.get(extension_type, [])
            extensions = [self.extensions[eid] for eid in extension_ids if eid in self.extensions]
        else:
            extensions = list(self.extensions.values())

        if status:
            extensions = [e for e in extensions if e.status == status]

        if enabled_only:
            extensions = [e for e in extensions if e.enabled]

        return extensions

    def record_download(self, extension_id: UUID):
        """Record extension download"""
        if extension_id in self.extensions:
            self.extensions[extension_id].downloads += 1

    def add_rating(self, extension_id: UUID, rating: float):
        """Add rating to extension (1-5 stars)"""
        if extension_id not in self.extensions:
            raise ValueError(f"Extension {extension_id} not found")

        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        extension = self.extensions[extension_id]

        # Calculate new average rating
        total_ratings = extension.rating * extension.reviews_count
        total_ratings += rating
        extension.reviews_count += 1
        extension.rating = total_ratings / extension.reviews_count

    def search_extensions(self, query: str) -> List[Extension]:
        """Search extensions by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for extension in self.extensions.values():
            if not extension.metadata:
                continue

            # Search in name, description, and tags
            if (
                query_lower in extension.metadata.name.lower()
                or query_lower in extension.metadata.description.lower()
                or any(query_lower in tag.lower() for tag in extension.metadata.tags)
            ):
                results.append(extension)

        return results


class ExtensionAPI:
    """
    Extension API for community plugin development.

    Provides standardized interface for plugin developers to integrate
    with the platform.
    """

    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.hooks: Dict[str, List[Callable]] = {}

    def register_hook(self, hook_name: str, callback: Callable):
        """
        Register hook callback.

        Args:
            hook_name: Name of hook point
            callback: Function to call at hook point
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    async def execute_hook(self, hook_name: str, **context) -> List[Any]:
        """
        Execute all callbacks for a hook.

        Args:
            hook_name: Hook to execute
            **context: Context data to pass to callbacks

        Returns:
            List of results from callbacks
        """
        if hook_name not in self.hooks:
            return []

        results = []
        for callback in self.hooks[hook_name]:
            try:
                if hasattr(callback, "__call__"):
                    result = callback(**context)
                    # Handle async callbacks
                    if hasattr(result, "__await__"):
                        result = await result
                    results.append(result)
            except Exception as e:
                print(f"Error executing hook {hook_name}: {e}")

        return results

    def list_hooks(self) -> List[str]:
        """List available hook points"""
        return list(self.hooks.keys())


# Global registry instance
_plugin_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """Get or create global plugin registry"""
    global _plugin_registry
    if _plugin_registry is None:
        _plugin_registry = PluginRegistry()
    return _plugin_registry
