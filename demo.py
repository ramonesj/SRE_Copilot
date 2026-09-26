#!/usr/bin/env python
"""
SRE Copilot MVP Demo Script
Tests the local incident pipeline without AWS dependencies.

This script demonstrates:
1. Alert ingestion from local source
2. Incident creation and lifecycle management
3. Evidence collection
4. AI diagnosis generation
5. Audit event logging
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alert_ingestion import LocalAlertProvider
from incident_manager import LocalIncidentManager
from evidence_collection import LocalEvidenceCollectionProvider
from diagnosis_engine import LocalDiagnosisProvider
from audit import LocalAuditLogger
from shared.models import Incident


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def demo_alert_ingestion():
    """Demonstrate alert ingestion workflow"""
    print_section("ALERT INGESTION")
    
    provider = LocalAlertProvider()
    
    # Load sample alerts
    sample_alerts = provider.load_sample_alerts()
    
    print(f"Loaded {len(sample_alerts)} sample alerts")
    
    # Process first alert
    alert_data = sample_alerts[0]
    print(f"\nProcessing alert: {alert_data['service']} - {alert_data['severity']}")
    
    success, alert, error = provider.ingest_alert(alert_data)
    if success:
        print(f"✓ Alert validated: {alert.service} ({alert.severity})")
    else:
        print(f"✗ Alert validation failed: {error}")
        return None
    
    # Create incident from alert
    incident = provider.create_incident_from_alert(alert)
    print(f"✓ Incident created: {incident.incident_id}")
    
    return incident


def demo_incident_manager(incident):
    """Demonstrate incident lifecycle management"""
    print_section("INCIDENT MANAGER")
    
    manager = LocalIncidentManager()
    
    # Create incident
    success, incident, error = manager.create_incident(incident)
    if success:
        print(f"✓ Incident saved: {incident.incident_id}")
    else:
        print(f"✗ Failed to create incident: {error}")
        return None
    
    # Get incident back
    retrieved = manager.get_incident(incident.incident_id)
    print(f"✓ Retrieved incident: {retrieved.service} - {retrieved.status}")
    
    # Transition to evidence collected state
    success, updated, error = manager.transition_incident(
        incident.incident_id,
        Incident.EVIDENCE_COLLECTED
    )
    if success:
        print(f"✓ State transition: {updated.status}")
    else:
        print(f"✗ State transition failed: {error}")
    
    return updated


def demo_evidence_collection(incident):
    """Demonstrate evidence collection workflow"""
    print_section("EVIDENCE COLLECTION")
    
    provider = LocalEvidenceCollectionProvider()
    
    # Collect evidence
    success, evidence, error = provider.collect_evidence(incident)
    if success:
        print(f"✓ Evidence collected: {len(evidence['logs'])} log entries")
        print(f"✓ Evidence type: {evidence['evidence_type']}")
        print(f"✓ Service metadata: {evidence['metadata']['service_name']}")
    else:
        print(f"✗ Evidence collection failed: {error}")
        return None
    
    return evidence


def demo_diagnosis_engine(incident, evidence_package):
    """Demonstrate diagnosis engine workflow"""
    print_section("DIAGNOSIS ENGINE")
    
    provider = LocalDiagnosisProvider()
    
    # Analyze incident
    success, diagnosis, error = provider.analyze(incident, evidence_package)
    if success:
        diag = diagnosis['diagnosis']
        print(f"✓ Diagnosis generated:")
        print(f"  - Summary: {diag['summary']}")
        print(f"  - Confidence: {diag['confidence']}")
        print(f"  - Root cause: {diag['root_cause']['cause_type']}")
        print(f"  - Recommended action: {diag['recommended_action']}")
        print(f"  - Evidence: {len(diag['evidence'])} data points")
    else:
        print(f"✗ Diagnosis failed: {error}")
        return None
    
    return diagnosis


def demo_audit_logging(incident, evidence_package, diagnosis):
    """Demonstrate audit event logging"""
    print_section("AUDIT LOGGER")
    
    logger = LocalAuditLogger()
    
    # Log various audit events
    events = [
        {
            'actor': 'AlertIngestion',
            'action': 'INCIDENT_CREATED',
            'details': {'service': incident.service, 'severity': incident.severity}
        },
        {
            'actor': 'EvidenceCollection',
            'action': 'EVIDENCE_COLLECTED',
            'details': {'source': 'CloudWatch', 'log_count': evidence_package['total_log_lines']}
        },
        {
            'actor': 'DiagnosisEngine',
            'action': 'DIAGNOSIS_GENERATED',
            'details': {'summary': diagnosis['diagnosis']['summary'], 'confidence': diagnosis['diagnosis']['confidence']}
        }
    ]
    
    for event_data in events:
        from shared.models import AuditEvent
        
        audit_event = AuditEvent(
            event_id=f"evt-{hash(str(event_data))}",
            timestamp=incident.timestamp,
            actor=event_data['actor'],
            action=event_data['action'],
            details=event_data['details'],
            incident_id=incident.incident_id
        )
        
        if logger.log_event(audit_event):
            print(f"✓ Logged: {audit_event.action} by {audit_event.actor}")
        else:
            print(f"✗ Failed to log: {audit_event.action}")
    
    # Retrieve events
    retrieved_events = logger.get_events_by_incident(incident.incident_id)
    print(f"\n✓ Retrieved {len(retrieved_events)} audit events for incident")


def main():
    """Run the complete demo"""
    print("=" * 60)
    print("  SRE Copilot MVP Demo - Local Incident Pipeline")
    print("=" * 60)
    print("  Sprint 2: Evidence Collection + Diagnosis Engine")
    print("=" * 60)
    
    try:
        # Run demo steps
        incident = demo_alert_ingestion()
        if incident:
            incident = demo_incident_manager(incident)
            if incident:
                evidence = demo_evidence_collection(incident)
                if evidence:
                    diagnosis = demo_diagnosis_engine(incident, evidence)
                    if diagnosis:
                        demo_audit_logging(incident, evidence, diagnosis)
        
        print_section("DEMO COMPLETE")
        print("✓ All components working locally")
        print("✓ No AWS dependencies required")
        print("\nNext steps: Implement Risk Assessment and HITL Approval")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())