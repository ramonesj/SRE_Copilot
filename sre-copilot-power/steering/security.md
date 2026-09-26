# SRE Copilot Security Steering

**Architectural Safety Invariant**:

**AI recommends. Policy evaluates. Human authorizes. Automation executes. System verifies. Audit records.**

## Security Boundaries

### 1. State-Changing Operations

ALL state-changing operations MUST require explicit human approval. No exceptions.

**Never allow**:
- State-changing remediation before explicit human approval
- AI components to execute state-changing operations
- Components to bypass the HITL approval boundary

### 2. Component Responsibilities

#### AI Diagnosis Engine

**Permissions**: Read-only access only
- May access: Bedrock (IAM-based), logs, evidence, CloudWatch
- MUST NOT have: ssm:StartExecution, ssm:SendCommand, or any execution permissions

#### Policy/Risk Engine

**Permissions**: Read-only access only
- May access: SSM Runbooks listing, metrics, service context
- MUST NOT have: Any state-changing or execution permissions

#### Execution Engine

**Permissions**: Execution only (SSM)
- May access: SSM Runbooks execution (ssm:StartExecution, ssm:SendCommand)
- MUST NOT have: Diagnostic or analysis permissions

#### Verification Engine

**Permissions**: Read-only access only
- May access: CloudWatch metrics, health checks
- MUST NOT have: Execution or modification permissions

#### Audit System

**Permissions**: Write-only access to audit storage
- May access: S3 write (audit storage)
- MUST NOT have: Execution or diagnostic permissions

### 3. Task Token Security

**MUST NOT**:
- Log Task Tokens in application logs
- Include Task Tokens in user-facing interfaces
- Include Task Tokens in EventBridge events
- Store Task Tokens in plaintext

**MUST**:
- Protect Task Tokens at rest if persisted
- Validate Task Tokens before processing
- Invalidate Task Tokens after first use

### 4. IAM Role Separation

**MUST enforce strict separation**:
- AI Diagnosis Role: NO SSM permissions
- Execution Role: NO diagnostic permissions
- Policy/Risk Role: NO execution permissions
- Each role follows least-privilege principle

### 5. Audit Trail

**All events MUST be recorded**:
- Decisions, recommendations, approvals, and actions
- Timestamp, actor, action, details format
- Immutable storage (S3 Object Lock)

## Approval Workflow

### APPROVE Path

- Triggers remediation execution
- SSM Runbook execution permitted

### REJECT Path

- Updates status to REMEDIATION_REJECTED
- NO SSM execution

### TIMEOUT Path

- Updates status to TIMEOUT_EXCEEDED
- NO SSM execution

## Critical Invariants

1. **REJECT => NO SSM**: Always verified
2. **TIMEOUT => NO SSM**: Always verified
3. **RESOLVED => Health Verification SUCCESS**: Always verified
4. **Execution Success != Recovery Verified**: Always enforced

## AWS Documentation

For AWS-specific security validation, use the `aws-docs` MCP server.