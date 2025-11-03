# Versioning Guidelines

**Purpose**: Ensure consistent and automatic version management using Semantic Versioning

**Last Updated**: 2025-11-03

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Semantic Versioning Rules](#semantic-versioning-rules)
3. [Automatic Version Bumping](#automatic-version-bumping)
4. [Manual Version Updates](#manual-version-updates)
5. [Commit Message Format](#commit-message-format)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

---

## 1. Overview

This project uses [Semantic Versioning 2.0.0](https://semver.org/) with **automatic version bumping** based on commit messages.

### Version Format

```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └─── Bug fixes, backward compatible
  │     └───────── New features, backward compatible
  └─────────────── Breaking changes, incompatible API
```

### Current Version

The current version is stored in the `VERSION` file at the repository root:

```bash
cat VERSION
# Output: 0.1.0
```

### Automatic vs Manual

| Method | When to Use | How It Works |
|--------|-------------|--------------|
| **Automatic** | Regular development (recommended) | Workflow analyzes PR commits and bumps version |
| **Manual** | Hotfixes, specific version needs | Developer updates VERSION file directly |

---

## 2. Semantic Versioning Rules

### MAJOR Version (Breaking Changes)

**Increment when**: Making incompatible API changes

**Examples**:
- Removing a CLI command
- Changing command arguments (breaking backward compatibility)
- Removing configuration options
- Changing API response format

**Commit prefix**: `feat!:`, `fix!:`, or `BREAKING CHANGE:` in commit body

```bash
# Example commit
feat!: Remove deprecated 'deploy' command

BREAKING CHANGE: The 'deploy' command has been removed. Use 'start' instead.
```

**Version change**: `1.5.3` → `2.0.0`

---

### MINOR Version (New Features)

**Increment when**: Adding functionality in a backward compatible manner

**Examples**:
- Adding a new CLI command
- Adding new configuration options
- Adding new features to existing commands
- Improving performance (non-breaking)

**Commit prefix**: `feat:`

```bash
# Example commit
feat: Add 'export' command for exporting results
```

**Version change**: `1.5.3` → `1.6.0`

---

### PATCH Version (Bug Fixes)

**Increment when**: Making backward compatible bug fixes

**Examples**:
- Fixing bugs
- Correcting documentation
- Refactoring code (no behavior change)
- Updating dependencies (security patches)

**Commit prefix**: `fix:`, `docs:`, `style:`, `refactor:`, `chore:`

```bash
# Example commits
fix: Correct error handling in status command
docs: Update installation instructions
chore: Update dependencies
```

**Version change**: `1.5.3` → `1.5.4`

---

## 3. Automatic Version Bumping

### How It Works

When a PR is merged to `main`, a workflow automatically:

1. **Analyzes commits** in the PR
2. **Determines version bump** based on commit types
3. **Updates VERSION file**
4. **Creates new commit** with version bump
5. **Triggers release** automatically

### Workflow Logic

```
Priority (highest to lowest):
1. BREAKING CHANGE → MAJOR bump
2. feat: → MINOR bump
3. fix: / docs: / chore: → PATCH bump
```

**Example**:

PR with these commits:
```
- feat: Add new export command
- fix: Correct status display
- docs: Update README
```

Result: **MINOR bump** (because `feat:` has higher priority than `fix:`)

### Configuration

The auto-version workflow runs automatically on PR merge. No configuration needed!

Location: `.github/workflows/auto-version-bump.yml`

---

## 4. Manual Version Updates

### When to Use Manual Updates

Use manual version updates for:

1. **Hotfixes** (urgent bug fixes)
2. **Initial releases** (0.1.0, 1.0.0)
3. **Specific version requirements** (aligning with external dependencies)
4. **Pre-release versions** (1.0.0-alpha.1, 1.0.0-beta.1)

### How to Manually Update

```bash
# 1. Update VERSION file
echo "1.2.0" > VERSION

# 2. Commit the change
git add VERSION
git commit -m "chore: Bump version to 1.2.0"

# 3. Create PR and merge
git push origin claude/bump-version-SESSION_ID

# 4. Release triggers automatically after merge
```

### Pre-release Versions

For alpha/beta releases:

```bash
# Alpha
echo "2.0.0-alpha.1" > VERSION

# Beta
echo "2.0.0-beta.1" > VERSION

# Release Candidate
echo "2.0.0-rc.1" > VERSION
```

**Note**: Pre-releases are marked as "pre-release" on GitHub automatically.

---

## 5. Commit Message Format

### Required Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types and Version Impact

| Type | Version Impact | Description | Example |
|------|---------------|-------------|---------|
| `feat!:` | **MAJOR** | Breaking change | `feat!: Remove old API` |
| `feat:` | **MINOR** | New feature | `feat: Add export command` |
| `fix:` | **PATCH** | Bug fix | `fix: Correct validation` |
| `docs:` | **PATCH** | Documentation | `docs: Update guide` |
| `style:` | **PATCH** | Formatting | `style: Apply gofmt` |
| `refactor:` | **PATCH** | Code restructure | `refactor: Simplify logic` |
| `test:` | **PATCH** | Tests | `test: Add unit tests` |
| `chore:` | **PATCH** | Maintenance | `chore: Update deps` |
| `perf:` | **PATCH** | Performance | `perf: Optimize query` |
| `ci:` | **PATCH** | CI/CD | `ci: Update workflow` |

### Breaking Changes

Two ways to indicate breaking changes:

#### Method 1: Exclamation mark

```bash
feat!: Remove deprecated commands
fix!: Change configuration format
```

#### Method 2: Footer

```bash
feat: Update API endpoint

BREAKING CHANGE: The /api/v1 endpoint has been removed. Use /api/v2 instead.
```

---

## 6. Examples

### Example 1: Feature Development (MINOR bump)

**Scenario**: Adding a new export feature

```bash
# Developer commits
git commit -m "feat: Add export command for results"
git commit -m "test: Add tests for export command"
git commit -m "docs: Document export command usage"

# Create PR and merge to main

# Automatic version bump:
# 0.1.0 → 0.2.0

# Automatic release:
# v0.2.0 created and published
```

---

### Example 2: Bug Fix (PATCH bump)

**Scenario**: Fixing a bug in status command

```bash
# Developer commits
git commit -m "fix: Correct status command output format"

# Create PR and merge to main

# Automatic version bump:
# 0.2.0 → 0.2.1

# Automatic release:
# v0.2.1 created and published
```

---

### Example 3: Breaking Change (MAJOR bump)

**Scenario**: Removing deprecated API

```bash
# Developer commits
git commit -m "feat!: Remove deprecated 'deploy' command

BREAKING CHANGE: The 'deploy' command has been removed.
Use 'start --deploy' instead.
"

# Create PR and merge to main

# Automatic version bump:
# 0.2.1 → 1.0.0

# Automatic release:
# v1.0.0 created and published
```

---

### Example 4: Multiple Commits (Highest Priority Wins)

**Scenario**: PR with mixed commit types

```bash
# PR contains:
git commit -m "feat: Add new dashboard view"
git commit -m "fix: Correct error handling"
git commit -m "docs: Update README"
git commit -m "chore: Update dependencies"

# Commit types: feat (MINOR), fix (PATCH), docs (PATCH), chore (PATCH)
# Highest priority: feat → MINOR bump

# Version bump:
# 1.0.0 → 1.1.0
```

---

### Example 5: Documentation Only (PATCH bump)

**Scenario**: Only updating documentation

```bash
# Developer commits
git commit -m "docs: Add installation guide"
git commit -m "docs: Update troubleshooting"

# Create PR and merge to main

# Automatic version bump:
# 1.1.0 → 1.1.1

# Automatic release:
# v1.1.1 created and published
```

---

## 7. Troubleshooting

### Issue: Version didn't bump after PR merge

**Possible causes**:

1. **No valid commit types**: All commits use non-standard prefixes
2. **Workflow not triggered**: Check GitHub Actions

**Solution**:

```bash
# Check commit messages in PR
git log main~10..main --oneline

# All commits should follow conventional format
# If not, manually bump version:
echo "0.3.0" > VERSION
git commit -m "chore: Manual version bump to 0.3.0"
```

---

### Issue: Wrong version bump (MINOR instead of PATCH)

**Cause**: A commit used `feat:` instead of `fix:`

**Solution**:

```bash
# Manually correct version
echo "0.2.2" > VERSION  # Instead of 0.3.0
git commit -m "chore: Correct version to 0.2.2"
```

**Prevention**: Review commit messages during PR review

---

### Issue: Need to skip auto-version for a PR

**Solution**: Add `[skip version]` to PR title or merge commit message

```bash
# In PR title
"docs: Update guide [skip version]"

# Or in merge commit
git merge --no-ff -m "Merge PR #123 [skip version]"
```

---

### Issue: Version bumped but release failed

**Cause**: Release workflow needs VERSION file change to trigger

**Check**:
```bash
# Was VERSION file actually changed in the PR?
git diff HEAD~1 HEAD -- VERSION
```

**Solution**: Version bump commit should have been created automatically. If not:

```bash
# Manually create version bump commit
echo "0.3.0" > VERSION
git commit -m "chore: Bump version to 0.3.0"
git push origin main
```

---

## 📝 Quick Reference

### Version Bump Decision Tree

```
Start: Merge PR to main
  │
  ├─ Contains BREAKING CHANGE? ─────> MAJOR bump (X.0.0)
  │
  ├─ Contains feat: commits? ───────> MINOR bump (0.X.0)
  │
  ├─ Contains fix: commits? ────────> PATCH bump (0.0.X)
  │
  ├─ Contains docs: commits? ───────> PATCH bump (0.0.X)
  │
  └─ Contains chore: commits? ──────> PATCH bump (0.0.X)
```

### Commit Type Cheat Sheet

```bash
# Breaking change
git commit -m "feat!: Remove old API"

# New feature
git commit -m "feat: Add export command"

# Bug fix
git commit -m "fix: Correct validation"

# Documentation
git commit -m "docs: Update README"

# Refactoring
git commit -m "refactor: Simplify code"

# Tests
git commit -m "test: Add unit tests"

# Maintenance
git commit -m "chore: Update deps"
```

### Version File Location

```bash
./VERSION
```

### Check Current Version

```bash
cat VERSION
```

### Latest Release

```bash
git tag -l | tail -1
# or
gh release list | head -1
```

---

## 🎯 Best Practices

1. **Use conventional commits**: Always follow the format
2. **One type per commit**: Don't mix `feat` and `fix` in same commit
3. **Review commit messages**: During PR review, check message format
4. **Breaking changes are rare**: Think twice before using `!` or `BREAKING CHANGE`
5. **Document breaking changes**: Always explain what broke and how to migrate
6. **Test before releasing**: CI should pass before version bump
7. **Keep VERSION file clean**: No manual edits unless necessary

---

## 📚 References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Release Workflow Guide](../docs/RELEASE_WORKFLOW.md)
- [Development Guidelines](.ai/DEVELOPMENT_GUIDELINES.md)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-03
**Maintainer**: Autonomous Dev Team
