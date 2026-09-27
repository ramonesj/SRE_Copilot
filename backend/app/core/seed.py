"""
Demo Data Seeder - Populates PostgreSQL with realistic SRE Copilot data
Guarantees UI consistency across Dashboard, Incidents, Approvals, and Audit.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.evidence import Evidence, EvidenceType
from app.models.risk import RiskAssessment, RiskClassification
from app.models.approval import Approval, ApprovalStatus
from app.models.audit import AuditLog, AuditAction


async def seed_database(db: AsyncSession):
    """Seed the database with 10 realistic incidents and associated data"""
    # Check if data already exists
    count_query = select(func.count(Incident.id))
    count = await db.scalar(count_query)
    if count and count >= 10:
        return {"status": "already_seeded", "count": count}

    # Clear any partial data
    await db.execute(delete(AuditLog))
    await db.execute(delete(Approval))
    await db.execute(delete(RiskAssessment))
    await db.execute(delete(Evidence))
    await db.execute(delete(Incident))
    await db.commit()

    now = datetime.utcnow()

    incident_definitions = [
        # --- 3 RESOLVED (Happy Path: APPROVE -> EXECUTION_SUCCESS -> VERIFICATION_SUCCESS -> RESOLVED) ---
        {
            "code": "INC-A1B2C3D4E5F1",
            "title": "Nginx Service Ingress HTTP 502 Outage",
            "description": "Upstream connection pool exhaustion on nginx ingress proxy causing elevated 502 errors.",
            "service": "nginx-ingress",
            "instance_id": "i-0a1b2c3d4e5f60001",
            "severity": IncidentSeverity.CRITICAL,
            "status": IncidentStatus.RESOLVED,
            "created_offset": 120,
            "resolved_offset": 105,
            "root_cause": "nginx worker thread saturation and socket leak",
            "recommended_action": "Execute SRE-Copilot-ServiceRestart and socket recycle",
            "risk_score": 45.0,
            "risk_class": RiskClassification.MEDIUM,
            "runbook": "SRE-Copilot-ServiceRestart",
            "approval_status": ApprovalStatus.APPROVED,
            "approver": "sre-lead@company.com",
            "approval_rationale": "Service restart approved after traffic re-route verification.",
            "audit_events": [
                (AuditAction.CREATE, "CloudWatch Alert: Nginx 502 rate > 5%"),
                (AuditAction.RISK_ASSESS, "Automated Risk Calculation: 45/100 (MEDIUM)"),
                (AuditAction.APPROVE, "Human Authorization granted by sre-lead@company.com"),
                (AuditAction.UPDATE, "SSM Execution completed successfully"),
                (AuditAction.UPDATE, "Health Verification SUCCESS - Endpoints healthy - Status: RESOLVED")
            ]
        },
        {
            "code": "INC-A1B2C3D4E5F2",
            "title": "Payment API Memory Pressure & Latency Spike",
            "description": "Garbage collection pauses in payment-service container causing p99 latency spike to 4500ms.",
            "service": "payment-api",
            "instance_id": "i-0a1b2c3d4e5f60002",
            "severity": IncidentSeverity.HIGH,
            "status": IncidentStatus.RESOLVED,
            "created_offset": 180,
            "resolved_offset": 160,
            "root_cause": "Heap memory fragmentation under high load",
            "recommended_action": "Execute SRE-Copilot-ContainerRestart and cache purge",
            "risk_score": 50.0,
            "risk_class": RiskClassification.MEDIUM,
            "runbook": "SRE-Copilot-ContainerRestart",
            "approval_status": ApprovalStatus.APPROVED,
            "approver": "payments-oncall@company.com",
            "approval_rationale": "Approved rolling restart of payment pods.",
            "audit_events": [
                (AuditAction.CREATE, "Prometheus Alert: payment_api_p99_latency > 3s"),
                (AuditAction.RISK_ASSESS, "Risk Assessment: 50/100 (MEDIUM)"),
                (AuditAction.APPROVE, "HITL Authorization: APPROVED"),
                (AuditAction.UPDATE, "SSM Execution: Runbook executed"),
                (AuditAction.UPDATE, "Health Verification SUCCESS: latency p99 normalized to 120ms")
            ]
        },
        {
            "code": "INC-A1B2C3D4E5F3",
            "title": "Auth Service Redis Cache Connection Pool Timeout",
            "description": "Auth token verification failures due to Redis cache socket timeout.",
            "service": "auth-service",
            "instance_id": "i-0a1b2c3d4e5f60003",
            "severity": IncidentSeverity.MEDIUM,
            "status": IncidentStatus.RESOLVED,
            "created_offset": 240,
            "resolved_offset": 225,
            "root_cause": "Stale connection pool in Redis client",
            "recommended_action": "Execute SRE-Copilot-CachePoolFlush",
            "risk_score": 30.0,
            "risk_class": RiskClassification.LOW,
            "runbook": "SRE-Copilot-CachePoolFlush",
            "approval_status": ApprovalStatus.APPROVED,
            "approver": "security-sre@company.com",
            "approval_rationale": "Flush approved, replica healthy.",
            "audit_events": [
                (AuditAction.CREATE, "Alert: auth_token_validation_failure_rate > 2%"),
                (AuditAction.RISK_ASSESS, "Risk Score: 30/100 (LOW)"),
                (AuditAction.APPROVE, "HITL Approval confirmed"),
                (AuditAction.UPDATE, "SSM Automation: SRE-Copilot-CachePoolFlush succeeded"),
                (AuditAction.UPDATE, "Health Verification SUCCESS: Token validations 100% passing")
            ]
        },

        # --- 2 RECOVERY_FAILED (Safety Invariant: EXECUTION_SUCCESS + VERIFICATION_FAILURE -> RECOVERY_FAILED) ---
        {
            "code": "INC-B1C2D3E4F5A1",
            "title": "Order Processing Queue Consumer Worker Hang",
            "description": "Order processing workers stalled. SSM restart executed successfully, but queue consumption rate remained zero due to deadlock.",
            "service": "order-processor",
            "instance_id": "i-0b1c2d3e4f5a60001",
            "severity": IncidentSeverity.CRITICAL,
            "status": IncidentStatus.RECOVERY_FAILED,
            "created_offset": 90,
            "resolved_offset": None,
            "root_cause": "Deadlock in database transaction lock manager",
            "recommended_action": "Execute SRE-Copilot-WorkerRestart",
            "risk_score": 65.0,
            "risk_class": RiskClassification.HIGH,
            "runbook": "SRE-Copilot-WorkerRestart",
            "approval_status": ApprovalStatus.APPROVED,
            "approver": "sre-duty@company.com",
            "approval_rationale": "Worker restart authorized.",
            "audit_events": [
                (AuditAction.CREATE, "Alert: order_queue_backlog_exceeded > 5000 items"),
                (AuditAction.RISK_ASSESS, "Risk Score: 65/100 (HIGH)"),
                (AuditAction.APPROVE, "Human Authorization granted"),
                (AuditAction.UPDATE, "SSM Execution completed: Exit code 0 (SUCCESS)"),
                (AuditAction.UPDATE, "Health Verification FAILED: Queue processing rate still 0 msg/sec - Status: RECOVERY_FAILED (Execution != Recovery)")
            ]
        },
        {
            "code": "INC-B1C2D3E4F5A2",
            "title": "Inventory Sync DB Connection Saturation",
            "description": "Connection pool exhausted. SSM script killed connections, but database remained CPU pegged at 100%.",
            "service": "inventory-db",
            "instance_id": "i-0b1c2d3e4f5a60002",
            "severity": IncidentSeverity.HIGH,
            "status": IncidentStatus.RECOVERY_FAILED,
            "created_offset": 75,
            "resolved_offset": None,
            "root_cause": "Unindexed full table scan locking schema",
            "recommended_action": "Execute SRE-Copilot-KillStaleConnections",
            "risk_score": 55.0,
            "risk_class": RiskClassification.MEDIUM,
            "runbook": "SRE-Copilot-KillStaleConnections",
            "approval_status": ApprovalStatus.APPROVED,
            "approver": "dba-oncall@company.com",
            "approval_rationale": "Connection termination approved.",
            "audit_events": [
                (AuditAction.CREATE, "Alert: postgres_active_connections > 95%"),
                (AuditAction.RISK_ASSESS, "Risk Score: 55/100 (MEDIUM)"),
                (AuditAction.APPROVE, "HITL Authorization: APPROVED"),
                (AuditAction.UPDATE, "SSM Execution: SUCCESS"),
                (AuditAction.UPDATE, "Health Verification FAILED: DB CPU > 99% after 120s - Status: RECOVERY_FAILED")
            ]
        },

        # --- 2 REJECTED (Reject Path: REJECT -> NO EXECUTION -> REMEDIATION_REJECTED) ---
        {
            "code": "INC-C1D2E3F4A5B1",
            "title": "Checkout Service High Memory Warning",
            "description": "Memory utilization at 82%. Automated recommendation to hard reboot EC2 host was rejected by SRE to avoid dropping in-flight transactions.",
            "service": "checkout-service",
            "instance_id": "i-0c1d2e3f4a5b60001",
            "severity": IncidentSeverity.MEDIUM,
            "status": IncidentStatus.REJECTED,
            "created_offset": 60,
            "resolved_offset": None,
            "root_cause": "Anticipated surge traffic during flash sale",
            "recommended_action": "Execute SRE-Copilot-InstanceHardReboot",
            "risk_score": 85.0,
            "risk_class": RiskClassification.CRITICAL,
            "runbook": "SRE-Copilot-InstanceHardReboot",
            "approval_status": ApprovalStatus.REJECTED,
            "approver": "principal-sre@company.com",
            "approval_rationale": "REJECTED: Risk too high during flash sale. Will autoscale horizontally instead. NO SSM EXECUTED.",
            "audit_events": [
                (AuditAction.CREATE, "Alert: checkout_memory_usage > 80%"),
                (AuditAction.RISK_ASSESS, "Risk Assessment: 85/100 (CRITICAL)"),
                (AuditAction.REJECT, "HITL Decision: REJECTED by principal-sre@company.com"),
                (AuditAction.UPDATE, "Safety Boundary: SSM Execution BLOCKED - Status: REMEDIATION_REJECTED")
            ]
        },
        {
            "code": "INC-C1D2E3F4A5B2",
            "title": "Customer Data API Latency Anomaly",
            "description": "Transient latency spike. Proposed cache flush rejected because cache cold-start would worsen database load.",
            "service": "customer-api",
            "instance_id": "i-0c1d2e3f4a5b60002",
            "severity": IncidentSeverity.LOW,
            "status": IncidentStatus.REJECTED,
            "created_offset": 50,
            "resolved_offset": None,
            "root_cause": "Temporary network jitter during ISP failover",
            "recommended_action": "Execute SRE-Copilot-CacheFullFlush",
            "risk_score": 70.0,
            "risk_class": RiskClassification.HIGH,
            "runbook": "SRE-Copilot-CacheFullFlush",
            "approval_status": ApprovalStatus.REJECTED,
            "approver": "sre-duty@company.com",
            "approval_rationale": "REJECTED: Network issue resolved itself, cache flush unnecessary. NO SSM EXECUTED.",
            "audit_events": [
                (AuditAction.CREATE, "Alert: customer_api_latency_anomaly"),
                (AuditAction.RISK_ASSESS, "Risk Score: 70/100 (HIGH)"),
                (AuditAction.REJECT, "HITL Decision: REJECTED"),
                (AuditAction.UPDATE, "SSM Execution bypassed - Status: REMEDIATION_REJECTED")
            ]
        },

        # --- 1 TIMEOUT_EXCEEDED (Timeout Path: TIMEOUT -> NO EXECUTION -> TIMEOUT_EXCEEDED) ---
        {
            "code": "INC-D1E2F3A4B5C1",
            "title": "Search Index Rebalancing Cluster Load",
            "description": "Node rebalance operation required confirmation. No operator response within 60-minute approval window; Step Functions timed out safely without execution.",
            "service": "elasticsearch-cluster",
            "instance_id": "i-0d1e2f3a4b5c60001",
            "severity": IncidentSeverity.LOW,
            "status": IncidentStatus.TIMEOUT_EXCEEDED,
            "created_offset": 100,
            "resolved_offset": None,
            "root_cause": "Cluster index shard redistribution",
            "recommended_action": "Execute SRE-Copilot-ClusterShardRelocate",
            "risk_score": 40.0,
            "risk_class": RiskClassification.MEDIUM,
            "runbook": "SRE-Copilot-ClusterShardRelocate",
            "approval_status": ApprovalStatus.TIMEOUT,
            "approver": None,
            "approval_rationale": "Approval token expired after 3600s. Automated escalation triggered.",
            "audit_events": [
                (AuditAction.CREATE, "Alert: elasticsearch_shard_unassigned_warning"),
                (AuditAction.RISK_ASSESS, "Risk Score: 40/100 (MEDIUM)"),
                (AuditAction.UPDATE, "HITL Approval Token issued - Task Token awaiting response"),
                (AuditAction.UPDATE, "States.Timeout triggered after 3600s - SSM Execution BLOCKED - Status: TIMEOUT_EXCEEDED")
            ]
        },

        # --- 2 APPROVAL_PENDING (Live Actionable in UI: Waiting for Operator Decision) ---
        {
            "code": "INC-E1F2A3B4C5D1",
            "title": "Billing Webhook Queue Dead-Letter Overflow",
            "description": "Dead-letter queue backlog exceeded threshold. SRE Copilot recommends SRE-Copilot-ReplayDeadLetters after verifying webhook destination health.",
            "service": "billing-webhooks",
            "instance_id": "i-0e1f2a3b4c5d60001",
            "severity": IncidentSeverity.HIGH,
            "status": IncidentStatus.RISK_ASSESSED,
            "created_offset": 15,
            "resolved_offset": None,
            "root_cause": "Partner billing endpoint transient 503 response",
            "recommended_action": "Execute SRE-Copilot-ReplayDeadLetters with rate limit 50/sec",
            "risk_score": 42.0,
            "risk_class": RiskClassification.MEDIUM,
            "runbook": "SRE-Copilot-ReplayDeadLetters",
            "approval_status": ApprovalStatus.PENDING,
            "approver": None,
            "approval_rationale": None,
            "audit_events": [
                (AuditAction.CREATE, "Alert: sqs_dlq_billing_messages > 200"),
                (AuditAction.RISK_ASSESS, "Risk Assessment completed: 42/100 (MEDIUM)"),
                (AuditAction.UPDATE, "HITL Approval Requested - Awaiting human authorization in SRE Copilot UI")
            ]
        },
        {
            "code": "INC-E1F2A3B4C5D2",
            "title": "User Notification Gateway Rate-Limit Throttling",
            "description": "Downstream SMS/Email provider 429 throttling. SRE Copilot recommends dynamic backoff configuration adjustment.",
            "service": "notification-gateway",
            "instance_id": "i-0e1f2a3b4c5d60002",
            "severity": IncidentSeverity.MEDIUM,
            "status": IncidentStatus.RISK_ASSESSED,
            "created_offset": 8,
            "resolved_offset": None,
            "root_cause": "Provider rate limit burst exhaustion",
            "recommended_action": "Execute SRE-Copilot-ApplyThrottlingPolicy",
            "risk_score": 28.0,
            "risk_class": RiskClassification.LOW,
            "runbook": "SRE-Copilot-ApplyThrottlingPolicy",
            "approval_status": ApprovalStatus.PENDING,
            "approver": None,
            "approval_rationale": None,
            "audit_events": [
                (AuditAction.CREATE, "Alert: notification_gateway_drop_rate > 3%"),
                (AuditAction.RISK_ASSESS, "Risk Assessment: 28/100 (LOW)"),
                (AuditAction.UPDATE, "HITL Approval Requested - Operator decision pending")
            ]
        }
    ]

    for item in incident_definitions:
        created_time = now - timedelta(minutes=item["created_offset"])
        resolved_time = (now - timedelta(minutes=item["resolved_offset"])) if item["resolved_offset"] else None

        inc = Incident(
            incident_id=item["code"],
            title=item["title"],
            description=item["description"],
            severity=item["severity"],
            status=item["status"],
            service=item["service"],
            instance_id=item["instance_id"],
            created_at=created_time,
            updated_at=resolved_time or created_time,
            resolved_at=resolved_time
        )
        db.add(inc)
        await db.flush()
        await db.refresh(inc)

        # Add Evidence
        evidence = Evidence(
            evidence_id=f"EVD-{uuid.uuid4().hex[:10].upper()}",
            incident_id=inc.id,
            filename=f"{item['service']}_error.log",
            filepath=f"/storage/evidence/{item['service']}_{inc.id}.log",
            evidence_type=EvidenceType.LOG,
            file_size=4096,
            mime_type="text/plain",
            description=f"Automated log extraction for {item['title']}",
            uploaded_by="EvidenceCollectorAgent",
            uploaded_at=created_time + timedelta(seconds=15)
        )
        db.add(evidence)

        # Add Risk Assessment
        risk = RiskAssessment(
            assessment_id=f"RSK-{uuid.uuid4().hex[:10].upper()}",
            incident_id=inc.id,
            risk_score=item["risk_score"],
            risk_classification=item["risk_class"],
            factors=item["runbook"],
            recommended_action=item["recommended_action"],
            assessed_at=created_time + timedelta(seconds=30)
        )
        db.add(risk)

        # Add Approval
        approval = Approval(
            approval_id=f"APP-{uuid.uuid4().hex[:10].upper()}",
            incident_id=inc.id,
            requested_by="RiskEngineAgent",
            approved_by=item["approver"],
            status=item["approval_status"],
            rationale=item["approval_rationale"],
            created_at=created_time + timedelta(seconds=45),
            decided_at=(created_time + timedelta(minutes=5)) if item["approver"] else None
        )
        db.add(approval)

        # Add Audit Events
        for action, details in item["audit_events"]:
            audit_log = AuditLog(
                log_id=f"AUD-{uuid.uuid4().hex[:10].upper()}",
                incident_id=inc.id,
                user=item["approver"] if action == AuditAction.APPROVE else "SRECopilotEngine",
                action=action,
                target=f"Incident {item['code']}",
                details=details,
                ip_address="10.0.4.15",
                timestamp=created_time + timedelta(minutes=2)
            )
            db.add(audit_log)

    await db.commit()
    return {"status": "success", "seeded_incidents": len(incident_definitions)}
