# Release Workflow Guide

Complete guide to the **fully automated** release workflow for Autonomous Dev CLI.

---

## 🎯 Overview

The release process is **100% automated** through GitHub Actions with automatic version bumping based on commit messages.

**Time to Release**: ~5 minutes (from PR merge to published release)

**Distributions**:
- GitHub Releases (binaries for 6 platforms)
- npm (coming soon - when NPM_TOKEN configured)
- deb/rpm/apk (Linux packages)

**How it Works**:
1. **You**: Write code with conventional commit messages
2. **GitHub Actions**: Automatically determines version bump (MAJOR/MINOR/PATCH)
3. **Auto Version Bump**: Updates VERSION file and commits to main
4. **Release Workflow**: Builds and publishes release

---

## 🚀 Quick Start (TL;DR)

**Just merge your PR with conventional commits - everything else is automatic!**

```bash
# 1. Write code with conventional commits
git commit -m "feat: Add new dashboard feature"
git commit -m "fix: Correct status display bug"

# 2. Create PR and merge to main
git push origin your-feature-branch

# 3. Auto magic! ✨
#    → Auto version bump (feat: = MINOR bump)
#    → VERSION updated (0.2.1 → 0.3.0)
#    → Release created automatically
```

**Done!** Check releases in ~5 minutes: https://github.com/Yuta-Hachino/ai-driven-development-template/releases

---

## 📋 Conventional Commits (Version Bump Rules)

Your commit messages control the version bump:

| Commit Type | Example | Version Bump | Example |
|-------------|---------|--------------|---------|
| `feat!:` or `BREAKING CHANGE:` | `feat!: Remove deprecated API` | **MAJOR** | 0.2.1 → 1.0.0 |
| `feat:` | `feat: Add export command` | **MINOR** | 0.2.1 → 0.3.0 |
| `fix:`, `docs:`, `chore:` | `fix: Correct error handling` | **PATCH** | 0.2.1 → 0.2.2 |

**See full guide**: [`.ai/VERSIONING_GUIDELINES.md`](../.ai/VERSIONING_GUIDELINES.md)

---

## 🔄 Automatic Release Flow

### Step 1: Development (You)

```bash
# Work on your feature
git checkout -b feature/amazing-feature

# Make commits with conventional format
git commit -m "feat: Add amazing feature"
git commit -m "docs: Update README"
git commit -m "test: Add feature tests"

# Push and create PR
git push origin feature/amazing-feature
```

### Step 2: PR Merge → Auto Version Bump

When your PR is merged to `main`:

```
1. Auto Version Bump Workflow triggers
   ↓
2. Analyzes all commits in the PR
   ├─ "feat:" found → MINOR bump
   ├─ "fix:" found → PATCH bump
   └─ "feat!:" found → MAJOR bump
   ↓
3. Updates VERSION file
   └─ Example: 0.2.1 → 0.3.0 (for feat:)
   ↓
4. Commits to main
   └─ "chore: Bump version to 0.3.0 [minor]"
   ↓
5. Comments on PR with new version
```

### Step 3: Release Workflow → Build & Publish

VERSION file change triggers release workflow:

```
1. Release Workflow triggers (VERSION changed)
   ↓
2. Creates git tag (v0.3.0)
   ↓
3. Runs tests
   ├─ If fail → stop ❌
   └─ If pass → continue ✓
   ↓
4. GoReleaser builds binaries
   ├─ macOS (Intel + ARM)
   ├─ Linux (amd64 + arm64)
   └─ Windows (amd64 + arm64)
   ↓
5. Creates GitHub Release with:
   ├─ Binary archives (.tar.gz, .zip)
   ├─ Linux packages (.deb, .rpm, .apk)
   ├─ Checksums (SHA256)
   └─ Auto-generated changelog
   ↓
6. Publishes to npm (if NPM_TOKEN set)
```

**Total time**: ~5 minutes from PR merge to published release

---

## 🎛️ Manual Release (Override)

If you need to manually trigger a release:

### Method 1: GitHub UI

1. Go to: https://github.com/Yuta-Hachino/ai-driven-development-template/actions/workflows/release.yml
2. Click "Run workflow"
3. Enter version (e.g., `0.3.0`)
4. Click "Run workflow" button ✅

### Method 2: Skip Auto Version Bump

Add `[skip version]` to PR title to prevent automatic version bump:

```
PR Title: "[skip version] Update documentation"
```

Then manually update VERSION and create release.

---

## 📖 Detailed Workflow

### Automated Workflows

#### 1. Auto Version Bump Workflow (`.github/workflows/auto-version-bump.yml`)

**Trigger**: PR closed (merged) to `main`

**Steps**:
```
1. Checkout main branch with full history
2. Get current VERSION (e.g., 0.2.1)
3. Fetch all commits from the merged PR
4. Analyze commit messages:
   ├─ Check for: feat!, fix!, BREAKING CHANGE:
   │  └─ Found → MAJOR bump (0.2.1 → 1.0.0)
   ├─ Check for: feat:
   │  └─ Found → MINOR bump (0.2.1 → 0.3.0)
   └─ Check for: fix:, docs:, chore:, etc.
      └─ Found → PATCH bump (0.2.1 → 0.2.2)
5. Update VERSION file with new version
6. Commit: "chore: Bump version to X.Y.Z [type]"
7. Push to main
8. Comment on PR with new version info
```

**Skip conditions**:
- PR title contains `[skip version]`
- No conventional commits found

#### 2. Release Workflow (`.github/workflows/release.yml`)

**Trigger**: Push to `main` with VERSION file changed

**Steps**:

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

---

## ✅ Verify Release

After ~5 minutes, verify the release was created successfully:

### GitHub Releases

1. **Go to**: https://github.com/Yuta-Hachino/ai-driven-development-template/releases
2. **Verify**: New release appears (e.g., `v0.3.0`)
3. **Check assets**:
   - [ ] `autonomous-dev_0.3.0_Linux_amd64.tar.gz`
   - [ ] `autonomous-dev_0.3.0_Darwin_arm64.tar.gz` (macOS Apple Silicon)
   - [ ] `autonomous-dev_0.3.0_Darwin_amd64.tar.gz` (macOS Intel)
   - [ ] `autonomous-dev_0.3.0_Windows_amd64.zip`
   - [ ] `autonomous-dev_0.3.0_amd64.deb` (Debian/Ubuntu)
   - [ ] `autonomous-dev_0.3.0_amd64.rpm` (Red Hat/Fedora)
   - [ ] `checksums.txt`
4. **Verify**: Changelog auto-generated from commits

### npm (If NPM_TOKEN configured)

```bash
# Check published version
npm view @autonomous-dev/cli version
# Expected: 0.3.0

# Install globally
npm install -g @autonomous-dev/cli

# Verify installation
autonomous-dev --version
# Expected: autonomous-dev version 0.3.0
```

**Note**: npm publishing requires `NPM_TOKEN` secret to be configured in GitHub repository settings.

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

## 🔄 Rollback & Hotfixes

### Rollback a Release

If a release has critical issues:

```bash
# 1. Delete the GitHub Release
# Go to: https://github.com/Yuta-Hachino/ai-driven-development-template/releases
# Click on release → Delete release

# 2. Delete the tag locally and remotely
git tag -d v0.3.0
git push origin :refs/tags/v0.3.0

# 3. Unpublish from npm (if published, within 72 hours)
npm unpublish @autonomous-dev/cli@0.3.0

# 4. Revert VERSION file if needed
echo "0.2.1" > VERSION
git add VERSION
git commit -m "chore: Revert to 0.2.1"
git push origin main
```

### Hotfix Release

For urgent bug fixes, just use conventional commits with `fix:`:

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug

# 2. Fix the bug with conventional commit
git commit -m "fix: Critical bug in start command"

# 3. Create PR and merge
# → Auto version bump: 0.3.0 → 0.3.1 (PATCH)
# → Release created automatically
```

**Fast track** (for very urgent fixes):

```bash
# Manually update VERSION and create release
echo "0.3.1" > VERSION
git add VERSION
git commit -m "chore: Bump version to 0.3.1 [patch]"
git push origin main
# → Release workflow triggers immediately
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
