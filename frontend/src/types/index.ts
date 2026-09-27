// Incident types
export type IncidentStatus = 
  | 'CREATED'
  | 'EVIDENCE_COLLECTED'
  | 'DIAGNOSIS_COMPLETE'
  | 'RISK_ASSESSED'
  | 'APPROVED'
  | 'EXECUTING'
  | 'RECOVERY_VERIFIED'
  | 'RECOVERY_FAILED'
  | 'VERIFICATION_ERROR'
  | 'REMEDIATION_REJECTED'
  | 'TIMEOUT_EXCEEDED'
  | 'DIAGNOSIS_FAILED'
  | 'DIAGNOSIS_TIMEOUT'
  | 'RESOLVED'

export type IncidentSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface Incident {
  id: string
  node_id: string
  service_name: string
  error_log: string
  severity: IncidentSeverity
  status: IncidentStatus
  created_at: string
  updated_at: string
  evidence_collected?: boolean
  diagnosis_complete?: boolean
  risk_assessed?: boolean
  diagnosis?: Diagnosis
  risk_assessment?: RiskAssessment
  approval?: Approval
}

export interface Diagnosis {
  root_cause: string
  confidence: number
  recommended_action: string
  evidence: Evidence[]
}

export interface Evidence {
  id: string
  incident_id: string
  type: 'LOG' | 'METRIC' | 'TRACE'
  content: string
  timestamp: string
}

export interface RiskAssessment {
  id: string
  incident_id: string
  risk_score: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  ssm_runbook: string
  impact_analysis: string
  created_at: string
}

// Approval types
export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'TIMEOUT'

export interface Approval {
  id: string
  incident_id: string
  status: ApprovalStatus
  approver?: string
  decision?: 'APPROVE' | 'REJECT'
  rationale?: string
  created_at: string
  responded_at?: string
  timeout_seconds: number
  approval_request_id?: string
}

export interface ApprovalRequest {
  id: string
  incident_id: string
  diagnosis: Diagnosis
  risk_assessment: RiskAssessment
  created_at: string
  expires_at: string
  status: ApprovalStatus
}

// Audit types
export type AuditAction = 
  | 'INCIDENT_CREATED'
  | 'EVIDENCE_COLLECTED'
  | 'DIAGNOSIS_COMPLETE'
  | 'RISK_ASSESSED'
  | 'APPROVAL_REQUESTED'
  | 'APPROVAL_GRANTED'
  | 'APPROVAL_REJECTED'
  | 'APPROVAL_TIMEOUT'
  | 'REMEDIATION_EXECUTED'
  | 'REMEDIATION_SUCCESS'
  | 'REMEDIATION_FAILED'
  | 'INCIDENT_RESOLVED'

export interface AuditLog {
  id: string
  incident_id?: string
  action: AuditAction
  actor: string
  details: Record<string, any>
  timestamp: string
}

// Metrics types
export interface DashboardMetrics {
  total_incidents: number
  active_incidents: number
  resolved_incidents: number
  pending_approvals: number
  avg_resolution_time: number
  incidents_by_severity: Record<IncidentSeverity, number>
  incidents_by_status: Record<IncidentStatus, number>
}

// API Response types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
