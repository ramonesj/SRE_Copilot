# Task Breakdown: SRE Copilot HITL Implementation

## Overview

This document breaks down the implementation of the SRE Copilot with Human-in-the-Loop (HITL) system into manageable tasks. Each task is derived from the requirements and design specifications, following the architectural safety invariant and security boundaries.

### Task Organization

Tasks are organized by component and ordered to follow the natural flow of the system:
1. Infrastructure Foundation (IaC, IAM, Storage)
2. Lambda Functions (by workflow order)
3. State Machine and Orchestration
4. Testing and Validation
5. Documentation and Deployment

### Task Status Legend

- `[ ]` - Not started
- `[IN PROGRESS]` - Currently being worked on
- `[DONE]` - Completed
- `[BLOCKED]` - Blocked by dependency
- `[SKIPPED]` - Skipped (with justification)

---

## Phase 1: Infrastructure Foundation

### Task 1.1: Project Structure and Repository Setup

**Description**: Set up the initial project structure following the approved IaC organization.

**Requirements Covered**: REQ-11 (Infrastructure as Code)

**Acceptance Criteria**:
- [ ] Directory structure matches IaC specification
- [ ] Git repository initialized with proper .gitignore
- [ ] README.md with project overview created
- [ ] CI/CD pipeline configuration added

**Implementation Details**:
```
infrastructure/
├── templates/
│   ├── sre-copilot-core.yaml
│   ├── sre-copilot-lambdas.yaml
│   ├── sre-copilot-stepfunctions.yaml
│   └── sre-copilot-monitoring.yaml
├── params/
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
└── scripts/
    ├── deploy.sh
    └── validate.sh

lambdas/
├── alert_ingestion/
├── incident_manager/
├── evidence_collection/
├── diagnosis_engine/
├── risk_assessment/
├── hitl_approval/
├── ssm_executor/
├── verification_engine/
└── audit_logger/

tests/
├── unit/
├── integration/
├── e2e/
└── data/
```

**Dependencies**: None

**Estimated Effort**: 2 hours

---

### Task 1.2: IAM Roles and Policies

**Description**: Create IAM roles with least-privilege permissions for each component, ensuring strict separation between AI diagnosis and execution roles.

**Requirements Covered**: REQ-5, REQ-6, REQ-11, REQ-12 (HITL Approval, Secrets Management, IaC)

**Acceptance Criteria**:
- [ ] AI Diagnosis Role has `bedrock:InvokeModel` but NO SSM execution permissions
- [ ] Execution Role has `ssm:StartExecution` but NO Bedrock permissions
- [ ] HITL Approver Role has appropriate channel access
- [ ] Audit Role has S3 write-only permissions
- [ ] All roles follow least-privilege principle
- [ ] No wildcard permissions (*) except where justified

**Implementation Details**:

Create CloudFormation template `infrastructure/templates/sre-copilot-core.yaml` with:

1. **AI Diagnosis Role**:
```yaml
AI.DiagnosisRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument: (Lambda service)
    Policies:
      - bedrock:InvokeModel
      - logs:CreateLogGroup, CreateLogStream, PutLogEvents
      - (NO SSM permissions, NO execution permissions)
```

2. **Execution Role**:
```yaml
ExecutionRole:
  Type: AWS::IAM::Role
  Properties:
    Policies:
      - ssm:StartExecution
      - ssm:DescribeExecution
      - secretsmanager:GetSecretValue (for runbook params)
      - logs:CreateLogGroup, CreateLogStream, PutLogEvents
      - (NO bedrock permissions)
```

3. **HITL Approver Role**:
```yaml
HITLApproverRole:
  Type: AWS::IAM::Role
  Properties:
    Policies:
      - secretsmanager:GetSecretValue (approval channel credentials)
      - sqs:SendMessage (if async approval)
      - logs:CreateLogGroup, CreateLogStream, PutLogEvents
      - (NO SSM permissions, NO bedrock permissions)
```

4. **Audit Role**:
```yaml
AuditRole:
  Type: AWS::IAM::Role
  Properties:
    Policies:
      - s3:PutObject (audit bucket)
      - s3:GetObjectVersion (read specific versions)
      - kms:Decrypt (if KMS encrypted)
      - (NO delete permissions, NO execution permissions)
```

**Security Validation**:
- Verify AI Diagnosis Role CANNOT invoke SSM
- Verify Execution Role CANNOT invoke Bedrock
- Verify roles are separate and cannot assume each other

**Dependencies**: Task 1.1

**Estimated Effort**: 4 hours

---

### Task 1.3: DynamoDB Tables

**Description**: Create DynamoDB tables for incident storage and state management.

**Requirements Covered**: REQ-2, REQ-10 (Incident Tracking, Workflow Orchestration)

**Acceptance Criteria**:
- [ ] Incidents table created with incident_id as partition key
- [ ] Approval requests table created for HITL state tracking
- [ ] Point-in-time recovery enabled
- [ ] Encryption at rest enabled
- [ ] TTL configured for approval tokens (300 seconds)

**Implementation Details**:

```yaml
IncidentsTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: SRE-Copilot-Incidents
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: incident_id
        AttributeType: S
    KeySchema:
      - AttributeName: incident_id
        KeyType: HASH
    PointInTimeRecoverySpecification:
      PointInTimeRecoveryEnabled: true
    SSESpecification:
      SSEEnabled: true

ApprovalRequestsTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: SRE-Copilot-ApprovalRequests
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: approval_request_id
        AttributeType: S
      - AttributeName: incident_id
        AttributeType: S
    KeySchema:
      - AttributeName: approval_request_id
        KeyType: HASH
      - AttributeName: incident_id
        KeyType: RANGE
    TimeToLiveSpecification:
      AttributeName: ttl
      Enabled: true
```

**Dependencies**: Task 1.1

**Estimated Effort**: 2 hours

---

### Task 1.4: S3 Audit Bucket

**Description**: Create S3 bucket for immutable audit trail storage.

**Requirements Covered**: REQ-9 (Complete Audit Trail)

**Acceptance Criteria**:
- [ ] S3 bucket created with versioning enabled
- [ ] Object Lock configuration:
  - MVP/demo: Object Lock is optional and configurable through IaC
  - Production: Object Lock is configurable according to organizational security and compliance requirements
- [ ] Default retention period: 30 days (configurable)
- [ ] Server-side encryption enabled (KMS preferred)
- [ ] Public access blocked
- [ ] Lifecycle policy configured

**Implementation Details**:

```yaml
AuditBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: sre-copilot-audit
    VersioningConfiguration:
      Status: Enabled
    PublicAccessBlockConfiguration:
      BlockPublicAcls: true
      BlockPublicPolicy: true
      IgnorePublicAcls: true
      RestrictPublicBuckets: true
    BucketEncryption:
      ServerSideEncryptionConfiguration:
        - ServerSideEncryptionByDefault:
            SSEAlgorithm: aws:kms
            KMSMasterKeyID: !Ref AuditKMSKey
    LifecycleConfiguration:
      Rules:
        - ID: AuditRetention
          Status: Enabled
          ExpirationInDays: 30  # Configurable
```

**Dependencies**: Task 1.1

**Estimated Effort**: 2 hours

---

### Task 1.5: Secrets Manager Configuration

**Description**: Configure Secrets Manager for approval channel credentials and sensitive configuration.

**Requirements Covered**: REQ-12 (Secrets Management)

**Acceptance Criteria**:
- [ ] Secret created for approval channel credentials
- [ ] Secret created for SSM runbook parameters (if needed)
- [ ] Automatic rotation enabled (90 days)
- [ ] IAM policies restrict access to specific roles
- [ ] No secrets in code or environment variables

**Implementation Details**:

```yaml
HITLApprovalSecret:
  Type: AWS::SecretsManager::Secret
  Properties:
    Name: sre-copilot/approval/credentials
    Description: Credentials for HITL approval channels
    SecretString: (initial placeholder, updated at deployment)
    RotationLambdaARN: (rotation Lambda ARN)
    RotationRules:
      AutomaticallyAfterDays: 90
```

**Dependencies**: Task 1.2

**Estimated Effort**: 2 hours

---

### Task 1.6: EventBridge Configuration

**Description**: Configure EventBridge rules for alert ingestion.

**Requirements Covered**: REQ-1 (Alert Event Ingestion)

**Acceptance Criteria**:
- [ ] EventBridge rule created for CloudWatch Alarm events
- [ ] Event pattern matches expected alert schema
- [ ] Target configured to invoke Alert Ingestion Lambda
- [ ] Dead-letter queue configured for failed events

**Implementation Details**:

```yaml
AlertEventRule:
  Type: AWS::Events::Rule
  Properties:
    Name: sre-copilot-alert-ingestion
    EventPattern:
      source:
        - aws.cloudwatch
      detail-type:
        - CloudWatch Alarm State Change
    State: ENABLED
    Targets:
      - Arn: !GetAtt AlertIngestionLambda.Arn
        Id: AlertIngestionTarget
        DeadLetterConfig:
          Arn: !GetAtt AlertEventDLQ.Arn
```

**Dependencies**: Task 1.2, Task 2.1

**Estimated Effort**: 2 hours

---

### Task 1.7: CloudWatch Logs Configuration

**Description**: Configure CloudWatch Logs for structured logging and retention.

**Requirements Covered**: REQ-13 (Error Handling), REQ-14 (Idempotent Scripts)

**Acceptance Criteria**:
- [ ] Log groups created for each Lambda function
- [ ] Structured log format enforced (JSON)
- [ ] Retention period set to 90 days (configurable)
- [ ] Log encryption enabled
- [ ] No sensitive data (tokens, secrets) in logs

**Implementation Details**:

```yaml
LogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /aws/lambda/sre-copilot-{function-name}
    RetentionInDays: 90
```

**Dependencies**: Task 1.1

**Estimated Effort**: 1 hour

---

## Phase 2: Lambda Functions

### Task 2.1: Alert Ingestion Lambda

**Description**: Implement Alert Ingestion Lambda to receive and validate alert events.

**Requirements Covered**: REQ-1 (Alert Event Ingestion)

**Acceptance Criteria**:
- [ ] Validates event schema within 100ms
- [ ] Creates incident record in DynamoDB
- [ ] Stores original alert payload
- [ ] Returns error response for invalid events
- [ ] Structured logging with correlation ID
- [ ] No state-changing operations (read-only)

**Implementation Details**:

**File**: `lambdas/alert_ingestion/handler.py`

```python
def handler(event, context):
    """
    Alert Ingestion Lambda Handler
    
    1. Validate event schema
    2. Create incident record
    3. Store original payload
    4. Return incident_id or error
    """
    pass
```

**Key Functions**:
- `validate_event_schema(event)`: Validate against JSON schema
- `create_incident_record(event)`: Create incident in DynamoDB
- `generate_incident_id()`: Generate UUID v4
- `log_structured(level, message, correlation_id)`: Structured logging

**Dependencies**: Task 1.2, Task 1.3

**Estimated Effort**: 4 hours

---

### Task 2.2: Incident Manager Lambda

**Description**: Implement Incident Manager Lambda for incident lifecycle management.

**Requirements Covered**: REQ-2, REQ-10 (Incident Tracking, Workflow Orchestration)

**Acceptance Criteria**:
- [ ] Creates incident with unique UUID v4
- [ ] Updates incident status through lifecycle
- [ ] Manages state transitions (CREATED → RESOLVED)
- [ ] Maintains immutable audit trail
- [ ] Handles concurrent updates with optimistic locking

**Implementation Details**:

**File**: `lambdas/incident_manager/handler.py`

**Key Functions**:
- `create_incident(event)`: Create new incident
- `update_status(incident_id, new_status, details)`: Update status
- `get_incident(incident_id)`: Retrieve incident
- `validate_state_transition(current_status, new_status)`: Validate transitions

**State Transitions**:
- CREATED → EVIDENCE_COLLECTED → DIAGNOSIS_COMPLETE → RISK_ASSESSED → APPROVED → EXECUTING → RECOVERY_VERIFIED → RESOLVED
- Branches for: DIAGNOSIS_FAILED, DIAGNOSIS_TIMEOUT, REMEDIATION_REJECTED, TIMEOUT_EXCEEDED, RECOVERY_FAILED, VERIFICATION_ERROR

**Dependencies**: Task 1.3, Task 2.1

**Estimated Effort**: 4 hours

---

### Task 2.3: Evidence Collection Lambda

**Description**: Implement Evidence Collection Lambda to gather logs and metrics.

**Requirements Covered**: REQ-3 (Log Analysis)

**Acceptance Criteria**:
- [ ] Extracts relevant logs from CloudWatch Logs
- [ ] Gathers node context and metadata
- [ ] Limits log excerpt to 10,000 characters
- [ ] Prepares data for Bedrock analysis
- [ ] Handles timeout (5 seconds)

**Implementation Details**:

**File**: `lambdas/evidence_collection/handler.py`

**Key Functions**:
- `extract_logs(node_id, service_name, timestamp)`: Extract CloudWatch logs
- `get_node_metadata(node_id)`: Get EC2/SSM metadata
- `prepare_evidence_package(logs, metadata)`: Create evidence package
- `truncate_logs(logs, max_length=10000)`: Limit log length

**Dependencies**: Task 1.2, Task 2.1

**Estimated Effort**: 3 hours

---

### Task 2.4: Diagnosis Engine Lambda

**Description**: Implement AI Diagnosis Engine Lambda using AWS Bedrock.

**Requirements Covered**: REQ-3 (Log Analysis and Diagnosis)

**Acceptance Criteria**:
- [ ] Sends error_log (max 10,000 chars) and node context to Bedrock
- [ ] Generates diagnosis with confidence score (0.0-1.0)
- [ ] Identifies probable root cause with cause_type
- [ ] Includes supporting evidence (up to 5 excerpts, max 500 chars each)
- [ ] Handles Bedrock timeout (30 seconds)
- [ ] Uses IAM authentication (NO Secrets Manager for Bedrock)
- [ ] NO SSM invocation permissions

**Security Boundary**: This Lambda MUST NOT have SSM execution permissions. It can ONLY diagnose and recommend.

**Implementation Details**:

**File**: `lambdas/diagnosis_engine/handler.py`

```python
def handler(event, context):
    """
    AI Diagnosis Engine Lambda Handler
    
    1. Extract error_log and node_context
    2. Invoke Bedrock via IAM role
    3. Parse diagnosis response
    4. Return structured diagnosis
    """
    pass
```

**Key Functions**:
- `invoke_bedrock(error_log, node_context)`: Call Bedrock LLM
- `parse_diagnosis_response(response)`: Parse Bedrock output
- `extract_supporting_evidence(logs)`: Extract log excerpts
- `calculate_confidence_score(response)`: Calculate confidence

**Bedrock Prompt Template**:
```
Analyze the following error logs and provide:
1. Diagnosis summary (max 2000 chars)
2. Probable root cause with cause_type
3. Supporting evidence (up to 5 excerpts)
4. Confidence score (0.0-1.0)

Error logs: {error_log}
Node context: {node_context}
```

**Dependencies**: Task 1.2 (AI Diagnosis Role), Task 2.3

**Estimated Effort**: 6 hours

---

### Task 2.5: Risk Assessment Lambda

**Description**: Implement Policy/Risk Engine Lambda to calculate remediation risk.

**Requirements Covered**: REQ-4 (Risk Assessment)

**Acceptance Criteria**:
- [ ] Calculates remediation_risk (0-100) using formula
- [ ] Identifies available SSM Runbooks
- [ ] Assesses blast radius (affected services, nodes, dependencies)
- [ ] Separates AI confidence from remediation risk
- [ ] Completes within 10 seconds
- [ ] NO execution permissions

**Security Boundary**: This Lambda MUST NOT execute remediations. It can ONLY assess risk and identify runbooks.

**Implementation Details**:

**File**: `lambdas/risk_assessment/handler.py`

**Risk Calculation**:
```python
remediation_risk = (
    action_impact * 0.25 +
    blast_radius_factor * 0.25 +
    environment_criticality * 0.25 +
    service_criticality * 0.25
)
```

**Key Functions**:
- `calculate_risk_score(diagnosis, node_context)`: Calculate risk
- `identify_runbooks(probable_root_cause)`: Find matching runbooks
- `assess_blast_radius(node_id, service_name)`: Assess impact
- `get_service_criticality(service_name)`: Retrieve criticality score
- `get_environment_criticality()`: Get environment score

**Dependencies**: Task 1.2, Task 2.4

**Estimated Effort**: 5 hours

---

### Task 2.6: HITL Approval Lambda

**Description**: Implement HITL Approval Lambda to manage approval requests and responses.

**Requirements Covered**: REQ-5, REQ-6 (HITL Approval)

**Acceptance Criteria**:
- [ ] Generates approval request with approval_request_id
- [ ] Sends request to configured channel (Email/Slack/Teams)
- [ ] Extracts Task Token from Step Functions
- [ ] Stores Task Token securely (encrypted, never logged)
- [ ] Handles approval timeout (300 seconds default)
- [ ] Supports APPROVE, REJECT, TIMEOUT outcomes
- [ ] NO SSM execution permissions

**Security Boundary**: This Lambda MUST NOT execute remediations. It can ONLY request and process approvals.

**Implementation Details**:

**File**: `lambdas/hitl_approval/handler.py`

**Key Functions**:
- `generate_approval_request(incident, diagnosis, risk)`: Create request
- `send_approval_notification(approval_request)`: Send to channel
- `store_task_token(task_token)`: Secure storage (encrypted)
- `validate_approval_response(response)`: Verify response hash
- `process_approval_decision(response)`: Process APPROVE/REJECT

**Task Token Security**:
- Store in Secrets Manager or encrypted DynamoDB
- Never log or expose in error messages
- Single-use tokens (invalidate after use)

**Approval Request Format**:
```json
{
  "approval_request_id": "uuid",
  "incident_id": "uuid",
  "request_timestamp": "ISO 8601",
  "request_hash": "sha256(incident_id + timestamp)",
  "approval_channel": "email|slack|teams",
  "approval_details": {
    "diagnosis_summary": "...",
    "ai_confidence_score": 0.0-1.0,
    "remediation_risk": 0-100,
    "proposed_ssm_runbook": "..."
  }
}
```

**Dependencies**: Task 1.2 (HITL Role), Task 1.5, Task 2.5

**Estimated Effort**: 6 hours

---

### Task 2.7: SSM Executor Lambda

**Description**: Implement Execution Engine Lambda to run approved SSM Runbooks.

**Requirements Covered**: REQ-7 (SSM Runbook Execution)

**Acceptance Criteria**:
- [ ] Executes ONLY approved SSM Runbooks
- [ ] Uses idempotency token (UUID v4)
- [ ] Implements retry logic (3 retries, exponential backoff)
- [ ] Handles timeout (300 seconds default)
- [ ] Captures execution result (status, output, error)
- [ ] NO Bedrock permissions

**Security Boundary**: This Lambda MUST NOT invoke Bedrock. It can ONLY execute pre-approved actions.

**Implementation Details**:

**File**: `lambdas/ssm_executor/handler.py`

**Key Functions**:
- `execute_runbook(runbook_name, instance_id, params)`: Start execution
- `poll_execution_status(execution_id)`: Poll status
- `handle_execution_result(result)`: Process result
- `retry_execution(params, retry_count)`: Retry with backoff

**Idempotency**:
```python
execution = ssm.start_execution(
    DocumentName=runbook_name,
    Parameters=params,
    IdempotencyToken=str(uuid.uuid4())
)
```

**Retry Logic**:
```python
def get_backoff_delay(retry_count):
    return min(5 * (2 ** retry_count), 60)
```

**Dependencies**: Task 1.2 (Execution Role), Task 2.6

**Estimated Effort**: 5 hours

---

### Task 2.8: Verification Engine Lambda

**Description**: Implement Verification Engine Lambda to confirm service recovery.

**Requirements Covered**: REQ-8 (Service Recovery Verification)

**Acceptance Criteria**:
- [ ] Retrieves original anomaly detection configuration
- [ ] Executes same monitoring check with identical parameters
- [ ] Compares result to expected threshold
- [ ] Returns SUCCESS, FAILURE, or ERROR outcome
- [ ] Handles timeout (30 seconds)
- [ ] Updates incident status based on result

**Implementation Details**:

**File**: `lambdas/verification_engine/handler.py`

**Key Functions**:
- `get_original_monitoring_config(incident_id)`: Retrieve config
- `execute_health_check(config)`: Run health check
- `compare_health_result(actual, expected)`: Compare results
- `update_incident_status(incident_id, verification_result)`: Update

**Verification Methods**:
- CloudWatch alarm check
- HTTP health check
- TCP port check
- Custom script execution

**Dependencies**: Task 1.2, Task 2.7

**Estimated Effort**: 4 hours

---

### Task 2.9: Audit Logger Lambda

**Description**: Implement Audit Logger Lambda to record all events to S3.

**Requirements Covered**: REQ-9 (Complete Audit Trail)

**Acceptance Criteria**:
- [ ] Records all audit events to S3
- [ ] Structured JSON format with consistent schema
- [ ] Includes timestamp, actor, action, details
- [ ] Immutable storage (append-only)
- [ ] Handles storage failures gracefully
- [ ] Configurable retention period

**Implementation Details**:

**File**: `lambdas/audit_logger/handler.py`

**Audit Entry Schema**:
```json
{
  "audit_id": "uuid",
  "incident_id": "uuid",
  "timestamp": "ISO 8601",
  "actor": "system|human",
  "actor_identity": {
    "user_id": "string",
    "user_name": "string",
    "role": "string"
  },
  "action": "INCIDENT_CREATED|DIAGNOSIS_GENERATED|...",
  "details": {},
  "correlation_id": "uuid"
}
```

**Audit Events**:
- INCIDENT_CREATED
- DIAGNOSIS_GENERATED
- RISK_ASSESSED
- APPROVAL_REQUESTED
- APPROVAL_RECEIVED
- EXECUTION_STARTED
- EXECUTION_COMPLETED
- VERIFICATION_COMPLETED
- STATUS_UPDATED

**Dependencies**: Task 1.4, Task 2.1

**Estimated Effort**: 3 hours

---

## Phase 3: Step Functions State Machine

### Task 3.1: State Machine Definition

**Description**: Implement Step Functions state machine for workflow orchestration.

**Requirements Covered**: REQ-10 (Workflow Orchestration)

**Acceptance Criteria**:
- [ ] State machine orchestrates complete workflow
- [ ] Implements HITL callback pattern using AWS Step Functions callback integration with waitForTaskToken
- [ ] Explicitly passes $$.Task.Token to HITL Approval component
- [ ] Workflow remains waiting (not synchronous Lambda invocation)
- [ ] Supports pause/resume for human approval via callback
- [ ] Error handling for all failure states
- [ ] Timeout handling for each step
- [ ] CloudWatch Events emission (every 5 seconds)
- [ ] Task Tokens treated as sensitive - never exposed in logs or user-facing interfaces

**Implementation Details**:

**File**: `infrastructure/templates/sre-copilot-stepfunctions.yaml`

**State Machine Flow**:
```
Step Functions callback task
  → Task Token ($$.Task.Token)
  → Approval request
  → Workflow remains waiting (PAUSED state)
  → Human decision
  → Approval Callback Service
  → Retrieve and validate Task Token
  → Resume Step Functions
  → Evaluate approval decision

APPROVE
  → ExecuteRemediation

REJECT
  → REMEDIATION_REJECTED
  → NO SSM execution

TIMEOUT
  → TIMEOUT_EXCEEDED
  → NO SSM execution
```

**Key States**:
- `ValidateEvent`: 10s timeout
- `CreateIncident`: 5s timeout, 3x retry
- `CollectEvidence`: 5s timeout, 3x retry
- `DiagnoseIncident`: 30s timeout
- `AssessRisk`: 10s timeout
- `RequestHumanApproval`: 300s timeout (callback with waitForTaskToken)
- `ExecuteRemediation`: 300s timeout, 3x retry
- `VerifyRecovery`: 30s timeout
- `RecordAudit`: 5s timeout

**Task Token Callback Pattern**:
```json
{
  "Type": "Task",
  "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
  "Parameters": {
    "FunctionName": "arn:aws:lambda:{region}:{account}:function:HITLApproval",
    "Payload": {
      "incident_id.$": "$.incident.incident_id",
      "diagnosis.$": "$.diagnosis",
      "risk_assessment.$": "$.risk_assessment",
      "task_token.$": "$$.Task.Token"
    }
  },
  "TimeoutSeconds": 300,
  "HeartbeatSeconds": 60,
  "ResultPath": "$.approval",
  "Next": "EvaluateApprovalDecision"
}
```

**Critical Requirement**: This MUST use the AWS Step Functions callback integration pattern with `waitForTaskToken`. A normal synchronous Lambda invocation (without `.waitForTaskToken`) MUST NOT satisfy the HITL Task Token requirement.

**Task Token Security**:
- Task Token is passed securely to HITL Approval Lambda
- HITL Approval Lambda stores token encrypted (never logs it)
- Approval Callback Service retrieves and validates token
- Token used to call `SendTaskSuccess` or `SendTaskFailure` to resume workflow
- Token is single-use and invalidated after callback

**Dependencies**: Task 2.6 (HITL Approval Lambda)

**Estimated Effort**: 6 hours

---

### Task 3.2: Error Handling States

**Description**: Implement error handling states for all failure scenarios.

**Requirements Covered**: REQ-10 (Workflow Orchestration)

**Acceptance Criteria**:
- [ ] DiagnosisFailure state
- [ ] ApprovalTimeout state
- [ ] ExecutionFailure state
- [ ] VerificationFailure state
- [ ] RecoveryFailure state
- [ ] RemediationRejected state

**Implementation Details**:

```json
{
  "Catch": [
    {
      "ErrorEquals": ["States.Timeout"],
      "Next": "DiagnosisTimeout"
    },
    {
      "ErrorEquals": ["Bedrock.Error"],
      "Next": "DiagnosisFailed"
    }
  ]
}
```

**Dependencies**: Task 3.1

**Estimated Effort**: 3 hours

---

### Task 3.3: CloudWatch Events Integration

**Description**: Configure CloudWatch Events for workflow monitoring.

**Requirements Covered**: REQ-10 (Workflow Orchestration)

**Acceptance Criteria**:
- [ ] Events emitted every 5 seconds during execution
- [ ] Events include: step_id, step_name, status, timestamp, incident_id
- [ ] CloudWatch Alarms for workflow failures
- [ ] Dashboard for workflow visualization

**Implementation Details**:

```yaml
WorkflowMonitoringRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern:
      source:
        - aws.states
      detail-type:
        - Step Functions Execution Status Change
```

**Dependencies**: Task 3.1

**Estimated Effort**: 2 hours

---

## Phase 4: SSM Runbooks

### Task 4.1: Service Restart Runbook (MVP)

**Description**: Create idempotent SSM Runbook for service restart.

**Requirements Covered**: REQ-7, REQ-14 (SSM Execution, Idempotent Scripts)

**Acceptance Criteria**:
- [ ] Validates preconditions (current service state)
- [ ] Checks if service is already healthy
- [ ] Restarts service only if needed
- [ ] Verifies service recovery after restart
- [ ] Logs all actions to CloudWatch
- [ ] Safe for repeated execution

**Implementation Details**:

**File**: `infrastructure/runbooks/service-restart.yaml`

```yaml
SSMDocument:
  Type: AWS::SSM::Document
  Properties:
    DocumentType: Automation
    Content:
      schemaVersion: '0.3'
      description: 'Idempotent service restart runbook'
      parameters:
        InstanceId:
          type: String
        ServiceName:
          type: String
      mainSteps:
        - name: CheckCurrentServiceState
          action: aws:executeScript
          inputs:
            Runtime: python3.11
            Handler: check_service
            Script: |
              # Check if service is active
              # Return: active, inactive, failed
        - name: DetermineRemediationRequired
          action: aws:branch
          inputs:
            Choices:
              - Variable: "{{CheckCurrentServiceState.serviceStatus}}"
                StringEquals: 'active'
                NextStep: VerifyAlreadyHealthy
              - Variable: "{{CheckCurrentServiceState.serviceStatus}}"
                StringEquals: 'failed'
                NextStep: RestartService
            defaultNextStep: RestartService
        - name: RestartService
          action: aws:runCommand
          inputs:
            DocumentName: AWS-RunShellScript
            InstanceIds: ["{{InstanceId}}"]
            Parameters:
              commands:
                - "systemctl restart {{ServiceName}}"
                - "systemctl is-active {{ServiceName}}"
        - name: VerifyServiceRecovered
          action: aws:executeScript
          inputs:
            Runtime: python3.11
            Handler: verify_recovery
            Script: |
              # Verify service is active
              # Return: success or raise exception
```

**Dependencies**: Task 1.2

**Estimated Effort**: 4 hours

---

### Task 4.2: Runbook Testing

**Description**: Test SSM Runbooks for idempotency and safety.

**Requirements Covered**: REQ-14 (Idempotent Scripts)

**Acceptance Criteria**:
- [ ] Test: Run when service is healthy → No action taken
- [ ] Test: Run when service is down → Service restarted
- [ ] Test: Run twice in succession → Second run idempotent
- [ ] Test: Runbook timeout → Graceful cancellation
- [ ] Test: Invalid parameters → Clear error message

**Implementation Details**:

**File**: `tests/integration/test_ssm_runbooks.py`

```python
def test_service_already_healthy():
    # Service is active
    # Execute runbook
    # Verify no action taken
    # Verify success result
    
def test_service_restart_required():
    # Service is inactive
    # Execute runbook
    # Verify service restarted
    # Verify health check passed
    
def test_idempotency():
    # Execute runbook twice
    # Verify same result
    # Verify no duplicate actions
```

**Dependencies**: Task 4.1

**Estimated Effort**: 3 hours

---

## Phase 5: Testing

### Task 5.1: Unit Tests - Lambda Functions

**Description**: Implement unit tests for all Lambda functions.

**Requirements Covered**: REQ-1 to REQ-15 (All requirements)

**Acceptance Criteria**:
- [ ] 80% code coverage for Lambda functions
- [ ] All public functions tested
- [ ] Edge cases and error paths covered
- [ ] Mocking for AWS services (moto)
- [ ] Structured test output

**Implementation Details**:

**Test Files**:
- `tests/unit/test_alert_ingestion.py`
- `tests/unit/test_incident_manager.py`
- `tests/unit/test_evidence_collection.py`
- `tests/unit/test_diagnosis_engine.py`
- `tests/unit/test_risk_assessment.py`
- `tests/unit/test_hitl_approval.py`
- `tests/unit/test_ssm_executor.py`
- `tests/unit/test_verification_engine.py`
- `tests/unit/test_audit_logger.py`

**Test Patterns**:
```python
class TestDiagnosisEngine:
    def test_valid_diagnosis(self, mock_bedrock):
        # Test normal flow
        
    def test_bedrock_timeout(self, mock_bedrock):
        # Test timeout handling
        
    def test_invalid_input(self, mock_bedrock):
        # Test validation
```

**Dependencies**: Task 2.1 to Task 2.9

**Estimated Effort**: 12 hours

---

### Task 5.2: Unit Tests - Security Boundaries

**Description**: Implement security boundary tests.

**Requirements Covered**: REQ-5, REQ-6, REQ-12 (Security)

**Acceptance Criteria**:
- [ ] Test: AI Diagnosis Engine CANNOT invoke SSM
- [ ] Test: State-changing operations CANNOT bypass HITL
- [ ] Test: REJECT response never invokes SSM
- [ ] Test: TIMEOUT response never invokes SSM
- [ ] Test: Task Tokens never appear in logs
- [ ] Test: Unauthorized approval callbacks rejected

**Implementation Details**:

**File**: `tests/unit/test_security_boundaries.py`

```python
def test_ai_diagnosis_no_ssm_permissions():
    # Verify diagnosis role has NO ssm:StartExecution
    
def test_reject_never_invokes_ssm():
    # Mock REJECT response
    # Verify SSM executor is never called
    
def test_timeout_never_invokes_ssm():
    # Mock timeout
    # Verify SSM executor is never called
    
def test_task_token_not_logged():
    # Execute workflow
    # Check CloudWatch Logs
    # Verify no task token in logs
```

**Dependencies**: Task 2.1 to Task 2.9

**Estimated Effort**: 4 hours

---

### Task 5.3: Integration Tests

**Description**: Implement integration tests for component interactions.

**Requirements Covered**: REQ-10 (Workflow Orchestration)

**Acceptance Criteria**:
- [ ] Lambda-to-Lambda communication tested
- [ ] Lambda-to-AWS-service integration tested
- [ ] Step Functions workflow execution tested
- [ ] EventBridge event flow tested
- [ ] DynamoDB state management tested

**Implementation Details**:

**File**: `tests/integration/test_workflow.py`

```python
@mock_aws
def test_complete_workflow():
    # Setup mock AWS resources
    # Trigger alert event
    # Verify incident created
    # Verify diagnosis generated
    # Verify risk assessed
    # Verify approval requested
    # Simulate approval response
    # Verify SSM execution
    # Verify health check
    # Verify incident resolved
```

**Dependencies**: Task 2.1 to Task 3.3

**Estimated Effort**: 8 hours

---

### Task 5.4: End-to-End Tests

**Description**: Implement E2E tests for complete workflow scenarios.

**Requirements Covered**: REQ-15 (End-to-End Demo Workflow)

**Acceptance Criteria**:
- [ ] Happy Path: Complete successful remediation
- [ ] Reject Path: No SSM execution on rejection
- [ ] Timeout Path: No SSM execution on timeout
- [ ] SSM Success + Health Failure Path
- [ ] Audit trail complete for all scenarios

**Implementation Details**:

**File**: `tests/e2e/test_e2e_scenarios.py`

**Scenarios**:

1. **Happy Path**:
```
Service Failure → Detection → Incident Created → 
Evidence Collected → AI Diagnosis → Risk Assessment → 
HITL Approval (APPROVE) → SSM Execution SUCCESS → 
Health Verification SUCCESS → RESOLVED
```

2. **Reject Path**:
```
Service Failure → Detection → Incident Created → 
Evidence Collected → AI Diagnosis → Risk Assessment → 
HITL Approval (REJECT) → REMEDIATION_REJECTED
(NO SSM execution)
```

3. **Timeout Path**:
```
Service Failure → Detection → Incident Created → 
Evidence Collected → AI Diagnosis → Risk Assessment → 
HITL Approval (TIMEOUT) → TIMEOUT_EXCEEDED
(NO SSM execution)
```

4. **SSM Success + Health Failure**:
```
Service Failure → Detection → Incident Created → 
Evidence Collected → AI Diagnosis → Risk Assessment → 
HITL Approval (APPROVE) → SSM Execution SUCCESS → 
Health Verification FAILS → RECOVERY_FAILED
```

**Dependencies**: Task 3.1, Task 4.1

**Estimated Effort**: 8 hours

---

### Task 5.5: Security Tests

**Description**: Implement security validation tests.

**Requirements Covered**: REQ-5, REQ-6, REQ-9, REQ-12 (Security)

**Acceptance Criteria**:
- [ ] IAM policy validation tests
- [ ] Secret rotation tests
- [ ] Audit trail verification tests
- [ ] Security boundary tests
- [ ] Token validation tests

**Implementation Details**:

**File**: `tests/security/test_security.py`

```python
def test_iam_least_privilege():
    # Verify all IAM roles follow least privilege
    
def test_ai_diagnosis_role_no_ssm():
    # Verify AI role has no SSM permissions
    
def test_execution_role_no_bedrock():
    # Verify execution role has no Bedrock permissions
    
def test_task_token_encryption():
    # Verify task tokens are encrypted at rest
    
def test_audit_trail_immutability():
    # Verify audit S3 bucket has Object Lock
```

**Dependencies**: Task 1.2, Task 1.5

**Estimated Effort**: 4 hours

---

### Task 5.6: Performance Tests

**Description**: Implement performance and load tests.

**Requirements Covered**: REQ-1, REQ-3, REQ-10 (Performance)

**Acceptance Criteria**:
- [ ] Event validation completes within 100ms
- [ ] Diagnosis completes within 30s
- [ ] Risk assessment completes within 10s
- [ ] Approval timeout handling tested
- [ ] Concurrent incident handling tested

**Implementation Details**:

**File**: `tests/performance/test_performance.py`

```python
def test_event_validation_latency():
    # Measure validation time
    # Assert < 100ms
    
def test_diagnosis_timeout():
    # Simulate Bedrock timeout
    # Verify graceful handling
    
def test_concurrent_incidents():
    # Send multiple alerts simultaneously
    # Verify all handled correctly
```

**Dependencies**: Task 2.1 to Task 2.9

**Estimated Effort**: 4 hours

---

## Phase 6: Documentation and Deployment

### Task 6.1: API Documentation

**Description**: Create API documentation for all Lambda functions and interfaces.

**Requirements Covered**: REQ-1 to REQ-15 (All requirements)

**Acceptance Criteria**:
- [ ] Lambda function documentation
- [ ] Input/output schemas documented
- [ ] Error codes documented
- [ ] Example requests/responses

**Implementation Details**:

**File**: `docs/api-documentation.md`

**Content**:
- Alert Ingestion API
- Incident Manager API
- Diagnosis Engine API
- Risk Assessment API
- HITL Approval API
- SSM Executor API
- Verification Engine API
- Audit Logger API

**Dependencies**: Task 2.1 to Task 2.9

**Estimated Effort**: 4 hours

---

### Task 6.2: Deployment Guide

**Description**: Create deployment guide for the SRE Copilot system.

**Requirements Covered**: REQ-11 (Infrastructure as Code)

**Acceptance Criteria**:
- [ ] Prerequisites documented
- [ ] Step-by-step deployment instructions
- [ ] Configuration options documented
- [ ] Troubleshooting guide

**Implementation Details**:

**File**: `docs/deployment-guide.md`

**Content**:
- Prerequisites (AWS account, CLI, permissions)
- Environment setup
- Parameter configuration
- Deployment commands
- Validation steps
- Rollback procedures

**Dependencies**: Task 1.1 to Task 1.7

**Estimated Effort**: 3 hours

---

### Task 6.3: Runbook Documentation

**Description**: Create operational runbook for SRE operators.

**Requirements Covered**: REQ-1 to REQ-15 (Operational)

**Acceptance Criteria**:
- [ ] Incident response procedures
- [ ] Manual intervention procedures
- [ ] Monitoring and alerting guide
- [ ] Common troubleshooting scenarios

**Implementation Details**:

**File**: `docs/operational-runbook.md`

**Content**:
- System overview
- Incident lifecycle
- HITL approval procedures
- Monitoring dashboard
- Troubleshooting common issues
- Manual escalation procedures

**Dependencies**: Task 3.1, Task 4.1

**Estimated Effort**: 3 hours

---

### Task 6.4: CI/CD Pipeline Setup

**Description**: Set up CI/CD pipeline for automated testing and deployment.

**Requirements Covered**: REQ-11 (Infrastructure as Code)

**Acceptance Criteria**:
- [ ] GitHub Actions workflow created
- [ ] Automated tests on pull requests
- [ ] Automated deployment on merge to main
- [ ] Change set review for production
- [ ] Post-deployment smoke tests

**Implementation Details**:

**File**: `.github/workflows/ci-cd.yml`

**Workflow**:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run linting
        run: flake8 lambdas/ tests/
      - name: Run unit tests
        run: pytest tests/unit -v
      - name: Run integration tests
        run: pytest tests/integration -v
      - name: Validate IaC
        run: |
          pip install cfn-lint
          cfn-lint infrastructure/templates/*.yaml
```

**Dependencies**: Task 1.1

**Estimated Effort**: 4 hours

---

### Task 6.5: Monitoring and Alerting Setup

**Description**: Set up CloudWatch monitoring and alerting.

**Requirements Covered**: REQ-10 (Workflow Orchestration)

**Acceptance Criteria**:
- [ ] CloudWatch dashboard for workflow monitoring
- [ ] Alarms for workflow failures
- [ ] Alarms for Lambda errors
- [ ] Alarms for Step Functions timeouts
- [ ] SNS notifications for critical alerts

**Implementation Details**:

**File**: `infrastructure/templates/sre-copilot-monitoring.yaml`

**Resources**:
- CloudWatch Dashboard
- CloudWatch Alarms
- SNS Topics
- Lambda Insights

**Dependencies**: Task 1.7, Task 3.1

**Estimated Effort**: 3 hours

---

## Task Summary

### Total Estimated Effort

| Phase | Tasks | Estimated Effort |
|-------|-------|------------------|
| Phase 1: Infrastructure Foundation | 7 tasks | 15 hours |
| Phase 2: Lambda Functions | 9 tasks | 40 hours |
| Phase 3: Step Functions State Machine | 3 tasks | 11 hours |
| Phase 4: SSM Runbooks | 2 tasks | 7 hours |
| Phase 5: Testing | 6 tasks | 40 hours |
| Phase 6: Documentation and Deployment | 5 tasks | 17 hours |
| **Total** | **32 tasks** | **130 hours** |

### Critical Path

1. Task 1.1 → Task 1.2 → Task 2.4 (Diagnosis Engine - core AI component)
2. Task 1.2 → Task 2.6 → Task 3.1 (HITL Approval - security boundary)
3. Task 3.1 → Task 5.4 (E2E Tests - validation)

### Parallel Work Opportunities

- Lambda functions (Tasks 2.1-2.9) can be developed in parallel after IAM roles are defined
- Unit tests (Task 5.1) can be developed alongside Lambda implementation
- Documentation (Tasks 6.1-6.3) can be developed in parallel with implementation

### Risk Areas

1. **Bedrock Integration**: Diagnosis Engine (Task 2.4) depends on Bedrock availability and API stability
2. **Task Token Security**: HITL Approval (Task 2.6) requires careful security implementation
3. **State Machine Complexity**: Step Functions (Task 3.1) orchestrates entire workflow
4. **Idempotency**: SSM Runbooks (Task 4.1) must be truly idempotent

---

## Validation Checklist

After all tasks are completed, validate:

### Requirement Coverage
- [ ] REQ-1: Alert Event Ingestion (Task 2.1, Task 1.6)
- [ ] REQ-2: Incident Creation and Tracking (Task 2.2, Task 1.3)
- [ ] REQ-3: Log Analysis and Diagnosis (Task 2.3, Task 2.4)
- [ ] REQ-4: Risk Assessment and Remediation Selection (Task 2.5)
- [ ] REQ-5: Human-in-the-Loop Approval Request (Task 2.6)
- [ ] REQ-6: Human Approval Response Handling (Task 2.6)
- [ ] REQ-7: SSM Runbook Execution (Task 2.7, Task 4.1)
- [ ] REQ-8: Service Recovery Verification (Task 2.8)
- [ ] REQ-9: Complete Audit Trail (Task 2.9, Task 1.4)
- [ ] REQ-10: Workflow Orchestration (Task 3.1, Task 3.2, Task 3.3)
- [ ] REQ-11: Infrastructure as Code (Task 1.1, Task 1.2)
- [ ] REQ-12: Secrets Management (Task 1.5)
- [ ] REQ-13: Error Handling and Input Validation (Task 2.1-2.9)
- [ ] REQ-14: Idempotent Remediation Scripts (Task 4.1)
- [ ] REQ-15: End-to-End Demo Workflow (Task 5.4)

### Architectural Consistency
- [ ] AI Diagnosis Engine has NO SSM execution permissions
- [ ] Policy/Risk Engine has NO execution permissions
- [ ] HITL Approval occurs before every state-changing operation
- [ ] Execution Engine executes ONLY pre-authorized actions
- [ ] Verification Engine is independent from Execution Engine
- [ ] Audit System records all lifecycle decisions
- [ ] Step Functions orchestrates end-to-end workflow

### HITL and Task Token Coverage
- [ ] Task Token callback pattern implemented
- [ ] Task Tokens stored encrypted (never in logs)
- [ ] Task Tokens are single-use
- [ ] APPROVE path continues to execution
- [ ] REJECT path terminates without execution
- [ ] TIMEOUT path terminates without execution

### Security Boundary Coverage
- [ ] IAM role separation enforced
- [ ] Least-privilege permissions applied
- [ ] No wildcard permissions (except where justified)
- [ ] Secrets in Secrets Manager (not in code)
- [ ] Audit trail immutable
- [ ] All communications encrypted (TLS 1.3)

### Testing and E2E Coverage
- [ ] Unit tests: 80% code coverage
- [ ] Integration tests: All critical paths
- [ ] E2E tests: All scenarios (Happy, Reject, Timeout, Health Failure)
- [ ] Security tests: All boundaries verified
- [ ] Performance tests: All timeouts validated
- [ ] Idempotency tests: All runbooks tested

---

## Next Steps

1. Review and approve task breakdown
2. Assign tasks to team members
3. Begin Phase 1: Infrastructure Foundation
4. Set up CI/CD pipeline early (Task 6.4)
5. Implement Lambda functions in order (Phase 2)
6. Implement Step Functions state machine (Phase 3)
7. Create and test SSM Runbooks (Phase 4)
8. Execute comprehensive testing (Phase 5)
9. Complete documentation (Phase 6)
10. Deploy to development environment
11. Execute E2E demo workflow
12. Review and iterate

---

**Document Status**: Approved
**Last Updated**: 2026-09-21
**Version**: 1.0