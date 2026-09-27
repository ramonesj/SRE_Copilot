"""HITL Approval Models for MVP"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional


class ApprovalDecision(Enum):
    """Approval decision states"""
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    TIMEOUT = 'TIMEOUT'


@dataclass
class ApprovalRequest:
    """Approval request record"""
    approval_request_id: str
    incident_id: str
    created_at: datetime
    diagnosis_summary: str
    confidence_score: float
    remediation_risk: float
    risk_classification: str
    recommended_action: str
    ssm_runbook: Optional[str]
    decision: ApprovalDecision = ApprovalDecision.PENDING
    decision_at: Optional[datetime] = None
    approver: Optional[str] = None
    rationale: Optional[str] = None

    @property
    def is_pending(self) -> bool:
        return self.decision == ApprovalDecision.PENDING

    @property
    def is_approved(self) -> bool:
        return self.decision == ApprovalDecision.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.decision == ApprovalDecision.REJECTED

    @property
    def is_timeout(self) -> bool:
        return self.decision == ApprovalDecision.TIMEOUT


@dataclass
class ApprovalResponse:
    """Approval response record"""
    approval_request_id: str
    decision: ApprovalDecision
    timestamp: datetime
    approver: Optional[str]
    rationale: Optional[str]
    incident_id: str