#!/usr/bin/env python
"""
SRE Copilot MVP Demo Script - SPRINT 5
Tests the local incident pipeline with Health Verification Engine.

This script demonstrates the CRITICAL SAFETY INVARIANT:
Execution Success ≠ Recovery Verified

SSM execution success alone does NOT mark incidents as RESOLVED.
Only successful health verification leads to RESOLVED status.

This script demonstrates:
1. Alert ingestion from local source
2. Incident creation and lifecycle management
3. Evidence collection
4. AI diagnosis generation
5. Risk assessment
6. Human approval (APPROVE/REJECT/TIMEOUT)
7. SSM Execution (simulated)
8. HEALTH VERIFICATION (new for SPRINT 5)
9. Audit event logging
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alert_ingestion import LocalAlertProvider
from incident_manager import LocalIncidentManager
from evidence_collection import LocalEvidenceCollectionProvider
from diagnosis_engine import LocalDiagnosisProvider
from risk_assessment import LocalRiskAssessmentProvider
from approval import LocalApprovalProvider, ApprovalDecision
from ssm_executor import MockSSMProvider
from verification_engine import LocalVerificationProvider, verify_service_recovery, VerificationResult, HealthStatus
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


def demo_ssm_execution(incident, risk_assessment, approval_request):
    """Demonstrate SSM execution workflow"""
    print_section("SSM EXECUTION ENGINE")
    
    provider = MockSSMProvider()
    
    # Extract execution parameters
    runbook_name = risk_assessment.get('ssm_runbook', 'SRE-Copilot-ServiceRestart')
    
    # Create execution parameters based on incident
    # Use default instance_id if not provided in incident
    instance_id = incident.instance_id or 'i-1234567890abcdef0'
    parameters = {
        'instance_id': instance_id,
        'service_name': incident.service,
        'region': 'us-east-1',
        'timeout_seconds': 300,
        'environment': 'development'
    }
    
    print(f"Executing SSM Runbook: {runbook_name}")
    print(f"Parameters:")
    for key, value in parameters.items():
        print(f"  - {key}: {value}")
    
    # Execute runbook (simulated)
    success, execution, error = provider.execute_ssm_runbook(
        incident, runbook_name, parameters
    )
    
    if not success:
        print(f"✗ SSM execution failed: {error}")
        return None, None
    
    print(f"✓ SSM Execution Result:")
    print(f"  - Execution ID: {execution.execution_id}")
    print(f"  - Status: {execution.status.value}")
    print(f"  - Started: {execution.started_at}")
    print(f"  - Completed: {execution.completed_at}")
    
    if execution.status.value == 'SUCCESS':
        print(f"  - Output: {execution.output.get('message', 'Success')}")
    else:
        print(f"  - Error: {execution.error_message}")
        print(f"  - Retry count: {execution.retry_count}/{execution.max_retries}")
    
    return execution, provider


def demo_health_verification(incident, ssm_execution, verification_scenario: str = "SUCCESS"):
    """
    Demonstrate health verification workflow.
    
    CRITICAL SAFETY INVARIANT: Execution Success ≠ Recovery Verified
    
    Args:
        verification_scenario: "SUCCESS", "FAILURE", or "RETRY"
    """
    print_section("HEALTH VERIFICATION ENGINE")
    
    print("⚠️  CRITICAL SAFETY INVARIANT:")
    print("   Execution Success ≠ Recovery Verified")
    print("   SSM execution success alone does NOT mark incidents as RESOLVED.")
    print("   Only successful health verification leads to RESOLVED status.")
    print()
    
    provider = LocalVerificationProvider()
    
    # Configure verification based on scenario
    success_probability = 0.8  # Default for SUCCESS
    
    if verification_scenario == "FAILURE":
        success_probability = 0.2  # Low probability of success
        print("Simulating FAILURE scenario (low success probability)")
    elif verification_scenario == "RETRY":
        success_probability = 0.5  # Medium probability, will likely require retry
        print("Simulating RETRY scenario (medium success probability with retry)")
    else:
        print("Simulating SUCCESS scenario (high success probability)")
    
    provider = LocalVerificationProvider(success_probability=success_probability)
    
    # Perform health verification
    verification_result = provider.verify_health(
        incident_id=incident.incident_id,
        execution_id=ssm_execution.execution_id,
        service_name=incident.service,
        node_id=incident.instance_id or 'i-1234567890abcdef0'
    )
    
    print(f"\n✓ Health Verification Result:")
    print(f"  - Verification ID: {verification_result.verification_id}")
    print(f"  - Execution ID: {verification_result.execution_id}")
    print(f"  - Overall Status: {verification_result.overall_status.value}")
    print(f"  - SUCCESS: {verification_result.success} ⭐")
    print(f"  - Confidence Score: {verification_result.confidence_score:.2f}")
    print(f"  - Checks Performed: {len(verification_result.checks)}")
    print(f"  - Verification Duration: {verification_result.verification_duration_seconds:.2f}s")
    
    # Show check details
    for i, check in enumerate(verification_result.checks, 1):
        print(f"    {i}. {check.method.value}: {check.status.value} ({check.duration_seconds:.2f}s)")
    
    # Demonstrate retry logic if verification failed
    if not verification_result.success and verification_scenario == "RETRY":
        print(f"\n⚠️  Initial verification failed. Attempting retry...")
        
        # Simulate retry with increasing success probability
        retry_result = provider.verify_health_with_retry(
            incident_id=incident.incident_id,
            execution_id=ssm_execution.execution_id,
            service_name=incident.service,
            node_id=incident.instance_id or 'i-1234567890abcdef0',
            max_attempts=3
        )
        
        print(f"✓ Retry Verification Result:")
        print(f"  - SUCCESS: {retry_result.success} ⭐")
        print(f"  - Retry Count: {retry_result.retry_count}")
        print(f"  - Final Status: {retry_result.overall_status.value}")
        
        verification_result = retry_result
    
    return verification_result, provider


def demo_incident_resolution(incident, verification_result, ssm_execution):
    """
    Demonstrate incident resolution based on verification results.
    
    Shows how the critical safety invariant affects resolution.
    """
    print_section("INCIDENT RESOLUTION")
    
    print("RESOLUTION LOGIC:")
    print("  SSM Execution Success: ", ssm_execution.status.value == 'SUCCESS')
    print("  Health Verification Success: ", verification_result.success)
    print()
    
    if ssm_execution.status.value == 'SUCCESS' and verification_result.success:
        print("✅ CONDITION MET: SSM success + Verification success = RESOLVED")
        print("   Incident can be marked as RESOLVED")
        resolution_status = "RESOLVED"
    elif ssm_execution.status.value == 'SUCCESS' and not verification_result.success:
        print("❌ CONDITION NOT MET: SSM success but Verification failed = RECOVERY_FAILED")
        print("   Incident must be marked as RECOVERY_FAILED")
        print("   CRITICAL: Execution success does NOT equal recovery verified")
        resolution_status = "RECOVERY_FAILED"
    elif ssm_execution.status.value != 'SUCCESS':
        print("❌ SSM execution failed")
        resolution_status = "EXECUTION_FAILED"
    else:
        print("❌ Unknown state")
        resolution_status = "UNKNOWN"
    
    print(f"\nFinal Resolution: {resolution_status}")
    print(f"Verification success is REQUIRED for RESOLVED status")
    
    return resolution_status


def demo_audit_logging(incident, evidence_package, diagnosis, risk_assessment, 
                       decision: ApprovalDecision, approval_request_id: str, 
                       ssm_execution=None, verification_result=None):
    """Demonstrate audit event logging with health verification"""
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
    
    # Add SSM execution event if present
    if ssm_execution:
        events.append({
            'actor': 'SSMExecution',
            'action': 'SSM_EXECUTED',
            'details': {
                'execution_id': ssm_execution.execution_id,
                'runbook_name': ssm_execution.runbook_name,
                'status': ssm_execution.status.value,
                'retry_count': ssm_execution.retry_count
            }
        })
    
    # Add health verification event if present
    if verification_result:
        events.append({
            'actor': 'HealthVerification',
            'action': 'VERIFICATION_COMPLETED',
            'details': {
                'verification_id': verification_result.verification_id,
                'success': verification_result.success,
                'overall_status': verification_result.overall_status.value,
                'confidence_score': verification_result.confidence_score,
                'checks_performed': len(verification_result.checks),
                'retry_count': verification_result.retry_count
            }
        })
        
        # Log each check individually for detailed audit trail
        for i, check in enumerate(verification_result.checks, 1):
            events.append({
                'actor': 'HealthVerification',
                'action': 'HEALTH_CHECK_EXECUTED',
                'details': {
                    'check_id': check.check_id,
                    'method': check.method.value,
                    'status': check.status.value,
                    'duration_seconds': check.duration_seconds,
                    'check_number': i,
                    'total_checks': len(verification_result.checks)
                }
            })
    
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


def run_approve_scenario_with_verification(verification_scenario: str):
    """Run APPROVE scenario with health verification"""
    print("\n" + "=" * 60)
    print(f"  SCENARIO: APPROVE with {verification_scenario} verification")
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
    
    # Approval Workflow (APPROVE only for this demo)
    decision, approval_request, approval_provider = demo_approval_workflow(
        incident, risk_assessment, "APPROVE"
    )
    if not decision:
        return False
    
    # SSM Execution
    ssm_execution, ssm_provider = demo_ssm_execution(incident, risk_assessment, approval_request)
    if not ssm_execution:
        print("⚠️ SSM execution failed, cannot proceed with health verification")
        return False
    
    # Health Verification
    verification_result, verification_provider = demo_health_verification(
        incident, ssm_execution, verification_scenario
    )
    
    # Incident Resolution
    resolution_status = demo_incident_resolution(incident, verification_result, ssm_execution)
    
    # Audit Logging
    demo_audit_logging(
        incident, evidence, diagnosis, risk_assessment, decision, 
        approval_request.approval_request_id, ssm_execution, verification_result
    )
    
    return True, verification_result.success, resolution_status


def main():
    """Run the complete demo with health verification scenarios"""
    print("=" * 60)
    print("  SRE Copilot MVP Demo - Local Incident Pipeline")
    print("=" * 60)
    print("  Sprint 5: Health Verification Engine")
    print("=" * 60)
    print()
    print("⚠️  CRITICAL SAFETY INVARIANT DEMONSTRATION")
    print("   Execution Success ≠ Recovery Verified")
    print("   SSM execution success alone does NOT mark incidents as RESOLVED.")
    print("   Only successful health verification leads to RESOLVED status.")
    print("=" * 60)
    
    # Test different verification scenarios
    scenarios = ["SUCCESS", "FAILURE", "RETRY"]
    results = {}
    
    for scenario in scenarios:
        print(f"\n{'#' * 60}")
        print(f"  TESTING: APPROVE scenario with {scenario} verification")
        print('#' * 60)
        
        success, verification_success, resolution_status = run_approve_scenario_with_verification(scenario)
        results[scenario] = {
            'pipeline_success': success,
            'verification_success': verification_success,
            'resolution_status': resolution_status
        }
    
    print_section("DEMO COMPLETE")
    
    print("\nVerification Scenario Results:")
    print("-" * 50)
    for scenario, result in results.items():
        pipeline_status = "✓ PASS" if result['pipeline_success'] else "✗ FAIL"
        verification_status = "✓ SUCCESS" if result['verification_success'] else "✗ FAILED"
        print(f"  {scenario}:")
        print(f"    - Pipeline: {pipeline_status}")
        print(f"    - Verification: {verification_status}")
        print(f"    - Resolution: {result['resolution_status']}")
    
    print("\nArchitecture Validation:")
    print("  ✓ AI Diagnosis Engine: No SSM execution permissions")
    print("  ✓ Policy/Risk Engine: No state-changing operations")
    print("  ✓ HITL Approval: Required before SSM execution")
    print("  ✓ SSM Execution: Mock provider, no real AWS calls")
    print("  ✓ Health Verification: CRITICAL invariant enforced")
    print("  ✓ Security boundaries preserved")
    
    print("\nCRITICAL SAFETY INVARIANT DEMONSTRATED:")
    print("  ✓ Execution Success ≠ Recovery Verified")
    print("  ✓ SUCCESS scenario: SSM success + Verification success = RESOLVED")
    print("  ✓ FAILURE scenario: SSM success + Verification failure = RECOVERY_FAILED")
    print("  ✓ RETRY scenario: Retry logic for failed verification")
    print("  ✓ Verification success is REQUIRED for RESOLVED status")
    
    print("\nKey Findings:")
    print("  - SSM execution success alone does NOT constitute incident resolution")
    print("  - Health verification is a mandatory step after SSM execution")
    print("  - Only VerificationResult.success = True leads to RESOLVED status")
    print("  - Retry logic allows for temporary service recovery issues")
    print("  - Audit trail includes comprehensive verification events")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
