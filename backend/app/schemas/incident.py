"""Incident Schemas"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.incident import IncidentSeverity, IncidentStatus


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    service: Optional[str] = None
    instance_id: Optional[str] = None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    service: Optional[str] = None
    instance_id: Optional[str] = None


class IncidentResponse(IncidentBase):
    id: int
    incident_id: str
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    total: int
    items: List[IncidentResponse]
