"""Local Diagnosis Engine Provider for MVP - Simulates Amazon Bedrock LLM analysis"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from shared.models import Incident


class LocalDiagnosisProvider:
    """
    Local diagnosis provider simulates Amazon Bedrock LLM for MVP.
    Generates diagnoses and root cause analysis using pattern matching.
    
    This provider is designed to be replaced with Bedrock integration later.
    """

    def __init__(self, output_dir: str = "data/diagnosis"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def analyze(self, incident: Incident, evidence_package: Dict[str, Any]) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze incident evidence and generate diagnosis.
        
        Args:
            incident: Incident object
            evidence_package: Evidence collection results
            
        Returns:
            tuple: (success, diagnosis, error_message)
        """
        try:
            # Extract logs from evidence
            logs = evidence_package.get('logs', [])
            
            # Generate diagnosis based on logs and incident type
            diagnosis = self._generate_diagnosis(incident, logs)
            
            # Save diagnosis
            self._save_diagnosis(diagnosis)
            
            return True, diagnosis, None
            
        except Exception as e:
            return False, None, f"Error analyzing incident: {str(e)}"

    def _generate_diagnosis(self, incident: Incident, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate diagnosis based on log patterns"""
        
        # Check for error patterns in logs
        error_logs = [log for log in logs if log.get('level') in ['ERROR', 'CRITICAL']]
        
        # Determine root cause based on service type and error patterns
        diagnosis_patterns = {
            'nginx': {
                'service_crash': {
                    'confidence': 0.92,
                    'summary': 'Service crash detected',
                    'evidence': [
                        'worker process crashed',
                        'restarting worker process',
                        'Connection timeout'
                    ],
                    'recommended_action': 'restart_service'
                },
                'upstream_failure': {
                    'confidence': 0.78,
                    'summary': 'Upstream service failure',
                    'evidence': [
                        'upstream timed out',
                        'Connection timed out'
                    ],
                    'recommended_action': 'check_upstream_services'
                }
            },
            'redis': {
                'memory_exhaustion': {
                    'confidence': 0.89,
                    'summary': 'Memory exhaustion detected',
                    'evidence': [
                        'Out of memory',
                        'Memory usage above 80%',
                        'Background saving error'
                    ],
                    'recommended_action': 'increase_memory_or_restart'
                },
                'client_overflow': {
                    'confidence': 0.85,
                    'summary': 'Too many client connections',
                    'evidence': [
                        'too many connections'
                    ],
                    'recommended_action': 'increase_connections_limit'
                }
            },
            'postgresql': {
                'connection_pool_exhausted': {
                    'confidence': 0.95,
                    'summary': 'Connection pool exhausted',
                    'evidence': [
                        'too many connections for role',
                        'remaining connection slots are reserved',
                        'FATAL: too many connections'
                    ],
                    'recommended_action': 'restart_database_or_increase_connections'
                },
                'parallel_worker_failure': {
                    'confidence': 0.88,
                    'summary': 'Parallel worker unavailable',
                    'evidence': [
                        'parallel workers unavailable'
                    ],
                    'recommended_action': 'restart_database'
                }
            }
        }
        
        # Get patterns for this service
        service_patterns = diagnosis_patterns.get(incident.service, diagnosis_patterns['nginx'])
        
        # Find matching pattern based on error messages
        matched_pattern = self._find_matching_pattern(service_patterns, error_logs)
        
        if matched_pattern:
            confidence = matched_pattern['confidence']
            cause_type = list(service_patterns.keys())[list(service_patterns.values()).index(matched_pattern)]
        else:
            # Default pattern if no match found
            default_pattern = list(service_patterns.values())[0]
            confidence = 0.65
            cause_type = list(service_patterns.keys())[0]
        
        # Create diagnosis
        diagnosis = {
            'incident_id': incident.incident_id,
            'generated_at': datetime.utcnow().isoformat(),
            'diagnosis': {
                'summary': matched_pattern['summary'] if matched_pattern else 'Service failure detected',
                'confidence': confidence,
                'root_cause': {
                    'cause_type': cause_type,
                    'description': self._describe_cause(cause_type, incident.service)
                },
                'evidence': matched_pattern['evidence'] if matched_pattern else [],
                'recommended_action': matched_pattern['recommended_action'] if matched_pattern else 'investigate_manually'
            },
            'evidence_summary': {
                'total_logs': len(logs),
                'error_count': len(error_logs),
                'error_levels': self._count_error_levels(error_logs)
            }
        }
        
        return diagnosis

    def _find_matching_pattern(self, patterns: Dict[str, Dict], logs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the best matching pattern based on error logs"""
        best_match = None
        best_score = 0
        
        for pattern_name, pattern_data in patterns.items():
            score = 0
            pattern_evidence = pattern_data.get('evidence', [])
            
            for log in logs:
                log_message = log.get('message', '').lower()
                for evidence_item in pattern_evidence:
                    if evidence_item.lower() in log_message:
                        score += 1
            
            if score > best_score:
                best_score = score
                best_match = pattern_data
        
        return best_match if best_score > 0 else None

    def _describe_cause(self, cause_type: str, service: str) -> str:
        """Generate human-readable description of the root cause"""
        descriptions = {
            'service_crash': f'{service} process terminated unexpectedly',
            'upstream_failure': f'{service} upstream service is unavailable',
            'memory_exhaustion': f'{service} ran out of memory',
            'client_overflow': f'{service} has too many client connections',
            'connection_pool_exhausted': f'{service} connection pool is exhausted',
            'parallel_worker_failure': f'{service} parallel workers are unavailable'
        }
        return descriptions.get(cause_type, 'Unknown service failure')

    def _count_error_levels(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count log entries by error level"""
        counts = {}
        for log in logs:
            level = log.get('level', 'UNKNOWN')
            counts[level] = counts.get(level, 0) + 1
        return counts

    def _save_diagnosis(self, diagnosis: Dict[str, Any]) -> bool:
        """Save diagnosis to local file"""
        try:
            diagnosis_file = f"{self.output_dir}/diagnosis_{diagnosis['incident_id']}.json"
            
            with open(diagnosis_file, 'w') as f:
                json.dump(diagnosis, f, indent=2)
            
            return True
        except Exception:
            return False

    def get_diagnosis(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve diagnosis for an incident"""
        diagnosis_file = f"{self.output_dir}/diagnosis_{incident_id}.json"
        
        if not os.path.exists(diagnosis_file):
            return None
        
        try:
            with open(diagnosis_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def load_sample_diagnosis(self, incident: Incident, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Load sample diagnosis for testing"""
        return self._generate_diagnosis(incident, logs)