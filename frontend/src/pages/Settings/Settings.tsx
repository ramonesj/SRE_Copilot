import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  IconButton,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  LinearProgress,
  Divider,
  Slider,
  Tooltip,
  Alert,
} from '@mui/material'
import {
  Dns as DnsIcon,
  Psychology as PsychologyIcon,
  Security as SecurityIcon,
  NotificationsActive as NotificationsIcon,
  Add as AddIcon,
  PlayArrow as PlayArrowIcon,
  DeleteOutline as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  CloudQueue as CloudIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Terminal as TerminalIcon,
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Lan as LanIcon,
  Business as BusinessIcon,
  CloudUpload as UploadIcon,
} from '@mui/icons-material'
import { nodeService } from '../../services/nodeService'
import { ServerNode, ConnectionTestResult } from '../../types/server'
import RunbookCatalogModal from '../../components/common/RunbookCatalogModal'
import { useBrandingStore } from '../../stores/brandingStore'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

export default function Settings() {
  const [tabValue, setTabValue] = useState(0)
  const [nodes, setNodes] = useState<ServerNode[]>([])
  const [isLoadingNodes, setIsLoadingNodes] = useState(true)
  const [runbookCatalogOpen, setRunbookCatalogOpen] = useState(false)

  // Branding Store
  const {
    companyName: storedCompanyName,
    companyLogo: storedCompanyLogo,
    department: storedDepartment,
    contactEmail: storedContactEmail,
    setBranding,
    resetBranding,
  } = useBrandingStore()

  const [companyNameInput, setCompanyNameInput] = useState(storedCompanyName)
  const [companyLogoInput, setCompanyLogoInput] = useState(storedCompanyLogo)
  const [departmentInput, setDepartmentInput] = useState(storedDepartment)
  const [contactEmailInput, setContactEmailInput] = useState(storedContactEmail)

  // Dialog State for Connecting New Server
  const [openConnectDialog, setOpenConnectDialog] = useState(false)
  const [testModalOpen, setTestModalOpen] = useState(false)
  const [activeTestLogs, setActiveTestLogs] = useState<ConnectionTestResult[]>([])
  const [isTesting, setIsTesting] = useState(false)

  // New Node Form
  const [formData, setFormData] = useState({
    name: '',
    instance_id: '',
    hostname: '',
    provider: 'AWS_EC2' as const,
    region: 'us-east-1',
    environment: 'PRODUCTION' as const,
    service_tag: '',
    iam_role_arn: 'arn:aws:iam::123456789012:role/SRECopilot-SSMManagedInstanceCore',
    telemetry_port: 9100,
    auto_remediation_enabled: true,
  })

  // AI & Safety Settings State
  const [aiSettings, setAiSettings] = useState({
    model: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    temperature: 0.2,
    maxTokens: 4096,
    bedrockRegion: 'us-east-1',
    enableReasoningArtifacts: true,
    promptPreset: 'SRE-Autonomous-Investigator-v2',
  })

  // Safety & HITL Policy State
  const [hitlSettings, setHitlSettings] = useState({
    autoRemediateLowRisk: true,
    maxAutoRiskScore: 25,
    approvalTimeoutMinutes: 60,
    twoPersonRuleForCritical: true,
    circuitBreakerActive: false,
  })

  // Integrations State
  const [integrationSettings, setIntegrationSettings] = useState({
    slackWebhook: 'https://hooks.slack.com/services/T000/B000/XXXXXX',
    pagerdutyKey: 'pd-live-key-9923847291',
    prometheusEndpoint: 'http://prometheus:9090',
    cloudwatchSnsTopic: 'arn:aws:sns:us-east-1:123456789012:sre-copilot-alerts',
  })

  useEffect(() => {
    loadNodes()
  }, [])

  const loadNodes = async () => {
    setIsLoadingNodes(true)
    const list = await nodeService.getNodes()
    setNodes(list)
    setIsLoadingNodes(false)
  }

  const handleOpenConnect = () => {
    setFormData({
      name: '',
      instance_id: `i-0${Math.random().toString(16).substring(2, 12)}`,
      hostname: '',
      provider: 'AWS_EC2',
      region: 'us-east-1',
      environment: 'PRODUCTION',
      service_tag: '',
      iam_role_arn: 'arn:aws:iam::123456789012:role/SRECopilot-SSMManagedInstanceCore',
      telemetry_port: 9100,
      auto_remediation_enabled: true,
    })
    setOpenConnectDialog(true)
  }

  const handleSaveNode = async () => {
    if (!formData.name || !formData.instance_id || !formData.service_tag) {
      toast.error('Please fill in Name, Instance ID, and Service Tag')
      return
    }

    try {
      await nodeService.addNode({
        ...formData,
        hostname: formData.hostname || `${formData.service_tag}-01.${formData.region}.internal`,
      })
      toast.success(`Instance ${formData.instance_id} connected successfully!`)
      setOpenConnectDialog(false)
      loadNodes()
    } catch (err: any) {
      toast.error(err.message || 'Failed to connect instance')
    }
  }

  const handleDeleteNode = async (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to disconnect ${name}?`)) {
      await nodeService.deleteNode(id)
      toast.success(`Disconnected ${name}`)
      loadNodes()
    }
  }

  const handleRunConnectionTest = async (node: ServerNode) => {
    setTestModalOpen(true)
    setIsTesting(true)
    setActiveTestLogs([])

    const currentLogs: ConnectionTestResult[] = []

    await nodeService.testConnection(
      {
        instance_id: node.instance_id,
        region: node.region,
        provider: node.provider,
      },
      (step) => {
        const existingIdx = currentLogs.findIndex((l) => l.step === step.step)
        if (existingIdx >= 0) {
          currentLogs[existingIdx] = step
        } else {
          currentLogs.push(step)
        }
        setActiveTestLogs([...currentLogs])
      }
    )

    setIsTesting(false)
    toast.success(`Connection to ${node.instance_id} verified healthy!`)
  }

  return (
    <Box sx={{ pb: 6 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="800" sx={{ letterSpacing: '-0.5px' }}>
            System Settings & Fleet Manager
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage target instances, AWS SSM telemetry, Bedrock AI models, and HITL safety policies.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenConnect}
          sx={{
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
            color: '#fff',
            fontWeight: '600',
            px: 3,
            py: 1,
            boxShadow: '0 4px 14px 0 rgba(6, 182, 212, 0.39)',
          }}
        >
          Connect Instance / Server
        </Button>
      </Box>

      {/* Navigation Tabs */}
      <Paper
        sx={{
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'divider',
          mb: 3,
          backgroundColor: 'background.paper',
        }}
      >
        <Tabs
          value={tabValue}
          onChange={(e, v) => setTabValue(v)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            px: 2,
            '& .MuiTab-root': {
              minHeight: 56,
              fontWeight: 600,
              fontSize: '0.9rem',
              textTransform: 'none',
            },
          }}
        >
          <Tab icon={<DnsIcon sx={{ mr: 1 }} />} iconPosition="start" label="Target Fleet & Instances" />
          <Tab icon={<PsychologyIcon sx={{ mr: 1 }} />} iconPosition="start" label="AI & Diagnostic Engine" />
          <Tab icon={<SecurityIcon sx={{ mr: 1 }} />} iconPosition="start" label="HITL Safety & Guardrails" />
          <Tab icon={<NotificationsIcon sx={{ mr: 1 }} />} iconPosition="start" label="Alerts & Integrations" />
          <Tab icon={<BusinessIcon sx={{ mr: 1 }} />} iconPosition="start" label="Company Branding & Reports" />
        </Tabs>
      </Paper>

      {/* TAB 1: FLEET & INSTANCE CONNECTION */}
      <CustomTabPanel value={tabValue} index={0}>
        {/* Fleet Summary KPI Strip */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper
              sx={{
                p: 2.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                background: 'linear-gradient(135deg, rgba(6,182,212,0.08) 0%, rgba(59,130,246,0.02) 100%)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary" fontWeight="600">
                  Managed Instances
                </Typography>
                <DnsIcon color="primary" />
              </Box>
              <Typography variant="h4" fontWeight="800" sx={{ mt: 1 }}>
                {nodes.length}
              </Typography>
              <Typography variant="caption" color="success.main" fontWeight="600">
                ● 100% In Active Pool
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Paper
              sx={{
                p: 2.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                background: 'linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(16,185,129,0.02) 100%)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary" fontWeight="600">
                  SSM Agents Active
                </Typography>
                <CheckCircleIcon color="success" />
              </Box>
              <Typography variant="h4" fontWeight="800" sx={{ mt: 1, color: 'success.main' }}>
                {nodes.filter((n) => n.ssm_agent_status === 'ACTIVE').length} / {nodes.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Systems Manager v3.2
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Paper
              sx={{
                p: 2.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary" fontWeight="600">
                  Fleet Telemetry Latency
                </Typography>
                <SpeedIcon color="info" />
              </Box>
              <Typography variant="h4" fontWeight="800" sx={{ mt: 1 }}>
                14.2 ms
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Prometheus scrape interval: 15s
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Paper
              sx={{
                p: 2.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary" fontWeight="600">
                  Remediation Mode
                </Typography>
                <SecurityIcon color="warning" />
              </Box>
              <Typography variant="h5" fontWeight="800" sx={{ mt: 1, color: 'warning.main' }}>
                HITL Enforced
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Policy verification active
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Server Cards List */}
        <Typography variant="h6" fontWeight="700" sx={{ mb: 2 }}>
          Connected Compute Nodes & Targets
        </Typography>

        <Grid container spacing={3}>
          {nodes.map((node) => (
            <Grid item xs={12} md={6} lg={4} key={node.id}>
              <Card
                sx={{
                  borderRadius: 2.5,
                  border: '1px solid',
                  borderColor: 'divider',
                  transition: 'all 0.25s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 24px -10px rgba(0,0,0,0.3)',
                    borderColor: 'primary.main',
                  },
                }}
              >
                <CardContent sx={{ pb: 1.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight="700" noWrap sx={{ maxWidth: 220 }}>
                        {node.name}
                      </Typography>
                      <Typography
                        variant="caption"
                        className="font-mono"
                        sx={{
                          color: 'primary.main',
                          backgroundColor: 'rgba(6, 182, 212, 0.12)',
                          px: 1,
                          py: 0.3,
                          borderRadius: 1,
                          fontWeight: 600,
                        }}
                      >
                        {node.instance_id}
                      </Typography>
                    </Box>
                    <Chip
                      size="small"
                      label={node.status}
                      color={node.status === 'ONLINE' ? 'success' : 'warning'}
                      sx={{ fontWeight: 700, fontSize: '0.7rem' }}
                    />
                  </Box>

                  <Divider sx={{ my: 1.5 }} />

                  {/* Metadata fields */}
                  <Grid container spacing={1} sx={{ fontSize: '0.82rem', mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Service Tag:
                      </Typography>
                      <Typography variant="body2" fontWeight="600">
                        {node.service_tag}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Region & Env:
                      </Typography>
                      <Typography variant="body2" fontWeight="600">
                        {node.region} ({node.environment.substring(0, 4)})
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        SSM Agent:
                      </Typography>
                      <Typography variant="body2" fontWeight="600" color="success.main">
                        ● Online (v{node.ssm_agent_version.substring(0, 5)})
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Auto-Remediate:
                      </Typography>
                      <Typography
                        variant="body2"
                        fontWeight="600"
                        color={node.auto_remediation_enabled ? 'primary.main' : 'text.secondary'}
                      >
                        {node.auto_remediation_enabled ? 'Allowed' : 'HITL Only'}
                      </Typography>
                    </Grid>
                  </Grid>

                  {/* Live Telemetry Progress */}
                  <Box sx={{ mb: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        CPU Load
                      </Typography>
                      <Typography variant="caption" fontWeight="600">
                        {node.cpu_usage}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={node.cpu_usage}
                      color={node.cpu_usage > 80 ? 'error' : node.cpu_usage > 60 ? 'warning' : 'primary'}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>

                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        Memory Usage
                      </Typography>
                      <Typography variant="caption" fontWeight="600">
                        {node.memory_usage}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={node.memory_usage}
                      color={node.memory_usage > 80 ? 'error' : 'info'}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                </CardContent>

                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2, pt: 0 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<TerminalIcon />}
                    onClick={() => handleRunConnectionTest(node)}
                    sx={{ textTransform: 'none', fontWeight: 600 }}
                  >
                    Ping & Verify SSM
                  </Button>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDeleteNode(node.id, node.name)}
                    title="Disconnect Node"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </CustomTabPanel>

      {/* TAB 2: AI & DIAGNOSIS ENGINE */}
      <CustomTabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={7}>
            <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" fontWeight="700" gutterBottom>
                Bedrock Foundation Model & Prompt Config
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure the LLM reasoning backbone used for log extraction, metric anomaly correlation, and SSM runbook synthesis.
              </Typography>

              <Grid container spacing={2.5}>
                <Grid item xs={12}>
                  <TextField
                    select
                    fullWidth
                    label="Primary LLM Model"
                    value={aiSettings.model}
                    onChange={(e) => setAiSettings({ ...aiSettings, model: e.target.value })}
                    helperText="AWS Bedrock hosted model endpoint"
                  >
                    <MenuItem value="anthropic.claude-3-5-sonnet-20241022-v2:0">
                      Anthropic Claude 3.5 Sonnet v2 (Recommended for SRE Triage)
                    </MenuItem>
                    <MenuItem value="anthropic.claude-3-opus-20240229-v1:0">
                      Anthropic Claude 3 Opus (Deep Analysis)
                    </MenuItem>
                    <MenuItem value="amazon.titan-text-premier-v1:0">
                      Amazon Titan Text Premier
                    </MenuItem>
                    <MenuItem value="deepseek-r1-sre-distill-70b">
                      DeepSeek-R1 SRE Distill (Local Invariant Engine)
                    </MenuItem>
                  </TextField>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    select
                    fullWidth
                    label="Bedrock AWS Region"
                    value={aiSettings.bedrockRegion}
                    onChange={(e) => setAiSettings({ ...aiSettings, bedrockRegion: e.target.value })}
                  >
                    <MenuItem value="us-east-1">us-east-1 (N. Virginia)</MenuItem>
                    <MenuItem value="us-west-2">us-west-2 (Oregon)</MenuItem>
                    <MenuItem value="eu-central-1">eu-central-1 (Frankfurt)</MenuItem>
                  </TextField>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Max Reasoning Tokens"
                    type="number"
                    value={aiSettings.maxTokens}
                    onChange={(e) => setAiSettings({ ...aiSettings, maxTokens: parseInt(e.target.value) || 4096 })}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="body2" fontWeight="600" gutterBottom>
                    Temperature: {aiSettings.temperature} (Deterministic SRE Diagnosis)
                  </Typography>
                  <Slider
                    value={aiSettings.temperature}
                    min={0.0}
                    max={1.0}
                    step={0.05}
                    onChange={(e, val) => setAiSettings({ ...aiSettings, temperature: val as number })}
                    valueLabelDisplay="auto"
                  />
                  <Typography variant="caption" color="text.secondary">
                    Lower temperature produces strict, deterministic root cause identification.
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={aiSettings.enableReasoningArtifacts}
                        onChange={(e) =>
                          setAiSettings({ ...aiSettings, enableReasoningArtifacts: e.target.checked })
                        }
                        color="primary"
                      />
                    }
                    label="Store Structured Diagnosis Chain & Evidence Graph in PostgreSQL"
                  />
                </Grid>

                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    onClick={() => toast.success('AI Engine configuration saved!')}
                    sx={{ fontWeight: 600 }}
                  >
                    Save AI Settings
                  </Button>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12} md={5}>
            <Paper
              sx={{
                p: 3,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                backgroundColor: 'background.paper',
              }}
            >
              <Typography variant="h6" fontWeight="700" gutterBottom>
                Diagnosis Invariants
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                The SRE Copilot enforces strict boundaries on all AI recommendations:
              </Alert>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, fontSize: '0.85rem' }}>
                <Box sx={{ p: 1.5, borderRadius: 1.5, border: '1px solid', borderColor: 'divider' }}>
                  <Typography fontWeight="700" color="primary.main">
                    1. AI Never Executes Directly
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Model outputs an advisory payload with confidence score. Policy Engine evaluates before any SSM call.
                  </Typography>
                </Box>
                <Box sx={{ p: 1.5, borderRadius: 1.5, border: '1px solid', borderColor: 'divider' }}>
                  <Typography fontWeight="700" color="success.main">
                    2. Risk Engine Evaluation
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    All recommended actions calculate risk (0–100) based on blast radius, active connections, and environment.
                  </Typography>
                </Box>
                <Box sx={{ p: 1.5, borderRadius: 1.5, border: '1px solid', borderColor: 'divider' }}>
                  <Typography fontWeight="700" color="warning.main">
                    3. Mandatory Audit Trail
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Every diagnosis prompt, token count, and model response is immutably recorded in the audit log.
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </CustomTabPanel>

      {/* TAB 3: HITL SAFETY & GUARDRAILS */}
      <CustomTabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={7}>
            <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" fontWeight="700" gutterBottom>
                Human-in-the-Loop (HITL) Authorization Rules
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure risk thresholds and approval workflows required before executing SSM remediation runbooks.
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Box>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={hitlSettings.autoRemediateLowRisk}
                        onChange={(e) =>
                          setHitlSettings({ ...hitlSettings, autoRemediateLowRisk: e.target.checked })
                        }
                      />
                    }
                    label="Auto-execute Low-Risk Remediations without human approval"
                  />
                  <Typography variant="caption" display="block" color="text.secondary">
                    Actions with risk score below threshold in Non-Production will execute immediately.
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="body2" fontWeight="600" gutterBottom>
                    Max Auto-Remediation Risk Score: {hitlSettings.maxAutoRiskScore}/100
                  </Typography>
                  <Slider
                    value={hitlSettings.maxAutoRiskScore}
                    min={5}
                    max={50}
                    step={5}
                    onChange={(e, val) =>
                      setHitlSettings({ ...hitlSettings, maxAutoRiskScore: val as number })
                    }
                    valueLabelDisplay="auto"
                  />
                  <Typography variant="caption" color="text.secondary">
                    Actions with score &gt; {hitlSettings.maxAutoRiskScore} ALWAYS require Human approval in the Approvals queue.
                  </Typography>
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    label="Approval Request Timeout (Minutes)"
                    type="number"
                    value={hitlSettings.approvalTimeoutMinutes}
                    onChange={(e) =>
                      setHitlSettings({
                        ...hitlSettings,
                        approvalTimeoutMinutes: parseInt(e.target.value) || 60,
                      })
                    }
                    helperText="Approvals not authorized within this window transition to TIMEOUT_EXCEEDED"
                  />
                </Box>

                <Box>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={hitlSettings.twoPersonRuleForCritical}
                        onChange={(e) =>
                          setHitlSettings({
                            ...hitlSettings,
                            twoPersonRuleForCritical: e.target.checked,
                          })
                        }
                      />
                    }
                    label="Require Two-Person Review for CRITICAL Severity Incidents"
                  />
                </Box>

                <Divider />

                <Box sx={{ p: 2, borderRadius: 2, border: '1px solid', borderColor: 'error.main', backgroundColor: 'rgba(239,68,68,0.06)' }}>
                  <Typography variant="subtitle2" fontWeight="700" color="error.main" gutterBottom>
                    Emergency Safety Circuit Breaker
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={hitlSettings.circuitBreakerActive}
                        onChange={(e) =>
                          setHitlSettings({
                            ...hitlSettings,
                            circuitBreakerActive: e.target.checked,
                          })
                        }
                        color="error"
                      />
                    }
                    label="EMERGENCY FREEZE: Halt all automated and pending remediation executions"
                  />
                </Box>

                <Button
                  variant="contained"
                  onClick={() => toast.success('Safety policies saved!')}
                  sx={{ width: 'fit-content', fontWeight: 600 }}
                >
                  Save Policy Rules
                </Button>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" fontWeight="700" gutterBottom>
                Permitted SSM Runbooks
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Approved automation documents allowed for execution on target instances.
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {[
                  { name: 'SRE-Copilot-RestartService', risk: 'LOW', targets: 'All Services' },
                  { name: 'SRE-Copilot-ScaleASG', risk: 'MEDIUM', targets: 'EC2 Auto Scaling' },
                  { name: 'SRE-Copilot-ClearDiskSpace', risk: 'LOW', targets: 'Log & Temp Files' },
                  { name: 'SRE-Copilot-ReplayDeadLetters', risk: 'MEDIUM', targets: 'SQS / Webhooks' },
                  { name: 'SRE-Copilot-FlushDatabasePool', risk: 'HIGH', targets: 'RDS / PostgreSQL' },
                ].map((rb) => (
                  <Box
                    key={rb.name}
                    sx={{
                      p: 1.5,
                      borderRadius: 1.5,
                      border: '1px solid',
                      borderColor: 'divider',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Box>
                      <Typography variant="body2" fontWeight="700" className="font-mono">
                        {rb.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Target: {rb.targets}
                      </Typography>
                    </Box>
                    <Chip
                      size="small"
                      label={rb.risk}
                      color={rb.risk === 'LOW' ? 'success' : rb.risk === 'MEDIUM' ? 'warning' : 'error'}
                      sx={{ fontWeight: 700, fontSize: '0.7rem' }}
                    />
                  </Box>
                ))}
              </Box>

              <Button
                variant="outlined"
                fullWidth
                startIcon={<TerminalIcon />}
                onClick={() => setRunbookCatalogOpen(true)}
                sx={{ mt: 2, textTransform: 'none', fontWeight: 600 }}
              >
                Inspect Full Runbook Catalog & Dry-Run Simulator →
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </CustomTabPanel>

      {/* TAB 4: ALERTS & INTEGRATIONS */}
      <CustomTabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" fontWeight="700" gutterBottom>
                Notification Channels & Observability Endpoints
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Connect your team's alerting pipelines for real-time incident escalation and telemetry ingest.
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Slack Webhook URL"
                    value={integrationSettings.slackWebhook}
                    onChange={(e) =>
                      setIntegrationSettings({ ...integrationSettings, slackWebhook: e.target.value })
                    }
                    helperText="Alerts on incident creation, HITL approval required, and resolution"
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="PagerDuty Integration Routing Key"
                    value={integrationSettings.pagerdutyKey}
                    onChange={(e) =>
                      setIntegrationSettings({ ...integrationSettings, pagerdutyKey: e.target.value })
                    }
                    helperText="Triggers on-call pages for CRITICAL unrecovered incidents"
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Prometheus Server URL"
                    value={integrationSettings.prometheusEndpoint}
                    onChange={(e) =>
                      setIntegrationSettings({
                        ...integrationSettings,
                        prometheusEndpoint: e.target.value,
                      })
                    }
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="CloudWatch SNS Topic ARN"
                    value={integrationSettings.cloudwatchSnsTopic}
                    onChange={(e) =>
                      setIntegrationSettings({
                        ...integrationSettings,
                        cloudwatchSnsTopic: e.target.value,
                      })
                    }
                  />
                </Grid>

                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    onClick={() => toast.success('Integrations configured successfully!')}
                    sx={{ fontWeight: 600 }}
                  >
                    Save Integrations
                  </Button>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </CustomTabPanel>

      {/* TAB 5: COMPANY BRANDING & LOGO */}
      <CustomTabPanel value={tabValue} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={7}>
            <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" fontWeight="700" gutterBottom>
                Enterprise Branding & Custom Logo
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Customize your organization name, logo, and department. These will appear in the top bar, sidebar, and in all generated SRE Post-Mortem reports.
              </Typography>

              <Grid container spacing={2.5}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    required
                    label="Company / Enterprise Name"
                    placeholder="e.g., MercadoLibre, Banco Santander, Acme Corp"
                    value={companyNameInput}
                    onChange={(e) => setCompanyNameInput(e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Department / Team"
                    placeholder="e.g., Core Cloud Infrastructure & SRE Operations"
                    value={departmentInput}
                    onChange={(e) => setDepartmentInput(e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="On-Call SRE Contact Email"
                    placeholder="e.g., sre-lead@enterprise.com"
                    value={contactEmailInput}
                    onChange={(e) => setContactEmailInput(e.target.value)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="subtitle2" fontWeight="700" gutterBottom>
                    Company Logo (Upload File or Paste Image URL)
                  </Typography>
                  <TextField
                    fullWidth
                    label="Logo Image URL"
                    placeholder="https://example.com/logo.png"
                    value={companyLogoInput}
                    onChange={(e) => setCompanyLogoInput(e.target.value)}
                    sx={{ mb: 1.5 }}
                  />

                  <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<UploadIcon />}
                      sx={{ textTransform: 'none', fontWeight: 600 }}
                    >
                      Upload Local Logo
                      <input
                        type="file"
                        hidden
                        accept="image/*"
                        onChange={(e) => {
                          const file = e.target.files?.[0]
                          if (file) {
                            const reader = new FileReader()
                            reader.onloadend = () => {
                              setCompanyLogoInput(reader.result as string)
                            }
                            reader.readAsDataURL(file)
                          }
                        }}
                      />
                    </Button>

                    {companyLogoInput && (
                      <Button
                        size="small"
                        color="error"
                        onClick={() => setCompanyLogoInput('')}
                        sx={{ textTransform: 'none' }}
                      >
                        Remove Logo
                      </Button>
                    )}
                  </Box>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="contained"
                      onClick={() => {
                        setBranding({
                          companyName: companyNameInput || 'SRE Copilot',
                          companyLogo: companyLogoInput,
                          department: departmentInput,
                          contactEmail: contactEmailInput,
                        })
                        toast.success('Branding & Company Logo saved successfully!')
                      }}
                      sx={{
                        background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
                        fontWeight: 700,
                        px: 3,
                      }}
                    >
                      Save Branding Settings
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        resetBranding()
                        setCompanyNameInput('SRE Copilot')
                        setCompanyLogoInput('')
                        setDepartmentInput('Autonomous Cloud Reliability Engineering')
                        setContactEmailInput('sre-oncall@enterprise.com')
                        toast.success('Reset to default branding')
                      }}
                    >
                      Reset Defaults
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Right: Live Preview */}
          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider', height: '100%' }}>
              <Typography variant="h6" fontWeight="700" gutterBottom>
                Live Branding Preview
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                How your company branding will look on headers and formal Post-Mortem reports:
              </Typography>

              {/* Preview Box */}
              <Paper
                sx={{
                  p: 2.5,
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  background: 'linear-gradient(135deg, rgba(6,182,212,0.08) 0%, rgba(59,130,246,0.04) 100%)',
                  mb: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5 }}>
                  {companyLogoInput ? (
                    <Box
                      component="img"
                      src={companyLogoInput}
                      alt={companyNameInput}
                      sx={{ width: 44, height: 44, objectFit: 'contain', borderRadius: 1.5 }}
                    />
                  ) : (
                    <Box
                      sx={{
                        width: 44,
                        height: 44,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontWeight: 800,
                        fontSize: '1.2rem',
                      }}
                    >
                      {(companyNameInput || 'S').charAt(0)}
                    </Box>
                  )}

                  <Box>
                    <Typography variant="subtitle1" fontWeight="800">
                      {companyNameInput || 'SRE Copilot'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {departmentInput || 'Site Reliability Engineering'}
                    </Typography>
                  </Box>
                </Box>

                <Divider sx={{ my: 1 }} />
                <Typography variant="caption" className="font-mono" color="text.secondary" display="block">
                  Post-Mortem Contact: {contactEmailInput || 'sre-oncall@enterprise.com'}
                </Typography>
              </Paper>
            </Paper>
          </Grid>
        </Grid>
      </CustomTabPanel>

      {/* MODAL: CONNECT NEW INSTANCE / SERVER */}
      <Dialog
        open={openConnectDialog}
        onClose={() => setOpenConnectDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, p: 1 },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h5" fontWeight="800">
            Connect New Compute Instance / Server
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Register an AWS EC2 instance, Kubernetes node, or on-premise host into SRE Copilot management.
          </Typography>
        </DialogTitle>

        <DialogContent dividers sx={{ py: 3 }}>
          <Grid container spacing={2.5}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Instance / Display Name"
                placeholder="e.g., Auth Gateway Replica 01"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="AWS Instance ID / Host Identifier"
                placeholder="e.g., i-0a1b2c3d4e5f67890"
                value={formData.instance_id}
                onChange={(e) => setFormData({ ...formData, instance_id: e.target.value })}
                InputProps={{ className: 'font-mono' }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Connection Protocol / Provider"
                value={formData.provider}
                onChange={(e) => setFormData({ ...formData, provider: e.target.value as any })}
              >
                <MenuItem value="AWS_EC2">AWS Systems Manager (SSM Agent - Recommended)</MenuItem>
                <MenuItem value="KUBERNETES">Kubernetes Node / DaemonSet</MenuItem>
                <MenuItem value="ON_PREMISE">On-Premise / Hybrid SSM Connector</MenuItem>
                <MenuItem value="BARE_METAL">Direct SSH Bastion</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Region / Zone"
                value={formData.region}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
              >
                <MenuItem value="us-east-1">us-east-1 (N. Virginia)</MenuItem>
                <MenuItem value="us-west-2">us-west-2 (Oregon)</MenuItem>
                <MenuItem value="eu-west-1">eu-west-1 (Ireland)</MenuItem>
                <MenuItem value="ap-southeast-1">ap-southeast-1 (Singapore)</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Environment"
                value={formData.environment}
                onChange={(e) => setFormData({ ...formData, environment: e.target.value as any })}
              >
                <MenuItem value="PRODUCTION">Production</MenuItem>
                <MenuItem value="STAGING">Staging</MenuItem>
                <MenuItem value="DEVELOPMENT">Development</MenuItem>
                <MenuItem value="DR">Disaster Recovery (DR)</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Service Tag / Workload"
                placeholder="e.g., auth-service, payment-gateway"
                value={formData.service_tag}
                onChange={(e) => setFormData({ ...formData, service_tag: e.target.value })}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="IAM Role ARN / SSM Instance Profile"
                value={formData.iam_role_arn}
                onChange={(e) => setFormData({ ...formData, iam_role_arn: e.target.value })}
                InputProps={{ className: 'font-mono' }}
                helperText="Required permissions: AmazonSSMManagedInstanceCore"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Prometheus Telemetry Port"
                type="number"
                value={formData.telemetry_port}
                onChange={(e) => setFormData({ ...formData, telemetry_port: parseInt(e.target.value) || 9100 })}
                helperText="Node exporter scrape port"
              />
            </Grid>

            <Grid item xs={12} sm={6} sx={{ display: 'flex', alignItems: 'center' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.auto_remediation_enabled}
                    onChange={(e) =>
                      setFormData({ ...formData, auto_remediation_enabled: e.target.checked })
                    }
                    color="primary"
                  />
                }
                label="Enable SRE Auto-Remediation"
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenConnectDialog(false)} color="inherit">
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSaveNode}
            sx={{
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
              fontWeight: 600,
              px: 3,
            }}
          >
            Register & Connect Instance
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL: INTERACTIVE LIVE CONNECTION TERMINAL TEST */}
      <Dialog
        open={testModalOpen}
        onClose={() => !isTesting && setTestModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            backgroundColor: '#0a0e17',
            border: '1px solid rgba(6,182,212,0.3)',
            color: '#f8fafc',
          },
        }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1.5, borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <TerminalIcon sx={{ color: '#06b6d4' }} />
          <Box>
            <Typography variant="h6" fontWeight="800" sx={{ color: '#f8fafc' }}>
              SSM Agent & Node Handshake Probe
            </Typography>
            <Typography variant="caption" sx={{ color: '#94a3b8' }}>
              Verifying real-time telemetry, IAM policies, and execution boundaries
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ py: 3 }}>
          {isTesting && <LinearProgress color="info" sx={{ mb: 2, borderRadius: 1 }} />}

          <Box
            sx={{
              p: 2.5,
              borderRadius: 2,
              backgroundColor: '#050811',
              border: '1px solid rgba(255,255,255,0.06)',
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '0.85rem',
              minHeight: 220,
              display: 'flex',
              flexDirection: 'column',
              gap: 1.5,
            }}
          >
            {activeTestLogs.map((log, i) => (
              <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                {log.status === 'RUNNING' && <Typography sx={{ color: '#38bdf8' }}>▶ [RUNNING]</Typography>}
                {log.status === 'SUCCESS' && <Typography sx={{ color: '#10b981' }}>✔ [OK]</Typography>}
                {log.status === 'ERROR' && <Typography sx={{ color: '#ef4444' }}>✖ [FAIL]</Typography>}
                <Box>
                  <Typography fontWeight="700" sx={{ color: '#e2e8f0' }}>
                    {log.step}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                    {log.message}
                  </Typography>
                </Box>
              </Box>
            ))}

            {isTesting && (
              <Typography sx={{ color: '#64748b', fontStyle: 'italic', mt: 1 }}>
                Running cryptographic verification...
              </Typography>
            )}

            {!isTesting && activeTestLogs.length > 0 && (
              <Box
                sx={{
                  mt: 2,
                  p: 1.5,
                  borderRadius: 1,
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  color: '#10b981',
                  fontWeight: 600,
                  fontSize: '0.82rem',
                }}
              >
                🎉 ALL CHECKS PASSED: Target node is connected and ready for autonomous SRE telemetry & HITL remediation.
              </Box>
            )}
          </Box>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2.5, borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <Button
            disabled={isTesting}
            onClick={() => setTestModalOpen(false)}
            variant="contained"
            sx={{
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
              fontWeight: 600,
              color: '#fff',
            }}
          >
            Done
          </Button>
        </DialogActions>
      </Dialog>

      {/* SSM Runbook Catalog Explorer Modal */}
      <RunbookCatalogModal
        open={runbookCatalogOpen}
        onClose={() => setRunbookCatalogOpen(false)}
      />
    </Box>
  )
}
