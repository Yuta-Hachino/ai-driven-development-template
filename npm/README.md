# @autonomous-dev/cli

> Multi-instance Claude Code orchestrator for parallel autonomous development

[![npm version](https://img.shields.io/npm/v/@autonomous-dev/cli.svg)](https://www.npmjs.com/package/@autonomous-dev/cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A language-agnostic CLI tool that orchestrates multiple Claude Code instances for parallel autonomous development on **any project**.

## 🚀 Installation

```bash
npm install -g @autonomous-dev/cli
```

**System Requirements:**
- Node.js 14.0 or higher
- Git 2.20+
- GitHub account

**Note:** The CLI will automatically download the appropriate binary for your platform (macOS, Linux, or Windows) during installation.

## ⚡ Quick Start

1. **Initialize in your project:**
```bash
cd your-project
autonomous-dev init
```

2. **Set GitHub token:**
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

Create token at: https://github.com/settings/tokens (scopes: `repo`, `workflow`)

3. **Start autonomous development:**
```bash
autonomous-dev start --instances=5 --task="Add user authentication with OAuth 2.0"
```

4. **Monitor progress:**
```bash
autonomous-dev status
autonomous-dev dashboard
```

## 🎯 What is Autonomous Dev?

Autonomous Dev turns **1 developer** into a **team of 5 AI developers** working in parallel.

```
You → autonomous-dev start --instances=5 --task="Add feature X"
  ↓
GitHub Actions launches 5 Claude Code instances
  ↓
Instance 1 (Leader): Coordinates the team
Instance 2-5 (Workers): Execute tasks in parallel
  ↓
30 minutes later: 5 Pull Requests ready for review
```

**Key Features:**
- ✅ **$0/month** - Runs on GitHub Actions (free tier)
- ✅ **Language-agnostic** - Python, JavaScript, Go, Rust, Java, etc.
- ✅ **Zero dependencies** - Single binary, no runtime required
- ✅ **P2P coordination** - Instances collaborate through GitHub Issues
- ✅ **Real-time dashboard** - Monitor progress in your browser

## 💻 CLI Commands

### `autonomous-dev init`
Initialize autonomous development in the current project.

### `autonomous-dev start`
Start parallel development with multiple instances.

```bash
autonomous-dev start --instances=3 --task="Refactor authentication module"
```

### `autonomous-dev status`
Check status of running instances.

### `autonomous-dev dashboard`
Open the monitoring dashboard in your browser.

### `autonomous-dev config`
Manage configuration.

```bash
autonomous-dev config set github.token "ghp_xxxx"
autonomous-dev config get github.owner
autonomous-dev config list
```

## 📦 Distribution Methods

This package is distributed via multiple channels:

- **npm**: `npm install -g @autonomous-dev/cli`
- **GitHub Releases**: Binary downloads for all platforms
- **Package managers**: `.deb`, `.rpm`, `.apk` for Linux

The npm package automatically downloads and installs the appropriate binary for your platform during the postinstall phase.

## 📖 Documentation

- [Installation Guide](https://github.com/Yuta-Hachino/ai-driven-development-template/blob/main/docs/INSTALLATION.md)
- [Quick Start](https://github.com/Yuta-Hachino/ai-driven-development-template/blob/main/docs/QUICK_START.md)
- [Full Documentation](https://github.com/Yuta-Hachino/ai-driven-development-template/blob/main/README.md)
- [Troubleshooting](https://github.com/Yuta-Hachino/ai-driven-development-template/blob/main/docs/TROUBLESHOOTING.md)

## 🌍 Platform Support

| Platform | Support | Architecture |
|----------|---------|--------------|
| **macOS** (Intel) | ✅ | amd64 |
| **macOS** (Apple Silicon) | ✅ | arm64 |
| **Linux** (Ubuntu/Debian) | ✅ | amd64, arm64 |
| **Linux** (WSL) | ✅ | amd64, arm64 |
| **Windows** | ⚠️ | amd64 (limited testing) |

## 🛠️ Use Cases

### Feature Development
```bash
autonomous-dev start --instances=5 --task="Add dark mode toggle with theme persistence"
```

### Refactoring
```bash
autonomous-dev start --instances=3 --task="Migrate class components to functional components"
```

### Testing
```bash
autonomous-dev start --instances=4 --task="Add E2E tests for checkout flow"
```

### Documentation
```bash
autonomous-dev start --instances=2 --task="Update API documentation for v2.0"
```

## 🔧 Troubleshooting

### Installation fails

If installation fails, you can download the binary manually:

1. Go to [GitHub Releases](https://github.com/Yuta-Hachino/ai-driven-development-template/releases)
2. Download the appropriate binary for your platform
3. Extract and move to `/usr/local/bin/` (macOS/Linux) or add to PATH (Windows)

### Binary not found after installation

The binary is installed in the npm package's `bin` directory and should be automatically added to your PATH. If not found:

```bash
# Find the installation path
npm list -g @autonomous-dev/cli

# Reinstall
npm uninstall -g @autonomous-dev/cli
npm install -g @autonomous-dev/cli
```

## 🤝 Contributing

Contributions are welcome! Please visit our [GitHub repository](https://github.com/Yuta-Hachino/ai-driven-development-template) for contribution guidelines.

## 📄 License

MIT License - see [LICENSE](https://github.com/Yuta-Hachino/ai-driven-development-template/blob/main/LICENSE) file for details.

## 🔗 Links

- **GitHub Repository**: https://github.com/Yuta-Hachino/ai-driven-development-template
- **Issues**: https://github.com/Yuta-Hachino/ai-driven-development-template/issues
- **Releases**: https://github.com/Yuta-Hachino/ai-driven-development-template/releases
- **npm Package**: https://www.npmjs.com/package/@autonomous-dev/cli

---

**Built with ❤️ for autonomous software development**
