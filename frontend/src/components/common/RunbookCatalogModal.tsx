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
  Divider,
  Paper,
  LinearProgress,
} from '@mui/material'
import {
  MenuBook as BookIcon,
  PlayArrow as PlayIcon,
  CheckCircle as CheckCircleIcon,
  Security as SecurityIcon,
  Terminal as TerminalIcon,
  Code as CodeIcon,
} from '@mui/icons-material'
import toast from 'react-hot-toast'

interface RunbookCatalogModalProps {
  open: boolean
  onClose: () => void
}

interface RunbookItem {
  name: string
  version: string
  description: string
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH'
  riskScore: number
  targetService: string
  preconditions: string[]
  rollbackPlan: string
  parameters: Record<string, string>
}

const RUNBOOKS: RunbookItem[] = [
  {
    name: 'SRE-Copilot-RestartService',
    version: '1.4.0',
    description: 'Gracefully drains active connection sockets and issues a systemd service restart with readiness probe check.',
    riskLevel: 'LOW',
    riskScore: 18,
    targetService: 'Systemd Services / Nginx / Node processes',
    preconditions: ['No active database schema migration locks', 'Backup replica healthy'],
    rollbackPlan: 'Reverts to previous systemd unit snapshot if readiness probe fails within 30s.',
    parameters: {
      ServiceName: 'billing-webhooks.service',
      DrainTimeoutSeconds: '15',
      VerifyEndpoint: 'http://localhost:8080/health',
    },
  },
  {
    name: 'SRE-Copilot-ScaleASG',
    version: '2.1.0',
    description: 'Increments Auto Scaling Group desired capacity by +2 replicas and distributes traffic across availability zones.',
    riskLevel: 'MEDIUM',
    riskScore: 35,
    targetService: 'EC2 Auto Scaling Groups / EKS NodeGroups',
    preconditions: ['AWS account EC2 vCPU limit not exceeded', 'Subnet IP pool > 10 IPs available'],
    rollbackPlan: 'Terminates newly launched instances if CPU saturation does not decline by 20% within 5m.',
    parameters: {
      AutoScalingGroupName: 'asg-checkout-service-prod',
      DesiredAdjustment: '+2',
      CooldownPeriod: '180',
    },
  },
  {
    name: 'SRE-Copilot-ReplayDeadLetters',
    version: '1.2.0',
    description: 'Redrives buffered messages from SQS Dead-Letter Queue back into the primary processing queue with token bucket rate-limiting.',
    riskLevel: 'MEDIUM',
    riskScore: 42,
    targetService: 'AWS SQS / EventBridge / Webhook Workers',
    preconditions: ['Downstream destination endpoint returning HTTP 200 OK', 'Worker error rate < 1%'],
    rollbackPlan: 'Pauses redrive immediately if DLQ consumer error rate exceeds 5%.',
    parameters: {
      SourceQueueArn: 'arn:aws:sqs:us-east-1:123456789012:notification-dlq',
      TargetQueueArn: 'arn:aws:sqs:us-east-1:123456789012:notification-primary',
      MaxMessageBatch: '50',
      RateLimitPerSec: '20',
    },
  },
  {
    name: 'SRE-Copilot-ClearDiskSpace',
    version: '1.0.2',
    description: 'Safely truncates rotated log archives (.log.gz older than 7 days) and empties /tmp directory to recover disk inode space.',
    riskLevel: 'LOW',
    riskScore: 12,
    targetService: 'Linux Host Filesystems / Elasticsearch Data Nodes',
    preconditions: ['Mounted filesystem utilization > 85%', 'Active application logs not locked'],
    rollbackPlan: 'Preserves compressed snapshots in S3 glacier bucket before local deletion.',
    parameters: {
      DirectoryPath: '/var/log/application',
      RetentionDays: '7',
      MinFreeSpaceGigaBytes: '20',
    },
  },
  {
    name: 'SRE-Copilot-FlushDatabasePool',
    version: '3.0.0',
    description: 'Terminates idle and abandoned connection pool handles in PostgreSQL/RDS while preserving active in-flight transactions.',
    riskLevel: 'HIGH',
    riskScore: 78,
    targetService: 'RDS PostgreSQL / Aurora Cluster',
    preconditions: ['Replica lag < 100ms', 'Database CPU < 90%'],
    rollbackPlan: 'Restarts PgBouncer pooler process if connection pool does not accept new connections.',
    parameters: {
      DatabaseClusterId: 'rds-order-processor-db',
      MaxIdleTransactionTimeSeconds: '120',
      PreserveSuperuser: 'true',
    },
  },
]

export default function RunbookCatalogModal({ open, onClose }: RunbookCatalogModalProps) {
  const [selectedRunbook, setSelectedRunbook] = useState<RunbookItem>(RUNBOOKS[0])
  const [isExecutingDryRun, setIsExecutingDryRun] = useState(false)
  const [dryRunOutput, setDryRunOutput] = useState<string | null>(null)

  const handleExecuteDryRun = async () => {
    setIsExecutingDryRun(true)
    setDryRunOutput(null)
    await new Promise((r) => setTimeout(r, 1200))
    setDryRunOutput(
      `[AWS-SSM-DRYRUN] Validation Passed:
Document: ${selectedRunbook.name} (v${selectedRunbook.version})
Target Policy: Risk Score ${selectedRunbook.riskScore}/100 (${selectedRunbook.riskLevel})
Preconditions Evaluated: ALL 2 CHECKS PASSED (No locks found, replica healthy)
Simulated Blast Radius: Isolated to single availability zone
Result: DRY RUN SUCCESSFUL (Ready for automated/HITL execution)`
    )
    setIsExecutingDryRun(false)
    toast.success(`Dry run simulation for ${selectedRunbook.name} passed!`)
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
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
            width: 36,
            height: 36,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <BookIcon sx={{ color: '#fff', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography variant="h5" fontWeight="800">
            SSM Automation Runbook Catalog
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Verified AWS Systems Manager documents with safety preconditions, parameter schemas, and dry-run execution.
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent dividers sx={{ py: 3 }}>
        <Grid container spacing={3}>
          {/* Left: List of Runbooks */}
          <Grid item xs={12} md={5}>
            <Typography variant="subtitle2" fontWeight="700" sx={{ mb: 1.5 }}>
              Permitted Automation Documents:
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {RUNBOOKS.map((rb) => {
                const isSelected = selectedRunbook.name === rb.name
                return (
                  <Card
                    key={rb.name}
                    onClick={() => {
                      setSelectedRunbook(rb)
                      setDryRunOutput(null)
                    }}
                    sx={{
                      cursor: 'pointer',
                      borderRadius: 2,
                      border: '2px solid',
                      borderColor: isSelected ? 'primary.main' : 'divider',
                      backgroundColor: isSelected ? 'rgba(6,182,212,0.06)' : 'background.paper',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        borderColor: 'primary.main',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                        <Typography variant="body2" className="font-mono" fontWeight="700">
                          {rb.name}
                        </Typography>
                        <Chip
                          label={rb.riskLevel}
                          size="small"
                          color={rb.riskLevel === 'LOW' ? 'success' : rb.riskLevel === 'MEDIUM' ? 'warning' : 'error'}
                          sx={{ height: 20, fontSize: '0.65rem', fontWeight: 800 }}
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                        v{rb.version} • {rb.targetService}
                      </Typography>
                    </CardContent>
                  </Card>
                )
              })}
            </Box>
          </Grid>

          {/* Right: Selected Runbook Details */}
          <Grid item xs={12} md={7}>
            <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider', height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box>
                  <Typography variant="h6" fontWeight="800" className="font-mono" color="primary.main">
                    {selectedRunbook.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Version {selectedRunbook.version} • Target: {selectedRunbook.targetService}
                  </Typography>
                </Box>
                <Chip
                  label={`Risk Score: ${selectedRunbook.riskScore}/100`}
                  color={selectedRunbook.riskScore > 50 ? 'error' : selectedRunbook.riskScore > 25 ? 'warning' : 'success'}
                  sx={{ fontWeight: 800 }}
                />
              </Box>

              <Typography variant="body2" paragraph>
                {selectedRunbook.description}
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" fontWeight="700" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <SecurityIcon fontSize="small" color="primary" /> Safety Preconditions:
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.8, mb: 2 }}>
                {selectedRunbook.preconditions.map((pc, idx) => (
                  <Typography key={idx} variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CheckCircleIcon sx={{ fontSize: 14, color: '#10b981' }} /> {pc}
                  </Typography>
                ))}
              </Box>

              <Typography variant="subtitle2" fontWeight="700" sx={{ mb: 1 }}>
                Rollback Strategy:
              </Typography>
              <Typography variant="caption" color="text.secondary" paragraph>
                {selectedRunbook.rollbackPlan}
              </Typography>

              <Typography variant="subtitle2" fontWeight="700" sx={{ mb: 1 }}>
                Default Parameters Schema:
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 1.5,
                  borderRadius: 1.5,
                  backgroundColor: 'rgba(255,255,255,0.03)',
                  border: '1px solid',
                  borderColor: 'divider',
                  fontSize: '0.75rem',
                  fontFamily: 'JetBrains Mono, monospace',
                  color: '#38bdf8',
                  overflow: 'auto',
                  mb: 2,
                }}
              >
                {JSON.stringify(selectedRunbook.parameters, null, 2)}
              </Box>

              {isExecutingDryRun && <LinearProgress color="primary" sx={{ mb: 2, borderRadius: 1 }} />}

              {dryRunOutput && (
                <Box
                  component="pre"
                  sx={{
                    p: 2,
                    borderRadius: 1.5,
                    backgroundColor: '#050811',
                    border: '1px solid rgba(16, 185, 129, 0.4)',
                    color: '#10b981',
                    fontSize: '0.75rem',
                    fontFamily: 'JetBrains Mono, monospace',
                    whiteSpace: 'pre-wrap',
                    mb: 2,
                  }}
                >
                  {dryRunOutput}
                </Box>
              )}

              <Button
                variant="outlined"
                startIcon={<TerminalIcon />}
                disabled={isExecutingDryRun}
                onClick={handleExecuteDryRun}
                sx={{ fontWeight: 600 }}
              >
                {isExecutingDryRun ? 'Validating Preconditions...' : 'Execute Dry-Run Simulation'}
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose} variant="contained" sx={{ fontWeight: 600 }}>
          Close Catalog
        </Button>
      </DialogActions>
    </Dialog>
  )
}
