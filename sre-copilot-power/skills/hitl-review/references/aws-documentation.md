# AWS Documentation References

Use the aws-docs MCP server for AWS-specific validation.

## Step Functions

### Task Token Callback Pattern

- **Resource**: `arn:aws:states:::sqs:sendMessage.waitForTaskToken`
- **Workflow pauses** until token is returned
- **Timeout**: Configurable (up to 1 year for Standard workflows)

### SendTaskSuccess API

- **Purpose**: Report task completion successfully
- **Parameters**: `taskToken`, `output`
- **Error Codes**: `InvalidToken`, `TaskDoesNotExist`, `TaskTimedOut`

### SendTaskFailure API

- **Purpose**: Report task failure
- **Parameters**: `taskToken`, `error`, `cause`
- **Error Codes**: `InvalidToken`, `TaskDoesNotExist`, `TaskTimedOut`

## IAM Permissions

### Required for Callback Completion

- `states:SendTaskSuccess`
- `states:SendTaskFailure`

### Required for State Machine

- `states:StartExecution`
- `lambda:InvokeFunction`

## AWS Documentation MCP

Use `aws-docs` MCP server for:

- Step Functions callback pattern documentation
- Task Token API reference
- Service integration patterns
- IAM permission requirements