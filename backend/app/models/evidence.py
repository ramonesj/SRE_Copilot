"""
Evidence Model - File attachments and evidence for incidents
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Text, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class EvidenceType(str, PyEnum):
    """Evidence file types"""
    LOG = "log"
    SCREENSHOT = "screenshot"
    METRIC = "metric"
    TRACE = "trace"
    DOCUMENT = "document"
    OTHER = "other"


class Evidence(Base):
    """Evidence model for incident attachments"""
    
    __tablename__ = "evidences"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    evidence_id = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    evidence_type = Column(Enum(EvidenceType), nullable=False, default=EvidenceType.OTHER)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    uploaded_by = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="evidences")
    
    def __repr__(self):
        return f"<Evidence(evidence_id={self.evidence_id}, filename={self.filename})>"
    
    def to_dict(self):
        """Convert evidence to dictionary"""
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "incident_id": self.incident_id,
            "filename": self.filename,
            "filepath": self.filepath,
            "evidence_type": self.evidence_type.value if self.evidence_type else None,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "description": self.description,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
