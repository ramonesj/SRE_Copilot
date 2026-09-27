"""Audit API Endpoints - Full Database Integration"""
import io
import csv
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.core.database import get_db
from app.models.audit import AuditLog, AuditAction
from app.models.incident import Incident

router = APIRouter()


@router.get("/export")
async def export_audit_logs(
    incident_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Export audit logs as CSV"""
    query = select(AuditLog).order_by(desc(AuditLog.timestamp))
    result = await db.execute(query)
    logs = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp", "Action", "Actor", "Incident ID", "Target", "Details"])
    
    for log in logs:
        writer.writerow([
            log.log_id,
            log.timestamp.isoformat() if log.timestamp else "",
            log.action.value if log.action else "",
            log.user,
            log.incident_id or "",
            log.target or "",
            log.details or ""
        ])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-logs.csv"}
    )


@router.get("")
@router.get("/")
async def get_audit_logs(
    incident_id: Optional[str] = None,
    action: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs with optional filters and pagination"""
    skip = (page - 1) * page_size
    
    count_query = select(func.count(AuditLog.id))
    query = select(AuditLog).order_by(desc(AuditLog.timestamp))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.offset(skip).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    items = []
    for log in logs:
        # Resolve incident code if available
        inc_code = None
        if log.incident_id:
            inc_res = await db.execute(select(Incident.incident_id).where(Incident.id == log.incident_id))
            inc_code = inc_res.scalar_one_or_none()
            
        items.append({
            "id": log.log_id,
            "incident_id": inc_code or (f"INC-{log.incident_id}" if log.incident_id else None),
            "action": log.action.value.upper() if log.action else "SYSTEM",
            "actor": log.user,
            "details": {
                "target": log.target,
                "message": log.details,
                "ip": log.ip_address
            },
            "timestamp": log.timestamp.isoformat() if log.timestamp else ""
        })
        
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
    }
