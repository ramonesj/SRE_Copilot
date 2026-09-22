# Product Overview

## Product Name

SRE Copilot

## Product Category

AIOps / SRE Incident Response

## Purpose

AI-assisted incident diagnosis and human-governed remediation for cloud infrastructure.

The SRE Copilot receives infrastructure telemetry, analyzes anomalies using AI, proposes remediations with risk assessments, requires human approval for all state-changing operations, executes approved remediations via AWS Systems Manager, and maintains a complete audit trail.

## Problem Solved

Manual incident diagnosis and remediation is:
- **Slow**: SREs spend hours identifying root causes
- **Error-prone**: Manual analysis can miss subtle patterns
- **Inconsistent**: Different operators respond differently to similar incidents
- **Non-scalable**: As cloud infrastructure grows, manual response becomes unsustainable

The SRE Copilot augments human operators with AI-powered analysis while maintaining human authority over production changes.

## Target Users

- SRE Engineers
- Cloud Engineers
- Platform Engineers
- Infrastructure Engineers
- Operations Teams
- DevOps Teams

## MVP Scope

The MVP implements a single complete scenario:
- **Incident Type**: Critical service failure on EC2/SSM-managed node
- **Detection Source**: CloudWatch Alarms
- **Remediation**: Service restart via SSM Runbook (e.g., restart nginx)
- **Environment**: Development/staging

## Differentiators

### AI-Assisted Root Cause Analysis
- Uses AWS Bedrock (LLM) to analyze error logs and context
- Provides probable root cause with confidence score
- Identifies supporting evidence from logs

### Human-in-the-Loop Approval
- ALL state-changing operations require explicit human approval
- No AI component can bypass the approval boundary
- Configurable approval channels (Email, Slack, Teams)

### Complete Audit Trail
- Immutable audit trail stored in S3
- All decisions, recommendations, approvals, and actions recorded
- Configurable retention (30 days MVP, 1 year production)

### Idempotent Remediation Scripts
- SSM Runbooks designed for safe repeated execution
- Prevents accidental repeated actions

### Verification Loop
- Health verification confirms service recovery after remediation
- SSM success does NOT automatically mean incident resolved
- Only verified recovery leads to RESOLVED status

## Main Cycle

```
Detect → Diagnose → Assess → Approve → Execute → Verify → Audit
```

1. **Detect**: EventBridge receives CloudWatch Alarm
2. **Diagnose**: AI Diagnosis Engine analyzes logs via Bedrock
3. **Assess**: Policy/Risk Engine calculates risk and identifies SSM Runbooks
4. **Approve**: Human-in-the-loop approval for state-changing operations
5. **Execute**: Execution Engine runs approved SSM Runbook
6. **Verify**: Verification Engine confirms service recovery
7. **Audit**: All events recorded in immutable audit trail

## Explicit Statements

### SRE Copilot Does NOT Replace Human Authority
- SRE Copilot assists but does NOT replace human judgment
- AI can recommend, but humans must approve
- All production changes require explicit human authorization
- Operators retain full control over infrastructure

### Remediation Success Criteria
Remediation is considered successful ONLY when:
1. SSM Runbook execution completes successfully AND
2. Health verification confirms service recovery

**Note**: SSM execution success alone does NOT constitute incident resolution.

## Architectural Safety Invariant

The SRE Copilot enforces a strict safety boundary:
- **AI recommends**: The AI Diagnosis Engine analyzes evidence and proposes root causes and remediation actions
- **Policy evaluates**: The Policy/Risk Engine evaluates operational impact and calculates risk scores
- **Human authorizes**: The HITL Approval component provides explicit human authorization for state-changing operations
- **Automation executes**: The Execution Engine executes only pre-authorized actions
- **System verifies**: The Verification Engine checks if remediation achieved desired outcomes
- **Audit records**: The Audit System records all decisions, approvals, executions, and results

**Security Boundary**: AI/LLM components can ONLY diagnose, analyze, and recommend - NEVER execute changes directly.