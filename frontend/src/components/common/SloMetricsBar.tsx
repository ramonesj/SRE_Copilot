import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  Tooltip,
  useTheme,
} from '@mui/material'
import {
  Speed as SpeedIcon,
  Timer as TimerIcon,
  CheckCircle as CheckCircleIcon,
  OpenInNew as OpenInNewIcon,
  Bolt as BoltIcon,
  QueryStats as QueryStatsIcon,
  Insights as InsightsIcon,
} from '@mui/icons-material'
import SimulateIncidentModal from './SimulateIncidentModal'

export default function SloMetricsBar() {
  const theme = useTheme()
  const isDark = theme.palette.mode === 'dark'
  const [injectModalOpen, setInjectModalOpen] = useState(false)

  return (
    <>
      <Paper
        elevation={0}
        sx={{
          p: 2.5,
          mb: 3,
          borderRadius: 2.5,
          border: '1px solid',
          borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(203, 213, 225, 0.9)',
          backgroundColor: isDark ? '#0f172a' : '#f1f5f9',
          backgroundImage: isDark
            ? 'linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.7) 100%)'
            : 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
        }}
      >
        <Grid container spacing={2} alignItems="center">
          {/* SLO Metric 1: MTTD */}
          <Grid item xs={6} sm={3} md={2}>
            <Box>
              <Typography
                variant="caption"
                color={isDark ? 'text.secondary' : '#475569'}
                fontWeight="600"
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
              >
                <TimerIcon sx={{ fontSize: 14, color: isDark ? '#38bdf8' : '#0284c7' }} /> MTTD (Detect)
              </Typography>
              <Typography variant="h6" fontWeight="800" color="primary.main">
                38s
              </Typography>
              <Typography variant="caption" color="success.main" sx={{ fontSize: '0.68rem', fontWeight: 700 }}>
                ● Target &lt; 60s (Met)
              </Typography>
            </Box>
          </Grid>

          {/* SLO Metric 2: MTTR */}
          <Grid item xs={6} sm={3} md={2}>
            <Box>
              <Typography
                variant="caption"
                color={isDark ? 'text.secondary' : '#475569'}
                fontWeight="600"
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
              >
                <SpeedIcon sx={{ fontSize: 14, color: '#10b981' }} /> MTTR (Remediate)
              </Typography>
              <Typography variant="h6" fontWeight="800" color="success.main">
                2.1m
              </Typography>
              <Typography variant="caption" color="success.main" sx={{ fontSize: '0.68rem', fontWeight: 700 }}>
                ● Target &lt; 5.0m (Met)
              </Typography>
            </Box>
          </Grid>

          {/* SLO Metric 3: Success Rate */}
          <Grid item xs={6} sm={3} md={2}>
            <Box>
              <Typography
                variant="caption"
                color={isDark ? 'text.secondary' : '#475569'}
                fontWeight="600"
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
              >
                <CheckCircleIcon sx={{ fontSize: 14, color: '#f59e0b' }} /> Auto-Success Rate
              </Typography>
              <Typography variant="h6" fontWeight="800" color="warning.main">
                94.2%
              </Typography>
              <Typography variant="caption" color={isDark ? 'text.secondary' : '#64748b'} sx={{ fontSize: '0.68rem' }}>
                43 Audit Verified
              </Typography>
            </Box>
          </Grid>

          {/* SLO Metric 4: Availability */}
          <Grid item xs={6} sm={3} md={2}>
            <Box>
              <Typography variant="caption" color={isDark ? 'text.secondary' : '#475569'} fontWeight="600">
                Fleet SLA Availability
              </Typography>
              <Typography variant="h6" fontWeight="800" color="text.primary">
                99.98%
              </Typography>
              <Typography variant="caption" color="success.main" sx={{ fontSize: '0.68rem', fontWeight: 700 }}>
                Triple-9 Invariant
              </Typography>
            </Box>
          </Grid>

          {/* Actions: Grafana, Prometheus & Inject Live Incident */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' }, gap: 1, flexWrap: 'wrap' }}>
              <Tooltip title="Open Live Grafana Dashboards (Port 3001)">
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<InsightsIcon />}
                  endIcon={<OpenInNewIcon sx={{ fontSize: '12px !important' }} />}
                  onClick={() => window.open('http://localhost:3001', '_blank')}
                  sx={{
                    textTransform: 'none',
                    fontSize: '0.78rem',
                    borderColor: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(203,213,225,1)',
                    color: isDark ? 'text.primary' : '#334155',
                    backgroundColor: isDark ? 'transparent' : '#ffffff',
                  }}
                >
                  Grafana
                </Button>
              </Tooltip>

              <Tooltip title="Open Prometheus Metric Explorer (Port 9090)">
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<QueryStatsIcon />}
                  endIcon={<OpenInNewIcon sx={{ fontSize: '12px !important' }} />}
                  onClick={() => window.open('http://localhost:9090', '_blank')}
                  sx={{
                    textTransform: 'none',
                    fontSize: '0.78rem',
                    borderColor: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(203,213,225,1)',
                    color: isDark ? 'text.primary' : '#334155',
                    backgroundColor: isDark ? 'transparent' : '#ffffff',
                  }}
                >
                  Prometheus
                </Button>
              </Tooltip>

              <Button
                size="small"
                variant="contained"
                startIcon={<BoltIcon />}
                onClick={() => setInjectModalOpen(true)}
                sx={{
                  background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
                  color: '#fff',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  boxShadow: '0 4px 12px rgba(245, 158, 11, 0.35)',
                }}
              >
                Inject Live Incident
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Incident Injector Modal */}
      <SimulateIncidentModal
        open={injectModalOpen}
        onClose={() => setInjectModalOpen(false)}
      />
    </>
  )
}
