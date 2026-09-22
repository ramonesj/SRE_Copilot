# Requirements Document

## Introduction

The SRE Copilot with Human-in-the-Loop (HITL) is an AIOps system that receives infrastructure telemetry, analyzes anomalies using AI, proposes remediations with risk assessments, requires human approval for all state-changing operations, and executes approved remediations via AWS Systems Manager. The system maintains a complete audit trail of all decisions, recommendations, and actions taken during incident response workflows.

### Architectural Safety Invariant

The SRE Copilot adheres to the following architectural safety invariant:
- **AI recommends**: The AI Diagnosis Engine analyzes evidence and proposes root causes and remediation actions
- **Policy evaluates**: The Policy/Risk Engine evaluates operational impact and calculates risk scores
- **Human authorizes**: The HITL Approval component provides explicit human authorization for state-changing operations
- **Automation executes**: The Execution Engine executes only pre-authorized actions
- **System verifies**: The Verification Engine checks if remediation achieved desired outcomes
- **Audit records**: The Audit System records all decisions, approvals, executions, and results

**Security Boundary**: No component may bypass the HITL approval boundary to execute state-changing remediations. AI/LLM components can ONLY diagnose, analyze, and recommend - NEVER execute changes directly.

## Glossary

- **SRE Copilot**: The AI-powered incident response system that orchestrates anomaly detection, diagnosis, risk assessment, and remediation execution
- **EventBridge**: AWS EventBridge service used to receive infrastructure alert events from monitored nodes
- **Bedrock**: AWS Bedrock service providing LLM capabilities for log analysis and diagnosis generation
- **SSM Runbook**: AWS Systems Manager Runbook containing idempotent remediation scripts to be executed after human approval
- **Step Functions**: AWS Step Functions service orchestrating the end-to-end incident response workflow
- **Incident**: A unique incident record created when an anomaly is detected, containing all related diagnostic information and audit trail
- **HITL Approval**: Human-in-the-Loop approval process requiring manual confirmation before executing any infrastructure-modifying actions
- **Blast Radius**: The potential scope of impact from a remediation action, including affected services, nodes, and dependencies
- **Audit Trail**: Complete log of all events, decisions, recommendations, approvals, and actions for compliance and post-incident analysis
- **Idempotent Script**: A remediation script that can be safely executed multiple times without causing unintended side effects or errors
- **AI Confidence**: A numeric value between 0.0 and 1.0 representing the LLM's confidence in its root cause identification (independent from remediation risk)
- **Remediation Risk**: A calculated value between 0-100 representing the operational impact of executing a proposed remediation action (calculated using action_impact, blast_radius, environment_criticality, service_criticality, dependency_impact - NOT including AI confidence)
- **State-Changing Operation**: Any operation that modifies infrastructure, service state, configuration, application state, operating system, or managed resources (including but not limited to: creating/modifying/deleting AWS resources, changing service configurations, restarting services, modifying application state). Read-only operations (evidence collection, diagnosis, risk assessment) do NOT require HITL approval.
- **Health Verification**: Automated check to confirm service recovery after remediation execution
- **IaC**: Infrastructure as Code, the practice of managing infrastructure using configuration files

### Component Responsibilities

- **AI Diagnosis Engine**: Analyzes evidence, proposes root causes and remediation actions. Does NOT have permissions to invoke remediation directly.
- **Policy/Risk Engine**: Evaluates operational impact and calculates risk scores. Uses action_impact, blast_radius, environment_criticality, service_criticality, dependency_impact.
- **HITL Approval**: Provides explicit human authorization for state-changing operations.
- **Execution Engine**: Executes only pre-authorized actions via SSM Runbooks.
- **Verification Engine**: Checks if remediation achieved desired outcomes (health verification).
- **Audit System**: Records all decisions, approvals, executions, and results.

## Requirements

### Requirement 1: Alert Event Ingestion

**User Story:** As an infrastructure operator, I want the SRE Copilot to receive alert events from monitored nodes, so that anomalies are detected and responded to automatically.

#### Acceptance Criteria

1. WHEN a valid alert event is published to EventBridge, THE SRE Copilot SHALL ingest the event and create a new incident
2. WHEN an invalid alert event is received, THE SRE Copilot SHALL return a descriptive error and not create an incident
3. THE SRE Copilot SHALL store the original alert event payload in the incident record for audit purposes
4. FOR ALL alert events, THE SRE Copilot SHALL validate that the event matches the expected data contract before processing
5. ALL state-changing operations require explicit HITL approval regardless of risk level; AI/LLM components can ONLY diagnose, analyze, and recommend - NEVER execute changes directly

### Requirement 2: Incident Creation and Tracking

**User Story:** As a monitoring system, I want incidents to be created when anomalies are detected, so that each anomaly is tracked independently with full context.

#### Acceptance Criteria

1. WHEN an alert event is successfully ingested, THE SRE Copilot SHALL create an incident with a unique incident_id (UUID v4 format)
2. THE incident SHALL contain node_id, service_name, error_log, severity (validated against: critical, high, medium, low), and timestamp from the alert event
3. WHILE an incident is active (created but not resolved/closed), THE SRE Copilot SHALL maintain the incident record with diagnostic findings and remediation status
4. THE incident record SHALL be immutable after creation, with all updates stored as append-only audit events (timestamp, actor, action, details format)

### Requirement 3: Log Analysis and Diagnosis

**User Story:** As the AI diagnosis engine, I want to analyze error logs using Bedrock LLM, so that probable root causes are identified with supporting evidence.

#### Acceptance Criteria

1. WHEN an incident is created, THE SRE Copilot SHALL send the error_log (max 10,000 characters) and node context to Bedrock for analysis
2. IF Bedrock returns an error response, THEN THE SRE Copilot SHALL log the error details, update the incident status to "diagnosis_failed", and notify the operations team
3. WHEN Bedrock returns a diagnosis response, THE SRE Copilot SHALL generate a diagnosis containing diagnosis_summary (max 2,000 characters), probable_root_cause (structured as JSON object with cause_type and description fields), ai_confidence_score, and supporting_evidence
4. THE ai_confidence_score SHALL be a numeric value between 0.0 and 1.0 indicating the LLM's confidence in the diagnosis (independent from remediation risk)
5. THE supporting_evidence SHALL include up to 5 log excerpts (each max 500 characters) containing error patterns that directly correspond to the probable_root_cause
6. IF the Bedrock analysis exceeds the timeout period (30 seconds), THEN THE SRE Copilot SHALL cancel the request, update the incident status to "diagnosis_timeout", and notify the operations team

### Requirement 4: Risk Assessment and Remediation Selection

**User Story:** As the risk assessment system, I want to evaluate proposed remediations for operational impact and risk level, so that human approvers can make informed decisions.

#### Acceptance Criteria

1. WHEN a diagnosis is generated, THE SRE Copilot SHALL identify available SSM Runbooks that match the probable_root_cause
2. THE blast_radius_assessment SHALL be structured as JSON with fields: affected_services (array), affected_nodes (array), dependency_impact (string), estimated_outage_duration_minutes (integer)
3. THE remediation_risk SHALL be calculated using: action_impact * 0.25 + blast_radius_factor * 0.25 + environment_criticality * 0.25 + service_criticality * 0.25 where scores are 0-100
4. WHILE assessing risk, THE SRE Copilot SHALL consider service criticality (business impact score), number of affected nodes (count), and dependency impact (cascading failure probability)
5. AI confidence and remediation risk are INDEPENDENT concepts - high AI confidence does NOT increase remediation risk
6. BOTH ai_confidence_score and remediation_risk SHALL be displayed separately in the approval request
7. ALL risk assessment operations SHALL complete within 10 seconds with timeout error handling

### Requirement 5: Human-in-the-Loop Approval Request

**User Story:** As a safety mechanism, I want to require human approval before executing any state-changing operation, so that infrastructure modifications cannot occur without explicit authorization.

#### Acceptance Criteria

1. ALL state-changing operations require explicit HITL approval regardless of risk level; read-only operations (evidence collection, diagnosis, risk assessment) can execute automatically
2. WHEN a state-changing operation is proposed, THE SRE Copilot SHALL generate a HITL approval request and pause workflow execution
3. WHEN a HITL approval request is generated, THE SRE Copilot SHALL send the request to the designated approval channel with approval_request_id for correlation
4. THE HITL approval request SHALL include incident_id, diagnosis_summary, proposed_ssm_runbook, blast_radius_assessment, ai_confidence_score (0.0-1.0), and remediation_risk (0-100)
5. IF no approval is received within the configured timeout period (default: 300 seconds, configurable 60-3600), THEN THE SRE Copilot SHALL auto-reject the request and log the rejection
6. WHILE paused, THE SRE Copilot SHALL preserve workflow state and resume from last completed step upon approval

### Requirement 6: Human Approval Response Handling

**User Story:** As an approver, I want to receive clear approval requests and respond with explicit decisions, so that the workflow proceeds only with my authorization.

#### Acceptance Criteria

1. WHEN an approval response is received, THE SRE Copilot SHALL validate that the response matches an active approval request (incident_id, request_timestamp, request_hash correlation)
2. IF the response is "approve", THEN THE SRE Copilot SHALL proceed to execute the approved SSM Runbook
3. IF the response is "reject", THEN THE SRE Copilot SHALL log the rejection with approver_identity, timestamp, and rationale, update the incident status to REMEDIATION_REJECTED, and maintain the incident for potential escalation or investigation
4. THE approval response SHALL include approver_identity, timestamp, optional rationale for rejection
5. ALL approval responses SHALL create an audit trail entry with timestamp, actor, action, and details fields
6. THE approval execution flow SHALL use idempotency tokens to prevent duplicate approvals

### Requirement 7: SSM Runbook Execution

**User Story:** As the execution engine, I want to run approved SSM Runbooks via SSM, so that remediations are executed safely with proper error handling.

#### Acceptance Criteria

1. WHEN an incident is approved for remediation, THE SRE Copilot SHALL initiate the SSM Runbook execution for the specified node_id
2. WHEN the SSM Runbook execution completes or times out, THE SRE Copilot SHALL capture the execution result including status, start_time, end_time, and output_document_url
3. IF the SSM Runbook execution fails or times out, THEN THE SRE Copilot SHALL log the failure with execution_id and update the incident with error details indicating the failure reason
4. IF the SSM Runbook execution exceeds the configured timeout (default: 300 seconds), THEN THE SRE Copilot SHALL terminate the execution and update the incident with timeout error details
5. IF the SSM Runbook execution encounters a transient failure, THEN THE SRE Copilot SHALL retry up to 3 times with exponential backoff (starting delay: 5 seconds, maximum delay: 60 seconds)
6. THE SRE Copilot SHALL track execution status continuously and update the incident record with real-time progress (in-progress, completed, failed, timed-out)

### Requirement 8: Service Recovery Verification

**User Story:** As a quality assurance mechanism, I want to verify that services are recovered after remediation, so that false positives or incomplete fixes are detected.

#### Acceptance Criteria

1. AFTER an SSM Runbook execution completes successfully, THE SRE Copilot SHALL initiate a health verification within 30 seconds to verify service recovery
2. WHEN health verification is initiated, THE SRE Copilot SHALL retrieve the original anomaly detection configuration to identify the monitoring mechanism used
3. THE health verification SHALL execute the same monitoring check that detected the original anomaly, using identical parameters and thresholds
4. IF the health verification fails (service not recovered), THEN THE SRE Copilot SHALL log the verification failure with details (original anomaly ID, verification timestamp, service identifier) and update the incident status to RECOVERY_FAILED
5. IF the health verification succeeds (service recovered), THEN THE SRE Copilot SHALL update the incident status to RESOLVED
6. THE verification result SHALL be stored in the audit trail with timestamp, verification method, outcome (SUCCESS/FAILURE), and original anomaly ID
7. IF no monitoring mechanism can be retrieved for the original anomaly, THEN THE SRE Copilot SHALL fail the health verification with error message indicating no verification method available and update the incident status to VERIFICATION_ERROR

### Requirement 9: Complete Audit Trail

**User Story:** As a compliance officer, I want a complete audit trail of all decisions, recommendations, and actions, so that incidents can be reviewed for process improvement and regulatory compliance.

#### Acceptance Criteria

1. THE SRE Copilot SHALL maintain an audit trail for each incident containing all events from ingestion to resolution
2. THE audit trail SHALL include: alert ingestion (timestamp, event payload), diagnosis generation (diagnosis JSON with ai_confidence_score), risk assessment (remediation_risk score, assessment JSON), approval requests (request data), approval responses (response data, approver_identity), execution events (execution_id, status, duration), verification results (outcome, verification_method), and final status (RESOLVED, RECOVERY_FAILED, VERIFICATION_ERROR, RESOLVED_MANUALLY, REMEDIATION_REJECTED)
3. EACH audit trail entry SHALL include timestamp, actor (system or human), action performed, and relevant context (incident_id, step_name, outcome)
4. THE audit trail SHALL be stored in immutable S3 storage (versioned, object locking) with a configurable retention period via Infrastructure as Code
5. THE default retention period SHALL be 30 days for MVP/demo scenarios and configurable per organizational requirements for production deployments
6. ONLY IAM principals with explicit audit:ViewAuditEntry permission SHALL be able to read audit trail entries
7. IF audit storage fails, THEN THE SRE Copilot SHALL fail the current operation and notify the operations team

### Requirement 10: Workflow Orchestration

**User Story:** As the orchestration engine, I want to use Step Functions to manage the end-to-end workflow, so that the system is resilient to failures and can resume from interruptions.

#### Acceptance Criteria

1. THE SRE Copilot SHALL use Step Functions to orchestrate the complete incident response workflow (Anomaly Detection → Incident Creation → AI Diagnosis → Risk Assessment → HITL Approval → SSM Execution → Health Verification)
2. WHEN a Step Functions execution is interrupted (timeout, error, system failure), THE SRE Copilot SHALL resume from the last completed state within 60 seconds of recovery
3. THE Step Functions state machine SHALL include error handling states for: DiagnosisFailure, ApprovalTimeout, ExecutionFailure, VerificationFailure, RecoveryFailure, and RemediationRejected
4. WHILE workflow steps are executing, THE SRE Copilot SHALL emit CloudWatch Events every 5 seconds with: step_id, step_name, status, timestamp, incident_id
5. THE Step Functions state machine SHALL support the following incident states: CREATED, DIAGNOSIS_FAILED, DIAGNOSIS_TIMEOUT, REMEDIATION_REJECTED, RESOLVED, RECOVERY_FAILED, VERIFICATION_ERROR, RESOLVED_MANUALLY, TIMEOUT_EXCEEDED

### Requirement 11: Infrastructure as Code

**User Story:** As a platform engineer, I want all AWS infrastructure to be defined as code, so that deployments are reproducible and auditable.

#### Acceptance Criteria

1. THE SRE Copilot infrastructure SHALL be defined using AWS CloudFormation version 2023-04-19 or later OR Terraform version 1.5.0 or later
2. FOR ALL AWS resources created, THE SRE Copilot SHALL apply access policies that restrict permissions to the minimum set required for each resource's function, verified by confirming no permission includes wildcard (*) action or resource specifications except where strictly justified with business justification documented in IaC
3. THE IaC templates SHALL include all required resources: EventBridge rules for workflow triggering, AWS Bedrock resource policies for model access, Step Functions state machine with error handling states, SSM Runbooks for remediation actions, and IAM roles with resource-specific permissions limited to required actions only
4. THE IaC templates SHALL include configurable parameters for: audit trail retention period (default: 30 days for MVP, configurable up to 10 years for production)
5. WHEN IaC templates are applied, THE SRE Copilot SHALL support dry-run mode to preview changes before execution
6. ALL IaC template changes SHALL be tracked in version control with commit history including author, timestamp, and change description

### Requirement 12: Secrets Management

**User Story:** As a security officer, I want to ensure secrets are never stored in code, so that credential exposure risks are eliminated.

#### Acceptance Criteria

1. THE SRE Copilot SHALL use AWS Secrets Manager or Parameter Store for all sensitive configuration, where sensitive configuration includes: API keys, database credentials, encryption keys, authentication tokens, and any value that could grant unauthorized access to systems or data
2. WHEN credentials are required for external service access, THE SRE Copilot SHALL retrieve them at runtime from secure storage within 500 milliseconds of the request, with a maximum of 3 retry attempts
3. NO hardcoded secrets, API keys, or tokens SHALL exist in source code, configuration files, or CI/CD pipelines, where hardcoded values are defined as non-configurable constant strings embedded directly in code, build scripts, or pipeline definitions (excluding environment variable references or configuration file placeholders); automated scanning tools shall verify this compliance at build time
4. WHILE credentials are active, THE SRE Copilot SHALL rotate them automatically every 60 days or 14 days before expiration, whichever occurs first

### Requirement 13: Error Handling and Input Validation

**User Story:** As a system reliability engineer, I want strict error handling and input validation throughout the system, so that malformed inputs and unexpected conditions are handled gracefully.

#### Acceptance Criteria

1. WHEN an incoming event arrives, THE SRE Copilot SHALL validate the payload against the expected schema within 100 milliseconds, and IF validation fails, THEN THE SRE Copilot SHALL return an error response indicating the validation failure reason and log the validation failure with correlation ID
2. WHILE external service calls are in progress, THE SRE Copilot SHALL implement retry logic with exponential backoff, attempting no more than 3 retries with initial backoff of 1 second and maximum backoff of 30 seconds, and IF all retries fail, THEN THE SRE Copilot SHALL return an error response indicating the service unavailability and log the failure with correlation ID
3. THE SRE Copilot SHALL use structured logging with consistent format including timestamp, log level, correlation ID, component name, and message field
4. FOR all error responses returned to callers, THE SRE Copilot SHALL include error code, human-readable message, and correlation ID for traceability

### Requirement 14: Idempotent Remediation Scripts

**User Story:** As a script developer, I want SSM Runbooks to be idempotent, so that repeated executions do not cause unintended side effects or errors.

#### Acceptance Criteria

1. EACH SSM Runbook SHALL validate preconditions (current state matches required state for operation) before executing any state-changing operations
2. IF a remediation has already been applied, THE SSM Runbook SHALL detect this using a unique identifier (runbook_execution_id) stored in the node's metadata and exit gracefully with success
3. THE SSM Runbook SHALL log all actions taken and verify the expected state (post-remediation target state) after execution
4. IF the SSM Runbook detects an unexpected state (state differs from expected target state), THEN IT SHALL return an explicit error with diagnostic information (current_state, expected_state, deviation_description)
5. ALL SSM Runbook execution logs SHALL be stored in CloudWatch Logs with retention period of 1 year minimum

### Requirement 15: End-to-End Demo Workflow

**User Story:** As a demo operator, I want to be able to execute a complete end-to-end demo of the SRE Copilot workflow, so that stakeholders can observe the full incident response capability.

#### Acceptance Criteria

1. FOR THE MVP demo scenario (configuration value "mvp_demo" = true), WHEN a single critical service failure is simulated on a managed node (severity >= HIGH, impact score >= 3), THE SRE Copilot SHALL execute the complete MVP workflow: Anomaly Detection → Incident Creation → Evidence Collection → AI Diagnosis → Risk Assessment → HITL Approval → SSM Execution → Health Verification → Audit Trail
2. THE workflow SHALL proceed through all MVP workflow steps without skipping any phases
3. ALL workflow steps SHALL complete within the configured timeout (bounds: 1 minute to 2 hours, default 30 minutes) and IF exceeded, THEN THE SRE Copilot SHALL abort and update status to TIMEOUT_EXCEEDED
4. THE final audit trail SHALL be available for review via authenticated API endpoint with configurable retention period (default 30 days for MVP/demo)
5. MVP focus is on perfect single demonstration rather than supporting multiple incomplete scenarios