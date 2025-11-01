"""
FastAPI Gateway for Real-time Collaboration Dashboard
Provides WebSocket and REST endpoints for P2P system monitoring
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import asyncio
import json
import os
from datetime import datetime
from github import Github
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Development Dashboard API",
    description="Real-time collaboration dashboard for P2P autonomous development system",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GitHub client initialization
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")  # Format: "owner/repo"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required")

gh = Github(GITHUB_TOKEN)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WebSocket] Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WebSocket] Error sending to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

manager = ConnectionManager()

# Pydantic models
class APIResponse(BaseModel):
    success: bool
    data: Optional[any] = None
    error: Optional[str] = None
    timestamp: str = datetime.now().isoformat()

# Helper functions
def get_repo():
    """Get GitHub repository object"""
    if not GITHUB_REPO:
        raise HTTPException(status_code=500, detail="GITHUB_REPO not configured")
    return gh.get_repo(GITHUB_REPO)

def parse_p2p_message(comment_body: str) -> Optional[Dict]:
    """Parse P2P message from issue comment"""
    markers = {
        '🎯 LEADER_ELECTION': 'leader_election',
        '📡 NODE_ANNOUNCE': 'node_announce',
        '📦 TASKS_DATA': 'tasks_data',
        '🎯 CLAIM': 'claim',
        '📊 PROGRESS': 'progress',
        '💓 HEARTBEAT': 'heartbeat',
    }

    for marker, msg_type in markers.items():
        if marker in comment_body:
            parts = comment_body.split('|')
            return {
                'type': msg_type,
                'raw': comment_body,
                'parts': parts if len(parts) > 1 else [comment_body]
            }
    return None

async def get_system_state() -> Dict:
    """Aggregate current system state from GitHub"""
    try:
        repo = get_repo()

        # Get autonomous dev issue (assuming it's labeled)
        issues = list(repo.get_issues(state='open', labels=['autonomous-dev']))
        if not issues:
            return {
                'instances': [],
                'tasks': [],
                'messages': [],
                'alerts': [],
                'metrics': {
                    'velocity': 0,
                    'completion_rate': 0,
                    'bottlenecks': 0,
                    'active_instances': 0,
                    'pending_tasks': 0,
                    'in_progress_tasks': 0,
                    'completed_tasks': 0,
                    'failed_tasks': 0,
                },
                'timestamp': datetime.now().isoformat()
            }

        issue = issues[0]

        # Parse P2P messages from comments
        comments = list(issue.get_comments())
        messages = []
        for comment in comments[-50:]:  # Last 50 comments
            parsed = parse_p2p_message(comment.body)
            if parsed:
                messages.append({
                    'id': str(comment.id),
                    'type': parsed['type'],
                    'sender_id': parsed['parts'][1] if len(parsed['parts']) > 1 else 'unknown',
                    'content': comment.body,
                    'timestamp': comment.created_at.isoformat(),
                })

        # Get workflow runs to determine instance status
        workflows = list(repo.get_workflow_runs(status='in_progress'))[:5]
        instances = []
        for idx, run in enumerate(workflows):
            if 'p2p' in run.name.lower():
                instances.append({
                    'id': f'instance-{run.id}',
                    'name': f'Instance {idx + 1}',
                    'status': 'active' if run.status == 'in_progress' else 'completed',
                    'workload': 0,  # Calculated from messages
                    'max_concurrent_tasks': 5,
                    'current_tasks': [],
                    'stats': {
                        'avg_completion_time': 0,
                        'quality_score': 0.85,
                        'tasks_completed': 0,
                        'tasks_failed': 0,
                        'recent_velocity': 0,
                    },
                    'started_at': run.created_at.isoformat(),
                    'last_heartbeat': run.updated_at.isoformat(),
                })

        # Calculate metrics
        metrics = {
            'velocity': 0,
            'completion_rate': 0,
            'bottlenecks': 0,
            'active_instances': len(instances),
            'pending_tasks': 0,
            'in_progress_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
        }

        return {
            'instances': instances,
            'tasks': [],  # TODO: Parse from messages
            'messages': messages,
            'alerts': [],
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"[Error] Failed to get system state: {e}")
        raise

# WebSocket endpoint
@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint for system updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send system state update every 5 seconds
            state = await get_system_state()
            await websocket.send_json({
                'type': 'system_state',
                'data': state,
                'timestamp': datetime.now().isoformat()
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        manager.disconnect(websocket)

# REST API endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "Autonomous Development Dashboard API"}

@app.get("/api/system/state")
async def get_state():
    """Get current system state"""
    try:
        state = await get_system_state()
        return APIResponse(success=True, data=state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/github/workflows")
async def get_workflows(repo: str):
    """Get GitHub workflow runs"""
    try:
        gh_repo = gh.get_repo(repo)
        runs = list(gh_repo.get_workflow_runs())[:10]

        workflows = [
            {
                'id': run.id,
                'name': run.name,
                'status': run.status,
                'conclusion': run.conclusion,
                'created_at': run.created_at.isoformat(),
                'updated_at': run.updated_at.isoformat(),
                'html_url': run.html_url,
            }
            for run in runs
        ]

        return APIResponse(success=True, data=workflows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/github/issue")
async def get_issue(repo: str, issue_number: int):
    """Get GitHub issue details"""
    try:
        gh_repo = gh.get_repo(repo)
        issue = gh_repo.get_issue(issue_number)

        return APIResponse(success=True, data={
            'number': issue.number,
            'title': issue.title,
            'state': issue.state,
            'labels': [label.name for label in issue.labels],
            'created_at': issue.created_at.isoformat(),
            'updated_at': issue.updated_at.isoformat(),
            'html_url': issue.html_url,
            'comments_count': issue.comments,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/search")
async def search_knowledge(q: str = ""):
    """Search knowledge base"""
    # TODO: Implement actual knowledge base search
    # For now, return mock data
    return APIResponse(success=True, data=[
        {
            'id': '1',
            'title': 'Database Selection Decision',
            'content': 'Decided to use PostgreSQL for ACID compliance and JSON support',
            'knowledge_type': 'decision',
            'tags': ['database', 'architecture'],
            'created_by': 'tech_lead',
            'created_at': '2025-11-01T10:00:00Z',
            'updated_at': '2025-11-01T10:00:00Z',
            'references': [],
        }
    ])

@app.post("/api/instances/{instance_id}/pause")
async def pause_instance(instance_id: str):
    """Pause an instance"""
    # TODO: Implement instance pause logic
    # This would involve adding a special comment to the GitHub issue
    return APIResponse(success=True, data={'message': f'Instance {instance_id} paused'})

@app.post("/api/instances/{instance_id}/resume")
async def resume_instance(instance_id: str):
    """Resume an instance"""
    # TODO: Implement instance resume logic
    return APIResponse(success=True, data={'message': f'Instance {instance_id} resumed'})

@app.put("/api/instances/{instance_id}/resources")
async def update_resources(instance_id: str, max_concurrent_tasks: int):
    """Update instance resource limits"""
    # TODO: Implement resource update logic
    return APIResponse(success=True, data={'message': f'Resources updated for {instance_id}'})

@app.post("/api/tasks/reassign")
async def reassign_task(task_id: str, instance_id: str):
    """Reassign a task to different instance"""
    # TODO: Implement task reassignment logic
    return APIResponse(success=True, data={'message': f'Task {task_id} reassigned to {instance_id}'})

@app.post("/api/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str):
    """Dismiss an alert"""
    # TODO: Implement alert dismissal logic
    return APIResponse(success=True, data={'message': f'Alert {alert_id} dismissed'})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
