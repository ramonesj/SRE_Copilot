"""
Health Verification Data Models

This module defines the data models for health verification in the SRE Copilot MVP.
No AWS dependencies, all models are serializable to JSON.

Critical Safety Invariant: Execution Success ≠ Recovery Verified
- SSM execution success alone does NOT constitute incident resolution
- Only health verification SUCCESS leads to RESOLVED status
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List


class HealthStatus(Enum):
    """Status of service health verification"""
    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    DEGRADED = "DEGRADED"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


class VerificationMethod(Enum):
    """Methods used for health verification"""
    SERVICE_STATUS = "SERVICE_STATUS"
    ENDPOINT_CHECK = "ENDPOINT_CHECK"
    METRICS_ANALYSIS = "METRICS_ANALYSIS"
    LOG_ANALYSIS = "LOG_ANALYSIS"
    SYNTHETIC_MONITOR = "SYNTHETIC_MONITOR"


@dataclass
class HealthCheck:
    """Individual health check with results"""
    
    check_id: str
    """Unique check identifier"""
    
    method: VerificationMethod
    """Verification method used"""
    
    status: HealthStatus
    """Check result status"""
    
    executed_at: datetime
    """When the check was executed"""
    
    duration_seconds: float
    """How long the check took"""
    
    details: Dict[str, Any]
    """Detailed check results"""
    
    error_message: Optional[str] = None
    """Error message if check failed"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'check_id': self.check_id,
            'method': self.method.value,
            'status': self.status.value,
            'executed_at': self.executed_at.isoformat(),
            'duration_seconds': self.duration_seconds,
            'details': self.details,
            'error_message': self.error_message
        }


@dataclass
class VerificationResult:
    """
    Complete health verification result for an incident.
    
    Enforces critical safety invariant:
    Execution Success ≠ Recovery Verified
    Only VerificationResult.success = True leads to RESOLVED status
    """
    
    verification_id: str
    """Unique verification identifier"""
    
    incident_id: str
    """Associated incident ID"""
    
    execution_id: str
    """SSM execution that was verified"""
    
    overall_status: HealthStatus
    """Overall verification status"""
    
    success: bool
    """Whether verification succeeded (critical for RESOLVED status)"""
    
    checks: List[HealthCheck]
    """Individual health checks performed"""
    
    verified_at: datetime
    """When verification was completed"""
    
    verification_duration_seconds: float
    """Total verification duration"""
    
    confidence_score: float
    """Confidence in verification result (0.0-1.0)"""
    
    failure_reason: Optional[str] = None
    """Reason for verification failure, if any"""
    
    retry_count: int = 0
    """Number of verification retry attempts"""
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    """When verification record was created"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'verification_id': self.verification_id,
            'incident_id': self.incident_id,
            'execution_id': self.execution_id,
            'overall_status': self.overall_status.value,
            'success': self.success,
            'checks': [check.to_dict() for check in self.checks],
            'verified_at': self.verified_at.isoformat(),
            'verification_duration_seconds': self.verification_duration_seconds,
            'confidence_score': self.confidence_score,
            'failure_reason': self.failure_reason,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationResult':
        """Create from dictionary"""
        checks = []
        for check_data in data.get('checks', []):
            checks.append(HealthCheck(
                check_id=check_data['check_id'],
                method=VerificationMethod(check_data['method']),
                status=HealthStatus(check_data['status']),
                executed_at=datetime.fromisoformat(check_data['executed_at']),
                duration_seconds=check_data['duration_seconds'],
                details=check_data['details'],
                error_message=check_data.get('error_message')
            ))
        
        return cls(
            verification_id=data['verification_id'],
            incident_id=data['incident_id'],
            execution_id=data['execution_id'],
            overall_status=HealthStatus(data['overall_status']),
            success=data['success'],
            checks=checks,
            verified_at=datetime.fromisoformat(data['verified_at']),
            verification_duration_seconds=data['verification_duration_seconds'],
            confidence_score=data['confidence_score'],
            failure_reason=data.get('failure_reason'),
            retry_count=data.get('retry_count', 0),
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class VerificationCriteria:
    """
    Criteria for health verification.
    Defines what constitutes a successful recovery.
    """
    
    required_checks: List[VerificationMethod]
    """Health checks that must pass"""
    
    minimum_confidence: float = 0.8
    """Minimum confidence score for success"""
    
    timeout_seconds: int = 60
    """Verification timeout in seconds"""
    
    max_retries: int = 3
    """Maximum verification retry attempts"""
    
    retry_delay_seconds: int = 10
    """Delay between retry attempts"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'required_checks': [method.value for method in self.required_checks],
            'minimum_confidence': self.minimum_confidence,
            'timeout_seconds': self.timeout_seconds,
            'max_retries': self.max_retries,
            'retry_delay_seconds': self.retry_delay_seconds
        }