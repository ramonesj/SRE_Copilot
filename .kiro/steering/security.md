# Security Guidelines

This document outlines security guidelines for the SRE Copilot HITL project.

## Security Boundaries

### The HITL Approval Boundary

All state-changing operations **MUST** pass through the HITL approval boundary. This is a non-negotiable security requirement.

**The Safety Invariant**:
- **AI recommends**: The AI Diagnosis Engine analyzes evidence and proposes root causes and remediation actions
- **Policy evaluates**: The Policy/Risk Engine evaluates operational impact and calculates risk scores
- **Human authorizes**: The HITL Approval component provides explicit human authorization for state-changing operations
- **Automation executes**: The Execution Engine executes only pre-authorized actions
- **System verifies**: The Verification Engine checks if remediation achieved desired outcomes
- **Audit records**: The Audit System records all decisions, recommendations, and actions

**Critical Constraint**: AI/LLM components can ONLY diagnose, analyze, and recommend - NEVER execute changes directly.

### Security Boundary Enforcement

To enforce this boundary:

1. **IAM Role Separation**:
   - AI Diagnosis Role: Has `bedrock:InvokeModel` but NO execution permissions
   - Execution Role: Has `ssm:StartExecution` and `ssm:SendCommand` but NO diagnostic permissions

2. **Architecture Enforcement**:
   - Use separate Lambda functions for diagnosis and execution
   - Step Functions orchestrates the workflow, not direct Lambda-to-Lambda calls
   - Task Token pattern ensures human intervention point

3. **Audit Trail**:
   - All state changes must be logged with actor identity
   - All approval decisions must be logged with timestamp and rationale
   - Audit trail is immutable (S3 Object Lock - configurable via IaC, disabled for MVP, enabled for production)

### Prohibited Actions

- **DO NOT** allow AI/LLM components to invoke SSM Runbooks directly
- **DO NOT** allow any component to modify infrastructure without going through Step Functions
- **DO NOT** skip HITL approval for "low risk" operations
- **DO NOT** store execution tokens or approval tokens in logs or error messages
- **DO NOT** allow the same IAM role to have both diagnostic and execution permissions

## IAM Role Separation

### Required IAM Roles

The SRE Copilot requires multiple IAM roles with strict separation of concerns:

### 1. EventBridge Role

**Purpose**: Receive alert events from EventBridge

**Permissions**:
- `events:PutEvents` (for EventBridge input)
- Read-only access to CloudWatch Logs for event validation

**Constraints**:
- Must not have any execution or modification permissions
- Used only for event ingestion

### 2. AI Diagnosis Role

**Purpose**: Analyze logs and propose diagnoses using Bedrock

**Permissions**:
- `bedrock:InvokeModel` (for LLM access)
- Read-only access to CloudWatch Logs for log analysis
- Read-only access to S3 for evidence retrieval

**Constraints**:
- **MUST NOT** have `ssm:StartExecution` or `ssm:SendCommand`
- **MUST NOT** have `secretsmanager:GetSecretValue` (use IAM auth for Bedrock, not Secrets)
- **MUST NOT** have any infrastructure modification permissions

### 3. Risk Assessment Role

**Purpose**: Calculate risk scores and identify SSM Runbooks

**Permissions**:
- Read-only access to SSM for listing Runbooks
- Read-only access to CloudWatch for metrics analysis
- Read-only access to IAM for service role verification

**Constraints**:
- Must not have any execution permissions
- Used only for information gathering and calculation

### 4. HITL Approver Role

**Purpose**: Send and receive approval requests

**Permissions**:
- `secretsmanager:GetSecretValue` (for approval channel credentials)
- `lambda:InvokeFunction` (for approval callback)
- Email/Slack/Teams API access for approval notifications

**Constraints**:
- Must not have any execution permissions
- Approval tokens must be stored securely (Secrets Manager)
- Timeout handling must be enforced

### 5. Execution Role

**Purpose**: Execute SSM Runbooks

**Permissions**:
- `ssm:StartExecution` (for Step Functions)
- `ssm:SendCommand` (for SSM Documents)
- `secretsmanager:GetSecretValue` (for Runbook parameters)
- `logs:CreateLogStream` (for execution logging)

**Constraints**:
- Must be separate from AI Diagnosis Role
- Should use least-privilege permissions for target resources
- Must have task token security (never log tokens)

### 6. Audit Role

**Purpose**: Write audit events to S3

**Permissions**:
- `s3:PutObject` (for audit storage)
- `s3:GetObject` (for audit retrieval)
- `kms:Decrypt` (if KMS-encrypted)

**Constraints**:
- Must be write-only for audit events
- Should have S3 Object Lock enabled
- Must not have any execution permissions

## Secrets Management

### What NOT to Store

- **DO NOT** store API keys in code or configuration files
- **DO NOT** use IAM root user credentials
- **DO NOT** share secrets across components

### What to Store

Use AWS Secrets Manager or Parameter Store for:

1. **Approval Channel Credentials**
   - Slack webhook URLs
   - Email SMTP credentials
   - Teams webhook URLs

2. **Runbook Parameters**
   - Service-specific configuration
   - Environment-specific variables
   - Criticality scores (if not in configuration)

3. **Task Tokens**
   - Approval tokens (Treat as sensitive - never expose in logs)
   - Execution tokens (Treat as sensitive - never expose in logs)

### Best Practices

1. **Rotation**:
   - Rotate secrets automatically using Secrets Manager
   - Use scheduled rotation for long-lived credentials
   - Audit all secret access

2. **Access Control**:
   - Use IAM policies to restrict secret access
   - Implement secret access logging
   - Use separate secrets for different environments

3. **Security**:
   - Encrypt secrets at rest with KMS
   - Audit all secret access
   - Use secret versioning for rollback

## Audit Trail Protection

### Immutable Storage

All audit events must be stored in immutable storage (S3 Object Lock):

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2024-01-15T10:30:00Z",
  "actor": "HITL_Approval_Service",
  "action": "APPROVAL_GRANTED",
  "details": {
    "incident_id": "inc-123",
    "approver": "user@example.com",
    "rationale": "Approved for service restart",
    "approval_token": "encrypted-token-here"
  }
}
```

### Encryption

- **At Rest**: S3 Object Lock with KMS encryption
- **In Transit**: TLS 1.3 for all service communications
- **Sensitive Fields**: Encrypt tokens and credentials before storage

### Retention

- **Default**: 30 days (configurable per environment)
- **Compliance**: Extend to 1 year for production environments
- **Deletion**: Automatic after retention period (no manual deletion)

### Access Control

- **Read Access**: Limited to audit team and compliance officers
- **Write Access**: Only audit service Lambda
- **Modify Access**: None (immutable storage)

## Task Token Security

### What are Task Tokens?

Task Tokens are unique identifiers used by Step Functions to resume paused workflows:

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "incident_id": "inc-123",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-15T11:00:00Z"
}
```

### Security Requirements

1. **Never Log Tokens**:
   ```javascript
   // GOOD: Mask the token
   logger.info(`Approval requested for incident ${incidentId}`);
   
   // BAD: Log the token
   logger.info(`Approval requested for incident ${incidentId}, token: ${token}`);
   ```

2. **Encrypt in Storage**:
   - Store tokens encrypted in Secrets Manager
   - Use KMS for token encryption
   - Never store tokens in plaintext

3. **Time-Bound**:
   - Tokens expire after configurable timeout (default 300 seconds)
   - Automatic token invalidation after timeout
   - Token reuse prevention

4. **Single Use**:
   - Each token can be used only once
   - Immediate invalidation after use
   - Duplicate token rejection

### Token Lifecycle

```
1. Generate token (UUID v4)
2. Encrypt and store in Secrets Manager
3. Include in Step Functions task input
4. Send to approval channel (without token)
5. Approvers receive link with encrypted token
6. Approval service decrypts and validates token
7. Token consumed (invalidated)
8. Workflow resumes
```

## Least Privilege Principles

### IAM Policy Guidelines

1. **Service-Specific Permissions**:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "bedrock:InvokeModel"
     ],
     "Resource": [
       "arn:aws:bedrock:*::foundation-model/*"
     ]
   }
   ```

2. **Resource-Specific Permissions**:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "ssm:StartExecution"
     ],
     "Resource": [
       "arn:aws:states:us-east-1:123456789012:stateMachine:SRE-Copilot-*"
     ]
   }
   ```

3. **Condition-Based Permissions**:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "s3:PutObject"
     ],
     "Resource": "arn:aws:s3:::audit-bucket/*",
     "Condition": {
       "StringEquals": {
         "s3:x-amz-server-side-encryption": "aws:kms"
       }
     }
   }
   ```

### Lambda Function Isolation

1. **Separate Functions**:
   - One function per major responsibility
   - No shared state between functions
   - Explicit data passing through Step Functions

2. **Environment Variables**:
   - No secrets in environment variables
   - Use Secrets Manager for dynamic secrets
   - Use Parameter Store for configuration

## Compliance Requirements

### Audit Retention

- **Development**: 30 days
- **Staging**: 90 days
- **Production**: 1 year (configurable)

### Access Logging

All access to sensitive resources must be logged:

1. **Audit Log Entries**:
   - Timestamp
   - Actor identity
   - Action performed
   - Resource affected
   - Result (success/failure)

2. **Log Retention**:
   - 90 days in CloudWatch Logs
   - 1 year in S3 (production)
   - Immutable storage

### Compliance Frameworks

The SRE Copilot architecture is designed to support compliance frameworks, but the MVP does NOT claim compliance with any specific framework:

- MVP is for demonstration and development purposes only
- Production deployments should work toward compliance with SOC 2, HIPAA, PCI DSS, or ISO 27001 as needed
- Compliance certification requires additional controls beyond MVP scope

### Regulatory Considerations

- **Data Residency**: Ensure all data remains in specified region
- **Export Controls**: Ensure no restricted countries access the system
- **Privacy**: No PII stored in logs without encryption

## Security Checklist

Before deployment, verify:

- [ ] All IAM roles have least-privilege permissions
- [ ] AI Diagnosis Role has NO execution permissions
- [ ] Execution Role is separate from AI Diagnosis Role
- [ ] Task tokens are never logged
- [ ] Audit trail is immutable (S3 Object Lock)
- [ ] All secrets are encrypted at rest
- [ ] Approval tokens are time-bound and single-use
- [ ] All services use TLS 1.3 for communications
- [ ] Audit retention is configured per environment
- [ ] Access logging is enabled for all services