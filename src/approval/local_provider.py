"""Local HITL Approval Provider for MVP - Simulates human approval without AWS services"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from shared.models import Incident
from .models import ApprovalDecision, ApprovalRequest, ApprovalResponse


class LocalApprovalProvider:
    """
    Local approval provider simulates Human-in-the-Loop approval for MVP.
    No AWS services, no Step Functions, no Task Tokens.
    """

    def __init__(self, data_dir: str = "data/approvals"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def create_approval_request(self, incident: Incident, risk_assessment: Dict[str, Any]) -> Tuple[bool, Optional[ApprovalRequest], Optional[str]]:
        """
        Create an approval request for an incident.
        
        Args:
            incident: Incident object
            risk_assessment: Risk assessment results
            
        Returns:
            tuple: (success, ApprovalRequest, error_message)
        """
        try:
            # Generate unique approval request ID
            approval_request_id = f"req-{uuid.uuid4().hex[:12]}"
            
            # Create approval request record
            approval_request = ApprovalRequest(
                approval_request_id=approval_request_id,
                incident_id=incident.incident_id,
                created_at=datetime.utcnow(),
                diagnosis_summary=risk_assessment['diagnosis_summary'],
                confidence_score=risk_assessment['confidence_score'],
                remediation_risk=risk_assessment['remediation_risk'],
                risk_classification=risk_assessment['risk_classification'],
                recommended_action=risk_assessment['recommended_action'],
                ssm_runbook=risk_assessment['ssm_runbook']
            )
            
            # Save approval request
            self._save_approval_request(approval_request)
            
            return True, approval_request, None
            
        except Exception as e:
            return False, None, f"Error creating approval request: {str(e)}"

    def approve(self, approval_request: ApprovalRequest, approver: str = "system", rationale: str = "Automated approval for MVP") -> Tuple[bool, Optional[ApprovalResponse], Optional[str]]:
        """
        Approve an approval request.
        
        Args:
            approval_request: ApprovalRequest object
            approver: Identity of the approver
            rationale: Reason for approval
            
        Returns:
            tuple: (success, ApprovalResponse, error_message)
        """
        try:
            # Update approval request
            approval_request.decision = ApprovalDecision.APPROVED
            approval_request.decision_at = datetime.utcnow()
            approval_request.approver = approver
            approval_request.rationale = rationale
            
            # Save updated request
            self._save_approval_request(approval_request)
            
            # Create response record
            approval_response = ApprovalResponse(
                approval_request_id=approval_request.approval_request_id,
                decision=ApprovalDecision.APPROVED,
                timestamp=approval_request.decision_at,
                approver=approver,
                rationale=rationale,
                incident_id=approval_request.incident_id
            )
            
            return True, approval_response, None
            
        except Exception as e:
            return False, None, f"Error approving request: {str(e)}"

    def reject(self, approval_request: ApprovalRequest, approver: str = "system", rationale: str = "Automated rejection for MVP") -> Tuple[bool, Optional[ApprovalResponse], Optional[str]]:
        """
        Reject an approval request.
        
        Args:
            approval_request: ApprovalRequest object
            approver: Identity of the approver
            rationale: Reason for rejection
            
        Returns:
            tuple: (success, ApprovalResponse, error_message)
        """
        try:
            # Update approval request
            approval_request.decision = ApprovalDecision.REJECTED
            approval_request.decision_at = datetime.utcnow()
            approval_request.approver = approver
            approval_request.rationale = rationale
            
            # Save updated request
            self._save_approval_request(approval_request)
            
            # Create response record
            approval_response = ApprovalResponse(
                approval_request_id=approval_request.approval_request_id,
                decision=ApprovalDecision.REJECTED,
                timestamp=approval_request.decision_at,
                approver=approver,
                rationale=rationale,
                incident_id=approval_request.incident_id
            )
            
            return True, approval_response, None
            
        except Exception as e:
            return False, None, f"Error rejecting request: {str(e)}"

    def timeout(self, approval_request: ApprovalRequest, rationale: str = "Approval timeout exceeded") -> Tuple[bool, Optional[ApprovalResponse], Optional[str]]:
        """
        Mark an approval request as timed out.
        
        Args:
            approval_request: ApprovalRequest object
            rationale: Reason for timeout
            
        Returns:
            tuple: (success, ApprovalResponse, error_message)
        """
        try:
            # Update approval request
            approval_request.decision = ApprovalDecision.TIMEOUT
            approval_request.decision_at = datetime.utcnow()
            approval_request.approver = "system"
            approval_request.rationale = rationale
            
            # Save updated request
            self._save_approval_request(approval_request)
            
            # Create response record
            approval_response = ApprovalResponse(
                approval_request_id=approval_request.approval_request_id,
                decision=ApprovalDecision.TIMEOUT,
                timestamp=approval_request.decision_at,
                approver="system",
                rationale=rationale,
                incident_id=approval_request.incident_id
            )
            
            return True, approval_response, None
            
        except Exception as e:
            return False, None, f"Error timing out request: {str(e)}"

    def _save_approval_request(self, approval_request: ApprovalRequest) -> bool:
        """Save approval request to local file"""
        try:
            approval_file = f"{self.data_dir}/approval_{approval_request.approval_request_id}.json"
            
            # Convert to dict for JSON serialization
            request_dict = {
                'approval_request_id': approval_request.approval_request_id,
                'incident_id': approval_request.incident_id,
                'created_at': approval_request.created_at.isoformat(),
                'diagnosis_summary': approval_request.diagnosis_summary,
                'confidence_score': approval_request.confidence_score,
                'remediation_risk': approval_request.remediation_risk,
                'risk_classification': approval_request.risk_classification,
                'recommended_action': approval_request.recommended_action,
                'ssm_runbook': approval_request.ssm_runbook,
                'decision': approval_request.decision.value,
                'decision_at': approval_request.decision_at.isoformat() if approval_request.decision_at else None,
                'approver': approval_request.approver,
                'rationale': approval_request.rationale
            }
            
            with open(approval_file, 'w') as f:
                json.dump(request_dict, f, indent=2)
            
            return True
        except Exception:
            return False

    def get_approval_request(self, approval_request_id: str) -> Optional[ApprovalRequest]:
        """Retrieve approval request by ID"""
        approval_file = f"{self.data_dir}/approval_{approval_request_id}.json"
        
        if not os.path.exists(approval_file):
            return None
        
        try:
            with open(approval_file, 'r') as f:
                data = json.load(f)
            
            return ApprovalRequest(
                approval_request_id=data['approval_request_id'],
                incident_id=data['incident_id'],
                created_at=datetime.fromisoformat(data['created_at']),
                diagnosis_summary=data['diagnosis_summary'],
                confidence_score=data['confidence_score'],
                remediation_risk=data['remediation_risk'],
                risk_classification=data['risk_classification'],
                recommended_action=data['recommended_action'],
                ssm_runbook=data['ssm_runbook'],
                decision=ApprovalDecision(data['decision']),
                decision_at=datetime.fromisoformat(data['decision_at']) if data['decision_at'] else None,
                approver=data.get('approver'),
                rationale=data.get('rationale')
            )
        except Exception:
            return None

    def get_approval_requests_by_incident(self, incident_id: str) -> list:
        """Get all approval requests for an incident"""
        requests = []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                request = self.get_approval_request(filename[:-5])
                if request and request.incident_id == incident_id:
                    requests.append(request)
        
        return requests