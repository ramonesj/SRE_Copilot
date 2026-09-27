"""
SSM Execution Data Models

This module defines the data models for SSM execution tracking in the local MVP.
No AWS dependencies, all models are serializable to JSON.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List


class ExecutionStatus(Enum):
    """Status of an SSM execution"""
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


@dataclass
class SSMExecution:
    """
    SSM execution record for the local MVP.
    Represents an SSM Runbook execution without AWS dependencies.
    """
    
    execution_id: str
    """Unique execution identifier"""
    
    incident_id: str
    """Associated incident ID"""
    
    runbook_name: str
    """Name of the SSM Runbook to execute"""
    
    parameters: Dict[str, Any]
    """Execution parameters"""
    
    status: ExecutionStatus = ExecutionStatus.PENDING
    """Current execution status"""
    
    started_at: Optional[datetime] = None
    """When execution started"""
    
    completed_at: Optional[datetime] = None
    """When execution completed"""
    
    error_message: Optional[str] = None
    """Error message if execution failed"""
    
    output: Optional[Dict[str, Any]] = None
    """Execution output"""
    
    retry_count: int = 0
    """Number of retry attempts"""
    
    max_retries: int = 3
    """Maximum retry attempts"""
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    """When the execution record was created"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution record to dictionary for JSON serialization"""
        return {
            'execution_id': self.execution_id,
            'incident_id': self.incident_id,
            'runbook_name': self.runbook_name,
            'parameters': self.parameters,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'output': self.output,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SSMExecution':
        """Create execution record from dictionary"""
        execution = cls(
            execution_id=data['execution_id'],
            incident_id=data['incident_id'],
            runbook_name=data['runbook_name'],
            parameters=data['parameters'],
            status=ExecutionStatus(data['status']),
            error_message=data.get('error_message'),
            output=data.get('output'),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3)
        )
        
        if data.get('started_at'):
            execution.started_at = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            execution.completed_at = datetime.fromisoformat(data['completed_at'])
        if data.get('created_at'):
            execution.created_at = datetime.fromisoformat(data['created_at'])
        
        return execution


@dataclass
class ExecutionParameters:
    """
    Common execution parameters for SSM Runbooks.
    These parameters would be passed to real SSM Runbooks in production.
    """
    
    instance_id: str
    """EC2 instance ID"""
    
    service_name: str
    """Service name to restart"""
    
    region: str = "us-east-1"
    """AWS region"""
    
    timeout_seconds: int = 300
    """Execution timeout in seconds"""
    
    environment: str = "development"
    """Environment (development/staging/production)"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'instance_id': self.instance_id,
            'service_name': self.service_name,
            'region': self.region,
            'timeout_seconds': self.timeout_seconds,
            'environment': self.environment
        }