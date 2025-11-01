"""
Project Memory System

Maintains project context, decisions, and learnings for Claude Code instances.
New instances can quickly onboard by reading the project memory.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class KnowledgeType(Enum):
    """Types of knowledge stored in project memory"""
    ARCHITECTURE = "architecture"
    DECISION = "decision"
    PATTERN = "pattern"
    LEARNING = "learning"
    FAILURE = "failure"
    SUCCESS = "success"
    CONVENTION = "convention"
    DEPENDENCY = "dependency"


@dataclass
class MemoryEntry:
    """Single entry in project memory"""
    entry_id: str
    knowledge_type: KnowledgeType
    title: str
    content: str
    created_by: str  # Instance or person who created it
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectMemory:
    """
    Manages project memory and context.

    Features:
    - Store and retrieve project decisions
    - Document architectural patterns
    - Record successes and failures
    - Provide onboarding information
    - Share knowledge between instances
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / "docs" / "project_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.context_file = self.project_root / "docs" / "PROJECT_CONTEXT.md"
        self.memory_index_file = self.memory_dir / "memory_index.json"

        self.entries: Dict[str, MemoryEntry] = {}
        self._load_memory()

    def _load_memory(self):
        """Load existing memory entries"""
        if self.memory_index_file.exists():
            try:
                with open(self.memory_index_file, 'r') as f:
                    data = json.load(f)

                for entry_data in data.get("entries", []):
                    entry = MemoryEntry(
                        entry_id=entry_data["entry_id"],
                        knowledge_type=KnowledgeType(entry_data["knowledge_type"]),
                        title=entry_data["title"],
                        content=entry_data["content"],
                        created_by=entry_data["created_by"],
                        created_at=datetime.fromisoformat(entry_data["created_at"]),
                        tags=entry_data.get("tags", []),
                        related_files=entry_data.get("related_files", []),
                        metadata=entry_data.get("metadata", {})
                    )
                    self.entries[entry.entry_id] = entry

                logger.info(f"Loaded {len(self.entries)} memory entries")

            except Exception as e:
                logger.error(f"Failed to load memory: {e}")

    def add_entry(
        self,
        knowledge_type: KnowledgeType,
        title: str,
        content: str,
        created_by: str,
        tags: Optional[List[str]] = None,
        related_files: Optional[List[str]] = None
    ) -> MemoryEntry:
        """
        Add new entry to project memory.

        Args:
            knowledge_type: Type of knowledge
            title: Entry title
            content: Entry content
            created_by: Creator identifier
            tags: Optional tags
            related_files: Optional related files

        Returns:
            Created MemoryEntry
        """
        entry_id = f"{knowledge_type.value}_{int(datetime.now().timestamp())}"

        entry = MemoryEntry(
            entry_id=entry_id,
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            created_by=created_by,
            tags=tags or [],
            related_files=related_files or []
        )

        self.entries[entry_id] = entry

        # Save to disk
        self._save_memory()

        logger.info(f"Added memory entry: {title} [{knowledge_type.value}]")

        return entry

    def get_entries_by_type(
        self,
        knowledge_type: KnowledgeType
    ) -> List[MemoryEntry]:
        """Get all entries of a specific type"""
        return [
            entry for entry in self.entries.values()
            if entry.knowledge_type == knowledge_type
        ]

    def search_entries(
        self,
        query: str,
        knowledge_type: Optional[KnowledgeType] = None
    ) -> List[MemoryEntry]:
        """
        Search entries by query string.

        Args:
            query: Search query
            knowledge_type: Optional filter by type

        Returns:
            List of matching entries
        """
        query_lower = query.lower()
        results = []

        for entry in self.entries.values():
            # Filter by type if specified
            if knowledge_type and entry.knowledge_type != knowledge_type:
                continue

            # Search in title, content, and tags
            if (query_lower in entry.title.lower() or
                query_lower in entry.content.lower() or
                any(query_lower in tag.lower() for tag in entry.tags)):
                results.append(entry)

        return results

    def _save_memory(self):
        """Save memory index to disk"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "entries": [
                {
                    **asdict(entry),
                    "knowledge_type": entry.knowledge_type.value,
                    "created_at": entry.created_at.isoformat()
                }
                for entry in self.entries.values()
            ]
        }

        with open(self.memory_index_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_onboarding_doc(self) -> str:
        """
        Generate onboarding document for new instances.

        Returns:
            Markdown formatted onboarding document
        """
        sections = []

        sections.append("# Project Onboarding - Autonomous Development System\n")
        sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Architecture
        arch_entries = self.get_entries_by_type(KnowledgeType.ARCHITECTURE)
        if arch_entries:
            sections.append("\n## 🏗️ Architecture\n")
            for entry in arch_entries:
                sections.append(f"### {entry.title}\n")
                sections.append(f"{entry.content}\n")

        # Conventions
        convention_entries = self.get_entries_by_type(KnowledgeType.CONVENTION)
        if convention_entries:
            sections.append("\n## 📋 Conventions & Standards\n")
            for entry in convention_entries:
                sections.append(f"### {entry.title}\n")
                sections.append(f"{entry.content}\n")

        # Patterns
        pattern_entries = self.get_entries_by_type(KnowledgeType.PATTERN)
        if pattern_entries:
            sections.append("\n## 🎨 Implementation Patterns\n")
            for entry in pattern_entries:
                sections.append(f"### {entry.title}\n")
                sections.append(f"{entry.content}\n")
                if entry.related_files:
                    sections.append("\n**Related Files:**\n")
                    for file in entry.related_files:
                        sections.append(f"- `{file}`\n")

        # Decisions
        decision_entries = self.get_entries_by_type(KnowledgeType.DECISION)
        if decision_entries:
            sections.append("\n## 💡 Key Decisions\n")
            for entry in decision_entries:
                sections.append(f"### {entry.title}\n")
                sections.append(f"{entry.content}\n")
                sections.append(f"\n*Decided by: {entry.created_by} on {entry.created_at.strftime('%Y-%m-%d')}*\n")

        # Learnings
        learning_entries = self.get_entries_by_type(KnowledgeType.LEARNING)
        if learning_entries:
            sections.append("\n## 📚 Learnings & Best Practices\n")
            for entry in learning_entries:
                sections.append(f"### {entry.title}\n")
                sections.append(f"{entry.content}\n")

        # Failures (what to avoid)
        failure_entries = self.get_entries_by_type(KnowledgeType.FAILURE)
        if failure_entries:
            sections.append("\n## ⚠️ Known Issues & What to Avoid\n")
            for entry in failure_entries:
                sections.append(f"### {entry.title}\n")
                sections.append(f"{entry.content}\n")

        return "\n".join(sections)

    def update_project_context(self):
        """Update PROJECT_CONTEXT.md with latest information"""
        context = self.generate_onboarding_doc()

        # Add project overview if not in memory
        if not any(e.knowledge_type == KnowledgeType.ARCHITECTURE for e in self.entries.values()):
            overview = self._generate_project_overview()
            context = overview + "\n\n" + context

        with open(self.context_file, 'w') as f:
            f.write(context)

        logger.info(f"Updated PROJECT_CONTEXT.md")

    def _generate_project_overview(self) -> str:
        """Generate project overview section"""
        return """# Autonomous Development Repository System

## Project Overview

This is an enterprise-grade autonomous development system that combines:
- **Google ADK** - Multi-agent framework
- **Git Worktrees** - 5 parallel development patterns
- **Enterprise Security** - Zero-trust architecture with gVisor
- **Self-Healing** - Automatic failure detection and recovery
- **Multi-Instance** - Parallel Claude Code execution

## Technology Stack

- **Language**: Python 3.11+
- **Agents**: Google ADK with Claude Code API
- **Infrastructure**: GCP, Kubernetes, Docker
- **CI/CD**: GitHub Actions
- **Security**: gVisor, AES-256-GCM, OAuth 2.0, MFA

## Quick Start for New Instance

1. Read this document thoroughly
2. Review `config/` files for system configuration
3. Check `src/` for implementation structure
4. Run tests: `pytest tests/`
5. Review recent commits and PRs
"""

    def record_decision(
        self,
        title: str,
        decision: str,
        rationale: str,
        decided_by: str,
        alternatives: Optional[List[str]] = None
    ) -> MemoryEntry:
        """
        Record an architectural or technical decision.

        Args:
            title: Decision title
            decision: What was decided
            rationale: Why it was decided
            decided_by: Who decided
            alternatives: Alternatives considered

        Returns:
            Created MemoryEntry
        """
        content = f"""**Decision**: {decision}

**Rationale**: {rationale}
"""

        if alternatives:
            content += "\n**Alternatives Considered**:\n"
            for alt in alternatives:
                content += f"- {alt}\n"

        return self.add_entry(
            knowledge_type=KnowledgeType.DECISION,
            title=title,
            content=content,
            created_by=decided_by,
            tags=["decision", "adr"]
        )

    def record_pattern(
        self,
        title: str,
        description: str,
        example: str,
        when_to_use: str,
        created_by: str,
        related_files: Optional[List[str]] = None
    ) -> MemoryEntry:
        """
        Record an implementation pattern.

        Args:
            title: Pattern name
            description: Pattern description
            example: Code example
            when_to_use: When to use this pattern
            created_by: Creator
            related_files: Related files

        Returns:
            Created MemoryEntry
        """
        content = f"""{description}

**When to Use**: {when_to_use}

**Example**:
```python
{example}
```
"""

        return self.add_entry(
            knowledge_type=KnowledgeType.PATTERN,
            title=title,
            content=content,
            created_by=created_by,
            related_files=related_files or [],
            tags=["pattern", "implementation"]
        )

    def record_learning(
        self,
        title: str,
        what_happened: str,
        what_learned: str,
        action_items: List[str],
        created_by: str
    ) -> MemoryEntry:
        """
        Record a learning or post-mortem.

        Args:
            title: Learning title
            what_happened: What occurred
            what_learned: Lessons learned
            action_items: Action items
            created_by: Creator

        Returns:
            Created MemoryEntry
        """
        content = f"""**What Happened**: {what_happened}

**What We Learned**: {what_learned}

**Action Items**:
"""
        for item in action_items:
            content += f"- {item}\n"

        return self.add_entry(
            knowledge_type=KnowledgeType.LEARNING,
            title=title,
            content=content,
            created_by=created_by,
            tags=["learning", "retrospective"]
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of project memory"""
        by_type = {}
        for knowledge_type in KnowledgeType:
            entries = self.get_entries_by_type(knowledge_type)
            by_type[knowledge_type.value] = len(entries)

        return {
            "total_entries": len(self.entries),
            "by_type": by_type,
            "last_updated": max(
                (e.created_at for e in self.entries.values()),
                default=None
            )
        }
