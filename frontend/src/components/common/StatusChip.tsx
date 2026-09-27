import React from 'react'
import { Chip, Box } from '@mui/material'
import type { IncidentStatus, IncidentSeverity, ApprovalStatus } from '../../types'

interface StatusChipProps {
  status: IncidentStatus | IncidentSeverity | ApprovalStatus | string
  type?: 'status' | 'severity' | 'approval'
}

const statusConfig: Record<string, { bg: string; color: string; dot: string }> = {
  // Incident Status
  CREATED: { bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', dot: '#38bdf8' },
  EVIDENCE_COLLECTED: { bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', dot: '#38bdf8' },
  DIAGNOSIS_COMPLETE: { bg: 'rgba(168, 85, 247, 0.12)', color: '#a855f7', dot: '#a855f7' },
  RISK_ASSESSED: { bg: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', dot: '#f59e0b' },
  APPROVED: { bg: 'rgba(16, 185, 129, 0.12)', color: '#10b981', dot: '#10b981' },
  EXECUTING: { bg: 'rgba(6, 182, 212, 0.15)', color: '#06b6d4', dot: '#06b6d4' },
  RECOVERY_VERIFIED: { bg: 'rgba(16, 185, 129, 0.15)', color: '#10b981', dot: '#10b981' },
  RESOLVED: { bg: 'rgba(16, 185, 129, 0.15)', color: '#10b981', dot: '#10b981' },
  RECOVERY_FAILED: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', dot: '#ef4444' },
  VERIFICATION_ERROR: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', dot: '#ef4444' },
  REMEDIATION_REJECTED: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', dot: '#ef4444' },
  TIMEOUT_EXCEEDED: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', dot: '#ef4444' },
  DIAGNOSIS_FAILED: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', dot: '#ef4444' },
  DIAGNOSIS_TIMEOUT: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', dot: '#ef4444' },

  // Severity
  LOW: { bg: 'rgba(16, 185, 129, 0.12)', color: '#10b981', dot: '#10b981' },
  MEDIUM: { bg: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', dot: '#f59e0b' },
  HIGH: { bg: 'rgba(249, 115, 22, 0.15)', color: '#f97316', dot: '#f97316' },
  CRITICAL: { bg: 'rgba(239, 68, 68, 0.18)', color: '#ef4444', dot: '#ef4444' },

  // Approval Status
  PENDING: { bg: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', dot: '#f59e0b' },
  REJECTED: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', dot: '#ef4444' },
  TIMEOUT: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', dot: '#ef4444' },
}

export default function StatusChip({ status, type = 'status' }: StatusChipProps) {
  const cfg = statusConfig[status] || {
    bg: 'rgba(148, 163, 184, 0.12)',
    color: '#94a3b8',
    dot: '#94a3b8',
  }

  const labelText = status.replace(/_/g, ' ')

  return (
    <Chip
      size="small"
      icon={
        <Box
          sx={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            backgroundColor: cfg.dot,
            ml: '8px !important',
            mr: '-4px !important',
            boxShadow: `0 0 8px ${cfg.dot}`,
          }}
        />
      }
      label={labelText}
      sx={{
        backgroundColor: cfg.bg,
        color: cfg.color,
        fontWeight: 700,
        fontSize: '0.74rem',
        textTransform: 'capitalize',
        border: `1px solid ${cfg.color}33`,
        borderRadius: 1.5,
        '& .MuiChip-label': {
          px: 1,
        },
      }}
    />
  )
}
