"""Risk Assessment Model"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Enum, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class RiskClassification(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_classification = Column(Enum(RiskClassification), nullable=False)
    factors = Column(String(500), nullable=True)
    recommended_action = Column(String(500), nullable=True)
    assessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    incident = relationship("Incident", back_populates="risk_assessments")
    
    def to_dict(self):
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "incident_id": self.incident_id,
            "risk_score": self.risk_score,
            "risk_classification": self.risk_classification.value if self.risk_classification else None,
            "factors": self.factors,
            "recommended_action": self.recommended_action,
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None
        }
