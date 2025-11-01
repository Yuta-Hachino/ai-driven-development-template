import React, { useMemo } from 'react'
import type { Instance, P2PMessage } from '@/types'

interface P2PNetworkGraphProps {
  instances: Instance[]
  messages: P2PMessage[]
}

export const P2PNetworkGraph: React.FC<P2PNetworkGraphProps> = ({ instances, messages }) => {
  // Calculate network statistics
  const stats = useMemo(() => {
    const messagesByType = messages.reduce((acc, msg) => {
      acc[msg.type] = (acc[msg.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const messagesBySender = messages.reduce((acc, msg) => {
      acc[msg.sender_id] = (acc[msg.sender_id] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      totalMessages: messages.length,
      messagesByType,
      messagesBySender,
      activeInstances: instances.filter(i => i.status === 'active').length,
    }
  }, [instances, messages])

  // Get recent messages (last 20)
  const recentMessages = messages.slice(-20).reverse()

  const getMessageIcon = (type: P2PMessage['type']) => {
    switch (type) {
      case 'leader_election':
        return '👑'
      case 'node_announce':
        return '📣'
      case 'tasks_data':
        return '📦'
      case 'claim':
        return '🎯'
      case 'progress':
        return '📊'
      case 'heartbeat':
        return '💓'
      default:
        return '📨'
    }
  }

  return (
    <div className="space-y-6">
      {/* Network Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm text-gray-600 mb-1">Total Messages</div>
          <div className="text-2xl font-bold text-gray-900">{stats.totalMessages}</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm text-gray-600 mb-1">Active Instances</div>
          <div className="text-2xl font-bold text-gray-900">{stats.activeInstances}</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm text-gray-600 mb-1">Heartbeats</div>
          <div className="text-2xl font-bold text-gray-900">{stats.messagesByType.heartbeat || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-sm text-gray-600 mb-1">Task Claims</div>
          <div className="text-2xl font-bold text-gray-900">{stats.messagesByType.claim || 0}</div>
        </div>
      </div>

      {/* Network Visualization */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Network Topology</h3>

        {/* Simple SVG-based network diagram */}
        <div className="relative h-80 bg-gray-50 rounded-lg flex items-center justify-center">
          <svg className="w-full h-full" viewBox="0 0 800 320">
            {/* GitHub (Central hub) */}
            <circle cx="400" cy="160" r="40" fill="#4F46E5" />
            <text x="400" y="168" textAnchor="middle" fill="white" fontSize="24">📘</text>
            <text x="400" y="220" textAnchor="middle" fill="#374151" fontSize="14" fontWeight="600">
              GitHub (Coordinator)
            </text>

            {/* Instances arranged in circle */}
            {instances.map((instance, index) => {
              const angle = (index / instances.length) * 2 * Math.PI - Math.PI / 2
              const radius = 120
              const x = 400 + radius * Math.cos(angle)
              const y = 160 + radius * Math.sin(angle)

              const statusColor = instance.status === 'active' ? '#10B981' :
                                instance.status === 'paused' ? '#F59E0B' :
                                instance.status === 'failed' ? '#EF4444' : '#6B7280'

              return (
                <g key={instance.id}>
                  {/* Connection line to GitHub */}
                  <line
                    x1="400" y1="160"
                    x2={x} y2={y}
                    stroke="#E5E7EB"
                    strokeWidth="2"
                    strokeDasharray="4"
                  />

                  {/* Instance node */}
                  <circle cx={x} cy={y} r="30" fill={statusColor} />
                  <text x={x} y={y + 5} textAnchor="middle" fill="white" fontSize="18">🤖</text>

                  {/* Instance label */}
                  <text
                    x={x} y={y + 50}
                    textAnchor="middle"
                    fill="#374151"
                    fontSize="11"
                    fontWeight="500"
                  >
                    {instance.name}
                  </text>

                  {/* Workload indicator */}
                  <text
                    x={x} y={y + 65}
                    textAnchor="middle"
                    fill="#6B7280"
                    fontSize="10"
                  >
                    {instance.current_tasks.length}/{instance.max_concurrent_tasks} tasks
                  </text>
                </g>
              )
            })}
          </svg>
        </div>

        <div className="mt-4 flex items-center justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-600">Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-600">Paused</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-gray-600">Failed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
            <span className="text-gray-600">Completed</span>
          </div>
        </div>
      </div>

      {/* Message Types Distribution */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Message Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(stats.messagesByType).map(([type, count]) => (
            <div key={type} className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-3xl mb-2">{getMessageIcon(type as P2PMessage['type'])}</div>
              <div className="text-lg font-bold text-gray-900">{count}</div>
              <div className="text-xs text-gray-600 capitalize">{type.replace('_', ' ')}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Messages Log */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Messages</h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {recentMessages.map((message) => (
            <div
              key={message.id}
              className="flex items-start gap-3 p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
            >
              <span className="text-2xl flex-shrink-0">{getMessageIcon(message.type)}</span>
              <div className="flex-grow min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-gray-900 capitalize">
                    {message.type.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  From: <span className="font-mono text-xs">{message.sender_id}</span>
                </div>
                <div className="text-xs text-gray-500 font-mono mt-1 truncate">
                  {message.content.substring(0, 100)}
                  {message.content.length > 100 && '...'}
                </div>
              </div>
            </div>
          ))}

          {recentMessages.length === 0 && (
            <div className="text-center py-8 text-gray-400">
              No messages yet
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
