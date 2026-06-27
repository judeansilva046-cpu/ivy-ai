"""
Admin routes for dashboard and management
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.user import User
from app.schemas.admin import (
    DashboardStatsResponse,
    UserStatsResponse,
    DocumentStatsResponse,
    SystemStatsResponse,
    UserListResponse,
    UserListItemResponse,
)
from app.database.db import get_db
from app.utils.logger import setup_logger
from api.routes.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])
logger = setup_logger(__name__)


def check_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    admin: User = Depends(check_admin),
    db: Session = Depends(get_db),
):
    """
    Get dashboard statistics
    """
    try:
        # User stats
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        admin_users = db.query(func.count(User.id)).filter(User.is_admin == True).scalar()

        # New users today
        today = datetime.utcnow().date()
        new_users_today = (
            db.query(func.count(User.id))
            .filter(func.date(User.created_at) == today)
            .scalar()
        )

        user_stats = UserStatsResponse(
            total_users=total_users or 0,
            active_users=active_users or 0,
            admin_users=admin_users or 0,
            new_users_today=new_users_today or 0,
        )

        # Document stats (from vector store)
        from app.database.qdrant import get_qdrant_store

        qdrant_store = get_qdrant_store()
        collection_info = qdrant_store.get_collection_info()

        doc_stats = DocumentStatsResponse(
            total_documents=collection_info.get("vectors_count", 0),
            total_vectors=collection_info.get("vectors_count", 0),
            total_segments=collection_info.get("segments_count", 0),
            avg_vectors_per_doc=(
                collection_info.get("vectors_count", 1) / max(1, collection_info.get("vectors_count", 1))
            ),
        )

        # System stats (placeholder)
        system_stats = SystemStatsResponse(
            uptime_hours=0.0,
            total_requests=0,
            avg_response_time_ms=0.0,
            error_rate_percent=0.0,
        )

        logger.info(f"Dashboard stats retrieved by {admin.username}")

        return DashboardStatsResponse(
            users=user_stats,
            documents=doc_stats,
            system=system_stats,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard stats",
        )


@router.get("/users", response_model=UserListResponse)
async def list_users(
    admin: User = Depends(check_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query("", min_length=0),
    is_active: bool = Query(None),
):
    """
    List all users with filters
    """
    try:
        query = db.query(User)

        # Search filter
        if search:
            query = query.filter(
                (User.email.ilike(f"%{search}%")) |
                (User.username.ilike(f"%{search}%")) |
                (User.full_name.ilike(f"%{search}%"))
            )

        # Active filter
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()
        users = query.offset(skip).limit(limit).all()

        logger.info(f"Users list retrieved by {admin.username}")

        return UserListResponse(
            total=total,
            page=skip // limit,
            limit=limit,
            users=[UserListItemResponse.from_orm(u) for u in users],
        )

    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users",
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(check_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a user (soft delete - deactivate)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself",
            )

        user.is_active = False
        db.commit()

        logger.info(f"User {user.username} deactivated by {admin.username}")

        return {"message": "User deactivated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )


@router.post("/users/{user_id}/admin")
async def toggle_admin(
    user_id: str,
    admin: User = Depends(check_admin),
    db: Session = Depends(get_db),
):
    """
    Toggle admin status for a user
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own admin status",
            )

        user.is_admin = not user.is_admin
        db.commit()

        logger.info(f"Admin status for {user.username} changed by {admin.username}")

        return {"user_id": user.id, "is_admin": user.is_admin}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle admin",
        )


@router.get("/health")
async def admin_health(
    admin: User = Depends(check_admin),
):
    """
    Admin-specific health check
    """
    try:
        from app.database.qdrant import get_qdrant_store

        qdrant = get_qdrant_store()
        qdrant_info = qdrant.get_collection_info()

        return {
            "status": "healthy",
            "admin_user": admin.username,
            "vector_store": "ok",
            "collection_info": qdrant_info,
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Admin health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed",
        )
