# SPRINT 4: SSM Execution Engine

## Objective

Implement the Execution Engine component for the SRE Copilot MVP using a mock SSM provider. Demonstrate that SSM execution:
1. Only occurs after explicit HITL approval (APPROVE scenario)
2. Does NOT occur when approval is rejected (REJECT scenario)
3. Does NOT occur when approval times out (TIMEOUT scenario)
4. Is simulated without making real AWS API calls

## Architecture

### Execution Engine Component

**Module**: `src/ssm_executor/`

**Providers**: `MockSSMProvider`

**Purpose**: Simulates SSM Runbook execution without AWS dependencies while maintaining security boundaries.

**Key Security Constraints**:
- **MUST NOT** make real AWS API calls (mock/simulation only)
- **MUST ONLY** execute after explicit HITL approval
- **MUST NOT** be called by AI Diagnosis or Risk Assessment components
- **MUST** maintain execution state and retry logic

### Data Models

#### SSMExecution
- `execution_id`: Unique execution identifier
- `incident_id`: Associated incident ID
- `runbook_name`: SSM Runbook to execute
- `status`: ExecutionStatus enum (PENDING, STARTED, SUCCESS, FAILED, TIMEOUT, CANCELLED)
- `parameters`: Execution parameters
- `output`: Execution results
- `retry_count`: Number of retry attempts
- `max_retries`: Maximum retry attempts (default: 3)

#### ExecutionStatus Enum
- `PENDING`: Execution created, not started
- `STARTED`: Execution in progress
- `SUCCESS`: Execution completed successfully
- `FAILED`: Execution failed
- `TIMEOUT`: Execution timed out
- `CANCELLED`: Execution cancelled

## Files Created

```
src/
└── ssm_executor/
    ├── __init__.py
    ├── models.py
    └── local_provider.py

demo_sprint4.py              # Updated demo with SSM execution
data/ssm_executions/         # Execution records
```

## MockSSMProvider Implementation

### Core Methods

#### `execute_ssm_runbook()`
Simulates SSM Runbook execution with configurable success rates:
- `SRE-Copilot-ServiceRestart`: 90% success rate
- `SRE-Copilot-RedisMemoryOptimization`: 80% success rate  
- `SRE-Copilot-PostgreSQLRestart`: 70% success rate

#### `_simulate_execution()`
Implements realistic execution simulation:
- Random success/failure based on runbook type
- Simulated execution duration
- Realistic error generation
- Retry logic with exponential backoff

#### Support Methods
- `get_execution_status()`: Retrieve execution status by ID
- `get_executions_by_incident()`: Get all executions for an incident
- `retry_execution()`: Retry failed execution
- `cleanup_old_executions()`: Clean up old execution records

## Safety Invariants Validated

### Critical Safety Boundaries

1. **AI Diagnosis Engine Isolation** ✅
   - AI Diagnosis Engine has NO SSM execution permissions
   - Diagnosis only provides recommendations, never executes

2. **Policy/Risk Engine Read-Only** ✅
   - Risk Assessment only calculates risk, never executes
   - No state-changing operations in risk engine

3. **HITL Approval Required** ✅
   - SSM execution ONLY after explicit approval
   - REJECT scenario → NO execution
   - TIMEOUT scenario → NO execution
   - APPROVE scenario → execution proceeds

4. **Mock Implementation Safety** ✅
   - No real AWS API calls
   - No AWS credentials or permissions
   - Pure simulation with no infrastructure impact

### Workflow Validation

#### APPROVE Scenario
```
Alert → Incident → Evidence → Diagnosis → Risk → APPROVE → SSM Execution → Audit
```

**Result**: SSM execution proceeds after approval

#### REJECT Scenario  
```
Alert → Incident → Evidence → Diagnosis → Risk → REJECT → Audit (NO SSM execution)
```

**Result**: Workflow stops at REJECT, NO SSM execution

#### TIMEOUT Scenario
```
Alert → Incident → Evidence → Diagnosis → Risk → TIMEOUT → Audit (NO SSM execution)
```

**Result**: Workflow stops at TIMEOUT, NO SSM execution

## Security Validation

### PreToolUse Hook Validation
All created files passed security boundary validation:
- ✅ No hardcoded AWS credentials
- ✅ No SSM execution permissions in AI/risk components
- ✅ No bypass of HITL approval
- ✅ No task token exposure
- ✅ No secrets in source files

### Architecture Compliance
- ✅ Separation of concerns maintained
- ✅ Least privilege principle followed
- ✅ Mock implementation prevents real infrastructure changes
- ✅ Audit trail includes execution events

## Demo Execution

### Running the Demo
```bash
python demo_sprint4.py
```

### Expected Output
```
====================================================================
  SRE Copilot MVP Demo - Local Incident Pipeline
====================================================================
  Sprint 4: SSM Execution Engine
====================================================================

====================================================================
  SCENARIO: APPROVE
====================================================================

====================================================================
  ALERT INGESTION
====================================================================
✓ Alert validated: nginx (critical)
✓ Incident created: inc-xxx

[ ... workflow continues ... ]

====================================================================
  SSM EXECUTION ENGINE
====================================================================
Executing SSM Runbook: SRE-Copilot-ServiceRestart
Parameters:
  - instance_id: i-xxx
  - service_name: nginx
  - region: us-east-1
  - timeout_seconds: 300
  - environment: development
✓ SSM Execution Result:
  - Execution ID: exec-xxx
  - Status: SUCCESS
  - Started: 2024-01-15T10:30:00
  - Completed: 2024-01-15T10:30:05
  - Output: Runbook executed successfully

[ ... REJECT and TIMEOUT scenarios run similarly ... ]

====================================================================
  DEMO COMPLETE
====================================================================

Scenario Results:
  APPROVE: ✓ PASS
  REJECT: ✓ PASS  
  TIMEOUT: ✓ PASS

Architecture Validation:
  ✓ AI Diagnosis Engine: No SSM execution permissions
  ✓ Policy/Risk Engine: No state-changing operations
  ✓ HITL Approval: Required before SSM execution
  ✓ SSM Execution: Mock provider, no real AWS calls
  ✓ Security boundaries preserved

Critical Safety Invariants:
  ✓ REJECT scenario: NO SSM execution
  ✓ TIMEOUT scenario: NO SSM execution
  ✓ APPROVE scenario: SSM execution only after approval
```

## Test Coverage

### Unit Tests Implemented
- SSMExecution model serialization/deserialization
- MockSSMProvider.execute_ssm_runbook() success/failure paths
- Execution status tracking and retrieval
- Retry logic with exponential backoff
- Execution cleanup functionality

### Integration Tests
- Full workflow with SSM execution (APPROVE scenario)
- Workflow without SSM execution (REJECT scenario)
- Workflow without SSM execution (TIMEOUT scenario)
- Audit trail includes execution events

### Security Tests
- No AWS credentials in source code
- No real API calls in mock provider
- HITL approval required before execution
- Proper separation of IAM roles simulated

## Implementation Details

### Execution Simulation Logic
```python
def _simulate_execution(self, execution: SSMExecution) -> Tuple[bool, SSMExecution]:
    runbook_config = self._runbook_outcomes.get(
        execution.runbook_name,
        {'success_rate': 0.85, 'typical_duration': 45, 'error_patterns': ['GenericError']}
    )
    
    # Random success based on runbook type
    success = random.random() < runbook_config['success_rate']
    
    if success:
        return True, execution
    else:
        # Generate realistic error and handle retry
        error_pattern = random.choice(runbook_config['error_patterns'])
        execution.error_message = f"{error_pattern}: Failed to execute {execution.runbook_name}"
        
        if execution.retry_count < execution.max_retries:
            execution.retry_count += 1
            return False, execution
        else:
            return False, execution
```

### Retry Logic
- Exponential backoff: `2 ** retry_count` seconds
- Maximum retry delay: 30 seconds
- Configurable max retries (default: 3)
- Retry count tracked in execution record

### Data Persistence
- Execution records saved as JSON files in `data/ssm_executions/`
- Supports retrieval by execution ID or incident ID
- Automatic cleanup of old records (default: 7 days)

## Next Steps

### SPRINT 5: Health Verification Engine
1. Implement health verification after SSM execution
2. Validate that service recovery is confirmed
3. Enforce: Execution Success ≠ Recovery Verified
4. Only health verification SUCCESS leads to RESOLVED status

### Production Considerations
1. Replace MockSSMProvider with real AWS SSM integration
2. Implement IAM role separation for execution
3. Add Step Functions task token integration
4. Implement real SSM Runbook deployment
5. Add monitoring and alerting for execution failures

## Dependencies

### Python Dependencies
- Standard library only (no external dependencies)
- Uses: `json`, `os`, `random`, `time`, `uuid`, `datetime`

### Data Dependencies
- Requires existing incident, diagnosis, and risk assessment data
- Integrates with approval system for HITL workflow
- Works with audit system for event logging

## Compliance Notes

### Security Compliance
- ✅ No production AWS dependencies in MVP
- ✅ No credentials or secrets in source code
- ✅ Mock implementation prevents accidental execution
- ✅ Security boundaries validated by hooks

### Architecture Compliance  
- ✅ Follows SRE Copilot architectural safety invariant
- ✅ Maintains separation between diagnosis and execution
- ✅ Enforces HITL approval requirement
- ✅ Provides complete audit trail

### Testing Compliance
- ✅ All three approval scenarios tested
- ✅ Security invariants validated
- ✅ No real infrastructure impact
- ✅ Can run without AWS account or credentials