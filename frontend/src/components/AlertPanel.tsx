import React from 'react'
import { dismissAlert } from '@/hooks/useGitHubData'
import type { Alert } from '@/types'

interface AlertPanelProps {
  alerts: Alert[]
}

export const AlertPanel: React.FC<AlertPanelProps> = ({ alerts }) => {
  const activeAlerts = alerts.filter(a => !a.dismissed)

  if (activeAlerts.length === 0) {
    return null
  }

  const handleDismiss = async (alertId: string) => {
    try {
      await dismissAlert(alertId)
    } catch (error) {
      console.error('Failed to dismiss alert:', error)
    }
  }

  const getAlertStyles = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: '🔴',
          iconBg: 'bg-red-100',
          iconColor: 'text-red-600',
          textColor: 'text-red-800',
        }
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: '❌',
          iconBg: 'bg-red-100',
          iconColor: 'text-red-600',
          textColor: 'text-red-800',
        }
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: '⚠️',
          iconBg: 'bg-yellow-100',
          iconColor: 'text-yellow-600',
          textColor: 'text-yellow-800',
        }
      case 'info':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          icon: 'ℹ️',
          iconBg: 'bg-blue-100',
          iconColor: 'text-blue-600',
          textColor: 'text-blue-800',
        }
    }
  }

  return (
    <div className="space-y-3">
      {activeAlerts.map((alert) => {
        const styles = getAlertStyles(alert.severity)
        return (
          <div
            key={alert.id}
            className={`${styles.bg} ${styles.border} border rounded-lg p-4 flex items-start gap-3`}
          >
            <div className={`${styles.iconBg} rounded-full p-2 flex-shrink-0`}>
              <span className="text-xl">{styles.icon}</span>
            </div>
            <div className="flex-grow">
              <h4 className={`font-semibold ${styles.textColor} mb-1`}>{alert.title}</h4>
              <p className={`text-sm ${styles.textColor}`}>{alert.message}</p>
              <p className="text-xs text-gray-500 mt-2">
                {new Date(alert.timestamp).toLocaleString()}
              </p>
            </div>
            <button
              onClick={() => handleDismiss(alert.id)}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Dismiss alert"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )
      })}
    </div>
  )
}
