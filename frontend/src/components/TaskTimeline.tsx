import React from 'react'
import type { Task } from '@/types'

interface TaskTimelineProps {
  tasks: Task[]
  compact?: boolean
}

export const TaskTimeline: React.FC<TaskTimelineProps> = ({ tasks, compact = false }) => {
  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-400'
      case 'in_progress':
        return 'bg-blue-500'
      case 'completed':
        return 'bg-green-500'
      case 'failed':
        return 'bg-red-500'
      case 'blocked':
        return 'bg-orange-500'
    }
  }

  const getPriorityBadge = (priority: Task['priority']) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (compact) {
    const recentTasks = tasks.filter(t => t.status === 'in_progress' || t.status === 'completed').slice(0, 5)

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Tasks</h3>
        <div className="space-y-3">
          {recentTasks.map((task) => (
            <div key={task.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-md">
              <div className={`w-3 h-3 rounded-full flex-shrink-0 ${getStatusColor(task.status)}`}></div>
              <div className="flex-grow min-w-0">
                <p className="font-medium text-gray-900 truncate">{task.title}</p>
                <p className="text-xs text-gray-600">
                  {task.assigned_to || 'Unassigned'} • {task.progress_percentage}%
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Group tasks by status
  const groupedTasks = {
    pending: tasks.filter(t => t.status === 'pending'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    blocked: tasks.filter(t => t.status === 'blocked'),
    completed: tasks.filter(t => t.status === 'completed'),
    failed: tasks.filter(t => t.status === 'failed'),
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {Object.entries(groupedTasks).map(([status, statusTasks]) => (
        <div key={status} className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
          {/* Column Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 capitalize">
                {status.replace('_', ' ')}
              </h3>
              <span className={`w-6 h-6 rounded-full ${getStatusColor(status as Task['status'])} flex items-center justify-center text-white text-xs font-bold`}>
                {statusTasks.length}
              </span>
            </div>
          </div>

          {/* Task Cards */}
          <div className="p-3 space-y-3 flex-grow overflow-y-auto max-h-[600px]">
            {statusTasks.map((task) => (
              <div
                key={task.id}
                className="bg-gray-50 rounded-md border border-gray-200 p-3 hover:shadow-md transition-shadow cursor-pointer"
              >
                {/* Priority Badge */}
                <div className="flex items-start justify-between mb-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityBadge(task.priority)}`}>
                    {task.priority}
                  </span>
                  {task.dependencies.length > 0 && (
                    <span className="text-xs text-gray-500" title={`Depends on ${task.dependencies.length} tasks`}>
                      🔗 {task.dependencies.length}
                    </span>
                  )}
                </div>

                {/* Task Title */}
                <h4 className="font-medium text-gray-900 text-sm mb-2 line-clamp-2">
                  {task.title}
                </h4>

                {/* Task Info */}
                <div className="space-y-2">
                  {/* Progress Bar */}
                  {task.status === 'in_progress' && (
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-gray-600">Progress</span>
                        <span className="font-medium">{task.progress_percentage}%</span>
                      </div>
                      <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 transition-all"
                          style={{ width: `${task.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {/* Assigned To */}
                  {task.assigned_to && (
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <span className="truncate">{task.assigned_to}</span>
                    </div>
                  )}

                  {/* Time Estimate */}
                  <div className="flex items-center gap-2 text-xs text-gray-600">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{task.estimated_hours}h est.</span>
                    {task.actual_hours && <span className="text-gray-400">/ {task.actual_hours}h actual</span>}
                  </div>

                  {/* Skills Required */}
                  {task.required_skills.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {task.required_skills.slice(0, 2).map((skill) => (
                        <span
                          key={skill}
                          className="px-1.5 py-0.5 bg-blue-50 text-blue-700 text-xs rounded border border-blue-200"
                        >
                          {skill}
                        </span>
                      ))}
                      {task.required_skills.length > 2 && (
                        <span className="px-1.5 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                          +{task.required_skills.length - 2}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Timestamps */}
                  <div className="text-xs text-gray-500 pt-2 border-t border-gray-200">
                    {task.completed_at ? (
                      <span>Completed {new Date(task.completed_at).toLocaleDateString()}</span>
                    ) : task.started_at ? (
                      <span>Started {new Date(task.started_at).toLocaleDateString()}</span>
                    ) : (
                      <span>Created {new Date(task.created_at).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {statusTasks.length === 0 && (
              <div className="text-center py-8 text-gray-400 text-sm">
                No {status.replace('_', ' ')} tasks
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
