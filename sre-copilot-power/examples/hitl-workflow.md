# HITL Workflow Example

## Complete Incident Response Workflow

```
Incident Detection
    ↓
EventBridge Alert (CloudWatch Alarm)
    ↓
Alert Ingestion Lambda
    ↓
Incident Created (unique incident_id)
    ↓
Evidence Collection Lambda
    ↓
Logs extracted from CloudWatch Logs
    ↓
AI Diagnosis Engine (Bedrock via IAM)
    ↓
Diagnosis generated (root cause + confidence)
    ↓
Policy/Risk Engine
    ↓
Risk score calculated (0-100)
SSM Runbooks identified
    ↓
Step Functions pauses (Task Token callback)
    ↓
Approval Request (Email/Slack/Teams)
    ↓
[Wait for human approval]
    ↓
APPROVE → SSM Executor Lambda → SSM Runbook → Verification Engine → RESOLVED
REJECT → REMEDIATION_REJECTED → NO SSM
TIMEOUT → TIMEOUT_EXCEEDED → NO SSM
```

## APPROVE Path

1. Human approves via callback
2. Step Functions sends `SendTaskSuccess` with decision
3. SSM Executor Lambda invoked
4. SSM Runbook executes (idempotent service restart)
5. Verification Engine checks service health
6. Health check SUCCESS → RESOLVED
7. Audit Logger records all events

## REJECT Path

1. Human rejects via callback
2. Step Functions sends `SendTaskFailure` with decision
3. Incident Manager updates status to REMEDIATION_REJECTED
4. NO SSM execution occurs
5. Audit Logger records all events

## TIMEOUT Path

1. Approval timeout expires (configurable, default 300 seconds)
2. Step Functions triggers States.Timeout error
3. Catch block routes to HandleTimeout state
4. Incident Manager updates status to TIMEOUT_EXCEEDED
5. NO SSM execution occurs
6. Audit Logger records all events

## Task Token Flow

1. Step Functions generates unique Task Token
2. Token stored securely by Approval Lambda (encrypted in Secrets Manager)
3. Approval request sent without token
4. Callback service validates request and retrieves token
5. Callback service calls `SendTaskSuccess` or `SendTaskFailure`
6. Token consumed (invalidated) after first use

## Security Invariants

- REJECT → NO SSM (verified)
- TIMEOUT → NO SSM (verified)
- RESOLVED → Health Verification SUCCESS (verified)
- AI Diagnosis Engine → NO SSM permissions (verified)
- Task Tokens never logged (verified)