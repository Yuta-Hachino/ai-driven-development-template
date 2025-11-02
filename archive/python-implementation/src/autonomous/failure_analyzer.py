"""
Failure Analyzer

Analyzes CI/CD failures and determines appropriate remediation strategies.
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of CI/CD failures"""
    TEST_FAILURE = "test"
    CODE_QUALITY = "code-quality"
    SECURITY_VULNERABILITY = "security"
    BUILD_ERROR = "build"
    DEPENDENCY_ERROR = "dependency"
    LINTING_ERROR = "linting"
    TYPE_ERROR = "type-error"
    IMPORT_ERROR = "import"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class SeverityLevel(Enum):
    """Severity levels for failures"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class FailureReport:
    """Comprehensive failure analysis report"""
    failure_type: FailureType
    severity: SeverityLevel
    title: str
    description: str
    affected_files: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    suggested_fixes: List[str] = field(default_factory=list)
    auto_fixable: bool = False
    requires_human: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class FailureAnalyzer:
    """
    Analyzes CI/CD failures and provides remediation strategies.

    Features:
    - Pattern matching for common errors
    - Severity assessment
    - Auto-fix feasibility determination
    - Suggested remediation steps
    """

    def __init__(self):
        self.error_patterns = self._load_error_patterns()

    def _load_error_patterns(self) -> Dict[FailureType, List[Dict]]:
        """Load error patterns for analysis"""
        return {
            FailureType.TEST_FAILURE: [
                {
                    "pattern": r"FAILED.*test_.*",
                    "severity": SeverityLevel.HIGH,
                    "auto_fixable": False,
                    "suggestion": "Review failed test and fix underlying issue"
                },
                {
                    "pattern": r"AssertionError",
                    "severity": SeverityLevel.MEDIUM,
                    "auto_fixable": False,
                    "suggestion": "Check assertion logic in test"
                },
            ],
            FailureType.IMPORT_ERROR: [
                {
                    "pattern": r"ImportError|ModuleNotFoundError",
                    "severity": SeverityLevel.HIGH,
                    "auto_fixable": True,
                    "suggestion": "Fix import statements or add missing dependencies"
                },
                {
                    "pattern": r"cannot import name",
                    "severity": SeverityLevel.MEDIUM,
                    "auto_fixable": True,
                    "suggestion": "Check module structure and import paths"
                },
            ],
            FailureType.LINTING_ERROR: [
                {
                    "pattern": r"pylint.*error",
                    "severity": SeverityLevel.LOW,
                    "auto_fixable": True,
                    "suggestion": "Run black and isort to auto-format"
                },
                {
                    "pattern": r"line too long",
                    "severity": SeverityLevel.LOW,
                    "auto_fixable": True,
                    "suggestion": "Auto-format with black"
                },
            ],
            FailureType.TYPE_ERROR: [
                {
                    "pattern": r"mypy.*error",
                    "severity": SeverityLevel.MEDIUM,
                    "auto_fixable": False,
                    "suggestion": "Add type hints or fix type inconsistencies"
                },
                {
                    "pattern": r"TypeError",
                    "severity": SeverityLevel.HIGH,
                    "auto_fixable": False,
                    "suggestion": "Check argument types and function signatures"
                },
            ],
            FailureType.SECURITY_VULNERABILITY: [
                {
                    "pattern": r"CRITICAL.*vulnerability",
                    "severity": SeverityLevel.CRITICAL,
                    "auto_fixable": False,
                    "suggestion": "Update vulnerable dependency or apply security patch"
                },
                {
                    "pattern": r"HIGH.*vulnerability",
                    "severity": SeverityLevel.HIGH,
                    "auto_fixable": False,
                    "suggestion": "Review and update affected packages"
                },
            ],
            FailureType.DEPENDENCY_ERROR: [
                {
                    "pattern": r"pip.*error|dependency.*conflict",
                    "severity": SeverityLevel.MEDIUM,
                    "auto_fixable": True,
                    "suggestion": "Update requirements.txt or resolve conflicts"
                },
            ],
        }

    def analyze_log(self, log_content: str, context: Optional[Dict] = None) -> FailureReport:
        """
        Analyze CI/CD log content and generate failure report.

        Args:
            log_content: Raw log content from CI/CD
            context: Additional context (branch, commit, etc.)

        Returns:
            FailureReport with analysis results
        """
        logger.info("Analyzing failure log...")

        # Detect failure type
        failure_type = self._detect_failure_type(log_content)

        # Extract error messages
        error_messages = self._extract_error_messages(log_content)

        # Identify affected files
        affected_files = self._extract_affected_files(log_content)

        # Determine severity
        severity = self._assess_severity(failure_type, error_messages)

        # Generate suggestions
        suggestions = self._generate_suggestions(failure_type, error_messages)

        # Determine auto-fix feasibility
        auto_fixable = self._is_auto_fixable(failure_type, error_messages)

        # Check if human intervention required
        requires_human = severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]

        # Create title and description
        title = self._generate_title(failure_type, severity)
        description = self._generate_description(
            failure_type, error_messages, affected_files
        )

        report = FailureReport(
            failure_type=failure_type,
            severity=severity,
            title=title,
            description=description,
            affected_files=affected_files,
            error_messages=error_messages[:10],  # Limit to first 10
            suggested_fixes=suggestions,
            auto_fixable=auto_fixable,
            requires_human=requires_human,
            metadata=context or {}
        )

        logger.info(
            f"Analysis complete: {failure_type.value}, "
            f"Severity: {severity.value}, Auto-fixable: {auto_fixable}"
        )

        return report

    def _detect_failure_type(self, log_content: str) -> FailureType:
        """Detect the type of failure from log content"""
        log_lower = log_content.lower()

        # Check patterns in priority order
        if re.search(r"critical.*vulnerability|cve-\d+", log_lower):
            return FailureType.SECURITY_VULNERABILITY

        if re.search(r"importerror|modulenotfounderror", log_lower):
            return FailureType.IMPORT_ERROR

        if re.search(r"failed.*test_|pytest.*failed", log_lower):
            return FailureType.TEST_FAILURE

        if re.search(r"mypy.*error|typeerror", log_lower):
            return FailureType.TYPE_ERROR

        if re.search(r"pylint|black|isort|line too long", log_lower):
            return FailureType.LINTING_ERROR

        if re.search(r"build.*failed|compilation error", log_lower):
            return FailureType.BUILD_ERROR

        if re.search(r"dependency|pip.*error|requirements", log_lower):
            return FailureType.DEPENDENCY_ERROR

        if re.search(r"timeout|timed out", log_lower):
            return FailureType.TIMEOUT

        return FailureType.UNKNOWN

    def _extract_error_messages(self, log_content: str) -> List[str]:
        """Extract error messages from log"""
        errors = []

        # Common error patterns
        patterns = [
            r"ERROR:.*",
            r"FAILED.*",
            r"Error:.*",
            r"Exception:.*",
            r"AssertionError.*",
            r"ImportError.*",
            r"ModuleNotFoundError.*",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, log_content, re.MULTILINE)
            errors.extend(matches)

        return list(set(errors))[:20]  # Deduplicate and limit

    def _extract_affected_files(self, log_content: str) -> List[str]:
        """Extract affected file paths from log"""
        files = []

        # Pattern for file paths
        file_patterns = [
            r"([a-zA-Z0-9_/]+\.py):\d+",
            r"File \"([^\"]+)\"",
            r"in ([a-zA-Z0-9_/]+\.py)",
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, log_content)
            files.extend(matches)

        # Filter to source files only
        source_files = [
            f for f in files
            if f.startswith(('src/', 'tests/', 'scripts/'))
        ]

        return list(set(source_files))[:10]  # Deduplicate and limit

    def _assess_severity(
        self,
        failure_type: FailureType,
        error_messages: List[str]
    ) -> SeverityLevel:
        """Assess severity of the failure"""
        # Security issues are always critical
        if failure_type == FailureType.SECURITY_VULNERABILITY:
            for msg in error_messages:
                if "CRITICAL" in msg.upper():
                    return SeverityLevel.CRITICAL
                if "HIGH" in msg.upper():
                    return SeverityLevel.HIGH
            return SeverityLevel.MEDIUM

        # Test failures are high priority
        if failure_type == FailureType.TEST_FAILURE:
            return SeverityLevel.HIGH

        # Build and import errors are high
        if failure_type in [FailureType.BUILD_ERROR, FailureType.IMPORT_ERROR]:
            return SeverityLevel.HIGH

        # Type errors and dependencies are medium
        if failure_type in [FailureType.TYPE_ERROR, FailureType.DEPENDENCY_ERROR]:
            return SeverityLevel.MEDIUM

        # Linting is low
        if failure_type == FailureType.LINTING_ERROR:
            return SeverityLevel.LOW

        return SeverityLevel.MEDIUM

    def _generate_suggestions(
        self,
        failure_type: FailureType,
        error_messages: List[str]
    ) -> List[str]:
        """Generate suggested fixes"""
        suggestions = []

        patterns = self.error_patterns.get(failure_type, [])

        for error_msg in error_messages:
            for pattern_info in patterns:
                if re.search(pattern_info["pattern"], error_msg, re.IGNORECASE):
                    suggestions.append(pattern_info["suggestion"])

        # Add generic suggestions based on type
        if failure_type == FailureType.LINTING_ERROR:
            suggestions.append("Run: black src/ tests/")
            suggestions.append("Run: isort src/ tests/")

        if failure_type == FailureType.IMPORT_ERROR:
            suggestions.append("Check import paths in affected files")
            suggestions.append("Verify __init__.py files exist")

        if failure_type == FailureType.TEST_FAILURE:
            suggestions.append("Run tests locally to reproduce")
            suggestions.append("Check test assertions and logic")

        return list(set(suggestions))  # Deduplicate

    def _is_auto_fixable(
        self,
        failure_type: FailureType,
        error_messages: List[str]
    ) -> bool:
        """Determine if failure can be auto-fixed"""
        # Security issues never auto-fix
        if failure_type == FailureType.SECURITY_VULNERABILITY:
            return False

        # Test failures usually need manual fix
        if failure_type == FailureType.TEST_FAILURE:
            # Unless it's just import issues
            if any("import" in msg.lower() for msg in error_messages):
                return True
            return False

        # Linting and formatting are auto-fixable
        if failure_type == FailureType.LINTING_ERROR:
            return True

        # Some import errors are auto-fixable
        if failure_type == FailureType.IMPORT_ERROR:
            return True

        # Dependencies might be auto-fixable
        if failure_type == FailureType.DEPENDENCY_ERROR:
            return True

        return False

    def _generate_title(
        self,
        failure_type: FailureType,
        severity: SeverityLevel
    ) -> str:
        """Generate issue title"""
        emoji = {
            SeverityLevel.CRITICAL: "🚨",
            SeverityLevel.HIGH: "⚠️",
            SeverityLevel.MEDIUM: "⚡",
            SeverityLevel.LOW: "ℹ️",
            SeverityLevel.INFO: "📝",
        }

        return (
            f"{emoji[severity]} CI Failure: "
            f"{failure_type.value.replace('-', ' ').title()} "
            f"[{severity.value.upper()}]"
        )

    def _generate_description(
        self,
        failure_type: FailureType,
        error_messages: List[str],
        affected_files: List[str]
    ) -> str:
        """Generate detailed description"""
        description_parts = [
            f"**Failure Type**: {failure_type.value}",
            f"\n**Affected Files**: {len(affected_files)}",
        ]

        if affected_files:
            description_parts.append("\n\nFiles:")
            for file in affected_files[:5]:
                description_parts.append(f"- `{file}`")

        if error_messages:
            description_parts.append("\n\n**Error Messages**:")
            for msg in error_messages[:3]:
                description_parts.append(f"```\n{msg}\n```")

        return "\n".join(description_parts)

    def analyze_workflow_run(
        self,
        workflow_data: Dict[str, Any]
    ) -> FailureReport:
        """
        Analyze GitHub workflow run data.

        Args:
            workflow_data: Workflow run data from GitHub API

        Returns:
            FailureReport with analysis
        """
        # Extract relevant information
        conclusion = workflow_data.get("conclusion", "unknown")
        logs = workflow_data.get("logs", "")
        branch = workflow_data.get("head_branch", "unknown")
        commit = workflow_data.get("head_sha", "unknown")

        context = {
            "branch": branch,
            "commit": commit,
            "conclusion": conclusion,
            "workflow_id": workflow_data.get("id"),
        }

        return self.analyze_log(logs, context)
