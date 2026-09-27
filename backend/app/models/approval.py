"""Approval Model - HITL System"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Enum, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ApprovalStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(String(100), nullable=False)
    approved_by = Column(String(100), nullable=True)
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at = Column(DateTime, nullable=True)
    
    incident = relationship("Incident", back_populates="approvals")
    
    def to_dict(self):
        return {
            "id": self.id,
            "approval_id": self.approval_id,
            "incident_id": self.incident_id,
            "requested_by": self.requested_by,
            "approved_by": self.approved_by,
            "status": self.status.value if self.status else None,
            "rationale": self.rationale,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None
        }
