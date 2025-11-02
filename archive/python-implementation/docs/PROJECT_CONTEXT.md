# Project Onboarding - Autonomous Development System

Generated: 2025-01-15

## 🏗️ Project Overview

This is an enterprise-grade **Autonomous Development Repository System** that enables multiple Claude Code instances to work collaboratively on software development tasks.

### Core Components

1. **Multi-Agent Framework** (`src/agents/`)
   - Development agents: Frontend, Backend, Algorithm, DevOps
   - Management agents: Approval, Security, Integration
   - Based on Google ADK patterns

2. **Git Worktree Patterns** (`src/worktree/`)
   - Competition: Multiple solutions, best wins
   - Parallel: Different features simultaneously
   - A/B Testing: Compare implementations
   - Role-Based: Specialized agents
   - Branch Tree: Exploratory development

3. **Enterprise Security** (`src/security/`)
   - AES-256-GCM encryption
   - OAuth 2.0 + MFA authentication
   - RBAC authorization
   - Tamper-proof audit logging

4. **Autonomous Self-Healing** (`src/autonomous/`)
   - Automatic failure detection
   - AI-powered failure analysis
   - Auto-fix strategies
   - GitHub Actions integration

5. **Multi-Instance Coordination** (`src/parallel_execution/`)
   - Parallel instance management
   - Task distribution
   - Inter-instance communication
   - Resource coordination

6. **Project Memory** (`src/memory/`)
   - Context preservation
   - Knowledge sharing
   - Decision records
   - Pattern catalog

## 📋 Technology Stack

- **Language**: Python 3.11+
- **AI**: Claude Code API (Anthropic)
- **Framework**: Google ADK
- **Infrastructure**: GCP, Kubernetes (GKE), Docker
- **Runtime**: gVisor sandboxes
- **CI/CD**: GitHub Actions
- **Storage**: Google Cloud Storage, Secret Manager
- **Monitoring**: Cloud Monitoring, Logging

## 🚀 Quick Start for New Claude Code Instance

### 1. Read This Document First

You are a Claude Code instance joining an ongoing development project. This document contains essential context.

### 2. Understand Your Role

You will be assigned to work in a specific Git worktree on specific tasks. You coordinate with other instances through:
- GitHub Issues (shared communication)
- Shared files in `docs/shared_knowledge/`
- Project Memory system

### 3. Check Your Assignment

```python
# Your instance will be registered with an ID
# Check: docs/shared_knowledge/shared_state.json
# Find your assigned tasks and worktree
```

### 4. Review Recent Context

- Check `docs/shared_knowledge/coordination_messages.jsonl` for recent communications
- Review `docs/project_memory/memory_index.json` for decisions and patterns
- Read recent commits: `git log --oneline -20`

### 5. Key Files to Review

**Configuration**:
- `config/agents.yaml` - Agent configurations
- `config/security.yaml` - Security policies
- `config/worktree.yaml` - Worktree patterns
- `config/parallel_execution.yaml` - Multi-instance settings

**Core Implementation**:
- `src/agents/` - Agent framework
- `src/worktree/` - Worktree management
- `src/parallel_execution/` - Multi-instance coordination
- `src/autonomous/` - Self-healing system

**Tests**:
- `tests/` - Test suite (90%+ coverage required)

## 📐 Architecture Decisions

### Decision: Use Google ADK for Agent Framework

**Rationale**: Google ADK provides production-ready patterns for multi-agent systems with built-in security and scalability.

**Date**: 2025-01-14

### Decision: Git Worktree for Parallel Development

**Rationale**: Git worktrees allow multiple instances to work on different branches simultaneously without repository cloning overhead.

**Date**: 2025-01-14

### Decision: gVisor for Container Security

**Rationale**: gVisor provides kernel-level isolation for enhanced security in multi-tenant environments.

**Date**: 2025-01-14

### Decision: GitHub Issues for Inter-Instance Communication

**Rationale**: Persistent, queryable, and accessible. Provides audit trail and integrates with workflow.

**Date**: 2025-01-15

## 🎨 Implementation Patterns

### Pattern: Agent Base Class Extension

All specialized agents inherit from `BaseAgent`:

```python
class CustomAgent(BaseAgent):
    async def process(self, task):
        # Your implementation
        return result
```

**When to Use**: Creating new agent types

**Related Files**: `src/agents/base_agent.py`

### Pattern: Worktree Lifecycle Management

```python
manager = ParallelWorktreeManager(repo_path)
worktree = manager.create_worktree(config)
# ... work in worktree ...
manager.release_worktree(worktree.name)
```

**When to Use**: Managing instance-specific worktrees

**Related Files**: `src/parallel_execution/parallel_worktree_manager.py`

### Pattern: Inter-Instance Communication

```python
# Send message to other instances
message = CoordinationMessage(
    from_instance=my_id,
    to_instance=None,  # broadcast
    message_type="task_complete",
    content={"task_id": task_id}
)
manager.send_message(message)
```

**When to Use**: Coordinating with other instances

## 📚 Coding Conventions

### Python Style
- Follow PEP 8
- Use type hints
- Black for formatting (line length: 88)
- isort for imports
- Docstrings for all public functions

### Testing
- Minimum 90% coverage
- Use pytest
- Async tests need `@pytest.mark.asyncio`
- Mock external services

### Security
- Never hardcode secrets
- Use Secret Manager for credentials
- All user input must be validated
- Run security scans before commit

### Git Commits
Format: `type(scope): description`

Types: feat, fix, docs, style, refactor, test, chore

Example: `feat(parallel): Add multi-instance coordinator`

## ⚠️ What to Avoid

### Don't: Modify Security Configurations Without Review

Security configurations require manual review. Never auto-fix security vulnerabilities.

### Don't: Work Outside Your Assigned Worktree

Each instance has a dedicated worktree. Working in another instance's worktree causes conflicts.

### Don't: Merge Without Running Tests

All merges require passing tests and security scans. CI/CD enforces this.

### Don't: Ignore Coordination Messages

Check for messages from other instances regularly. Ignoring coordination can cause duplicate work.

## 🔄 Workflow

### Your Typical Workflow

1. **Check Assignment**: Read your assigned tasks from shared state
2. **Claim Task**: Send `task_claim` message
3. **Switch to Worktree**: `cd` to your assigned worktree
4. **Implement**: Write code, tests, documentation
5. **Test**: Run `pytest` locally
6. **Commit**: Follow commit conventions
7. **Notify**: Send `task_complete` message
8. **Create PR**: Auto-created by system or manual
9. **Wait for Review**: Approval agent or human review
10. **Merge**: Automated if all checks pass

### Communication Protocol

- **Task Claim**: Notify before starting work
- **Progress Update**: Every 30 minutes for long tasks
- **Blocked**: Immediately notify if blocked
- **Complete**: Notify with results when done
- **Help Request**: Ask for help if stuck

## 💡 Best Practices

### For Efficient Collaboration

1. **Check Shared State First**: Avoid duplicate work
2. **Communicate Early**: Notify intentions before starting
3. **Document Decisions**: Add to Project Memory
4. **Share Learnings**: Record failures and successes
5. **Respect Locks**: Don't modify locked resources
6. **Update Context**: Keep PROJECT_CONTEXT.md current

### For Code Quality

1. **Write Tests First**: TDD approach
2. **Small Commits**: Atomic, reviewable changes
3. **Clear Documentation**: Explain why, not what
4. **Security First**: Think security at every step
5. **Performance Matters**: Profile before optimizing

## 📊 Success Metrics

Your contributions are measured by:
- **Code Quality**: SonarQube score ≥ 80
- **Test Coverage**: ≥ 90%
- **Security**: Zero HIGH/CRITICAL vulnerabilities
- **Efficiency**: Task completion time
- **Collaboration**: Communication quality

## 🆘 Getting Help

If you encounter issues:

1. **Check Project Memory**: Similar issues may be documented
2. **Search Shared Knowledge**: `docs/shared_knowledge/`
3. **Review Recent Messages**: Coordination messages
4. **Ask Other Instances**: Send `help_request` message
5. **Create Issue**: For blocking problems

## 🎯 Current Focus

**Phase 2.5**: Multi-Instance Collaboration Enhancement

Priority areas:
1. Parallel execution optimization
2. Inter-instance communication
3. Project memory enrichment
4. Documentation automation

---

**Welcome to the Team!** 🎉

You're now part of an autonomous development system. Follow these guidelines, communicate actively, and contribute to our collective knowledge base.

*Last Updated: 2025-01-15*
