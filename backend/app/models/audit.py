"""Audit Log Model"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Enum, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditAction(str, PyEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    UPLOAD = "upload"
    RISK_ASSESS = "risk_assess"

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    user = Column(String(100), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    target = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    incident = relationship("Incident", back_populates="audit_logs")
    
    def to_dict(self):
        return {
            "id": self.id,
            "log_id": self.log_id,
            "incident_id": self.incident_id,
            "user": self.user,
            "action": self.action.value if self.action else None,
            "target": self.target,
            "details": self.details,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
