# HITL Review Skill

**Purpose**: Review and validate Human-in-the-Loop architectures.

## Security Invariant

Always enforce:

**AI recommends. Policy evaluates. Human authorizes. Automation executes. System verifies. Audit records.**

## Validation Checklist

### 1. State-Changing Operations

- [ ] All state-changing operations require explicit human approval
- [ ] No component may bypass the HITL approval boundary
- [ ] AI/LLM components can ONLY diagnose, analyze, and recommend - NEVER execute changes directly

### 2. Security Invariants

- [ ] **REJECT => NO SSM**: REJECT decision must never trigger SSM execution
- [ ] **TIMEOUT => NO SSM**: TIMEOUT must never trigger SSM execution
- [ ] **RESOLVED => Health Verification SUCCESS**: Only verified recovery leads to RESOLVED status

### 3. Execution vs Recovery

- [ ] Execution success does NOT equal recovery verified
- [ ] SSM execution success alone does NOT mean RESOLVED
- [ ] Health verification must be independent from execution

### 4. Task Token Security

- [ ] Task Tokens MUST NOT be logged
- [ ] Task Tokens MUST NOT appear in user-facing interfaces
- [ ] Task Tokens MUST NOT be included in EventBridge events
- [ ] Task Tokens MUST be accessible only by authorized callback component
- [ ] Task Tokens MUST remain protected at rest if persisted

### 5. IAM Role Separation

- [ ] AI Diagnosis Engine has NO SSM permissions (no ssm:StartExecution, ssm:SendCommand)
- [ ] Policy/Risk Engine has NO execution permissions
- [ ] Execution Engine has NO diagnostic permissions
- [ ] Each component follows least-privilege principle

### 6. Auditability

- [ ] All events recorded in immutable audit trail
- [ ] All decisions, recommendations, approvals, and actions logged
- [ ] Audit trail supports compliance and post-incident analysis

## HITL Architecture Requirements

### 1. Approval Workflow

- [ ] Step Functions pauses with Task Token callback
- [ ] APPROVE triggers remediation execution
- [ ] REJECT updates status to REMEDIATION_REJECTED
- [ ] TIMEOUT updates status to TIMEOUT_EXCEEDED

### 2. Component Separation

- [ ] AI Diagnosis Engine: Read-only access (Bedrock, logs, evidence)
- [ ] Policy/Risk Engine: Read-only access (risk calculation, Runbook identification)
- [ ] HITL Approval: Manages approval lifecycle and callback
- [ ] Execution Engine: SSM runbook execution only
- [ ] Verification Engine: Health verification after remediation

### 3. Step Functions Pattern

- [ ] Uses Task Token callback pattern for async human approval
- [ ] Workflow uses `.waitForTaskToken` integration
- [ ] Task Token is available in `$$.Task.Token` context
- [ ] External system calls `SendTaskSuccess` (APPROVE) or `SendTaskFailure` (REJECT)

## AWS Documentation

When validating AWS Step Functions implementations:

1. Use `aws-docs` MCP server for:
   - Step Functions callback pattern documentation
   - Task Token API reference (SendTaskSuccess, SendTaskFailure)
   - Error handling (Retry, Catch)
   - Service integration patterns

## Output Format

After validation, return:

```
HITL Architecture Review: [PASS/FAIL]

[Specific findings, concerns, and recommendations]
```