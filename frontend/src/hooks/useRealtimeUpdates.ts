import { useState, useEffect, useCallback, useRef } from 'react'
import type { SystemState, WSMessage } from '@/types'

interface UseRealtimeUpdatesReturn {
  state: SystemState | null
  connected: boolean
  error: string | null
  reconnect: () => void
}

const WS_URL = import.meta.env.PROD
  ? 'wss://your-backend.example.com/ws/realtime'
  : 'ws://localhost:8000/ws/realtime'

const RECONNECT_INTERVAL = 5000
const MAX_RECONNECT_ATTEMPTS = 10

export const useRealtimeUpdates = (): UseRealtimeUpdatesReturn => {
  const [state, setState] = useState<SystemState | null>(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('[WebSocket] Connected')
        setConnected(true)
        setError(null)
        setReconnectAttempts(0)
      }

      ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data)

          switch (message.type) {
            case 'system_state':
              setState(message.data)
              break
            case 'instance_update':
              setState(prev => {
                if (!prev) return null
                return {
                  ...prev,
                  instances: prev.instances.map(inst =>
                    inst.id === message.data.id ? { ...inst, ...message.data } : inst
                  )
                }
              })
              break
            case 'task_update':
              setState(prev => {
                if (!prev) return null
                return {
                  ...prev,
                  tasks: prev.tasks.map(task =>
                    task.id === message.data.id ? { ...task, ...message.data } : task
                  )
                }
              })
              break
            case 'alert':
              setState(prev => {
                if (!prev) return null
                return {
                  ...prev,
                  alerts: [message.data, ...prev.alerts]
                }
              })
              break
            case 'error':
              console.error('[WebSocket] Server error:', message.data)
              setError(message.data.message || 'Unknown server error')
              break
            default:
              console.warn('[WebSocket] Unknown message type:', message.type)
          }
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err)
        }
      }

      ws.onerror = (event) => {
        console.error('[WebSocket] Error:', event)
        setError('WebSocket connection failed')
        setConnected(false)
      }

      ws.onclose = (event) => {
        console.log('[WebSocket] Closed:', event.code, event.reason)
        setConnected(false)

        // Attempt to reconnect
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          console.log(`[WebSocket] Reconnecting in ${RECONNECT_INTERVAL}ms (attempt ${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`)

          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1)
            connect()
          }, RECONNECT_INTERVAL)
        } else {
          setError('Max reconnection attempts reached. Please refresh the page.')
        }
      }
    } catch (err) {
      console.error('[WebSocket] Connection error:', err)
      setError('Failed to establish WebSocket connection')
    }
  }, [reconnectAttempts])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  const reconnect = useCallback(() => {
    disconnect()
    setReconnectAttempts(0)
    connect()
  }, [connect, disconnect])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return {
    state,
    connected,
    error,
    reconnect,
  }
}
