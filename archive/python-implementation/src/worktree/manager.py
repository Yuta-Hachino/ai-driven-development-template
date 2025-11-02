"""
Worktree Manager

Manages Git worktrees for parallel development patterns.
"""

import asyncio
import os
import shutil
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

logger = logging.getLogger(__name__)


class DevelopmentPattern(Enum):
    """Development pattern types"""
    COMPETITION = "competition"
    PARALLEL = "parallel"
    AB_TEST = "ab-test"
    ROLE_BASED = "role-based"
    BRANCH_TREE = "branch-tree"


@dataclass
class WorktreeConfig:
    """Worktree configuration"""
    pattern: DevelopmentPattern
    name: str
    branch: str
    agent: str
    feature: str
    base_path: str = "../worktrees"
    auto_cleanup: bool = True
    cleanup_after_days: int = 7


@dataclass
class WorktreeInfo:
    """Worktree information"""
    name: str
    path: str
    branch: str
    pattern: DevelopmentPattern
    agent: str
    created_at: datetime
    last_commit: Optional[str] = None
    status: str = "active"


class WorktreeManager:
    """
    Manages Git worktrees for autonomous development.

    Features:
    - Create and manage multiple worktrees
    - Track worktree status and metadata
    - Automatic cleanup of old worktrees
    - Synchronization across worktrees
    - Pattern-specific workflows
    """

    def __init__(self, repo_path: str, config: Optional[Dict] = None):
        self.repo_path = Path(repo_path)
        self.config = config or {}
        self.worktrees: Dict[str, WorktreeInfo] = {}
        self.base_path = Path(self.config.get("base_path", "../worktrees"))
        self._ensure_base_path()

    def _ensure_base_path(self):
        """Ensure base worktree directory exists"""
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _run_git_command(self, command: List[str], cwd: Optional[Path] = None) -> str:
        """
        Run git command and return output.

        Args:
            command: Git command as list of strings
            cwd: Working directory (defaults to repo_path)

        Returns:
            Command output as string
        """
        cwd = cwd or self.repo_path
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e.stderr}")
            raise

    def _generate_worktree_name(
        self,
        pattern: DevelopmentPattern,
        agent: str,
        feature: str
    ) -> str:
        """Generate worktree name following naming convention"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = f"{pattern.value}-{agent}-{feature}-{timestamp}"
        # Sanitize name
        name = name.replace(" ", "-").lower()
        return name[:100]  # Enforce max length

    def create_worktree(self, config: WorktreeConfig) -> WorktreeInfo:
        """
        Create a new worktree.

        Args:
            config: Worktree configuration

        Returns:
            WorktreeInfo object
        """
        worktree_name = config.name or self._generate_worktree_name(
            config.pattern,
            config.agent,
            config.feature
        )

        worktree_path = self.base_path / worktree_name

        # Create worktree
        try:
            self._run_git_command([
                "worktree", "add",
                str(worktree_path),
                "-b", config.branch
            ])

            logger.info(f"Created worktree: {worktree_name} at {worktree_path}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create worktree: {e}")
            raise

        # Create worktree info
        worktree_info = WorktreeInfo(
            name=worktree_name,
            path=str(worktree_path),
            branch=config.branch,
            pattern=config.pattern,
            agent=config.agent,
            created_at=datetime.now(),
        )

        self.worktrees[worktree_name] = worktree_info

        return worktree_info

    def list_worktrees(self) -> List[WorktreeInfo]:
        """
        List all active worktrees.

        Returns:
            List of WorktreeInfo objects
        """
        try:
            output = self._run_git_command(["worktree", "list", "--porcelain"])

            # Parse git worktree list output
            # (This is a simplified version, production code would parse properly)
            return list(self.worktrees.values())

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list worktrees: {e}")
            return []

    def remove_worktree(self, name: str, force: bool = False) -> bool:
        """
        Remove a worktree.

        Args:
            name: Worktree name
            force: Force removal even if worktree has uncommitted changes

        Returns:
            True if successful
        """
        if name not in self.worktrees:
            logger.warning(f"Worktree not found: {name}")
            return False

        worktree_info = self.worktrees[name]

        try:
            # Remove worktree
            cmd = ["worktree", "remove", worktree_info.path]
            if force:
                cmd.append("--force")

            self._run_git_command(cmd)

            # Remove from tracking
            del self.worktrees[name]

            logger.info(f"Removed worktree: {name}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove worktree {name}: {e}")
            return False

    def sync_worktree(self, name: str) -> bool:
        """
        Sync worktree with main branch.

        Args:
            name: Worktree name

        Returns:
            True if successful
        """
        if name not in self.worktrees:
            logger.warning(f"Worktree not found: {name}")
            return False

        worktree_info = self.worktrees[name]
        worktree_path = Path(worktree_info.path)

        try:
            # Fetch latest
            self._run_git_command(["fetch", "origin"], cwd=worktree_path)

            # Rebase on main
            self._run_git_command(
                ["rebase", "origin/main"],
                cwd=worktree_path
            )

            logger.info(f"Synced worktree: {name}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sync worktree {name}: {e}")
            return False

    async def sync_all_worktrees(self) -> Dict[str, bool]:
        """
        Sync all worktrees concurrently.

        Returns:
            Dict mapping worktree name to sync success status
        """
        tasks = []
        names = []

        for name in self.worktrees:
            tasks.append(asyncio.to_thread(self.sync_worktree, name))
            names.append(name)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            name: result if not isinstance(result, Exception) else False
            for name, result in zip(names, results)
        }

    def cleanup_old_worktrees(self, days: Optional[int] = None) -> int:
        """
        Clean up worktrees older than specified days.

        Args:
            days: Number of days (defaults to config value)

        Returns:
            Number of worktrees removed
        """
        days = days or self.config.get("cleanup_after_days", 7)
        cutoff_date = datetime.now() - timedelta(days=days)

        removed_count = 0

        for name, info in list(self.worktrees.items()):
            if info.created_at < cutoff_date:
                if self.remove_worktree(name, force=True):
                    removed_count += 1

        logger.info(f"Cleaned up {removed_count} old worktrees")
        return removed_count

    def get_worktree_status(self, name: str) -> Optional[Dict]:
        """
        Get status of a worktree.

        Args:
            name: Worktree name

        Returns:
            Status dict or None if not found
        """
        if name not in self.worktrees:
            return None

        worktree_info = self.worktrees[name]
        worktree_path = Path(worktree_info.path)

        try:
            # Get git status
            status_output = self._run_git_command(
                ["status", "--porcelain"],
                cwd=worktree_path
            )

            # Get last commit
            last_commit = self._run_git_command(
                ["log", "-1", "--format=%H %s"],
                cwd=worktree_path
            )

            return {
                "name": name,
                "branch": worktree_info.branch,
                "pattern": worktree_info.pattern.value,
                "agent": worktree_info.agent,
                "has_changes": bool(status_output),
                "last_commit": last_commit,
                "created_at": worktree_info.created_at.isoformat(),
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get status for {name}: {e}")
            return None

    def merge_worktree(self, name: str, target_branch: str = "main") -> bool:
        """
        Merge worktree changes to target branch.

        Args:
            name: Worktree name
            target_branch: Target branch to merge into

        Returns:
            True if successful
        """
        if name not in self.worktrees:
            logger.warning(f"Worktree not found: {name}")
            return False

        worktree_info = self.worktrees[name]

        try:
            # Switch to target branch
            self._run_git_command(["checkout", target_branch])

            # Merge worktree branch
            self._run_git_command(["merge", worktree_info.branch])

            logger.info(
                f"Merged worktree {name} into {target_branch}"
            )
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to merge worktree {name}: {e}")
            return False

    def create_competition_worktrees(
        self,
        feature: str,
        agents: List[str],
        max_competitors: int = 5
    ) -> List[WorktreeInfo]:
        """
        Create worktrees for competition pattern.

        Args:
            feature: Feature name
            agents: List of agent names
            max_competitors: Maximum number of competitors

        Returns:
            List of created WorktreeInfo objects
        """
        worktrees = []
        agents = agents[:max_competitors]

        for i, agent in enumerate(agents):
            config = WorktreeConfig(
                pattern=DevelopmentPattern.COMPETITION,
                name="",
                branch=f"competition/{feature}/solution-{i+1}",
                agent=agent,
                feature=feature,
            )

            worktree_info = self.create_worktree(config)
            worktrees.append(worktree_info)

        logger.info(
            f"Created {len(worktrees)} competition worktrees for {feature}"
        )
        return worktrees

    def create_parallel_worktrees(
        self,
        features: List[str],
        agent_assignments: Dict[str, str]
    ) -> List[WorktreeInfo]:
        """
        Create worktrees for parallel development pattern.

        Args:
            features: List of feature names
            agent_assignments: Dict mapping feature to agent

        Returns:
            List of created WorktreeInfo objects
        """
        worktrees = []

        for feature in features:
            agent = agent_assignments.get(feature, "default_agent")

            config = WorktreeConfig(
                pattern=DevelopmentPattern.PARALLEL,
                name="",
                branch=f"feature/{feature}",
                agent=agent,
                feature=feature,
            )

            worktree_info = self.create_worktree(config)
            worktrees.append(worktree_info)

        logger.info(
            f"Created {len(worktrees)} parallel worktrees"
        )
        return worktrees

    def get_metrics(self) -> Dict:
        """
        Get worktree management metrics.

        Returns:
            Dict of metrics
        """
        pattern_counts = {}
        for info in self.worktrees.values():
            pattern = info.pattern.value
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        return {
            "total_worktrees": len(self.worktrees),
            "patterns": pattern_counts,
            "oldest_worktree": min(
                (info.created_at for info in self.worktrees.values()),
                default=None
            ),
            "newest_worktree": max(
                (info.created_at for info in self.worktrees.values()),
                default=None
            ),
        }
