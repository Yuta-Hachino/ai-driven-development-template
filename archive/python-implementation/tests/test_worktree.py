"""
Tests for Worktree Management System
"""

import pytest
from pathlib import Path
from src.worktree.manager import (
    WorktreeManager,
    WorktreeConfig,
    DevelopmentPattern,
)
from src.worktree.evaluation import EvaluationSystem, MetricType


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary git repository"""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    return repo_path


@pytest.fixture
def worktree_config():
    """Worktree configuration"""
    return WorktreeConfig(
        pattern=DevelopmentPattern.PARALLEL,
        name="test-worktree",
        branch="test-branch",
        agent="test_agent",
        feature="test_feature",
    )


def test_worktree_manager_creation(temp_repo):
    """Test worktree manager creation"""
    manager = WorktreeManager(str(temp_repo))

    assert manager.repo_path == temp_repo
    assert isinstance(manager.worktrees, dict)


def test_development_pattern_enum():
    """Test development pattern enumeration"""
    assert DevelopmentPattern.COMPETITION.value == "competition"
    assert DevelopmentPattern.PARALLEL.value == "parallel"
    assert DevelopmentPattern.AB_TEST.value == "ab-test"
    assert DevelopmentPattern.ROLE_BASED.value == "role-based"
    assert DevelopmentPattern.BRANCH_TREE.value == "branch-tree"


def test_worktree_name_generation(temp_repo):
    """Test worktree name generation"""
    manager = WorktreeManager(str(temp_repo))

    name = manager._generate_worktree_name(
        DevelopmentPattern.COMPETITION,
        "agent1",
        "feature-x"
    )

    assert "competition" in name
    assert "agent1" in name
    assert "feature-x" in name
    assert len(name) <= 100


def test_worktree_metrics(temp_repo):
    """Test worktree metrics"""
    manager = WorktreeManager(str(temp_repo))

    metrics = manager.get_metrics()

    assert "total_worktrees" in metrics
    assert "patterns" in metrics
    assert metrics["total_worktrees"] == 0


@pytest.mark.asyncio
async def test_evaluation_system():
    """Test evaluation system"""
    eval_system = EvaluationSystem()

    assert MetricType.PERFORMANCE in eval_system.metrics
    assert MetricType.CODE_QUALITY in eval_system.metrics
    assert MetricType.SECURITY in eval_system.metrics


@pytest.mark.asyncio
async def test_performance_evaluation(tmp_path):
    """Test performance evaluation"""
    eval_system = EvaluationSystem()

    score = await eval_system.evaluate_performance(tmp_path)

    assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_code_quality_evaluation(tmp_path):
    """Test code quality evaluation"""
    eval_system = EvaluationSystem()

    score = await eval_system.evaluate_code_quality(tmp_path)

    assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_security_evaluation(tmp_path):
    """Test security evaluation"""
    eval_system = EvaluationSystem()

    score = await eval_system.evaluate_security(tmp_path)

    assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_worktree_evaluation(tmp_path):
    """Test full worktree evaluation"""
    eval_system = EvaluationSystem()

    result = await eval_system.evaluate_worktree(tmp_path, "test-worktree")

    assert result.worktree_name == "test-worktree"
    assert 0 <= result.overall_score <= 100
    assert "performance" in result.metric_scores
    assert "code_quality" in result.metric_scores


def test_evaluation_report_generation(tmp_path):
    """Test evaluation report generation"""
    from src.worktree.evaluation import EvaluationResult

    result = EvaluationResult(
        worktree_name="test",
        overall_score=85.5,
        metric_scores={"performance": 90, "quality": 80},
        passed=True,
    )

    eval_system = EvaluationSystem()
    report = eval_system.generate_report(result)

    assert "test" in report
    assert "85.5" in report
    assert "PASSED" in report
