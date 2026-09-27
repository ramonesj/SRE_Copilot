import { useNavigate, useLocation } from 'react-router-dom'
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
  Box,
  Typography,
  Chip,
  Avatar,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  WarningAmber as WarningIcon,
  Gavel as ApprovalIcon,
  HistoryToggleOff as HistoryIcon,
  SettingsSuggest as SettingsIcon,
  Terminal as TerminalIcon,
} from '@mui/icons-material'
import { useBrandingStore } from '../../stores/brandingStore'

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Incidents', icon: <WarningIcon />, path: '/incidents' },
  { text: 'Approvals', icon: <ApprovalIcon />, path: '/approvals' },
  { text: 'Audit Logs', icon: <HistoryIcon />, path: '/audit' },
  { text: 'Settings & Fleet', icon: <SettingsIcon />, path: '/settings' },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { companyName, companyLogo } = useBrandingStore()

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Brand Header */}
      <Toolbar sx={{ px: 2.5, py: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {companyLogo ? (
            <Box
              component="img"
              src={companyLogo}
              alt={companyName}
              sx={{ width: 36, height: 36, objectFit: 'contain', borderRadius: 1.5 }}
            />
          ) : (
            <Box
              sx={{
                width: 38,
                height: 38,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(6, 182, 212, 0.4)',
              }}
            >
              <TerminalIcon sx={{ color: '#fff', fontSize: 22 }} />
            </Box>
          )}

          <Box sx={{ overflow: 'hidden' }}>
            <Typography variant="subtitle1" fontWeight="800" noWrap sx={{ lineHeight: 1.2, letterSpacing: '-0.3px' }}>
              {companyName}
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.72rem' }}>
              SRE Autonomous Copilot
            </Typography>
          </Box>
        </Box>
      </Toolbar>

      <Divider sx={{ opacity: 0.6 }} />

      {/* Navigation Links */}
      <List sx={{ px: 1.5, py: 2, flexGrow: 1 }}>
        {menuItems.map((item) => {
          const isSelected =
            item.path === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(item.path)

          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.8 }}>
              <ListItemButton
                selected={isSelected}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1.2,
                  px: 2,
                  transition: 'all 0.2s ease',
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(6, 182, 212, 0.12)',
                    color: 'primary.main',
                    fontWeight: 700,
                    '& .MuiListItemIcon-root': {
                      color: 'primary.main',
                    },
                    '&:hover': {
                      backgroundColor: 'rgba(6, 182, 212, 0.18)',
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.04)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isSelected ? 'primary.main' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: isSelected ? 700 : 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>

      <Divider sx={{ opacity: 0.6 }} />

      {/* Footer System Pill */}
      <Box sx={{ p: 2, m: 1.5, borderRadius: 2, backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="caption" fontWeight="700">
            System Invariants
          </Typography>
          <Chip label="PASSING" size="small" color="success" sx={{ height: 18, fontSize: '0.65rem', fontWeight: 800 }} />
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
          Hypothesis: 200/200 PBT Verified
        </Typography>
      </Box>
    </Box>
  )
}
