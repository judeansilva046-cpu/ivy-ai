"""
N8N integration routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas.n8n import (
    N8NWebhookPayload,
    WorkflowTriggerRequest,
    WorkflowTriggerResponse,
    EventLogResponse,
    EventLogListResponse,
)
from app.services.n8n import get_n8n_service
from app.models.n8n import N8NEventLog
from app.database.db import get_db
from app.utils.logger import setup_logger
from api.routes.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/n8n", tags=["n8n"])
logger = setup_logger(__name__)


@router.post("/webhook", status_code=202)
async def receive_webhook(
    payload: N8NWebhookPayload,
    db: Session = Depends(get_db),
):
    """
    Receive webhook from N8N
    """
    try:
        # Log event
        event_log = N8NEventLog(
            event_type=payload.event_type,
            status="pending",
            source=payload.source,
            data=payload.data,
        )
        db.add(event_log)
        db.commit()

        logger.info(
            f"Webhook received: {payload.event_type} (id={event_log.id})"
        )

        return {
            "success": True,
            "event_id": event_log.id,
            "message": "Webhook received",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed",
        )


@router.post("/trigger", response_model=WorkflowTriggerResponse)
async def trigger_workflow(
    request: WorkflowTriggerRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Trigger an N8N workflow
    """
    try:
        n8n_service = get_n8n_service()

        result = await n8n_service.trigger_workflow(
            workflow_id=request.workflow_id,
            data=request.data,
        )

        if result.get("success"):
            logger.info(
                f"Workflow triggered by {current_user.username}: {request.workflow_id}"
            )
            return WorkflowTriggerResponse(
                success=True,
                workflow_id=request.workflow_id,
                execution_id="n8n_" + str(datetime.utcnow().timestamp()),
                status="triggered",
                timestamp=datetime.utcnow(),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to trigger workflow"),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow trigger error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workflow trigger failed",
        )


@router.get("/workflows")
async def list_workflows(
    current_user: User = Depends(get_current_user),
):
    """
    List N8N workflows
    """
    try:
        n8n_service = get_n8n_service()
        workflows = await n8n_service.list_workflows()

        logger.info(f"Workflows listed by {current_user.username}")

        return workflows

    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list workflows",
        )


@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get workflow details
    """
    try:
        n8n_service = get_n8n_service()
        workflow = await n8n_service.get_workflow(workflow_id)

        logger.info(f"Workflow retrieved by {current_user.username}: {workflow_id}")

        return workflow

    except Exception as e:
        logger.error(f"Error getting workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow",
        )


@router.get("/events", response_model=EventLogListResponse)
async def get_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """
    Get N8N event logs
    """
    try:
        total = db.query(N8NEventLog).count()
        events = (
            db.query(N8NEventLog)
            .order_by(N8NEventLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        logger.info(f"Events retrieved by {current_user.username}")

        return EventLogListResponse(
            total=total,
            events=[EventLogResponse.from_orm(e) for e in events],
        )

    except Exception as e:
        logger.error(f"Error retrieving events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve events",
        )


@router.put("/events/{event_id}")
async def update_event(
    event_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update event status
    """
    try:
        event = db.query(N8NEventLog).filter(N8NEventLog.id == event_id).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        event.status = status
        if status in ["completed", "failed"]:
            event.completed_at = datetime.utcnow()

        db.commit()

        logger.info(f"Event updated by {current_user.username}: {event_id} -> {status}")

        return {"success": True, "event_id": event_id, "status": status}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event",
        )


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete event log
    """
    try:
        event = db.query(N8NEventLog).filter(N8NEventLog.id == event_id).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        db.delete(event)
        db.commit()

        logger.info(f"Event deleted by {current_user.username}: {event_id}")

        return {"success": True, "event_id": event_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event",
        )
