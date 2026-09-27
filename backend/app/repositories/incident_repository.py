"""Incident Repository"""
import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import Incident, IncidentSeverity, IncidentStatus


class IncidentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_incident_id(self) -> str:
        return f"INC-{uuid.uuid4().hex[:12].upper()}"

    async def create(self, incident: Incident) -> Incident:
        incident.incident_id = self._generate_incident_id()
        self.db.add(incident)
        await self.db.flush()
        await self.db.refresh(incident)
        return incident

    async def get_by_id(self, incident_id: int) -> Optional[Incident]:
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()

    async def get_by_incident_id(self, incident_id: str) -> Optional[Incident]:
        result = await self.db.execute(
            select(Incident).where(Incident.incident_id == incident_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        severity: Optional[IncidentSeverity] = None,
        status: Optional[IncidentStatus] = None
    ) -> tuple[List[Incident], int]:
        query = select(Incident)
        
        if severity:
            query = query.where(Incident.severity == severity)
        if status:
            query = query.where(Incident.status == status)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        query = query.offset(skip).limit(limit).order_by(Incident.created_at.desc())
        result = await self.db.execute(query)
        incidents = result.scalars().all()
        
        return incidents, total or 0

    async def update(self, incident: Incident) -> Incident:
        await self.db.flush()
        await self.db.refresh(incident)
        return incident

    async def delete(self, incident_id: int) -> bool:
        incident = await self.get_by_id(incident_id)
        if incident:
            await self.db.delete(incident)
            await self.db.flush()
            return True
        return False
