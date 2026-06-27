"""
Plugin Marketplace API Routes
Central plugin management and distribution
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.plugins.registry import (
    get_plugin_registry,
    PluginMetadataRegistry,
    PluginVersion,
    PluginReview,
)
from app.auth.middleware import verify_token_required
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/plugin-marketplace", tags=["plugin-marketplace"])


# Plugin Registry
@router.get("/plugins")
async def list_plugins(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """List all plugins"""
    registry = get_plugin_registry()
    plugins = list(registry.plugins.values())

    total = len(plugins)
    plugins_page = plugins[skip : skip + limit]

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "author": p.author,
                "category": p.category,
                "rating": p.rating,
                "downloads": p.downloads,
                "is_verified": p.is_verified,
                "is_featured": p.is_featured,
            }
            for p in plugins_page
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }


@router.get("/plugins/featured")
async def get_featured_plugins(limit: int = Query(10, ge=1, le=50)):
    """Get featured plugins"""
    registry = get_plugin_registry()
    featured = registry.get_featured_plugins(limit)

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "icon_url": p.icon_url,
                "rating": p.rating,
                "downloads": p.downloads,
            }
            for p in featured
        ],
    }


@router.get("/plugins/trending")
async def get_trending_plugins(limit: int = Query(10, ge=1, le=50)):
    """Get trending plugins"""
    registry = get_plugin_registry()
    trending = registry.get_trending_plugins(limit)

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "rating": p.rating,
                "downloads": p.downloads,
            }
            for p in trending
        ],
    }


@router.get("/plugins/search")
async def search_plugins(
    q: str = Query("", min_length=0),
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
):
    """Search plugins"""
    registry = get_plugin_registry()
    results = registry.search_plugins(
        query=q,
        category=category,
        limit=limit,
    )

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "author": p.author,
                "rating": p.rating,
                "downloads": p.downloads,
            }
            for p in results
        ],
        "count": len(results),
    }


@router.get("/plugins/{plugin_id}")
async def get_plugin_details(plugin_id: str):
    """Get plugin details"""
    registry = get_plugin_registry()
    plugin = registry.get_plugin(plugin_id)

    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")

    versions = registry.versions.get(plugin_id, [])

    return {
        "success": True,
        "data": {
            "id": plugin.id,
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "author": plugin.author,
            "license": plugin.license,
            "repository": plugin.repository,
            "homepage": plugin.homepage,
            "category": plugin.category,
            "rating": plugin.rating,
            "reviews_count": plugin.reviews_count,
            "downloads": plugin.downloads,
            "is_verified": plugin.is_verified,
            "is_featured": plugin.is_featured,
            "is_official": plugin.is_official,
            "versions": [
                {
                    "version": v.version,
                    "released_at": v.released_at,
                    "is_stable": v.is_stable,
                    "is_recommended": v.is_recommended,
                }
                for v in versions[:5]  # Last 5 versions
            ],
        },
    }


@router.get("/plugins/{plugin_id}/versions")
async def get_plugin_versions(plugin_id: str):
    """Get all versions of a plugin"""
    registry = get_plugin_registry()

    if plugin_id not in registry.plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    versions = registry.versions.get(plugin_id, [])

    return {
        "success": True,
        "data": [
            {
                "version": v.version,
                "released_at": v.released_at,
                "is_stable": v.is_stable,
                "is_recommended": v.is_recommended,
                "release_notes": v.release_notes,
                "compatibility": v.compatibility,
            }
            for v in versions
        ],
        "count": len(versions),
    }


@router.get("/plugins/{plugin_id}/reviews")
async def get_plugin_reviews(
    plugin_id: str,
    limit: int = Query(10, ge=1, le=50),
):
    """Get plugin reviews"""
    registry = get_plugin_registry()

    if plugin_id not in registry.plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    reviews = registry.get_reviews(plugin_id, limit)

    return {
        "success": True,
        "data": [
            {
                "id": r.id,
                "user_name": r.user_name,
                "rating": r.rating,
                "title": r.title,
                "content": r.content,
                "helpful_count": r.helpful_count,
                "created_at": r.created_at,
            }
            for r in reviews
        ],
        "count": len(reviews),
    }


@router.post("/plugins/{plugin_id}/reviews")
async def add_plugin_review(
    plugin_id: str,
    review_data: dict,
    user: dict = Depends(verify_token_required),
):
    """Add a review to plugin"""
    registry = get_plugin_registry()

    if plugin_id not in registry.plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    review = PluginReview(
        id="",  # Will be set by registry
        plugin_id=plugin_id,
        user_id=user.get("user_id"),
        user_name=user.get("email"),
        rating=review_data.get("rating"),
        title=review_data.get("title"),
        content=review_data.get("content"),
    )

    registry.add_review(plugin_id, review)

    return {
        "success": True,
        "message": "Review added successfully",
        "data": {
            "id": review.id,
            "rating": review.rating,
            "created_at": review.created_at,
        },
    }


@router.post("/plugins/{plugin_id}/download")
async def download_plugin(
    plugin_id: str,
    version: str = Query("latest"),
):
    """Download plugin"""
    registry = get_plugin_registry()

    if plugin_id not in registry.plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")

    plugin_version = registry.get_version(plugin_id, version)

    if not plugin_version:
        raise HTTPException(status_code=404, detail="Version not found")

    # Increment download count
    registry.increment_download(plugin_id)

    return {
        "success": True,
        "data": {
            "download_url": plugin_version.download_url,
            "version": plugin_version.version,
            "size": plugin_version.size,
            "checksum": plugin_version.checksum,
        },
    }


@router.post("/plugins/publish")
async def publish_plugin(
    plugin_data: dict,
    user: dict = Depends(verify_token_required),
):
    """Publish a new plugin"""
    registry = get_plugin_registry()

    plugin_id = plugin_data.get("name").lower().replace(" ", "_")

    # Check if plugin already exists
    if plugin_id in registry.plugins:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Plugin already exists",
        )

    # Create metadata
    metadata = PluginMetadataRegistry(
        id=plugin_id,
        name=plugin_data.get("name"),
        version=plugin_data.get("version", "1.0.0"),
        description=plugin_data.get("description"),
        author=plugin_data.get("author"),
        license=plugin_data.get("license", "MIT"),
        repository=plugin_data.get("repository"),
        homepage=plugin_data.get("homepage"),
        keywords=plugin_data.get("keywords", []),
        category=plugin_data.get("category", "tool"),
        tags=plugin_data.get("tags", []),
        icon_url=plugin_data.get("icon_url"),
        documentation_url=plugin_data.get("documentation_url"),
    )

    # Register plugin
    registry.register_plugin(plugin_id, metadata)

    logger.info(f"Plugin published by {user.get('email')}: {plugin_id}")

    return {
        "success": True,
        "message": "Plugin published successfully",
        "data": {
            "id": plugin_id,
            "name": metadata.name,
            "url": f"/plugin-marketplace/plugins/{plugin_id}",
        },
    }


@router.get("/stats")
async def get_marketplace_stats():
    """Get marketplace statistics"""
    registry = get_plugin_registry()

    total_plugins = len(registry.plugins)
    total_versions = sum(len(v) for v in registry.versions.values())
    total_downloads = sum(p.downloads for p in registry.plugins.values())
    avg_rating = (
        sum(p.rating for p in registry.plugins.values()) / total_plugins
        if total_plugins > 0
        else 0
    )

    return {
        "success": True,
        "data": {
            "total_plugins": total_plugins,
            "total_versions": total_versions,
            "total_downloads": total_downloads,
            "average_rating": round(avg_rating, 1),
            "featured_count": len(registry.featured_plugins),
        },
    }
