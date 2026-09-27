"""Evidence API Endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.evidence import EvidenceType
from app.schemas.evidence import EvidenceResponse, EvidenceListResponse
from app.repositories.evidence_repository import EvidenceRepository

router = APIRouter()


@router.post("/upload", response_model=EvidenceResponse, status_code=201)
async def upload_evidence(
    incident_id: int = Query(..., description="Incident ID"),
    file: UploadFile = File(...),
    evidence_type: EvidenceType = EvidenceType.OTHER,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload evidence file for an incident"""
    repo = EvidenceRepository(db)
    
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    
    evidence = await repo.create(
        incident_id=incident_id,
        filename=file.filename or "unknown",
        content=content,
        evidence_type=evidence_type,
        description=description
    )
    
    return EvidenceResponse.model_validate(evidence)


@router.get("/", response_model=EvidenceListResponse)
async def list_evidence(
    incident_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List evidence with optional incident filter"""
    repo = EvidenceRepository(db)
    
    if incident_id:
        evidences, total = await repo.get_by_incident(incident_id, skip, limit)
    else:
        evidences, total = [], 0
    
    return EvidenceListResponse(
        total=total,
        items=[EvidenceResponse.model_validate(ev) for ev in evidences]
    )


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get evidence by ID"""
    repo = EvidenceRepository(db)
    evidence = await repo.get_by_id(evidence_id)
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return EvidenceResponse.model_validate(evidence)


@router.get("/{evidence_id}/download")
async def download_evidence(
    evidence_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Download evidence file"""
    repo = EvidenceRepository(db)
    evidence = await repo.get_by_id(evidence_id)
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    content = await repo.read_file(evidence)
    
    return Response(
        content=content,
        media_type=evidence.mime_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{evidence.filename}"'
        }
    )


@router.delete("/{evidence_id}", status_code=204)
async def delete_evidence(
    evidence_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete evidence and its file"""
    repo = EvidenceRepository(db)
    deleted = await repo.delete(evidence_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return None
