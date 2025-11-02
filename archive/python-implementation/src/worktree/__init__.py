"""
Git Worktree Management System

Implements the 5 development patterns using Git worktrees:
- Competition Resolution
- Parallel Development
- A/B Testing
- Role-based Specialization
- Branch Tree Exploration
"""

from .manager import WorktreeManager, WorktreeConfig, WorktreeInfo
from .evaluation import EvaluationSystem, EvaluationResult

__all__ = [
    "WorktreeManager",
    "WorktreeConfig",
    "WorktreeInfo",
    "EvaluationSystem",
    "EvaluationResult",
]

__version__ = "0.1.0"
