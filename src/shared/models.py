"""SRE Copilot Data Models"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


@dataclass
class Alert:
    """Alert payload from monitoring systems"""
    service: str
    severity: str
    message: str
    region: Optional[str] = None
    instance_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def validate(self) -> bool:
        """Validate alert payload"""
        valid_severities = ['critical', 'high', 'medium', 'low']
        if self.severity not in valid_severities:
            return False
        if not self.service or not self.message:
            return False
        return True


@dataclass
class Incident:
    """Incident record with lifecycle state"""
    incident_id: str
    service: str
    severity: str
    message: str
    status: str  # Lifecycle state
    region: Optional[str] = None
    instance_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Lifecycle states
    CREATED = 'CREATED'
    EVIDENCE_COLLECTED = 'EVIDENCE_COLLECTED'
    DIAGNOSIS_COMPLETE = 'DIAGNOSIS_COMPLETE'
    RISK_ASSESSED = 'RISK_ASSESSED'
    APPROVAL_PENDING = 'APPROVAL_PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    TIMEOUT_EXCEEDED = 'TIMEOUT_EXCEEDED'
    EXECUTION_SUCCEEDED = 'EXECUTION_SUCCEEDED'
    RECOVERY_VERIFIED = 'RECOVERY_VERIFIED'
    RECOVERY_FAILED = 'RECOVERY_FAILED'
    RESOLVED = 'RESOLVED'
    
    # Diagnosis fields
    diagnosis: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    root_cause: Optional[Dict[str, Any]] = None
    
    # Risk fields
    risk_score: Optional[int] = None
    ssm_runbook: Optional[str] = None
    
    # Execution fields
    execution_result: Optional[Dict[str, Any]] = None
    verification_result: Optional[Dict[str, Any]] = None
    
    def validate_transition(self, new_status: str) -> bool:
        """Validate state transition"""
        valid_transitions = {
            self.CREATED: [self.EVIDENCE_COLLECTED],
            self.EVIDENCE_COLLECTED: [self.DIAGNOSIS_COMPLETE],
            self.DIAGNOSIS_COMPLETE: [self.RISK_ASSESSED],
            self.RISK_ASSESSED: [self.APPROVAL_PENDING],
            self.APPROVAL_PENDING: [self.APPROVED, self.REJECTED, self.TIMEOUT_EXCEEDED],
            self.APPROVED: [self.EXECUTION_SUCCEEDED],
            self.EXECUTION_SUCCEEDED: [self.RECOVERY_VERIFIED, self.RECOVERY_FAILED],
            self.RECOVERY_VERIFIED: [self.RESOLVED],
        }
        return new_status in valid_transitions.get(self.status, [])


@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str
    timestamp: datetime
    actor: str  # Component that triggered the event
    action: str  # Action performed
    details: Dict[str, Any]
    incident_id: Optional[str] = None
    
    # Event types
    INCIDENT_CREATED = 'INCIDENT_CREATED'
    EVIDENCE_COLLECTED = 'EVIDENCE_COLLECTED'
    DIAGNOSIS_GENERATED = 'DIAGNOSIS_GENERATED'
    RISK_ASSESSED = 'RISK_ASSESSED'
    APPROVAL_REQUESTED = 'APPROVAL_REQUESTED'
    APPROVAL_RECEIVED = 'APPROVAL_RECEIVED'
    EXECUTION_STARTED = 'EXECUTION_STARTED'
    EXECUTION_COMPLETED = 'EXECUTION_COMPLETED'
    VERIFICATION_COMPLETED = 'VERIFICATION_COMPLETED'
    INCIDENT_RESOLVED = 'INCIDENT_RESOLVED'
    INCIDENT_REJECTED = 'INCIDENT_REJECTED'
    INCIDENT_TIMEOUT = 'INCIDENT_TIMEOUT'