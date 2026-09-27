export type ServerProvider = 'AWS_EC2' | 'ON_PREMISE' | 'KUBERNETES' | 'BARE_METAL'
export type ServerEnvironment = 'PRODUCTION' | 'STAGING' | 'DEVELOPMENT' | 'DR'
export type ServerStatus = 'ONLINE' | 'DEGRADED' | 'OFFLINE' | 'CONNECTING'
export type SsmAgentStatus = 'ACTIVE' | 'INACTIVE' | 'NOT_INSTALLED'

export interface ServerNode {
  id: string
  name: string
  instance_id: string
  hostname: string
  provider: ServerProvider
  region: string
  environment: ServerEnvironment
  service_tag: string
  status: ServerStatus
  ssm_agent_status: SsmAgentStatus
  ssm_agent_version: string
  iam_role_arn: string
  telemetry_port: number
  cpu_usage: number
  memory_usage: number
  latency_ms: number
  last_heartbeat: string
  auto_remediation_enabled: boolean
}

export interface ConnectionTestResult {
  step: string
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'ERROR'
  message: string
  duration_ms?: number
}
