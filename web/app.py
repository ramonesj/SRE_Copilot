#!/usr/bin/env python
"""
SRE Copilot MVP - Web UI
FastAPI-based Dashboard for Incident Response

Architecture: Uses existing MVP components without modification
Security: All architectural safety invariants preserved
"""

import sys
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Import MVP components
from alert_ingestion import LocalAlertProvider
from incident_manager import LocalIncidentManager
from evidence_collection import LocalEvidenceCollectionProvider
from diagnosis_engine import LocalDiagnosisProvider
from risk_assessment import LocalRiskAssessmentProvider
from approval import LocalApprovalProvider, ApprovalDecision
from ssm_executor import MockSSMProvider
from verification_engine import LocalVerificationProvider
from audit import LocalAuditLogger
from shared.models import Incident, AuditEvent

app = FastAPI(title="SRE Copilot MVP", version="1.0.0")

# Static and templates setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

# Create static directory if it doesn't exist
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Custom Jinja2 environment to avoid Python 3.14 compatibility issues
jinja_env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(['html', 'xml']),
    cache_size=0  # Disable cache completely
)

templates = Jinja2Templates(directory=templates_dir)
templates.env = jinja_env  # Replace the environment

# Global state for demo
class AppState:
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.evidence: Dict[str, Dict] = {}
        self.diagnoses: Dict[str, Dict] = {}
        self.risk_assessments: Dict[str, Dict] = {}
        self.approval_requests: Dict[str, Any] = {}
        self.executions: Dict[str, Any] = {}
        self.verifications: Dict[str, Any] = {}
        self.audit_events: Dict[str, List[AuditEvent]] = {}
        
    def clear(self):
        self.incidents.clear()
        self.evidence.clear()
        self.diagnoses.clear()
        self.risk_assessments.clear()
        self.approval_requests.clear()
        self.executions.clear()
        self.verifications.clear()
        self.audit_events.clear()

state = AppState()


def get_incident_stats() -> Dict[str, int]:
    """Calculate incident statistics"""
    total = len(state.incidents)
    open_incidents = sum(1 for i in state.incidents.values() if i.status in [
        Incident.CREATED, Incident.EVIDENCE_COLLECTED, Incident.DIAGNOSIS_COMPLETE,
        Incident.RISK_ASSESSED, Incident.APPROVED, Incident.EXECUTING
    ])
    resolved = sum(1 for i in state.incidents.values() if i.status == Incident.RESOLVED)
    rejected = sum(1 for i in state.incidents.values() if i.status == Incident.REJECTED)
    recovery_failed = sum(1 for i in state.incidents.values() if i.status == Incident.RECOVERY_FAILED)
    timeout = sum(1 for i in state.incidents.values() if i.status == Incident.TIMEOUT_EXCEEDED)
    
    return {
        'total': total,
        'open': open_incidents,
        'resolved': resolved,
        'rejected': rejected,
        'recovery_failed': recovery_failed,
        'timeout': timeout
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard with incident statistics"""
    stats = get_incident_stats()
    recent_incidents = sorted(state.incidents.values(), key=lambda i: i.timestamp, reverse=True)[:10]
    
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "stats": stats,
            "incidents": recent_incidents,
            "title": "Dashboard"
        }
    )


@app.get("/incident/{incident_id}", response_class=HTMLResponse)
async def incident_details(request: Request, incident_id: str):
    """Incident details page"""
    incident = state.incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return templates.TemplateResponse(request=request, name="incident.html", context={
        
        "incident": incident,
        "evidence": state.evidence.get(incident_id, {}),
        "diagnosis": state.diagnoses.get(incident_id, {}),
        "risk": state.risk_assessments.get(incident_id, {}),
        "execution": state.executions.get(incident_id),
        "verification": state.verifications.get(incident_id),
        "audit_trail": state.audit_events.get(incident_id, []),
        "title": f"Incident {incident_id}"
    })


@app.get("/approve/{incident_id}", response_class=HTMLResponse)
async def approval_screen(request: Request, incident_id: str):
    """Human-in-the-loop approval interface"""
    incident = state.incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return templates.TemplateResponse(request=request, name="approval.html", context={
        
        "incident": incident,
        "diagnosis": state.diagnoses.get(incident_id, {}),
        "risk": state.risk_assessments.get(incident_id, {}),
        "title": f"Approve {incident_id}"
    })


@app.post("/approve/{incident_id}/decision")
async def process_approval(incident_id: str, decision: str = Form(...)):
    """Process approval decision - maintains security boundaries"""
    incident = state.incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if decision not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Invalid decision")
    
    approval_request = state.approval_requests.get(incident_id)
    if not approval_request:
        raise HTTPException(status_code=400, detail="No approval request found")
    
    provider = LocalApprovalProvider()
    
    if decision == "APPROVE":
        provider.approve(approval_request)
        incident.status = Incident.APPROVED
        
        # Execute SSM only after approval
        ssm_provider = MockSSMProvider()
        risk = state.risk_assessments.get(incident_id, {})
        _, execution, _ = ssm_provider.execute_ssm_runbook(
            incident,
            risk.get('ssm_runbook', 'SRE-Copilot-ServiceRestart'),
            {
                'instance_id': incident.instance_id or 'i-1234567890abcdef0',
                'service_name': incident.service,
                'region': 'us-east-1',
                'timeout_seconds': 300,
                'environment': 'development'
            }
        )
        state.executions[incident_id] = execution
        
        # Verify health independently
        verification_provider = LocalVerificationProvider(success_probability=1.0)
        verification = verification_provider.verify_health(
            incident_id=incident_id,
            execution_id=execution.execution_id,
            service_name=incident.service,
            node_id=incident.instance_id or 'i-1234567890abcdef0'
        )
        state.verifications[incident_id] = verification
        
        # CRITICAL: SSM success ≠ Recovery verified
        if verification.success:
            incident.status = Incident.RESOLVED
        else:
            incident.status = Incident.RECOVERY_FAILED
    else:  # REJECT
        provider.reject(approval_request)
        incident.status = Incident.REJECTED
        # CRITICAL: NO SSM execution on REJECT - security boundary enforced
    
    return RedirectResponse(url=f"/incident/{incident_id}", status_code=303)


@app.get("/simulate", response_class=HTMLResponse)
async def simulate_screen(request: Request):
    """Simulation interface"""
    return templates.TemplateResponse(request=request, name="simulate.html", context={
        
        "title": "Simulate"
    })


@app.post("/simulate/create")
async def create_simulated_incident(
    service: str = Form(...),
    severity: str = Form(...),
    scenario: str = Form(...),
    node: Optional[str] = Form(None),
    error_message: Optional[str] = Form(None)
):
    """Create simulated incident demonstrating all security boundaries"""
    # Create incident
    alert_provider = LocalAlertProvider()
    custom_message = error_message if error_message else f'{service} failure'
    alert_data = {
        'service': service,
        'severity': severity,
        'message': custom_message,
        'timestamp': datetime.utcnow().isoformat()
    }
    _, alert, _ = alert_provider.ingest_alert(alert_data)
    incident = alert_provider.create_incident_from_alert(alert)
    
    # Set node if provided
    if node:
        incident.instance_id = node
    
    state.incidents[incident.incident_id] = incident
    
    # Collect evidence
    manager = LocalIncidentManager()
    manager.create_incident(incident)
    manager.transition_incident(incident.incident_id, Incident.EVIDENCE_COLLECTED)
    evidence_provider = LocalEvidenceCollectionProvider()
    _, evidence, _ = evidence_provider.collect_evidence(incident)
    state.evidence[incident.incident_id] = evidence
    
    # Generate diagnosis
    manager.transition_incident(incident.incident_id, Incident.DIAGNOSIS_COMPLETE)
    diagnosis_provider = LocalDiagnosisProvider()
    _, diagnosis, _ = diagnosis_provider.analyze(incident, evidence)
    state.diagnoses[incident.incident_id] = diagnosis
    
    # Assess risk
    manager.transition_incident(incident.incident_id, Incident.RISK_ASSESSED)
    risk_provider = LocalRiskAssessmentProvider()
    _, risk, _ = risk_provider.assess_risk(incident, diagnosis)
    state.risk_assessments[incident.incident_id] = risk
    
    # Create approval request
    approval_provider = LocalApprovalProvider()
    _, approval_request, _ = approval_provider.create_approval_request(incident, risk)
    state.approval_requests[incident.incident_id] = approval_request
    
    # Handle scenarios preserving all security boundaries
    if scenario == "AUTO_APPROVE":
        incident.status = Incident.APPROVED
        ssm_provider = MockSSMProvider()
        _, execution, _ = ssm_provider.execute_ssm_runbook(incident, risk.get('ssm_runbook', 'SRE-Copilot-ServiceRestart'), {'instance_id': incident.instance_id or 'i-1234567890abcdef0', 'service_name': incident.service, 'region': 'us-east-1', 'timeout_seconds': 300, 'environment': 'development'})
        state.executions[incident.incident_id] = execution
        verification_provider = LocalVerificationProvider(success_probability=1.0)
        verification = verification_provider.verify_health(incident_id=incident.incident_id, execution_id=execution.execution_id, service_name=incident.service, node_id=incident.instance_id or 'i-1234567890abcdef0')
        state.verifications[incident.incident_id] = verification
        incident.status = Incident.RESOLVED if verification.success else Incident.RECOVERY_FAILED
    elif scenario == "AUTO_REJECT":
        incident.status = Incident.REJECTED
        # NO SSM EXECUTION - Security boundary
    elif scenario == "AUTO_TIMEOUT":
        incident.status = Incident.TIMEOUT_EXCEEDED
        # NO SSM EXECUTION - Security boundary
    elif scenario == "AUTO_RECOVERY_FAILED":
        incident.status = Incident.APPROVED
        ssm_provider = MockSSMProvider()
        _, execution, _ = ssm_provider.execute_ssm_runbook(incident, risk.get('ssm_runbook', 'SRE-Copilot-ServiceRestart'), {'instance_id': incident.instance_id or 'i-1234567890abcdef0', 'service_name': incident.service, 'region': 'us-east-1', 'timeout_seconds': 300, 'environment': 'development'})
        state.executions[incident.incident_id] = execution
        verification_provider = LocalVerificationProvider(success_probability=0.0)
        verification = verification_provider.verify_health(incident_id=incident.incident_id, execution_id=execution.execution_id, service_name=incident.service, node_id=incident.instance_id or 'i-1234567890abcdef0')
        state.verifications[incident.incident_id] = verification
        incident.status = Incident.RECOVERY_FAILED
    
    return RedirectResponse(url=f"/incident/{incident.incident_id}", status_code=303)


@app.get("/audit/{incident_id}", response_class=HTMLResponse)
async def audit_trail(request: Request, incident_id: str):
    """Audit trail viewer"""
    incident = state.incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return templates.TemplateResponse(request=request, name="audit.html", context={
        
        "incident": incident,
        "audit_events": state.audit_events.get(incident_id, []),
        "title": f"Audit {incident_id}"
    })


@app.post("/clear")
async def clear_data():
    """Clear demo data"""
    state.clear()
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
