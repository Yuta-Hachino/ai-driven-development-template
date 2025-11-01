import { useQuery, UseQueryResult } from '@tanstack/react-query'
import axios from 'axios'
import type { WorkflowRun, GitHubIssue, SystemState } from '@/types'

const API_BASE = '/api'

// GitHub API data fetching hooks
export const useWorkflowRuns = (
  repo: string,
  refreshInterval = 30000
): UseQueryResult<WorkflowRun[], Error> => {
  return useQuery({
    queryKey: ['workflow-runs', repo],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/github/workflows`, {
        params: { repo }
      })
      return response.data.data
    },
    refetchInterval: refreshInterval,
    staleTime: 10000,
  })
}

export const useAutonomousDevIssue = (
  repo: string,
  issueNumber?: number
): UseQueryResult<GitHubIssue, Error> => {
  return useQuery({
    queryKey: ['autonomous-dev-issue', repo, issueNumber],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/github/issue`, {
        params: { repo, issue_number: issueNumber }
      })
      return response.data.data
    },
    enabled: !!issueNumber,
    refetchInterval: 15000,
  })
}

export const useSystemState = (
  refreshInterval = 10000
): UseQueryResult<SystemState, Error> => {
  return useQuery({
    queryKey: ['system-state'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/system/state`)
      return response.data.data
    },
    refetchInterval: refreshInterval,
    staleTime: 5000,
  })
}

export const useKnowledgeBase = (
  searchQuery?: string
): UseQueryResult<any[], Error> => {
  return useQuery({
    queryKey: ['knowledge-base', searchQuery],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/memory/search`, {
        params: { q: searchQuery || '' }
      })
      return response.data.data
    },
    enabled: searchQuery !== undefined && searchQuery.length > 0,
    staleTime: 30000,
  })
}

// API mutations
export const pauseInstance = async (instanceId: string): Promise<void> => {
  await axios.post(`${API_BASE}/instances/${instanceId}/pause`)
}

export const resumeInstance = async (instanceId: string): Promise<void> => {
  await axios.post(`${API_BASE}/instances/${instanceId}/resume`)
}

export const reassignTask = async (
  taskId: string,
  newInstanceId: string
): Promise<void> => {
  await axios.post(`${API_BASE}/tasks/reassign`, {
    task_id: taskId,
    instance_id: newInstanceId,
  })
}

export const updateInstanceResources = async (
  instanceId: string,
  maxConcurrentTasks: number
): Promise<void> => {
  await axios.put(`${API_BASE}/instances/${instanceId}/resources`, {
    max_concurrent_tasks: maxConcurrentTasks,
  })
}

export const dismissAlert = async (alertId: string): Promise<void> => {
  await axios.post(`${API_BASE}/alerts/${alertId}/dismiss`)
}
