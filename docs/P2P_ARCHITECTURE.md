# P2P Architecture Documentation

## Overview

The Autonomous Development System uses a **Peer-to-Peer (P2P) architecture** where Claude Code instances coordinate through GitHub without a central server.

**Last Updated:** 2025-11-01

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ GitHub (Coordination Layer)                              │
│  ├── Issues/Comments: P2P messaging                      │
│  ├── Actions: Claude Code execution                      │
│  └── Repository: Code & state storage                    │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴────────┬────────────────┬──────────────┐
    ▼                 ▼                ▼              ▼
┌─────────┐      ┌─────────┐     ┌─────────┐   ┌─────────┐
│Instance1│◄────►│Instance2│◄───►│Instance3│◄─►│Instance4│
│(Leader) │      │(Worker) │     │(Worker) │   │(Worker) │
└─────────┘      └─────────┘     └─────────┘   └─────────┘

                         ▼
              ┌────────────────────┐
              │ Dashboard          │
              │ (Optional)         │
              │                    │
              │ - GitHub Pages     │
              │ - Cloud Run        │
              │ - VPS              │
              └────────────────────┘
```

---

## Core Components

### 1. P2P Coordinator (`src/p2p/coordinator.py`)

**Responsibilities:**
- Leader election
- Node discovery
- Task distribution
- Progress reporting
- Heartbeat monitoring

**Communication Protocol:**

All coordination happens through GitHub Issue comments with special markers:

```python
# Leader election
"🎯 LEADER_ELECTION|{node_id}|{timestamp}"

# Node announcement
"📡 NODE_ANNOUNCE|{json_data}"

# Task publication
"📦 TASKS_DATA|{json_data}"

# Task claim
"🎯 CLAIM|{task_id}|{node_id}|{timestamp}"

# Progress report
"📊 PROGRESS|{json_data}"

# Heartbeat
"💓 HEARTBEAT|{json_data}"
```

### 2. GitHub Actions Workflow (`.github/workflows/p2p-autonomous-dev.yml`)

**Trigger Methods:**

1. **Issue with label:**
   ```bash
   # Create issue with label 'p2p-dev'
   ```

2. **Comment command:**
   ```bash
   # Comment on any issue: /p2p-dev
   ```

3. **Manual dispatch:**
   ```bash
   # GitHub UI: Actions > P2P Autonomous Development > Run workflow
   ```

**Execution Flow:**

```yaml
1. check-trigger
   ├── Validate trigger
   └── Extract issue number

2. p2p-execute (matrix: 5 instances)
   ├── Elect leader (instance 1-5 race)
   │   └── First to comment wins
   ├── Leader: Create & publish tasks
   └── Workers: Claim & execute tasks

3. aggregate-results
   ├── Collect metrics from all instances
   ├── Update GitHub Pages dashboard
   └── Post summary to issue
```

---

## Leader Election

### Algorithm

**Optimistic Locking with GitHub Comments:**

1. All instances attempt to claim leadership by posting a comment
2. Wait 2 seconds for competing claims
3. Earliest comment (by `created_at`) wins
4. Winner becomes leader, others become workers

```python
async def elect_leader(self) -> bool:
    marker = f"🎯 LEADER_ELECTION|{self.node_id}|{time.time()}"

    # Attempt to claim
    self.issue.create_comment(marker)

    # Wait for competition
    await asyncio.sleep(2)

    # Check who won
    comments = self.issue.get_comments()
    election_comments = [c for c in comments if "LEADER_ELECTION" in c.body]
    earliest = min(election_comments, key=lambda c: c.created_at)

    return earliest.body == marker  # We won!
```

**Guarantees:**
- Eventual consistency (2-second window)
- No central coordinator needed
- GitHub API provides ordering

---

## Task Distribution

### Leader Responsibilities

1. **Create Task Plan**
   - Parse issue description
   - Break down into subtasks
   - Assign priorities and dependencies

2. **Publish Tasks**
   - Post tasks to issue as structured comment
   - Workers monitor and claim

### Worker Responsibilities

1. **Discover Tasks**
   - Poll issue for task announcements
   - Filter by status (available)

2. **Claim Task**
   - Attempt claim with optimistic locking
   - Similar to leader election
   - First worker to comment gets the task

3. **Execute Task**
   - Run Claude Code on claimed task
   - Report progress periodically
   - Report completion/failure

---

## Dashboard

The P2P system uses the **Enhanced P2P Dashboard** - a 100% serverless, single-file dashboard that runs entirely in your browser.

**Key Features:**
- ✅ **$0/month** - Completely free, no server required
- ✅ **Real-time** - 5-second polling via GitHub API (Octokit)
- ✅ **Rich Visualizations** - Chart.js charts (Grafana-equivalent)
- ✅ **Interactive** - 3 tabs (Overview, Workflows, P2P Messages)
- ✅ **Secure** - GitHub token stored locally in browser only
- ✅ **Mobile Responsive** - Works on all devices

**Quick Start:**
```bash
# Option 1: Open locally (no server needed)
open dashboard/index.html

# Option 2: Deploy to GitHub Pages (free hosting)
# Settings → Pages → Source: main → /dashboard
# Your dashboard: https://<username>.github.io/<repo>/
```

**Configuration:**
1. Create GitHub token: https://github.com/settings/tokens (scope: `repo`, `workflow`)
2. Open dashboard in browser
3. Enter token and repository (`owner/repo`)
4. Click "Connect"

**See complete documentation:** [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)

---
---

## Usage Guide

### Starting a P2P Workflow

**Method 1: Issue Label**

```bash
# 1. Create an issue with feature description
# 2. Add label: p2p-dev
# 3. Workflow starts automatically
```

**Method 2: Comment Command**

```bash
# On any issue, comment:
/p2p-dev

# Workflow starts automatically
```

**Method 3: Manual Trigger**

```bash
# 1. Go to Actions tab
# 2. Select "P2P Autonomous Development"
# 3. Click "Run workflow"
# 4. Enter issue number
# 5. Click "Run workflow"
```

---

### Monitoring Progress

**Via Issue Comments:**

All coordination happens in the issue comments. You'll see:

```
🎯 Leader Elected: Node run-123-job-1

📋 Available Tasks
- [ ] task-1: Implement backend API (Priority: high, Est: 8h)
- [ ] task-2: Create frontend UI (Priority: medium, Est: 6h)
- [ ] task-3: Write tests (Priority: medium, Est: 4h)

✅ Task Claimed: task-1 by Node run-123-job-2

⚙️ Progress Update
- Task: task-1
- Node: run-123-job-2
- Status: in_progress
- Progress: 50%

✅ Progress Update
- Task: task-1
- Node: run-123-job-2
- Status: completed
- Progress: 100%
```

**Via Dashboard:**

Access the dashboard to see real-time status:
- Active instances
- Task progress
- Success rate
- Timeline chart

---

## Configuration

### Environment Variables

```bash
# Required
GITHUB_TOKEN=ghp_xxx          # GitHub personal access token
GITHUB_REPO=user/repo         # Repository name

# Optional
PORT=8080                     # Server port (Cloud Run, VPS)
MAX_INSTANCES=5               # Max parallel instances
```

### Workflow Configuration

Edit `.github/workflows/p2p-autonomous-dev.yml`:

```yaml
# Change max instances
strategy:
  matrix:
    instance: [1, 2, 3, 4, 5]  # Add more: [1, 2, 3, ..., 10]
  max-parallel: 5               # Increase: 10
```

---

## Advantages of P2P Architecture

### vs. Central Server (Kubernetes)

| Aspect | P2P | Kubernetes |
|--------|-----|------------|
| **Cost** | $0-10/month | $200-500/month |
| **Complexity** | Low | High |
| **Single Point of Failure** | None | Yes (control plane) |
| **Scalability** | GitHub Actions limit | Node limit |
| **Maintenance** | Minimal | Regular |
| **Setup Time** | 5 minutes | 40 minutes |

### Benefits

1. **No Central Server Required**
   - GitHub is the coordinator
   - No infrastructure to manage
   - No server downtime

2. **Cost Effective**
   - Dashboard can be free (GitHub Pages)
   - Pay only for GitHub Actions usage
   - No always-on servers

3. **Scalable**
   - Limited only by GitHub Actions concurrency
   - Can run 5-20 instances in parallel
   - Auto-scales with workflow

4. **Simple**
   - One YAML file
   - One Python file
   - No Kubernetes complexity

5. **Reliable**
   - GitHub SLA: 99.9%
   - No custom infrastructure to fail
   - Built-in redundancy

---

## Troubleshooting

### Issue: Leader Not Elected

**Cause:** All instances start simultaneously

**Solution:**
- Workflow includes staggered start (2-second delays)
- If still failing, increase delay in workflow

### Issue: Tasks Not Claimed

**Cause:** Workers not discovering tasks

**Solution:**
- Check issue comments for task publication
- Verify worker loop is running
- Check GitHub API rate limits

### Issue: Dashboard Not Updating

**Cause:** gh-pages branch not updating

**Solution:**
```bash
# Check workflow logs
gh run list --workflow=p2p-autonomous-dev.yml

# Manually trigger
gh workflow run p2p-autonomous-dev.yml
```

---

## Migration from Kubernetes

### Quick Migration

```bash
# 1. Keep existing Kubernetes setup (optional)
# Files in k8s/production/ are preserved

# 2. Start using P2P
# Just run the workflow - no deployment needed

# 3. Monitor both
# Kubernetes dashboard + GitHub Pages dashboard

# 4. Deprecate Kubernetes (optional)
# When comfortable, remove k8s/ directory
```

### Gradual Migration

**Week 1:** Run both (Kubernetes + P2P)
**Week 2:** Compare performance and costs
**Week 3:** Switch primary to P2P
**Week 4:** Deprecate Kubernetes

---

## Advanced Configuration

### Custom Task Planner

Edit the leader code in workflow:

```python
# In .github/workflows/p2p-autonomous-dev.yml
# Customize task creation logic

tasks = parse_issue_to_tasks(issue_body)  # Your custom parser
```

### Custom Execution

Workers can use any task execution method:

```python
# In p2p/coordinator.py execute_task()

# Option 1: Claude Code
result = subprocess.run(['claude-code', 'execute', task])

# Option 2: Custom script
result = your_custom_executor(task)

# Option 3: AI Agent
result = await ai_agent.execute(task)
```

---

## Security Considerations

### GitHub Token Permissions

Required scopes:
- `repo` (full control)
- `workflow` (for triggering workflows)

**Store in GitHub Secrets:**
```bash
# Settings > Secrets > Actions > New repository secret
# Name: GITHUB_TOKEN
# Value: ghp_your_token_here
```

### Public vs Private Repos

**Public Repo:**
- Issue comments are public
- Dashboard is public
- Consider sensitive data exposure

**Private Repo:**
- Issue comments are private
- Dashboard requires authentication
- Recommended for production

---

## Performance

### Benchmarks

| Metric | Value |
|--------|-------|
| Leader Election Time | ~2-5 seconds |
| Task Claim Time | ~1-2 seconds |
| Progress Report Time | ~1 second |
| Dashboard Update Time | ~30 seconds |
| Max Concurrent Instances | 5-20 |
| Task Throughput | ~10-50 tasks/hour |

### Optimization Tips

1. **Reduce Comment Frequency**
   - Report progress every 10% instead of 1%
   - Batch heartbeats (every 5 minutes)

2. **Increase Parallelism**
   - Add more matrix instances
   - Adjust max-parallel limit

3. **Cache Dependencies**
   - Use GitHub Actions cache
   - Pre-build Docker images

---

## Future Enhancements

### Planned Features

- [ ] Automatic task planning from issue description
- [ ] Machine learning-based task estimation
- [ ] Cross-repository coordination
- [ ] Real-time WebSocket dashboard
- [ ] Mobile app for monitoring

### Community Contributions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## References

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [P2P Coordinator Source](../src/p2p/coordinator.py)
- [P2P Workflow Source](../.github/workflows/p2p-autonomous-dev.yml)

---

**Last Updated:** 2025-11-01
**Version:** 1.0.0
