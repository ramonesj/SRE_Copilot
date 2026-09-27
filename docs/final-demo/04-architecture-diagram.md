# SRE Copilot - Architecture Diagram

## Component Flow Diagram

```mermaid
graph TD
    %% Event Sources
    CW[CloudWatch Alarms]
    EB[EventBridge]
    
    %% Component 1: Alert Ingestion
    AI[Alert Ingestion<br/>Lambda]
    
    %% Component 2: Incident Manager
    IM[Incident Manager<br/>Lambda]
    DDB[(DynamoDB<br/>Incident Store)]
    
    %% Component 3: Evidence Collection
    EC[Evidence Collection<br/>Lambda]
    CWL[CloudWatch Logs]
    
    %% Component 4: AI Diagnosis Engine
    ADE[AI Diagnosis Engine<br/>Lambda]
    BR[Amazon Bedrock<br/>LLM]
    
    %% Component 5: Risk Assessment
    RA[Risk Assessment<br/>Lambda]
    
    %% Component 6: HITL Approval Service
    HITL[HITL Approval Service<br/>Lambda]
    APPROVER[👤 Human Approver<br/>Email/Slack/Teams]
    
    %% Component 7: Execution Engine
    EE[Execution Engine<br/>Lambda]
    SSM[Systems Manager<br/>Runbooks]
    
    %% Component 8: Verification Engine
    VE[Verification Engine<br/>Lambda]
    
    %% Component 9: Audit Logger
    AL[Audit Logger<br/>Lambda]
    S3[(S3<br/>Audit Trail)]
    
    %% Flow
    CW -->|Alert| EB
    EB -->|Event| AI
    AI -->|Create| IM
    IM -->|Store| DDB
    IM -->|Trigger| EC
    EC -->|Fetch Logs| CWL
    EC -->|Evidence| ADE
    ADE -->|Analyze| BR
    ADE -->|Diagnosis| RA
    RA -->|Risk Assessment| HITL
    HITL -->|Request Approval| APPROVER
    APPROVER -->|APPROVE/REJECT| HITL
    
    %% Approval Decision Paths
    HITL -->|APPROVE| EE
    HITL -->|REJECT| AL
    HITL -->|TIMEOUT| AL
    
    EE -->|Execute| SSM
    EE -->|Result| VE
    VE -->|Verify Health| CW
    VE -->|Verification Result| IM
    IM -->|Log| AL
    AL -->|Store| S3
    
    %% Security Boundary
    style ADE fill:#ffcccc,stroke:#ff0000,stroke-width:3px
    style EE fill:#ccffcc,stroke:#00ff00,stroke-width:3px
    
    classDef securityBoundary fill:#fff3cd,stroke:#856404,stroke-width:2px,stroke-dasharray: 5 5;
    class HITL securityBoundary
```

---

## Security Architecture Diagram

```mermaid
graph LR
    subgraph "AI Diagnosis Role"
        ADE[AI Diagnosis Engine]
        BR[Bedrock]
        ADE -->|bedrock:InvokeModel| BR
        ADE -.->|❌ NO SSM Permissions| SSM
    end
    
    subgraph "Execution Role"
        EE[Execution Engine]
        SSM[Systems Manager]
        EE -->|ssm:StartExecution| SSM
    end
    
    subgraph "HITL Approval Boundary"
        HITL[HITL Service]
        TOKEN[🔐 Task Token]
        APPROVER[👤 Human]
        HITL -->|Store Token| TOKEN
        HITL -->|Request| APPROVER
        APPROVER -->|Decision| HITL
    end
    
    ADE -->|Diagnosis| HITL
    HITL -->|Approved?| EE
    
    style ADE fill:#ffcccc
    style EE fill:#ccffcc
    style HITL fill:#fff3cd,stroke:#856404,stroke-width:4px
```

---

## Incident Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> CREATED: Alert Received
    CREATED --> EVIDENCE_COLLECTED: Evidence Gathered
    EVIDENCE_COLLECTED --> DIAGNOSIS_COMPLETE: AI Analysis Done
    DIAGNOSIS_COMPLETE --> RISK_ASSESSED: Risk Calculated
    RISK_ASSESSED --> HITL_PENDING: Approval Requested
    
    HITL_PENDING --> APPROVED: Human Approves
    HITL_PENDING --> REMEDIATION_REJECTED: Human Rejects
    HITL_PENDING --> TIMEOUT_EXCEEDED: Timeout
    
    APPROVED --> EXECUTING: SSM Runbook Started
    EXECUTING --> RECOVERY_VERIFIED: Health Check Pass
    EXECUTING --> RECOVERY_FAILED: Health Check Fail
    EXECUTING --> VERIFICATION_ERROR: Verification Error
    
    RECOVERY_VERIFIED --> RESOLVED: Incident Resolved
    RECOVERY_FAILED --> [*]: Manual Intervention
    REMEDIATION_REJECTED --> [*]: No Execution
    TIMEOUT_EXCEEDED --> [*]: No Execution
    VERIFICATION_ERROR --> [*]: Manual Check
    RESOLVED --> [*]: Complete
    
    note right of HITL_PENDING
        🔒 MANDATORY APPROVAL BOUNDARY
        All state changes require
        explicit human authorization
    end note
    
    note right of EXECUTING
        ⚠️ SAFETY INVARIANT
        SSM Success ≠ Recovery Verified
        Health verification required
    end note
```

---

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant CW as CloudWatch
    participant EB as EventBridge
    participant AI as Alert Ingestion
    participant IM as Incident Manager
    participant EC as Evidence Collection
    participant ADE as AI Diagnosis
    participant RA as Risk Assessment
    participant HITL as HITL Approval
    participant Human as 👤 Approver
    participant EE as Execution Engine
    participant SSM as Systems Manager
    participant VE as Verification Engine
    participant AL as Audit Logger
    
    CW->>EB: Alert Triggered
    EB->>AI: Event
    AI->>IM: Create Incident
    IM->>EC: Collect Evidence
    EC->>ADE: Analyze
    ADE->>RA: Assess Risk
    RA->>HITL: Request Approval
    
    alt APPROVE
        HITL->>Human: Send Request
        Human->>HITL: APPROVE
        HITL->>EE: Execute Remediation
        EE->>SSM: Run Runbook
        SSM->>VE: Verify Recovery
        VE->>IM: Update Status
        IM->>AL: Log Audit
    else REJECT
        HITL->>Human: Send Request
        Human->>HITL: REJECT
        HITL->>AL: Log Rejection
        Note over HITL,SSM: ❌ NO SSM EXECUTION
    else TIMEOUT
        HITL->>HITL: Timeout Expired
        HITL->>AL: Log Timeout
        Note over HITL,SSM: ❌ NO SSM EXECUTION
    end
```

---

## Component Responsibilities

| Component | Responsibility | IAM Permissions | Constraint |
|-----------|---------------|-----------------|------------|
| **Alert Ingestion** | Receive and validate events | `events:PutEvents` | Read-only validation |
| **Incident Manager** | Lifecycle management | `dynamodb:*` | No execution permissions |
| **Evidence Collection** | Gather logs and telemetry | `logs:GetLogEvents` | Read-only access |
| **AI Diagnosis Engine** | Analyze and diagnose | `bedrock:InvokeModel` | ❌ NO SSM permissions |
| **Risk Assessment** | Calculate risk scores | `ssm:ListDocuments` (read) | ❌ NO execution |
| **HITL Approval** | Request human approval | `secretsmanager:GetSecretValue` | No execution permissions |
| **Execution Engine** | Execute approved runbooks | `ssm:StartExecution` | Requires prior approval |
| **Verification Engine** | Verify service recovery | `cloudwatch:GetMetricData` | Read-only verification |
| **Audit Logger** | Record all events | `s3:PutObject` | Write-only audit |

---

## Security Boundaries

### 1. IAM Role Separation

```mermaid
graph TB
    subgraph "AI Diagnosis Role (NO EXECUTION)"
        ADE[AI Diagnosis Engine]
        ADE -->|bedrock:InvokeModel| BR[Bedrock]
        ADE -.->|❌ DENIED| SSM[SSM]
    end
    
    subgraph "Execution Role (APPROVED ONLY)"
        EE[Execution Engine]
        EE -->|ssm:StartExecution| SSM
    end
    
    subgraph "Audit Role (WRITE ONLY)"
        AL[Audit Logger]
        AL -->|s3:PutObject| S3[S3 Audit]
    end
```

### 2. Task Token Security

- Tokens are **NEVER** logged
- Encrypted in Secrets Manager
- Time-bound (expires after timeout)
- Single-use (invalidated after use)

### 3. Approval Boundary Enforcement

```mermaid
graph LR
    A[Diagnosis] -->|Recommend| B[HITL Approval]
    B -->|APPROVE| C[Execute]
    B -->|REJECT| D[No Execution]
    B -->|TIMEOUT| E[No Execution]
    
    style B fill:#fff3cd,stroke:#856404,stroke-width:4px
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph AWS Cloud
        subgraph "Event Layer"
            EB[EventBridge]
            CW[CloudWatch]
        end
        
        subgraph "Compute Layer"
            L1[Lambda: Alert Ingestion]
            L2[Lambda: Incident Manager]
            L3[Lambda: Evidence Collection]
            L4[Lambda: Diagnosis Engine]
            L5[Lambda: Risk Assessment]
            L6[Lambda: HITL Approval]
            L7[Lambda: Execution Engine]
            L8[Lambda: Verification Engine]
            L9[Lambda: Audit Logger]
        end
        
        subgraph "Orchestration Layer"
            SF[Step Functions<br/>State Machine]
        end
        
        subgraph "Data Layer"
            DDB[(DynamoDB)]
            S3[(S3 Audit)]
            SM[Secrets Manager]
        end
        
        subgraph "AI Layer"
            BR[Amazon Bedrock]
        end
        
        subgraph "Execution Layer"
            SSM[Systems Manager]
            EC2[EC2 Instances]
        end
    end
    
    EB --> L1
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> BR
    L4 --> L5
    L5 --> L6
    L6 --> SF
    SF --> L7
    L7 --> SSM
    SSM --> EC2
    L7 --> L8
    L8 --> L2
    L2 --> L9
    L9 --> S3
```

---

## Key Messages for Demo

### Safety Invariant Message

> **"SSM execution success alone does NOT mark incidents as RESOLVED.  
> Health verification is REQUIRED for RESOLVED status."**

### Security Boundary Message

> **"AI components can ONLY recommend, NEVER execute directly.  
> All state-changing operations require human approval."**

### Human Authority Message

> **"SRE Copilot assists but does NOT replace human judgment.  
> AI recommends, humans authorize."**

---

**Document Version**: 1.0  
**Last Updated**: September 26, 2026
