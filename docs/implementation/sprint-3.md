# SPRINT 3: Risk Assessment + HITL Approval

## Objective

Implement Risk Assessment and Human-in-the-Loop Approval modules for the local MVP.

Demonstrate three approval paths:
1. APPROVE - Continue workflow
2. REJECT - Stop progression (REMEDIATION_REJECTED)
3. TIMEOUT - Stop progression (TIMEOUT_EXCEEDED)

## Architecture

### Risk Assessment Engine

**Module**: `src/risk_assessment/`

**Provider**: `LocalRiskAssessmentProvider`

**Purpose**: Integrates existing Risk Engine to evaluate remediation risk.

**Risk Calculation**:
- Action Impact (0-100)
- Blast Radius Factor (0-100)
- Environment Criticality (0-100)
- Service Criticality (0-100)

**Weighted Formula**:
```
remediation_risk = (
    action_impact * 0.25 +
    blast_radius_factor * 0.25 +
    environment_criticality * 0.25 +
    service_criticality * 0.25
)
```

**Risk Classification**:
- LOW: 0-33
- MEDIUM: 34-66
- HIGH: 67-100

### HITL Approval Service

**Module**: `src/approval/`

**Providers**: `LocalApprovalProvider`

**Models**:
- `ApprovalDecision` (PENDING, APPROVED, REJECTED, TIMEOUT)
- `ApprovalRequest` (approval request record)
- `ApprovalResponse` (approval response record)

**Methods**:
- `create_approval_request()` - Create request record
- `approve()` - Approve request
- `reject()` - Reject request
- `timeout()` - Mark request as timeout

## Files Created

```
src/
├── risk_assessment/
│   ├── __init__.py
│   └── local_provider.py
└── approval/
    ├── __init__.py
    ├── models.py
    └── local_provider.py
```

## Approval Model

### ApprovalDecision Enum

| Value | Description |
|-------|-------------|
| PENDING | Request created, awaiting decision |
| APPROVED | Request approved, workflow continues |
| REJECTED | Request rejected, workflow stops |
| TIMEOUT | Request timed out, workflow stops |

### ApprovalRequest Dataclass

| Field | Description |
|-------|-------------|
| approval_request_id | Unique request identifier |
| incident_id | Associated incident |
| created_at | Request creation timestamp |
| diagnosis_summary | Summary from diagnosis engine |
| confidence_score | AI confidence (0.0-1.0) |
| remediation_risk | Risk score (0-100) |
| risk_classification | LOW/MEDIUM/HIGH |
| recommended_action | Suggested remediation action |
| ssm_runbook | Suggested SSM runbook |
| decision | ApprovalDecision enum |
| decision_at | Decision timestamp |
| approver | Decision actor |
| rationale | Decision reason |

### ApprovalResponse Dataclass

| Field | Description |
|-------|-------------|
| approval_request_id | Request identifier |
| decision | ApprovalDecision enum |
| timestamp | Decision timestamp |
| approver | Decision actor |
| rationale | Decision reason |
| incident_id | Associated incident |

## Audit Events

| Event | Actor | Description |
|-------|-------|-------------|
| INCIDENT_CREATED | AlertIngestion | Incident record created |
| EVIDENCE_COLLECTED | EvidenceCollection | Evidence package collected |
| DIAGNOSIS_GENERATED | DiagnosisEngine | Diagnosis generated |
| RISK_ASSESSED | RiskAssessment | Risk calculated |
| APPROVAL_REQUESTED | HITLApproval | Approval request created |

## Test Results

### Python Syntax Validation
```
✓ src/risk_assessment/__init__.py - Syntax OK
✓ src/risk_assessment/local_provider.py - Syntax OK
✓ src/approval/__init__.py - Syntax OK
✓ src/approval/models.py - Syntax OK
✓ src/approval/local_provider.py - Syntax OK
✓ demo.py - Syntax OK
```

### Demo Script Execution

All three scenarios passed:

**APPROVE SCENARIO**:
```
✓ Alert validated: nginx (critical)
✓ Incident created: inc-xxx
✓ State transition: EVIDENCE_COLLECTED
✓ Evidence collected: 5 log entries
✓ Diagnosis generated: Service crash detected (confidence: 0.92)
✓ Risk assessed: 52.5 (MEDIUM)
✓ APPROVED: req-xxx
✓ 5 audit events logged
```

**REJECT SCENARIO**:
```
✓ Alert validated: nginx (critical)
✓ Incident created: inc-xxx
✓ State transition: EVIDENCE_COLLECTED
✓ Evidence collected: 5 log entries
✓ Diagnosis generated: Service crash detected (confidence: 0.92)
✓ Risk assessed: 52.5 (MEDIUM)
✗ REJECTED: req-xxx
✓ 5 audit events logged
```

**TIMEOUT SCENARIO**:
```
✓ Alert validated: nginx (critical)
✓ Incident created: inc-xxx
✓ State transition: EVIDENCE_COLLECTED
✓ Evidence collected: 5 log entries
✓ Diagnosis generated: Service crash detected (confidence: 0.92)
✓ Risk assessed: 52.5 (MEDIUM)
✗ TIMEOUT: req-xxx
✓ 5 audit events logged
```

### Scenario Results

| Scenario | Result | Notes |
|----------|--------|-------|
| APPROVE | ✓ PASS | Workflow continues |
| REJECT | ✓ PASS | Workflow stops, REMEDIATION_REJECTED |
| TIMEOUT | ✓ PASS | Workflow stops, TIMEOUT_EXCEEDED |

## Demo Results

**Total Scenarios**: 3
**Passed**: 3
**Failed**: 0

**Files Modified**:
- `demo.py` - Updated with Risk and Approval modules

**Data Created**:
- `data/risk_assessment/` - Risk assessment results
- `data/approvals/` - Approval request records

## Remaining Work

- SSM Executor (Execution Engine)
- Health Verification Engine
- Complete end-to-end workflow with all components