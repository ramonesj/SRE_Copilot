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
  TextField,
  Grid,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Download as DownloadIcon,
  Code as CodeIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { auditService } from '../../services/auditService'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function Audit() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [incidentFilter, setIncidentFilter] = useState('')
  const [selectedDetails, setSelectedDetails] = useState<any | null>(null)
  const [detailsModalOpen, setDetailsModalOpen] = useState(false)

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['audit-logs', page, rowsPerPage, incidentFilter],
    queryFn: () =>
      auditService.getAuditLogs({
        page: page + 1,
        page_size: rowsPerPage,
        incident_id: incidentFilter || undefined,
      }),
  })

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleExport = async () => {
    try {
      const blob = await auditService.exportAuditLogs({
        incident_id: incidentFilter || undefined,
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `sre-audit-logs-${format(new Date(), 'yyyy-MM-dd')}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Audit log CSV exported successfully')
    } catch (error) {
      toast.error('Failed to export audit logs')
    }
  }

  const handleInspectDetails = (log: any) => {
    setSelectedDetails(log)
    setDetailsModalOpen(true)
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
        Error loading audit logs.
      </Alert>
    )
  }

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="800" sx={{ letterSpacing: '-0.5px' }}>
            Immutable Audit Trail
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Append-only cryptographic record of AI diagnoses, human authorizations, and SSM executions.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Tooltip title="Refresh Logs">
            <IconButton onClick={() => refetch()} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
            sx={{
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
              fontWeight: 600,
            }}
          >
            Export CSV
          </Button>
        </Box>
      </Box>

      {/* Filter */}
      <Paper sx={{ p: 2.5, mb: 3, borderRadius: 2.5, border: '1px solid', borderColor: 'divider' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Filter by Incident ID"
              placeholder="e.g., INC-E1F2A3B4C5D2"
              value={incidentFilter}
              onChange={(e) => setIncidentFilter(e.target.value)}
              size="small"
              InputProps={{ className: 'font-mono' }}
            />
          </Grid>
          <Grid item xs={12} md={8}>
            <Typography variant="caption" color="text.secondary" fontWeight="600" sx={{ display: 'block', textAlign: { md: 'right' } }}>
              Total Recorded Security & Remediation Events: {data?.total || 0}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Audit Table */}
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
              <TableCell sx={{ fontWeight: 700 }}>Timestamp (UTC)</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Action</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Actor</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Incident ID</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Details Payload</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700 }}>Inspect</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.items.map((log) => (
              <TableRow
                key={log.id}
                hover
                sx={{
                  '&:hover': {
                    backgroundColor: 'rgba(6, 182, 212, 0.04) !important',
                  },
                }}
              >
                <TableCell sx={{ fontSize: '0.82rem', whiteSpace: 'nowrap' }}>
                  {format(new Date(log.timestamp), 'MMM dd, yyyy HH:mm:ss')}
                </TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    label={log.action}
                    sx={{
                      fontWeight: 700,
                      fontSize: '0.7rem',
                      fontFamily: 'JetBrains Mono, monospace',
                      backgroundColor:
                        log.action.includes('APPROVE') || log.action.includes('SUCCESS') || log.action.includes('RESOLVED')
                          ? 'rgba(16, 185, 129, 0.12)'
                          : log.action.includes('FAIL') || log.action.includes('REJECT')
                          ? 'rgba(239, 68, 68, 0.12)'
                          : 'rgba(56, 189, 248, 0.12)',
                      color:
                        log.action.includes('APPROVE') || log.action.includes('SUCCESS') || log.action.includes('RESOLVED')
                          ? '#10b981'
                          : log.action.includes('FAIL') || log.action.includes('REJECT')
                          ? '#ef4444'
                          : '#38bdf8',
                    }}
                  />
                </TableCell>
                <TableCell sx={{ fontSize: '0.85rem', fontWeight: 600 }}>
                  {log.actor}
                </TableCell>
                <TableCell>
                  {log.incident_id ? (
                    <Typography variant="body2" className="font-mono" color="primary.main" fontWeight="600">
                      {log.incident_id.substring(0, 16)}...
                    </Typography>
                  ) : (
                    '-'
                  )}
                </TableCell>
                <TableCell>
                  <Typography
                    variant="caption"
                    className="font-mono"
                    sx={{
                      display: 'block',
                      maxWidth: 260,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      color: 'text.secondary',
                      backgroundColor: 'rgba(255,255,255,0.02)',
                      p: 0.5,
                      borderRadius: 1,
                    }}
                  >
                    {JSON.stringify(log.details)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Inspect Raw JSON">
                    <IconButton size="small" onClick={() => handleInspectDetails(log)}>
                      <CodeIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
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

      {/* JSON Inspector Modal */}
      <Dialog
        open={detailsModalOpen}
        onClose={() => setDetailsModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            backgroundColor: '#0a0e17',
            border: '1px solid rgba(255,255,255,0.1)',
            color: '#f8fafc',
          },
        }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <Typography variant="h6" fontWeight="800" sx={{ color: '#f8fafc' }}>
            Audit Event Raw JSON Inspection
          </Typography>
          <Typography variant="caption" sx={{ color: '#94a3b8' }}>
            Event ID: {selectedDetails?.id} • Action: {selectedDetails?.action}
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ py: 3 }}>
          <Box
            component="pre"
            sx={{
              p: 2.5,
              borderRadius: 2,
              backgroundColor: '#050811',
              border: '1px solid rgba(255,255,255,0.06)',
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.82rem',
              color: '#38bdf8',
              overflow: 'auto',
              maxHeight: 400,
            }}
          >
            {JSON.stringify(selectedDetails, null, 2)}
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <Button onClick={() => setDetailsModalOpen(false)} variant="contained" sx={{ fontWeight: 600 }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
