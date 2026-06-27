"""
Tests for Plugin Marketplace
Plugin registry, publishing, and search functionality
"""
import pytest
from app.plugins.registry import (
    get_plugin_registry,
    PluginMetadataRegistry,
    PluginVersion,
    PluginReview,
)


class TestPluginRegistry:
    """Test plugin registry"""

    def test_register_plugin(self):
        """Test registering a plugin"""
        registry = get_plugin_registry()
        metadata = PluginMetadataRegistry(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            license="MIT",
            repository="https://github.com/test/test-plugin",
            homepage="https://test-plugin.dev",
            keywords=["test"],
            category="tool",
            tags=["test"],
        )

        success = registry.register_plugin("test-plugin", metadata)
        assert success is True
        assert registry.get_plugin("test-plugin") is not None

    def test_publish_version(self):
        """Test publishing plugin version"""
        registry = get_plugin_registry()
        metadata = PluginMetadataRegistry(
            id="versioned-plugin",
            name="Versioned Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("versioned-plugin", metadata)

        version = PluginVersion(
            version="1.0.0",
            released_at="",
            download_url="https://example.com/v1.0.0",
            size=1024,
            checksum="abc123",
            release_notes="Initial release",
            compatibility=["1.0.0"],
            dependencies={},
        )

        success = registry.publish_version("versioned-plugin", version)
        assert success is True

    def test_search_plugins(self):
        """Test searching plugins"""
        registry = get_plugin_registry()

        # Register test plugins
        for i in range(3):
            metadata = PluginMetadataRegistry(
                id=f"plugin-{i}",
                name=f"Plugin {i}",
                version="1.0.0",
                description="Test plugin",
                author="Test",
                license="MIT",
                repository="",
                homepage="",
                keywords=["test"],
                category="tool",
                tags=["test"],
            )
            registry.register_plugin(f"plugin-{i}", metadata)

        # Search
        results = registry.search_plugins(query="Plugin", limit=10)
        assert len(results) >= 3

    def test_get_plugin_details(self):
        """Test getting plugin details"""
        registry = get_plugin_registry()
        metadata = PluginMetadataRegistry(
            id="detail-plugin",
            name="Detail Plugin",
            version="1.0.0",
            description="Test",
            author="Author",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("detail-plugin", metadata)
        plugin = registry.get_plugin("detail-plugin")

        assert plugin.name == "Detail Plugin"
        assert plugin.author == "Author"
        assert plugin.version == "1.0.0"

    def test_add_review(self):
        """Test adding review to plugin"""
        registry = get_plugin_registry()
        metadata = PluginMetadataRegistry(
            id="review-plugin",
            name="Review Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("review-plugin", metadata)

        review = PluginReview(
            id="",
            plugin_id="review-plugin",
            user_id="user123",
            user_name="Test User",
            rating=5,
            title="Great plugin!",
            content="Works perfectly",
        )

        success = registry.add_review("review-plugin", review)
        assert success is True

        # Check rating updated
        plugin = registry.get_plugin("review-plugin")
        assert plugin.rating == 5.0
        assert plugin.reviews_count == 1

    def test_get_featured_plugins(self):
        """Test getting featured plugins"""
        registry = get_plugin_registry()

        metadata = PluginMetadataRegistry(
            id="featured-plugin",
            name="Featured Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("featured-plugin", metadata)
        registry.feature_plugin("featured-plugin")

        featured = registry.get_featured_plugins()
        assert len(featured) > 0
        assert any(p.id == "featured-plugin" for p in featured)

    def test_get_trending_plugins(self):
        """Test getting trending plugins"""
        registry = get_plugin_registry()

        metadata = PluginMetadataRegistry(
            id="trending-plugin",
            name="Trending Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("trending-plugin", metadata)

        # Increment downloads
        for _ in range(10):
            registry.increment_download("trending-plugin")

        trending = registry.get_trending_plugins()
        assert len(trending) > 0

    def test_verify_plugin(self):
        """Test verifying plugin as official"""
        registry = get_plugin_registry()

        metadata = PluginMetadataRegistry(
            id="official-plugin",
            name="Official Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("official-plugin", metadata)
        registry.verify_plugin("official-plugin")

        plugin = registry.get_plugin("official-plugin")
        assert plugin.is_verified is True
        assert plugin.is_official is True

    def test_plugin_version_compatibility(self):
        """Test plugin version compatibility"""
        registry = get_plugin_registry()

        metadata = PluginMetadataRegistry(
            id="compat-plugin",
            name="Compat Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("compat-plugin", metadata)

        version = PluginVersion(
            version="1.0.0",
            released_at="",
            download_url="https://example.com/v1.0.0",
            size=1024,
            checksum="abc123",
            release_notes="Test",
            compatibility=["1.0.0", "1.1.0"],
            dependencies={"ivy-ai": ">=1.0.0"},
        )

        registry.publish_version("compat-plugin", version)

        retrieved = registry.get_version("compat-plugin", "1.0.0")
        assert retrieved is not None
        assert "1.0.0" in retrieved.compatibility
        assert "ivy-ai" in retrieved.dependencies

    def test_plugin_export_import(self):
        """Test exporting and importing registry"""
        registry = get_plugin_registry()

        # Register plugin
        metadata = PluginMetadataRegistry(
            id="export-plugin",
            name="Export Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("export-plugin", metadata)

        # Export
        json_data = registry.export_to_json()
        assert json_data is not None
        assert "export-plugin" in json_data

        # Import into new registry
        new_registry = get_plugin_registry()
        success = new_registry.import_from_json(json_data)
        assert success is True

    def test_duplicate_plugin_registration(self):
        """Test duplicate plugin registration fails"""
        registry = get_plugin_registry()

        metadata = PluginMetadataRegistry(
            id="dup-plugin",
            name="Dup Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("dup-plugin", metadata)
        success = registry.register_plugin("dup-plugin", metadata)

        assert success is False

    def test_filter_by_category(self):
        """Test filtering plugins by category"""
        registry = get_plugin_registry()

        # Register plugins with different categories
        for cat in ["tool", "agent", "service"]:
            metadata = PluginMetadataRegistry(
                id=f"plugin-{cat}",
                name=f"Plugin {cat}",
                version="1.0.0",
                description="Test",
                author="Test",
                license="MIT",
                repository="",
                homepage="",
                keywords=[],
                category=cat,
                tags=[],
            )
            registry.register_plugin(f"plugin-{cat}", metadata)

        # Search by category
        results = registry.search_plugins(category="tool")
        assert all(p.category == "tool" for p in results)

    def test_plugin_rating_calculation(self):
        """Test plugin rating calculation"""
        registry = get_plugin_registry()

        metadata = PluginMetadataRegistry(
            id="rating-plugin",
            name="Rating Plugin",
            version="1.0.0",
            description="Test",
            author="Test",
            license="MIT",
            repository="",
            homepage="",
            keywords=[],
            category="tool",
            tags=[],
        )

        registry.register_plugin("rating-plugin", metadata)

        # Add reviews with different ratings
        for rating in [5, 4, 3, 5]:
            review = PluginReview(
                id="",
                plugin_id="rating-plugin",
                user_id=f"user-{rating}",
                user_name=f"User {rating}",
                rating=rating,
                title="Review",
                content="Test",
            )
            registry.add_review("rating-plugin", review)

        # Check average rating
        plugin = registry.get_plugin("rating-plugin")
        assert plugin.rating == 4.25  # (5 + 4 + 3 + 5) / 4
        assert plugin.reviews_count == 4
