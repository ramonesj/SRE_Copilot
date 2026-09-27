# SRE Copilot - Final Video Walkthrough & Presentation Script

**Kiro University Final Exam Demonstration**  
**System**: SRE Copilot (Human-Governed Autonomous Incident Remediation)  
**Safety Invariant**: *AI recommends. Policy evaluates. Human authorizes. Automation executes. System verifies. Audit records.*

---

## Video Recording Checklist & Timeline (Total Duration: 5–7 Minutes)

| Stage | Step / Scene | Visual Focus | Key Architectural Takeaway |
|:---|:---|:---|:---|
| **00:00 - 00:45** | **1. Dashboard Overview** | `http://localhost:3000/` | Real-time KPI Cards (Total, Active, Resolved, Pending) + Severity & Status Charts. Single source of truth. |
| **00:45 - 01:30** | **2. Incident Ingestion & Lifecycle** | `http://localhost:3000/incidents` | Incident list, severity/status filters, pagination, and incident lifecycle transitions. |
| **01:30 - 02:15** | **3. Evidence Collection** | Incident Details / Evidence API | Automated log extraction, metrics inspection, and trace correlation without mutating infrastructure. |
| **02:15 - 03:00** | **4. AI Diagnosis Engine** | Bedrock AI Analysis | Root cause isolation and recommended remediation with confidence score (Read-only; zero SSM access). |
| **03:00 - 03:45** | **5. Policy & Risk Engine (PBT Validated)** | Risk Assessment View | Independent calculation of operational risk (0–100) bound to policy, independent of AI confidence. |
| **03:45 - 04:30** | **6. Human-in-the-Loop (HITL) Approval** | `http://localhost:3000/approvals` | Explicit operator authorization boundary. Task Token callback pattern (APPROVE vs REJECT). |
| **04:30 - 05:15** | **7. Execution Engine (SSM Automation)** | Execution Logs / Console | Pre-authorized SSM runbook execution ONLY after explicit human approval. |
| **05:15 - 06:00** | **8. Health Verification Engine** | Health Probes / Resolution Check | Verification of actual system health. Crucial rule: **Execution Success $\neq$ Recovery Verified**. |
| **06:00 - 06:45** | **9. Immutable Audit Trail** | `http://localhost:3000/audit` | Complete event timeline: Actor, Action, Target, IP, Details, and CSV Export. |
| **06:45 - 07:15** | **10. Resolution & Invariant Wrap-up** | Dashboard & Incident State | Transition to `RESOLVED` vs `RECOVERY_FAILED` vs `REMEDIATION_REJECTED`. |

---

## 4 Core Architectural Workflow Demonstrations

### Path 1: The Happy Path (Deterministic Recovery)
```
Alert Ingested (CRITICAL)
  └── AI Diagnosis (Root Cause Identified, Confidence: 94%)
        └── Policy Risk Evaluated (45/100 MEDIUM)
              └── Operator Authorizes (APPROVE in UI)
                    └── SSM Automation Executes (Exit Code 0)
                          └── Health Verification Probes (SUCCESS / HEALTHY)
                                └── Status -> RESOLVED (Audit Trail Recorded)
```
- **Demonstration**: In `http://localhost:3000/approvals`, select pending incident `INC-E1F2A3B4C5D1`, review diagnosis & risk, enter rationale *"Authorized rolling fix after load review"*, click **Approve**.
- **Result**: Incident state transitions to `RESOLVED`. Audit log records human approver identity.

---

### Path 2: Safety Invariant Path (Execution Success $\neq$ Recovery Verified)
```
SSM Runbook Executes (Exit Code 0 - SUCCESS)
  └── Active Health Probes Triggered
        └── Probes Detect Unhealthy Sockets (FAILURE)
              └── Status -> RECOVERY_FAILED (NEVER RESOLVED)
```
- **Demonstration**: Inspect incident `INC-B1C2D3E4F5A1` in the incident list.
- **Architectural Proof**: Shows that even though the automation script returned exit code 0, because endpoint health probes failed, the incident was blocked from reaching `RESOLVED` and placed into `RECOVERY_FAILED`.

---

### Path 3: The Reject Path (Zero Execution Boundary)
```
AI Proposes Hard Reboot (Risk: 85/100 CRITICAL)
  └── Operator Evaluates Traffic Surge
        └── Operator Clicks REJECT (with rationale)
              └── Step Functions Routes to HandleRejection
                    └── SSM Execution BLOCKED (Status -> REMEDIATION_REJECTED)
```
- **Demonstration**: Inspect incident `INC-C1D2E3F4A5B1`.
- **Architectural Proof**: Demonstrates that $\text{REJECT} \Longrightarrow \text{NO EXECUTION}$. SSM is never invoked.

---

### Path 4: The Timeout Path (Fail-Safe Boundary)
```
Task Token Issued (Wait for Approval Callback)
  └── Operator Response Window Expires (3600s)
        └── States.Timeout Triggered
              └── SSM Execution BLOCKED (Status -> TIMEOUT_EXCEEDED)
```
- **Demonstration**: Inspect incident `INC-D1E2F3A4B5C1`.
- **Architectural Proof**: Demonstrates that $\text{TIMEOUT} \Longrightarrow \text{NO EXECUTION}$. Workflows fail-safe.

---

## Presentation Talking Points for the Examiner

1. **Autonomous but Strictly Governed**: AI provides recommendations, but cannot execute mutating actions.
2. **Property-Based Verification**: Proved via Hypothesis PBT that operational risk cannot exceed $[0, 100]$ and remains independent of AI hallucination/confidence.
3. **Enterprise Auditability**: Every decision, prompt, token issuance, and probe result is recorded in the unified audit trail.
