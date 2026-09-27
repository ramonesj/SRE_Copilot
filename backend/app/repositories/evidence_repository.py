"""Evidence Repository with File Storage"""
import uuid
import os
import aiofiles
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evidence import Evidence, EvidenceType
from app.core.config import settings


class EvidenceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage_path = settings.EVIDENCE_PATH

    def _generate_evidence_id(self) -> str:
        return f"EV-{uuid.uuid4().hex[:12].upper()}"

    async def save_file(self, filename: str, content: bytes) -> str:
        """Save file to storage and return filepath"""
        evidence_id = self._generate_evidence_id()
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{evidence_id}{file_extension}"
        filepath = os.path.join(self.storage_path, unique_filename)
        
        os.makedirs(self.storage_path, exist_ok=True)
        
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(content)
        
        return filepath

    async def create(
        self,
        incident_id: int,
        filename: str,
        content: bytes,
        evidence_type: EvidenceType,
        description: Optional[str] = None,
        uploaded_by: Optional[str] = None
    ) -> Evidence:
        """Create evidence with file upload"""
        filepath = await self.save_file(filename, content)
        
        evidence = Evidence(
            evidence_id=self._generate_evidence_id(),
            incident_id=incident_id,
            filename=filename,
            filepath=filepath,
            evidence_type=evidence_type,
            file_size=len(content),
            mime_type=self._get_mime_type(filename),
            description=description,
            uploaded_by=uploaded_by
        )
        
        self.db.add(evidence)
        await self.db.flush()
        await self.db.refresh(evidence)
        return evidence

    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename"""
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.txt': 'text/plain',
            '.log': 'text/plain',
            '.json': 'application/json',
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        return mime_types.get(ext, 'application/octet-stream')

    async def get_by_id(self, evidence_id: int) -> Optional[Evidence]:
        result = await self.db.execute(
            select(Evidence).where(Evidence.id == evidence_id)
        )
        return result.scalar_one_or_none()

    async def get_by_incident(
        self,
        incident_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Evidence], int]:
        query = select(Evidence).where(Evidence.incident_id == incident_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        query = query.offset(skip).limit(limit).order_by(Evidence.uploaded_at.desc())
        result = await self.db.execute(query)
        evidences = result.scalars().all()
        
        return evidences, total or 0

    async def delete(self, evidence_id: int) -> bool:
        evidence = await self.get_by_id(evidence_id)
        if evidence:
            if os.path.exists(evidence.filepath):
                os.remove(evidence.filepath)
            await self.db.delete(evidence)
            await self.db.flush()
            return True
        return False

    async def read_file(self, evidence: Evidence) -> bytes:
        """Read file content"""
        async with aiofiles.open(evidence.filepath, 'rb') as f:
            return await f.read()
