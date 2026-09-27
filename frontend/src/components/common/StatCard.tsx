import React from 'react'
import { Card, CardContent, Typography, Box } from '@mui/material'
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  trend?: 'up' | 'down' | 'flat'
  trendValue?: string
  icon?: React.ReactNode
  color?: string
  gradient?: string
}

export default function StatCard({
  title,
  value,
  subtitle,
  trend,
  trendValue,
  icon,
  color = '#06b6d4',
  gradient,
}: StatCardProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp sx={{ color: 'success.main', fontSize: 18 }} />
      case 'down':
        return <TrendingDown sx={{ color: 'error.main', fontSize: 18 }} />
      case 'flat':
        return <TrendingFlat sx={{ color: 'text.secondary', fontSize: 18 }} />
      default:
        return null
    }
  }

  return (
    <Card
      sx={{
        height: '100%',
        borderRadius: 2.5,
        border: '1px solid',
        borderColor: 'divider',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.25s ease-in-out',
        background: gradient || 'background.paper',
        '&:hover': {
          transform: 'translateY(-3px)',
          boxShadow: '0 10px 25px -8px rgba(0,0,0,0.3)',
          borderColor: color,
        },
      }}
    >
      <CardContent sx={{ p: 2.8, '&:last-child': { pb: 2.8 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
          <Typography color="text.secondary" variant="body2" fontWeight="600">
            {title}
          </Typography>
          {icon && (
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                backgroundColor: `${color}18`,
                color: color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {icon}
            </Box>
          )}
        </Box>

        <Typography variant="h3" component="div" fontWeight="800" sx={{ mb: 1, letterSpacing: '-0.03em' }}>
          {value}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
          {trend && getTrendIcon()}
          {trendValue && (
            <Typography
              variant="caption"
              fontWeight="700"
              sx={{
                color:
                  trend === 'up' ? 'success.main' : trend === 'down' ? 'error.main' : 'text.secondary',
              }}
            >
              {trendValue}
            </Typography>
          )}
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  )
}
