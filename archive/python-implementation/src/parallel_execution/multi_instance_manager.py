"""
Multi-Instance Manager

Manages multiple Claude Code instances working in parallel.
Coordinates tasks, resources, and communication between instances.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import json

logger = logging.getLogger(__name__)


class InstanceStatus(Enum):
    """Status of Claude Code instance"""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class InstanceConfig:
    """Configuration for a Claude Code instance"""
    instance_id: int
    name: str
    worktree_path: str
    assigned_tasks: List[str] = field(default_factory=list)
    specialization: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 3
    resource_limits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoordinationMessage:
    """Message for inter-instance communication"""
    from_instance: int
    to_instance: Optional[int]  # None = broadcast
    message_type: str  # 'task_claim', 'task_complete', 'help_request', 'share_knowledge'
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: TaskPriority = TaskPriority.MEDIUM


@dataclass
class Task:
    """Represents a development task"""
    task_id: str
    description: str
    priority: TaskPriority
    assigned_to: Optional[int] = None
    status: str = "pending"
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None


class MultiInstanceManager:
    """
    Manages multiple Claude Code instances working in parallel.

    Features:
    - Instance lifecycle management
    - Task distribution and load balancing
    - Inter-instance communication
    - Resource coordination
    - Conflict detection and resolution
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.instances: Dict[int, InstanceConfig] = {}
        self.instance_status: Dict[int, InstanceStatus] = {}
        self.tasks: Dict[str, Task] = {}
        self.message_queue: List[CoordinationMessage] = []
        self.shared_state: Dict[str, Any] = {}
        self.max_instances = self.config.get("max_instances", 10)

        # Communication channels
        self.github_issues_enabled = self.config.get("use_github_issues", True)
        self.shared_files_path = Path(self.config.get("shared_files_path", "docs/shared_knowledge"))
        self.shared_files_path.mkdir(parents=True, exist_ok=True)

    def register_instance(self, config: InstanceConfig) -> bool:
        """
        Register a new Claude Code instance.

        Args:
            config: Instance configuration

        Returns:
            True if registration successful
        """
        if config.instance_id in self.instances:
            logger.warning(f"Instance {config.instance_id} already registered")
            return False

        if len(self.instances) >= self.max_instances:
            logger.error(f"Maximum instances ({self.max_instances}) reached")
            return False

        self.instances[config.instance_id] = config
        self.instance_status[config.instance_id] = InstanceStatus.IDLE

        logger.info(
            f"Registered instance {config.instance_id}: {config.name} "
            f"at {config.worktree_path}"
        )

        # Save to shared state
        self._update_shared_state()

        return True

    def create_task(
        self,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None
    ) -> Task:
        """
        Create a new task.

        Args:
            description: Task description
            priority: Task priority
            dependencies: List of task IDs this depends on

        Returns:
            Created Task object
        """
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"

        task = Task(
            task_id=task_id,
            description=description,
            priority=priority,
            dependencies=dependencies or []
        )

        self.tasks[task_id] = task

        logger.info(f"Created task {task_id}: {description} [{priority.value}]")

        return task

    def assign_task(self, task_id: str, instance_id: int) -> bool:
        """
        Assign task to instance.

        Args:
            task_id: Task identifier
            instance_id: Instance to assign to

        Returns:
            True if assignment successful
        """
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False

        if instance_id not in self.instances:
            logger.error(f"Instance {instance_id} not found")
            return False

        task = self.tasks[task_id]

        # Check dependencies
        if not self._check_dependencies(task):
            logger.warning(f"Task {task_id} has unmet dependencies")
            return False

        task.assigned_to = instance_id
        task.status = "assigned"

        self.instances[instance_id].assigned_tasks.append(task_id)

        logger.info(f"Assigned task {task_id} to instance {instance_id}")

        # Send message to instance
        self._send_message(
            CoordinationMessage(
                from_instance=0,  # Manager
                to_instance=instance_id,
                message_type="task_assigned",
                content={"task_id": task_id, "description": task.description},
                priority=task.priority
            )
        )

        return True

    def auto_assign_tasks(self) -> Dict[str, int]:
        """
        Automatically assign pending tasks to available instances.

        Uses load balancing based on:
        - Instance current workload
        - Task priority
        - Instance specialization

        Returns:
            Dict mapping task_id to assigned instance_id
        """
        assignments = {}

        # Get pending tasks sorted by priority
        pending_tasks = [
            t for t in self.tasks.values()
            if t.status == "pending" and self._check_dependencies(t)
        ]
        pending_tasks.sort(key=lambda t: t.priority.value, reverse=True)

        # Get available instances
        available_instances = [
            inst_id for inst_id, status in self.instance_status.items()
            if status == InstanceStatus.IDLE or status == InstanceStatus.RUNNING
        ]

        for task in pending_tasks:
            # Find best instance for this task
            best_instance = self._find_best_instance(task, available_instances)

            if best_instance is not None:
                if self.assign_task(task.task_id, best_instance):
                    assignments[task.task_id] = best_instance

        logger.info(f"Auto-assigned {len(assignments)} tasks")

        return assignments

    def _find_best_instance(
        self,
        task: Task,
        available_instances: List[int]
    ) -> Optional[int]:
        """Find best instance for task based on load and specialization"""
        if not available_instances:
            return None

        # Score each instance
        scores = {}

        for inst_id in available_instances:
            instance = self.instances[inst_id]

            # Calculate workload
            current_tasks = len(instance.assigned_tasks)
            workload_score = max(0, 100 - (current_tasks * 20))

            # Check specialization match
            specialization_score = 0
            # Could check if task description matches instance specialization

            # Total score
            scores[inst_id] = workload_score + specialization_score

        # Return instance with highest score
        if scores:
            return max(scores, key=scores.get)

        return available_instances[0]

    def _check_dependencies(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                if self.tasks[dep_id].status != "completed":
                    return False
        return True

    def complete_task(self, task_id: str, result: Any) -> bool:
        """
        Mark task as completed.

        Args:
            task_id: Task identifier
            result: Task result

        Returns:
            True if successful
        """
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = "completed"
        task.completed_at = datetime.now()
        task.result = result

        # Remove from instance's assigned tasks
        if task.assigned_to is not None:
            instance = self.instances[task.assigned_to]
            if task_id in instance.assigned_tasks:
                instance.assigned_tasks.remove(task_id)

        logger.info(f"Task {task_id} completed by instance {task.assigned_to}")

        # Broadcast completion
        self._send_message(
            CoordinationMessage(
                from_instance=task.assigned_to or 0,
                to_instance=None,  # Broadcast
                message_type="task_complete",
                content={"task_id": task_id, "result": result}
            )
        )

        return True

    def _send_message(self, message: CoordinationMessage):
        """Send coordination message"""
        self.message_queue.append(message)

        # Persist to shared files
        self._save_message_to_file(message)

        logger.debug(
            f"Message from instance {message.from_instance}: "
            f"{message.message_type}"
        )

    def get_messages(
        self,
        instance_id: int,
        message_type: Optional[str] = None
    ) -> List[CoordinationMessage]:
        """
        Get messages for instance.

        Args:
            instance_id: Instance to get messages for
            message_type: Optional filter by message type

        Returns:
            List of messages
        """
        messages = [
            msg for msg in self.message_queue
            if msg.to_instance is None or msg.to_instance == instance_id
        ]

        if message_type:
            messages = [msg for msg in messages if msg.message_type == message_type]

        return messages

    def _save_message_to_file(self, message: CoordinationMessage):
        """Save message to shared file for persistence"""
        messages_file = self.shared_files_path / "coordination_messages.jsonl"

        message_dict = {
            "from_instance": message.from_instance,
            "to_instance": message.to_instance,
            "message_type": message.message_type,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "priority": message.priority.value
        }

        with open(messages_file, "a") as f:
            f.write(json.dumps(message_dict) + "\n")

    def _update_shared_state(self):
        """Update shared state file"""
        state_file = self.shared_files_path / "shared_state.json"

        state = {
            "instances": {
                inst_id: {
                    "name": inst.name,
                    "worktree_path": inst.worktree_path,
                    "assigned_tasks": inst.assigned_tasks,
                    "status": self.instance_status[inst_id].value
                }
                for inst_id, inst in self.instances.items()
            },
            "tasks": {
                task_id: {
                    "description": task.description,
                    "priority": task.priority.value,
                    "status": task.status,
                    "assigned_to": task.assigned_to
                }
                for task_id, task in self.tasks.items()
            },
            "updated_at": datetime.now().isoformat()
        }

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    def get_instance_status(self, instance_id: int) -> Optional[Dict[str, Any]]:
        """Get status of an instance"""
        if instance_id not in self.instances:
            return None

        instance = self.instances[instance_id]
        status = self.instance_status[instance_id]

        return {
            "instance_id": instance_id,
            "name": instance.name,
            "status": status.value,
            "assigned_tasks": len(instance.assigned_tasks),
            "worktree_path": instance.worktree_path,
            "specialization": instance.specialization
        }

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all instances and tasks"""
        return {
            "total_instances": len(self.instances),
            "active_instances": sum(
                1 for s in self.instance_status.values()
                if s == InstanceStatus.RUNNING
            ),
            "total_tasks": len(self.tasks),
            "pending_tasks": sum(1 for t in self.tasks.values() if t.status == "pending"),
            "completed_tasks": sum(1 for t in self.tasks.values() if t.status == "completed"),
            "instances": {
                inst_id: self.get_instance_status(inst_id)
                for inst_id in self.instances
            }
        }

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Detect potential conflicts between instances.

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Check for duplicate work
        task_assignments = {}
        for task_id, task in self.tasks.items():
            if task.assigned_to is not None:
                key = task.description.lower()
                if key in task_assignments:
                    conflicts.append({
                        "type": "duplicate_work",
                        "task1": task_id,
                        "task2": task_assignments[key],
                        "description": task.description
                    })
                else:
                    task_assignments[key] = task_id

        return conflicts

    async def coordinate_instances(self):
        """
        Continuous coordination loop.

        Monitors instances, assigns tasks, resolves conflicts.
        """
        logger.info("Starting instance coordination loop")

        while True:
            try:
                # Auto-assign pending tasks
                self.auto_assign_tasks()

                # Detect and resolve conflicts
                conflicts = self.detect_conflicts()
                if conflicts:
                    logger.warning(f"Detected {len(conflicts)} conflicts")
                    # TODO: Implement conflict resolution

                # Update shared state
                self._update_shared_state()

                # Wait before next iteration
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(10)
