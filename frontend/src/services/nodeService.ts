import { ServerNode, ConnectionTestResult } from '../types/server'

const STORAGE_KEY = 'sre_copilot_registered_nodes'

const INITIAL_NODES: ServerNode[] = [
  {
    id: 'node-1',
    name: 'Notification Gateway Primary',
    instance_id: 'i-0ef1f2a3b4c5d60002',
    hostname: 'notify-gw-01.us-east-1.internal',
    provider: 'AWS_EC2',
    region: 'us-east-1',
    environment: 'PRODUCTION',
    service_tag: 'notification-gateway',
    status: 'ONLINE',
    ssm_agent_status: 'ACTIVE',
    ssm_agent_version: '3.2.1643.0',
    iam_role_arn: 'arn:aws:iam::123456789012:role/SRECopilot-SSMManagedInstanceCore',
    telemetry_port: 9100,
    cpu_usage: 42,
    memory_usage: 68,
    latency_ms: 12,
    last_heartbeat: new Date(Date.now() - 1000 * 30).toISOString(),
    auto_remediation_enabled: true,
  },
  {
    id: 'node-2',
    name: 'Billing Webhooks Worker',
    instance_id: 'i-0ef1f2a3b4c5d60001',
    hostname: 'billing-wh-01.us-east-1.internal',
    provider: 'AWS_EC2',
    region: 'us-east-1',
    environment: 'PRODUCTION',
    service_tag: 'billing-webhooks',
    status: 'ONLINE',
    ssm_agent_status: 'ACTIVE',
    ssm_agent_version: '3.2.1643.0',
    iam_role_arn: 'arn:aws:iam::123456789012:role/SRECopilot-SSMManagedInstanceCore',
    telemetry_port: 9100,
    cpu_usage: 84,
    memory_usage: 77,
    latency_ms: 18,
    last_heartbeat: new Date(Date.now() - 1000 * 15).toISOString(),
    auto_remediation_enabled: true,
  },
  {
    id: 'node-3',
    name: 'Customer API Service Node',
    instance_id: 'i-0c1d2e3f4a5b60002',
    hostname: 'customer-api-02.us-east-1.internal',
    provider: 'AWS_EC2',
    region: 'us-east-1',
    environment: 'PRODUCTION',
    service_tag: 'customer-api',
    status: 'ONLINE',
    ssm_agent_status: 'ACTIVE',
    ssm_agent_version: '3.2.1520.0',
    iam_role_arn: 'arn:aws:iam::123456789012:role/SRECopilot-SSMManagedInstanceCore',
    telemetry_port: 9100,
    cpu_usage: 28,
    memory_usage: 45,
    latency_ms: 9,
    last_heartbeat: new Date(Date.now() - 1000 * 45).toISOString(),
    auto_remediation_enabled: false,
  },
  {
    id: 'node-4',
    name: 'Checkout Service Engine',
    instance_id: 'i-0c1d2e3f4a5b60001',
    hostname: 'checkout-srv-01.us-east-1.internal',
    provider: 'AWS_EC2',
    region: 'us-east-1',
    environment: 'PRODUCTION',
    service_tag: 'checkout-service',
    status: 'ONLINE',
    ssm_agent_status: 'ACTIVE',
    ssm_agent_version: '3.2.1643.0',
    iam_role_arn: 'arn:aws:iam::123456789012:role/SRECopilot-SSMManagedInstanceCore',
    telemetry_port: 9100,
    cpu_usage: 56,
    memory_usage: 62,
    latency_ms: 14,
    last_heartbeat: new Date(Date.now() - 1000 * 20).toISOString(),
    auto_remediation_enabled: true,
  },
  {
    id: 'node-5',
    name: 'Order Processor Worker',
    instance_id: 'i-0b1c2d3e4f5a60001',
    hostname: 'order-proc-01.us-east-1.internal',
    provider: 'AWS_EC2',
    region: 'us-east-1',
    environment: 'PRODUCTION',
    service_tag: 'order-processor',
    status: 'ONLINE',
    ssm_agent_status: 'ACTIVE',
    ssm_agent_version: '3.2.1643.0',
    iam_role_arn: 'arn:aws:iam::123456789012:role/SRECopilot-SSMManagedInstanceCore',
    telemetry_port: 9100,
    cpu_usage: 73,
    memory_usage: 81,
    latency_ms: 16,
    last_heartbeat: new Date(Date.now() - 1000 * 10).toISOString(),
    auto_remediation_enabled: true,
  },
  {
    id: 'node-6',
    name: 'Elasticsearch Search Cluster Leader',
    instance_id: 'i-0d1e2f3a4b5c60001',
    hostname: 'es-cluster-01.us-east-1.internal',
    provider: 'AWS_EC2',
    region: 'us-east-1',
    environment: 'PRODUCTION',
    service_tag: 'elasticsearch-cluster',
    status: 'ONLINE',
    ssm_agent_status: 'ACTIVE',
    ssm_agent_version: '3.2.1643.0',
    iam_role_arn: 'arn:aws:iam::123456789012:role/SRECopilot-SSMManagedInstanceCore',
    telemetry_port: 9200,
    cpu_usage: 34,
    memory_usage: 89,
    latency_ms: 22,
    last_heartbeat: new Date(Date.now() - 1000 * 60).toISOString(),
    auto_remediation_enabled: false,
  }
]

export const nodeService = {
  getNodes: async (): Promise<ServerNode[]> => {
    const data = localStorage.getItem(STORAGE_KEY)
    if (!data) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_NODES))
      return INITIAL_NODES
    }
    try {
      return JSON.parse(data)
    } catch {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_NODES))
      return INITIAL_NODES
    }
  },

  addNode: async (nodeData: Omit<ServerNode, 'id' | 'last_heartbeat' | 'status' | 'ssm_agent_status' | 'ssm_agent_version' | 'cpu_usage' | 'memory_usage' | 'latency_ms'>): Promise<ServerNode> => {
    const nodes = await nodeService.getNodes()
    const newNode: ServerNode = {
      ...nodeData,
      id: `node-${Date.now()}`,
      status: 'ONLINE',
      ssm_agent_status: 'ACTIVE',
      ssm_agent_version: '3.2.1643.0',
      cpu_usage: Math.floor(Math.random() * 40) + 15,
      memory_usage: Math.floor(Math.random() * 45) + 30,
      latency_ms: Math.floor(Math.random() * 20) + 8,
      last_heartbeat: new Date().toISOString(),
    }
    const updated = [newNode, ...nodes]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
    return newNode
  },

  updateNode: async (id: string, updates: Partial<ServerNode>): Promise<ServerNode> => {
    const nodes = await nodeService.getNodes()
    const index = nodes.findIndex((n) => n.id === id)
    if (index === -1) throw new Error('Node not found')
    nodes[index] = { ...nodes[index], ...updates, last_heartbeat: new Date().toISOString() }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nodes))
    return nodes[index]
  },

  deleteNode: async (id: string): Promise<void> => {
    const nodes = await nodeService.getNodes()
    const filtered = nodes.filter((n) => n.id !== id)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
  },

  testConnection: async (
    target: { instance_id: string; region: string; provider: string },
    onProgress?: (step: ConnectionTestResult) => void
  ): Promise<boolean> => {
    const steps: ConnectionTestResult[] = [
      {
        step: '1. DNS & Network Resolution',
        status: 'RUNNING',
        message: `Resolving endpoint for ${target.instance_id} in ${target.region}...`,
      },
      {
        step: '2. AWS SSM Agent Handshake',
        status: 'PENDING',
        message: 'Establishing secure websocket session via Systems Manager...',
      },
      {
        step: '3. IAM Policy & Role Verification',
        status: 'PENDING',
        message: 'Validating ssm:SendCommand and ssm:GetCommandInvocation policies...',
      },
      {
        step: '4. Telemetry Scraping & Health Probe',
        status: 'PENDING',
        message: 'Scraping Prometheus node_exporter / CloudWatch agent metrics...',
      },
      {
        step: '5. SRE Copilot Fleet Registration',
        status: 'PENDING',
        message: 'Enrolling instance in auto-remediation pool...',
      },
    ]

    for (let i = 0; i < steps.length; i++) {
      steps[i].status = 'RUNNING'
      onProgress?.(steps[i])
      await new Promise((r) => setTimeout(r, 600))
      steps[i].status = 'SUCCESS'
      if (i === 0) steps[i].message = `Resolved network route in ${target.region} (RTT: 14ms)`
      if (i === 1) steps[i].message = `SSM Agent v3.2.1643 online & responding to ping`
      if (i === 2) steps[i].message = `IAM permissions validated (ssm:SendCommand OK)`
      if (i === 3) steps[i].message = `Telemetry stream active (CPU: 32%, Load: 0.45)`
      if (i === 4) steps[i].message = `Enrolled node into SRE Copilot active management pool`
      onProgress?.(steps[i])
    }

    return true
  },
}
