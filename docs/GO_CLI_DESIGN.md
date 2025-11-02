# Autonomous Dev CLI - Go Implementation Design

## Overview

Language-agnostic CLI tool to orchestrate multiple Claude Code instances for parallel development.

**Target Platforms:**
- macOS (Intel & Apple Silicon)
- Linux (WSL, native)
- GitHub Actions (Linux)

**Distribution:**
- Homebrew (macOS/Linux)
- npm (binary wrapper)
- GitHub Releases (direct download)

---

## Architecture

```
autonomous-dev CLI (Go)
    ↓
GitHub API
    ↓
Trigger GitHub Actions workflows
    ↓
Multiple Claude Code instances (parallel execution)
```

**Key Point:** The CLI is just an orchestrator. All heavy lifting happens in GitHub Actions.

---

## Commands

### `autonomous-dev init`

Initialize autonomous development in an existing project.

```bash
cd my-existing-project
autonomous-dev init
```

**What it does:**
1. Create `.autonomous-dev/` directory
2. Generate `.autonomous-dev/config.yaml`
3. Create `.github/workflows/autonomous-dev.yml`
4. Add `.autonomous-dev/` to `.gitignore`

**Output:**
```
✓ Created .autonomous-dev/config.yaml
✓ Created .github/workflows/autonomous-dev.yml
✓ Updated .gitignore

Next steps:
1. Edit .autonomous-dev/config.yaml to configure instances
2. Commit and push the workflow file
3. Run: autonomous-dev start
```

---

### `autonomous-dev start`

Start parallel development with multiple Claude Code instances.

```bash
autonomous-dev start [--instances=5] [--task="feature description"]
```

**What it does:**
1. Read `.autonomous-dev/config.yaml`
2. Create GitHub Issue with task description
3. Trigger GitHub Actions workflow with `workflow_dispatch`
4. Pass instance count as parameter

**Output:**
```
✓ Created issue #123: "Implement user authentication"
✓ Triggered workflow run #456
✓ Started 5 Claude Code instances

Monitor progress:
  Dashboard: https://your-repo.github.io/autonomous-dev-dashboard
  Workflow: https://github.com/owner/repo/actions/runs/456
```

---

### `autonomous-dev status`

Check status of running instances.

```bash
autonomous-dev status
```

**What it does:**
1. Query GitHub API for latest workflow runs
2. Check issue comments for P2P messages
3. Display progress

**Output:**
```
Workflow Run #456 (in_progress)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instance 1 (leader)    ✓ Task 1 completed
Instance 2 (worker)    ⏳ Task 2 in progress (70%)
Instance 3 (worker)    ⏳ Task 3 in progress (30%)
Instance 4 (worker)    ⏳ Task 4 in progress (10%)
Instance 5 (worker)    ⏸ Waiting for task

Overall Progress: 3/10 tasks completed (30%)
```

---

### `autonomous-dev dashboard`

Open the monitoring dashboard in browser.

```bash
autonomous-dev dashboard
```

**What it does:**
1. Check if dashboard is deployed (GitHub Pages)
2. Open browser to dashboard URL
3. If not deployed, open local `dashboard/index.html`

---

### `autonomous-dev config`

Manage configuration.

```bash
autonomous-dev config set github.token <token>
autonomous-dev config set instances.default 5
autonomous-dev config get github.token
autonomous-dev config list
```

---

## Configuration File

`.autonomous-dev/config.yaml`:

```yaml
# GitHub repository
github:
  owner: "your-username"
  repo: "your-repo"
  token: "${GITHUB_TOKEN}"  # Or use env var

# Default settings
instances:
  default: 5
  max: 10

# Agent specializations
agents:
  - name: "frontend-specialist"
    skills: ["react", "typescript", "css"]
  - name: "backend-specialist"
    skills: ["api", "database", "performance"]
  - name: "test-specialist"
    skills: ["testing", "e2e", "unit-test"]

# Workflow settings
workflow:
  file: ".github/workflows/autonomous-dev.yml"
  concurrency: 5
```

---

## Project Structure

```
.
├── cmd/
│   └── autonomous-dev/
│       └── main.go              # CLI entry point
├── internal/
│   ├── cli/
│   │   ├── init.go              # init command
│   │   ├── start.go             # start command
│   │   ├── status.go            # status command
│   │   └── dashboard.go         # dashboard command
│   ├── config/
│   │   ├── config.go            # Config struct
│   │   └── loader.go            # YAML loader
│   ├── github/
│   │   ├── client.go            # GitHub API client
│   │   ├── workflow.go          # Workflow operations
│   │   └── issues.go            # Issue operations
│   └── template/
│       ├── workflow.yaml.tmpl   # GitHub Actions template
│       └── config.yaml.tmpl     # Config template
├── pkg/
│   └── version/
│       └── version.go           # Version info
├── go.mod
├── go.sum
├── Makefile
├── .goreleaser.yml              # Release automation
└── README.md
```

---

## Dependencies

```go
// go.mod
module github.com/autonomous-dev/cli

go 1.21

require (
    github.com/spf13/cobra v1.8.0        // CLI framework
    github.com/google/go-github/v56 v56.0.0  // GitHub API
    gopkg.in/yaml.v3 v3.0.1              // YAML parsing
    github.com/fatih/color v1.16.0       // Colored output
    github.com/briandowns/spinner v1.23.0    // Progress spinner
    golang.org/x/oauth2 v0.15.0          // GitHub auth
)
```

---

## GitHub Actions Workflow Template

`.github/workflows/autonomous-dev.yml`:

```yaml
name: Autonomous Development

on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number with task description'
        required: true
      instance_count:
        description: 'Number of parallel instances'
        required: false
        default: '5'

jobs:
  coordinate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        instance: [1, 2, 3, 4, 5]  # Generated dynamically
    steps:
      - uses: actions/checkout@v4

      - name: Run Claude Code Instance
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          INSTANCE_ID: ${{ matrix.instance }}
          ISSUE_NUMBER: ${{ inputs.issue_number }}
        run: |
          # Claude Code execution logic here
          echo "Instance $INSTANCE_ID processing issue #$ISSUE_NUMBER"
```

---

## Cross-Platform Support

### macOS
- Homebrew installation
- Support both Intel and Apple Silicon (universal binary)

### Linux (WSL & Native)
- Binary works on both
- No special WSL handling needed (Go binaries are portable)

### GitHub Actions
- Linux runner (ubuntu-latest)
- No installation needed (download binary in workflow)

---

## Distribution Strategy

### 1. GitHub Releases (Primary)

```bash
# GoReleaser builds for all platforms
goreleaser release --clean

# Outputs:
# - autonomous-dev_1.0.0_darwin_amd64.tar.gz
# - autonomous-dev_1.0.0_darwin_arm64.tar.gz
# - autonomous-dev_1.0.0_linux_amd64.tar.gz
# - autonomous-dev_1.0.0_linux_arm64.tar.gz
# - autonomous-dev_1.0.0_windows_amd64.zip
```

### 2. Homebrew

```ruby
# Formula/autonomous-dev.rb
class AutonomousDev < Formula
  desc "Multi-instance Claude Code orchestrator"
  homepage "https://github.com/autonomous-dev/cli"
  version "1.0.0"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_arm64.tar.gz"
      sha256 "..."
    else
      url "https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_amd64.tar.gz"
      sha256 "..."
    end
  end

  on_linux do
    url "https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_linux_amd64.tar.gz"
    sha256 "..."
  end

  def install
    bin.install "autonomous-dev"
  end
end
```

Install:
```bash
brew tap autonomous-dev/tap
brew install autonomous-dev
```

### 3. npm (Binary Wrapper)

```json
{
  "name": "@autonomous-dev/cli",
  "version": "1.0.0",
  "bin": {
    "autonomous-dev": "./bin/autonomous-dev.js"
  },
  "scripts": {
    "postinstall": "node scripts/install.js"
  }
}
```

`scripts/install.js`:
```javascript
const { execSync } = require('child_process');
const os = require('os');
const fs = require('fs');

const platform = os.platform();
const arch = os.arch();

let downloadUrl;
if (platform === 'darwin' && arch === 'arm64') {
  downloadUrl = 'https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_arm64.tar.gz';
} else if (platform === 'darwin' && arch === 'x64') {
  downloadUrl = 'https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_amd64.tar.gz';
} else if (platform === 'linux' && arch === 'x64') {
  downloadUrl = 'https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_linux_amd64.tar.gz';
}

// Download and extract binary
execSync(`curl -L ${downloadUrl} | tar xz -C ./bin`);
fs.chmodSync('./bin/autonomous-dev', 0o755);
```

Install:
```bash
npm install -g @autonomous-dev/cli
```

---

## Development Roadmap

### Phase 1: Core CLI (Week 1)
- [x] Project structure
- [ ] `init` command
- [ ] `start` command (basic)
- [ ] `status` command (basic)
- [ ] GitHub API integration
- [ ] Config file handling

### Phase 2: Workflow Integration (Week 2)
- [ ] Generate workflow files
- [ ] Trigger workflows via API
- [ ] Parse workflow status
- [ ] Issue creation/management

### Phase 3: Distribution (Week 3)
- [ ] GoReleaser setup
- [ ] Homebrew formula
- [ ] npm wrapper
- [ ] CI/CD for releases
- [ ] Documentation

### Phase 4: Testing & Polish (Week 4)
- [ ] Test on macOS (Intel & ARM)
- [ ] Test on Linux/WSL
- [ ] Test in GitHub Actions
- [ ] Error handling improvements
- [ ] User documentation

---

## Testing Strategy

```bash
# Unit tests
go test ./...

# Integration tests
go test -tags=integration ./...

# Cross-platform build test
make build-all

# End-to-end test
./test/e2e.sh
```

---

## Example Usage

```bash
# 1. Install
brew install autonomous-dev
# or
npm install -g @autonomous-dev/cli

# 2. Initialize in your project
cd ~/my-web-app
autonomous-dev init

# 3. Configure
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
autonomous-dev config set github.owner "myusername"
autonomous-dev config set github.repo "my-web-app"

# 4. Start development
autonomous-dev start --instances=5 --task="Add user authentication with OAuth"

# 5. Monitor
autonomous-dev status
autonomous-dev dashboard

# 6. Check results
# PRs will be automatically created
# Review and merge
```

---

## Success Criteria

✅ Single binary (no dependencies)
✅ Works on macOS, Linux, WSL, GitHub Actions
✅ Install via Homebrew or npm
✅ Simple 3-command workflow (init, start, status)
✅ Language-agnostic (works with any project)
✅ GitHub-native (no external servers)
