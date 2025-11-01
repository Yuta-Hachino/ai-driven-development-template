import React, { useState } from 'react'
import { pauseInstance, resumeInstance, updateInstanceResources } from '@/hooks/useGitHubData'
import type { Instance } from '@/types'

interface InstanceGridProps {
  instances: Instance[]
  compact?: boolean
}

export const InstanceGrid: React.FC<InstanceGridProps> = ({ instances, compact = false }) => {
  const [expandedInstance, setExpandedInstance] = useState<string | null>(null)

  const getStatusColor = (status: Instance['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
    }
  }

  const handlePause = async (instanceId: string) => {
    try {
      await pauseInstance(instanceId)
    } catch (error) {
      console.error('Failed to pause instance:', error)
    }
  }

  const handleResume = async (instanceId: string) => {
    try {
      await resumeInstance(instanceId)
    } catch (error) {
      console.error('Failed to resume instance:', error)
    }
  }

  const handleResourceChange = async (instanceId: string, value: number) => {
    try {
      await updateInstanceResources(instanceId, value)
    } catch (error) {
      console.error('Failed to update resources:', error)
    }
  }

  if (compact) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Instances</h3>
        <div className="space-y-3">
          {instances.slice(0, 5).map((instance) => (
            <div key={instance.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
              <div className="flex items-center gap-3">
                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(instance.status)}`}>
                  {instance.status}
                </div>
                <span className="font-medium text-gray-900">{instance.name}</span>
              </div>
              <div className="text-sm text-gray-600">
                {instance.current_tasks.length}/{instance.max_concurrent_tasks} tasks
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {instances.map((instance) => {
        const isExpanded = expandedInstance === instance.id
        const workloadPercentage = (instance.current_tasks.length / instance.max_concurrent_tasks) * 100

        return (
          <div
            key={instance.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
          >
            {/* Instance Header */}
            <div
              className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => setExpandedInstance(isExpanded ? null : instance.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-grow">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{instance.name}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(instance.status)}`}>
                      {instance.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">ID: {instance.id}</p>

                  {/* Workload Bar */}
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Workload</span>
                      <span className="font-medium text-gray-900">
                        {instance.current_tasks.length}/{instance.max_concurrent_tasks}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          workloadPercentage >= 90 ? 'bg-red-500' :
                          workloadPercentage >= 70 ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`}
                        style={{ width: `${Math.min(workloadPercentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                    <div>
                      <p className="text-xs text-gray-600">Quality Score</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {(instance.stats.quality_score * 100).toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Avg Time</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {instance.stats.avg_completion_time.toFixed(1)}h
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Completed</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {instance.stats.tasks_completed}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Velocity</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {instance.stats.recent_velocity.toFixed(1)}/hr
                      </p>
                    </div>
                  </div>
                </div>

                {/* Expand Icon */}
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            {/* Expanded Controls */}
            {isExpanded && (
              <div className="border-t border-gray-200 p-6 bg-gray-50">
                <h4 className="font-semibold text-gray-900 mb-4">Instance Controls</h4>

                <div className="space-y-4">
                  {/* Control Buttons */}
                  <div className="flex gap-2">
                    {instance.status === 'active' ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handlePause(instance.id)
                        }}
                        className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors"
                      >
                        Pause Instance
                      </button>
                    ) : instance.status === 'paused' ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleResume(instance.id)
                        }}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                      >
                        Resume Instance
                      </button>
                    ) : null}
                  </div>

                  {/* Resource Slider */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-2">
                      Max Concurrent Tasks: {instance.max_concurrent_tasks}
                    </label>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={instance.max_concurrent_tasks}
                      onChange={(e) => handleResourceChange(instance.id, parseInt(e.target.value))}
                      onClick={(e) => e.stopPropagation()}
                      className="w-full"
                    />
                  </div>

                  {/* Current Tasks */}
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Current Tasks</h5>
                    {instance.current_tasks.length > 0 ? (
                      <ul className="space-y-2">
                        {instance.current_tasks.map((task) => (
                          <li key={task.id} className="text-sm text-gray-600 bg-white p-2 rounded border border-gray-200">
                            {task.title} ({task.progress_percentage}%)
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No current tasks</p>
                    )}
                  </div>

                  {/* Metadata */}
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                    <div>
                      <p className="text-xs text-gray-600">Started</p>
                      <p className="text-sm text-gray-900">
                        {new Date(instance.started_at).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Last Heartbeat</p>
                      <p className="text-sm text-gray-900">
                        {new Date(instance.last_heartbeat).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
