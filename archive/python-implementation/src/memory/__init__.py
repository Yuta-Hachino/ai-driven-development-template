"""
Memory Module

Provides project memory and context management for Claude Code instances.
Enables knowledge sharing and onboarding of new instances.
"""

from .project_memory import ProjectMemory, MemoryEntry, KnowledgeType

__all__ = [
    "ProjectMemory",
    "MemoryEntry",
    "KnowledgeType",
]

__version__ = "0.1.0"
