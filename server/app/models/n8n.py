"""
N8N models for database
"""
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class N8NEventLog(Base):
    """N8N event log"""
    __tablename__ = "n8n_event_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False)
    source = Column(String(100), default="jarvis_ai", nullable=False)
    data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<N8NEventLog(id={self.id}, event_type={self.event_type}, status={self.status})>"


class N8NAutomation(Base):
    """N8N automation configuration"""
    __tablename__ = "n8n_automations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    event_type = Column(String(100), nullable=False, index=True)
    workflow_id = Column(String(255), nullable=False)
    conditions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<N8NAutomation(id={self.id}, name={self.name}, workflow_id={self.workflow_id})>"
