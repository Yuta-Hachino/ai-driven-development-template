import React, { useState } from 'react'
import { useRealtimeUpdates } from '@/hooks/useRealtimeUpdates'
import { InstanceGrid } from './InstanceGrid'
import { TaskTimeline } from './TaskTimeline'
import { MetricsOverview } from './MetricsOverview'
import { AlertPanel } from './AlertPanel'
import { P2PNetworkGraph } from './P2PNetworkGraph'
import { KnowledgeBase } from './KnowledgeBase'

export const Dashboard: React.FC = () => {
  const { state, connected, error, reconnect } = useRealtimeUpdates()
  const [activeTab, setActiveTab] = useState<'overview' | 'instances' | 'tasks' | 'network' | 'knowledge'>('overview')

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mx-auto mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-center text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 text-center mb-6">{error}</p>
          <button
            onClick={reconnect}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            Reconnect
          </button>
        </div>
      </div>
    )
  }

  if (!state) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-600">Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Autonomous Development</h1>
              <p className="text-sm text-gray-500 mt-1">Real-time P2P Collaboration Dashboard</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-600">
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                {new Date(state.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'instances', label: 'Instances', icon: '🤖' },
              { id: 'tasks', label: 'Tasks', icon: '📋' },
              { id: 'network', label: 'P2P Network', icon: '🌐' },
              { id: 'knowledge', label: 'Knowledge Base', icon: '📚' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Alerts */}
        {state.alerts.length > 0 && (
          <div className="mb-6">
            <AlertPanel alerts={state.alerts} />
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <MetricsOverview metrics={state.metrics} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <InstanceGrid instances={state.instances} compact />
              <TaskTimeline tasks={state.tasks} compact />
            </div>
          </div>
        )}

        {activeTab === 'instances' && (
          <InstanceGrid instances={state.instances} />
        )}

        {activeTab === 'tasks' && (
          <TaskTimeline tasks={state.tasks} />
        )}

        {activeTab === 'network' && (
          <P2PNetworkGraph
            instances={state.instances}
            messages={state.messages}
          />
        )}

        {activeTab === 'knowledge' && (
          <KnowledgeBase />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              <span className="font-semibold text-gray-700">Phase 7:</span> Real-time Collaboration UI
            </div>
            <div className="flex items-center gap-6">
              <span>{state.metrics.active_instances} Active Instances</span>
              <span>{state.metrics.in_progress_tasks} Tasks In Progress</span>
              <span>{state.metrics.completion_rate.toFixed(1)}% Completion</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
