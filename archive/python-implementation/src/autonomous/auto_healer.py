"""
Auto Healer

Automatically fixes common CI/CD failures.
"""

import asyncio
import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

from .failure_analyzer import FailureReport, FailureType

logger = logging.getLogger(__name__)


class HealingStrategy(Enum):
    """Healing strategies for different failure types"""
    AUTO_FORMAT = "auto_format"
    FIX_IMPORTS = "fix_imports"
    UPDATE_DEPENDENCIES = "update_dependencies"
    FIX_TESTS = "fix_tests"
    NO_ACTION = "no_action"
    MANUAL_REQUIRED = "manual_required"


@dataclass
class HealingResult:
    """Result of healing attempt"""
    success: bool
    strategy: HealingStrategy
    actions_taken: List[str]
    files_modified: List[str]
    error_message: Optional[str] = None
    requires_verification: bool = True


class AutoHealer:
    """
    Automatically fixes common CI/CD failures.

    Features:
    - Auto-formatting code
    - Fixing import statements
    - Updating dependencies
    - Basic test fixes
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.actions_taken = []
        self.files_modified = []

    def _run_command(
        self,
        command: List[str],
        cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess:
        """Run command and return result"""
        cwd = cwd or self.repo_path

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

    async def heal(self, failure_report: FailureReport) -> HealingResult:
        """
        Attempt to heal the failure.

        Args:
            failure_report: Analysis of the failure

        Returns:
            HealingResult with outcome
        """
        logger.info(f"Attempting to heal {failure_report.failure_type.value}")

        # Determine strategy
        strategy = self._determine_strategy(failure_report)

        if strategy == HealingStrategy.MANUAL_REQUIRED:
            return HealingResult(
                success=False,
                strategy=strategy,
                actions_taken=[],
                files_modified=[],
                error_message="Manual intervention required",
                requires_verification=True
            )

        if strategy == HealingStrategy.NO_ACTION:
            return HealingResult(
                success=True,
                strategy=strategy,
                actions_taken=["No action needed"],
                files_modified=[],
                requires_verification=False
            )

        # Execute healing strategy
        try:
            if strategy == HealingStrategy.AUTO_FORMAT:
                result = await self._auto_format()
            elif strategy == HealingStrategy.FIX_IMPORTS:
                result = await self._fix_imports(failure_report.affected_files)
            elif strategy == HealingStrategy.UPDATE_DEPENDENCIES:
                result = await self._update_dependencies()
            elif strategy == HealingStrategy.FIX_TESTS:
                result = await self._fix_tests(failure_report.affected_files)
            else:
                result = HealingResult(
                    success=False,
                    strategy=strategy,
                    actions_taken=[],
                    files_modified=[],
                    error_message=f"Unknown strategy: {strategy}"
                )

            return result

        except Exception as e:
            logger.error(f"Healing failed: {e}")
            return HealingResult(
                success=False,
                strategy=strategy,
                actions_taken=self.actions_taken,
                files_modified=self.files_modified,
                error_message=str(e)
            )

    def _determine_strategy(self, failure_report: FailureReport) -> HealingStrategy:
        """Determine appropriate healing strategy"""
        if not failure_report.auto_fixable:
            return HealingStrategy.MANUAL_REQUIRED

        failure_type = failure_report.failure_type

        if failure_type == FailureType.LINTING_ERROR:
            return HealingStrategy.AUTO_FORMAT

        if failure_type == FailureType.IMPORT_ERROR:
            return HealingStrategy.FIX_IMPORTS

        if failure_type == FailureType.DEPENDENCY_ERROR:
            return HealingStrategy.UPDATE_DEPENDENCIES

        if failure_type == FailureType.TEST_FAILURE:
            # Only if it's import-related
            if any("import" in msg.lower() for msg in failure_report.error_messages):
                return HealingStrategy.FIX_IMPORTS
            return HealingStrategy.MANUAL_REQUIRED

        return HealingStrategy.NO_ACTION

    async def _auto_format(self) -> HealingResult:
        """Auto-format code"""
        logger.info("Auto-formatting code...")
        actions = []
        modified = []

        try:
            # Remove unused imports
            logger.info("Removing unused imports...")
            result = self._run_command([
                "autoflake",
                "--in-place",
                "--remove-all-unused-imports",
                "--recursive",
                "src/", "tests/"
            ])
            if result.returncode == 0:
                actions.append("Removed unused imports with autoflake")

            # Sort imports
            logger.info("Sorting imports...")
            result = self._run_command(["isort", "src/", "tests/"])
            if result.returncode == 0:
                actions.append("Sorted imports with isort")

            # Format with black
            logger.info("Formatting with black...")
            result = self._run_command(["black", "src/", "tests/"])
            if result.returncode == 0:
                actions.append("Formatted code with black")

            # Get list of modified files
            git_result = self._run_command(["git", "diff", "--name-only"])
            if git_result.returncode == 0:
                modified = git_result.stdout.strip().split('\n')
                modified = [f for f in modified if f]

            return HealingResult(
                success=True,
                strategy=HealingStrategy.AUTO_FORMAT,
                actions_taken=actions,
                files_modified=modified,
                requires_verification=True
            )

        except Exception as e:
            return HealingResult(
                success=False,
                strategy=HealingStrategy.AUTO_FORMAT,
                actions_taken=actions,
                files_modified=modified,
                error_message=str(e)
            )

    async def _fix_imports(self, affected_files: List[str]) -> HealingResult:
        """Fix import statements"""
        logger.info("Fixing import statements...")
        actions = []
        modified = []

        try:
            # Common import fixes
            for file_path in affected_files:
                full_path = self.repo_path / file_path

                if not full_path.exists():
                    continue

                # Read file
                content = full_path.read_text()
                original_content = content

                # Fix relative imports
                content = content.replace('from ..', 'from src.')

                # Fix common import issues
                if 'from agents import' in content:
                    content = content.replace('from agents import', 'from src.agents import')

                if 'from worktree import' in content:
                    content = content.replace('from worktree import', 'from src.worktree import')

                if 'from security import' in content:
                    content = content.replace('from security import', 'from src.security import')

                # Write back if changed
                if content != original_content:
                    full_path.write_text(content)
                    modified.append(file_path)
                    actions.append(f"Fixed imports in {file_path}")

            return HealingResult(
                success=len(modified) > 0,
                strategy=HealingStrategy.FIX_IMPORTS,
                actions_taken=actions if actions else ["No import issues found"],
                files_modified=modified,
                requires_verification=True
            )

        except Exception as e:
            return HealingResult(
                success=False,
                strategy=HealingStrategy.FIX_IMPORTS,
                actions_taken=actions,
                files_modified=modified,
                error_message=str(e)
            )

    async def _update_dependencies(self) -> HealingResult:
        """Update dependencies"""
        logger.info("Updating dependencies...")
        actions = []

        try:
            # Update pip
            self._run_command(["pip", "install", "--upgrade", "pip"])
            actions.append("Updated pip")

            # Reinstall requirements
            requirements_file = self.repo_path / "requirements.txt"
            if requirements_file.exists():
                self._run_command([
                    "pip", "install", "-r", str(requirements_file)
                ])
                actions.append("Reinstalled requirements.txt")

            return HealingResult(
                success=True,
                strategy=HealingStrategy.UPDATE_DEPENDENCIES,
                actions_taken=actions,
                files_modified=[],
                requires_verification=True
            )

        except Exception as e:
            return HealingResult(
                success=False,
                strategy=HealingStrategy.UPDATE_DEPENDENCIES,
                actions_taken=actions,
                files_modified=[],
                error_message=str(e)
            )

    async def _fix_tests(self, affected_files: List[str]) -> HealingResult:
        """Fix common test issues"""
        logger.info("Fixing test issues...")
        actions = []
        modified = []

        try:
            test_files = [f for f in affected_files if f.startswith('tests/')]

            for file_path in test_files:
                full_path = self.repo_path / file_path

                if not full_path.exists():
                    continue

                content = full_path.read_text()
                original_content = content

                # Add pytest.mark.asyncio for async tests
                lines = content.split('\n')
                new_lines = []

                for i, line in enumerate(lines):
                    # Check if this is an async test without decorator
                    if line.strip().startswith('async def test_'):
                        # Check previous line for decorator
                        prev_line = lines[i-1] if i > 0 else ""
                        if '@pytest.mark.asyncio' not in prev_line:
                            new_lines.append('@pytest.mark.asyncio')

                    new_lines.append(line)

                content = '\n'.join(new_lines)

                # Write back if changed
                if content != original_content:
                    full_path.write_text(content)
                    modified.append(file_path)
                    actions.append(f"Fixed async test decorators in {file_path}")

            return HealingResult(
                success=len(modified) > 0,
                strategy=HealingStrategy.FIX_TESTS,
                actions_taken=actions if actions else ["No test issues found"],
                files_modified=modified,
                requires_verification=True
            )

        except Exception as e:
            return HealingResult(
                success=False,
                strategy=HealingStrategy.FIX_TESTS,
                actions_taken=actions,
                files_modified=modified,
                error_message=str(e)
            )

    async def verify_fix(self) -> bool:
        """Verify that fixes resolve the issue"""
        logger.info("Verifying fixes...")

        try:
            # Run tests
            test_result = self._run_command(["pytest", "tests/", "-v"])

            if test_result.returncode != 0:
                logger.warning("Tests still failing after fix")
                return False

            # Run linting
            lint_result = self._run_command([
                "black", "--check", "src/", "tests/"
            ])

            if lint_result.returncode != 0:
                logger.warning("Linting issues remain")
                return False

            logger.info("Verification successful!")
            return True

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
