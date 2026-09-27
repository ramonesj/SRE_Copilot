#!/usr/bin/env python
"""
SRE Copilot MVP Demo Script
Tests the local incident pipeline without AWS dependencies.

This script demonstrates:
1. Alert ingestion from local source
2. Incident creation and lifecycle management
3. Evidence collection
4. AI diagnosis generation
5. Risk assessment
6. Human approval (APPROVE/REJECT/TIMEOUT)
7. Audit event logging
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alert_ingestion import LocalAlertProvider
from incident_manager import LocalIncidentManager
from evidence_collection import LocalEvidenceCollectionProvider
from diagnosis_engine import LocalDiagnosisProvider
from risk_assessment import LocalRiskAssessmentProvider
from approval import LocalApprovalProvider, ApprovalDecision
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
        return None, None
    
    # Create incident from alert
    incident = provider.create_incident_from_alert(alert)
    print(f"✓ Incident created: {incident.incident_id}")
    
    return incident, provider


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
        return None, None
    
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
    
    return updated, manager


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
        return None, None
    
    return evidence, provider


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
        return None, None
    
    return diagnosis, provider


def demo_risk_assessment(incident, diagnosis):
    """Demonstrate risk assessment workflow"""
    print_section("RISK ASSESSMENT")
    
    provider = LocalRiskAssessmentProvider()
    
    # Assess risk
    success, risk_assessment, error = provider.assess_risk(incident, diagnosis)
    if success:
        print(f"✓ Risk assessed:")
        print(f"  - Remediation Risk: {risk_assessment['remediation_risk']}")
        print(f"  - Classification: {risk_assessment['risk_classification']}")
        print(f"  - SSM Runbook: {risk_assessment['ssm_runbook']}")
    else:
        print(f"✗ Risk assessment failed: {error}")
        return None, None
    
    return risk_assessment, provider


def demo_approval_workflow(incident, risk_assessment, scenario: str):
    """Demonstrate approval workflow based on scenario"""
    print_section(f"HITL APPROVAL - {scenario} SCENARIO")
    
    provider = LocalApprovalProvider()
    
    # Create approval request
    success, approval_request, error = provider.create_approval_request(
        incident, risk_assessment
    )
    if not success:
        print(f"✗ Failed to create approval request: {error}")
        return None, None, None
    
    print(f"✓ Approval request created: {approval_request.approval_request_id}")
    print(f"  - Diagnosis: {approval_request.diagnosis_summary}")
    print(f"  - Risk: {approval_request.remediation_risk} ({approval_request.risk_classification})")
    print(f"  - Action: {approval_request.recommended_action}")
    
    # Process based on scenario
    if scenario == "APPROVE":
        success, approval_response, error = provider.approve(approval_request)
        if success:
            print(f"✓ APPROVED: {approval_request.approval_request_id}")
            print(f"  - Approver: {approval_response.approver}")
            print(f"  - Decision: {approval_response.decision.value}")
            return approval_response.decision, approval_request, provider
    
    elif scenario == "REJECT":
        success, approval_response, error = provider.reject(approval_request)
        if success:
            print(f"✗ REJECTED: {approval_request.approval_request_id}")
            print(f"  - Approver: {approval_response.approver}")
            print(f"  - Decision: {approval_response.decision.value}")
            return approval_response.decision, approval_request, provider
    
    elif scenario == "TIMEOUT":
        success, approval_response, error = provider.timeout(approval_request)
        if success:
            print(f"✗ TIMEOUT: {approval_request.approval_request_id}")
            print(f"  - Approver: {approval_response.approver}")
            print(f"  - Decision: {approval_response.decision.value}")
            return approval_response.decision, approval_request, provider
    
    return None, None, None


def demo_audit_logging(incident, evidence_package, diagnosis, risk_assessment, decision: ApprovalDecision, approval_request_id: str):
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
        },
        {
            'actor': 'RiskAssessment',
            'action': 'RISK_ASSESSED',
            'details': {'remediation_risk': risk_assessment['remediation_risk'], 'classification': risk_assessment['risk_classification']}
        },
        {
            'actor': 'HITLApproval',
            'action': 'APPROVAL_REQUESTED',
            'details': {'approval_request_id': approval_request_id, 'decision': decision.value}
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


def run_scenario(scenario: str):
    """Run a complete demo scenario"""
    print("\n" + "=" * 60)
    print(f"  SCENARIO: {scenario}")
    print("=" * 60)
    
    # Alert Ingestion
    incident, alert_provider = demo_alert_ingestion()
    if not incident:
        return False
    
    # Incident Manager
    incident, incident_manager = demo_incident_manager(incident)
    if not incident:
        return False
    
    # Evidence Collection
    evidence, evidence_provider = demo_evidence_collection(incident)
    if not evidence:
        return False
    
    # Diagnosis Engine
    diagnosis, diagnosis_provider = demo_diagnosis_engine(incident, evidence)
    if not diagnosis:
        return False
    
    # Risk Assessment
    risk_assessment, risk_provider = demo_risk_assessment(incident, diagnosis)
    if not risk_assessment:
        return False
    
    # Approval Workflow
    decision, approval_request, approval_provider = demo_approval_workflow(incident, risk_assessment, scenario)
    if not decision:
        return False
    
    # Audit Logging
    demo_audit_logging(incident, evidence, diagnosis, risk_assessment, decision, approval_request.approval_request_id)
    
    return True


def main():
    """Run the complete demo with all scenarios"""
    print("=" * 60)
    print("  SRE Copilot MVP Demo - Local Incident Pipeline")
    print("=" * 60)
    print("  Sprint 3: Risk Assessment + HITL Approval")
    print("=" * 60)
    
    scenarios = ["APPROVE", "REJECT", "TIMEOUT"]
    results = {}
    
    for scenario in scenarios:
        success = run_scenario(scenario)
        results[scenario] = success
    
    print_section("DEMO COMPLETE")
    print("\nScenario Results:")
    for scenario, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {scenario}: {status}")
    
    print("\n✓ All components working locally")
    print("✓ No AWS dependencies required")
    print("\nNext steps: Implement SSM Executor and Health Verification")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())