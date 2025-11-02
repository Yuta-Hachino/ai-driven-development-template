"""
P2P Coordination System

GitHub Issue/Comment based peer-to-peer coordination for Claude Code instances.
No central server required - all coordination happens through GitHub API.
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from github import Github, GithubException


@dataclass
class P2PNode:
    """Represents a Claude Code instance in the P2P network"""
    node_id: str
    job_id: str
    run_id: str
    is_leader: bool
    status: str  # 'initializing', 'ready', 'working', 'completed', 'failed'
    current_task: Optional[str] = None
    started_at: str = None
    last_heartbeat: str = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class P2PTask:
    """Represents a task in the P2P network"""
    task_id: str
    title: str
    description: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    estimated_hours: float
    required_skills: List[str]
    dependencies: List[str]
    status: str  # 'available', 'claimed', 'in_progress', 'completed', 'failed'
    claimed_by: Optional[str] = None
    claimed_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class P2PCoordinator:
    """
    Peer-to-peer coordinator using GitHub as the communication layer.

    Uses GitHub Issues and Comments for:
    - Leader election
    - Task distribution
    - Progress reporting
    - Node discovery
    - Heartbeat monitoring
    """

    def __init__(
        self,
        github_token: str,
        repo: str,
        issue_number: int,
        run_id: str,
        job_id: str
    ):
        self.gh = Github(github_token)
        self.repo = self.gh.get_repo(repo)
        self.issue = self.repo.get_issue(issue_number)
        self.run_id = run_id
        self.job_id = job_id
        self.node_id = f"{run_id}-{job_id}"
        self.is_leader = False
        self.peers: Dict[str, P2PNode] = {}
        self.tasks: Dict[str, P2PTask] = {}

    # ==================== Leader Election ====================

    async def elect_leader(self) -> bool:
        """
        Elect a leader using GitHub comments as a distributed lock.
        First node to comment becomes the leader.

        Returns:
            bool: True if this node is the leader
        """
        marker = f"🎯 LEADER_ELECTION|{self.node_id}|{time.time()}"

        try:
            # Try to claim leadership
            self.issue.create_comment(marker)

            # Wait for other nodes to potentially claim
            await asyncio.sleep(2)

            # Get all election comments
            comments = list(self.issue.get_comments())
            election_comments = [
                c for c in comments
                if c.body.startswith("🎯 LEADER_ELECTION|")
            ]

            if not election_comments:
                return False

            # Earliest comment wins
            earliest = min(election_comments, key=lambda c: c.created_at)
            is_leader = earliest.body == marker

            if is_leader:
                self.is_leader = True
                self.issue.create_comment(
                    f"✅ **Leader Elected:** Node `{self.node_id}`\n\n"
                    f"This node will coordinate task distribution."
                )

            return is_leader

        except GithubException as e:
            print(f"Leader election error: {e}")
            return False

    # ==================== Node Discovery ====================

    async def announce_presence(self):
        """Announce this node's presence to the network"""
        node = P2PNode(
            node_id=self.node_id,
            job_id=self.job_id,
            run_id=self.run_id,
            is_leader=self.is_leader,
            status='ready',
            started_at=datetime.utcnow().isoformat(),
            last_heartbeat=datetime.utcnow().isoformat()
        )

        marker = f"📡 NODE_ANNOUNCE|{json.dumps(node.to_dict())}"
        self.issue.create_comment(marker)

        print(f"✓ Announced presence: {self.node_id}")

    async def discover_peers(self) -> List[P2PNode]:
        """Discover all active nodes in the network"""
        comments = list(self.issue.get_comments())

        nodes = []
        for comment in comments:
            if comment.body.startswith("📡 NODE_ANNOUNCE|"):
                try:
                    data_str = comment.body.split("|", 1)[1]
                    node_data = json.loads(data_str)
                    node = P2PNode(**node_data)

                    # Check if node is still alive (heartbeat < 5 minutes ago)
                    if node.last_heartbeat:
                        last_hb = datetime.fromisoformat(node.last_heartbeat)
                        if datetime.utcnow() - last_hb < timedelta(minutes=5):
                            nodes.append(node)
                            self.peers[node.node_id] = node

                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Failed to parse node announcement: {e}")
                    continue

        print(f"✓ Discovered {len(nodes)} active peers")
        return nodes

    # ==================== Task Management ====================

    async def publish_tasks(self, tasks: List[P2PTask]):
        """
        Publish tasks to the network (leader only).

        Args:
            tasks: List of tasks to distribute
        """
        if not self.is_leader:
            print("⚠ Only leader can publish tasks")
            return

        self.tasks = {task.task_id: task for task in tasks}

        # Create a formatted task list
        task_list = "\n".join([
            f"- [ ] **{task.task_id}**: {task.title} "
            f"(Priority: {task.priority}, Est: {task.estimated_hours}h)"
            for task in tasks
        ])

        # Publish to GitHub
        comment = (
            f"## 📋 Available Tasks\n\n"
            f"{task_list}\n\n"
            f"---\n"
            f"**To claim a task:** Comment with `🎯 CLAIM|task-id|node-id`\n"
            f"**Total tasks:** {len(tasks)}"
        )

        self.issue.create_comment(comment)

        # Store tasks in a structured comment
        tasks_data = {
            task.task_id: task.to_dict()
            for task in tasks
        }
        self.issue.create_comment(
            f"📦 TASKS_DATA|{json.dumps(tasks_data)}"
        )

        print(f"✓ Published {len(tasks)} tasks")

    async def get_available_tasks(self) -> List[P2PTask]:
        """Get all available (unclaimed) tasks"""
        comments = list(self.issue.get_comments())

        # Find latest tasks data
        for comment in reversed(comments):
            if comment.body.startswith("📦 TASKS_DATA|"):
                try:
                    data_str = comment.body.split("|", 1)[1]
                    tasks_data = json.loads(data_str)

                    tasks = []
                    for task_id, task_dict in tasks_data.items():
                        task = P2PTask(**task_dict)
                        if task.status == 'available':
                            tasks.append(task)

                    return tasks

                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Failed to parse tasks data: {e}")
                    continue

        return []

    async def claim_task(self, task_id: str) -> bool:
        """
        Attempt to claim a task using optimistic locking.

        Args:
            task_id: ID of the task to claim

        Returns:
            bool: True if claim was successful
        """
        claim_marker = f"🎯 CLAIM|{task_id}|{self.node_id}|{time.time()}"

        try:
            # Attempt to claim
            self.issue.create_comment(claim_marker)

            # Wait for competing claims
            await asyncio.sleep(1)

            # Check all claims for this task
            comments = list(self.issue.get_comments())
            claim_comments = [
                c for c in comments
                if c.body.startswith(f"🎯 CLAIM|{task_id}|")
            ]

            if not claim_comments:
                return False

            # Earliest claim wins
            earliest = min(claim_comments, key=lambda c: c.created_at)
            success = earliest.body == claim_marker

            if success:
                self.issue.create_comment(
                    f"✅ **Task Claimed:** `{task_id}` by Node `{self.node_id}`"
                )
                print(f"✓ Successfully claimed task: {task_id}")
            else:
                print(f"✗ Task {task_id} claimed by another node")

            return success

        except GithubException as e:
            print(f"Task claim error: {e}")
            return False

    # ==================== Progress Reporting ====================

    async def report_progress(
        self,
        task_id: str,
        status: str,
        progress: int,
        message: str = ""
    ):
        """
        Report task progress.

        Args:
            task_id: ID of the task
            status: Current status ('in_progress', 'completed', 'failed')
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        report = {
            "task_id": task_id,
            "node_id": self.node_id,
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Progress emoji based on status
        emoji = {
            'in_progress': '⚙️',
            'completed': '✅',
            'failed': '❌'
        }.get(status, '📊')

        comment = (
            f"{emoji} **Progress Update**\n\n"
            f"- **Task:** `{task_id}`\n"
            f"- **Node:** `{self.node_id}`\n"
            f"- **Status:** {status}\n"
            f"- **Progress:** {progress}%\n"
        )

        if message:
            comment += f"- **Message:** {message}\n"

        self.issue.create_comment(comment)

        # Store structured data
        self.issue.create_comment(
            f"📊 PROGRESS|{json.dumps(report)}"
        )

        print(f"✓ Reported progress: {task_id} - {progress}%")

    async def heartbeat(self):
        """Send heartbeat to indicate node is still alive"""
        heartbeat_data = {
            "node_id": self.node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "alive"
        }

        self.issue.create_comment(
            f"💓 HEARTBEAT|{json.dumps(heartbeat_data)}"
        )

    # ==================== Monitoring ====================

    async def get_network_status(self) -> Dict[str, Any]:
        """Get overall network status"""
        peers = await self.discover_peers()
        tasks = await self.get_available_tasks()

        # Count tasks by status
        comments = list(self.issue.get_comments())
        progress_reports = []

        for comment in comments:
            if comment.body.startswith("📊 PROGRESS|"):
                try:
                    data_str = comment.body.split("|", 1)[1]
                    report = json.loads(data_str)
                    progress_reports.append(report)
                except:
                    continue

        # Get latest status for each task
        task_status = {}
        for report in sorted(progress_reports, key=lambda r: r['timestamp']):
            task_status[report['task_id']] = report

        completed = sum(1 for r in task_status.values() if r['status'] == 'completed')
        in_progress = sum(1 for r in task_status.values() if r['status'] == 'in_progress')
        failed = sum(1 for r in task_status.values() if r['status'] == 'failed')

        return {
            "active_nodes": len(peers),
            "total_tasks": len(self.tasks),
            "available_tasks": len(tasks),
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "failed_tasks": failed,
            "nodes": [node.to_dict() for node in peers],
            "task_status": task_status
        }

    # ==================== Utility Methods ====================

    async def wait_for_completion(self, timeout: int = 3600):
        """
        Wait for all tasks to complete or timeout.

        Args:
            timeout: Maximum time to wait in seconds
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = await self.get_network_status()

            total = status['total_tasks']
            completed = status['completed_tasks']
            failed = status['failed_tasks']

            if total > 0 and (completed + failed) >= total:
                print(f"✓ All tasks completed: {completed} success, {failed} failed")
                return True

            await asyncio.sleep(30)

        print(f"⚠ Timeout waiting for task completion")
        return False

    async def cleanup(self):
        """Clean up and announce node departure"""
        self.issue.create_comment(
            f"👋 **Node Departing:** `{self.node_id}`\n\n"
            f"Status: {'Leader' if self.is_leader else 'Worker'}"
        )


# ==================== Helper Functions ====================

async def run_as_leader(coordinator: P2PCoordinator, tasks: List[P2PTask]):
    """Run this node as the leader"""
    print(f"\n{'='*60}")
    print(f"🎯 Running as LEADER")
    print(f"{'='*60}\n")

    # Announce presence
    await coordinator.announce_presence()

    # Publish tasks
    await coordinator.publish_tasks(tasks)

    # Monitor progress
    heartbeat_task = asyncio.create_task(periodic_heartbeat(coordinator))

    try:
        # Wait for all tasks to complete
        await coordinator.wait_for_completion()

        # Print final status
        status = await coordinator.get_network_status()
        print(f"\n{'='*60}")
        print(f"📊 Final Status:")
        print(f"  Active Nodes: {status['active_nodes']}")
        print(f"  Completed: {status['completed_tasks']}")
        print(f"  Failed: {status['failed_tasks']}")
        print(f"{'='*60}\n")

    finally:
        heartbeat_task.cancel()
        await coordinator.cleanup()


async def run_as_worker(coordinator: P2PCoordinator):
    """Run this node as a worker"""
    print(f"\n{'='*60}")
    print(f"⚙️ Running as WORKER")
    print(f"{'='*60}\n")

    # Announce presence
    await coordinator.announce_presence()

    # Start heartbeat
    heartbeat_task = asyncio.create_task(periodic_heartbeat(coordinator))

    try:
        # Main work loop
        while True:
            # Get available tasks
            tasks = await coordinator.get_available_tasks()

            if not tasks:
                print("No tasks available, waiting...")
                await asyncio.sleep(10)
                continue

            # Try to claim a task
            task = tasks[0]  # Take highest priority
            claimed = await coordinator.claim_task(task.task_id)

            if claimed:
                # Execute the task
                await execute_task(coordinator, task)
            else:
                # Try another task
                await asyncio.sleep(5)

    finally:
        heartbeat_task.cancel()
        await coordinator.cleanup()


async def execute_task(coordinator: P2PCoordinator, task: P2PTask):
    """Execute a claimed task"""
    print(f"\n{'='*60}")
    print(f"🔨 Executing Task: {task.task_id}")
    print(f"  Title: {task.title}")
    print(f"  Priority: {task.priority}")
    print(f"{'='*60}\n")

    try:
        # Report start
        await coordinator.report_progress(
            task.task_id,
            'in_progress',
            0,
            "Starting task execution"
        )

        # TODO: Actual task execution would go here
        # For now, simulate work
        await asyncio.sleep(5)

        # Report completion
        await coordinator.report_progress(
            task.task_id,
            'completed',
            100,
            "Task completed successfully"
        )

        print(f"✓ Task {task.task_id} completed\n")

    except Exception as e:
        # Report failure
        await coordinator.report_progress(
            task.task_id,
            'failed',
            0,
            f"Task failed: {str(e)}"
        )
        print(f"✗ Task {task.task_id} failed: {e}\n")


async def periodic_heartbeat(coordinator: P2PCoordinator):
    """Send periodic heartbeats"""
    while True:
        try:
            await coordinator.heartbeat()
            await asyncio.sleep(60)  # Every minute
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Heartbeat error: {e}")
            await asyncio.sleep(60)
