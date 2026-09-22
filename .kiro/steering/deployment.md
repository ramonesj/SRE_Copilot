# Deployment and Configuration

This document outlines deployment guidelines for the SRE Copilot HITL project.

## Infrastructure as Code

### IaC Tool Choice

We use **AWS CloudFormation** as the primary IaC tool for the following reasons:

- Native integration with AWS services
- Strong support for Step Functions, Lambda, and IAM
- Built-in drift detection and compliance checking
- Comprehensive CI/CD integration

### IaC Structure

```yaml
# Infrastructure organization
infrastructure/
+-- templates/
¦   +-- sre-copilot-core.yaml          # Core infrastructure
¦   +-- sre-copilot-lambdas.yaml       # Lambda functions
¦   +-- sre-copilot-stepfunctions.yaml # State machines
¦   +-- sre-copilot-monitoring.yaml    # Monitoring and alerts
+-- params/
¦   +-- dev.yaml                       # Development parameters
¦   +-- staging.yaml                   # Staging parameters
¦   +-- prod.yaml                      # Production parameters
+-- scripts/
    +-- deploy.sh                      # Deployment script
    +-- validate.sh                    # Validation script
```

### IaC Best Practices

1. **Parameterization**:
   - Use parameters for environment-specific values
   - Use mappings for region-specific values
   - Use conditions for optional resources

2. **Drift Detection**:
   - Enable drift detection for all stacks
   - Monitor drift notifications
   - Auto-remediate where possible

3. **Rollback Policies**:
   - Enable automatic rollback on failure
   - Configure CloudWatch alarms for deployment failures

4. **Change Sets**:
   - Always review change sets before deployment
   - Use change sets for production deployments

### MVP Remediation Flow

The MVP implements a single complete remediation scenario:

**Flow**: Service Healthy ? Service Failure ? Anomaly Detected ? Incident Created ? Evidence Collected ? AI Diagnosis ? Risk Assessment ? HITL Approval ? SSM Service Remediation ? Health Verification ? RESOLVED

Key points:
- MVP remediation is **service-level restart** (e.g., restart nginx service), NOT EC2 instance restart
- The SSM Runbook uses `systemctl restart` or equivalent to restart the service on the managed node
- Health verification confirms service recovery before marking incident as RESOLVED

## Environment Configuration

### Configuration Layers

```json
{
  "environment": "development|staging|production",
  "audit_retention_days": 30,
  "approval_timeout_seconds": 300,
  "execution_timeout_seconds": 300,
  "max_retry_attempts": 3,
  "retry_backoff_seconds": 5,
  "max_retry_delay_seconds": 60
}
```

### Environment-Specific Settings

#### Development Environment

- **Audit Retention**: 30 days
- **Approval Timeout**: 300 seconds (5 minutes)
- **Execution Timeout**: 300 seconds (5 minutes)
- **Max Retries**: 3
- **SSM Runbook**: Development version
- **Bedrock Model**: Configurable via Parameter Store or environment variable

#### Staging Environment

- **Audit Retention**: 90 days
- **Approval Timeout**: 600 seconds (10 minutes)
- **Execution Timeout**: 600 seconds (10 minutes)
- **Max Retries**: 3
- **SSM Runbook**: Staging version
- **Bedrock Model**: Configurable via Parameter Store or environment variable

#### Production Environment

- **Audit Retention**: 365 days (1 year)
- **Approval Timeout**: 900 seconds (15 minutes)
- **Execution Timeout**: 900 seconds (15 minutes)
- **Max Retries**: 5
- **SSM Runbook**: Production version
- **Bedrock Model**: Configurable via Parameter Store or environment variable

### Configuration Management

#### Parameter Store Structure

```
/sre-copilot/{environment}/
+-- audit/
¦   +-- retention_days
¦   +-- bucket_name
+-- approval/
¦   +-- timeout_seconds
¦   +-- channel
+-- execution/
¦   +-- timeout_seconds
¦   +-- max_retries
+-- bedrock/
¦   +-- model_id
+-- ssm/
    +-- runbook_name
    +-- execution_role_arn
```

#### Configuration Validation

All configurations must be validated before deployment:

```yaml
# Example validation in CloudFormation
Parameters:
  ApprovalTimeout:
    Type: Number
    MinValue: 60
    MaxValue: 3600
    Default: 300

  BedrockModelId:
    Type: String
    Default: ""
    Description: "Bedrock model ID - leave empty to use default for region"
```

## Bedrock Model Configuration

### Model Selection

Bedrock model selection MUST be configurable through IaC and/or Parameter Store. The actual model must be selected at deployment time based on:

- Availability in the selected AWS Region
- Required capabilities (reasoning, vision, etc.)
- Cost considerations
- Latency requirements
- Project-specific requirements

### Configuration Example

```yaml
# CloudFormation Parameter
Parameters:
  BedrockModelId:
    Type: String
    Default: ""
    Description: "Bedrock foundation model ID. If empty, defaults to region-appropriate model."

# Lambda Environment Variable
Environment:
  Variables:
    BEDROCK_MODEL_ID: !Ref BedrockModelId
```

### Authentication

Bedrock authentication MUST use IAM-based authentication via Lambda execution roles. Do NOT store AWS credentials for Bedrock in Secrets Manager.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    }
  ]
}
```

## SSM Runbook Deployment

### Runbook Structure

SSM Runbooks should be deployed as separate CloudFormation stacks. The MVP remediation is service-level restart (not EC2 instance restart):

```yaml
# Example SSM Runbook - Service Restart (MVP)
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Idempotent service restart runbook for SRE Copilot MVP'
Resources:
  ServiceRestartRunbook:
    Type: AWS::SSM::Document
    Properties:
      DocumentType: Automation
      Content:
        schemaVersion: '0.3'
        description: 'Idempotent service restart via SSM - verifies state before and after'
        AssumeRole: '{{AutomationAssumeRole}}'
        parameters:
          InstanceId:
            type: String
            description: 'EC2 instance ID with SSM agent'
          ServiceName:
            type: String
            description: 'Service name to restart (e.g., nginx, httpd)'
        mainSteps:
          - name: CheckCurrentServiceState
            action: aws:executeScript
            inputs:
              Runtime: python3.x
              Handler: check_service
              Script: |
                import subprocess
                result = subprocess.run(
                    ['systemctl', 'is-active', '{{ServiceName}}'],
                    capture_output=True, text=True
                )
                return {'status': result.stdout.strip()}
            outputs:
              - Name: serviceStatus
                type: String
                selector: $.status
            nextStep: DetermineRemediationRequired
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
                - Default: RestartService
            defaultNextStep: RestartService
          - name: VerifyAlreadyHealthy
            action: aws:executeScript
            inputs:
              Runtime: python3.x
              Handler: return_success
              Script: |
                return {'result': 'Service already healthy, no action needed'}
            nextStep: RecordSuccess
          - name: RestartService
            action: aws:runCommand
            inputs:
              DocumentName: AWS-RunShellScript
              InstanceIds:
                - '{{InstanceId}}'
              Parameters:
                commands:
                  - "systemctl restart {{ServiceName}}"
                  - "systemctl status {{ServiceName}}"
                  - "systemctl is-active {{ServiceName}}"
            nextStep: VerifyServiceRecovered
          - name: VerifyServiceRecovered
            action: aws:executeScript
            inputs:
              Runtime: python3.x
              Handler: verify_recovery
              Script: |
                import subprocess
                result = subprocess.run(
                    ['systemctl', 'is-active', '{{ServiceName}}'],
                    capture_output=True, text=True
                )
                if result.stdout.strip() != 'active':
                    raise Exception('Service failed to recover')
                return {'status': 'recovered'}
            nextStep: RecordSuccess
          - name: RecordSuccess
            action: aws:executeScript
            inputs:
              Runtime: python3.x
              Handler: record_result
              Script: |
                return {
                    'result': 'success',
                    'message': 'Service restart completed successfully'
                }
```

### Idempotency Requirements

The Runbook MUST follow these idempotency principles:

1. **Check Preconditions**: Verify current service state before taking action
2. **Conditional Execution**: Only restart if service is not healthy
3. **Verify Postconditions**: Confirm service is healthy after remediation
4. **Return Explicit Results**: Provide clear success/failure information
5. **Audit Correlation**: Generate information suitable for audit trail

The Runbook must:
- Be safe when invoked repeatedly
- Minimize blast radius (service-level, not instance-level)
- Verify the service after remediation
- Return explicit success/failure information

### Runbook Parameters

```json
{
  "InstanceId": "i-0123456789abcdef0",
  "ServiceName": "nginx",
  "Region": "us-east-1",
  "AutomationAssumeRole": "arn:aws:iam::123456789012:role/SRE-Copilot-Execution",
  "CommandTimeout": "300"
}
```

## Step Functions State Machine Deployment

### State Machine Structure - HITL Workflow

The Step Functions state machine MUST ensure human approval is obtained before any remediation execution:

```yaml
# Example Step Functions State Machine with HITL Callback
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  SRECopilotStateMachine:
    Type: AWS::StepFunctions::StateMachine
    Properties:
      DefinitionString:
        'Fn::Sub': |
          {
            "Comment": "SRE Copilot Incident Response Workflow",
            "StartAt": "ValidateEvent",
            "States": {
              "ValidateEvent": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:AlertIngestion",
                "ResultPath": "$.event",
                "Next": "CreateIncident"
              },
              "CreateIncident": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:IncidentManager",
                "ResultPath": "$.incident",
                "Next": "CollectEvidence"
              },
              "CollectEvidence": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:EvidenceCollection",
                "ResultPath": "$.evidence",
                "Next": "DiagnoseIncident"
              },
              "DiagnoseIncident": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:DiagnosisEngine",
                "ResultPath": "$.diagnosis",
                "Next": "AssessRisk"
              },
              "AssessRisk": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:RiskAssessment",
                "ResultPath": "$.risk",
                "Next": "RequestHumanApproval"
              },
              "RequestHumanApproval": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:HITLApproval",
                "TimeoutSeconds": 3600,
                "HeartbeatSeconds": 300,
                "ResultPath": "$.approval",
                "Catch": [
                  {
                    "ErrorEquals": ["HITLApprovalTimeout"],
                    "Next": "HandleTimeout"
                  }
                ],
                "Next": "EvaluateApprovalDecision"
              },
              "EvaluateApprovalDecision": {
                "Type": "Choice",
                "Choices": [
                  {
                    "Variable": "$.approval.decision",
                    "StringEquals": "APPROVE",
                    "Next": "ExecuteRemediation"
                  },
                  {
                    "Variable": "$.approval.decision",
                    "StringEquals": "REJECT",
                    "Next": "HandleRejection"
                  }
                ],
                "Default": "HandleTimeout"
              },
              "ExecuteRemediation": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:SSMExecutor",
                "ResultPath": "$.execution",
                "Next": "VerifyRecovery"
              },
              "VerifyRecovery": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:VerificationEngine",
                "ResultPath": "$.verification",
                "Next": "EvaluateRecovery"
              },
              "EvaluateRecovery": {
                "Type": "Choice",
                "Choices": [
                  {
                    "Variable": "$.verification.success",
                    "BooleanEquals": true,
                    "Next": "ResolveIncident"
                  }
                ],
                "Default": "MarkRecoveryFailed"
              },
              "ResolveIncident": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:IncidentManager",
                "Parameters": {
                  "action": "resolve",
                  "incidentId.$": "$.incident.incidentId"
                },
                "Next": "RecordAudit"
              },
              "HandleRejection": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:IncidentManager",
                "Parameters": {
                  "action": "reject",
                  "incidentId.$": "$.incident.incidentId"
                },
                "Next": "RecordAudit"
              },
              "HandleTimeout": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:IncidentManager",
                "Parameters": {
                  "action": "timeout",
                  "incidentId.$": "$.incident.incidentId"
                },
                "Next": "RecordAudit"
              },
              "MarkRecoveryFailed": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:IncidentManager",
                "Parameters": {
                  "action": "recovery_failed",
                  "incidentId.$": "$.incident.incidentId"
                },
                "Next": "RecordAudit"
              },
              "RecordAudit": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:${Region}:${AccountId}:function:AuditLogger",
                "ResultPath": "$.audit",
                "End": true
              }
            }
          }
      RoleArn: "${StateMachineRoleArn}"
```

**Critical Workflow Rules**:
- **APPROVE** ? Continue to ExecuteRemediation
- **REJECT** ? HandleRejection ? REMEDIATION_REJECTED ? NO SSM execution
- **TIMEOUT** ? HandleTimeout ? TIMEOUT_EXCEEDED ? NO SSM execution
- There MUST NOT be a path where ExecuteRemediation is reached before explicit human approval

## IAM Role Deployment

### Role Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  SRECopilotExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: SRE-Copilot-Execution
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: SRE-Copilot-Execution-Policy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - ssm:StartExecution
                  - ssm:SendCommand
                Resource: '*'
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource:
                  - arn:aws:secretsmanager:*:*:secret:sre-copilot-*
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: arn:aws:logs:*:*:log-group:/aws/lambda/sre-copilot-*
```

### Role Deployment Best Practices

1. **Least Privilege**:
   - Use resource-level permissions where possible
   - Avoid wildcard resources (`*`)
   - Use condition statements for fine-grained control

2. **Audit**:
   - Enable IAM Access Analyzer
   - Review role permissions regularly
   - Monitor role usage with CloudTrail

3. **Rotation**:
   - Use IAM roles instead of access keys
   - Enable automatic credential rotation
   - Audit role usage regularly

## Secrets Manager Configuration

### Secret Structure

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  HITLApprovalSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: sre-copilot/approval/credentials
      Description: 'Secrets for HITL approval channel'
      SecretString: |
        {
          "SlackWebhookUrl": "https://hooks.slack.com/services/...",
          "EmailSmtpServer": "smtp.example.com",
          "EmailSmtpPort": 587
        }
      RotationLambdaARN: "{{RotationLambdaArn}}"
      RotationRules:
        AutomaticallyAfterDays: 90
```

### Secrets Management Best Practices

1. **Rotation**:
   - Enable automatic rotation (90 days recommended)
   - Use rotation Lambda for complex secrets
   - Monitor rotation failures

2. **Access Control**:
   - Use IAM policies to restrict access
   - Enable secret access logging
   - Audit secret usage

3. **Encryption**:
   - Use KMS for encryption
   - Rotate KMS keys periodically
   - Audit encryption usage

## Dry-Run Deployment

### Dry-Run Process

Before production deployment:

1. **Validate Template**:
   ```bash
   aws cloudformation validate-template \
     --template-body file://infrastructure/templates/sre-copilot-core.yaml
   ```

2. **Create Change Set**:
   ```bash
   aws cloudformation create-change-set \
     --stack-name sre-copilot-prod \
     --template-body file://infrastructure/templates/sre-copilot-core.yaml \
     --change-set-name prod-deployment-$(date +%Y%m%d%H%M%S)
   ```

3. **Review Change Set**:
   - Review all changes in AWS Console or CLI
   - Verify no unexpected modifications
   - Confirm IAM role changes are correct

4. **Execute Change Set**:
   ```bash
   aws cloudformation execute-change-set \
     --change-set-name prod-deployment-$(date +%Y%m%d%H%M%S)
   ```

### Pre-Deployment Checklist

- [ ] All tests pass in development environment
- [ ] Change set reviewed and approved
- [ ] IAM role changes validated
- [ ] Backup of current configuration created
- [ ] Rollback plan documented
- [ ] Monitoring alarms configured
- [ ] Incident response plan ready

## Version Control for Infrastructure

### Repository Structure

```
infrastructure/
+-- README.md
+-- templates/
+-- params/
+-- scripts/
+-- docs/
    +-- deployment-guide.md
    +-- rollback-guide.md
    +-- troubleshooting.md
```

### Versioning Strategy

1. **Semantic Versioning**: `vX.Y.Z`
   - Major: Breaking changes
   - Minor: New features
   - Patch: Bug fixes

2. **Tagging**:
   - Tag all releases
   - Include version in stack name (e.g., `sre-copilot-v1.0.0`)

3. **Branching**:
   - `main`: Production-ready code
   - `develop`: Integration branch
   - `feature/*`: Feature branches
   - `hotfix/*`: Emergency fixes

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Infrastructure Deployment

on:
  push:
    branches: [main]
    paths: ['infrastructure/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Template
        run: |
          aws cloudformation validate-template \
            --template-body file://infrastructure/templates/sre-copilot-core.yaml
      - name: Deploy to Development
        run: |
          ./infrastructure/scripts/deploy.sh dev
      - name: Deploy to Staging
        run: |
          ./infrastructure/scripts/deploy.sh staging
      - name: Deploy to Production
        run: |
          ./infrastructure/scripts/deploy.sh prod
```

### Deployment Hooks

Use GitHub hooks or AWS CodeBuild to trigger deployments:

1. **Pre-Deployment**:
   - Run tests
   - Validate templates
   - Check for security issues

2. **Post-Deployment**:
   - Run smoke tests
   - Verify drift detection
   - Notify stakeholders

## Deployment Checklist

Before deployment:

- [ ] All code changes merged to main branch
- [ ] All tests pass
- [ ] Infrastructure validated
- [ ] Change set reviewed
- [ ] Backup created
- [ ] Monitoring configured
- [ ] Rollback plan documented

During deployment:

- [ ] Monitor deployment progress
- [ ] Check CloudWatch Logs
- [ ] Verify no drift
- [ ] Test critical paths

After deployment:

- [ ] Smoke tests pass
- [ ] Monitoring active
- [ ] Documentation updated
- [ ] Stakeholders notified