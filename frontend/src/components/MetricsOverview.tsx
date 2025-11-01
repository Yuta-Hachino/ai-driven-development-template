import React from 'react'
import type { SystemMetrics } from '@/types'

interface MetricsOverviewProps {
  metrics: SystemMetrics
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({ metrics }) => {
  const cards = [
    {
      title: 'Active Instances',
      value: metrics.active_instances,
      icon: '🤖',
      color: 'blue',
      trend: null,
    },
    {
      title: 'Completion Rate',
      value: `${metrics.completion_rate.toFixed(1)}%`,
      icon: '📈',
      color: 'green',
      trend: metrics.completion_rate >= 80 ? 'up' : metrics.completion_rate >= 50 ? 'neutral' : 'down',
    },
    {
      title: 'Velocity',
      value: `${metrics.velocity.toFixed(1)} tasks/hr`,
      icon: '⚡',
      color: 'yellow',
      trend: metrics.velocity >= 2 ? 'up' : 'neutral',
    },
    {
      title: 'Bottlenecks',
      value: metrics.bottlenecks,
      icon: '⚠️',
      color: metrics.bottlenecks > 0 ? 'red' : 'gray',
      trend: metrics.bottlenecks === 0 ? 'up' : 'down',
    },
  ]

  const taskStats = [
    { label: 'Pending', value: metrics.pending_tasks, color: 'bg-gray-400' },
    { label: 'In Progress', value: metrics.in_progress_tasks, color: 'bg-blue-500' },
    { label: 'Completed', value: metrics.completed_tasks, color: 'bg-green-500' },
    { label: 'Failed', value: metrics.failed_tasks, color: 'bg-red-500' },
  ]

  const total = taskStats.reduce((sum, stat) => sum + stat.value, 0)

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <div
            key={card.title}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
              <div className="text-3xl">{card.icon}</div>
            </div>
            {card.trend && (
              <div className="mt-2">
                <span className={`text-xs ${
                  card.trend === 'up' ? 'text-green-600' :
                  card.trend === 'down' ? 'text-red-600' :
                  'text-gray-600'
                }`}>
                  {card.trend === 'up' ? '↑ Good' : card.trend === 'down' ? '↓ Needs attention' : '→ Stable'}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Task Status Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Distribution</h3>

        {/* Progress Bar */}
        <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden mb-4">
          {taskStats.map((stat, index) => {
            const percentage = total > 0 ? (stat.value / total) * 100 : 0
            return percentage > 0 ? (
              <div
                key={stat.label}
                className={`absolute h-full ${stat.color}`}
                style={{
                  left: `${taskStats.slice(0, index).reduce((sum, s) => sum + (total > 0 ? (s.value / total) * 100 : 0), 0)}%`,
                  width: `${percentage}%`,
                }}
              ></div>
            ) : null
          })}
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {taskStats.map((stat) => (
            <div key={stat.label} className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${stat.color}`}></div>
              <div>
                <p className="text-xs text-gray-600">{stat.label}</p>
                <p className="text-sm font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
