"""Local Risk Assessment Provider for MVP - Integrates existing Risk Engine"""

import sys
import os

# Add project root to path for importing risk_engine
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from lambdas.risk_assessment.risk_engine import calculate_risk_score
from typing import Dict, Any, Optional, Tuple

from shared.models import Incident


class LocalRiskAssessmentProvider:
    """
    Local risk assessment provider that integrates the existing Risk Engine.
    Evaluates remediation risk and identifies appropriate SSM Runbooks.
    """

    def __init__(self):
        pass

    def assess_risk(self, incident: Incident, diagnosis: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Assess risk for an incident based on diagnosis.
        
        Args:
            incident: Incident object
            diagnosis: Diagnosis results from diagnosis engine
            
        Returns:
            tuple: (success, risk assessment, error_message)
        """
        try:
            # Calculate risk scores using the existing risk engine
            # Use fixed values for MVP (can be configured per service in production)
            risk_score = self._calculate_risk_scores(incident, diagnosis)
            
            # Get SSM runbook for this incident type
            ssm_runbook = self._identify_runbook(incident, diagnosis)
            
            # Create risk assessment object
            risk_assessment = {
                'incident_id': incident.incident_id,
                'assessed_at': self._get_current_timestamp(),
                'remediation_risk': risk_score['total_risk'],
                'risk_classification': self._classify_risk(risk_score['total_risk']),
                'risk_factors': risk_score,
                'diagnosis_summary': diagnosis['diagnosis']['summary'],
                'confidence_score': diagnosis['diagnosis']['confidence'],
                'root_cause': diagnosis['diagnosis']['root_cause'],
                'recommended_action': diagnosis['diagnosis']['recommended_action'],
                'ssm_runbook': ssm_runbook
            }
            
            return True, risk_assessment, None
            
        except Exception as e:
            return False, None, f"Error assessing risk: {str(e)}"

    def _calculate_risk_scores(self, incident: Incident, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk scores using the existing Risk Engine"""
        
        # Determine risk factors based on incident characteristics
        # These are placeholder values that can be configured in production
        
        # Action impact: Restart service has moderate impact
        action_impact = self._determine_action_impact(incident.service)
        
        # Blast radius: Depends on service criticality
        blast_radius = self._determine_blast_radius(incident.service)
        
        # Environment criticality: Development = 30, Staging = 50, Production = 70
        environment_criticality = self._determine_environment_criticality(incident)
        
        # Service criticality: Based on severity and service type
        service_criticality = self._determine_service_criticality(incident)
        
        # Calculate weighted risk score using existing Risk Engine
        total_risk = calculate_risk_score(
            action_impact,
            blast_radius,
            environment_criticality,
            service_criticality
        )
        
        return {
            'total_risk': total_risk,
            'action_impact': action_impact,
            'blast_radius_factor': blast_radius,
            'environment_criticality': environment_criticality,
            'service_criticality': service_criticality
        }

    def _determine_action_impact(self, service: str) -> int:
        """Determine action impact score (0-100)"""
        impact_map = {
            'nginx': 50,      # Web service restart affects users
            'redis': 40,      # Cache restart affects performance
            'postgresql': 60, # Database restart affects all services
        }
        return impact_map.get(service, 50)

    def _determine_blast_radius(self, service: str) -> int:
        """Determine blast radius factor (0-100)"""
        radius_map = {
            'nginx': 40,      # Affects frontend users
            'redis': 50,      # Affects caching layer
            'postgresql': 80, # Affects all dependent services
        }
        return radius_map.get(service, 50)

    def _determine_environment_criticality(self, incident: Incident) -> int:
        """Determine environment criticality (0-100)"""
        # Development environment
        return 30

    def _determine_service_criticality(self, incident: Incident) -> int:
        """Determine service criticality (0-100) based on severity"""
        severity_map = {
            'critical': 90,
            'high': 70,
            'medium': 50,
            'low': 30
        }
        return severity_map.get(incident.severity, 50)

    def _classify_risk(self, risk_score: float) -> str:
        """Classify risk score into categories"""
        if risk_score <= 33:
            return 'LOW'
        elif risk_score <= 66:
            return 'MEDIUM'
        else:
            return 'HIGH'

    def _identify_runbook(self, incident: Incident, diagnosis: Dict[str, Any]) -> Optional[str]:
        """Identify appropriate SSM Runbook for remediation"""
        action = diagnosis['diagnosis']['recommended_action']
        
        runbook_map = {
            'restart_service': 'SRE-Copilot-ServiceRestart',
            'increase_memory_or_restart': 'SRE-Copilot-RedisMemoryOptimization',
            'check_upstream_services': 'SRE-Copilot-ServiceHealthCheck',
            'increase_connections_limit': 'SRE-Copilot-ConnectionPoolFix',
            'restart_database_or_increase_connections': 'SRE-Copilot-PostgreSQLRestart',
            'restart_database': 'SRE-Copilot-PostgreSQLRestart',
            'investigate_manually': None
        }
        
        return runbook_map.get(action)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()