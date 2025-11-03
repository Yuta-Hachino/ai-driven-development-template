# AI Development Guidelines

**Target Audience**: AI assistants (Claude Code, GitHub Copilot, etc.) working on this project

**Purpose**: Prevent common mistakes and ensure consistent development practices

**Last Updated**: 2025-11-03

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Development Workflow](#development-workflow)
4. [Pre-Commit Checklist](#pre-commit-checklist)
5. [Common Pitfalls](#common-pitfalls)
6. [CI/CD Understanding](#cicd-understanding)
7. [Release Process](#release-process)
8. [Troubleshooting](#troubleshooting)

---

## 1. Project Overview

### What This Project Is

**Autonomous Dev CLI** - A Go-based CLI tool that orchestrates multiple Claude Code instances for parallel development.

- **Language**: Go 1.21+
- **Type**: CLI application (single binary)
- **Distribution**: npm, GitHub Releases, apt/yum
- **Architecture**: Language-agnostic orchestrator

### What This Project Is NOT

- ❌ NOT a Python project (Python code is archived)
- ❌ NOT Claude Code itself (it orchestrates Claude Code)
- ❌ NOT using Homebrew anymore (removed)
- ❌ NOT using Kubernetes (uses GitHub Actions)

### Directory Structure

```
.
├── cmd/autonomous-dev/       # CLI entry point
├── internal/
│   ├── cli/                  # CLI commands (init, start, status, etc.)
│   ├── config/               # Configuration management
│   ├── github/               # GitHub API client
│   └── template/             # Workflow templates
├── pkg/version/              # Version information
├── .github/workflows/
│   ├── ci.yml               # Go CI (tests, builds)
│   └── release.yml          # Automatic releases
├── docs/                     # Documentation
├── VERSION                   # Version file (0.1.0)
└── archive/                  # Old Python implementation
```

**IMPORTANT**: Only modify files in `cmd/`, `internal/`, `pkg/`, `.github/workflows/`, and root config files.

---

## 2. Technology Stack

### Primary Stack

- **Language**: Go 1.21
- **CLI Framework**: cobra
- **GitHub API**: go-github v56
- **Configuration**: YAML

### Dependencies

```bash
# Check current dependencies
go mod tidy
cat go.mod
```

### Deprecated/Archived

- ❌ Python 3.11 (archived in `archive/python-implementation/`)
- ❌ FastAPI (not used)
- ❌ Homebrew distribution (removed)

---

## 3. Development Workflow

### Standard Development Flow

```bash
# 1. Create feature branch (MUST start with 'claude/')
git checkout -b claude/your-feature-name-SESSION_ID

# 2. Make changes
# Edit code...

# 3. BEFORE COMMITTING - Run checks
go test ./...           # Run tests
go build ./cmd/...      # Verify build
gofmt -s -w .          # Format code
go vet ./...           # Static analysis

# 4. Commit with descriptive message
git add .
git commit -m "feat: Add new feature

Detailed description of changes...
"

# 5. Push to remote
git push -u origin claude/your-feature-name-SESSION_ID

# 6. Create PR to main
# Use GitHub UI or provide PR URL

# 7. After merge, release happens automatically
```

### Branch Naming Convention

**REQUIRED**: Branch names must start with `claude/` and end with session ID

```bash
# ✅ CORRECT
claude/fix-bug-011CUgao5VMcJ1Du3197VsFD
claude/add-feature-011CUgao5VMcJ1Du3197VsFD

# ❌ INCORRECT (will fail to push)
feature/fix-bug
fix-bug
main
```

### Branch Cleanup

**IMPORTANT**: Delete merged branches to keep the repository clean.

#### After PR is Merged

```bash
# 1. Check which branches are merged
git fetch origin main:main
git branch --merged main | grep claude/

# 2. Delete local merged branches
git branch -d claude/your-old-branch-SESSION_ID

# 3. Delete remote merged branches
git push origin --delete claude/your-old-branch-SESSION_ID
```

#### Automated Cleanup (Recommended)

```bash
# Delete all local merged branches (except current)
git branch --merged main | grep -v "\*" | grep claude/ | xargs -r git branch -d

# Delete corresponding remote branches
git branch -r --merged main | grep origin/claude/ | sed 's/origin\///' | xargs -r -I {} git push origin --delete {}
```

**Best Practice**: Clean up branches after every successful PR merge.

### Commit Message Format

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (gofmt)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance (dependencies, .gitignore)

**Examples**:
```
feat(cli): Add status command with real-time updates

fix(github): Fix API call arguments in logs.go

docs: Update installation guide for Go CLI

style: Apply gofmt formatting

chore: Add Go build artifacts to .gitignore
```

### Versioning

**IMPORTANT**: This project uses **automatic version bumping** based on commit messages.

**See full guide**: [VERSIONING_GUIDELINES.md](VERSIONING_GUIDELINES.md)

**Quick rules**:
- `feat!:` or `BREAKING CHANGE:` → **MAJOR** bump (1.0.0 → 2.0.0)
- `feat:` → **MINOR** bump (1.0.0 → 1.1.0)
- `fix:`, `docs:`, `chore:` → **PATCH** bump (1.0.0 → 1.0.1)

**Your commit messages automatically control version bumps!**

Example:
```bash
# This will trigger MINOR version bump (new feature)
git commit -m "feat: Add export command"

# This will trigger PATCH version bump (bug fix)
git commit -m "fix: Correct status display"

# This will trigger MAJOR version bump (breaking change)
git commit -m "feat!: Remove deprecated API"
```

When your PR is merged, the version is automatically updated and a release is created. No manual VERSION file editing needed!

---

## 4. Pre-Commit Checklist

**CRITICAL**: Run this checklist BEFORE every commit to prevent CI failures.

### Quick Checklist

```bash
# 1. Build succeeds
go build ./cmd/autonomous-dev

# 2. Tests pass
go test ./...

# 3. Code is formatted
gofmt -s -w .
git diff  # Should show no changes after format

# 4. No vet warnings
go vet ./...

# 5. No uncommitted binary files
git status | grep -E "autonomous-dev$|\.exe$|\.dylib$"
# Should return nothing

# 6. Clean working tree
git status
# Should not show untracked binaries
```

### Automated Pre-Commit Script

Save as `.git/hooks/pre-commit` (optional):

```bash
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Format code
gofmt -s -w .

# Run tests
go test ./...

# Run vet
go vet ./...

echo "✅ All checks passed"
```

---

## 5. Common Pitfalls

### Issue 1: Old Python Workflows Causing CI Failures

**Symptom**: CI fails with "pylint not found" or "Secret Scanning failed"

**Cause**: Old Python workflows still exist in `.github/workflows/`

**Solution**:
```bash
# Check for old workflows
ls -la .github/workflows/

# Should ONLY have:
# - ci.yml (Go CI)
# - release.yml (Release automation)

# Remove any other .yaml or .yml files:
# - auto-fix.yaml
# - auto-issue-on-failure.yaml
# - ci.yaml (Python version)
# - parallel-claude-execution.yml
# - p2p-autonomous-dev.yml
```

**Prevention**: After deleting workflows, commit immediately.

### Issue 2: Binary Files Tracked in Git

**Symptom**: git status shows `autonomous-dev` or `*.exe` files

**Cause**: Built binaries not in .gitignore

**Solution**:
```bash
# Check .gitignore includes:
grep -E "autonomous-dev|\.exe|\.dylib" .gitignore

# Should contain:
# autonomous-dev
# *.exe
# *.dll
# *.dylib
# *.test
# /bin/
# /pkg/

# If missing, add them and commit .gitignore
```

**Prevention**: Never commit binary files. Always check `git status` before committing.

### Issue 3: Go Build Errors (Type Mismatches)

**Symptom**: `cannot use true (untyped bool constant) as int value`

**Cause**: GitHub API v56 expects `int` for boolean parameters

**Common Location**: `internal/github/logs.go`

**Solution**:
```go
// ❌ WRONG
c.client.Actions.GetWorkflowRunLogs(..., true)

// ✅ CORRECT
c.client.Actions.GetWorkflowRunLogs(..., 1)  // 1 = true, 0 = false
```

**Prevention**: Check API documentation for parameter types.

### Issue 4: Formatting Errors in CI

**Symptom**: CI fails on "Check formatting" step

**Cause**: Code not formatted with gofmt

**Solution**:
```bash
# Format all code
gofmt -s -w .

# Verify no changes
git diff

# If changes exist, commit them
git add .
git commit -m "style: Apply gofmt formatting"
```

**Prevention**: ALWAYS run `gofmt -s -w .` before committing.

### Issue 5: Unused Imports

**Symptom**: Build fails with "imported and not used"

**Cause**: Imports added but not used in code

**Solution**:
```go
// Remove unused imports manually, or use goimports
import (
    "fmt"           // Used
    // "context"    // Unused - remove this
)
```

**Prevention**: Use IDE with Go support (removes unused imports automatically).

### Issue 6: Release Workflow Failures

**Symptom**: Release job fails with "tag not found"

**Cause**: Tag created locally but not pushed to remote

**Current Fix**: Workflow now automatically pushes tags (as of commit 6d53b34)

**Prevention**: If manually creating releases, always push tags:
```bash
git tag v1.0.0
git push origin v1.0.0  # ← Don't forget this!
```

---

## 6. CI/CD Understanding

### CI Workflow (`.github/workflows/ci.yml`)

**Triggers**: Push to `main`, `develop`, or `claude/*` branches, PRs to `main`

**Jobs**:
1. **test**: Run `go test ./...` with race detector
2. **build**: Build for 6 platforms (linux/darwin/windows × amd64/arm64)
3. **vet**: Run `go vet ./...`
4. **format**: Check `gofmt -s -l .` returns no files

**Expected Duration**: ~2 minutes

**Common Failures**:
- Test failures → Fix code
- Build failures → Check syntax, imports
- Vet warnings → Fix code issues
- Format failures → Run `gofmt -s -w .`

### Release Workflow (`.github/workflows/release.yml`)

**Triggers**:
1. Push to `main` branch (automatic)
2. Manual workflow dispatch
3. Tag push (backward compatible)

**Process**:
```
1. Read VERSION file (e.g., "0.1.0")
2. Check if tag v0.1.0 exists
   - If exists → Skip release
   - If new → Continue
3. Create & push tag v0.1.0
4. Run tests
5. Build binaries (6 platforms)
6. Create GitHub Release
7. Publish to npm (if NPM_TOKEN set)
8. Create Linux packages (.deb, .rpm, .apk)
```

**Expected Duration**: ~5 minutes

**Common Failures**:
- Tests fail → Fix tests before releasing
- GoReleaser fails → Check .goreleaser.yml syntax
- npm publish fails → Check NPM_TOKEN secret

---

## 7. Release Process

### Automatic Release (Recommended)

```bash
# 1. Update VERSION file
echo "0.2.0" > VERSION

# 2. Commit
git add VERSION
git commit -m "chore: Bump version to 0.2.0"

# 3. Create PR and merge to main
git push origin claude/bump-version-SESSION_ID
# Create PR on GitHub → Merge

# 4. Automatic release starts
# Wait ~5 minutes → v0.2.0 is live!
```

### Manual Release (Emergency)

```bash
# Only if GitHub Actions is down

# 1. Install GoReleaser
# See: https://goreleaser.com/install/

# 2. Create tag
git tag v0.2.0

# 3. Run GoReleaser
export GITHUB_TOKEN="your_token"
goreleaser release --clean

# 4. Manually publish to npm
cd npm
npm version 0.2.0 --no-git-tag-version
npm publish --access public
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features (backward compatible)
- **PATCH** (1.0.0 → 1.0.1): Bug fixes

---

## 8. Troubleshooting

### Build Fails Locally

```bash
# 1. Check Go version
go version  # Should be 1.21+

# 2. Clean build cache
go clean -cache

# 3. Download dependencies
go mod download

# 4. Verify dependencies
go mod verify

# 5. Try building again
go build ./cmd/autonomous-dev
```

### Tests Fail

```bash
# 1. Run tests with verbose output
go test -v ./...

# 2. Run specific package
go test -v ./internal/cli

# 3. Run with race detector
go test -race ./...
```

### CI Passes Locally But Fails on GitHub

**Likely causes**:
1. Uncommitted changes → `git status`
2. Different Go version → Check CI uses Go 1.21
3. Platform-specific code → Test on Linux (use Docker)

**Solution**:
```bash
# Test in Docker (same as CI)
docker run --rm -v $(pwd):/app -w /app golang:1.21 go test ./...
```

### Cannot Push to Remote

**Error**: `HTTP 403` or `permission denied`

**Cause**: Branch name doesn't start with `claude/`

**Solution**:
```bash
# Rename branch
git branch -m claude/your-branch-SESSION_ID
git push -u origin claude/your-branch-SESSION_ID
```

### Release Workflow Doesn't Trigger

**Check**:
1. Is VERSION file updated?
2. Did you push to `main` branch?
3. Check Actions tab on GitHub

**Manual trigger**:
```
GitHub → Actions → Release → Run workflow
Enter version: 0.2.0
```

---

## 📝 Quick Reference Card

### Before Every Commit

```bash
go test ./...       # Tests
go build ./cmd/...  # Build
gofmt -s -w .      # Format
go vet ./...       # Lint
git status         # Check for binaries
```

### Branch Names

```bash
# ✅ MUST start with claude/
claude/feature-name-SESSION_ID
```

### File Patterns to NEVER Commit

```
autonomous-dev      # Binary
*.exe, *.dll        # Windows binaries
*.dylib             # macOS libraries
*.test              # Test binaries
/bin/, /pkg/        # Build directories
```

### CI/CD Files

```
.github/workflows/ci.yml      # Go CI (tests, builds)
.github/workflows/release.yml # Automatic releases
VERSION                        # Version number
.goreleaser.yml               # Release configuration
```

### Branch Cleanup (After PR Merge)

```bash
# Delete merged branches
git branch --merged main | grep claude/ | xargs -r git branch -d
git push origin --delete claude/old-branch-name
```

### Getting Help

- Project docs: `docs/`
- CI logs: GitHub → Actions tab
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- This guide: `.ai/DEVELOPMENT_GUIDELINES.md`

---

## 🎯 Success Criteria

You're doing well if:

- ✅ All commits build successfully (`go build`)
- ✅ All tests pass (`go test ./...`)
- ✅ Code is formatted (`gofmt -s -l .` returns nothing)
- ✅ CI passes on GitHub (green checkmarks)
- ✅ No binary files in git status
- ✅ Branch names start with `claude/`
- ✅ Merged branches are deleted (clean repository)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-03
**Maintainer**: Autonomous Dev Team

