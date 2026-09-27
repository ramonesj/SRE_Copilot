import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  TextField,
  MenuItem,
  Divider,
  LinearProgress,
  Tabs,
  Tab,
} from '@mui/material'
import {
  Bolt as BoltIcon,
  PlayArrow as PlayArrowIcon,
  Psychology as PsychologyIcon,
  Shield as ShieldIcon,
  Gavel as GavelIcon,
  Speed as SpeedIcon,
  Tune as TuneIcon,
  DashboardCustomize as PresetsIcon,
} from '@mui/icons-material'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { incidentService } from '../../services/incidentService'

interface SimulateIncidentModalProps {
  open: boolean
  onClose: () => void
}

interface IncidentPreset {
  id: string
  title: string
  service: string
  nodeId: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  errorLog: string
  rootCause: string
  runbook: string
  riskScore: number
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  requiresHitl: boolean
}

const PRESETS: IncidentPreset[] = [
  {
    id: 'dlq-surge',
    title: 'SQS Dead-Letter Backlog Surge',
    service: 'notification-gateway',
    nodeId: 'i-0ef1f2a3b4c5d60002',
    severity: 'MEDIUM',
    errorLog: 'CRITICAL: DLQ depth exceeded threshold (4,250 unconsumed messages). Rate-limited by downstream push providers.',
    rootCause: 'Downstream webhook destination throttled delivery rate, causing exponential retry queue accumulation.',
    runbook: 'SRE-Copilot-ReplayDeadLetters',
    riskScore: 42,
    riskLevel: 'MEDIUM',
    requiresHitl: true,
  },
  {
    id: 'memory-leak',
    title: 'High Memory Saturation & Pod OOM',
    service: 'checkout-service',
    nodeId: 'i-0c1d2e3f4a5b60001',
    severity: 'HIGH',
    errorLog: 'WARN: Resident memory exceeded 92% ceiling. Garbage collector thrashing observed on checkout-worker-01.',
    rootCause: 'Unbounded memory cache leak during high-volume cart checkout sessions.',
    runbook: 'SRE-Copilot-ScaleASG',
    riskScore: 68,
    riskLevel: 'HIGH',
    requiresHitl: true,
  },
  {
    id: 'db-pool-exhausted',
    title: 'PostgreSQL Connection Pool Starvation',
    service: 'order-processor',
    nodeId: 'i-0b1c2d3e4f5a60001',
    severity: 'CRITICAL',
    errorLog: 'FATAL: remaining connection slots are reserved for non-replication superuser connections (max_connections=200).',
    rootCause: 'Zombie connection leak from unclosed transaction handles in order ingestion worker threads.',
    runbook: 'SRE-Copilot-FlushDatabasePool',
    riskScore: 88,
    riskLevel: 'CRITICAL',
    requiresHitl: true,
  },
  {
    id: 'nginx-worker-lock',
    title: 'Nginx Worker Threads Lockup',
    service: 'billing-webhooks',
    nodeId: 'i-0ef1f2a3b4c5d60001',
    severity: 'LOW',
    errorLog: 'WARN: worker process 10294 exited on signal 11 (core dumped) - respawning worker process.',
    rootCause: 'Temporary socket buffer overflow in SSL termination module.',
    runbook: 'SRE-Copilot-RestartService',
    riskScore: 18,
    riskLevel: 'LOW',
    requiresHitl: false,
  },
]

export default function SimulateIncidentModal({ open, onClose }: SimulateIncidentModalProps) {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState(0)
  const [selectedPreset, setSelectedPreset] = useState<IncidentPreset>(PRESETS[0])
  const [isSimulating, setIsSimulating] = useState(false)
  const [simulationStage, setSimulationStage] = useState('')

  // Custom live incident form
  const [customTitle, setCustomTitle] = useState('')
  const [customService, setCustomService] = useState('payment-gateway')
  const [customNode, setCustomNode] = useState('i-0ef1f2a3b4c5d60002')
  const [customSeverity, setCustomSeverity] = useState<'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'>('HIGH')
  const [customLog, setCustomLog] = useState('')

  const handleSimulate = async () => {
    setIsSimulating(true)
    setSimulationStage('1. Ingesting Live Alert & Error Telemetry into Backend...')
    await new Promise((r) => setTimeout(r, 600))

    setSimulationStage('2. Invoking AWS Bedrock Claude 3.5 Sonnet for Triage...')
    await new Promise((r) => setTimeout(r, 700))

    setSimulationStage('3. Calculating Policy Risk Score & Checking HITL Boundary...')
    await new Promise((r) => setTimeout(r, 600))

    const isCustom = activeTab === 1
    const title = isCustom ? customTitle || `${customService} Service Outage` : selectedPreset.title
    const service = isCustom ? customService : selectedPreset.service
    const instance_id = isCustom ? customNode : selectedPreset.nodeId
    const severity = isCustom ? customSeverity : selectedPreset.severity
    const description = isCustom ? customLog || `Automated failure alert on ${service}` : selectedPreset.errorLog

    try {
      // Create real live incident in backend DB
      const result = await incidentService.createIncident({
        title,
        service,
        instance_id,
        severity: severity.toLowerCase() as any,
        description,
      } as any)

      if (severity !== 'LOW') {
        setSimulationStage('4. Enqueuing HITL Approval Request in Database...')
      } else {
        setSimulationStage('4. Autonomous Execution & Verification...')
      }
      await new Promise((r) => setTimeout(r, 500))

      // Refresh all queries so live data updates instantly
      await queryClient.invalidateQueries({ queryKey: ['incidents'] })
      await queryClient.invalidateQueries({ queryKey: ['incident-metrics'] })
      await queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      await queryClient.invalidateQueries({ queryKey: ['audit-logs'] })

      if (severity !== 'LOW') {
        toast.success(`⚡ Live Incident ${(result as any)?.incident_id || ''} created! Enqueued for HITL Approval.`, {
          duration: 5000,
        })
      } else {
        toast.success(`⚡ Live Incident ${(result as any)?.incident_id || ''} created and auto-remediated!`, {
          duration: 5000,
        })
      }

      setIsSimulating(false)
      onClose()
    } catch (err: any) {
      toast.error(`Simulation Error: ${err.message}`)
      setIsSimulating(false)
    }
  }

  return (
    <Dialog
      open={open}
      onClose={() => !isSimulating && onClose()}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          backgroundColor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      <DialogTitle sx={{ pb: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box
          sx={{
            width: 38,
            height: 38,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px rgba(245, 158, 11, 0.4)',
          }}
        >
          <BoltIcon sx={{ color: '#fff', fontSize: 24 }} />
        </Box>
        <Box>
          <Typography variant="h5" fontWeight="800">
            Live Incident Injector & Real Pipeline Simulation
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Creates a real database incident, calculates risk, enqueues HITL approval, and records audit trails.
          </Typography>
        </Box>
      </DialogTitle>

      <Box sx={{ px: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
          <Tab icon={<PresetsIcon sx={{ mr: 1, fontSize: 18 }} />} iconPosition="start" label="Preset Scenarios" sx={{ textTransform: 'none', fontWeight: 600 }} />
          <Tab icon={<TuneIcon sx={{ mr: 1, fontSize: 18 }} />} iconPosition="start" label="Custom Incident Builder" sx={{ textTransform: 'none', fontWeight: 600 }} />
        </Tabs>
      </Box>

      <DialogContent sx={{ py: 3 }}>
        {isSimulating && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" fontWeight="700" color="primary.main" sx={{ mb: 1 }}>
              {simulationStage}
            </Typography>
            <LinearProgress color="warning" sx={{ height: 6, borderRadius: 3 }} />
          </Box>
        )}

        {/* TAB 0: PRESETS */}
        {activeTab === 0 && (
          <>
            <Typography variant="subtitle2" fontWeight="700" gutterBottom>
              Choose Failure Scenario:
            </Typography>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              {PRESETS.map((preset) => {
                const isSelected = selectedPreset.id === preset.id
                return (
                  <Grid item xs={12} sm={6} key={preset.id}>
                    <Card
                      onClick={() => setSelectedPreset(preset)}
                      sx={{
                        cursor: 'pointer',
                        borderRadius: 2,
                        border: '2px solid',
                        borderColor: isSelected ? 'primary.main' : 'divider',
                        backgroundColor: isSelected ? 'rgba(6,182,212,0.06)' : 'background.paper',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          borderColor: 'primary.main',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    >
                      <CardContent sx={{ p: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Typography variant="subtitle2" fontWeight="800">
                            {preset.title}
                          </Typography>
                          <Chip
                            label={preset.severity}
                            size="small"
                            color={
                              preset.severity === 'CRITICAL'
                                ? 'error'
                                : preset.severity === 'HIGH'
                                ? 'warning'
                                : preset.severity === 'MEDIUM'
                                ? 'info'
                                : 'success'
                            }
                            sx={{ height: 20, fontSize: '0.65rem', fontWeight: 800 }}
                          />
                        </Box>

                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                          Service: <strong>{preset.service}</strong> ({preset.nodeId})
                        </Typography>

                        <Typography
                          variant="caption"
                          className="font-mono"
                          sx={{
                            display: 'block',
                            color: 'text.secondary',
                            backgroundColor: 'rgba(255,255,255,0.03)',
                            p: 1,
                            borderRadius: 1,
                            fontSize: '0.72rem',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {preset.errorLog}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )
              })}
            </Grid>

            {/* Invariant Details Preview */}
            <Box sx={{ p: 2, borderRadius: 2, backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" fontWeight="700" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <PsychologyIcon color="primary" fontSize="small" /> Pipeline Lifecycle Action:
              </Typography>

              <Grid container spacing={2} sx={{ fontSize: '0.82rem' }}>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    Target Runbook:
                  </Typography>
                  <Typography variant="body2" className="font-mono" fontWeight="700" color="primary.main">
                    {selectedPreset.runbook}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    Risk Calculation:
                  </Typography>
                  <Typography variant="body2" fontWeight="800" color={selectedPreset.riskScore > 50 ? 'warning.main' : 'success.main'}>
                    {selectedPreset.riskScore}/100 ({selectedPreset.riskLevel})
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    Safety Evaluation:
                  </Typography>
                  <Typography variant="body2" fontWeight="700" color={selectedPreset.requiresHitl ? 'warning.main' : 'success.main'}>
                    {selectedPreset.requiresHitl ? 'Enqueues for Operator Authorization' : 'Autonomous Resolution'}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </>
        )}

        {/* TAB 1: CUSTOM INCIDENT BUILDER */}
        {activeTab === 1 && (
          <Grid container spacing={2.5}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Incident Title"
                placeholder="e.g., Payment Gateway SSL Handshake Latency Spike"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Impacted Service"
                placeholder="e.g., payment-gateway, auth-service"
                value={customService}
                onChange={(e) => setCustomService(e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Target Instance ID / Host"
                value={customNode}
                onChange={(e) => setCustomNode(e.target.value)}
                InputProps={{ className: 'font-mono' }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Severity Level"
                value={customSeverity}
                onChange={(e) => setCustomSeverity(e.target.value as any)}
              >
                <MenuItem value="LOW">LOW (Risk &lt; 25, Autonomous Execution)</MenuItem>
                <MenuItem value="MEDIUM">MEDIUM (Risk ~42, HITL Approval Required)</MenuItem>
                <MenuItem value="HIGH">HIGH (Risk ~68, HITL Approval Required)</MenuItem>
                <MenuItem value="CRITICAL">CRITICAL (Risk ~88, Immediate Escalation)</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Error Log / Telemetry Stack Trace"
                placeholder="e.g., HTTP 504 Gateway Timeout: upstream connection timed out (110: Connection timed out) while reading response header from upstream"
                value={customLog}
                onChange={(e) => setCustomLog(e.target.value)}
                InputProps={{ className: 'font-mono' }}
              />
            </Grid>
          </Grid>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button disabled={isSimulating} onClick={onClose} color="inherit">
          Cancel
        </Button>
        <Button
          variant="contained"
          disabled={isSimulating}
          onClick={handleSimulate}
          startIcon={<PlayArrowIcon />}
          sx={{
            background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
            fontWeight: 700,
            px: 3,
            boxShadow: '0 4px 14px rgba(245, 158, 11, 0.4)',
          }}
        >
          {isSimulating ? 'Injecting Real Incident...' : 'Inject Real Incident into System'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
