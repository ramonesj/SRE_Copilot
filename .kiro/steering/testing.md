# Testing Strategy

This document outlines the testing strategy for the SRE Copilot HITL project.

## Test Categories

### 1. Infrastructure as Code (IaC) Tests

**Purpose**: Validate CloudFormation templates before deployment

**Test Types**:
- Template syntax validation
- Parameter validation
- Resource dependency validation
- Drift detection
- Security scanning

**Tools**:
- `cfn-lint`: CloudFormation linting
- `cfn-nag`: Security scanning
- CloudFormation `validate-template`

**Test Coverage**:
- 100% of template resources
- All parameter combinations
- All condition branches

### 2. Lambda Function Unit Tests

**Purpose**: Validate Lambda function logic

**Test Types**:
- Input validation
- Business logic
- Error handling
- Edge cases

**Tools**:
- **pytest** (Python): Primary test framework
- **unittest** (Python): Built-in testing framework
- **JSON Schema validation**: For event/response validation
- **Pydantic**: For data validation and modeling
- **moto**: AWS service mocking
- **boto3**: AWS SDK for Python

**Test Coverage**:
- 80% code coverage for Lambda functions
- All public functions tested
- Edge cases and error paths covered

**Specific Unit Tests Required**:
- Event validation (valid/invalid EventBridge events)
- Incident lifecycle state transitions
- Risk calculation logic
- AI confidence vs remediation risk separation
- Idempotency verification

### 3. Integration Tests

**Purpose**: Validate component interactions

**Test Types**:
- Lambda-to-Lambda communication
- Lambda-to-AWS-service integration
- Step Functions workflow execution
- EventBridge event flow

**Tools**:
- **AWS SAM CLI**: Local Lambda invocation
- **LocalStack**: Local AWS service emulation (optional, where it adds value)
- **Docker Compose**: Local services orchestration

**Test Coverage**:
- All critical workflows
- All component interfaces
- Error scenarios

### 4. Schema Validation Tests

**Purpose**: Validate data contracts between components

**Test Types**:
- Event schema validation
- Response schema validation
- API contract validation

**Tools**:
- **JSON Schema**: Event/response validation
- **Pydantic**: Python data validation

**Test Coverage**:
- 100% of event schemas
- 100% of response schemas

### 5. Smoke Tests

**Purpose**: Validate deployment success

**Test Types**:
- Endpoint availability
- Service health
- Critical path validation

**Tools**:
- AWS CLI
- Custom test scripts
- CI/CD pipeline checks

**Test Coverage**:
- All deployed services
- All critical endpoints

### 6. Security Tests

**Purpose**: Validate security controls

**Test Types**:
- IAM policy validation
- Secret rotation
- Audit trail verification
- Security boundary verification

**Tools**:
- IAM Access Analyzer
- AWS Security Hub
- Custom security tests

**Test Coverage**:
- All IAM policies
- All security boundaries

**Required Security Tests**:
1. AI Diagnosis Engine CANNOT invoke SSM (verify IAM policy denies ssm:StartExecution)
2. State-changing operations CANNOT bypass HITL approval (verify workflow enforcement)
3. REJECT response never invokes SSM (verify workflow terminates without execution)
4. TIMEOUT response never invokes SSM (verify auto-reject without execution)
5. Task Tokens never appear in logs (verify log scrubbing)
6. Unauthorized approval callbacks are rejected (verify token validation)
7. SSM success does NOT automatically mean RESOLVED (verify verification requirement)
8. Only Health Verification SUCCESS leads to RESOLVED status

## Coverage Targets

### Lambda Functions

- **Unit Tests**: 80% code coverage
- **Integration Tests**: All critical paths
- **Edge Cases**: 100% of known edge cases

### Infrastructure

- **IaC Tests**: 100% of resources
- **Security Tests**: 100% of security controls
- **Drift Detection**: Continuous monitoring

### Workflows

- **Integration Tests**: 100% of critical workflows
- **Error Scenarios**: All error paths covered
- **Edge Cases**: All known edge cases

## Test Environment Setup

### Development Environment

```bash
# Install Python dependencies
pip install -r requirements-dev.txt

# Install AWS SAM CLI (for local testing)
# See: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

# Run unit tests
pytest tests/unit -v

# Run unit tests with coverage
pytest tests/unit --cov=lambdas --cov-report=html

# Run integration tests
pytest tests/integration -v

# Run with specific marker
pytest tests/unit -m "not integration" -v
```

### CI/CD Environment

```yaml
# Example GitHub Actions workflow
name: Tests

on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run Linting
        run: |
          pip install flake8
          flake8 lambdas/
      - name: Run Unit Tests
        run: pytest tests/unit -v
      - name: Run Integration Tests
        run: pytest tests/integration -v
      - name: Run IaC Tests
        run: |
          pip install cfn-lint
          cfn-lint templates/*.yaml
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Test Data Setup

```json
// Example test data structure
{
  "events": {
    "valid": "tests/data/events/valid.json",
    "invalid": "tests/data/events/invalid.json"
  },
  "incidents": {
    "new": "tests/data/incidents/new.json",
    "approved": "tests/data/incidents/approved.json"
  },
  "responses": {
    "diagnosis": "tests/data/responses/diagnosis.json",
    "risk": "tests/data/responses/risk.json"
  }
}
```

## CI/CD Pipeline Integration

### Pre-Commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run linter
flake8 lambdas/ tests/

# Run unit tests
pytest tests/unit -v

# Run IaC validation
cfn-lint templates/*.yaml

# Exit with test results
exit $?
```

### Build Pipeline

```yaml
# Example GitHub Actions workflow
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Validate IaC
        run: |
          pip install cfn-lint cfn-nag
          cfn-lint templates/*.yaml
          cfn-nag templates/*.yaml
      - name: Run Tests
        run: pytest tests/ -v --cov=lambdas
      - name: Build Lambda Package
        run: |
          mkdir -p dist
          zip -r dist/function.zip lambdas/
      - name: Deploy
        run: |
          ./scripts/deploy.sh ${{ env.ENVIRONMENT }}
```

### Post-Deployment Tests

```bash
# Example post-deployment test
#!/bin/bash

# Test endpoint availability
aws cloudformation describe-stacks \
  --stack-name sre-copilot-${ENVIRONMENT} \
  --query 'Stacks[0].StackStatus'

# Test critical path
aws lambda invoke \
  --function-name sre-copilot-alert-ingestion-${ENVIRONMENT} \
  --payload file://tests/data/events/valid.json \
  response.json

# Verify deployment
if [ $? -eq 0 ]; then
  echo "Deployment successful"
  exit 0
else
  echo "Deployment failed"
  exit 1
fi
```

## Example Test Patterns

### Lambda Unit Test (Python/pytest)

```python
# tests/unit/test_alert_ingestion.py

import pytest
import json
from unittest.mock import MagicMock, patch

# Import the Lambda handler
from lambdas.alert_ingestion import handler


class TestAlertIngestion:
    """Test suite for Alert Ingestion Lambda"""

    def test_valid_event_creates_incident(self):
        """Test that valid alert event creates an incident"""
        event = {
            "source": "aws.cloudwatch",
            "detail-type": "CloudWatch Alarm",
            "detail": {
                "alarm-name": "ServiceDown",
                "region": "us-east-1",
                "instance-id": "i-1234567890abcdef0"
            }
        }

        with patch('lambdas.alert_ingestion.dynamodb_client') as mock_ddb:
            mock_ddb.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
            result = handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['incidentCreated'] is True

    def test_invalid_event_returns_error(self):
        """Test that invalid event returns descriptive error"""
        event = {
            "source": "aws.cloudwatch",
            "detail": {
                "alarm-name": "ServiceDown"
                # Missing required fields
            }
        }

        result = handler(event, {})

        assert result['statusCode'] == 400
        assert 'Invalid event' in result['body']
```

### IaC Validation Test

```bash
# tests/iac/validate.sh

#!/bin/bash

echo "Validating CloudFormation templates..."

cfn-lint templates/sre-copilot-core.yaml
cfn-lint templates/sre-copilot-lambdas.yaml
cfn-lint templates/sre-copilot-stepfunctions.yaml

cfn-nag templates/sre-copilot-core.yaml
cfn-nag templates/sre-copilot-lambdas.yaml
cfn-nag templates/sre-copilot-stepfunctions.yaml

echo "All IaC tests passed"
```

### Integration Test

```python
# tests/integration/test_workflow.py

import pytest
import json
import boto3
from moto import mock_aws


@mock_aws
def test_alert_ingestion_integration():
    """Test complete alert ingestion workflow"""
    
    # Setup mock AWS clients
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    
    # Create test table
    dynamodb.create_table(
        TableName='SRE-Copilot-Incidents-dev',
        KeySchema=[{'AttributeName': 'incident_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'incident_id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Test event
    event = {
        "source": "aws.cloudwatch",
        "detail-type": "CloudWatch Alarm",
        "detail": {
            "alarm-name": "ServiceDown",
            "region": "us-east-1",
            "instance-id": "i-1234567890abcdef0"
        }
    }
    
    # Invoke Lambda (simulated)
    # In real integration test, use SAM local or deployed Lambda
    
    # Verify incident created
    response = dynamodb.scan(
        TableName='SRE-Copilot-Incidents-dev'
    )
    
    assert len(response['Items']) >= 1
```

## Mock Strategies

### AWS Service Mocks (Python)

#### Lambda Function Mocks using moto

```python
# tests/mocks/aws_services.py

import pytest
from unittest.mock import MagicMock, patch
import json


class MockBedrockClient:
    """Mock Bedrock client for testing"""

    def invoke_model(self, modelId, body):
        return {
            'body': json.dumps({
                'diagnosis': 'Service failure detected',
                'confidence': 0.95,
                'root_cause': {
                    'cause_type': 'service_crash',
                    'description': 'Service process terminated unexpectedly'
                },
                'evidence': [
                    {'log_excerpt': 'Process killed', 'severity': 'ERROR'}
                ]
            })
        }


class MockSSMClient:
    """Mock SSM client for testing"""

    def start_automation_execution(self, documentName, parameters):
        return {
            'automationExecutionId': 'exec-1234567890abcdef0'
        }

    def describe_automation_executions(self, filters):
        return {
            'AutomationExecutionMetadataList': [
                {
                    'AutomationExecutionId': 'exec-1234567890abcdef0',
                    'Status': 'Success'
                }
            ]
        }


class MockStepFunctionsClient:
    """Mock Step Functions client for testing"""

    def send_task_success(self, taskToken, output):
        return {}

    def send_task_failure(self, taskToken, error, cause):
        return {}


# Fixtures
@pytest.fixture
def mock_bedrock():
    with patch('boto3.client') as mock:
        mock.return_value = MockBedrockClient()
        yield mock


@pytest.fixture
def mock_ssm():
    with patch('boto3.client') as mock:
        mock.return_value = MockSSMClient()
        yield mock


@pytest.fixture
def mock_sfn():
    with patch('boto3.client') as mock:
        mock.return_value = MockStepFunctionsClient()
        yield mock
```

### LocalStack for Integration Testing

```yaml
# docker-compose.yml

version: '3.8'
services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - '4566:4566'
    environment:
      - SERVICES=lambda,stepfunctions,ssm,events,secretsmanager
      - DEBUG=1
```

### Custom Test Double

```python
# tests/mocks/diagnosis_engine.py

from unittest.mock import MagicMock
from typing import Dict, Any


class MockDiagnosisEngine:
    """Mock diagnosis engine for testing"""

    def __init__(self):
        self.analyze = MagicMock()
        self._setup_default_behavior()

    def _setup_default_behavior(self):
        """Configure default mock behavior"""
        self.analyze.return_value = {
            'diagnosis': 'Service failure detected',
            'confidence': 0.95,
            'root_cause': {
                'cause_type': 'service_crash',
                'description': 'Service process terminated unexpectedly'
            },
            'evidence': [
                {'log_excerpt': 'Process killed', 'severity': 'ERROR'}
            ]
        }

    def reset(self):
        """Reset mock state"""
        self.analyze.reset_mock()
        self._setup_default_behavior()


# Singleton instance
mock_diagnosis_engine = MockDiagnosisEngine()
```

## Test Data Management

### Test Data Structure

```
tests/
+-- data/
¦   +-- events/
¦   ¦   +-- valid-alert.json
¦   ¦   +-- invalid-alert.json
¦   ¦   +-- edge-case-alert.json
¦   +-- incidents/
¦   ¦   +-- new.json
¦   ¦   +-- in-progress.json
¦   ¦   +-- resolved.json
¦   +-- responses/
¦       +-- diagnosis.json
¦       +-- risk.json
¦       +-- execution.json
```

### Test Data Examples

```json
// tests/data/events/valid-alert.json

{
  "source": "aws.cloudwatch",
  "detail-type": "CloudWatch Alarm",
  "detail": {
    "alarm-name": "ServiceDown",
    "region": "us-east-1",
    "instance-id": "i-1234567890abcdef0",
    "state": "ALARM",
    "previous-state": "OK",
    "reason": "Threshold Crossed"
  }
}
```

```json
// tests/data/incidents/new.json

{
  "incident_id": "inc-123456",
  "node_id": "i-1234567890abcdef0",
  "service_name": "nginx",
  "error_log": "Connection timeout",
  "severity": "critical",
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "CREATED",
  "evidence_collected": false,
  "diagnosis_complete": false,
  "risk_assessed": false
}
```

## End-to-End (E2E) Test Scenarios

### Primary E2E Scenario: Happy Path

**Test**: Service Failure ? Detection ? Incident Creation ? Evidence Collection ? AI Diagnosis ? Risk Assessment ? HITL Pause ? Human APPROVAL ? SSM Service Remediation ? Health Verification SUCCESS ? RESOLVED ? Audit Trail

**Steps**:
1. Simulate service failure event (EventBridge alert)
2. Verify incident created with unique ID
3. Verify evidence collected from CloudWatch
4. Verify AI diagnosis generated with confidence score
5. Verify risk assessment calculated
6. Verify workflow pauses at HITL approval step
7. Simulate human APPROVAL response
8. Verify SSM Runbook executed (service restart)
9. Verify health verification initiated
10. Verify health check returns SUCCESS
11. Verify incident status = RESOLVED
12. Verify audit trail contains all events

### Alternative E2E Scenarios

#### Scenario: REJECT - No SSM Execution

**Test**: Service Failure ? Detection ? Incident Creation ? AI Diagnosis ? Risk Assessment ? HITL Pause ? Human REJECT ? REMEDIATION_REJECTED (NO SSM invocation)

**Expected**: SSM is NEVER invoked when approver rejects

#### Scenario: TIMEOUT - No SSM Execution

**Test**: Service Failure ? Detection ? Incident Creation ? AI Diagnosis ? Risk Assessment ? HITL Pause ? TIMEOUT exceeds ? TIMEOUT_EXCEEDED (NO SSM invocation)

**Expected**: SSM is NEVER invoked when approval times out

#### Scenario: SSM Success + Health Failure

**Test**: Service Failure ? Detection ? Incident Creation ? AI Diagnosis ? Risk Assessment ? HITL Approval ? SSM Execution SUCCESS ? Health Verification FAILS ? RECOVERY_FAILED

**Expected**: Incident status = RECOVERY_FAILED (NOT RESOLVED) even when SSM succeeds

## Test Coverage Reporting

### Coverage Reports

```bash
# Generate coverage report
pytest tests/ --cov=lambdas --cov-report=html --cov-report=xml

# Output format
 coverage/
 +-- coverage-summary.json
 +-- coverage.xml
 +-- htmlcov/
 ¦   +-- index.html
```

### Coverage Thresholds

- Lambda functions: 80% minimum coverage
- Critical paths: 100% coverage
- Error paths: 100% coverage

## Test Execution Schedule

### Local Development

- Run tests before commit
- Run all tests before push
- Run integration tests daily

### CI/CD Pipeline

- Run on every pull request
- Run on every push to main
- Run post-deployment smoke tests

### Scheduled Testing

- Security tests: Daily
- Integration tests: Weekly
- Performance tests: Monthly

## Test Maintenance

### Test Cleanup

- Remove tests for deprecated features
- Update tests for breaking changes
- Archive tests for known issues

### Test Improvement

- Add tests for new features
- Add tests for bug fixes
- Improve test coverage for critical paths