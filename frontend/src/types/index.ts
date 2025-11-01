/**
 * Type definitions for Autonomous Development Dashboard
 */

export interface Instance {
  id: string
  name: string
  status: 'active' | 'paused' | 'completed' | 'failed'
  workload: number
  max_concurrent_tasks: number
  current_tasks: Task[]
  stats: InstanceStats
  started_at: string
  last_heartbeat: string
}

export interface InstanceStats {
  avg_completion_time: number
  quality_score: number
  tasks_completed: number
  tasks_failed: number
  recent_velocity: number
}

export interface Task {
  id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'blocked'
  assigned_to?: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  progress_percentage: number
  estimated_hours: number
  actual_hours?: number
  dependencies: string[]
  required_skills: string[]
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface P2PMessage {
  id: string
  type: 'leader_election' | 'node_announce' | 'tasks_data' | 'claim' | 'progress' | 'heartbeat'
  sender_id: string
  content: string
  timestamp: string
}

export interface Alert {
  id: string
  title: string
  message: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  timestamp: string
  dismissed: boolean
}

export interface SystemMetrics {
  velocity: number
  completion_rate: number
  bottlenecks: number
  active_instances: number
  pending_tasks: number
  in_progress_tasks: number
  completed_tasks: number
  failed_tasks: number
}

export interface KnowledgeEntry {
  id: string
  title: string
  content: string
  knowledge_type: 'decision' | 'pattern' | 'learning' | 'issue_resolution' | 'best_practice'
  tags: string[]
  created_by: string
  created_at: string
  updated_at: string
  references: string[]
}

export interface SystemState {
  instances: Instance[]
  tasks: Task[]
  messages: P2PMessage[]
  alerts: Alert[]
  metrics: SystemMetrics
  timestamp: string
}

export interface WorkflowRun {
  id: number
  name: string
  status: 'queued' | 'in_progress' | 'completed' | 'failed'
  conclusion?: 'success' | 'failure' | 'cancelled'
  created_at: string
  updated_at: string
  html_url: string
}

export interface GitHubIssue {
  number: number
  title: string
  state: 'open' | 'closed'
  labels: string[]
  created_at: string
  updated_at: string
  html_url: string
  comments_count: number
}

// WebSocket message types
export interface WSMessage {
  type: 'system_state' | 'instance_update' | 'task_update' | 'alert' | 'error'
  data: any
  timestamp: string
}

// API Response types
export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
  timestamp: string
}
