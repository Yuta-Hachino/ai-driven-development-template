# Autonomous Dev CLI

> **Multi-instance Claude Code orchestrator for parallel development**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/Go-1.21+-blue.svg)](https://golang.org/dl/)

A language-agnostic CLI tool that orchestrates multiple Claude Code instances for parallel autonomous development on **any project**.

---

## 🎯 What is Autonomous Dev?

Autonomous Dev is a **command-line tool** that turns **1 developer** into a **team of 5 AI developers** working in parallel.

```
You → autonomous-dev start --instances=5 --task="Add user authentication"
  ↓
GitHub Actions launches 5 Claude Code instances
  ↓
Instance 1 (Leader): Coordinates the team
Instance 2: Builds OAuth integration
Instance 3: Creates login UI
Instance 4: Writes tests
Instance 5: Updates documentation
  ↓
30 minutes later: 5 Pull Requests ready for review
```

**Key Features:**
- ✅ **$0/month** - Runs on GitHub Actions (free tier)
- ✅ **Language-agnostic** - Works with Python, JavaScript, Go, Rust, Java, etc.
- ✅ **Zero dependencies** - Single binary, no runtime required
- ✅ **P2P coordination** - Instances collaborate through GitHub Issues
- ✅ **Real-time dashboard** - Monitor progress in your browser
- ✅ **Cross-platform** - macOS, Linux, WSL, GitHub Actions

---

## 🚀 Quick Start

### 1. Install

**macOS/Linux (Homebrew):**
```bash
brew tap autonomous-dev/tap
brew install autonomous-dev
```

**npm (Any OS):**
```bash
npm install -g @autonomous-dev/cli
```

**Direct download:**
```bash
# Linux
curl -L https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_linux_amd64.tar.gz | tar xz
sudo mv autonomous-dev /usr/local/bin/

# macOS (Apple Silicon)
curl -L https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_arm64.tar.gz | tar xz
sudo mv autonomous-dev /usr/local/bin/
```

### 2. Initialize in Your Project

```bash
cd ~/my-existing-project
autonomous-dev init
```

This creates:
- `.autonomous-dev/config.yaml` - Configuration file
- `.github/workflows/autonomous-dev.yml` - GitHub Actions workflow

### 3. Set GitHub Token

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

Create token at: https://github.com/settings/tokens (scopes: `repo`, `workflow`)

### 4. Start Autonomous Development

```bash
autonomous-dev start --instances=5 --task="Add user authentication with OAuth 2.0"
```

### 5. Monitor Progress

```bash
# Check status
autonomous-dev status

# Open dashboard
autonomous-dev dashboard
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/QUICK_START.md) | Get started in 5 minutes |
| [Installation Guide](docs/INSTALLATION.md) | Detailed installation instructions |
| [P2P Monitoring](docs/P2P_MONITORING.md) | How instances coordinate and monitor each other |
| [Dashboard Guide](docs/DASHBOARD_GUIDE.md) | Using the web dashboard |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [Go CLI Design](docs/GO_CLI_DESIGN.md) | Technical design and architecture |

---

## 🏗️ How It Works

### Architecture

```
┌──────────────────────────────────────────────┐
│ Your Computer                                │
│                                              │
│  $ autonomous-dev start --instances=5       │
│                                              │
└──────────────────┬───────────────────────────┘
                   ↓
         ┌─────────────────────┐
         │ GitHub API          │
         │ - Create Issue      │
         │ - Trigger Workflow  │
         └─────────────────────┘
                   ↓
┌──────────────────────────────────────────────┐
│ GitHub Actions (Free Tier)                   │
│                                              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐    │
│  │Inst 1│  │Inst 2│  │Inst 3│  │Inst 4│... │
│  │Leader│  │Worker│  │Worker│  │Worker│    │
│  └───┬──┘  └───┬──┘  └───┬──┘  └───┬──┘    │
│      │         │         │         │        │
│      └─────────┴─────────┴─────────┘        │
│                 ↓                            │
└─────────────────┼────────────────────────────┘
                  ↓
       ┌──────────────────────┐
       │ GitHub Issue         │
       │ (P2P Message Bus)    │
       │                      │
       │ - Status updates     │
       │ - Task assignments   │
       │ - Health checks      │
       └──────────────────────┘
                  ↓
       ┌──────────────────────┐
       │ Dashboard            │
       │ (GitHub Pages - $0)  │
       │                      │
       │ - Instance status    │
       │ - Console logs       │
       │ - Progress metrics   │
       └──────────────────────┘
```

### Workflow

1. **CLI triggers GitHub Actions** via GitHub API
2. **5 instances launch** in parallel (1 leader + 4 workers)
3. **Leader coordinates** - assigns tasks, monitors workers
4. **Workers execute** - write code, run tests, create PRs
5. **P2P communication** - via structured GitHub Issue comments
6. **Real-time monitoring** - dashboard shows live progress
7. **PRs created** - ready for human review

---

## 💻 CLI Commands

### `autonomous-dev init`

Initialize autonomous development in the current project.

```bash
autonomous-dev init
```

**What it does:**
- Detects Git repository (owner/repo)
- Creates `.autonomous-dev/config.yaml`
- Generates `.github/workflows/autonomous-dev.yml`
- Updates `.gitignore`

---

### `autonomous-dev start`

Start parallel development with multiple instances.

```bash
autonomous-dev start [flags]
```

**Flags:**
- `-n, --instances <count>` - Number of instances (default: 5)
- `-t, --task <description>` - Task description (required)

**Example:**
```bash
autonomous-dev start \
  --instances=3 \
  --task="Refactor authentication module to use JWT tokens"
```

---

### `autonomous-dev status`

Check status of running instances.

```bash
autonomous-dev status
```

**Output:**
```
Workflow Run # 456 (in_progress)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: in_progress
Started: 2025-11-02 12:30:45
URL: https://github.com/owner/repo/actions/runs/456

Instances:
✓ Instance 1 (leader) completed
⏳ Instance 2 (worker) in_progress
⏳ Instance 3 (worker) in_progress
⏳ Instance 4 (worker) in_progress
⏸ Instance 5 (worker) queued

Overall Progress: 1/5 instances completed (20%)
```

---

### `autonomous-dev dashboard`

Open the monitoring dashboard in your browser.

```bash
autonomous-dev dashboard
```

Opens `dashboard/index.html` or GitHub Pages URL.

---

### `autonomous-dev config`

Manage configuration.

```bash
# Set value
autonomous-dev config set github.token "ghp_xxxx"

# Get value
autonomous-dev config get github.owner

# List all
autonomous-dev config list
```

---

## 📊 Dashboard Features

### Main Dashboard (`dashboard/index.html`)

**3 Tabs:**
1. **Overview** - Workflow summary, instance grid, progress chart
2. **Workflows** - Recent workflow runs, success rate
3. **P2P Messages** - Inter-instance communication log

**Features:**
- Real-time updates (5-second polling)
- Instance status grid
- Progress charts (Chart.js)
- GitHub Actions integration
- Mobile responsive

### Instance Detail View (`dashboard/instance-detail.html`)

**Per-instance monitoring:**
- Current task and progress (0-100%)
- Health metrics (CPU, memory, heartbeat)
- Console output (real-time)
- Full logs viewer
- Status history timeline

**Access:** Click on any instance in the main dashboard

---

## 🔧 Configuration

`.autonomous-dev/config.yaml`:

```yaml
github:
  owner: "your-username"
  repo: "your-repo"
  token: "${GITHUB_TOKEN}"  # Or direct value

instances:
  default: 5
  max: 10

agents:
  - name: "frontend-specialist"
    skills: ["react", "typescript", "css"]
  - name: "backend-specialist"
    skills: ["api", "database", "performance"]
  - name: "test-specialist"
    skills: ["testing", "e2e", "unit-test"]

workflow:
  file: ".github/workflows/autonomous-dev.yml"
  concurrency: 5
```

---

## 🎯 Use Cases

### 1. Feature Development

```bash
autonomous-dev start --instances=5 --task="Add dark mode toggle with theme persistence"
```

**Result:**
- Instance 1: Coordinates
- Instance 2: CSS theme variables
- Instance 3: React context provider
- Instance 4: LocalStorage integration
- Instance 5: Tests + Storybook stories

### 2. Refactoring

```bash
autonomous-dev start --instances=3 --task="Migrate class components to functional components with hooks"
```

**Result:**
- 3 instances refactor different modules in parallel
- Faster completion (3x speed)

### 3. Testing

```bash
autonomous-dev start --instances=4 --task="Add E2E tests for checkout flow"
```

**Result:**
- Each instance writes tests for different checkout steps
- Comprehensive test coverage

### 4. Documentation

```bash
autonomous-dev start --instances=2 --task="Update API documentation for v2.0 endpoints"
```

---

## 🆚 Comparison

| Approach | Time | Cost | Quality |
|----------|------|------|---------|
| **1 human developer** | 5 days | $$ | Good |
| **1 Claude Code** | 2 days | $ | Good |
| **5 Claude Code (Autonomous Dev)** | 8 hours | $0* | Excellent |

*Using GitHub Actions free tier (2,000 minutes/month)

---

## 🔐 Security

- ✅ **No data leaves GitHub** - Everything on GitHub infrastructure
- ✅ **Token stored locally** - Never sent to third parties
- ✅ **Audit trail** - All actions logged in GitHub Issues
- ✅ **PR review required** - Human approval before merge

---

## 🌍 Platform Support

| Platform | Support | Installation |
|----------|---------|--------------|
| **macOS** (Intel) | ✅ | Homebrew, npm, binary |
| **macOS** (Apple Silicon) | ✅ | Homebrew, npm, binary |
| **Linux** (Ubuntu/Debian) | ✅ | Homebrew, npm, binary |
| **Linux** (WSL) | ✅ | Homebrew, npm, binary |
| **Windows** | ⚠️ | npm, binary (limited testing) |
| **GitHub Actions** | ✅ | Direct binary download |

---

## 🛠️ Development

### Build from Source

```bash
# Clone repository
git clone https://github.com/autonomous-dev/cli.git
cd cli

# Install dependencies
go mod download

# Build
make build

# Run
./autonomous-dev --version
```

### Build for All Platforms

```bash
make build-all
```

Outputs to `dist/`:
- `autonomous-dev_darwin_amd64` (macOS Intel)
- `autonomous-dev_darwin_arm64` (macOS Apple Silicon)
- `autonomous-dev_linux_amd64` (Linux)
- `autonomous-dev_windows_amd64.exe` (Windows)

---

## 📦 Project Structure

```
.
├── cmd/
│   └── autonomous-dev/
│       └── main.go              # CLI entry point
├── internal/
│   ├── cli/                     # Command implementations
│   │   ├── init.go
│   │   ├── start.go
│   │   ├── status.go
│   │   ├── dashboard.go
│   │   └── config.go
│   ├── config/                  # Configuration management
│   ├── github/                  # GitHub API client
│   │   ├── client.go
│   │   └── logs.go
│   └── template/                # Workflow templates
├── pkg/
│   └── version/                 # Version info
├── dashboard/
│   ├── index.html               # Main dashboard
│   └── instance-detail.html     # Instance detail view
├── scripts/
│   └── instance-status-reporter.sh  # Status reporting
├── docs/                        # Documentation
├── .devcontainer/               # VS Code Dev Container
├── Makefile                     # Build automation
├── .goreleaser.yml              # Release automation
└── go.mod                       # Go dependencies
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Cobra](https://github.com/spf13/cobra) (CLI framework)
- [go-github](https://github.com/google/go-github) (GitHub API client)
- [Chart.js](https://www.chartjs.org/) (Dashboard charts)
- [Vue.js](https://vuejs.org/) (Dashboard UI)

---

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/autonomous-dev/cli/issues)
- **Releases**: [GitHub Releases](https://github.com/autonomous-dev/cli/releases)

---

**Built with ❤️ for autonomous software development**
