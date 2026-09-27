import { api } from './api'
import type { AuditLog, ApiResponse, PaginatedResponse } from '../types'

export interface AuditFilters {
  incident_id?: string
  action?: string
  actor?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}

export const auditService = {
  // Get audit logs with filters
  async getAuditLogs(filters?: AuditFilters): Promise<PaginatedResponse<AuditLog>> {
    const params = new URLSearchParams()
    if (filters?.incident_id) params.append('incident_id', filters.incident_id)
    if (filters?.action) params.append('action', filters.action)
    if (filters?.actor) params.append('actor', filters.actor)
    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.page_size) params.append('page_size', filters.page_size.toString())

    const response = await api.get<PaginatedResponse<AuditLog>>(`/api/audit?${params.toString()}`)
    return response.data
  },

  // Get audit log by ID
  async getAuditLog(id: string): Promise<AuditLog> {
    const response = await api.get<ApiResponse<AuditLog>>(`/api/audit/${id}`)
    return response.data.data!
  },

  // Get audit logs for specific incident
  async getIncidentAuditLogs(incidentId: string): Promise<AuditLog[]> {
    const response = await api.get<ApiResponse<AuditLog[]>>(
      `/api/incidents/${incidentId}/audit`
    )
    return response.data.data!
  },

  // Export audit logs
  async exportAuditLogs(filters?: AuditFilters): Promise<Blob> {
    const params = new URLSearchParams()
    if (filters?.incident_id) params.append('incident_id', filters.incident_id)
    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)

    const response = await api.get(`/api/audit/export?${params.toString()}`, {
      responseType: 'blob',
    })
    return response.data
  },
}
