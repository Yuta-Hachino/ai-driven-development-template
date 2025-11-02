"""
Autonomous Healing Example

Demonstrates the self-healing capabilities of the autonomous development system.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autonomous import FailureAnalyzer, AutoHealer, FailureType


def example_analyze_test_failure():
    """Example: Analyze test failure logs"""
    print("\n=== Analyzing Test Failure ===\n")

    # Simulate test failure log
    log_content = """
    FAILED tests/test_agents.py::test_agent_execution - AssertionError
    FAILED tests/test_worktree.py::test_worktree_creation - ImportError: No module named 'worktree'
    ERROR: 2 tests failed
    """

    analyzer = FailureAnalyzer()
    report = analyzer.analyze_log(log_content)

    print(f"Title: {report.title}")
    print(f"Type: {report.failure_type.value}")
    print(f"Severity: {report.severity.value}")
    print(f"Auto-fixable: {report.auto_fixable}")
    print(f"Requires human: {report.requires_human}")

    print(f"\nAffected Files: {len(report.affected_files)}")
    for file in report.affected_files:
        print(f"  • {file}")

    print(f"\nSuggested Fixes:")
    for i, fix in enumerate(report.suggested_fixes, 1):
        print(f"  {i}. {fix}")

    print()


def example_analyze_security_failure():
    """Example: Analyze security vulnerability"""
    print("\n=== Analyzing Security Vulnerability ===\n")

    log_content = """
    CRITICAL vulnerability detected: CVE-2023-12345
    HIGH vulnerability in dependency: requests==2.25.0
    Vulnerability scan failed
    """

    analyzer = FailureAnalyzer()
    report = analyzer.analyze_log(log_content)

    print(f"Title: {report.title}")
    print(f"Type: {report.failure_type.value}")
    print(f"Severity: {report.severity.value}")
    print(f"Auto-fixable: {report.auto_fixable}")

    if not report.auto_fixable:
        print("\n⚠️  Security issues require manual review!")

    print()


def example_analyze_linting_error():
    """Example: Analyze code quality issues"""
    print("\n=== Analyzing Linting Errors ===\n")

    log_content = """
    src/agents/base_agent.py:125:1: E501 line too long (120 > 100 characters)
    src/worktree/manager.py:45:1: F401 'os' imported but unused
    pylint: Your code has been rated at 8.5/10
    """

    analyzer = FailureAnalyzer()
    report = analyzer.analyze_log(log_content)

    print(f"Title: {report.title}")
    print(f"Type: {report.failure_type.value}")
    print(f"Auto-fixable: {report.auto_fixable}")

    if report.auto_fixable:
        print("\n✓ This can be automatically fixed!")

    print()


async def example_auto_heal_linting():
    """Example: Automatically heal linting issues"""
    print("\n=== Auto-Healing Linting Issues ===\n")

    # Create failure report
    log_content = """
    pylint errors detected
    src/agents/base_agent.py:125: line too long
    """

    analyzer = FailureAnalyzer()
    report = analyzer.analyze_log(log_content)

    print(f"Failure: {report.failure_type.value}")
    print(f"Auto-fixable: {report.auto_fixable}\n")

    if report.auto_fixable:
        print("Attempting automatic healing...\n")

        # Create healer
        healer = AutoHealer(str(Path.cwd()))

        # Attempt to heal
        result = await healer.heal(report)

        if result.success:
            print("✓ Healing successful!\n")
            print("Actions taken:")
            for action in result.actions_taken:
                print(f"  • {action}")

            if result.files_modified:
                print(f"\nFiles modified:")
                for file in result.files_modified:
                    print(f"  • {file}")
        else:
            print(f"✗ Healing failed: {result.error_message}")

    print()


async def example_healing_workflow():
    """Example: Complete healing workflow"""
    print("\n=== Complete Healing Workflow ===\n")

    # Step 1: Analyze failure
    print("Step 1: Analyzing failure...\n")

    log_content = """
    ImportError: cannot import name 'BaseAgent' from 'agents'
    FAILED tests/test_agents.py::test_base_agent
    """

    analyzer = FailureAnalyzer()
    report = analyzer.analyze_log(log_content)

    print(f"  Detected: {report.failure_type.value}")
    print(f"  Severity: {report.severity.value}")
    print(f"  Auto-fixable: {report.auto_fixable}\n")

    # Step 2: Attempt healing
    if report.auto_fixable:
        print("Step 2: Attempting automatic healing...\n")

        healer = AutoHealer(str(Path.cwd()))
        healing_result = await healer.heal(report)

        print(f"  Strategy: {healing_result.strategy.value}")
        print(f"  Success: {healing_result.success}\n")

        if healing_result.success:
            print("Step 3: Verifying fix...\n")

            verified = await healer.verify_fix()

            if verified:
                print("  ✓ Fix verified successfully!")
                print("\nWorkflow complete - changes ready for commit")
            else:
                print("  ⚠️  Fix applied but verification failed")
                print("  Manual review recommended")
        else:
            print(f"  ✗ Healing failed: {healing_result.error_message}")
            print("\nManual intervention required")
    else:
        print("Step 2: Automatic healing not applicable\n")
        print("Creating issue for manual review...")
        print(f"  Issue title: {report.title}")
        print(f"  Severity: {report.severity.value}")

    print()


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Autonomous Development System - Self-Healing Examples")
    print("="*60)

    # Analysis examples
    example_analyze_test_failure()
    await asyncio.sleep(0.3)

    example_analyze_security_failure()
    await asyncio.sleep(0.3)

    example_analyze_linting_error()
    await asyncio.sleep(0.3)

    # Healing examples
    print("\n" + "-"*60)
    print("Healing Examples")
    print("-"*60 + "\n")

    await example_auto_heal_linting()
    await asyncio.sleep(0.3)

    await example_healing_workflow()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")

    print("💡 Tip: In production, these workflows run automatically")
    print("   when CI/CD failures are detected.\n")


if __name__ == "__main__":
    asyncio.run(main())
