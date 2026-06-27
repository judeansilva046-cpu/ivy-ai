"""
Plugin Registry System
Central registry for plugin management and distribution
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class PluginMetadataRegistry:
    """Plugin metadata for registry"""
    id: str
    name: str
    version: str
    description: str
    author: str
    license: str
    repository: str
    homepage: str
    keywords: List[str]
    category: str
    tags: List[str]
    icon_url: Optional[str]
    documentation_url: Optional[str]
    downloads: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    created_at: str = None
    updated_at: str = None
    is_verified: bool = False
    is_featured: bool = False
    is_official: bool = False


@dataclass
class PluginVersion:
    """Plugin version information"""
    version: str
    released_at: str
    download_url: str
    size: int
    checksum: str
    release_notes: str
    compatibility: List[str]  # ['1.0.0', '1.1.0', ...]
    dependencies: Dict[str, str]  # {'ivy-ai': '>=1.0.0'}
    is_stable: bool = True
    is_recommended: bool = False


@dataclass
class PluginReview:
    """Plugin review"""
    id: str
    plugin_id: str
    user_id: str
    user_name: str
    rating: int  # 1-5
    title: str
    content: str
    helpful_count: int = 0
    created_at: str = None


class PluginRegistry:
    """Central plugin registry"""

    def __init__(self):
        self.plugins: Dict[str, PluginMetadataRegistry] = {}
        self.versions: Dict[str, List[PluginVersion]] = {}
        self.reviews: Dict[str, List[PluginReview]] = {}
        self.featured_plugins: List[str] = []

    def register_plugin(
        self,
        plugin_id: str,
        metadata: PluginMetadataRegistry
    ) -> bool:
        """Register a new plugin"""
        if plugin_id in self.plugins:
            logger.warning(f"Plugin already registered: {plugin_id}")
            return False

        metadata.id = plugin_id
        metadata.created_at = datetime.utcnow().isoformat()
        metadata.updated_at = datetime.utcnow().isoformat()

        self.plugins[plugin_id] = metadata
        self.versions[plugin_id] = []

        logger.info(f"Plugin registered: {plugin_id}")
        return True

    def publish_version(
        self,
        plugin_id: str,
        version: PluginVersion
    ) -> bool:
        """Publish a new plugin version"""
        if plugin_id not in self.plugins:
            logger.error(f"Plugin not found: {plugin_id}")
            return False

        if plugin_id not in self.versions:
            self.versions[plugin_id] = []

        # Check for duplicate version
        for v in self.versions[plugin_id]:
            if v.version == version.version:
                logger.warning(f"Version already exists: {version.version}")
                return False

        version.released_at = datetime.utcnow().isoformat()

        # Add to versions list (sorted by release date)
        self.versions[plugin_id].append(version)
        self.versions[plugin_id].sort(
            key=lambda x: datetime.fromisoformat(x.released_at),
            reverse=True
        )

        # Update plugin metadata
        self.plugins[plugin_id].version = version.version
        self.plugins[plugin_id].updated_at = datetime.utcnow().isoformat()

        logger.info(f"Version published: {plugin_id}@{version.version}")
        return True

    def get_plugin(self, plugin_id: str) -> Optional[PluginMetadataRegistry]:
        """Get plugin metadata"""
        return self.plugins.get(plugin_id)

    def get_version(
        self,
        plugin_id: str,
        version: str = "latest"
    ) -> Optional[PluginVersion]:
        """Get specific plugin version"""
        if plugin_id not in self.versions:
            return None

        versions = self.versions[plugin_id]
        if not versions:
            return None

        if version == "latest":
            return versions[0]

        for v in versions:
            if v.version == version:
                return v

        return None

    def search_plugins(
        self,
        query: str = "",
        category: str = "",
        tags: List[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[PluginMetadataRegistry]:
        """Search plugins"""
        results = []

        for plugin in self.plugins.values():
            # Query match
            if query and query.lower() not in plugin.name.lower():
                if query.lower() not in plugin.description.lower():
                    continue

            # Category filter
            if category and plugin.category != category:
                continue

            # Tags filter
            if tags:
                if not any(tag in plugin.tags for tag in tags):
                    continue

            results.append(plugin)

        # Sort by rating and downloads
        results.sort(
            key=lambda x: (x.rating, x.downloads),
            reverse=True
        )

        return results[offset:offset + limit]

    def add_review(
        self,
        plugin_id: str,
        review: PluginReview
    ) -> bool:
        """Add a review to plugin"""
        if plugin_id not in self.plugins:
            return False

        if plugin_id not in self.reviews:
            self.reviews[plugin_id] = []

        review.id = f"review_{len(self.reviews[plugin_id]) + 1}"
        review.plugin_id = plugin_id
        review.created_at = datetime.utcnow().isoformat()

        self.reviews[plugin_id].append(review)

        # Update plugin rating
        self._update_plugin_rating(plugin_id)

        logger.info(f"Review added to {plugin_id}: {review.id}")
        return True

    def get_reviews(
        self,
        plugin_id: str,
        limit: int = 10
    ) -> List[PluginReview]:
        """Get plugin reviews"""
        if plugin_id not in self.reviews:
            return []

        reviews = self.reviews[plugin_id]
        # Sort by helpful count
        reviews.sort(key=lambda x: x.helpful_count, reverse=True)
        return reviews[:limit]

    def _update_plugin_rating(self, plugin_id: str):
        """Update plugin rating based on reviews"""
        if plugin_id not in self.reviews or not self.reviews[plugin_id]:
            self.plugins[plugin_id].rating = 0.0
            self.plugins[plugin_id].reviews_count = 0
            return

        reviews = self.reviews[plugin_id]
        avg_rating = sum(r.rating for r in reviews) / len(reviews)

        self.plugins[plugin_id].rating = round(avg_rating, 1)
        self.plugins[plugin_id].reviews_count = len(reviews)

    def feature_plugin(self, plugin_id: str) -> bool:
        """Feature a plugin"""
        if plugin_id not in self.plugins:
            return False

        if plugin_id not in self.featured_plugins:
            self.featured_plugins.append(plugin_id)
            self.plugins[plugin_id].is_featured = True

        logger.info(f"Plugin featured: {plugin_id}")
        return True

    def unfeature_plugin(self, plugin_id: str) -> bool:
        """Unfeature a plugin"""
        if plugin_id in self.featured_plugins:
            self.featured_plugins.remove(plugin_id)
            self.plugins[plugin_id].is_featured = False

        return True

    def verify_plugin(self, plugin_id: str) -> bool:
        """Verify a plugin as official"""
        if plugin_id not in self.plugins:
            return False

        self.plugins[plugin_id].is_verified = True
        self.plugins[plugin_id].is_official = True

        logger.info(f"Plugin verified: {plugin_id}")
        return True

    def increment_download(self, plugin_id: str) -> bool:
        """Increment plugin download count"""
        if plugin_id not in self.plugins:
            return False

        self.plugins[plugin_id].downloads += 1
        return True

    def get_featured_plugins(self, limit: int = 10) -> List[PluginMetadataRegistry]:
        """Get featured plugins"""
        featured = [
            self.plugins[pid] for pid in self.featured_plugins
            if pid in self.plugins
        ]
        return featured[:limit]

    def get_trending_plugins(self, limit: int = 10) -> List[PluginMetadataRegistry]:
        """Get trending plugins"""
        plugins = list(self.plugins.values())
        # Sort by recent downloads and rating
        plugins.sort(
            key=lambda x: (x.downloads, x.rating),
            reverse=True
        )
        return plugins[:limit]

    def export_to_json(self) -> str:
        """Export registry to JSON"""
        data = {
            "plugins": {
                pid: asdict(plugin)
                for pid, plugin in self.plugins.items()
            },
            "versions": {
                pid: [asdict(v) for v in versions]
                for pid, versions in self.versions.items()
            }
        }
        return json.dumps(data, indent=2)

    def import_from_json(self, json_data: str) -> bool:
        """Import registry from JSON"""
        try:
            data = json.loads(json_data)

            # Import plugins
            for pid, plugin_data in data.get("plugins", {}).items():
                metadata = PluginMetadataRegistry(**plugin_data)
                self.plugins[pid] = metadata

            # Import versions
            for pid, versions_data in data.get("versions", {}).items():
                self.versions[pid] = [
                    PluginVersion(**v) for v in versions_data
                ]

            logger.info(f"Registry imported: {len(self.plugins)} plugins")
            return True

        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False


# Singleton instance
_registry = None


def get_plugin_registry() -> PluginRegistry:
    """Get plugin registry singleton"""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry
