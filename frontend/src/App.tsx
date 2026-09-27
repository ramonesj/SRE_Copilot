import { useMemo } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard/Dashboard'
import Incidents from './pages/Incidents/Incidents'
import Approvals from './pages/Approvals/Approvals'
import Audit from './pages/Audit/Audit'
import Settings from './pages/Settings/Settings'
import { useAppStore } from './stores/appStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
})

function App() {
  const themeMode = useAppStore((state) => state.theme)

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: themeMode,
          ...(themeMode === 'dark'
            ? {
                primary: {
                  main: '#06b6d4', // Neon Cyan
                  light: '#38bdf8',
                  dark: '#0891b2',
                  contrastText: '#0f172a',
                },
                secondary: {
                  main: '#a855f7', // Purple Neon
                  light: '#c084fc',
                  dark: '#7e22ce',
                },
                background: {
                  default: '#070b14',
                  paper: '#0f172a',
                },
                text: {
                  primary: '#f8fafc',
                  secondary: '#94a3b8',
                },
                divider: 'rgba(255, 255, 255, 0.08)',
                success: { main: '#10b981', light: '#34d399', dark: '#059669' },
                warning: { main: '#f59e0b', light: '#fbbf24', dark: '#d97706' },
                error: { main: '#ef4444', light: '#f87171', dark: '#dc2626' },
                info: { main: '#38bdf8', light: '#7dd3fc', dark: '#0284c7' },
              }
            : {
                primary: {
                  main: '#0284c7',
                  light: '#38bdf8',
                  dark: '#0369a1',
                },
                secondary: {
                  main: '#7c3aed',
                },
                background: {
                  default: '#f8fafc',
                  paper: '#ffffff',
                },
                text: {
                  primary: '#0f172a',
                  secondary: '#64748b',
                },
                divider: 'rgba(0, 0, 0, 0.08)',
                success: { main: '#10b981' },
                warning: { main: '#f59e0b' },
                error: { main: '#ef4444' },
                info: { main: '#0284c7' },
              }),
        },
        typography: {
          fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          h4: {
            fontWeight: 800,
            letterSpacing: '-0.02em',
          },
          h5: {
            fontWeight: 700,
            letterSpacing: '-0.01em',
          },
          h6: {
            fontWeight: 700,
          },
        },
        shape: {
          borderRadius: 10,
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
                fontWeight: 600,
                borderRadius: 8,
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
              },
            },
          },
        },
      }),
    [themeMode]
  )

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="incidents" element={<Incidents />} />
              <Route path="incidents/:incidentId" element={<Incidents />} />
              <Route path="approvals" element={<Approvals />} />
              <Route path="audit" element={<Audit />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Routes>
        </BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: themeMode === 'dark' ? '#1e293b' : '#334155',
              color: '#fff',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              fontFamily: 'Inter, sans-serif',
            },
          }}
        />
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
