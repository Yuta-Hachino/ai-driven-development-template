"""
Parallel Execution Module

Manages multiple Claude Code instances working in parallel across Git worktrees.
Enables collaborative development with instance coordination.
"""

from .multi_instance_manager import (
    MultiInstanceManager,
    InstanceConfig,
    InstanceStatus,
    CoordinationMessage,
)
from .parallel_worktree_manager import ParallelWorktreeManager

__all__ = [
    "MultiInstanceManager",
    "InstanceConfig",
    "InstanceStatus",
    "CoordinationMessage",
    "ParallelWorktreeManager",
]

__version__ = "0.1.0"
