"""Metrics API Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.core.database import get_db
from app.models.incident import Incident, IncidentSeverity, IncidentStatus

from app.models.approval import Approval, ApprovalStatus

router = APIRouter()


@router.get("")
@router.get("/")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Get incident metrics for dashboard"""
    # Total incidents
    total_query = select(func.count(Incident.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # Active incidents (not resolved)
    active_query = select(func.count(Incident.id)).where(
        Incident.status != IncidentStatus.RESOLVED
    )
    active_result = await db.execute(active_query)
    active = active_result.scalar() or 0
    
    # Resolved incidents
    resolved_query = select(func.count(Incident.id)).where(
        Incident.status == IncidentStatus.RESOLVED
    )
    resolved_result = await db.execute(resolved_query)
    resolved = resolved_result.scalar() or 0

    # Pending approvals
    pending_query = select(func.count(Approval.id)).where(
        Approval.status == ApprovalStatus.PENDING
    )
    pending_result = await db.execute(pending_query)
    pending_approvals = pending_result.scalar() or 0
    
    # Incidents by severity
    severity_query = select(
        Incident.severity,
        func.count(Incident.id)
    ).group_by(Incident.severity)
    severity_result = await db.execute(severity_query)
    by_severity = {row[0].value: row[1] for row in severity_result}
    
    # Ensure all severities are present
    for sev in IncidentSeverity:
        if sev.value not in by_severity:
            by_severity[sev.value] = 0
    
    # Incidents by status
    status_query = select(
        Incident.status,
        func.count(Incident.id)
    ).group_by(Incident.status)
    status_result = await db.execute(status_query)
    by_status = {row[0].value: row[1] for row in status_result}
    
    # Ensure all statuses are present
    for st in IncidentStatus:
        if st.value not in by_status:
            by_status[st.value] = 0
    
    return {
        "total": total,
        "active": active,
        "resolved": resolved,
        "pending_approvals": pending_approvals,
        "by_severity": by_severity,
        "by_status": by_status
    }
