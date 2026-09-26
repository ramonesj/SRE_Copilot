"""Local Evidence Collection Provider for MVP - Simulates CloudWatch log collection"""

import json
import os
import random
from datetime import datetime
from typing import Dict, Any, Optional, List

from shared.models import Incident


class LocalEvidenceCollectionProvider:
    """
    Local evidence collection provider simulates CloudWatch log collection for MVP.
    Gathers evidence from incidents and creates evidence packages.
    """

    def __init__(self, evidence_dir: str = "data/evidence"):
        self.evidence_dir = evidence_dir
        os.makedirs(evidence_dir, exist_ok=True)

    def collect_evidence(self, incident: Incident) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Collect evidence for an incident.
        
        Args:
            incident: Incident object
            
        Returns:
            tuple: (success, evidence package, error_message)
        """
        try:
            # Generate synthetic logs based on incident type
            logs = self._generate_synthetic_logs(incident)
            
            # Collect service metadata
            metadata = self._collect_service_metadata(incident)
            
            # Create evidence package
            evidence_package = {
                'incident_id': incident.incident_id,
                'collected_at': datetime.utcnow().isoformat(),
                'logs': logs,
                'metadata': metadata,
                'evidence_type': 'cloudwatch_logs',
                'total_log_lines': len(logs)
            }
            
            # Save evidence package
            self._save_evidence_package(evidence_package)
            
            return True, evidence_package, None
            
        except Exception as e:
            return False, None, f"Error collecting evidence: {str(e)}"

    def _generate_synthetic_logs(self, incident: Incident) -> List[Dict[str, Any]]:
        """Generate synthetic log entries based on incident type"""
        logs = []
        
        # Base timestamp
        base_time = datetime.utcnow()
        
        # Generate log entries leading up to the incident
        error_patterns = {
            'nginx': [
                {'level': 'INFO', 'message': 'Connection from 192.168.1.100 accepted'},
                {'level': 'ERROR', 'message': 'Connection timeout after 30s'},
                {'level': 'ERROR', 'message': 'upstream timed out (110: Connection timed out)'},
                {'level': 'CRITICAL', 'message': 'worker process crashed'},
                {'level': 'ERROR', 'message': 'restarting worker process'},
            ],
            'redis': [
                {'level': 'INFO', 'message': 'Client connected from 127.0.0.1:54321'},
                {'level': 'WARNING', 'message': 'Memory usage above 80% threshold'},
                {'level': 'WARNING', 'message': 'Memory usage above 85% threshold'},
                {'level': 'ERROR', 'message': 'Out of memory allocating 1024 bytes'},
                {'level': 'CRITICAL', 'message': 'Background saving error'},
            ],
            'postgresql': [
                {'level': 'INFO', 'message': 'connection received: host=10.0.0.1 port=12345'},
                {'level': 'WARNING', 'message': 'too many connections for role "app"'},
                {'level': 'ERROR', 'message': 'remaining connection slots are reserved'},
                {'level': 'ERROR', 'message': 'FATAL: too many connections'},
                {'level': 'CRITICAL', 'message': 'parallel workers unavailable'},
            ],
        }
        
        pattern = error_patterns.get(incident.service, error_patterns['nginx'])
        
        for i, log_entry in enumerate(pattern):
            timestamp = base_time.replace(
                second=max(0, base_time.second - (len(pattern) - i)),
                microsecond=0
            )
            logs.append({
                'timestamp': timestamp.isoformat(),
                'level': log_entry['level'],
                'message': log_entry['message'],
                'service': incident.service,
                'region': incident.region or 'us-east-1',
                'source': 'CloudWatch Logs'
            })
        
        return logs

    def _collect_service_metadata(self, incident: Incident) -> Dict[str, Any]:
        """Collect service metadata and context"""
        return {
            'service_name': incident.service,
            'instance_id': incident.instance_id or 'unknown',
            'region': incident.region or 'us-east-1',
            'severity': incident.severity,
            'error_message': incident.message,
            'environment': 'development',  # Configurable per environment
            'tags': ['critical', 'service-outage'],
            'related_services': self._get_related_services(incident.service)
        }

    def _get_related_services(self, service: str) -> List[str]:
        """Get related services based on common architecture"""
        service_dependencies = {
            'nginx': ['backend-api', 'cache-redis'],
            'redis': ['api-gateway', 'session-store'],
            'postgresql': ['api-gateway', 'user-service', 'order-service'],
        }
        return service_dependencies.get(service, [])

    def _save_evidence_package(self, evidence_package: Dict[str, Any]) -> bool:
        """Save evidence package to local file"""
        try:
            evidence_file = f"{self.evidence_dir}/evidence_{evidence_package['incident_id']}.json"
            
            with open(evidence_file, 'w') as f:
                json.dump(evidence_package, f, indent=2)
            
            return True
        except Exception:
            return False

    def get_evidence(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve evidence package for an incident"""
        evidence_file = f"{self.evidence_dir}/evidence_{incident_id}.json"
        
        if not os.path.exists(evidence_file):
            return None
        
        try:
            with open(evidence_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def load_sample_evidence(self, incident: Incident) -> Dict[str, Any]:
        """Load sample evidence for testing"""
        evidence_package = {
            'incident_id': incident.incident_id,
            'collected_at': datetime.utcnow().isoformat(),
            'logs': self._generate_synthetic_logs(incident),
            'metadata': self._collect_service_metadata(incident),
            'evidence_type': 'cloudwatch_logs',
            'total_log_lines': 5
        }
        return evidence_package