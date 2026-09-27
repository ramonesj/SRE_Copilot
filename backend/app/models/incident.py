"""
Incident Model - Core entity for incident management
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Text, DateTime, Enum, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


class IncidentSeverity(str, PyEnum):
    """Incident severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, PyEnum):
    """Incident status lifecycle"""
    CREATED = "created"
    EVIDENCE_COLLECTED = "evidence_collected"
    DIAGNOSIS_COMPLETE = "diagnosis_complete"
    RISK_ASSESSED = "risk_assessed"
    APPROVED = "approved"
    EXECUTING = "executing"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    RECOVERY_FAILED = "recovery_failed"


class Incident(Base):
    """Incident model for tracking incidents throughout their lifecycle"""
    
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Enum(IncidentSeverity), nullable=False, default=IncidentSeverity.MEDIUM)
    status = Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.CREATED)
    service = Column(String(100), nullable=True)
    instance_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    evidences = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="incident", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="incident", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="incident", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Incident(incident_id={self.incident_id}, title={self.title}, status={self.status})>"
    
    def to_dict(self):
        """Convert incident to dictionary"""
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value if self.severity else None,
            "status": self.status.value if self.status else None,
            "service": self.service,
            "instance_id": self.instance_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }
