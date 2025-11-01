# Phase 7: Real-time Collaboration UI

**Status**: ✅ Completed
**Duration**: Week 14-16
**Goal**: Build interactive web interface for real-time monitoring and control of P2P autonomous development

## Overview

Phase 7 introduces a modern, real-time web dashboard for monitoring and controlling the P2P autonomous development system. This replaces the static GitHub Pages dashboard (Phase 6) with a fully interactive, WebSocket-powered application.

### Key Features

- **Real-time Updates**: WebSocket connection provides instant system state updates
- **Interactive Controls**: Pause/resume instances, adjust resources, reassign tasks
- **Rich Visualizations**: Instance grids, task timelines, P2P network graphs
- **Knowledge Base Browser**: Search and browse project memory
- **Alert System**: Real-time notifications for system events
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         React + TypeScript Frontend (Port 3000)         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Components:                                     │   │
│  │  • Dashboard (main layout)                       │   │
│  │  • InstanceGrid (instance management)            │   │
│  │  • TaskTimeline (Kanban-style task board)        │   │
│  │  • P2PNetworkGraph (network visualization)       │   │
│  │  • KnowledgeBase (search & browse)               │   │
│  │  • MetricsOverview (system metrics)              │   │
│  │  • AlertPanel (notifications)                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────┘
                  │ WebSocket/REST
                  │ ws://localhost:8000/ws/realtime
                  │ http://localhost:8000/api/*
┌─────────────────▼───────────────────────────────────────┐
│         FastAPI Backend (Port 8000)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Endpoints:                                      │   │
│  │  • WebSocket: Real-time state broadcasting       │   │
│  │  • GET /api/system/state                         │   │
│  │  • GET /api/github/workflows                     │   │
│  │  • GET /api/github/issue                         │   │
│  │  • GET /api/memory/search                        │   │
│  │  • POST /api/instances/{id}/pause                │   │
│  │  • POST /api/instances/{id}/resume               │   │
│  │  • PUT /api/instances/{id}/resources             │   │
│  │  • POST /api/tasks/reassign                      │   │
│  │  • POST /api/alerts/{id}/dismiss                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────┘
                  │ GitHub API (PyGithub)
┌─────────────────▼───────────────────────────────────────┐
│              GitHub (Data Source)                       │
│  • Issue Comments (P2P Messages)                        │
│  • Workflow Runs (Instance Status)                      │
│  • Project Memory (Knowledge Base)                      │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend

- **React 18** - Modern UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **TanStack Query (React Query)** - Data fetching and caching
- **Zustand** - Lightweight state management
- **Recharts** - Data visualization
- **Lucide React** - Icon library

### Backend

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server with WebSocket support
- **PyGithub** - GitHub API client
- **Pydantic** - Data validation
- **WebSockets** - Real-time communication protocol

## Setup & Installation

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- GitHub Personal Access Token with repo access

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN="your_github_token_here"
export GITHUB_REPO="owner/repo"

# Run server
python api/gateway.py
# Or with uvicorn:
uvicorn api.gateway:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (optional, defaults work for local development)
cp .env.example .env

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000` (or the port Vite assigns)

## Usage Guide

### 1. Overview Tab

The main dashboard showing system health at a glance:

- **Metrics Cards**: Active instances, completion rate, velocity, bottlenecks
- **Task Distribution**: Visual breakdown of pending/in-progress/completed/failed tasks
- **Quick Instance View**: Top 5 active instances with workload
- **Recent Tasks**: Latest task updates

### 2. Instances Tab

Detailed instance management:

- **Instance Cards**: Full information for each Claude Code instance
- **Status Indicators**: Active (green), Paused (yellow), Failed (red), Completed (gray)
- **Workload Visualization**: Progress bars showing task capacity
- **Performance Stats**: Quality score, average completion time, velocity
- **Interactive Controls**:
  - Pause/Resume buttons
  - Resource limit slider (max concurrent tasks)
  - Current task list
  - Timestamps for start and last heartbeat

### 3. Tasks Tab

Kanban-style task board with 5 columns:

- **Pending**: Unassigned or queued tasks
- **In Progress**: Currently being worked on
- **Blocked**: Waiting on dependencies
- **Completed**: Successfully finished
- **Failed**: Encountered errors

Each task card shows:
- Priority badge (critical, high, medium, low)
- Progress percentage
- Assigned instance
- Time estimates (estimated vs actual)
- Required skills
- Dependencies count

### 4. P2P Network Tab

Network topology and communication monitoring:

- **Network Statistics**: Total messages, active instances, heartbeats, claims
- **Visual Network Graph**: SVG diagram showing GitHub as central hub with instances
- **Message Distribution**: Breakdown by message type (leader election, heartbeat, etc.)
- **Message Log**: Recent 20 P2P messages with timestamps and details

### 5. Knowledge Base Tab

Search and browse project memory:

- **Search Bar**: Full-text search with 2-character minimum
- **Type Filters**: All, Decisions, Patterns, Learnings, Resolutions, Best Practices
- **Entry Cards**: Rich display with content, tags, references
- **Metadata**: Created by, timestamps, update history

## WebSocket Protocol

### Client → Server

The WebSocket connection is currently one-way (server → client), but can be extended for:
- Manual state refresh requests
- Subscription to specific instance updates
- Custom alert thresholds

### Server → Client

Messages follow this format:

```json
{
  "type": "system_state" | "instance_update" | "task_update" | "alert" | "error",
  "data": { ... },
  "timestamp": "2025-11-01T12:00:00Z"
}
```

**Message Types:**

1. **system_state** - Full system snapshot (sent every 5 seconds)
   ```json
   {
     "type": "system_state",
     "data": {
       "instances": [...],
       "tasks": [...],
       "messages": [...],
       "alerts": [...],
       "metrics": {...}
     }
   }
   ```

2. **instance_update** - Partial update for single instance
3. **task_update** - Partial update for single task
4. **alert** - New alert notification
5. **error** - Server error message

## REST API Reference

### System Endpoints

#### `GET /api/system/state`

Get current system state.

**Response:**
```json
{
  "success": true,
  "data": {
    "instances": [...],
    "tasks": [...],
    "messages": [...],
    "alerts": [...],
    "metrics": {...}
  },
  "timestamp": "2025-11-01T12:00:00Z"
}
```

### GitHub Endpoints

#### `GET /api/github/workflows?repo=owner/repo`

Get workflow runs from GitHub repository.

#### `GET /api/github/issue?repo=owner/repo&issue_number=123`

Get specific issue details.

### Instance Control Endpoints

#### `POST /api/instances/{instance_id}/pause`

Pause an instance (prevents it from claiming new tasks).

#### `POST /api/instances/{instance_id}/resume`

Resume a paused instance.

#### `PUT /api/instances/{instance_id}/resources`

Update instance resource limits.

**Body:**
```json
{
  "max_concurrent_tasks": 5
}
```

### Task Endpoints

#### `POST /api/tasks/reassign`

Reassign task to different instance.

**Body:**
```json
{
  "task_id": "task-123",
  "instance_id": "instance-456"
}
```

### Knowledge Base Endpoints

#### `GET /api/memory/search?q=database`

Search knowledge base entries.

## Deployment

### Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python api/gateway.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Production

#### Option 1: Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - GITHUB_REPO=${GITHUB_REPO}

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

#### Option 2: Separate Deployments

**Backend** - Deploy to Cloud Run, Heroku, or any Python hosting:
```bash
# Build and deploy
docker build -t autonomous-dev-backend backend/
gcloud run deploy autonomous-dev-backend --image autonomous-dev-backend
```

**Frontend** - Deploy to Vercel, Netlify, or any static hosting:
```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting platform
```

## Performance Metrics

### Target Metrics

- ✅ WebSocket latency: <100ms
- ✅ Initial page load: <2 seconds
- ✅ State update frequency: Every 5 seconds
- ✅ Concurrent users: 100+
- ✅ Mobile responsive: ✓

### Optimization Strategies

1. **Data Fetching**:
   - React Query caching reduces redundant API calls
   - Stale-while-revalidate strategy
   - Automatic retry on failure

2. **WebSocket Efficiency**:
   - Connection pooling and reuse
   - Automatic reconnection with exponential backoff
   - Broadcast to multiple clients efficiently

3. **UI Performance**:
   - Virtual scrolling for long lists (if needed)
   - Lazy loading of components
   - Optimistic UI updates

## Security Considerations

### Authentication & Authorization

Currently, the dashboard has no built-in authentication. For production use:

1. **Add Authentication**:
   - GitHub OAuth for user login
   - JWT tokens for API access
   - Role-based access control (RBAC)

2. **Secure WebSocket**:
   - WSS (WebSocket Secure) with TLS
   - Token-based authentication for WebSocket handshake

3. **API Rate Limiting**:
   - Implement rate limiting per IP/user
   - GitHub API quota management

### Environment Variables

Never commit sensitive data:
```bash
# Backend .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=owner/repo
SECRET_KEY=your-secret-key-here

# Frontend .env
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com
```

## Future Enhancements

### Phase 7.1: Advanced Features

- [ ] **Drag-and-Drop Task Reassignment**: Move tasks between instances visually
- [ ] **Instance Chat**: Send direct messages to instances
- [ ] **Custom Dashboards**: User-configurable layouts and widgets
- [ ] **Saved Views**: Bookmark specific filters and searches
- [ ] **Export Reports**: PDF/CSV export of metrics and logs

### Phase 7.2: AI-Powered Insights

- [ ] **Anomaly Detection**: Automatically flag unusual behavior
- [ ] **Predictive Analytics**: Forecast bottlenecks before they occur (Phase 6 ML integration)
- [ ] **Smart Recommendations**: Suggest optimal task assignments
- [ ] **Natural Language Queries**: Ask questions in plain English

### Phase 7.3: Collaboration Features

- [ ] **Multi-User Support**: Multiple developers viewing simultaneously
- [ ] **Real-time Cursors**: See what others are viewing
- [ ] **Shared Annotations**: Comment on tasks and instances
- [ ] **Approval Workflows**: Human-in-the-loop approvals for critical decisions

## Troubleshooting

### WebSocket Connection Failed

**Problem**: Dashboard shows "Disconnected" status

**Solutions**:
1. Verify backend is running (`http://localhost:8000`)
2. Check CORS settings in `backend/api/gateway.py`
3. Ensure no firewall blocking WebSocket connections
4. Check browser console for detailed errors

### No Data Showing

**Problem**: Dashboard loads but shows empty state

**Solutions**:
1. Verify `GITHUB_TOKEN` is set correctly
2. Confirm `GITHUB_REPO` environment variable is in `owner/repo` format
3. Ensure the repository has at least one issue with `autonomous-dev` label
4. Check GitHub API rate limits

### Frontend Build Errors

**Problem**: `npm run build` fails

**Solutions**:
1. Delete `node_modules` and `package-lock.json`, run `npm install` again
2. Ensure Node.js version is 18+
3. Check for TypeScript errors: `npm run type-check`
4. Clear Vite cache: `rm -rf node_modules/.vite`

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### E2E Tests

```bash
# Install Playwright
npm install -D @playwright/test

# Run E2E tests
npm run test:e2e
```

## Contributing

See main [CONTRIBUTING.md](../CONTRIBUTING.md) for general guidelines.

**Dashboard-Specific Guidelines**:

1. **Component Structure**: One component per file
2. **TypeScript**: All components must be typed
3. **Styling**: Use TailwindCSS utilities only (no custom CSS)
4. **State Management**: Prefer React Query for server state, Zustand for client state
5. **Accessibility**: Ensure WCAG 2.1 AA compliance

## License

MIT License - see [LICENSE](../LICENSE)

---

**Phase 7 Summary**: Real-time Collaboration UI provides a modern, interactive dashboard for monitoring and controlling the P2P autonomous development system, replacing the static GitHub Pages dashboard with WebSocket-powered real-time updates and interactive controls.

**Next Phase**: Phase 8 - Advanced Features (ML-powered insights, cross-repository collaboration, or enterprise features)
