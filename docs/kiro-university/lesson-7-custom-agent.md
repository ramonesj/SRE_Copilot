# Kiro University Lesson 7

## Custom Agents

### Agent Configuration

- **Agent name**: `sre-copilot-architect`
- **Agent purpose**: Architecture review, HITL validation, security boundary enforcement, MCP-assisted AWS validation, and Step Functions workflow review

### Agent Configuration File

**File**: `.kiro/agents/sre-copilot-architect.json`

### Agent Configuration Details

The agent configuration enables:

- **includePowers**: true - Uses Kiro Powers for context-specific guidance
- **includeMcpJson**: true - Uses workspace MCP configuration for AWS documentation
- **loadProjectContext**: true - Loads project-specific resources
- **useSteeringAsPrimary**: true - Uses Steering Documents as primary guidance

### Agent Capabilities

#### Powers Available

| Power | Purpose |
|-------|---------|
| **aws-step-functions** | Step Functions workflow review, callback pattern validation |
| **aws-observability** | Observability gap analysis, logging validation |
| **aws-devops-agent** | Architecture review, incident investigation |
| **iam-policy-autopilot-power** | IAM policy validation, least-privilege verification |
| **aws-sam** | Serverless deployment validation |

#### MCP Available

| MCP Server | Purpose |
|------------|---------|
| **aws-docs** | AWS documentation validation, API reference lookup |

### Security Invariant

The agent enforces:

**AI recommends. Policy evaluates. Human authorizes. Automation executes. System verifies. Audit records.**

### Validation Tasks

1. **HITR Approval Validation** - APPROVE/REJECT/TIMEOUT paths
2. **Security Boundary Validation** - IAM separation and permissions
3. **Step Functions Validation** - Task Token callback pattern

### Validation Results

✅ **APPROVE validation**: PASS - APPROVE path allows remediation execution

✅ **REJECT validation**: PASS - REJECT path returns REMEDIATION_REJECTED with NO SSM execution

✅ **TIMEOUT validation**: PASS - TIMEOUT path returns TIMEOUT_EXCEEDED with NO SSM execution

✅ **REJECT => NO SSM**: PASS - Invariant maintained

✅ **TIMEOUT => NO SSM**: PASS - Invariant maintained

### How It Works

**Lesson 5**: Kiro Power provides specialized contextual knowledge on demand based on conversation context.

**Lesson 6**: MCP provides external tools/resources that Kiro can actively invoke for AWS documentation retrieval.

**Lesson 7**: Custom Agent orchestrates Steering, Powers, MCP, tools, permissions, and project context into a reusable role.

### Limitations

1. **Static Configuration**: Agent configuration is static and must be updated for new requirements
2. **Manual Invocation**: Agent must be invoked for each validation task (not automated)
3. **No Self-Modification**: Agent cannot modify its own configuration
4. **Context Window**: Limited to available context and tool capabilities

### Validation Summary

| Check | Result |
|-------|--------|
| Custom agent created | YES |
| Agent name | sre-copilot-architect |
| Powers available | YES |
| MCP available | YES |
| Resources loaded | YES |
| Security invariant enforced | YES |
| Validation completed | YES |

### Evidence Path

- **Agent Configuration**: `.kiro/agents/sre-copilot-architect.json`
- **Evidence Document**: `docs/kiro-university/lesson-7-custom-agent.md`

---

**Lesson 7 Status**: COMPLETED

The custom SRE Copilot Architect agent has been created and validated.