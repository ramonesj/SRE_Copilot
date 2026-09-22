<!-- Language Navigation -->
<div align="right">
  <strong>English</strong> | <a href="./README.es.md">Español</a>
</div>

<!-- Hero Section -->
<div align="center">

# SRE Copilot
## Human-Governed Autonomous Incident Remediation

**AI diagnoses. Humans authorize. Automation remediates. Recovery is verified.**

![SRE Copilot Hero](docs/assets/branding/sre-copilot-hero.png)

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/AWS-Cloud-FF9900?logo=amazonaws&logoColor=white" alt="AWS Cloud" />
  <img src="https://img.shields.io/badge/Amazon-Bedrock-232F3E?logo=amazonaws&logoColor=white" alt="Amazon Bedrock" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/Infrastructure_as_Code-CloudFormation-FF9900?logo=amazonaws&logoColor=white" alt="Infrastructure as Code" />
  <img src="https://img.shields.io/badge/Human_in_the_Loop-Required-FF6B6B?logo=people&logoColor=white" alt="Human-in-the-Loop" />
  <img src="https://img.shields.io/badge/Status-MVP_Development-4CAF50?logo=git&logoColor=white" alt="MVP Development Status" />
</p>

</div>

---

## Executive Summary

SRE Copilot is an AIOps/SRE platform designed to augment human operators with AI-powered analysis while maintaining human authority over production changes. The system follows a strict workflow that ensures safety, accountability, and verifiable recovery.

### Core Workflow:
1. **Detect** operational anomalies via AWS EventBridge
2. **Create** structured incidents with technical evidence
3. **Collect** comprehensive logs and telemetry
4. **Diagnose** root causes using Amazon Bedrock (LLM)
5. **Assess** remediation risk and operational impact
6. **Pause** workflow for human authorization (HITL)
7. **Execute** approved remediations via AWS Systems Manager
8. **Verify** service recovery independently
9. **Record** complete lifecycle in immutable audit trail

## The Problem

Traditional incident response in cloud environments requires SRE teams to manually correlate multiple data sources:
- Real-time alerts from monitoring systems
- Application and system logs
- Infrastructure telemetry and metrics
- Service dependencies and topology
- Probable root causes and remediation options
- Operational risk assessment and blast radius
- Execution results and error handling
- Post-remediation health verification

This manual process is:
- **Slow**: Hours spent identifying root causes during critical incidents
- **Error-prone**: Manual analysis can miss subtle patterns or dependencies
- **Inconsistent**: Different operators respond differently to similar incidents
- **Non-scalable**: As cloud infrastructure grows, manual response becomes unsustainable
- **Fatiguing**: Cognitive load leads to operator burnout and decreased effectiveness

SRE Copilot reduces this cognitive and operational burden while preserving human authority over all state-changing actions.

## Architectural Safety Invariant

<div align="center">
<h3>AI recommends.<br>Policy evaluates.<br>Human authorizes.<br>Automation executes.<br>System verifies.<br>Audit records.</h3>
</div>

### Critical Security Boundaries:

1. **AI Diagnosis Engine MUST NOT directly modify infrastructure or invoke remediation**
   - Bedrock access via IAM roles only (no secrets storage)
   - Read-only permissions for evidence collection
   - Zero execution permissions for state-changing operations

2. **Policy/Risk Engine MUST NOT execute remediation**
   - Risk assessment is read-only information gathering
   - Execution is handled by a separate, authorized component

3. **Every state-changing operation MUST require explicit Human-in-the-Loop approval**
   - No exceptions regardless of risk level or confidence score
   - Configurable approval channels (Email/Slack/Teams)
   - Timeout-based auto-rejection after configurable period

4. **Only the authorized Execution Engine may execute a previously approved remediation**
   - Separate IAM role with least-privilege permissions
   - Execution tokens are encrypted and never logged
   - Idempotent SSM Runbooks designed for safe repeated execution

5. **Recovery must be independently verified before incident resolution**
   - SSM execution success ≠ service recovery verified
   - Health verification uses same monitoring as original detection
   - Only verified recovery leads to RESOLVED status

## Key Features

### 🚨 **Automated Incident Detection**
- EventBridge integration for CloudWatch Alarms and custom events
- Schema validation and deduplication
- Automatic incident creation with unique identifiers

### 🔍 **AI-Assisted Root Cause Analysis**
- Amazon Bedrock integration for log analysis and pattern recognition
- Confidence scoring for diagnosis recommendations
- Evidence-based root cause identification

### ⚖️ **Risk-Aware Decision Support**
- Operational impact assessment
- Blast radius calculation
- SSM Runbook identification and compatibility checking

### 👥 **Human-in-the-Loop Approval**
- Configurable approval channels (Email/Slack/Teams)
- Task Token callback pattern for secure workflow resumption
- Timeout management with auto-rejection

### ⚡ **Safe Automation Execution**
- Idempotent SSM Runbooks for service-level remediation
- Execution status tracking and error handling
- Secure token management (never logged)

### ✅ **Independent Recovery Verification**
- Post-execution health checks
- Same monitoring source as original detection
- Verification failure triggers recovery failed status

### 📜 **Complete Audit Trail**
- Immutable S3 storage with configurable retention
- Structured JSON events with actor attribution
- Compliance-ready logging for all lifecycle events

## Technology Stack

### Core AWS Services
- **Amazon EventBridge**: Event ingestion and routing
- **AWS Lambda**: Serverless compute for all application logic
- **AWS Step Functions**: Workflow orchestration with HITL wait states
- **Amazon Bedrock**: LLM-based diagnosis and analysis
- **AWS Systems Manager (SSM)**: Runbook execution and automation
- **Amazon S3**: Immutable audit trail storage
- **Amazon CloudWatch**: Monitoring, logging, and health verification
- **AWS IAM**: Role-based access control and permissions management

### Development Stack
- **Python 3.11+**: Primary Lambda runtime
- **AWS CDK/CloudFormation**: Infrastructure as Code
- **pytest**: Unit and integration testing
- **GitHub Actions**: CI/CD pipeline automation

## Project Status

### Kiro University Progress

#### Completed
- [x] Project Definition
- [x] Requirements
- [x] Technical Design
- [x] Implementation Tasks
- [x] Steering Documents
- [x] Kiro Hooks
- [x] Lesson 3 Hook Demonstration
- [x] PBT Properties Defined
- [x] PBT-001 Risk Score Bounds Executed
- [x] PBT-002 AI Confidence Independence Executed
- [x] 200 Generated PBT Cases Passed

#### Pending
- [ ] HITL Safety PBT Execution
- [ ] Recovery Lifecycle PBT Execution
- [ ] Infrastructure as Code Implementation
- [ ] Core Lambda Components
- [ ] HITL Workflow
- [ ] SSM Service Remediation
- [ ] Health Verification
- [ ] Complete Audit System
- [ ] Final End-to-End Demo

**Current Phase**: MVP Development  
**Target**: Single complete remediation scenario (critical service restart)

### MVP Scope:
- ✅ Critical service failure detection via CloudWatch Alarms
- ✅ Incident creation and evidence collection
- ✅ AI-assisted diagnosis via Bedrock
- ✅ Risk assessment and SSM Runbook identification
- ✅ HITL approval workflow with timeout management
- ✅ Service-level remediation via SSM (not instance restart)
- ✅ Independent health verification
- ✅ Immutable audit trail (30-day retention MVP)

## Kiro University Lessons

### Lesson 3: Kiro Hooks for Quality Gates

**Status**: ✅ Completed

Implemented three Kiro hooks to enforce quality gates and security boundaries:

#### Python Quality Gate Hook
- **File**: `.kiro/hooks/python-quality-gate.json`
- **Trigger**: `PostFileSave`
- **Matcher**: `\.py$`
- **Action Type**: `agent`
- **Purpose**: Performs Python quality validation on files modified by Kiro. It checks syntax and available linting tools.

#### Security Boundary Guard Hook
- **File**: `.kiro/hooks/security-boundary-guard.json`
- **Trigger**: `PreToolUse`
- **Action Type**: `agent`
- **Purpose**: Validates relevant agent operations against the SRE Copilot architectural safety invariant.

#### Post Task Spec Validation Hook
- **File**: `.kiro/hooks/post-task-validation.json`
- **Trigger**: `PostTaskExecution`
- **Action Type**: `agent`
- **Purpose**: Validates completed Spec tasks against Requirements, Design, Steering, security constraints and relevant tests.

### Lesson 4: Property-Based Testing

**Status**: ✅ Completed

Implemented Property-Based Testing (PBT) for core Risk Engine functions using Hypothesis.

#### PBT Properties Defined: 7

##### Executed Properties (2)
1. **PBT-001: Risk Score Bounds**
   - **Invariant**: `0 <= remediation_risk <= 100`
   - **Status**: EXECUTED_PASS
   - **Cases**: 100 generated, 100 passed, 0 failed

2. **PBT-002: AI Confidence Independence**
   - **Invariant**: Changing AI Confidence alone MUST NOT change Remediation Risk
   - **Status**: EXECUTED_PASS
   - **Cases**: 100 generated, 100 passed, 0 failed

##### Pending Properties (5)
3. **PBT-003: REJECT Safety Invariant**
   - **Invariant**: REJECT => NO SSM
   - **Status**: EXECUTION_PENDING_IMPLEMENTATION

4. **PBT-004: TIMEOUT Safety Invariant**
   - **Invariant**: TIMEOUT => NO SSM
   - **Status**: EXECUTION_PENDING_IMPLEMENTATION

5. **PBT-005: Execution Success Is Not Recovery**
   - **Invariant**: SSM SUCCESS + Health Verification != SUCCESS => status != RESOLVED
   - **Status**: EXECUTION_PENDING_IMPLEMENTATION

6. **PBT-006: Resolution Requires Verified Recovery**
   - **Invariant**: RESOLVED => Health Verification SUCCESS
   - **Status**: EXECUTION_PENDING_IMPLEMENTATION

7. **PBT-007: Idempotent Service Remediation**
   - **Invariant**: remediate(remediate(state)) == remediate(state)
   - **Status**: EXECUTION_DEFERRED

#### PBT Execution Summary
- **Properties Defined**: 7
- **Properties Executed**: 2
- **Generated Cases**: 200
- **Passed**: 200
- **Failed**: 0
- **Counterexamples**: 0

## Getting Started

> **Note**: This project is under active development. Installation and deployment instructions will be added as components are implemented.

### Prerequisites
- AWS Account with appropriate permissions
- Python 3.11+ and pip
- AWS CLI configured
- Git for version control

## Contributing

We welcome contributions that align with the project's architectural safety principles. Please review the following before submitting changes:

1. **Security Boundaries**: Any changes must maintain the separation between diagnosis and execution
2. **HITL Requirement**: No component may bypass human approval for state-changing operations
3. **Audit Trail**: All significant events must be recorded in the immutable audit trail

## License

This project is proprietary and confidential. All rights reserved.

---

<div align="center">
  <p><em>AI diagnoses. Humans authorize. Automation remediates. Recovery is verified.</em></p>
  <p><a href="./README.es.md">Leer en Español</a></p>
</div>
