# Release Workflow Guide

Complete guide to the automated release workflow for Autonomous Dev CLI.

---

## Overview

The release process is **fully automated** through GitHub Actions. When a PR is merged to `main`, a new release is automatically created based on the `VERSION` file.

**Time to Release**: ~5 minutes (fully automated)

**Distributions**:
- GitHub Releases (binaries for 6 platforms)
- npm (all platforms)
- apt/yum (Linux packages)

**Trigger Methods**:
1. **Automatic**: Merge PR to `main` (recommended)
2. **Manual**: Run workflow from GitHub UI
3. **Legacy**: Push version tag (backward compatible)

---

## Quick Release (TL;DR)

### Method 1: Automatic (Recommended)

```bash
# 1. Update VERSION file in your branch
echo "0.2.0" > VERSION
git add VERSION
git commit -m "chore: Bump version to 0.2.0"

# 2. Create PR and merge to main
git push origin your-feature-branch

# 3. Merge PR on GitHub → Release automatically triggers! ✅
```

### Method 2: Manual Trigger

1. Go to: https://github.com/your-org/your-repo/actions/workflows/release.yml
2. Click "Run workflow"
3. Enter version (e.g., `0.2.0`)
4. Click "Run workflow" button ✅

---

## Detailed Workflow

### Step 1: Decide on Version Number

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes, incompatible API
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Step 2: Update VERSION File

In your feature branch:

```bash
# Update VERSION file
echo "1.2.0" > VERSION

# Commit the change
git add VERSION
git commit -m "chore: Bump version to 1.2.0"
```

**Important**: The `VERSION` file contains only the version number (no `v` prefix).

### Step 3: Create PR and Merge

```bash
# Push your branch
git push origin feature/my-feature

# Create PR on GitHub
# Review, approve, merge to main
```

### Step 4: Automated Release Process

Once merged to `main`, `.github/workflows/release.yml` is triggered automatically:

#### Job 1: `goreleaser` (Build & Publish Binaries)

```
1. Checkout repository with full git history
2. Read version from VERSION file
3. Check if tag v{VERSION} already exists
   ├─ If exists → skip release ⏭️
   └─ If new → continue ✓
4. Create git tag v{VERSION}
5. Setup Go 1.21 environment
6. Run tests (go test ./...)
   ├─ If tests fail → workflow stops ❌
   └─ If tests pass → continue ✓
7. Execute GoReleaser
   ├─ Build binaries (6 platforms)
   │  ├─ linux/amd64
   │  ├─ linux/arm64
   │  ├─ darwin/amd64 (macOS Intel)
   │  ├─ darwin/arm64 (macOS Apple Silicon)
   │  ├─ windows/amd64
   │  └─ windows/arm64
   ├─ Create archives (.tar.gz, .zip)
   ├─ Generate checksums (SHA256)
   ├─ Create GitHub Release
   │  ├─ Upload binaries
   │  ├─ Upload checksums
   │  └─ Generate changelog
   └─ Create Linux packages
      ├─ .deb (Debian/Ubuntu)
      ├─ .rpm (Red Hat/Fedora)
      └─ .apk (Alpine)
```

#### Job 2: `update-npm` (Publish to npm)

Runs after `goreleaser` completes successfully:

```
1. Checkout repository
2. Setup Node.js 18 environment
3. Update package.json version
   ├─ Extract version from tag (v1.0.1 → 1.0.1)
   └─ Run: npm version $VERSION --no-git-tag-version
4. Publish to npm registry
   └─ Run: npm publish --access public
```

### Step 4: Verify Release

After ~5 minutes, verify the release:

#### GitHub Releases

1. Go to https://github.com/autonomous-dev/cli/releases
2. Verify new release appears (e.g., `v1.0.1`)
3. Check assets:
   - [ ] `autonomous-dev_1.0.1_linux_amd64.tar.gz`
   - [ ] `autonomous-dev_1.0.1_darwin_arm64.tar.gz`
   - [ ] `autonomous-dev_1.0.1_windows_amd64.zip`
   - [ ] `checksums.txt`
   - [ ] Other platform binaries

#### npm

```bash
# Check published version
npm view @autonomous-dev/cli version
# Output: 1.0.1

# Install/update
npm install -g @autonomous-dev/cli
# or
npm update -g @autonomous-dev/cli

# Verify
autonomous-dev --version
# Output: autonomous-dev version 1.0.1
```

---

## Configuration Requirements

### GitHub Repository Secrets

Set these in GitHub repository settings → Secrets and variables → Actions:

| Secret Name | Required | Purpose | How to Get |
|------------|----------|---------|------------|
| `GITHUB_TOKEN` | ✅ Auto | GitHub Releases, workflow logs | Automatically provided by GitHub |
| `NPM_TOKEN` | ✅ | Publish to npm | [Create at npmjs.com](https://www.npmjs.com/settings/~/tokens) |

#### Creating NPM_TOKEN

1. Go to https://www.npmjs.com/
2. Login → Account Settings → Access Tokens
3. Click **"Generate New Token"** → **"Automation"**
4. Copy token (starts with `npm_`)
5. Add to GitHub Secrets as `NPM_TOKEN`

---

## Rollback & Hotfixes

### Rollback a Release

If a release has critical issues:

```bash
# 1. Delete the GitHub Release
# Go to: https://github.com/autonomous-dev/cli/releases
# Click on release → Delete release

# 2. Delete the tag locally and remotely
git tag -d v1.0.1
git push origin :refs/tags/v1.0.1

# 3. Unpublish from npm (within 72 hours)
npm unpublish @autonomous-dev/cli@1.0.1
```

### Hotfix Release

For urgent bug fixes:

```bash
# 1. Create hotfix branch from tag
git checkout -b hotfix/1.0.2 v1.0.1

# 2. Fix the bug
vim internal/cli/start.go
git commit -m "fix: Critical bug in start command"

# 3. Merge to main
git checkout main
git merge hotfix/1.0.2

# 4. Create hotfix tag
git tag v1.0.2
git push origin v1.0.2

# 5. Release happens automatically
```

---

## Development Workflow Integration

### Complete Development Cycle

```
┌─────────────────────────────────────────────────────────┐
│ 1. Feature Development                                  │
│    $ git checkout -b feature/new-command                │
│    $ git commit -m "feat: Add new command"              │
│    $ git push origin feature/new-command                │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Pull Request & CI                                    │
│    - Create PR on GitHub                                │
│    - .github/workflows/ci.yml runs:                     │
│      ✓ go test (with race detector)                    │
│      ✓ go vet (code quality)                           │
│      ✓ gofmt (formatting check)                        │
│      ✓ Multi-platform build verification              │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Code Review & Merge                                  │
│    - Reviewer approves PR                               │
│    - Merge to main branch                               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Accumulate Changes                                   │
│    - Multiple features/fixes merged to main             │
│    - Decide when to release (daily/weekly/on-demand)    │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Release Decision                                     │
│    $ git tag v1.1.0                                     │
│    $ git push origin v1.1.0                             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Automated Release (.github/workflows/release.yml)   │
│    ✓ Run tests                                         │
│    ✓ Build 6 platform binaries                        │
│    ✓ Create GitHub Release                            │
│    ✓ Publish to npm                                   │
│    ✓ Create Linux packages (.deb/.rpm/.apk)           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 7. Users Update                                         │
│    $ npm update -g @autonomous-dev/cli                  │
└─────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Release Workflow Fails

#### Problem: Tests fail during release

```
Error: go test ./... exited with code 1
```

**Solution**:
```bash
# Run tests locally
go test ./...

# Fix failing tests
# Commit and push to main
# Delete and recreate tag
git tag -d v1.0.1
git push origin :refs/tags/v1.0.1
git tag v1.0.1
git push origin v1.0.1
```

#### Problem: GoReleaser fails

```
Error: goreleaser failed
```

**Solution**:
```bash
# Test GoReleaser locally (dry-run)
goreleaser release --snapshot --rm-dist

# Check .goreleaser.yml syntax
# Fix issues and retry release
```

#### Problem: npm publish fails

```
Error: You do not have permission to publish
```

**Solution**:
1. Verify `NPM_TOKEN` is set correctly in GitHub Secrets
2. Check npm token has "Automation" type
3. Ensure you're a collaborator on `@autonomous-dev` npm organization

### Manual Release (Emergency)

If GitHub Actions is down or you need to release manually:

```bash
# 1. Install GoReleaser
# See: https://goreleaser.com/install/

# 2. Create tag
git tag v1.0.1

# 3. Run GoReleaser locally
export GITHUB_TOKEN="ghp_xxxx"
goreleaser release --clean

# 4. Manually publish to npm
cd npm
npm version 1.0.1 --no-git-tag-version
npm publish --access public
```

---

## Best Practices

### Version Numbering

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes, incompatible API
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Release Frequency

**Recommended**:
- **Patch releases**: As needed for critical bugs (within hours)
- **Minor releases**: Weekly or bi-weekly for new features
- **Major releases**: Quarterly or when breaking changes are necessary

**Too Frequent** (❌): Daily releases confuse users
**Too Infrequent** (❌): Users wait months for bug fixes

### Pre-Release Versions

For beta/alpha releases:

```bash
# Alpha release
git tag v2.0.0-alpha.1
git push origin v2.0.0-alpha.1

# Beta release
git tag v2.0.0-beta.1
git push origin v2.0.0-beta.1

# Release candidate
git tag v2.0.0-rc.1
git push origin v2.0.0-rc.1
```

GoReleaser will automatically mark these as "pre-release" on GitHub.

### Changelog Maintenance

Keep `CHANGELOG.md` updated:

```markdown
# Changelog

## [1.0.1] - 2025-11-03

### Fixed
- Fixed config loading issue when path contains spaces

### Changed
- Improved error messages for GitHub API failures

## [1.0.0] - 2025-11-02

### Added
- Initial release with Go CLI
- Multi-instance orchestration
- P2P coordination via GitHub Issues
- Real-time dashboard
```

---

## Summary

✅ **Automated Release Process**:
1. Developer creates tag: `git tag v1.0.1 && git push origin v1.0.1`
2. GitHub Actions builds and publishes automatically
3. Users update: `npm update -g @autonomous-dev/cli`

✅ **Zero Manual Steps** (after initial setup)

✅ **Multi-Platform Support**: macOS, Linux, Windows (6 architectures)

✅ **Multi-Channel Distribution**: GitHub Releases, npm, apt/yum

✅ **Fast**: ~5 minutes from tag push to user availability

---

**Next**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for development workflow
