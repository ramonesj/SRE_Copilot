import { api } from './api'
import type { Approval, ApprovalRequest, ApiResponse, PaginatedResponse } from '../types'

export const approvalService = {
  // Get pending approval requests
  async getPendingApprovals(page = 1, pageSize = 10): Promise<PaginatedResponse<ApprovalRequest>> {
    const response = await api.get<PaginatedResponse<ApprovalRequest>>(
      `/api/approvals/pending?page=${page}&page_size=${pageSize}`
    )
    return response.data
  },

  // Get approval request by ID
  async getApprovalRequest(id: string): Promise<ApprovalRequest> {
    const response = await api.get<ApiResponse<ApprovalRequest>>(`/api/approvals/${id}`)
    return response.data.data!
  },

  // Submit approval decision
  async submitDecision(
    approvalId: string,
    decision: 'APPROVE' | 'REJECT',
    rationale: string
  ): Promise<Approval> {
    const response = await api.post<ApiResponse<Approval>>(
      `/api/approvals/${approvalId}/respond`,
      {
        decision,
        rationale,
      }
    )
    return response.data.data!
  },

  // Get approval history
  async getApprovalHistory(incidentId?: string): Promise<Approval[]> {
    const params = incidentId ? `?incident_id=${incidentId}` : ''
    const response = await api.get<ApiResponse<Approval[]>>(`/api/approvals/history${params}`)
    return response.data.data!
  },
}
