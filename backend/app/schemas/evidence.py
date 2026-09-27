"""Evidence Schemas"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.evidence import EvidenceType


class EvidenceBase(BaseModel):
    description: Optional[str] = None
    evidence_type: EvidenceType = EvidenceType.OTHER


class EvidenceCreate(EvidenceBase):
    incident_id: int


class EvidenceUpdate(BaseModel):
    description: Optional[str] = None
    evidence_type: Optional[EvidenceType] = None


class EvidenceResponse(EvidenceBase):
    id: int
    evidence_id: str
    incident_id: int
    filename: str
    filepath: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class EvidenceListResponse(BaseModel):
    total: int
    items: List[EvidenceResponse]
