"""
E2E Test Configuration and Fixtures

Provides test fixtures and setup for end-to-end testing of the
autonomous development system.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents import FrontendAgent, BackendAgent, AgentConfig
from worktree import WorktreeManager, WorktreeConfig
from parallel_execution import MultiInstanceManager, InstanceConfig
from memory import ProjectMemory
from management import TechLeadSystem, TaskPlanner
from monitoring import NotificationHub
from security import DataEncryption, AuditLogger


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary git repository for testing"""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    import subprocess
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)

    # Create initial commit
    (repo_path / "README.md").write_text("# Test Repository")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

    yield repo_path

    # Cleanup
    shutil.rmtree(repo_path, ignore_errors=True)


@pytest.fixture
def agent_config():
    """Create test agent configuration"""
    return AgentConfig(
        name="test_agent",
        model="claude-3-sonnet",
        specialization=["testing"],
        max_tokens=1000,
        timeout=30
    )


@pytest.fixture
def frontend_agent(agent_config):
    """Create frontend agent for testing"""
    config = agent_config
    config.name = "frontend_test"
    config.specialization = ["frontend", "react", "typescript"]
    return FrontendAgent(config)


@pytest.fixture
def backend_agent(agent_config):
    """Create backend agent for testing"""
    config = agent_config
    config.name = "backend_test"
    config.specialization = ["backend", "api", "database"]
    return BackendAgent(config)


@pytest.fixture
def worktree_manager(temp_repo):
    """Create worktree manager for testing"""
    config = {
        "max_parallel": 5,
        "cleanup_after_days": 1
    }
    return WorktreeManager(str(temp_repo), config)


@pytest.fixture
def multi_instance_manager():
    """Create multi-instance manager for testing"""
    return MultiInstanceManager()


@pytest.fixture
def project_memory(temp_repo):
    """Create project memory for testing"""
    return ProjectMemory(str(temp_repo))


@pytest.fixture
def tech_lead_system(temp_repo):
    """Create tech lead system for testing"""
    return TechLeadSystem(str(temp_repo))


@pytest.fixture
def task_planner():
    """Create task planner for testing"""
    return TaskPlanner()


@pytest.fixture
def notification_hub(temp_repo):
    """Create notification hub for testing"""
    return NotificationHub(str(temp_repo))


@pytest.fixture
def test_instances():
    """Create test Claude Code instances"""
    instances = []
    for i in range(1, 4):
        instance = InstanceConfig(
            instance_id=i,
            name=f"Test-Instance-{i}",
            capabilities=["backend", "frontend", "testing"],
            status="active",
            max_concurrent_tasks=2
        )
        instances.append(instance)
    return instances


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing"""
    from management import TaskBreakdown

    tasks = [
        TaskBreakdown(
            task_id="task-1",
            title="Implement user authentication",
            description="Build OAuth 2.0 authentication",
            estimated_hours=10.0,
            required_skills=["backend", "security"],
            priority=10
        ),
        TaskBreakdown(
            task_id="task-2",
            title="Create login UI",
            description="Build login form component",
            estimated_hours=6.0,
            required_skills=["frontend", "ui"],
            dependencies=["task-1"],
            priority=9
        ),
        TaskBreakdown(
            task_id="task-3",
            title="Write authentication tests",
            description="Unit and integration tests",
            estimated_hours=8.0,
            required_skills=["testing"],
            dependencies=["task-1", "task-2"],
            priority=8
        )
    ]
    return tasks


@pytest.fixture
def mock_task_results():
    """Mock task execution results"""
    return {
        "task-1": {
            "success": True,
            "completion_time": 9.5,
            "quality_score": 0.92,
            "files_changed": ["src/auth.py", "tests/test_auth.py"]
        },
        "task-2": {
            "success": True,
            "completion_time": 5.8,
            "quality_score": 0.88,
            "files_changed": ["src/components/Login.tsx"]
        },
        "task-3": {
            "success": True,
            "completion_time": 7.2,
            "quality_score": 0.95,
            "files_changed": ["tests/integration/test_auth_flow.py"]
        }
    }


@pytest.fixture
def encryption_service():
    """Create encryption service for testing"""
    return DataEncryption()


@pytest.fixture
def audit_logger(temp_repo):
    """Create audit logger for testing"""
    return AuditLogger(str(temp_repo))


# Helper functions for tests

def create_test_file(repo_path: Path, file_path: str, content: str) -> Path:
    """Create a test file in repository"""
    full_path = repo_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)
    return full_path


def commit_changes(repo_path: Path, message: str) -> None:
    """Commit changes in test repository"""
    import subprocess
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)


async def wait_for_condition(condition_fn, timeout=10, interval=0.1):
    """Wait for a condition to become true"""
    import time
    start_time = time.time()

    while time.time() - start_time < timeout:
        if await condition_fn() if asyncio.iscoroutinefunction(condition_fn) else condition_fn():
            return True
        await asyncio.sleep(interval)

    return False


# Pytest configuration

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add e2e marker to all tests in e2e directory
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
