import { api } from './api'
import type { Incident, ApiResponse, PaginatedResponse } from '../types'

export interface IncidentFilters {
  status?: string
  severity?: string
  service_name?: string
  page?: number
  page_size?: number
}

export const incidentService = {
  // Get all incidents with filters
  async getIncidents(filters?: IncidentFilters): Promise<PaginatedResponse<Incident>> {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.severity) params.append('severity', filters.severity)
    if (filters?.service_name) params.append('service_name', filters.service_name)
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.page_size) params.append('page_size', filters.page_size.toString())

    const response = await api.get<PaginatedResponse<Incident>>(`/api/incidents?${params.toString()}`)
    return response.data
  },

  // Get single incident by ID
  async getIncident(id: string): Promise<Incident> {
    const response = await api.get<ApiResponse<Incident>>(`/api/incidents/${id}`)
    return response.data.data!
  },

  // Create new incident
  async createIncident(data: Partial<Incident>): Promise<Incident> {
    const response = await api.post<ApiResponse<Incident>>('/api/incidents', data)
    return response.data.data!
  },

  // Update incident
  async updateIncident(id: string, data: Partial<Incident>): Promise<Incident> {
    const response = await api.put<ApiResponse<Incident>>(`/api/incidents/${id}`, data)
    return response.data.data!
  },

  // Delete incident
  async deleteIncident(id: string): Promise<void> {
    await api.delete(`/api/incidents/${id}`)
  },

  // Get incident metrics
  async getMetrics(): Promise<{
    total: number
    active: number
    resolved: number
    pending_approvals?: number
    by_severity: Record<string, number>
    by_status: Record<string, number>
  }> {
    const response = await api.get<ApiResponse<{
      total: number
      active: number
      resolved: number
      by_severity: Record<string, number>
      by_status: Record<string, number>
    }>>('/api/incidents/metrics')
    return (response.data?.data || response.data) as any
  },
}
