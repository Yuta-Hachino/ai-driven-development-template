"""
Worktree Evaluation System

Evaluates worktrees based on multiple criteria to determine
the best implementation for merging.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import subprocess

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of evaluation metrics"""
    PERFORMANCE = "performance"
    CODE_QUALITY = "quality"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    TEST_COVERAGE = "test_coverage"


@dataclass
class EvaluationResult:
    """Result of worktree evaluation"""
    worktree_name: str
    overall_score: float
    metric_scores: Dict[str, float] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    passed: bool = True
    failures: List[str] = field(default_factory=list)


class EvaluationSystem:
    """
    Evaluates worktrees based on configurable metrics.

    Metrics:
    - Performance (benchmarks, execution time, resource usage)
    - Code Quality (linting, complexity, documentation)
    - Security (vulnerability scans, best practices)
    - Maintainability (complexity, duplication, structure)
    - Test Coverage (unit tests, integration tests)
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.metrics = {
            MetricType.PERFORMANCE: 0.30,
            MetricType.CODE_QUALITY: 0.25,
            MetricType.SECURITY: 0.25,
            MetricType.MAINTAINABILITY: 0.20,
        }

        # Override weights from config
        if "metrics" in self.config:
            for metric, weight in self.config["metrics"].items():
                if isinstance(weight, dict) and "weight" in weight:
                    metric_type = MetricType(metric)
                    self.metrics[metric_type] = weight["weight"]

    def _run_command(
        self,
        command: List[str],
        cwd: Path
    ) -> subprocess.CompletedProcess:
        """Run command in worktree directory"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {' '.join(command)}")
            raise
        except Exception as e:
            logger.error(f"Command failed: {e}")
            raise

    async def evaluate_performance(self, worktree_path: Path) -> float:
        """
        Evaluate performance metrics.

        Returns:
            Score from 0 to 100
        """
        logger.info(f"Evaluating performance for {worktree_path.name}")

        # Simulate performance benchmarking
        # In production, this would run actual benchmarks
        await asyncio.sleep(0.2)

        # Mock scores
        execution_time_score = 85
        memory_usage_score = 90
        throughput_score = 88

        # Calculate average
        score = (execution_time_score + memory_usage_score + throughput_score) / 3

        logger.info(f"Performance score: {score}")
        return score

    async def evaluate_code_quality(self, worktree_path: Path) -> float:
        """
        Evaluate code quality metrics.

        Returns:
            Score from 0 to 100
        """
        logger.info(f"Evaluating code quality for {worktree_path.name}")

        # Simulate code quality analysis
        await asyncio.sleep(0.2)

        # Mock scores from tools like SonarQube, pylint
        sonarqube_score = 87
        pylint_score = 85
        mypy_score = 90

        score = (sonarqube_score + pylint_score + mypy_score) / 3

        logger.info(f"Code quality score: {score}")
        return score

    async def evaluate_security(self, worktree_path: Path) -> float:
        """
        Evaluate security metrics.

        Returns:
            Score from 0 to 100
        """
        logger.info(f"Evaluating security for {worktree_path.name}")

        # Simulate security scanning
        await asyncio.sleep(0.2)

        # Mock vulnerability counts
        critical_vulns = 0
        high_vulns = 0
        medium_vulns = 2
        low_vulns = 5

        # Calculate score (penalize based on severity)
        score = 100
        score -= critical_vulns * 50
        score -= high_vulns * 20
        score -= medium_vulns * 5
        score -= low_vulns * 1

        score = max(0, score)

        logger.info(f"Security score: {score}")
        return score

    async def evaluate_maintainability(self, worktree_path: Path) -> float:
        """
        Evaluate maintainability metrics.

        Returns:
            Score from 0 to 100
        """
        logger.info(f"Evaluating maintainability for {worktree_path.name}")

        # Simulate maintainability analysis
        await asyncio.sleep(0.2)

        # Mock metrics
        complexity_score = 82
        duplication_score = 90
        documentation_score = 85

        score = (complexity_score + duplication_score + documentation_score) / 3

        logger.info(f"Maintainability score: {score}")
        return score

    async def evaluate_test_coverage(self, worktree_path: Path) -> float:
        """
        Evaluate test coverage.

        Returns:
            Coverage percentage (0-100)
        """
        logger.info(f"Evaluating test coverage for {worktree_path.name}")

        # Simulate test coverage analysis
        await asyncio.sleep(0.2)

        # Mock coverage
        coverage = 92.5

        logger.info(f"Test coverage: {coverage}%")
        return coverage

    async def evaluate_worktree(
        self,
        worktree_path: Path,
        worktree_name: str
    ) -> EvaluationResult:
        """
        Evaluate a worktree comprehensively.

        Args:
            worktree_path: Path to worktree
            worktree_name: Name of worktree

        Returns:
            EvaluationResult object
        """
        logger.info(f"Evaluating worktree: {worktree_name}")

        # Run evaluations concurrently
        performance_task = self.evaluate_performance(worktree_path)
        quality_task = self.evaluate_code_quality(worktree_path)
        security_task = self.evaluate_security(worktree_path)
        maintainability_task = self.evaluate_maintainability(worktree_path)
        coverage_task = self.evaluate_test_coverage(worktree_path)

        # Gather results
        performance_score = await performance_task
        quality_score = await quality_task
        security_score = await security_task
        maintainability_score = await maintainability_task
        coverage_score = await coverage_task

        # Store metric scores
        metric_scores = {
            "performance": performance_score,
            "code_quality": quality_score,
            "security": security_score,
            "maintainability": maintainability_score,
            "test_coverage": coverage_score,
        }

        # Calculate weighted overall score
        overall_score = (
            performance_score * self.metrics.get(MetricType.PERFORMANCE, 0) +
            quality_score * self.metrics.get(MetricType.CODE_QUALITY, 0) +
            security_score * self.metrics.get(MetricType.SECURITY, 0) +
            maintainability_score * self.metrics.get(MetricType.MAINTAINABILITY, 0)
        )

        # Check for failures
        failures = []
        min_coverage = self.config.get("test_coverage", {}).get("min_coverage", 90)
        if coverage_score < min_coverage:
            failures.append(
                f"Test coverage {coverage_score}% below minimum {min_coverage}%"
            )

        max_critical_vulns = self.config.get("security", {}).get(
            "max_vulnerabilities", {}
        ).get("critical", 0)
        if security_score < 50:  # Indicates critical vulnerabilities
            failures.append("Critical security vulnerabilities found")

        min_quality_score = self.config.get("code_quality", {}).get("min_score", 80)
        if quality_score < min_quality_score:
            failures.append(
                f"Code quality {quality_score} below minimum {min_quality_score}"
            )

        passed = len(failures) == 0

        result = EvaluationResult(
            worktree_name=worktree_name,
            overall_score=overall_score,
            metric_scores=metric_scores,
            details={
                "weights": {k.value: v for k, v in self.metrics.items()},
                "test_coverage": coverage_score,
            },
            passed=passed,
            failures=failures,
        )

        logger.info(
            f"Evaluation complete for {worktree_name}: "
            f"Score={overall_score:.2f}, Passed={passed}"
        )

        return result

    async def evaluate_multiple(
        self,
        worktrees: Dict[str, Path]
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple worktrees concurrently.

        Args:
            worktrees: Dict mapping worktree name to path

        Returns:
            List of EvaluationResult objects sorted by score
        """
        tasks = []

        for name, path in worktrees.items():
            tasks.append(self.evaluate_worktree(path, name))

        results = await asyncio.gather(*tasks)

        # Sort by overall score (descending)
        results.sort(key=lambda r: r.overall_score, reverse=True)

        return results

    def select_best_worktree(
        self,
        results: List[EvaluationResult]
    ) -> Optional[EvaluationResult]:
        """
        Select the best worktree from evaluation results.

        Args:
            results: List of EvaluationResult objects

        Returns:
            Best EvaluationResult or None if all failed
        """
        # Filter to passed results only
        passed_results = [r for r in results if r.passed]

        if not passed_results:
            logger.warning("No worktrees passed evaluation")
            return None

        # Results are already sorted by score
        best = passed_results[0]

        logger.info(
            f"Selected best worktree: {best.worktree_name} "
            f"with score {best.overall_score:.2f}"
        )

        return best

    def compare_worktrees(
        self,
        results: List[EvaluationResult]
    ) -> Dict[str, Any]:
        """
        Generate comparison report for worktrees.

        Args:
            results: List of EvaluationResult objects

        Returns:
            Comparison report dict
        """
        if not results:
            return {"error": "No results to compare"}

        best = max(results, key=lambda r: r.overall_score)
        worst = min(results, key=lambda r: r.overall_score)

        metric_averages = {}
        for metric in ["performance", "code_quality", "security", "maintainability"]:
            scores = [r.metric_scores.get(metric, 0) for r in results]
            metric_averages[metric] = sum(scores) / len(scores)

        return {
            "total_worktrees": len(results),
            "passed_count": sum(1 for r in results if r.passed),
            "failed_count": sum(1 for r in results if not r.passed),
            "best_worktree": {
                "name": best.worktree_name,
                "score": best.overall_score,
            },
            "worst_worktree": {
                "name": worst.worktree_name,
                "score": worst.overall_score,
            },
            "metric_averages": metric_averages,
            "score_range": {
                "min": worst.overall_score,
                "max": best.overall_score,
                "spread": best.overall_score - worst.overall_score,
            },
        }

    def generate_report(
        self,
        result: EvaluationResult
    ) -> str:
        """
        Generate detailed evaluation report.

        Args:
            result: EvaluationResult object

        Returns:
            Formatted report string
        """
        report_lines = [
            f"Evaluation Report: {result.worktree_name}",
            "=" * 50,
            f"Overall Score: {result.overall_score:.2f}/100",
            f"Status: {'PASSED' if result.passed else 'FAILED'}",
            "",
            "Metric Scores:",
        ]

        for metric, score in result.metric_scores.items():
            report_lines.append(f"  {metric}: {score:.2f}")

        if result.details.get("test_coverage"):
            report_lines.append(
                f"  test_coverage: {result.details['test_coverage']:.2f}%"
            )

        if result.failures:
            report_lines.extend([
                "",
                "Failures:",
            ])
            for failure in result.failures:
                report_lines.append(f"  - {failure}")

        return "\n".join(report_lines)
