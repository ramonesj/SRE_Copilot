import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Divider,
  Chip,
} from '@mui/material'
import {
  Visibility as VisibilityIcon,
  Refresh as RefreshIcon,
  ContentCopy as CopyIcon,
  Check as CheckIcon,
  Terminal as TerminalIcon,
  Search as SearchIcon,
  Description as DescriptionIcon,
  Bolt as BoltIcon,
} from '@mui/icons-material'
import StatusChip from '../../components/common/StatusChip'
import PostMortemModal from '../../components/common/PostMortemModal'
import SimulateIncidentModal from '../../components/common/SimulateIncidentModal'
import { incidentService } from '../../services/incidentService'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function Incidents() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [statusFilter, setStatusFilter] = useState('')
  const [severityFilter, setSeverityFilter] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedIncident, setSelectedIncident] = useState<any | null>(null)
  const [detailModalOpen, setDetailModalOpen] = useState(false)
  const [postMortemIncident, setPostMortemIncident] = useState<any | null>(null)
  const [postMortemOpen, setPostMortemOpen] = useState(false)
  const [simulateOpen, setSimulateOpen] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['incidents', page, rowsPerPage, statusFilter, severityFilter],
    queryFn: () =>
      incidentService.getIncidents({
        page: page + 1,
        page_size: rowsPerPage,
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
      }),
  })

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(text)
    toast.success(`Copied: ${text}`)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleViewIncident = (incident: any) => {
    setSelectedIncident(incident)
    setDetailModalOpen(true)
  }

  const handleOpenPostMortem = (incident: any) => {
    setPostMortemIncident(incident)
    setPostMortemOpen(true)
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
        Error loading incidents. Please try again later.
      </Alert>
    )
  }

  const filteredItems = (data?.items || []).filter((inc: any) => {
    if (!searchTerm) return true
    const term = searchTerm.toLowerCase()
    const id = (inc.incident_id || String(inc.id)).toLowerCase()
    const svc = (inc.service || inc.service_name || '').toLowerCase()
    const node = (inc.instance_id || inc.node_id || '').toLowerCase()
    return id.includes(term) || svc.includes(term) || node.includes(term)
  })

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight="800" sx={{ letterSpacing: '-0.5px' }}>
            Incident Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Triaged anomalies, AI-synthesized root cause analyses, and automated remediation states.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button
            variant="contained"
            startIcon={<BoltIcon />}
            onClick={() => setSimulateOpen(true)}
            sx={{
              background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
              color: '#fff',
              fontWeight: 700,
              boxShadow: '0 4px 12px rgba(245, 158, 11, 0.35)',
            }}
          >
            Inject Live Incident
          </Button>
          <Tooltip title="Refresh Incidents">
            <IconButton onClick={() => refetch()} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Filters Bar */}
      <Paper sx={{ p: 2.5, mb: 3, borderRadius: 2.5, border: '1px solid', borderColor: 'divider' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search by ID, service, or node..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ color: 'text.secondary', mr: 1, fontSize: 20 }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              select
              fullWidth
              label="Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Statuses</MenuItem>
              <MenuItem value="CREATED">Created</MenuItem>
              <MenuItem value="DIAGNOSIS_COMPLETE">Diagnosis Complete</MenuItem>
              <MenuItem value="APPROVED">Approved</MenuItem>
              <MenuItem value="EXECUTING">Executing</MenuItem>
              <MenuItem value="RESOLVED">Resolved</MenuItem>
              <MenuItem value="RECOVERY_FAILED">Recovery Failed</MenuItem>
              <MenuItem value="REJECTED">Rejected</MenuItem>
              <MenuItem value="TIMEOUT_EXCEEDED">Timeout Exceeded</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              select
              fullWidth
              label="Severity"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Severities</MenuItem>
              <MenuItem value="LOW">Low</MenuItem>
              <MenuItem value="MEDIUM">Medium</MenuItem>
              <MenuItem value="HIGH">High</MenuItem>
              <MenuItem value="CRITICAL">Critical</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Typography variant="caption" color="text.secondary" fontWeight="600" sx={{ display: 'block', textAlign: 'right' }}>
              Showing {filteredItems.length} of {data?.total || 0} incidents
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Incidents Table */}
      <TableContainer
        component={Paper}
        sx={{
          borderRadius: 2.5,
          border: '1px solid',
          borderColor: 'divider',
          overflow: 'hidden',
        }}
      >
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: 'rgba(255,255,255,0.02)' }}>
              <TableCell sx={{ fontWeight: 700 }}>Incident ID</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Service</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Severity</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Target Node</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Created (UTC)</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredItems.map((incident: any) => {
              const incId = incident.incident_id || String(incident.id)
              const service = incident.service || incident.service_name || 'N/A'
              const node = incident.instance_id || incident.node_id || '-'

              return (
                <TableRow
                  key={incident.id}
                  hover
                  sx={{
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'rgba(6, 182, 212, 0.04) !important',
                    },
                  }}
                  onClick={() => handleViewIncident(incident)}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" className="font-mono" fontWeight="700" color="primary.main">
                        {incId}
                      </Typography>
                      <Tooltip title="Copy ID">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleCopy(incId)
                          }}
                        >
                          {copiedId === incId ? <CheckIcon fontSize="small" color="success" /> : <CopyIcon fontSize="small" />}
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="600">
                      {service}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <StatusChip status={incident.severity} type="severity" />
                  </TableCell>
                  <TableCell>
                    <StatusChip status={incident.status} type="status" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" className="font-mono" color="text.secondary">
                      {node}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {incident.created_at ? format(new Date(incident.created_at), 'MMM dd, yyyy HH:mm') : '-'}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 0.5 }}>
                      <Tooltip title="Inspect Triage & Diagnosis">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleViewIncident(incident)
                          }}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>

                      <Tooltip title="Generate SRE Post-Mortem Report">
                        <IconButton
                          size="small"
                          color="info"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleOpenPostMortem(incident)
                          }}
                        >
                          <DescriptionIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={data?.total || 0}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      </TableContainer>

      {/* Incident Detail Modal */}
      <Dialog
        open={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, p: 1 },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h5" fontWeight="800">
                Incident Triage Details
              </Typography>
              <Typography variant="body2" className="font-mono" color="primary.main">
                {selectedIncident?.incident_id || selectedIncident?.id}
              </Typography>
            </Box>
            {selectedIncident && <StatusChip status={selectedIncident.status} />}
          </Box>
        </DialogTitle>

        <DialogContent dividers sx={{ py: 3 }}>
          {selectedIncident && (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">
                  Service / Workload
                </Typography>
                <Typography variant="body1" fontWeight="700">
                  {selectedIncident.service || selectedIncident.service_name}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">
                  Target Node ID
                </Typography>
                <Typography variant="body1" className="font-mono" fontWeight="600">
                  {selectedIncident.instance_id || selectedIncident.node_id}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="caption" color="text.secondary">
                  Severity Level
                </Typography>
                <Box sx={{ mt: 0.5 }}>
                  <StatusChip status={selectedIncident.severity} type="severity" />
                </Box>
              </Grid>

              <Grid item xs={12}>
                <Divider />
              </Grid>

              {/* Diagnosis Details */}
              <Grid item xs={12}>
                <Typography variant="subtitle1" fontWeight="800" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TerminalIcon sx={{ color: 'primary.main' }} /> AI Diagnosis & Root Cause
                </Typography>
                <Paper sx={{ p: 2, borderRadius: 2, backgroundColor: 'rgba(6, 182, 212, 0.05)', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Root Cause:</strong> {selectedIncident.diagnosis?.root_cause || 'Dead-letter queue backlog exceeded threshold after webhook destination throttling.'}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Confidence Score:</strong>{' '}
                    <Chip
                      size="small"
                      label={`${((selectedIncident.diagnosis?.confidence || 0.94) * 100).toFixed(1)}%`}
                      color="success"
                      sx={{ height: 20, fontSize: '0.72rem', fontWeight: 800 }}
                    />
                  </Typography>
                  <Typography variant="body2">
                    <strong>Recommended Runbook:</strong>{' '}
                    <code className="font-mono">
                      {selectedIncident.risk_assessment?.ssm_runbook || 'SRE-Copilot-ReplayDeadLetters'}
                    </code>
                  </Typography>
                </Paper>
              </Grid>

              {/* Risk Assessment */}
              <Grid item xs={12}>
                <Typography variant="subtitle1" fontWeight="800" gutterBottom>
                  Policy & Risk Assessment
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="caption" color="text.secondary">
                        Calculated Risk Score
                      </Typography>
                      <Typography variant="h4" fontWeight="800" color="warning.main">
                        {selectedIncident.risk_assessment?.risk_score || 42}/100
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Level: {selectedIncident.risk_assessment?.risk_level || 'MEDIUM'}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
                      <Typography variant="caption" color="text.secondary">
                        Human Authorization Gate
                      </Typography>
                      <Typography variant="h6" fontWeight="700" color="info.main">
                        HITL Mandatory
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Requires SRE On-call authorization before execution
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2, justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            startIcon={<DescriptionIcon />}
            onClick={() => {
              setDetailModalOpen(false)
              handleOpenPostMortem(selectedIncident)
            }}
          >
            Export Post-Mortem
          </Button>
          <Button onClick={() => setDetailModalOpen(false)} variant="contained" sx={{ fontWeight: 600 }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Post-Mortem Modal */}
      <PostMortemModal
        open={postMortemOpen}
        onClose={() => setPostMortemOpen(false)}
        incident={postMortemIncident}
      />

      {/* Live Chaos Simulator Modal */}
      <SimulateIncidentModal
        open={simulateOpen}
        onClose={() => setSimulateOpen(false)}
      />
    </Box>
  )
}
