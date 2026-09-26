# SRE Copilot Power

Human-Governed Autonomous Incident Remediation

## What This Power Does

The SRE Copilot Power packages the architecture, guidance, skills, and best practices for building Human-in-the-Loop (HITL) incident remediation systems on AWS.

## Intended Use Cases

- **Architecture Review**: Validate HITL architecture against security invariants
- **HITL Validation**: Ensure state-changing operations require explicit approval
- **Step Functions Review**: Verify callback patterns and Task Token implementation
- **Security Boundary Enforcement**: Confirm AI components cannot execute state-changing operations
- **AWS Documentation**: Validate AWS Step Functions implementations using aws-docs MCP

## Architecture Overview

### Security Invariant

**AI recommends. Policy evaluates. Human authorizes. Automation executes. System verifies. Audit records.**

### Core Components

1. **AI Diagnosis Engine**: Analyzes evidence and proposes root causes (read-only)
2. **Policy/Risk Engine**: Calculates risk scores and identifies remediation (read-only)
3. **HITL Approval**: Provides explicit human authorization (callback pattern)
4. **Execution Engine**: Runs approved SSM Runbooks (execution only)
5. **Verification Engine**: Confirms service recovery (read-only)
6. **Audit System**: Records all events (write-only)

### Approval Workflow

```
APPROVE -> SSM Execution -> Verification -> RESOLVED
REJECT -> REMEDIATION_REJECTED -> NO SSM
TIMEOUT -> TIMEOUT_EXCEEDED -> NO SSM
```

## AWS Step Functions Pattern

The Power enforces the Task Token callback pattern for HITL approval:

1. Step Functions invokes HITL Approval with Task Token
2. Workflow pauses (NOT an error state)
3. Approval Lambda stores Task Token securely
4. Approval request sent to channel (email/Slack/Teams)
5. Approvers respond via callback URL
6. Callback service validates and calls `SendTaskSuccess` (APPROVE) or `SendTaskFailure` (REJECT)
7. Step Functions resumes and branches accordingly

## Task Token Workflow

Task Tokens are sensitive callback credentials that:

- Must never be logged
- Must never appear in user-facing interfaces
- Must never be included in EventBridge events
- Must be accessible only by authorized callback component
- Must remain protected at rest if persisted

## Security Boundaries

### IAM Role Separation

- **AI Diagnosis Role**: NO SSM permissions
- **Policy/Risk Role**: NO execution permissions
- **Execution Role**: NO diagnostic permissions

### Component Permissions

- AI Diagnosis Engine: `bedrock:InvokeModel` only
- Policy/Risk Engine: Read-only access only
- Execution Engine: `ssm:StartExecution` only
- Verification Engine: Read-only access only
- Audit System: `s3:PutObject` only

## Verification Lifecycle

1. SSM Runbook executes remediation
2. Verification Engine checks service health
3. Health verification SUCCESS -> RESOLVED
4. Health verification FAIL -> RECOVERY_FAILED

**Important**: SSM execution success alone does NOT mean RESOLVED. Only verified recovery leads to RESOLVED status.

## Audit Trail

- All events recorded in immutable S3 storage
- Timestamp, actor, action, details format
- Supports compliance and post-incident analysis

## Example Usage

See `examples/hitl-workflow.md` for a complete HITL workflow example.

## Skills

### HITL Review

The `hitl-review` skill validates HITL architectures against security invariants:

- REJECT => NO SSM
- TIMEOUT => NO SSM
- RESOLVED => Health Verification SUCCESS
- Task Token security
- IAM role separation

## MCP Integration

The Power includes `aws-docs` MCP server for AWS documentation validation:

- Step Functions callback patterns
- Task Token API reference
- Service integration patterns

## Project Structure

```
sre-copilot-power/
├── plugin.json          # Power manifest
├── README.md            # This file
├── mcp.json             # MCP configuration
├── skills/
│   └── hitl-review/     # HITL validation skill
│       ├── SKILL.md
│       └── references/
├── steering/
│   └── security.md      # Security steering document
└── examples/
    └── hitl-workflow.md # Example workflow
```

## Keywords

- sre
- incident
- operations
- aiops
- step-functions
- task-token
- human-in-the-loop
- hitl
- aws
- remediation
- audit
- verification
- policy
- risk
- observability

## Author

José Ramones

## Version

1.0.0