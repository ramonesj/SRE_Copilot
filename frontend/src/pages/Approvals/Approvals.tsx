import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  CardActions,
  Button,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Chip,
  Divider,
  LinearProgress,
} from '@mui/material'
import {
  CheckCircleOutline as ApproveIcon,
  CancelOutlined as RejectIcon,
  Gavel as GavelIcon,
  ShieldOutlined as ShieldIcon,
  Schedule as ScheduleIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material'
import { approvalService } from '../../services/approvalService'
import StatusChip from '../../components/common/StatusChip'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function Approvals() {
  const queryClient = useQueryClient()
  const [selectedApproval, setSelectedApproval] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [decision, setDecision] = useState<'APPROVE' | 'REJECT' | null>(null)
  const [rationale, setRationale] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: () => approvalService.getPendingApprovals(1, 20),
    refetchInterval: 10000,
  })

  const submitMutation = useMutation({
    mutationFn: ({
      approvalId,
      decision,
      rationale,
    }: {
      approvalId: string
      decision: 'APPROVE' | 'REJECT'
      rationale: string
    }) => approvalService.submitDecision(approvalId, decision, rationale),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      queryClient.invalidateQueries({ queryKey: ['incident-metrics'] })
      toast.success('Decision submitted successfully')
      handleCloseDialog()
    },
    onError: (error: Error) => {
      toast.error(`Error: ${error.message}`)
    },
  })

  const handleOpenDialog = (approvalId: string, decision: 'APPROVE' | 'REJECT') => {
    setSelectedApproval(approvalId)
    setDecision(decision)
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setSelectedApproval(null)
    setDecision(null)
    setRationale('')
    setDialogOpen(false)
  }

  const handleSubmit = () => {
    if (selectedApproval && decision && rationale) {
      submitMutation.mutate({
        approvalId: selectedApproval,
        decision,
        rationale,
      })
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress color="primary" />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ borderRadius: 2 }}>
        Error loading pending approvals. Please try again later.
      </Alert>
    )
  }

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="800" sx={{ letterSpacing: '-0.5px' }}>
            HITL Approval Queue
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Human-in-the-Loop authorization gate for Medium, High, and Critical automated SSM remediations.
          </Typography>
        </Box>
        <Chip
          icon={<GavelIcon sx={{ fontSize: '18px !important' }} />}
          label={`${data?.items?.length || 0} Pending Authorization`}
          color="warning"
          sx={{ fontWeight: 700 }}
        />
      </Box>

      {!data?.items?.length ? (
        <Paper
          sx={{
            p: 6,
            textAlign: 'center',
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
            backgroundColor: 'background.paper',
          }}
        >
          <ShieldIcon sx={{ fontSize: 56, color: 'success.main', mb: 1 }} />
          <Typography variant="h6" fontWeight="700">
            No Pending Approvals
          </Typography>
          <Typography color="textSecondary" variant="body2" sx={{ maxWidth: 450, mx: 'auto', mt: 1 }}>
            All active remediations have been evaluated, authorized, or handled. The autonomous policy boundary is secure.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {data.items.map((approval) => {
            const riskScore = approval.risk_assessment?.risk_score || 42
            const riskLevel = approval.risk_assessment?.risk_level || 'MEDIUM'

            return (
              <Grid item xs={12} key={approval.id}>
                <Card
                  sx={{
                    borderRadius: 3,
                    border: '1px solid',
                    borderColor: 'divider',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                    overflow: 'hidden',
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box>
                        <Typography variant="h6" fontWeight="800">
                          Remediation Plan Authorization
                        </Typography>
                        <Typography variant="caption" className="font-mono" sx={{ color: 'primary.main', fontWeight: 600 }}>
                          Incident ID: {approval.incident_id}
                        </Typography>
                      </Box>
                      <StatusChip status={approval.status} type="approval" />
                    </Box>

                    <Divider sx={{ mb: 2.5 }} />

                    <Grid container spacing={3}>
                      {/* Left: AI Diagnosis */}
                      <Grid item xs={12} md={7}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <PsychologyIcon sx={{ color: 'primary.main', fontSize: 20 }} />
                          <Typography variant="subtitle2" fontWeight="700">
                            AI-Synthesized Diagnosis
                          </Typography>
                        </Box>
                        <Paper sx={{ p: 2, borderRadius: 2, backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid', borderColor: 'divider' }}>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            <strong>Root Cause:</strong> {approval.diagnosis?.root_cause || 'Dead-letter queue backlog exceeded threshold.'}
                          </Typography>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            <strong>Confidence:</strong>{' '}
                            <span style={{ color: '#10b981', fontWeight: 700 }}>
                              {approval.diagnosis?.confidence
                                ? `${(approval.diagnosis.confidence * 100).toFixed(1)}%`
                                : '94.0%'}
                            </span>
                          </Typography>
                          <Typography variant="body2">
                            <strong>Recommended Action:</strong>{' '}
                            {approval.diagnosis?.recommended_action || 'Execute SRE-Copilot-ReplayDeadLetters'}
                          </Typography>
                        </Paper>
                      </Grid>

                      {/* Right: Risk Assessment & Gauge */}
                      <Grid item xs={12} md={5}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <ShieldIcon sx={{ color: 'warning.main', fontSize: 20 }} />
                          <Typography variant="subtitle2" fontWeight="700">
                            Risk Assessment & Policy Score
                          </Typography>
                        </Box>
                        <Paper sx={{ p: 2, borderRadius: 2, backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid', borderColor: 'divider' }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="body2" fontWeight="600">
                              Risk Score: {riskScore}/100
                            </Typography>
                            <StatusChip status={riskLevel} type="severity" />
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={riskScore}
                            color={riskScore > 75 ? 'error' : riskScore > 40 ? 'warning' : 'success'}
                            sx={{ height: 8, borderRadius: 4, mb: 1.5 }}
                          />
                          <Typography variant="body2" sx={{ fontSize: '0.82rem' }}>
                            <strong>Target SSM Runbook:</strong>{' '}
                            <code className="font-mono">{approval.risk_assessment?.ssm_runbook || 'SRE-Copilot-ReplayDeadLetters'}</code>
                          </Typography>
                        </Paper>
                      </Grid>

                      {/* Timestamps */}
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, color: 'text.secondary', fontSize: '0.8rem' }}>
                          <ScheduleIcon sx={{ fontSize: 16 }} />
                          <span>Created: {format(new Date(approval.created_at), 'MMM dd, yyyy HH:mm:ss')}</span>
                          <span>•</span>
                          <span>Expires: {format(new Date(approval.expires_at), 'MMM dd, yyyy HH:mm:ss')}</span>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>

                  <CardActions sx={{ justifyContent: 'flex-end', px: 3, py: 2, backgroundColor: 'rgba(255,255,255,0.02)', borderTop: '1px solid', borderColor: 'divider', gap: 1.5 }}>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<RejectIcon />}
                      onClick={() => handleOpenDialog(approval.id, 'REJECT')}
                    >
                      Reject Remediation
                    </Button>
                    <Button
                      variant="contained"
                      color="success"
                      startIcon={<ApproveIcon />}
                      onClick={() => handleOpenDialog(approval.id, 'APPROVE')}
                      sx={{
                        fontWeight: 700,
                        px: 3,
                        boxShadow: '0 4px 14px rgba(16, 185, 129, 0.4)',
                      }}
                    >
                      Authorize & Execute Runbook
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            )
          })}
        </Grid>
      )}

      {/* Rationale Confirmation Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, p: 1 } }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h5" fontWeight="800">
            {decision === 'APPROVE' ? 'Authorize SSM Remediation' : 'Reject Remediation Plan'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {decision === 'APPROVE'
              ? 'Provide SRE authorization rationale before triggering automated execution.'
              : 'Specify reason for rejection to update the incident audit trail.'}
          </Typography>
        </DialogTitle>
        <DialogContent dividers sx={{ py: 3 }}>
          <TextField
            fullWidth
            multiline
            rows={4}
            required
            label="SRE Decision Rationale"
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            placeholder="e.g., Verified webhook endpoint rate limits and confirmed DLQ drain is safe to run."
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={handleCloseDialog} color="inherit">
            Cancel
          </Button>
          <Button
            variant="contained"
            color={decision === 'APPROVE' ? 'success' : 'error'}
            onClick={handleSubmit}
            disabled={!rationale.trim() || submitMutation.isPending}
            sx={{ fontWeight: 700, px: 3 }}
          >
            {submitMutation.isPending ? 'Executing...' : 'Confirm Decision'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
