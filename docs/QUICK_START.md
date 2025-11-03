# Quick Start Guide

Get up and running with Autonomous Dev in **5 minutes**.

---

## Prerequisites

- Git repository (GitHub)
- GitHub account
- Command line access

**No additional requirements:**
- ❌ No Python
- ❌ No Node.js
- ❌ No Docker
- ❌ No Kubernetes

---

## Step 1: Install (2 minutes)

Choose your preferred installation method:

### Option A: npm (Any OS)

```bash
npm install -g @autonomous-dev/cli
```

### Option B: Direct Download

```bash
# macOS (Apple Silicon)
curl -L https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_arm64.tar.gz | tar xz
sudo mv autonomous-dev /usr/local/bin/

# macOS (Intel)
curl -L https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_amd64.tar.gz | tar xz
sudo mv autonomous-dev /usr/local/bin/

# Linux
curl -L https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_linux_amd64.tar.gz | tar xz
sudo mv autonomous-dev /usr/local/bin/
```

**Verify installation:**

```bash
autonomous-dev --version
# Output: autonomous-dev version 1.0.0
```

---

## Step 2: Create GitHub Token (1 minute)

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name: `autonomous-dev`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click **"Generate token"**
6. **Copy the token** (starts with `ghp_`)

**Set token in environment:**

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

💡 **Tip:** Add to your `~/.bashrc` or `~/.zshrc` to persist:

```bash
echo 'export GITHUB_TOKEN="ghp_xxx..."' >> ~/.zshrc
```

---

## Step 3: Initialize Your Project (1 minute)

Navigate to your existing project:

```bash
cd ~/my-existing-project
```

Initialize autonomous development:

```bash
autonomous-dev init
```

**Output:**
```
✓ Created .autonomous-dev/config.yaml
✓ Created .github/workflows/autonomous-dev.yml
✓ Updated .gitignore

Next steps:
1. Review and edit .autonomous-dev/config.yaml
2. Set GITHUB_TOKEN environment variable:
   export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
3. Commit and push the workflow file
4. Start development:
   autonomous-dev start --task="Your feature description"
```

**Commit the changes:**

```bash
git add .autonomous-dev .github/workflows/autonomous-dev.yml .gitignore
git commit -m "Add autonomous development workflow"
git push
```

---

## Step 4: Start Development (30 seconds)

Run your first autonomous development task:

```bash
autonomous-dev start \
  --instances=3 \
  --task="Add a README.md file with project description"
```

**What happens:**

1. ✅ Creates GitHub Issue #N with task description
2. ✅ Triggers GitHub Actions workflow
3. ✅ Launches 3 Claude Code instances
4. ✅ Instances collaborate via P2P messaging
5. ✅ Creates Pull Requests when complete

**Output:**
```
✓ Autonomous development started!

Monitor progress:
  Issue: https://github.com/owner/repo/issues/123
  Workflow: https://github.com/owner/repo/actions/runs/456
  Dashboard: autonomous-dev dashboard

Check status:
  autonomous-dev status
```

---

## Step 5: Monitor Progress (ongoing)

### Check Status (CLI)

```bash
autonomous-dev status
```

**Output:**
```
Workflow Run # 456 (in_progress)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: in_progress
Started: 2025-11-02 12:30:45

Instances:
✓ Instance 1 (leader) completed
⏳ Instance 2 (worker) in_progress
⏳ Instance 3 (worker) in_progress

Overall Progress: 1/3 instances completed (33%)
```

### Open Dashboard (Browser)

```bash
autonomous-dev dashboard
```

Opens in your browser:
- **Overview tab** - Instance grid, progress chart
- **Workflows tab** - Recent runs, success rate
- **P2P Messages tab** - Inter-instance communication

**Click on any instance** to see detailed view:
- Current task and progress
- Console output (real-time)
- Health metrics (CPU, memory)
- Full logs

---

## What's Next?

### Try More Complex Tasks

```bash
# Feature development
autonomous-dev start \
  --instances=5 \
  --task="Add user authentication with OAuth 2.0 and JWT tokens"

# Refactoring
autonomous-dev start \
  --instances=4 \
  --task="Refactor API routes to use Express Router pattern"

# Testing
autonomous-dev start \
  --instances=3 \
  --task="Add unit tests for all services with 80%+ coverage"

# Documentation
autonomous-dev start \
  --instances=2 \
  --task="Generate OpenAPI documentation for all REST endpoints"
```

### Adjust Instance Count

```bash
# Small task - 2 instances
autonomous-dev start --instances=2 --task="Fix typo in homepage"

# Medium task - 3-5 instances (recommended)
autonomous-dev start --instances=5 --task="Add shopping cart feature"

# Large task - up to 10 instances (requires config change)
autonomous-dev config set instances.max 10
autonomous-dev start --instances=10 --task="Migrate from REST to GraphQL"
```

### Configure Agent Specializations

Edit `.autonomous-dev/config.yaml`:

```yaml
agents:
  - name: "frontend-specialist"
    skills: ["react", "vue", "angular", "typescript", "css"]

  - name: "backend-specialist"
    skills: ["api", "database", "authentication", "performance"]

  - name: "test-specialist"
    skills: ["jest", "pytest", "e2e", "integration-testing"]

  - name: "devops-specialist"
    skills: ["docker", "kubernetes", "ci-cd", "monitoring"]

  - name: "documentation-specialist"
    skills: ["technical-writing", "api-docs", "tutorials"]
```

Commit and push:

```bash
git add .autonomous-dev/config.yaml
git commit -m "Update agent specializations"
git push
```

---

## Troubleshooting

### Issue: "GITHUB_TOKEN not set"

```bash
export GITHUB_TOKEN="ghp_xxx..."
```

Or set directly in config:

```bash
autonomous-dev config set github.token "ghp_xxx..."
```

### Issue: "Failed to create issue"

Check token permissions:
- ✅ Token has `repo` and `workflow` scopes
- ✅ You have write access to the repository

### Issue: "Workflow not found"

Ensure workflow file exists and is pushed:

```bash
ls .github/workflows/autonomous-dev.yml
git push
```

### Issue: "Instances not starting"

Check GitHub Actions:
1. Go to repository → **Actions** tab
2. Check if workflow run appears
3. Click on run to see logs
4. Check for errors in setup or execution

---

## Next Steps

- 📖 Read [Installation Guide](INSTALLATION.md) for advanced options
- 🏗️ Learn [P2P Monitoring](P2P_MONITORING.md) to understand coordination
- 📊 Explore [Dashboard Guide](DASHBOARD_GUIDE.md) for monitoring tips
- 🛠️ Review [Troubleshooting](TROUBLESHOOTING.md) for common issues
- 🏛️ Understand [Architecture](GO_CLI_DESIGN.md) for technical details

---

## Summary

✅ **Installed** autonomous-dev CLI
✅ **Created** GitHub token
✅ **Initialized** your project
✅ **Started** first autonomous development task
✅ **Monitored** progress via CLI and dashboard

**Time spent:** ~5 minutes
**Cost:** $0 (using GitHub free tier)
**Result:** AI team working in parallel on your tasks

---

**You're ready to go! 🎉**

Start using autonomous development to accelerate your workflow.
