# Lesson 5: AWS Step Functions Power Demonstration

## Overview

This lesson demonstrates the activation and use of the AWS Step Functions Power for analyzing the SRE Copilot Human-in-the-Loop (HITL) orchestration architecture.

## Power Activation Summary

### Power Information

- **Power installed**: YES
- **Power activated on demand**: YES
- **Power name**: aws-step-functions
- **Activation context/keywords**: step functions, state machine, serverless, jsonata, asl, amazon states language, workflow, orchestration

### Specialized Knowledge Loaded

The AWS Step Functions Power provides comprehensive guidance for:
- ASL structure and JSONata expression syntax
- Eight available workflow states (Task, Pass, Choice, Wait, Succeed, Fail, Parallel, Map)
- `$states` reserved variable and variable assignment with `Assign`
- Error handling with Retry and Catch
- AWS Service integration patterns (optimized, SDK, HTTP)
- Architecture patterns (polling, saga, human-in-the-loop, semaphore)
- Data transformation with JSONata
- State input/output handling
- Validation and testing

## HITL Orchestration Analysis

### Current Design Review

The SRE Copilot HITL workflow uses AWS Step Functions to orchestrate:
1. Alert event ingestion from EventBridge
2. Incident creation and evidence collection
3. AI diagnosis via Bedrock
4. Risk assessment calculation
5. **HITL approval wait state with Task Token callback**
6. SSM execution only after explicit approval
7. Health verification
8. Audit trail recording

### Key Assessment Points

#### 1. AWS Step Functions Orchestration

**Assessment**: The state machine architecture aligns with AWS Step Functions best practices for orchestrating distributed workflows with human approval.

**Power Guidance Applied**:
- Standard workflow selected (supports long duration and callbacks)
- Task Token pattern for human-in-the-loop approval
- Choice states for branching APPROVE/REJECT/TIMEOUT

#### 2. Callback Integration Pattern

**Assessment**: The `.waitForTaskToken` callback pattern is correctly identified in the requirements.

**Power Guidance Applied**:
- Standard workflow supports `.waitForTaskToken` (Express workflows do not)
- Callback pattern documented in service-integrations.md
- External system must call `SendTaskSuccess` or `SendTaskFailure`

#### 3. waitForTaskToken

**Assessment**: The `waitForTaskToken` integration pattern is appropriate for the HITL approval use case.

**Power Guidance Applied**:
- Resource ARN format: `arn:aws:states:::sqs:sendMessage.waitForTaskToken`
- Task Token available via `$$.Task.Token` in Step Functions context
- Execution pauses until token is returned (maximum 1 year for Standard workflows)

#### 4. $$.Task.Token

**Assessment**: The Task Token context variable must be extracted and stored securely by the approval Lambda.

**Power Guidance Applied**:
- Task Token is available in `$$.context.Task.Token` in JSONata expressions
- Task Tokens are sensitive callback credentials and must be:
  - never appear in application logs
  - never appear in user-facing interfaces
  - never be included in EventBridge events
  - accessible only by the authorized callback component
  - associated securely with the correct approval request and workflow execution
  - remain protected at rest if persisted
- The exact protected persistence mechanism must follow the approved SRE Copilot design and security steering
- Token should never appear in logs

#### 5. Human-in-the-Loop Approval

**Assessment**: The approval pattern aligns with the human-in-the-loop architecture pattern from the Power's steering guides.

**Power Guidance Applied**:
- See `architecture-patterns.md` human-in-the-loop with timeout escalation
- Multiple approval levels can be chained with timeout escalation
- Timeout causes automatic rejection after configurable period

#### 6. APPROVE Path

**Assessment**: The APPROVE path must transition to SSM execution state.

**Power Guidance Applied**:
- Choice state checks `$.approval.decision == "APPROVE"`
- Must not include SSM execution in same state as approval task
- Decision must be explicit string comparison

#### 7. REJECT Path

**Assessment**: The REJECT path must update status to REMEDIATION_REJECTED with NO SSM execution.

**Power Guidance Applied**:
- Choice state checks `$.approval.decision == "REJECT"`
- Routes to "HandleRejection" state
- SSM executor Lambda must not be invoked

#### 8. TIMEOUT Path

**Assessment**: The TIMEOUT path must update status to TIMEOUT_EXCEEDED with NO SSM execution.

**Power Guidance Applied**:
- Catch block for `States.Timeout` error
- Routes to "HandleTimeout" state
- SSM executor Lambda must not be invoked

#### 9. SSM Execution Prevention Before APPROVE

**Assessment**: The architectural safety invariant is correctly enforced.

**Power Guidance Applied**:
- Choice state ensures SSM executor only reachable after explicit approval
- REJECT and TIMEOUT paths do not include SSM execution
- Each component has separate IAM roles with least-privilege permissions

#### 10. Retry and Error-Handling Behavior

**Assessment**: Comprehensive error handling is required for all states.

**Power Guidance Applied**:
- See `error-handling.md` for Retry and Catch configuration
- Built-in error codes: `States.Timeout`, `States.TaskFailed`, `States.Permissions`, `States.QueryEvaluationError`
- Custom error names allowed (must NOT start with `States.`)
- `States.ALL` must appear alone and as last Catch entry

#### 11. Task Token Security

**Assessment**: Task Tokens must be handled securely.

**Power Guidance Applied**:
- Token stored encrypted (Secrets Manager recommended)
- Token never logged or exposed in error messages
- Token single-use (invalidated after first use)
- Token time-bound (expires after configurable period)

#### 12. Least-Privilege Permissions

**Assessment**: Each state machine role needs minimal permissions.

**Power Guidance Applied**:
- State machine role needs `states:StartExecution` for nested workflows
- Lambda integration needs `lambda:InvokeFunction`
- Task Token pattern needs `states:SendTaskSuccess` and `states:SendTaskFailure`
- DynamoDB lock needs `dynamodb:PutItem`, `dynamodb:UpdateItem`, `dynamodb:DeleteItem`

## Recommendations from Power Context

### 1. JSONata Configuration

**Recommendation**: Enable JSONata at the top level of the state machine definition.

**Reason**: Modern, preferred way to reference and transform data in ASL. Replaces JSONPath I/O fields with `Arguments` and `Output`.

```json
{
  "QueryLanguage": "JSONata",
  "StartAt": "ValidateEvent",
  "States": {
    ...
  }
}
```

### 2. Task Token Storage

**Recommendation**: Store Task Tokens using the protected persistence mechanism defined in the SRE Copilot security design.

**Reason**: Task Tokens are sensitive callback credentials. Power guidance emphasizes never exposing tokens in logs or error messages, and requiring secure storage per the approved security architecture.

### 3. Error Handling

**Recommendation**: Implement comprehensive Retry and Catch for all Task states.

**Reason**: External systems (Bedrock, SSM) can fail transiently or permanently. Power guidance recommends:
- Retry for transient errors with exponential backoff
- Catch for all errors with fallback state
- Guard all variable references with `$exists()` in JSONata

### 4. Lambda Integration

**Recommendation**: Use optimized Lambda integration (`arn:aws:states:::lambda:invoke`) instead of SDK.

**Reason**: More efficient, recommended pattern for Lambda invocation.

### 5. Variable Scope

**Recommendation**: Use `Assign` to store variables instead of threading through Output.

**Reason**: Clean separation of concerns. `Assign` and `Output` are evaluated in parallel in the same state.

## Safe Demonstration Performed

### Demonstration Steps

1. **Power Installation Verified**: Confirmed aws-step-functions power is installed
2. **Power Activation**: Activated power using `action="activate"`
3. **Steering Files Loaded**: Review of architecture-patterns.md, error-handling.md, service-integrations.md
4. **Documentation Analysis**: Reviewed SRE Copilot HITL requirements, design, and tasks
5. **Architecture Review**: Analyzed HITL orchestration against Power guidance
6. **Recommendations Generated**: 5 specific recommendations for improvement

### Key Findings

- State machine architecture aligns with AWS best practices
- Human-in-the-loop pattern correctly implemented using Task Tokens
- Error handling requirements addressed by Power guidance
- JSONata configuration recommended for modern ASL
- Security recommendations for Token management

## Result

The AWS Step Functions Power successfully provided specialized guidance for:
- Validating the HITL orchestration architecture
- Identifying compliance with AWS best practices
- Generating specific recommendations for improvement
- Ensuring architectural safety invariant is maintained

## Limitations

### Power Limitations

1. **No State Machine Execution**: Power provides guidance, not execution of the state machine
2. **No Real-World Testing**: Guidance is theoretical; actual deployment testing required
3. **No Cost Analysis**: Power does not provide cost estimates for the workflow

### Context Limitations

1. **Assumes Standard Workflow**: Power assumes Standard workflow (not Express) for long-running approvals
2. **JSONata Default**: Power assumes JSONata mode (not JSONPath)
3. **No Environment Details**: Power guidance is generic; environment-specific adjustments needed

## Documentation Files Reviewed

### SRE Copilot HITL Documentation
- `.kiro/specs/sre-copilot-hitl/requirements.md`
- `.kiro/specs/sre-copilot-hitl/design.md`
- `.kiro/specs/sre-copilot-hitl/tasks.md`

### Steering Documents
- `.kiro/steering/architecture.md`
- `.kiro/steering/deployment.md`
- `.kiro/steering/product.md`
- `.kiro/steering/security.md`
- `.kiro/steering/technology.md`

### Power Steering Files
- `architecture-patterns.md` - Human-in-the-loop pattern
- `error-handling.md` - Retry and Catch configuration
- `service-integrations.md` - Task Token callback pattern
- `asl-state-types.md` - State machine states
- `processing-state-inputs-and-outputs.md` - Data handling

## Conclusion

The AWS Step Functions Power successfully demonstrated contextual activation and contributed specialized guidance for the SRE Copilot HITL orchestration. The Power validated the architecture against AWS best practices and provided 5 specific recommendations for improvement.

**Lesson 5 Status**: COMPLETED

**Ready to begin Lesson 6 when user is ready.**