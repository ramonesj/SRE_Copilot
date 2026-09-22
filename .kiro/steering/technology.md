# Technology Stack

## Overview

The SRE Copilot uses AWS as its primary cloud platform, leveraging managed services for scalability, reliability, and security.

## Approved Technology Stack

### Core AWS Services

| Service | Purpose |
|---------|---------|
| **Amazon EventBridge** | Event ingestion from CloudWatch Alarms and other sources |
| **Amazon Bedrock** | LLM-based AI diagnosis and root cause analysis |
| **AWS Step Functions** | Workflow orchestration and state management |
| **AWS Lambda** | Serverless compute for all application components |
| **AWS Systems Manager (SSM)** | Runbook execution and automation |
| **Amazon CloudWatch** | Monitoring, logging, and health verification |
| **Amazon DynamoDB** | Incident state storage |
| **Amazon S3** | Immutable audit trail storage |
| **AWS IAM** | Role-based access control |
| **AWS Secrets Manager** | Secure credential storage |

### Supporting Services

| Service | Purpose |
|---------|---------|
| **Amazon CloudWatch Logs** | Log aggregation and analysis |
| **Amazon CloudWatch Alarms** | Anomaly detection triggers |
| **AWS KMS** | Encryption at rest for S3 and Secrets Manager |
| **AWS X-Ray** | Distributed tracing (optional) |

## Technology Decisions

### Why AWS?

- **Native Integration**: All components are AWS services that integrate natively
- **Managed Services**: No infrastructure to manage, AWS handles scaling and availability
- **Security**: Built-in IAM, encryption, and compliance certifications
- **Cost-Effective**: Pay-per-use model suitable for development and production

### Why Python for Lambda?

- **Rich AWS SDK**: boto3 provides comprehensive AWS coverage
- **Strong Testing Ecosystem**: pytest is the industry standard
- **AWS Native**: Lambda runtime includes boto3 by default
- **Maintenance**: Active community and long-term support

### Why Step Functions?

- **Built-in Wait**: Task Token pattern supports async human approval
- **Error Handling**: Built-in retry and catch mechanisms
- **Audit**: Execution history is automatically recorded
- **Visual**: State machine diagrams help document workflow

## Implementation Notes

### Lambda Functions (Python)

All Lambda functions are implemented in Python 3.11+ using:
- `boto3` for AWS SDK
- `aws-lambda-powertools` for logging and tracing
- `pydantic` for data validation
- `moto` for testing AWS mocks

### Testing Stack

- **pytest**: Primary test framework
- **pytest-cov**: Code coverage reporting
- **moto**: AWS service mocking
- **JSON Schema**: Event/response validation
- **cfn-lint**: CloudFormation template validation
- **cfn-nag**: Security scanning for CloudFormation

### Infrastructure as Code

- **AWS CloudFormation**: Primary IaC tool
- YAML-based templates
- Parameterized for environment-specific values

## Service Dependencies

```
EventBridge → Alert Ingestion Lambda → Incident Manager Lambda
                                              ↓
                                    Evidence Collection Lambda
                                              ↓
                                    AI Diagnosis Engine (Bedrock)
                                              ↓
                                    Policy/Risk Engine
                                              ↓
                                    Step Functions (HITL Wait)
                                              ↓
                                    Approval Channel (Email/Slack/Teams)
                                              ↓
                                    Step Functions (Resume)
                                              ↓
                                    SSM Executor Lambda → SSM Runbook
                                              ↓
                                    Verification Engine (CloudWatch)
                                              ↓
                                    Audit Logger Lambda → S3
```