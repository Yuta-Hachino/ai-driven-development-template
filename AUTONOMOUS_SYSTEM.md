# Autonomous System Documentation

## Overview

The Autonomous Development System is designed to be fully self-healing and self-managing. This document describes the autonomous capabilities implemented in Phase 2.

## Self-Healing Architecture

### 1. Failure Detection

The system automatically detects failures through GitHub Actions webhooks:

```yaml
Trigger: CI/CD workflow completion
↓
Check: workflow.conclusion == 'failure'
↓
Action: Auto-issue workflow triggered
```

### 2. Failure Analysis

**FailureAnalyzer** (`src/autonomous/failure_analyzer.py`)

Analyzes failure logs and determines:
- Failure type (test, security, linting, etc.)
- Severity level (critical, high, medium, low)
- Auto-fix feasibility
- Affected files
- Suggested remediation steps

```python
from autonomous import FailureAnalyzer

analyzer = FailureAnalyzer()
report = analyzer.analyze_log(ci_logs)

# report.failure_type → FailureType.TEST_FAILURE
# report.severity → SeverityLevel.HIGH
# report.auto_fixable → True/False
# report.suggested_fixes → List[str]
```

### 3. Automatic Issue Creation

When a failure is detected, the system automatically:

1. **Creates a GitHub Issue**
   - Title based on failure type and severity
   - Detailed description with error messages
   - Labels (automated, ci-failure, priority)
   - Commands for manual intervention

2. **Updates Existing Issues**
   - If similar issue exists, adds a comment
   - Tracks failure frequency
   - Links to latest workflow run

### 4. Auto-Fix Workflows

**AutoHealer** (`src/autonomous/auto_healer.py`)

Automatically fixes common issues:

#### Supported Fix Strategies

| Strategy | Failure Type | Actions |
|----------|--------------|---------|
| **auto_format** | Linting errors | • Remove unused imports<br>• Sort imports with isort<br>• Format with black |
| **fix_imports** | Import errors | • Fix relative imports<br>• Update import paths<br>• Add __init__.py if missing |
| **update_dependencies** | Dependency conflicts | • Update pip<br>• Reinstall requirements |
| **fix_tests** | Test failures (import-related) | • Add @pytest.mark.asyncio<br>• Fix import statements |

#### Auto-Fix Process

```
1. Analyze failure
   ↓
2. Determine healing strategy
   ↓
3. Apply fixes
   ↓
4. Verify fixes (run tests + linting)
   ↓
5. Create PR with fixes
```

### 5. Pull Request Creation

When auto-fix succeeds:

1. **Create new branch**: `auto-fix/YYYYMMDD-HHMMSS-{type}`
2. **Commit changes** with detailed message
3. **Push to remote**
4. **Create Pull Request**:
   - Title: "🤖 Auto-fix: {failure_type} failures"
   - Description with fix details
   - Labels: automated, auto-fix
   - Draft if verification partial
   - Ready to merge if all checks pass

### 6. Verification

After applying fixes:

```python
# Run tests
pytest tests/ -v

# Check code quality
black --check src/ tests/

# Verify no new issues introduced
```

## Workflows

### Auto-Issue on Failure

**File**: `.github/workflows/auto-issue-on-failure.yaml`

**Trigger**: When CI/CD workflow completes with failure

**Actions**:
1. Analyze failure type
2. Create/update GitHub issue
3. Trigger auto-fix workflow (if applicable)
4. Send notifications for critical failures

### Auto-Fix Workflow

**File**: `.github/workflows/auto-fix.yaml`

**Triggers**:
1. `workflow_dispatch` - Manual trigger from failed workflow
2. `issue_comment` - Comment with `/auto-fix` command

**Process**:
1. Checkout code at failed commit
2. Analyze failure
3. Apply appropriate fixes
4. Verify fixes
5. Create PR if successful
6. Update issue with status

## CLI Commands

The autonomous system provides CLI commands for manual operation:

### Analyze Failures

```bash
# Analyze a failure log
autonomous-dev analyze logs/ci-failure.log

# Output:
# - Failure type
# - Severity level
# - Auto-fix feasibility
# - Suggested fixes
```

### Trigger Healing

```bash
# Attempt auto-heal from log
autonomous-dev heal logs/ci-failure.log

# Dry run (analyze only)
autonomous-dev heal logs/ci-failure.log --dry-run
```

### Check System Status

```bash
# Show system status
autonomous-dev status

# Output:
# - Active worktrees
# - Pattern distribution
# - Recent failures
# - Healing success rate
```

## Issue Commands

Users can interact with auto-created issues using commands:

### `/auto-fix`

Triggers automatic fix attempt:

```
/auto-fix
```

Response:
```
🤖 Auto-fix PR created: #123
Verification status: **success**
```

### `/assign-agent <agent-name>`

Assigns specific agent to handle the issue:

```
/assign-agent security_agent
```

### `/close`

Closes the issue if resolved externally:

```
/close
```

## Configuration

### Failure Patterns

Edit `src/autonomous/failure_analyzer.py` to add custom patterns:

```python
FailureType.CUSTOM_ERROR: [
    {
        "pattern": r"your_error_pattern",
        "severity": SeverityLevel.HIGH,
        "auto_fixable": True,
        "suggestion": "How to fix this error"
    }
]
```

### Healing Strategies

Add custom healing strategies in `src/autonomous/auto_healer.py`:

```python
async def _fix_custom_error(self) -> HealingResult:
    """Custom healing logic"""
    # Your fix implementation
    return HealingResult(
        success=True,
        strategy=HealingStrategy.CUSTOM,
        actions_taken=["Fixed custom error"],
        files_modified=[]
    )
```

## Monitoring

### Metrics Collected

- Failure detection rate
- Auto-fix success rate
- Average time to fix
- PR merge rate
- Issue resolution time

### Dashboards

Access dashboards at:
- GitHub Actions: Workflow runs
- Issues: Auto-created issues with label `automated`
- Pull Requests: Auto-fix PRs with label `auto-fix`

## Security Considerations

### What Gets Auto-Fixed

✅ **Safe to auto-fix**:
- Code formatting (black, isort)
- Import organization
- Unused import removal
- Simple test decorator additions

❌ **Never auto-fixed**:
- Security vulnerabilities
- Critical test failures
- Data loss risks
- Breaking API changes

### Manual Review Required

Certain failures always require manual review:

1. **Critical Security Vulnerabilities**
   - CVE with CRITICAL severity
   - Authentication/authorization issues
   - Data exposure risks

2. **High-Impact Failures**
   - Production outages
   - Data corruption
   - Integration breakages

3. **Complex Logic Errors**
   - Business logic failures
   - Algorithm correctness issues
   - State management problems

## Best Practices

### 1. Monitor Auto-Fix PRs

Review all auto-fix PRs even if CI passes:
- Check for unintended side effects
- Verify fix addresses root cause
- Ensure no security implications

### 2. Tune Failure Patterns

Regularly update failure patterns based on:
- New types of failures encountered
- False positive rates
- Auto-fix success rates

### 3. Set Up Notifications

Configure notifications for:
- Critical failures
- Auto-fix failures
- Security issues
- High error rates

### 4. Regular Audits

Audit autonomous system performance:
- Weekly: Review auto-fix success rate
- Monthly: Analyze failure patterns
- Quarterly: Update healing strategies

## Troubleshooting

### Auto-Fix Not Triggering

**Check**:
1. Workflow permissions (issues: write)
2. Branch protection rules
3. GitHub Actions enabled
4. Failure type is auto-fixable

### Fixes Not Working

**Debug**:
1. Check auto-fix workflow logs
2. Verify fix strategy selection
3. Review verification step output
4. Check file permissions

### PR Not Created

**Verify**:
1. Branch creation successful
2. Commit push successful
3. PR permissions
4. No conflicts with existing PRs

## Future Enhancements

Planned improvements:

- [ ] ML-based failure prediction
- [ ] Intelligent test selection
- [ ] Auto-revert on regression
- [ ] Cross-repo learning
- [ ] Performance optimization suggestions
- [ ] Cost optimization recommendations

## Support

For issues with the autonomous system:

1. Check workflow logs in GitHub Actions
2. Review auto-created issues
3. Examine auto-fix PR descriptions
4. Contact development team if needed

---

**Remember**: The autonomous system is designed to handle routine failures. Complex issues may still require human expertise and judgment.
