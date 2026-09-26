"""Local Alert Provider for MVP - Simulates EventBridge alert ingestion"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from shared.models import Alert, Incident


class LocalAlertProvider:
    """
    Local alert provider simulates EventBridge for MVP.
    Processes alerts from local sources and creates incident records.
    """

    def __init__(self, output_dir: str = "data/alerts"):
        self.output_dir = output_dir
        self.alert_counter = 0

    def ingest_alert(self, alert_data: Dict[str, Any]) -> tuple[bool, Optional[Alert], Optional[str]]:
        """
        Ingest an alert and validate its structure.
        
        Args:
            alert_data: Raw alert payload from monitoring system
            
        Returns:
            tuple: (success, Alert object, error_message)
        """
        try:
            # Extract required fields
            service = alert_data.get('service')
            severity = alert_data.get('severity', 'medium')
            message = alert_data.get('message', '')
            region = alert_data.get('region')
            instance_id = alert_data.get('instance_id')
            
            # Validate required fields
            if not service or not message:
                return False, None, "Missing required fields: service and message are required"
            
            # Validate severity
            valid_severities = ['critical', 'high', 'medium', 'low']
            if severity not in valid_severities:
                return False, None, f"Invalid severity. Must be one of: {valid_severities}"
            
            # Create Alert object
            alert = Alert(
                service=service,
                severity=severity,
                message=message,
                region=region,
                instance_id=instance_id,
                timestamp=datetime.utcnow()
            )
            
            return True, alert, None
            
        except Exception as e:
            return False, None, f"Error processing alert: {str(e)}"

    def create_incident_from_alert(self, alert: Alert) -> Incident:
        """
        Create an incident record from an alert.
        
        Args:
            alert: Validated Alert object
            
        Returns:
            Incident object in CREATED state
        """
        incident = Incident(
            incident_id=f"inc-{uuid.uuid4().hex[:12]}",
            service=alert.service,
            severity=alert.severity,
            message=alert.message,
            region=alert.region,
            instance_id=alert.instance_id,
            status=Incident.CREATED,
            timestamp=alert.timestamp
        )
        
        return incident

    def process_alert(self, alert_data: Dict[str, Any]) -> tuple[bool, Optional[Incident], Optional[str]]:
        """
        Process a complete alert ingestion workflow.
        
        Args:
            alert_data: Raw alert payload
            
        Returns:
            tuple: (success, Incident object, error_message)
        """
        # Validate alert
        success, alert, error = self.ingest_alert(alert_data)
        if not success:
            return False, None, error
        
        # Create incident
        incident = self.create_incident_from_alert(alert)
        
        # Save alert to local storage
        self._save_alert(alert)
        
        return True, incident, None

    def _save_alert(self, alert: Alert) -> None:
        """Save alert to local JSON file"""
        self.alert_counter += 1
        alert_file = f"{self.output_dir}/alert_{self.alert_counter:04d}.json"
        
        # Ensure output directory exists
        import os
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Serialize alert to JSON
        alert_dict = {
            'service': alert.service,
            'severity': alert.severity,
            'message': alert.message,
            'region': alert.region,
            'instance_id': alert.instance_id,
            'timestamp': alert.timestamp.isoformat()
        }
        
        with open(alert_file, 'w') as f:
            json.dump(alert_dict, f, indent=2)

    def load_sample_alerts(self) -> List[Dict[str, Any]]:
        """
        Load sample alerts for testing.
        
        Returns:
            List of sample alert payloads
        """
        return [
            {
                "service": "nginx",
                "severity": "critical",
                "message": "Connection timeout - service unresponsive",
                "region": "us-east-1",
                "instance_id": "i-1234567890abcdef0"
            },
            {
                "service": "redis",
                "severity": "high",
                "message": "Memory usage above 90% threshold",
                "region": "us-east-1",
                "instance_id": "i-0987654321fedcba0"
            },
            {
                "service": "postgresql",
                "severity": "critical",
                "message": "Database connection pool exhausted",
                "region": "us-west-2",
                "instance_id": "i-abcdef1234567890"
            }
        ]