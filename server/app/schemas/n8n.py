"""
N8N integration schemas
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict, List
from datetime import datetime


class N8NWebhookPayload(BaseModel):
    """N8N webhook payload"""
    event_type: str  # document_ingested, chat_completed, etc
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    source: str = "jarvis_ai"

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "document_ingested",
                "data": {
                    "document_id": "123",
                    "filename": "test.pdf",
                    "chunks_count": 10
                },
                "timestamp": "2026-06-27T10:00:00",
                "source": "jarvis_ai"
            }
        }


class WorkflowTriggerRequest(BaseModel):
    """Trigger N8N workflow"""
    workflow_id: str
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "workflow_123",
                "data": {
                    "document_id": "doc_123",
                    "action": "index"
                }
            }
        }


class WorkflowTriggerResponse(BaseModel):
    """Workflow trigger response"""
    success: bool
    workflow_id: str
    execution_id: str
    status: str
    timestamp: datetime


class WorkflowListResponse(BaseModel):
    """N8N workflows list"""
    total: int
    workflows: List[Dict[str, Any]]


class EventLogResponse(BaseModel):
    """Event log entry"""
    id: str
    event_type: str
    status: str  # pending, processing, completed, failed
    source: str
    data: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class EventLogListResponse(BaseModel):
    """Event logs list"""
    total: int
    events: List[EventLogResponse]


class AutomationResponse(BaseModel):
    """Automation configuration"""
    id: str
    name: str
    description: str
    enabled: bool
    event_type: str
    workflow_id: str
    conditions: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AutomationCreateRequest(BaseModel):
    """Create automation"""
    name: str
    description: str
    event_type: str
    workflow_id: str
    conditions: Dict[str, Any] = {}


class AutomationUpdateRequest(BaseModel):
    """Update automation"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
