# SRE Copilot - Project Overview

## Project Name

**SRE Copilot** - AI-Assisted Incident Response with Human-in-the-Loop Approval

## Tagline

AI-powered incident diagnosis and human-governed remediation for cloud infrastructure.

## Executive Summary

SRE Copilot is an intelligent incident response system that combines AI-driven root cause analysis with mandatory human approval for all state-changing operations. The system receives infrastructure alerts, analyzes evidence using AI, proposes remediation actions with risk assessments, requires explicit human approval before execution, and maintains a complete audit trail for compliance and accountability.

## Problem Statement

Manual incident response in modern cloud environments faces critical challenges:

- **Slow Response Times**: SREs spend hours identifying root causes during incidents
- **Cognitive Overload**: Complex systems generate overwhelming amounts of telemetry data
- **Inconsistent Remediation**: Different operators respond differently to similar incidents
- **Scaling Challenges**: As infrastructure grows, manual response becomes unsustainable
- **Knowledge Silos**: Incident resolution expertise remains locked in experienced engineers' heads

## Solution

SRE Copilot augments human operators with AI-powered analysis while maintaining human authority over production changes:

### Core Value Proposition

1. **AI Recommends, Human Authorizes**
   - AI analyzes evidence and proposes remediation actions
   - All state-changing operations require explicit human approval
   - Zero possibility of unauthorized automated changes

2. **Intelligent Root Cause Analysis**
   - AWS Bedrock (LLM) analyzes logs and telemetry
   - Provides diagnosis with confidence scores
   - Identifies probable root causes with supporting evidence

3. **Risk-Based Decision Support**
   - Evaluates operational impact of proposed remediations
   - Calculates risk scores to inform human decisions
   - Identifies appropriate SSM runbooks for remediation

4. **Complete Audit Trail**
   - Immutable logging of all decisions and actions
   - Full traceability for compliance requirements
   - Post-incident analysis capabilities

## Key Features

### 1. Event-Driven Incident Response
- Amazon EventBridge integration for real-time alert ingestion
- Support for CloudWatch Alarms and custom event sources
- Automatic incident creation and tracking

### 2. Evidence Collection
- Automated CloudWatch Logs extraction
- Service metadata and context gathering
- Structured evidence packages for AI analysis

### 3. AI-Powered Diagnosis
- AWS Bedrock integration for intelligent analysis
- Root cause identification with confidence scores
- Recommended remediation actions based on evidence

### 4. Risk Assessment
- Operational impact evaluation
- Risk classification (LOW, MEDIUM, HIGH, CRITICAL)
- SSM runbook identification and parameter mapping

### 5. Human-in-the-Loop Approval
- Configurable approval channels (Email, Slack, Teams)
- Task token callback pattern for secure workflow resumption
- Timeout-based auto-rejection for unresponsive approvers

### 6. Safe Execution
- AWS Systems Manager runbook execution
- Idempotent remediation scripts
- Service-level restarts (not instance restarts)

### 7. Health Verification
- Post-remediation health checks
- Service recovery verification
- Independent confirmation of successful remediation

### 8. Comprehensive Audit Trail
- Immutable S3 storage with configurable retention
- Complete decision and action logging
- Compliance-ready audit reports

## Architecture Highlights

### Architectural Safety Invariant

The system enforces a strict safety boundary:

```
AI recommends → Policy evaluates → Human authorizes → Automation executes → System verifies → Audit records
```

**Critical Constraint**: AI/LLM components can ONLY diagnose, analyze, and recommend - NEVER execute changes directly.

### Component Architecture

```
EventBridge → Alert Ingestion → Incident Manager
                                       ↓
                            Evidence Collection
                                       ↓
                            AI Diagnosis Engine
                                       ↓
                            Risk Assessment
                                       ↓
                            HITL Approval Service
                                       ↓
                            Execution Engine
                                       ↓
                            Verification Engine
                                       ↓
                            Audit Logger
```

### Security Boundaries

1. **IAM Role Separation**: Separate roles for diagnosis and execution
2. **Task Token Security**: Tokens never exposed in logs
3. **Approval Boundary**: All state changes require human approval
4. **Immutable Audit**: S3 Object Lock for tamper-proof audit trail

## Technology Stack

### Core AWS Services
- **Amazon EventBridge**: Event ingestion
- **AWS Step Functions**: Workflow orchestration
- **AWS Lambda**: Serverless compute
- **Amazon Bedrock**: AI/LLM capabilities
- **AWS Systems Manager**: Runbook execution
- **Amazon DynamoDB**: Incident state storage
- **Amazon S3**: Audit trail storage
- **AWS IAM**: Role-based access control

### Development Stack
- **Python 3.11+**: Primary language
- **boto3**: AWS SDK
- **pytest**: Testing framework
- **moto**: AWS service mocking
- **AWS SAM**: Local development and testing

### Testing Stack
- **pytest**: Unit and integration testing
- **pytest-cov**: Code coverage
- **moto**: AWS service mocking
- **cfn-lint**: CloudFormation validation
- **cfn-nag**: Security scanning

## Implementation Approach

### Spec-Driven Development

The project follows a rigorous spec-driven development methodology:

1. **Requirements Specification**: Detailed functional and non-functional requirements
2. **Design Specification**: Complete architecture and component design
3. **Task Breakdown**: Granular implementation tasks with dependencies
4. **Implementation**: Sprint-based execution with continuous validation
5. **Testing**: Comprehensive unit, integration, and end-to-end tests
6. **Documentation**: Living documentation updated with each sprint

### Sprint Organization

- **SPRINT 1-2**: Core infrastructure and data models
- **SPRINT 3**: Risk Assessment and HITL Approval
- **SPRINT 4**: SSM Execution Engine
- **SPRINT 5**: Health Verification Engine
- **SPRINT 6**: End-to-End Workflow Integration
- **SPRINT 7**: Final Demo Package and Exam Preparation

## Differentiators

### 1. Safety First
- All state changes require human approval
- AI cannot execute remediations
- Comprehensive audit trail
- Idempotent operations

### 2. Intelligent Analysis
- AI-powered root cause identification
- Evidence-based recommendations
- Confidence scoring for transparency

### 3. Production Ready
- Complete MVP implementation
- Local testing without AWS dependencies
- Property-based testing for robustness
- Security boundary validation

### 4. Extensible Architecture
- Modular component design
- Pluggable providers for different environments
- Support for multiple approval channels
- Configurable runbook library

## Use Cases

### Primary Use Case: Critical Service Failure

**Scenario**: Nginx web server crashes on EC2 instance

**Flow**:
1. CloudWatch Alarm detects service failure
2. EventBridge triggers SRE Copilot
3. Incident created with unique ID
4. Evidence collected from CloudWatch Logs
5. AI diagnoses root cause (service crash)
6. Risk assessment calculates MEDIUM risk
7. Human approves remediation
8. SSM executes service restart
9. Health verification confirms recovery
10. Incident marked as RESOLVED
11. Complete audit trail recorded

### Additional Use Cases

- **Database Connection Pool Exhaustion**: Automated connection pool reset with approval
- **Memory Leak Detection**: Service restart with memory profiling
- **Disk Space Critical**: Log cleanup and space reclamation
- **Certificate Expiration**: Automated certificate renewal with approval

## Success Metrics

### Operational Metrics
- **Mean Time to Diagnosis (MTTD)**: Target < 5 minutes
- **Mean Time to Remediation (MTTR)**: Target < 15 minutes
- **Approval Rate**: Target > 95% for legitimate incidents
- **False Positive Rate**: Target < 5%

### System Metrics
- **Availability**: 99.9% uptime for incident processing
- **Latency**: < 30 seconds for diagnosis generation
- **Audit Completeness**: 100% of incidents fully audited
- **Security Compliance**: Zero security boundary violations

## Constraints and Limitations

### MVP Scope Limitations

1. **Single Scenario**: Critical service failure on EC2/SSM-managed nodes
2. **Single Remediation**: Service restart (not instance restart)
3. **Single Environment**: Development/staging only
4. **Limited Approval Channels**: Single channel (Email/Slack/Teams)
5. **No Multi-Region**: Single region deployment
6. **No Custom ML Models**: Bedrock foundation models only

### Technical Constraints

- AWS-only implementation
- No cross-account operations
- No real-time collaboration features
- Limited runbook library
- Basic approval workflow (no multi-level approval)

## Future Roadmap

### Phase 2: Enhanced Capabilities
- Multi-region support
- Additional remediation actions
- Custom ML model integration
- Advanced approval workflows

### Phase 3: Enterprise Features
- Multi-tenant architecture
- Role-based access control
- Advanced analytics and reporting
- Integration with ITSM tools

### Phase 4: AI Advancement
- Predictive incident detection
- Automated runbook generation
- Learning from historical incidents
- Cross-service correlation

## Project Team

**Course**: Kiro University - AI Engineering Certification

**Development Approach**: Individual project with spec-driven methodology

**Duration**: Multiple sprints over comprehensive development cycle

## Documentation Structure

```
SRE_Copilot/
├── .kiro/
│   ├── specs/
│   │   ├── requirements.md
│   │   ├── design.md
│   │   └── tasks.md
│   └── steering/
│       ├── architecture.md
│       ├── security.md
│       ├── testing.md
│       ├── product.md
│       ├── deployment.md
│       └── adr.md
├── docs/
│   ├── implementation/
│   │   ├── sprint-1.md
│   │   ├── sprint-2.md
│   │   ├── sprint-3.md
│   │   ├── sprint-4.md
│   │   ├── sprint-5.md
│   │   ├── sprint-6.md
│   │   └── sprint-7.md
│   └── final-demo/
│       ├── 01-project-overview.md
│       ├── 02-demo-script.md
│       └── 03-video-checklist.md
├── src/
│   ├── alert_ingestion/
│   ├── incident_manager/
│   ├── evidence_collection/
│   ├── diagnosis_engine/
│   ├── risk_assessment/
│   ├── approval/
│   ├── ssm_executor/
│   ├── verification_engine/
│   ├── audit/
│   └── shared/
├── tests/
│   ├── unit/
│   └── integration/
├── demo.py
├── demo_sprint4.py
├── demo_sprint5.py
└── demo_end_to_end.py
```

## Key Achievements

✅ Complete MVP implementation with all 9 core components
✅ Comprehensive test coverage with property-based testing
✅ Local development environment without AWS dependencies
✅ Complete spec-driven documentation
✅ Security boundary validation
✅ End-to-end workflow integration
✅ Multiple scenario demonstrations (APPROVE, REJECT, TIMEOUT, Safety Invariant)
✅ Comprehensive audit trail
✅ Production-ready architecture

---

**Project Status**: ✅ **MVP COMPLETE - READY FOR FINAL DEMONSTRATION**

**Document Version**: 1.0
**Last Updated**: September 26, 2026
**Author**: SRE Copilot Team