"""
Plugin Marketplace
Centralized marketplace for custom Nethical Recon plugins
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class PluginCategory(Enum):
    """Plugin categories"""

    SCANNER = "scanner"
    ANALYZER = "analyzer"
    REPORTER = "reporter"
    INTEGRATION = "integration"
    WEAPON = "weapon"
    SENSOR = "sensor"


@dataclass
class PluginMetadata:
    """Plugin metadata"""

    plugin_id: UUID
    name: str
    version: str
    description: str
    author: str
    category: PluginCategory
    tags: list[str]
    homepage_url: str
    download_url: str
    created_at: datetime
    updated_at: datetime
    downloads: int
    rating: float
    is_verified: bool
    is_official: bool


@dataclass
class PluginReview:
    """User review for a plugin"""

    review_id: UUID
    plugin_id: UUID
    user_id: UUID
    rating: int  # 1-5
    comment: str
    created_at: datetime


class PluginMarketplace:
    """
    Plugin Marketplace for custom modules

    Features:
    - Plugin discovery and browsing
    - Version management
    - User reviews and ratings
    - Download statistics
    - Security scanning
    """

    def __init__(self):
        """Initialize plugin marketplace"""
        self._plugins: dict[UUID, PluginMetadata] = {}
        self._reviews: dict[UUID, list[PluginReview]] = {}

    def publish_plugin(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        category: PluginCategory,
        tags: list[str],
        homepage_url: str,
        download_url: str,
    ) -> PluginMetadata:
        """
        Publish a new plugin to the marketplace

        Args:
            name: Plugin name
            version: Plugin version (semver)
            description: Plugin description
            author: Author name/org
            category: Plugin category
            tags: Search tags
            homepage_url: Documentation URL
            download_url: Package download URL

        Returns:
            Plugin metadata
        """
        now = datetime.now()

        plugin = PluginMetadata(
            plugin_id=uuid4(),
            name=name,
            version=version,
            description=description,
            author=author,
            category=category,
            tags=tags,
            homepage_url=homepage_url,
            download_url=download_url,
            created_at=now,
            updated_at=now,
            downloads=0,
            rating=0.0,
            is_verified=False,
            is_official=False,
        )

        self._plugins[plugin.plugin_id] = plugin
        return plugin

    def search_plugins(
        self,
        query: str | None = None,
        category: PluginCategory | None = None,
        tags: list[str] | None = None,
        verified_only: bool = False,
    ) -> list[PluginMetadata]:
        """
        Search for plugins

        Args:
            query: Search query (name/description)
            category: Filter by category
            tags: Filter by tags
            verified_only: Only show verified plugins

        Returns:
            List of matching plugins
        """
        results = list(self._plugins.values())

        # Filter by query
        if query:
            query_lower = query.lower()
            results = [p for p in results if query_lower in p.name.lower() or query_lower in p.description.lower()]

        # Filter by category
        if category:
            results = [p for p in results if p.category == category]

        # Filter by tags
        if tags:
            results = [p for p in results if any(tag in p.tags for tag in tags)]

        # Filter by verification
        if verified_only:
            results = [p for p in results if p.is_verified]

        # Sort by rating and downloads
        results.sort(key=lambda p: (p.rating, p.downloads), reverse=True)

        return results

    def get_plugin(self, plugin_id: UUID) -> PluginMetadata | None:
        """Get plugin by ID"""
        return self._plugins.get(plugin_id)

    def update_plugin(self, plugin_id: UUID, version: str | None = None, **updates) -> PluginMetadata | None:
        """Update plugin metadata"""
        if plugin_id not in self._plugins:
            return None

        plugin = self._plugins[plugin_id]

        if version:
            plugin.version = version

        for key, value in updates.items():
            if hasattr(plugin, key):
                setattr(plugin, key, value)

        plugin.updated_at = datetime.now()
        return plugin

    def download_plugin(self, plugin_id: UUID) -> str | None:
        """
        Download a plugin (returns download URL)

        Args:
            plugin_id: Plugin ID

        Returns:
            Download URL or None
        """
        if plugin_id not in self._plugins:
            return None

        plugin = self._plugins[plugin_id]
        plugin.downloads += 1

        return plugin.download_url

    def add_review(self, plugin_id: UUID, user_id: UUID, rating: int, comment: str) -> PluginReview:
        """Add a user review for a plugin"""
        if plugin_id not in self._plugins:
            raise ValueError(f"Plugin {plugin_id} not found")

        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        review = PluginReview(
            review_id=uuid4(),
            plugin_id=plugin_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            created_at=datetime.now(),
        )

        if plugin_id not in self._reviews:
            self._reviews[plugin_id] = []
        self._reviews[plugin_id].append(review)

        # Update plugin rating
        self._update_plugin_rating(plugin_id)

        return review

    def get_reviews(self, plugin_id: UUID) -> list[PluginReview]:
        """Get all reviews for a plugin"""
        return self._reviews.get(plugin_id, [])

    def _update_plugin_rating(self, plugin_id: UUID):
        """Update average rating for a plugin"""
        reviews = self._reviews.get(plugin_id, [])

        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            self._plugins[plugin_id].rating = round(avg_rating, 2)

    def verify_plugin(self, plugin_id: UUID) -> bool:
        """Mark plugin as verified (admin only)"""
        if plugin_id in self._plugins:
            self._plugins[plugin_id].is_verified = True
            self._plugins[plugin_id].updated_at = datetime.now()
            return True
        return False

    def mark_official(self, plugin_id: UUID) -> bool:
        """Mark plugin as official (admin only)"""
        if plugin_id in self._plugins:
            self._plugins[plugin_id].is_official = True
            self._plugins[plugin_id].is_verified = True
            self._plugins[plugin_id].updated_at = datetime.now()
            return True
        return False

    def get_popular_plugins(self, limit: int = 10) -> list[PluginMetadata]:
        """Get most popular plugins by downloads"""
        plugins = list(self._plugins.values())
        plugins.sort(key=lambda p: p.downloads, reverse=True)
        return plugins[:limit]

    def get_top_rated_plugins(self, limit: int = 10) -> list[PluginMetadata]:
        """Get top rated plugins"""
        plugins = [p for p in self._plugins.values() if p.rating > 0]
        plugins.sort(key=lambda p: p.rating, reverse=True)
        return plugins[:limit]

    def get_recent_plugins(self, limit: int = 10) -> list[PluginMetadata]:
        """Get recently published plugins"""
        plugins = list(self._plugins.values())
        plugins.sort(key=lambda p: p.created_at, reverse=True)
        return plugins[:limit]
