import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Grid,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Divider,
} from '@mui/material'
import {
  WarningAmber as WarningIcon,
  CheckCircleOutline as CheckCircleIcon,
  ErrorOutline as ErrorIcon,
  HourglassTop as HourglassIcon,
  Dns as DnsIcon,
  TrendingUp as TrendingUpIcon,
  ArrowForward as ArrowForwardIcon,
  AutoAwesome as AutoAwesomeIcon,
  MenuBook as BookIcon,
  Bolt as BoltIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import StatCard from '../../components/common/StatCard'
import StatusChip from '../../components/common/StatusChip'
import SloMetricsBar from '../../components/common/SloMetricsBar'
import RunbookCatalogModal from '../../components/common/RunbookCatalogModal'
import SimulateIncidentModal from '../../components/common/SimulateIncidentModal'
import { incidentService } from '../../services/incidentService'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

const PIE_COLORS = ['#38bdf8', '#10b981', '#f59e0b', '#ef4444', '#a855f7', '#6366f1']

export default function Dashboard() {
  const navigate = useNavigate()
  const [runbookModalOpen, setRunbookModalOpen] = useState(false)
  const [simulateModalOpen, setSimulateModalOpen] = useState(false)

  const { data: metrics, isLoading, error } = useQuery({
    queryKey: ['incident-metrics'],
    queryFn: incidentService.getMetrics,
    refetchInterval: 15000,
  })

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
        Error loading dashboard metrics. Ensure backend is running.
      </Alert>
    )
  }

  const severityData = metrics
    ? Object.entries(metrics.by_severity || {}).map(([name, value]) => ({ name, value }))
    : []

  const statusData = metrics
    ? Object.entries(metrics.by_status || {}).map(([name, value]) => ({
        name: name.replace(/_/g, ' '),
        rawName: name,
        value,
      }))
    : []

  return (
    <Box sx={{ pb: 6 }}>
      {/* Top Banner */}
      <Paper
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          background: 'linear-gradient(135deg, rgba(6,182,212,0.12) 0%, rgba(59,130,246,0.06) 50%, rgba(139,92,246,0.08) 100%)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: { md: 'center' }, gap: 2 }}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
              <AutoAwesomeIcon sx={{ color: '#06b6d4', fontSize: 26 }} />
              <Typography variant="h5" fontWeight="800">
                SRE Copilot Mission Control
              </Typography>
              <Chip
                label="LIVE AUTOPILOT"
                size="small"
                sx={{
                  backgroundColor: 'rgba(6, 182, 212, 0.2)',
                  color: '#06b6d4',
                  fontWeight: 800,
                  fontSize: '0.68rem',
                  border: '1px solid rgba(6, 182, 212, 0.4)',
                }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              AI-driven incident triage, deterministic risk modeling, and human-in-the-loop SSM runbook remediation.
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
            <Button
              variant="outlined"
              startIcon={<BookIcon />}
              onClick={() => setRunbookModalOpen(true)}
              sx={{ borderColor: 'divider' }}
            >
              SSM Runbooks (5)
            </Button>
            <Button
              variant="outlined"
              startIcon={<DnsIcon />}
              onClick={() => navigate('/settings')}
              sx={{ borderColor: 'divider' }}
            >
              Fleet (6 Nodes)
            </Button>
            <Button
              variant="contained"
              endIcon={<ArrowForwardIcon />}
              onClick={() => navigate('/approvals')}
              sx={{
                background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
                boxShadow: '0 4px 14px rgba(6, 182, 212, 0.4)',
                fontWeight: 600,
              }}
            >
              Review Approvals ({metrics?.pending_approvals || 0})
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* SLI / SLO Metrics & Chaos Simulator Bar */}
      <SloMetricsBar />

      {/* KPI Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Incidents"
            value={metrics?.total || 0}
            icon={<WarningIcon sx={{ fontSize: 28 }} />}
            color="#f59e0b"
            trend="flat"
            trendValue="Seeded & Live"
            subtitle="Recorded across fleet"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Incidents"
            value={metrics?.active || 0}
            icon={<ErrorIcon sx={{ fontSize: 28 }} />}
            color="#ef4444"
            trend="up"
            trendValue={`${metrics?.active || 0} Open`}
            subtitle="Requires attention"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Resolved Incidents"
            value={metrics?.resolved || 0}
            icon={<CheckCircleIcon sx={{ fontSize: 28 }} />}
            color="#10b981"
            trend="up"
            trendValue="30% Success Rate"
            subtitle="Recovered & Verified"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending HITL Approvals"
            value={metrics?.pending_approvals || 0}
            icon={<HourglassIcon sx={{ fontSize: 28 }} />}
            color="#06b6d4"
            trend="down"
            trendValue="Awaiting SRE Auth"
            subtitle="Safety gate active"
          />
        </Grid>
      </Grid>

      {/* Visual Charts */}
      <Grid container spacing={3}>
        {/* Incidents by Severity Pie Chart */}
        <Grid item xs={12} md={5}>
          <Paper
            sx={{
              p: 3,
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight="700">
                Incidents by Severity
              </Typography>
              <Chip label="Risk Profile" size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
            </Box>
            <Divider sx={{ mb: 2 }} />

            <Box sx={{ flexGrow: 1, minHeight: 280 }}>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={95}
                    paddingAngle={4}
                    dataKey="value"
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      color: '#f8fafc',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Incidents by Status Bar Chart */}
        <Grid item xs={12} md={7}>
          <Paper
            sx={{
              p: 3,
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight="700">
                Incident State Distribution
              </Typography>
              <Button size="small" onClick={() => navigate('/incidents')} sx={{ textTransform: 'none' }}>
                View All Incidents →
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />

            <Box sx={{ flexGrow: 1, minHeight: 280 }}>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={statusData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="name"
                    stroke="#94a3b8"
                    fontSize={11}
                    interval={0}
                    angle={-15}
                    textAnchor="end"
                  />
                  <YAxis stroke="#94a3b8" fontSize={12} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      color: '#f8fafc',
                    }}
                  />
                  <Bar dataKey="value" fill="#06b6d4" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
      </Grid>
      {/* SSM Runbook Catalog Explorer Modal */}
      <RunbookCatalogModal
        open={runbookModalOpen}
        onClose={() => setRunbookModalOpen(false)}
      />
    </Box>
  )
}
