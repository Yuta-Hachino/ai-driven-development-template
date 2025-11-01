"""
End-to-End Test: Worktree Development Patterns

Tests all 5 worktree patterns:
1. Competition
2. Parallel Development
3. A/B Testing
4. Role-Based Specialization
5. Branch Tree Exploration
"""

import pytest
import subprocess
from pathlib import Path

from worktree import WorktreeConfig, WorktreePattern


@pytest.mark.e2e
@pytest.mark.slow
def test_competition_pattern(temp_repo, worktree_manager):
    """
    Test Competition Pattern: Multiple agents solve same problem
    """

    # Create competition worktrees
    feature = "sorting-algorithm-optimization"
    agents = ["algorithm_agent_1", "algorithm_agent_2", "algorithm_agent_3"]

    worktrees = worktree_manager.create_competition_worktrees(
        feature=feature,
        agents=agents,
        max_competitors=3
    )

    # Verify worktrees created
    assert len(worktrees) == 3, "Should create 3 competition worktrees"

    # Verify each worktree exists
    for worktree in worktrees:
        assert worktree.path.exists(), f"Worktree path should exist: {worktree.path}"
        assert worktree.pattern == WorktreePattern.COMPETITION
        assert worktree.agent_name in agents

    # Simulate work in each worktree
    test_files = []
    for i, worktree in enumerate(worktrees):
        # Create test file in worktree
        test_file = worktree.path / f"solution_{i}.py"
        test_file.write_text(f"def sort(arr):\n    # Solution {i}\n    pass\n")

        # Commit changes
        subprocess.run(
            ["git", "add", "."],
            cwd=worktree.path,
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"Solution {i} for {feature}"],
            cwd=worktree.path,
            check=True
        )

        test_files.append(test_file)

    # Evaluate solutions
    evaluation_results = {}
    for i, worktree in enumerate(worktrees):
        # Mock evaluation scores
        evaluation_results[worktree.name] = {
            "performance": 80 + i * 5,  # Simulated scores
            "code_quality": 85 + i * 3,
            "total_score": 82.5 + i * 4
        }

    # Select winner
    winner = max(evaluation_results.items(), key=lambda x: x[1]["total_score"])
    print(f"\n✓ Competition pattern test passed")
    print(f"  - Created {len(worktrees)} competing solutions")
    print(f"  - Winner: {winner[0]} (score: {winner[1]['total_score']})")

    # Cleanup worktrees
    for worktree in worktrees:
        worktree_manager.remove_worktree(worktree.name)


@pytest.mark.e2e
def test_parallel_development_pattern(temp_repo, worktree_manager):
    """
    Test Parallel Development Pattern: Different features simultaneously
    """

    features = [
        "user-authentication",
        "payment-integration",
        "notification-system"
    ]

    worktrees = []
    for feature in features:
        config = WorktreeConfig(
            feature=feature,
            pattern=WorktreePattern.PARALLEL,
            base_branch="main",
            agent_name=f"dev_agent_{feature}"
        )

        worktree_info = worktree_manager.create_worktree(config)
        worktrees.append(worktree_info)

    # Verify parallel worktrees
    assert len(worktrees) == 3, "Should create 3 parallel worktrees"

    # Simulate parallel development
    for i, worktree in enumerate(worktrees):
        feature_file = worktree.path / f"{features[i].replace('-', '_')}.py"
        feature_file.write_text(f"# Implementation of {features[i]}\n")

        subprocess.run(
            ["git", "add", "."],
            cwd=worktree.path,
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"Implement {features[i]}"],
            cwd=worktree.path,
            check=True
        )

    # Verify all features developed independently
    for worktree in worktrees:
        # Check branch exists
        result = subprocess.run(
            ["git", "rev-parse", "--verify", worktree.branch],
            cwd=temp_repo,
            capture_output=True
        )
        assert result.returncode == 0, f"Branch {worktree.branch} should exist"

    print(f"\n✓ Parallel development pattern test passed")
    print(f"  - Developed {len(features)} features in parallel")

    # Cleanup
    for worktree in worktrees:
        worktree_manager.remove_worktree(worktree.name)


@pytest.mark.e2e
def test_ab_testing_pattern(temp_repo, worktree_manager):
    """
    Test A/B Testing Pattern: Two implementation variants
    """

    feature = "search-algorithm"

    # Create variant A
    config_a = WorktreeConfig(
        feature=f"{feature}-variant-a",
        pattern=WorktreePattern.AB_TEST,
        base_branch="main",
        agent_name="agent_variant_a"
    )

    variant_a = worktree_manager.create_worktree(config_a)

    # Create variant B
    config_b = WorktreeConfig(
        feature=f"{feature}-variant-b",
        pattern=WorktreePattern.AB_TEST,
        base_branch="main",
        agent_name="agent_variant_b"
    )

    variant_b = worktree_manager.create_worktree(config_b)

    # Implement variant A (linear search)
    file_a = variant_a.path / "search.py"
    file_a.write_text("""
def search(arr, target):
    '''Linear search implementation'''
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
""")

    subprocess.run(["git", "add", "."], cwd=variant_a.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Variant A: Linear search"],
        cwd=variant_a.path,
        check=True
    )

    # Implement variant B (binary search)
    file_b = variant_b.path / "search.py"
    file_b.write_text("""
def search(arr, target):
    '''Binary search implementation'''
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""")

    subprocess.run(["git", "add", "."], cwd=variant_b.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Variant B: Binary search"],
        cwd=variant_b.path,
        check=True
    )

    # Compare variants (mock evaluation)
    variant_a_score = 70  # Linear search: simpler but slower
    variant_b_score = 90  # Binary search: faster but requires sorted array

    winner = variant_b if variant_b_score > variant_a_score else variant_a

    print(f"\n✓ A/B testing pattern test passed")
    print(f"  - Variant A score: {variant_a_score}")
    print(f"  - Variant B score: {variant_b_score}")
    print(f"  - Winner: {winner.name}")

    # Cleanup
    worktree_manager.remove_worktree(variant_a.name)
    worktree_manager.remove_worktree(variant_b.name)


@pytest.mark.e2e
def test_role_based_specialization_pattern(temp_repo, worktree_manager):
    """
    Test Role-Based Pattern: Specialized agents in dedicated areas
    """

    roles = [
        ("frontend", "frontend-dashboard"),
        ("backend", "backend-api"),
        ("database", "database-schema")
    ]

    worktrees = []
    for role, feature in roles:
        config = WorktreeConfig(
            feature=feature,
            pattern=WorktreePattern.ROLE_BASED,
            base_branch="main",
            agent_name=f"{role}_specialist"
        )

        worktree = worktree_manager.create_worktree(config)
        worktrees.append((role, worktree))

    # Simulate role-based development
    for role, worktree in worktrees:
        if role == "frontend":
            file_path = worktree.path / "components" / "Dashboard.tsx"
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text("export const Dashboard = () => <div>Dashboard</div>")

        elif role == "backend":
            file_path = worktree.path / "api" / "routes.py"
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text("@app.route('/api/dashboard')\ndef dashboard(): pass")

        elif role == "database":
            file_path = worktree.path / "schema" / "dashboard.sql"
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text("CREATE TABLE dashboard_widgets (id INT PRIMARY KEY);")

        subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"{role} implementation"],
            cwd=worktree.path,
            check=True
        )

    print(f"\n✓ Role-based specialization pattern test passed")
    print(f"  - {len(roles)} specialized roles worked independently")

    # Cleanup
    for _, worktree in worktrees:
        worktree_manager.remove_worktree(worktree.name)


@pytest.mark.e2e
def test_branch_tree_exploration_pattern(temp_repo, worktree_manager):
    """
    Test Branch Tree Pattern: Exploratory development with pruning
    """

    base_feature = "ml-model-exploration"

    # Create multiple exploratory branches
    explorations = [
        "random-forest",
        "neural-network",
        "gradient-boosting",
        "ensemble-method"
    ]

    worktrees = []
    for exploration in explorations:
        config = WorktreeConfig(
            feature=f"{base_feature}-{exploration}",
            pattern=WorktreePattern.BRANCH_TREE,
            base_branch="main",
            agent_name=f"research_agent_{exploration}"
        )

        worktree = worktree_manager.create_worktree(config)
        worktrees.append((exploration, worktree))

    # Simulate exploration
    exploration_results = {}
    for exploration, worktree in worktrees:
        model_file = worktree.path / f"{exploration.replace('-', '_')}.py"
        model_file.write_text(f"# {exploration} implementation\nclass Model: pass")

        subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Explore {exploration}"],
            cwd=worktree.path,
            check=True
        )

        # Mock evaluation
        import random
        exploration_results[exploration] = {
            "accuracy": random.uniform(0.75, 0.95),
            "training_time": random.uniform(10, 100),
            "complexity": random.randint(1, 10)
        }

    # Prune unsuccessful explorations (accuracy < 0.85)
    pruned = []
    kept = []

    for exploration, results in exploration_results.items():
        if results["accuracy"] < 0.85:
            # Prune this branch
            worktree = next(wt for exp, wt in worktrees if exp == exploration)
            worktree_manager.remove_worktree(worktree.name)
            pruned.append(exploration)
        else:
            kept.append(exploration)

    print(f"\n✓ Branch tree exploration pattern test passed")
    print(f"  - Explored {len(explorations)} approaches")
    print(f"  - Kept {len(kept)} promising branches: {kept}")
    print(f"  - Pruned {len(pruned)} unsuccessful branches: {pruned}")

    # Cleanup remaining worktrees
    for exploration, worktree in worktrees:
        if exploration in kept:
            worktree_manager.remove_worktree(worktree.name)


@pytest.mark.e2e
def test_worktree_pattern_transitions(temp_repo, worktree_manager):
    """
    Test transitioning between different patterns
    """

    # Start with parallel development
    config = WorktreeConfig(
        feature="multi-pattern-test",
        pattern=WorktreePattern.PARALLEL,
        base_branch="main",
        agent_name="transition_agent"
    )

    worktree = worktree_manager.create_worktree(config)
    assert worktree.pattern == WorktreePattern.PARALLEL

    # Do some work
    test_file = worktree.path / "test.py"
    test_file.write_text("# Initial work\n")
    subprocess.run(["git", "add", "."], cwd=worktree.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial work"],
        cwd=worktree.path,
        check=True
    )

    # Transition to A/B testing (create variant)
    variant_config = WorktreeConfig(
        feature="multi-pattern-test-variant",
        pattern=WorktreePattern.AB_TEST,
        base_branch=worktree.branch,  # Base on previous work
        agent_name="variant_agent"
    )

    variant = worktree_manager.create_worktree(variant_config)
    assert variant.pattern == WorktreePattern.AB_TEST

    # Modify variant
    variant_file = variant.path / "test.py"
    variant_file.write_text("# Initial work\n# Variant changes\n")
    subprocess.run(["git", "add", "."], cwd=variant.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Variant implementation"],
        cwd=variant.path,
        check=True
    )

    print(f"\n✓ Pattern transition test passed")
    print(f"  - Transitioned from PARALLEL to AB_TEST")

    # Cleanup
    worktree_manager.remove_worktree(worktree.name)
    worktree_manager.remove_worktree(variant.name)


@pytest.mark.e2e
@pytest.mark.slow
def test_all_patterns_integration(temp_repo, worktree_manager):
    """
    Test using all 5 patterns in a single workflow
    """

    created_worktrees = []

    # 1. Start with competition for algorithm selection
    competition_wts = worktree_manager.create_competition_worktrees(
        feature="initial-algorithm",
        agents=["agent1", "agent2"],
        max_competitors=2
    )
    created_worktrees.extend(competition_wts)

    # 2. Use parallel development for different modules
    parallel_config = WorktreeConfig(
        feature="parallel-module",
        pattern=WorktreePattern.PARALLEL,
        base_branch="main",
        agent_name="parallel_agent"
    )
    parallel_wt = worktree_manager.create_worktree(parallel_config)
    created_worktrees.append(parallel_wt)

    # 3. A/B test for UI component
    ab_config_a = WorktreeConfig(
        feature="ui-variant-a",
        pattern=WorktreePattern.AB_TEST,
        base_branch="main",
        agent_name="ui_agent_a"
    )
    ab_wt_a = worktree_manager.create_worktree(ab_config_a)
    created_worktrees.append(ab_wt_a)

    # 4. Role-based for specialized work
    role_config = WorktreeConfig(
        feature="specialized-backend",
        pattern=WorktreePattern.ROLE_BASED,
        base_branch="main",
        agent_name="backend_specialist"
    )
    role_wt = worktree_manager.create_worktree(role_config)
    created_worktrees.append(role_wt)

    # 5. Branch tree for exploration
    tree_config = WorktreeConfig(
        feature="experimental-feature",
        pattern=WorktreePattern.BRANCH_TREE,
        base_branch="main",
        agent_name="research_agent"
    )
    tree_wt = worktree_manager.create_worktree(tree_config)
    created_worktrees.append(tree_wt)

    # Verify all patterns in use
    patterns_used = set(wt.pattern for wt in created_worktrees)
    assert len(patterns_used) == 5, "Should use all 5 patterns"

    print(f"\n✓ All patterns integration test passed")
    print(f"  - Used all 5 worktree patterns")
    print(f"  - Created {len(created_worktrees)} total worktrees")
    print(f"  - Patterns: {[p.value for p in patterns_used]}")

    # Cleanup
    for wt in created_worktrees:
        worktree_manager.remove_worktree(wt.name)
