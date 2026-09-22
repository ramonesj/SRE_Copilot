# Architecture Overview

## Architectural Safety Invariant

The SRE Copilot enforces a strict safety boundary:

- **AI recommends**: The AI Diagnosis Engine analyzes evidence and proposes root causes and remediation actions
- **Policy evaluates**: The Policy/Risk Engine evaluates operational impact and calculates risk scores
- **Human authorizes**: The HITL Approval component provides explicit human authorization for state-changing operations
- **Automation executes**: The Execution Engine executes only pre-authorized actions
- **System verifies**: The Verification Engine checks if remediation achieved desired outcomes
- **Audit records**: The Audit System records all decisions, approvals, executions, and results

**Security Boundary**: AI/LLM components can ONLY diagnose, analyze, and recommend - NEVER execute changes directly.

## Component Responsibilities

### Alert Ingestion
- Receives alert events from EventBridge
- Validates event schema
- Creates incident records in DynamoDB
- Triggers evidence collection

### Incident Manager
- Creates and maintains incident lifecycle
- Manages state transitions
- Coordinates workflow through Step Functions

### Evidence Collection
- Extracts relevant logs from CloudWatch
- Gathers node context and metadata
- Prepares data for AI analysis

### AI Diagnosis Engine
- Analyzes evidence using Bedrock (LLM)
- Generates diagnosis with confidence score
- Identifies probable root cause
- **MUST NOT**: Invoke SSM, modify infrastructure, or perform any state-changing operations
- Uses IAM role for Bedrock access (not Secrets Manager)

### Policy/Risk Engine
- Evaluates operational impact
- Calculates remediation risk score
- Identifies appropriate SSM Runbooks
- **MUST NOT**: Execute remediation actions

### HITL Approval Service
- Sends approval requests to designated channel
- Manages approval lifecycle
- Handles timeout and rejection
- Validates approval tokens before processing responses

### Execution Engine
- Executes approved SSM Runbooks
- Handles execution retry logic
- Reports execution status
- **MUST ONLY**: Execute pre-authorized actions

### Verification Engine
- Performs health verification after remediation
- Uses same monitoring mechanism as original detection
- Determines if service recovery was successful

### Audit System
- Records all events to immutable S3 storage
- Maintains complete audit trail
- Supports compliance and post-incident analysis

## Mandatory Architecture Rules

1. **AI Diagnosis Engine MUST NOT call SSM**: The AI Diagnosis Engine has no permissions to invoke SSM or modify any infrastructure/service state.

2. **Policy/Risk Engine MUST NOT execute remediation**: Risk assessment is read-only; execution is handled by a separate component.

3. **HITL approval MUST occur before every state-changing remediation**: No exceptions regardless of risk level.

4. **Execution Engine may execute only pre-authorized actions**: Only actions approved through the HITL workflow can be executed.

5. **Verification must be independent from execution**: Health verification confirms recovery, not execution completion.

6. **Audit must record all important lifecycle decisions**: Every significant event must be logged.

7. **Step Functions must orchestrate end-to-end workflow**: Centralized workflow coordination.

8. **HITL wait state must use Task Token callback pattern**: Step Functions pauses with Task Token, resumes on callback.

## State Transitions

### Approval Flow
- **APPROVE** → Execution allowed, proceed to SSM Runbook execution
- **REJECT** → Update status to REMEDIATION_REJECTED, NO execution
- **TIMEOUT** → Update status to TIMEOUT_EXCEEDED, NO execution

### Resolution Flow
- **SSM SUCCESS + Health Verify SUCCESS** → RESOLVED
- **SSM SUCCESS + Health Verify FAIL** → RECOVERY_FAILED
- **SSM FAIL** → Update status with error details

**Critical**: Execution success does NOT equal recovery verified. Only Health Verification SUCCESS leads to RESOLVED.

## Incident Lifecycle States

- `CREATED`: Incident record created, evidence collection pending
- `EVIDENCE_COLLECTED`: Evidence gathered, diagnosis pending
- `DIAGNOSIS_COMPLETE`: Diagnosis generated, risk assessment pending
- `RISK_ASSESSED`: Risk assessed, HITL approval pending
- `APPROVED`: Approved for remediation, execution pending
- `EXECUTING`: SSM Runbook execution in progress
- `RECOVERY_VERIFIED`: Health check passed, incident resolved
- `RECOVERY_FAILED`: Health check failed, incident not resolved
- `VERIFICATION_ERROR`: Health check could not be performed
- `REMEDIATION_REJECTED`: Remediation rejected by human approver
- `TIMEOUT_EXCEEDED`: Approval timeout exceeded, no execution
- `DIAGNOSIS_FAILED`: Bedrock analysis failed
- `DIAGNOSIS_TIMEOUT`: Bedrock analysis timed out

## MVP Workflow

```
Service Healthy → Service Failure → Anomaly Detected → Incident Created → 
Evidence Collected → AI Diagnosis → Risk Assessment → HITL Approval → 
SSM Service Remediation → Health Verification → RESOLVED
```

Key MVP characteristics:
- Single scenario: Critical service failure
- Single remediation: Service restart via SSM (not instance restart)
- Health verification required for RESOLVED status