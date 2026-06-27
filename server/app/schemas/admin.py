"""
Admin schemas
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserStatsResponse(BaseModel):
    """User statistics"""
    total_users: int
    active_users: int
    admin_users: int
    new_users_today: int


class DocumentStatsResponse(BaseModel):
    """Document statistics"""
    total_documents: int
    total_vectors: int
    total_segments: int
    avg_vectors_per_doc: float


class SystemStatsResponse(BaseModel):
    """System statistics"""
    uptime_hours: float
    total_requests: int
    avg_response_time_ms: float
    error_rate_percent: float


class DashboardStatsResponse(BaseModel):
    """Complete dashboard statistics"""
    users: UserStatsResponse
    documents: DocumentStatsResponse
    system: SystemStatsResponse
    timestamp: datetime


class UserListItemResponse(BaseModel):
    """User list item"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response"""
    total: int
    page: int
    limit: int
    users: List[UserListItemResponse]


class ChatSessionResponse(BaseModel):
    """Chat session response"""
    session_id: str
    user_id: str
    username: str
    created_at: datetime
    message_count: int
    last_message_at: Optional[datetime]


class ChatSessionListResponse(BaseModel):
    """Chat session list"""
    total: int
    sessions: List[ChatSessionResponse]


class DocumentLogResponse(BaseModel):
    """Document ingestion log"""
    id: str
    user_id: str
    filename: str
    status: str  # success, failed, processing
    chunks_count: int
    vectors_count: int
    created_at: datetime
    completed_at: Optional[datetime]


class DocumentLogListResponse(BaseModel):
    """Document logs list"""
    total: int
    logs: List[DocumentLogResponse]
