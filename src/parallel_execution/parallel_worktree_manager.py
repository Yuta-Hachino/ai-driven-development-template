"""
Parallel Worktree Manager

Extends WorktreeManager to support multiple Claude Code instances
working in parallel across different worktrees.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from worktree import WorktreeManager, WorktreeConfig, DevelopmentPattern
from .multi_instance_manager import MultiInstanceManager, InstanceConfig

logger = logging.getLogger(__name__)


class ParallelWorktreeManager(WorktreeManager):
    """
    Enhanced WorktreeManager for parallel multi-instance development.

    Extends the base WorktreeManager with:
    - Instance-to-worktree mapping
    - Resource allocation across instances
    - Coordination between instances
    - Conflict prevention
    """

    def __init__(
        self,
        repo_path: str,
        config: Optional[Dict] = None,
        instance_manager: Optional[MultiInstanceManager] = None
    ):
        super().__init__(repo_path, config)

        self.instance_manager = instance_manager or MultiInstanceManager(config)
        self.instance_worktrees: Dict[int, List[str]] = {}  # instance_id -> worktree names
        self.worktree_locks: Dict[str, int] = {}  # worktree_name -> instance_id

    def assign_worktree_to_instance(
        self,
        worktree_name: str,
        instance_id: int
    ) -> bool:
        """
        Assign a worktree to a specific instance.

        Args:
            worktree_name: Worktree to assign
            instance_id: Instance to assign to

        Returns:
            True if assignment successful
        """
        # Check if worktree exists
        if worktree_name not in self.worktrees:
            logger.error(f"Worktree {worktree_name} not found")
            return False

        # Check if already locked
        if worktree_name in self.worktree_locks:
            current_owner = self.worktree_locks[worktree_name]
            logger.warning(
                f"Worktree {worktree_name} already locked by instance {current_owner}"
            )
            return False

        # Assign worktree
        self.worktree_locks[worktree_name] = instance_id

        if instance_id not in self.instance_worktrees:
            self.instance_worktrees[instance_id] = []

        self.instance_worktrees[instance_id].append(worktree_name)

        logger.info(f"Assigned worktree {worktree_name} to instance {instance_id}")

        return True

    def release_worktree(self, worktree_name: str) -> bool:
        """
        Release a worktree lock.

        Args:
            worktree_name: Worktree to release

        Returns:
            True if successful
        """
        if worktree_name not in self.worktree_locks:
            return False

        instance_id = self.worktree_locks[worktree_name]
        del self.worktree_locks[worktree_name]

        if instance_id in self.instance_worktrees:
            if worktree_name in self.instance_worktrees[instance_id]:
                self.instance_worktrees[instance_id].remove(worktree_name)

        logger.info(f"Released worktree {worktree_name}")

        return True

    def create_parallel_worktrees_for_instances(
        self,
        feature: str,
        num_instances: int,
        pattern: DevelopmentPattern = DevelopmentPattern.PARALLEL
    ) -> List[Dict[str, any]]:
        """
        Create multiple worktrees for parallel instance execution.

        Args:
            feature: Feature name
            num_instances: Number of instances
            pattern: Development pattern

        Returns:
            List of dicts with worktree info and assigned instance
        """
        worktrees_created = []

        for i in range(num_instances):
            instance_id = i + 1

            # Register instance if not already registered
            if instance_id not in self.instance_manager.instances:
                instance_config = InstanceConfig(
                    instance_id=instance_id,
                    name=f"claude_code_{instance_id}",
                    worktree_path="",  # Will be set after worktree creation
                    specialization=[]
                )
                self.instance_manager.register_instance(instance_config)

            # Create worktree
            config = WorktreeConfig(
                pattern=pattern,
                name=f"{pattern.value}-{feature}-instance{instance_id}",
                branch=f"{pattern.value}/{feature}/instance{instance_id}",
                agent=f"claude_code_{instance_id}",
                feature=feature
            )

            try:
                worktree_info = self.create_worktree(config)

                # Update instance config with worktree path
                self.instance_manager.instances[instance_id].worktree_path = worktree_info.path

                # Assign worktree to instance
                self.assign_worktree_to_instance(worktree_info.name, instance_id)

                worktrees_created.append({
                    "worktree": worktree_info,
                    "instance_id": instance_id,
                    "status": "created"
                })

                logger.info(
                    f"Created worktree {worktree_info.name} for instance {instance_id}"
                )

            except Exception as e:
                logger.error(f"Failed to create worktree for instance {instance_id}: {e}")
                worktrees_created.append({
                    "instance_id": instance_id,
                    "status": "failed",
                    "error": str(e)
                })

        return worktrees_created

    async def sync_all_instance_worktrees(self) -> Dict[int, bool]:
        """
        Sync all worktrees assigned to instances.

        Returns:
            Dict mapping instance_id to sync success status
        """
        results = {}

        for instance_id, worktree_names in self.instance_worktrees.items():
            instance_results = []

            for worktree_name in worktree_names:
                success = self.sync_worktree(worktree_name)
                instance_results.append(success)

            results[instance_id] = all(instance_results)

        return results

    def get_instance_worktrees(self, instance_id: int) -> List[str]:
        """Get all worktrees assigned to an instance"""
        return self.instance_worktrees.get(instance_id, [])

    def check_worktree_conflicts(self) -> List[Dict]:
        """
        Check for conflicts between worktrees.

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Check for overlapping file modifications
        # This is a simplified check - real implementation would
        # compare actual file changes

        worktree_statuses = {}
        for name in self.worktrees:
            status = self.get_worktree_status(name)
            if status and status.get("has_changes"):
                worktree_statuses[name] = status

        # Check if multiple worktrees are modifying same files
        # (Simplified - actual implementation would parse git status)

        return conflicts

    def create_competition_worktrees_parallel(
        self,
        feature: str,
        num_competitors: int = 5
    ) -> List[Dict]:
        """
        Create competition worktrees for parallel execution.

        Each instance gets its own worktree to solve the same problem.

        Args:
            feature: Feature/problem to solve
            num_competitors: Number of competing instances

        Returns:
            List of created worktrees with assignments
        """
        return self.create_parallel_worktrees_for_instances(
            feature=feature,
            num_instances=num_competitors,
            pattern=DevelopmentPattern.COMPETITION
        )

    def get_parallel_metrics(self) -> Dict:
        """
        Get metrics for parallel execution.

        Returns:
            Dict of metrics
        """
        base_metrics = self.get_metrics()

        parallel_metrics = {
            **base_metrics,
            "total_instances": len(self.instance_worktrees),
            "active_instances": sum(
                1 for worktrees in self.instance_worktrees.values()
                if len(worktrees) > 0
            ),
            "locked_worktrees": len(self.worktree_locks),
            "instance_distribution": {
                inst_id: len(worktrees)
                for inst_id, worktrees in self.instance_worktrees.items()
            }
        }

        return parallel_metrics

    async def coordinate_parallel_development(
        self,
        feature: str,
        tasks: List[str],
        num_instances: int = 3
    ) -> Dict:
        """
        Coordinate parallel development across multiple instances.

        Args:
            feature: Feature being developed
            tasks: List of task descriptions
            num_instances: Number of instances to use

        Returns:
            Coordination results
        """
        logger.info(
            f"Starting parallel development: {feature} "
            f"with {num_instances} instances"
        )

        # Create worktrees
        worktrees = self.create_parallel_worktrees_for_instances(
            feature=feature,
            num_instances=num_instances
        )

        # Create tasks in instance manager
        created_tasks = []
        for task_desc in tasks:
            from .multi_instance_manager import TaskPriority
            task = self.instance_manager.create_task(
                description=task_desc,
                priority=TaskPriority.MEDIUM
            )
            created_tasks.append(task)

        # Auto-assign tasks
        assignments = self.instance_manager.auto_assign_tasks()

        logger.info(f"Assigned {len(assignments)} tasks to instances")

        return {
            "feature": feature,
            "worktrees_created": len([w for w in worktrees if w["status"] == "created"]),
            "tasks_created": len(created_tasks),
            "tasks_assigned": len(assignments),
            "instances_active": num_instances,
            "worktrees": worktrees,
            "assignments": assignments
        }
