# API Reference - Autonomous Development System

## Overview

REST API documentation for the Autonomous Development System.

**Base URL (Production):** `https://autonomous-dev.example.com/api/v1`
**API Version:** 1.0.0
**Last Updated:** 2025-11-01

---

## Authentication

All API requests require authentication using Bearer tokens.

```http
Authorization: Bearer <your_api_token>
```

**Obtain Token:**
```bash
curl -X POST https://autonomous-dev.example.com/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

---

## Endpoints

### System

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-01T10:00:00Z"
}
```

#### GET /metrics

Prometheus metrics endpoint.

**Response:** Prometheus format metrics

---

### Agents

#### POST /agents

Create and execute an agent task.

**Request:**
```json
{
  "agent_type": "backend",
  "task": "Implement user authentication",
  "priority": "high",
  "timeout_seconds": 300
}
```

**Response:**
```json
{
  "agent_id": "agent-123",
  "status": "running",
  "created_at": "2025-11-01T10:00:00Z"
}
```

#### GET /agents/{agent_id}

Get agent status.

**Response:**
```json
{
  "agent_id": "agent-123",
  "status": "completed",
  "result": "Task completed successfully",
  "execution_time_seconds": 45.2
}
```

---

### Worktrees

#### POST /worktrees

Create a new worktree.

**Request:**
```json
{
  "feature": "user-authentication",
  "pattern": "parallel",
  "base_branch": "main",
  "agent_name": "backend-agent-1"
}
```

**Response:**
```json
{
  "worktree_id": "wt-456",
  "name": "feature/user-authentication-backend-agent-1",
  "path": "/data/worktrees/wt-456",
  "branch": "feature/user-authentication-backend-agent-1"
}
```

#### GET /worktrees

List all active worktrees.

**Response:**
```json
{
  "worktrees": [
    {
      "worktree_id": "wt-456",
      "feature": "user-authentication",
      "pattern": "parallel",
      "status": "active",
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### DELETE /worktrees/{worktree_id}

Remove a worktree.

**Response:**
```json
{
  "status": "deleted",
  "worktree_id": "wt-456"
}
```

---

### Tasks

#### POST /tasks

Create a task plan.

**Request:**
```json
{
  "feature_name": "User Authentication",
  "description": "Implement OAuth 2.0",
  "strategy": "feature_first",
  "complexity": "medium"
}
```

**Response:**
```json
{
  "plan_id": "plan-789",
  "tasks": [
    {
      "task_id": "task-1",
      "title": "Backend API",
      "estimated_hours": 8.0,
      "priority": "high",
      "dependencies": []
    }
  ]
}
```

#### GET /tasks/{task_id}

Get task status.

**Response:**
```json
{
  "task_id": "task-1",
  "status": "completed",
  "assigned_to": "instance-1",
  "progress": 100
}
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Rate Limiting

- **Limit:** 100 requests per minute per API key
- **Headers:**
  - `X-RateLimit-Limit`: Total limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

---

## Webhooks

Configure webhooks to receive event notifications.

**Events:**
- `agent.completed`
- `worktree.created`
- `task.completed`
- `system.error`

**Payload Example:**
```json
{
  "event": "agent.completed",
  "data": {
    "agent_id": "agent-123",
    "status": "success"
  },
  "timestamp": "2025-11-01T10:00:00Z"
}
```

---

## SDK Examples

### Python
```python
import requests

API_BASE = "https://autonomous-dev.example.com/api/v1"
headers = {"Authorization": f"Bearer {api_token}"}

response = requests.post(
    f"{API_BASE}/agents",
    headers=headers,
    json={"agent_type": "backend", "task": "Implement feature"}
)

print(response.json())
```

### cURL
```bash
curl -X POST https://autonomous-dev.example.com/api/v1/agents \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "backend", "task": "Implement feature"}'
```

---

For complete documentation, visit: https://docs.autonomous-dev.example.com
