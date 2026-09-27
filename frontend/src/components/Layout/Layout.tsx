import { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  useTheme,
  useMediaQuery,
  Chip,
  Tooltip,
  Button,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Brightness4 as DarkIcon,
  Brightness7 as LightIcon,
  Sensors as SensorsIcon,
  Shield as ShieldIcon,
  Bolt as BoltIcon,
} from '@mui/icons-material'
import Sidebar from './Sidebar'
import SimulateIncidentModal from '../common/SimulateIncidentModal'
import { useAppStore } from '../../stores/appStore'

const drawerWidth = 260

export default function Layout() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const { sidebarOpen, toggleSidebar, theme: themeMode, toggleTheme } = useAppStore()
  const [time, setTime] = useState(new Date().toUTCString().slice(17, 25))
  const [simulateOpen, setSimulateOpen] = useState(false)

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toUTCString().slice(17, 25))
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: 'background.default' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { md: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : '100%' },
          ml: { md: sidebarOpen ? `${drawerWidth}px` : 0 },
          backgroundColor: theme.palette.mode === 'dark' ? 'rgba(15, 23, 42, 0.85)' : 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid',
          borderColor: 'divider',
          color: 'text.primary',
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={toggleSidebar}
            >
              <MenuIcon />
            </IconButton>

            {/* Live Operational Status Pills */}
            <Box sx={{ display: { xs: 'none', sm: 'flex' }, alignItems: 'center', gap: 1.5 }}>
              <Chip
                icon={<SensorsIcon sx={{ fontSize: '16px !important', color: '#10b981 !important' }} />}
                label="Autonomous Engine Active"
                size="small"
                sx={{
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  color: '#10b981',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  border: '1px solid rgba(16, 185, 129, 0.25)',
                }}
              />
              <Chip
                icon={<ShieldIcon sx={{ fontSize: '16px !important', color: '#06b6d4 !important' }} />}
                label="AWS SSM: Connected"
                size="small"
                sx={{
                  backgroundColor: 'rgba(6, 182, 212, 0.1)',
                  color: '#06b6d4',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  border: '1px solid rgba(6, 182, 212, 0.25)',
                }}
              />
            </Box>
          </Box>

          {/* Right Header Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Button
              size="small"
              variant="contained"
              startIcon={<BoltIcon />}
              onClick={() => setSimulateOpen(true)}
              sx={{
                display: { xs: 'none', sm: 'flex' },
                background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
                color: '#fff',
                fontWeight: 700,
                fontSize: '0.78rem',
                boxShadow: '0 4px 10px rgba(245, 158, 11, 0.3)',
              }}
            >
              Inject Live Incident
            </Button>

            <Typography
              variant="caption"
              className="font-mono"
              sx={{
                display: { xs: 'none', md: 'block' },
                color: 'text.secondary',
                backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)',
                px: 1.5,
                py: 0.5,
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              UTC: {time}
            </Typography>

            <Tooltip title={`Switch to ${themeMode === 'dark' ? 'Light' : 'Dark'} Mode`}>
              <IconButton onClick={toggleTheme} color="inherit">
                {themeMode === 'dark' ? <LightIcon sx={{ color: '#fbbf24' }} /> : <DarkIcon />}
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar Navigation */}
      <Box
        component="nav"
        sx={{ width: { md: sidebarOpen ? drawerWidth : 0 }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={isMobile && sidebarOpen}
          onClose={toggleSidebar}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: 'background.paper',
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
        >
          <Sidebar />
        </Drawer>

        <Drawer
          variant="persistent"
          open={!isMobile && sidebarOpen}
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: 'background.paper',
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
        >
          <Sidebar />
        </Drawer>
      </Box>

      {/* Main Content Viewport */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, md: 3.5 },
          width: { md: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : '100%' },
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>

      {/* Global Chaos / Incident Simulator Modal */}
      <SimulateIncidentModal
        open={simulateOpen}
        onClose={() => setSimulateOpen(false)}
      />
    </Box>
  )
}
