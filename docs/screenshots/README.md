# SRE Copilot - Screenshots & Visual Artifacts Index

This catalog documents the user interface states and architectural evidence for the **SRE Copilot** submission.

---

## Visual Artifact Index

| # | Screen / State | Route / Location | Architectural Component | Key Observations |
|:---|:---|:---|:---|:---|
| **1** | **Dashboard** | `http://localhost:3000/` | Global Health & Analytics | Displays 10 total incidents, 7 active, 3 resolved, 2 pending approvals. Severity & Status Pie/Bar charts live. |
| **2** | **Incident List** | `http://localhost:3000/incidents` | Incident Manager | Live table with ID, Service, Severity badges, Status badges, Instance ID, and Date. Filters by status & severity. |
| **3** | **Incident Detail** | `http://localhost:3000/incidents/:id` | Incident Orchestration | Full lifecycle view showing service details, error logs, and state transitions. |
| **4** | **Diagnosis Engine** | Incident Detail / Approvals | AI Diagnosis (Bedrock) | Displays isolated root cause analysis, confidence rating (e.g., 94%), and recommended remediation. |
| **5** | **Risk Assessment** | Incident Detail / Approvals | Policy & Risk Engine | Displays PBT-validated operational risk score (0–100), risk classification badge, and target SSM runbook. |
| **6** | **HITL Approval View** | `http://localhost:3000/approvals` | HITL Boundary | Displays pending authorization cards with Diagnosis + Risk summaries, and explicit **Approve** / **Reject** buttons. |
| **7** | **Execution Engine** | Incident Timeline / Audit | SSM Automation | Records pre-authorized SSM runbook execution logs and output parameters. |
| **8** | **Health Verification** | Incident Timeline / Audit | Verification Probes | Active health check inspection verifying port availability, latency benchmarks, and socket response. |
| **9** | **Audit Logs** | `http://localhost:3000/audit` | Immutable Audit Trail | Paginated table with timestamp, action type, actor, incident ID, target, and CSV export functionality. |
| **10** | **State: RESOLVED** | Incident List & Dashboard | Recovery Verification SUCCESS | Incident `INC-A1B2C3D4E5F1` — Verified happy path after explicit human approval and passing health probes. |
| **11** | **State: RECOVERY_FAILED** | Incident List | Safety Invariant Proof | Incident `INC-B1C2D3E4F5A1` — Demonstrates $\text{Execution Success} \neq \text{Recovery Verified}$ (SSM exit 0, but health check failed). |
| **12** | **State: REJECTED** | Incident List | Reject Boundary | Incident `INC-C1D2E3F4A5B1` — Demonstrates $\text{REJECT} \Longrightarrow \text{NO EXECUTION}$ (Status: `REMEDIATION_REJECTED`). |
| **13** | **State: TIMEOUT** | Incident List | Timeout Boundary | Incident `INC-D1E2F3A4B5C1` — Demonstrates $\text{TIMEOUT} \Longrightarrow \text{NO EXECUTION}$ (Status: `TIMEOUT_EXCEEDED`). |

---

## Instructions for Capturing Submission Media

1. Open Chrome/Edge at `http://localhost:3000/`.
2. Capture full-page screenshots of:
   - Dashboard (`/`)
   - Incidents Table (`/incidents`) with status filters active
   - Pending Approvals (`/approvals`)
   - Audit Logs (`/audit`) with CSV export action
3. Run the live demo script in terminal:
   ```bash
   python demo_end_to_end.py
   ```
4. Record the video walkthrough following the flow defined in [docs/final-demo/video-walkthrough.md](file:///e:/mis_proyectos/SRE_Copilot/docs/final-demo/video-walkthrough.md).
