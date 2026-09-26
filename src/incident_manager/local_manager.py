"""Local Incident Manager for MVP - Manages incident lifecycle without AWS services"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from shared.models import Incident, AuditEvent


class LocalIncidentManager:
    """
    Local incident manager simulates DynamoDB for MVP.
    Manages incident lifecycle states and transitions.
    """

    def __init__(self, data_dir: str = "data/incidents"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def create_incident(self, incident: Incident) -> tuple[bool, Optional[Incident], Optional[str]]:
        """
        Create a new incident record.
        
        Args:
            incident: Incident object in CREATED state
            
        Returns:
            tuple: (success, Incident object, error_message)
        """
        try:
            # Validate initial state
            if incident.status != Incident.CREATED:
                return False, None, "New incidents must have status CREATED"
            
            # Save incident
            if self._save_incident(incident):
                return True, incident, None
            else:
                return False, None, "Failed to save incident"
                
        except Exception as e:
            return False, None, f"Error creating incident: {str(e)}"

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """
        Retrieve an incident by ID.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            Incident object or None if not found
        """
        incident_file = f"{self.data_dir}/{incident_id}.json"
        
        if not os.path.exists(incident_file):
            return None
        
        try:
            with open(incident_file, 'r') as f:
                data = json.load(f)
            
            # Convert timestamp string back to datetime
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            
            return Incident(**data)
            
        except Exception as e:
            return None

    def update_incident(self, incident: Incident) -> tuple[bool, Optional[Incident], Optional[str]]:
        """
        Update an existing incident with state transition.
        
        Args:
            incident: Incident object with new state
            
        Returns:
            tuple: (success, Incident object, error_message)
        """
        try:
            # Validate state transition
            existing = self.get_incident(incident.incident_id)
            if not existing:
                return False, None, f"Incident {incident.incident_id} not found"
            
            # Validate transition
            if not existing.validate_transition(incident.status):
                return False, None, f"Invalid state transition: {existing.status} -> {incident.status}"
            
            # Update and save
            if self._save_incident(incident):
                return True, incident, None
            else:
                return False, None, "Failed to save incident"
                
        except Exception as e:
            return False, None, f"Error updating incident: {str(e)}"

    def transition_incident(self, incident_id: str, new_status: str) -> tuple[bool, Optional[Incident], Optional[str]]:
        """
        Transition an incident to a new state.
        
        Args:
            incident_id: Incident identifier
            new_status: Target state
            
        Returns:
            tuple: (success, Incident object, error_message)
        """
        existing = self.get_incident(incident_id)
        if not existing:
            return False, None, f"Incident {incident_id} not found"
        
        # Validate transition
        if not existing.validate_transition(new_status):
            return False, None, f"Invalid state transition: {existing.status} -> {new_status}"
        
        # Update status
        existing.status = new_status
        existing.timestamp = datetime.utcnow()
        
        return self.update_incident(existing)

    def _save_incident(self, incident: Incident) -> bool:
        """Save incident to local JSON file"""
        incident_file = f"{self.data_dir}/{incident.incident_id}.json"
        
        # Convert datetime to ISO format for JSON serialization
        incident_dict = {
            'incident_id': incident.incident_id,
            'service': incident.service,
            'severity': incident.severity,
            'message': incident.message,
            'status': incident.status,
            'region': incident.region,
            'instance_id': incident.instance_id,
            'timestamp': incident.timestamp.isoformat(),
            'diagnosis': incident.diagnosis,
            'confidence': incident.confidence,
            'root_cause': incident.root_cause,
            'risk_score': incident.risk_score,
            'ssm_runbook': incident.ssm_runbook,
            'execution_result': incident.execution_result,
            'verification_result': incident.verification_result
        }
        
        try:
            with open(incident_file, 'w') as f:
                json.dump(incident_dict, f, indent=2)
            return True
        except Exception:
            return False

    def list_incidents(self, status_filter: Optional[str] = None) -> List[Incident]:
        """
        List incidents, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of Incident objects
        """
        incidents = []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                incident = self.get_incident(filename[:-5])  # Remove .json extension
                if incident:
                    if status_filter is None or incident.status == status_filter:
                        incidents.append(incident)
        
        return incidents

    def record_audit_event(self, incident: Incident, actor: str, action: str, details: Dict[str, Any]) -> bool:
        """
        Create and save an audit event for an incident action.
        
        Args:
            incident: Incident object
            actor: Component that triggered the event
            action: Action performed
            details: Additional context
            
        Returns:
            bool: Success status
        """
        from audit.local_logger import LocalAuditLogger
        
        audit_event = AuditEvent(
            event_id=f"evt-{datetime.now().timestamp():.0f}",
            timestamp=datetime.utcnow(),
            actor=actor,
            action=action,
            details=details,
            incident_id=incident.incident_id
        )
        
        audit_logger = LocalAuditLogger()
        return audit_logger.log_event(audit_event)