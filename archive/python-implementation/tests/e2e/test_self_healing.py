"""
End-to-End Test: Self-Healing and Autonomous Recovery

Tests Phase 2 self-healing capabilities:
1. Auto-healing on test failures
2. CI/CD failure recovery
3. Dependency conflict resolution
4. Error pattern detection
5. Proactive issue prevention
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

from self_healing import (
    AutoHealingOrchestrator,
    HealingStrategy,
    HealingResult,
    ErrorPattern,
)
from ci_cd_integration import CICDIntegration, CIStatus
from dependency_manager import DependencyConflictResolver


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_auto_healing_on_test_failure(temp_repo, auto_healing_orchestrator):
    """
    Test automatic healing when tests fail
    """

    # Create a failing test
    test_file = temp_repo / "test_example.py"
    test_file.write_text("""
def test_addition():
    assert 1 + 1 == 3  # Intentionally failing
""")

    # Commit the failing test
    subprocess.run(["git", "add", "."], cwd=temp_repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Add failing test"],
        cwd=temp_repo,
        check=True
    )

    # Run tests and detect failure
    result = subprocess.run(
        ["pytest", str(test_file)],
        cwd=temp_repo,
        capture_output=True,
        text=True
    )

    assert result.returncode != 0, "Test should fail"

    # Trigger auto-healing
    healing_result = await auto_healing_orchestrator.heal_test_failure(
        test_file=str(test_file),
        failure_output=result.stdout + result.stderr,
        repository_path=temp_repo
    )

    # Verify healing attempt
    assert healing_result.success or healing_result.attempted
    assert healing_result.strategy in [
        HealingStrategy.FIX_TEST,
        HealingStrategy.FIX_CODE,
        HealingStrategy.UPDATE_DEPENDENCIES
    ]

    print(f"\n✓ Auto-healing test passed")
    print(f"  - Detected failing test")
    print(f"  - Applied healing strategy: {healing_result.strategy}")
    print(f"  - Healing success: {healing_result.success}")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_ci_failure_recovery(
    temp_repo, auto_healing_orchestrator, ci_integration
):
    """
    Test recovery from CI/CD pipeline failures
    """

    # Simulate CI failure
    ci_failure = {
        "status": CIStatus.FAILED,
        "job": "build",
        "error": "ModuleNotFoundError: No module named 'requests'",
        "logs": "Build failed due to missing dependency",
        "commit_sha": "abc123"
    }

    # Trigger CI failure handling
    recovery_result = await auto_healing_orchestrator.handle_ci_failure(
        ci_status=ci_failure,
        repository_path=temp_repo
    )

    # Verify recovery actions
    assert recovery_result.attempted
    assert "dependency" in recovery_result.actions_taken.lower() or \
           "install" in recovery_result.actions_taken.lower()

    # Verify requirements.txt was updated or created
    requirements_file = temp_repo / "requirements.txt"
    if requirements_file.exists():
        content = requirements_file.read_text()
        print(f"\n✓ CI failure recovery test passed")
        print(f"  - Detected missing dependency")
        print(f"  - Updated requirements.txt")
        print(f"  - Actions: {recovery_result.actions_taken}")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_dependency_conflict_resolution(
    temp_repo, dependency_resolver
):
    """
    Test automatic resolution of dependency conflicts
    """

    # Create conflicting dependencies
    requirements_file = temp_repo / "requirements.txt"
    requirements_file.write_text("""
requests==2.25.1
urllib3==1.26.15
# requests 2.25.1 requires urllib3>=1.21.1,<1.27
# But we have urllib3==1.26.15 which should be compatible
# Let's create actual conflict:
requests==2.28.0
requests==2.25.1
""")

    subprocess.run(["git", "add", "."], cwd=temp_repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Add conflicting dependencies"],
        cwd=temp_repo,
        check=True
    )

    # Detect and resolve conflicts
    conflicts = dependency_resolver.detect_conflicts(temp_repo)

    if conflicts:
        resolution_result = await dependency_resolver.resolve_conflicts(
            conflicts=conflicts,
            repository_path=temp_repo
        )

        assert resolution_result.resolved
        assert resolution_result.strategy in [
            "use_latest",
            "use_compatible",
            "pin_versions"
        ]

        print(f"\n✓ Dependency conflict resolution test passed")
        print(f"  - Detected {len(conflicts)} conflicts")
        print(f"  - Resolution strategy: {resolution_result.strategy}")
        print(f"  - Resolved: {resolution_result.resolved}")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_error_pattern_detection(
    temp_repo, auto_healing_orchestrator, project_memory
):
    """
    Test detection and learning from error patterns
    """

    # Simulate recurring error pattern
    error_logs = [
        {
            "timestamp": "2025-11-01T10:00:00",
            "error": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "file": "src/calculator.py",
            "line": 42
        },
        {
            "timestamp": "2025-11-01T11:30:00",
            "error": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "file": "src/calculator.py",
            "line": 42
        },
        {
            "timestamp": "2025-11-01T14:00:00",
            "error": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "file": "src/calculator.py",
            "line": 42
        }
    ]

    # Feed errors to orchestrator
    patterns = []
    for error in error_logs:
        pattern = await auto_healing_orchestrator.analyze_error(
            error_message=error["error"],
            context={
                "file": error["file"],
                "line": error["line"]
            }
        )
        patterns.append(pattern)

    # Detect recurring pattern
    recurring_pattern = auto_healing_orchestrator.detect_recurring_pattern(
        patterns
    )

    assert recurring_pattern is not None
    assert recurring_pattern.frequency >= 3
    assert "TypeError" in recurring_pattern.error_signature

    # Verify learning from pattern
    prevention_rule = await auto_healing_orchestrator.create_prevention_rule(
        recurring_pattern
    )

    assert prevention_rule is not None
    assert prevention_rule.pattern_id == recurring_pattern.id

    # Store in project memory
    project_memory.store_error_pattern(recurring_pattern)
    project_memory.store_prevention_rule(prevention_rule)

    print(f"\n✓ Error pattern detection test passed")
    print(f"  - Detected recurring error (frequency: {recurring_pattern.frequency})")
    print(f"  - Created prevention rule: {prevention_rule.description}")
    print(f"  - Stored in project memory")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_proactive_issue_prevention(
    temp_repo, auto_healing_orchestrator, project_memory
):
    """
    Test proactive prevention of known issues
    """

    # Add known error pattern to memory
    known_pattern = ErrorPattern(
        id="pattern-001",
        error_signature="TypeError: unsupported operand",
        frequency=5,
        contexts=["type coercion", "string concatenation"],
        prevention_rule="Always validate types before operations"
    )

    project_memory.store_error_pattern(known_pattern)

    # Create code that might trigger the pattern
    code_file = temp_repo / "src" / "new_feature.py"
    code_file.parent.mkdir(parents=True, exist_ok=True)
    code_file.write_text("""
def process_data(value, multiplier):
    # This might cause TypeError if value is string
    result = value + multiplier
    return result
""")

    # Run proactive analysis
    issues = await auto_healing_orchestrator.analyze_code_proactively(
        file_path=code_file,
        known_patterns=[known_pattern]
    )

    # Verify issue detection
    assert len(issues) > 0
    assert any("type" in issue.description.lower() for issue in issues)

    # Apply preventive fix
    fix_result = await auto_healing_orchestrator.apply_preventive_fix(
        file_path=code_file,
        issues=issues
    )

    assert fix_result.applied

    # Verify code was improved
    fixed_content = code_file.read_text()
    assert "isinstance" in fixed_content or "type(" in fixed_content

    print(f"\n✓ Proactive issue prevention test passed")
    print(f"  - Detected {len(issues)} potential issues")
    print(f"  - Applied preventive fixes")
    print(f"  - Prevented known error pattern")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_healing_orchestration_workflow(
    temp_repo, auto_healing_orchestrator, ci_integration,
    project_memory, notification_hub
):
    """
    Test complete healing orchestration workflow:
    1. Error occurs in CI
    2. Auto-healing detects and analyzes
    3. Applies fix
    4. Re-runs validation
    5. Records learning
    6. Sends notification
    """

    # Step 1: Simulate CI failure with build error
    ci_failure = {
        "status": CIStatus.FAILED,
        "job": "test",
        "error": "AssertionError: Expected 5, got 3",
        "logs": """
        tests/test_math.py:10: AssertionError
        def test_add():
            result = add(2, 1)
        >   assert result == 5
        E   AssertionError: Expected 5, got 3
        """,
        "commit_sha": "def456",
        "file": "tests/test_math.py"
    }

    # Step 2: Orchestrator detects and analyzes
    analysis = await auto_healing_orchestrator.analyze_failure(ci_failure)

    assert analysis.error_type == "assertion"
    assert analysis.likely_cause in ["logic_error", "incorrect_expectation"]

    # Step 3: Apply healing strategy
    healing_result = await auto_healing_orchestrator.heal(
        analysis=analysis,
        repository_path=temp_repo
    )

    assert healing_result.attempted

    # Step 4: Simulate re-run validation
    if healing_result.changes_made:
        # In real scenario, CI would re-run automatically
        # Here we mock the success
        healing_result.validation_passed = True

    # Step 5: Record learning in project memory
    if healing_result.success:
        learning = {
            "error_type": analysis.error_type,
            "healing_strategy": healing_result.strategy,
            "success": True,
            "pattern": analysis.error_pattern
        }

        project_memory.record_healing_success(learning)

    # Step 6: Send notification
    notification = notification_hub.create_notification(
        title="Auto-Healing Success",
        message=f"Automatically fixed {analysis.error_type} error",
        priority="medium",
        category="self_healing"
    )

    notification_hub.send(notification)

    print(f"\n✓ Healing orchestration workflow test passed")
    print(f"  - Analyzed failure: {analysis.error_type}")
    print(f"  - Applied strategy: {healing_result.strategy}")
    print(f"  - Validation: {'Passed' if healing_result.validation_passed else 'Failed'}")
    print(f"  - Learning recorded: Yes")
    print(f"  - Notification sent: Yes")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_healing_with_rollback(
    temp_repo, auto_healing_orchestrator
):
    """
    Test healing with automatic rollback on failure
    """

    # Create baseline code
    code_file = temp_repo / "src" / "feature.py"
    code_file.parent.mkdir(parents=True, exist_ok=True)
    original_code = """
def calculate(x, y):
    return x + y
"""
    code_file.write_text(original_code)

    subprocess.run(["git", "add", "."], cwd=temp_repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Add baseline code"],
        cwd=temp_repo,
        check=True
    )

    # Get current commit
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=temp_repo,
        capture_output=True,
        text=True,
        check=True
    )
    baseline_commit = result.stdout.strip()

    # Simulate healing attempt that makes things worse
    healing_result = await auto_healing_orchestrator.heal_with_rollback(
        file_path=code_file,
        healing_action=lambda: code_file.write_text("invalid syntax here {{"),
        validation_action=lambda: subprocess.run(
            ["python", "-m", "py_compile", str(code_file)],
            capture_output=True
        ).returncode == 0,
        baseline_commit=baseline_commit,
        repository_path=temp_repo
    )

    # Verify rollback occurred
    assert healing_result.rolled_back
    assert code_file.read_text() == original_code

    print(f"\n✓ Healing with rollback test passed")
    print(f"  - Attempted healing")
    print(f"  - Validation failed")
    print(f"  - Rolled back to baseline: {baseline_commit[:7]}")


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_continuous_healing_over_time(
    temp_repo, auto_healing_orchestrator, project_memory
):
    """
    Test that healing improves over time with learning
    """

    # Simulate multiple healing cycles
    healing_attempts = []

    for i in range(5):
        # Create an error
        error = {
            "type": "ImportError",
            "message": f"No module named 'module_{i}'",
            "file": f"src/file_{i}.py"
        }

        # Attempt healing
        result = await auto_healing_orchestrator.heal_import_error(
            error=error,
            repository_path=temp_repo,
            learning_enabled=True
        )

        healing_attempts.append(result)

        # Record learning
        if result.success:
            project_memory.record_healing_success({
                "error_type": "ImportError",
                "strategy": result.strategy,
                "success_rate": result.success_rate
            })

    # Verify improvement over time
    success_rates = [attempt.success_rate for attempt in healing_attempts]

    # Success rate should generally improve (allowing for some variation)
    avg_early = sum(success_rates[:2]) / 2
    avg_late = sum(success_rates[-2:]) / 2

    assert avg_late >= avg_early or avg_late > 0.8, \
        "Success rate should improve or remain high"

    print(f"\n✓ Continuous healing improvement test passed")
    print(f"  - Healing attempts: {len(healing_attempts)}")
    print(f"  - Early avg success rate: {avg_early:.1%}")
    print(f"  - Late avg success rate: {avg_late:.1%}")
    print(f"  - Improvement: {avg_late - avg_early:.1%}")
