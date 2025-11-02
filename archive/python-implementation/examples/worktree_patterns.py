"""
Worktree Patterns Example

Demonstrates the 5 Git worktree development patterns.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from worktree import (
    WorktreeManager,
    WorktreeConfig,
    DevelopmentPattern,
    EvaluationSystem,
)


def example_competition_pattern():
    """Example: Competition Resolution Pattern"""
    print("\n=== Competition Resolution Pattern ===\n")

    repo_path = Path.cwd()
    manager = WorktreeManager(str(repo_path))

    # Create competition worktrees
    print("Creating competition worktrees for sorting algorithm...\n")

    feature = "sorting-optimization"
    agents = ["algorithm_agent_1", "algorithm_agent_2", "algorithm_agent_3"]

    try:
        worktrees = manager.create_competition_worktrees(
            feature=feature,
            agents=agents,
            max_competitors=3
        )

        print(f"✓ Created {len(worktrees)} competition worktrees:\n")
        for wt in worktrees:
            print(f"  • {wt.name}")
            print(f"    Branch: {wt.branch}")
            print(f"    Agent: {wt.agent}")
            print()

        print("Each agent will independently solve the problem.")
        print("The best solution will be selected based on evaluation.\n")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_parallel_pattern():
    """Example: Parallel Development Pattern"""
    print("\n=== Parallel Development Pattern ===\n")

    repo_path = Path.cwd()
    manager = WorktreeManager(str(repo_path))

    # Create parallel worktrees
    print("Creating parallel worktrees for different features...\n")

    features = ["authentication", "user-dashboard", "api-endpoints"]
    agent_assignments = {
        "authentication": "security_agent",
        "user-dashboard": "frontend_agent",
        "api-endpoints": "backend_agent"
    }

    try:
        worktrees = manager.create_parallel_worktrees(
            features=features,
            agent_assignments=agent_assignments
        )

        print(f"✓ Created {len(worktrees)} parallel worktrees:\n")
        for wt in worktrees:
            print(f"  • {wt.name}")
            print(f"    Feature: {wt.path}")
            print(f"    Agent: {wt.agent}")
            print()

        print("All features are being developed simultaneously.\n")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_worktree_metrics():
    """Example: Get worktree metrics"""
    print("\n=== Worktree Metrics ===\n")

    repo_path = Path.cwd()
    manager = WorktreeManager(str(repo_path))

    metrics = manager.get_metrics()

    print("Current Worktree Status:\n")
    print(f"Total worktrees: {metrics['total_worktrees']}")
    print(f"\nPatterns breakdown:")

    for pattern, count in metrics.get('patterns', {}).items():
        print(f"  • {pattern}: {count} worktrees")

    print()


async def example_evaluation():
    """Example: Evaluate worktrees"""
    print("\n=== Worktree Evaluation ===\n")

    # Create evaluation system
    evaluator = EvaluationSystem()

    # Simulate evaluating a worktree
    print("Evaluating worktree: competition-algorithm-sorting-001\n")

    worktree_path = Path("/tmp/example-worktree")
    worktree_path.mkdir(exist_ok=True)

    try:
        result = await evaluator.evaluate_worktree(
            worktree_path,
            "competition-algorithm-sorting-001"
        )

        print(f"Overall Score: {result.overall_score:.2f}/100\n")
        print("Metric Scores:")
        for metric, score in result.metric_scores.items():
            print(f"  • {metric}: {score:.2f}")

        print(f"\nTest Coverage: {result.details.get('test_coverage', 0):.2f}%")
        print(f"Passed: {result.passed}")

        if result.failures:
            print(f"\nFailures:")
            for failure in result.failures:
                print(f"  • {failure}")

    except Exception as e:
        print(f"✗ Error: {e}")


async def example_select_best():
    """Example: Select best worktree from evaluation"""
    print("\n=== Selecting Best Worktree ===\n")

    evaluator = EvaluationSystem()

    # Simulate multiple worktree evaluations
    print("Evaluating 3 competition worktrees...\n")

    from worktree.evaluation import EvaluationResult

    results = [
        EvaluationResult(
            worktree_name="solution-1",
            overall_score=85.5,
            metric_scores={"performance": 90, "quality": 85, "security": 80},
            passed=True
        ),
        EvaluationResult(
            worktree_name="solution-2",
            overall_score=92.3,
            metric_scores={"performance": 95, "quality": 90, "security": 92},
            passed=True
        ),
        EvaluationResult(
            worktree_name="solution-3",
            overall_score=78.1,
            metric_scores={"performance": 75, "quality": 80, "security": 80},
            passed=True
        ),
    ]

    # Select best
    best = evaluator.select_best_worktree(results)

    if best:
        print(f"✓ Best worktree: {best.worktree_name}")
        print(f"  Score: {best.overall_score:.2f}/100")
        print(f"\n  Metrics:")
        for metric, score in best.metric_scores.items():
            print(f"    • {metric}: {score:.2f}")
    else:
        print("✗ No worktrees passed evaluation")

    # Comparison report
    print("\n" + "="*50)
    comparison = evaluator.compare_worktrees(results)

    print("\nComparison Report:")
    print(f"  Total worktrees: {comparison['total_worktrees']}")
    print(f"  Passed: {comparison['passed_count']}")
    print(f"  Failed: {comparison['failed_count']}")
    print(f"\n  Best: {comparison['best_worktree']['name']} "
          f"({comparison['best_worktree']['score']:.2f})")
    print(f"  Worst: {comparison['worst_worktree']['name']} "
          f"({comparison['worst_worktree']['score']:.2f})")
    print(f"  Score spread: {comparison['score_range']['spread']:.2f}")


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Autonomous Development System - Worktree Pattern Examples")
    print("="*60)

    # Note: These examples are for demonstration
    # Some may require an actual git repository
    print("\n⚠️  Note: Some examples require an active git repository\n")

    # Run examples
    try:
        example_competition_pattern()
    except Exception as e:
        print(f"Skipping (requires git repo): {e}\n")

    try:
        example_parallel_pattern()
    except Exception as e:
        print(f"Skipping (requires git repo): {e}\n")

    try:
        example_worktree_metrics()
    except Exception as e:
        print(f"Skipping (requires git repo): {e}\n")

    await example_evaluation()
    await asyncio.sleep(0.5)

    await example_select_best()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
