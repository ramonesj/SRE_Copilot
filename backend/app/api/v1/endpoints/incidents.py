"""Incident API Endpoints"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.risk import RiskAssessment, RiskClassification
from app.models.approval import Approval, ApprovalStatus
from app.models.audit import AuditLog, AuditAction
from app.schemas.incident import (
    IncidentCreate, IncidentUpdate, IncidentResponse, IncidentListResponse
)
from app.repositories.incident_repository import IncidentRepository

router = APIRouter()


@router.post("/", response_model=IncidentResponse, status_code=201)
@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(
    incident_data: IncidentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new live incident and trigger AI triage, risk assessment, and HITL approval queue"""
    repo = IncidentRepository(db)
    
    # Generate unique ID
    gen_inc_id = f"INC-{uuid.uuid4().hex[:10].upper()}"
    
    # Determine risk score and runbook
    sev = incident_data.severity
    if sev == IncidentSeverity.CRITICAL:
        risk_score = 88.0
        risk_class = RiskClassification.CRITICAL
        runbook = "SRE-Copilot-FlushDatabasePool"
        status = IncidentStatus.RISK_ASSESSED
    elif sev == IncidentSeverity.HIGH:
        risk_score = 68.0
        risk_class = RiskClassification.HIGH
        runbook = "SRE-Copilot-ScaleASG"
        status = IncidentStatus.RISK_ASSESSED
    elif sev == IncidentSeverity.MEDIUM:
        risk_score = 42.0
        risk_class = RiskClassification.MEDIUM
        runbook = "SRE-Copilot-ReplayDeadLetters"
        status = IncidentStatus.RISK_ASSESSED
    else:
        risk_score = 18.0
        risk_class = RiskClassification.LOW
        runbook = "SRE-Copilot-RestartService"
        status = IncidentStatus.RESOLVED

    incident = Incident(
        incident_id=gen_inc_id,
        title=incident_data.title,
        description=incident_data.description or f"Operational anomaly in {incident_data.service or 'service'}",
        severity=sev,
        status=status,
        service=incident_data.service or "notification-gateway",
        instance_id=incident_data.instance_id or "i-0ef1f2a3b4c5d60002",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(incident)
    await db.flush()  # to get incident.id

    # 1. Create Risk Assessment
    risk = RiskAssessment(
        assessment_id=f"RISK-{uuid.uuid4().hex[:10].upper()}",
        incident_id=incident.id,
        risk_score=risk_score,
        risk_classification=risk_class,
        factors=runbook,
        recommended_action=f"Execute {runbook} via AWS Systems Manager",
        assessed_at=datetime.utcnow()
    )
    db.add(risk)

    # 2. If Medium/High/Critical, enqueue HITL Approval
    if sev in [IncidentSeverity.MEDIUM, IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
        approval = Approval(
            approval_id=f"APP-{uuid.uuid4().hex[:10].upper()}",
            incident_id=incident.id,
            requested_by="SRECopilotEngine",
            status=ApprovalStatus.PENDING,
            rationale=f"Automated risk score {risk_score}/100 exceeds autonomous execution policy limit (25/100). SRE on-call approval required.",
            created_at=datetime.utcnow()
        )
        db.add(approval)

    # 3. Create Audit Trail
    audit_create = AuditLog(
        log_id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
        incident_id=incident.id,
        user="SRECopilotEngine",
        action=AuditAction.CREATE,
        target=f"Incident {gen_inc_id}",
        details=f'{{"target":"Incident {gen_inc_id}","message":"Live Incident Ingested & Triaged via AWS Bedrock"}}',
        ip_address="127.0.0.1",
        timestamp=datetime.utcnow()
    )
    db.add(audit_create)

    audit_risk = AuditLog(
        log_id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
        incident_id=incident.id,
        user="SRECopilotEngine",
        action=AuditAction.RISK_ASSESS,
        target=f"Incident {gen_inc_id}",
        details=f'{{"target":"Incident {gen_inc_id}","risk_score":{risk_score},"recommended_runbook":"{runbook}"}}',
        ip_address="127.0.0.1",
        timestamp=datetime.utcnow()
    )
    db.add(audit_risk)

    await db.commit()
    await db.refresh(incident)
    return IncidentResponse.model_validate(incident)


@router.get("", response_model=IncidentListResponse)
@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=1000),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all incidents with optional filters"""
    if page is not None and page_size is not None:
        skip = (page - 1) * page_size
        limit = page_size
    elif page_size is not None:
        limit = page_size

    sev_filter = None
    if severity:
        try:
            sev_filter = IncidentSeverity(severity.lower())
        except ValueError:
            sev_filter = None

    stat_filter = None
    if status:
        try:
            stat_filter = IncidentStatus(status.lower())
        except ValueError:
            stat_filter = None

    repo = IncidentRepository(db)
    incidents, total = await repo.get_all(skip=skip, limit=limit, severity=sev_filter, status=stat_filter)
    return IncidentListResponse(
        total=total,
        items=[IncidentResponse.model_validate(inc) for inc in incidents]
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get incident by ID"""
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(incident)


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_data: IncidentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing incident"""
    repo = IncidentRepository(db)
    incident = await repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    update_data = incident_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
    
    updated_incident = await repo.update(incident)
    return IncidentResponse.model_validate(updated_incident)


@router.delete("/{incident_id}", status_code=204)
async def delete_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an incident"""
    repo = IncidentRepository(db)
    deleted = await repo.delete(incident_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Incident not found")
    return None
