# P2P Instance Monitoring

How Claude Code instances coordinate, monitor each other, and ensure task completion.

---

## Overview

Autonomous Dev uses a **Peer-to-Peer (P2P) architecture** where instances communicate directly through GitHub Issues without a central server.

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│Instance1│◄───►│Instance2│◄───►│Instance3│
│(Leader) │     │(Worker) │     │(Worker) │
└────┬────┘     └────┬────┘     └────┬────┘
     │               │               │
     └───────────────┴───────────────┘
                     ↓
          ┌──────────────────────┐
          │ GitHub Issue         │
          │ (Message Bus)        │
          └──────────────────────┘
```

**Key Principles:**
- ✅ No central server required
- ✅ $0/month (GitHub free tier)
- ✅ Built-in audit trail (GitHub Issues)
- ✅ Decentralized and fault-tolerant

---

## Roles

### Leader (Instance 1)

**Responsibilities:**
1. **Coordinate workers** - Assign tasks based on capabilities
2. **Health monitoring** - Check if workers are responsive
3. **Task redistribution** - Reassign work from failed instances
4. **Final verification** - Ensure all tasks completed

**When does it activate?**
- Always assigned to Instance 1 in the matrix
- Launches first in the workflow

---

### Workers (Instance 2+)

**Responsibilities:**
1. **Report availability** - Signal ready to receive tasks
2. **Execute assigned work** - Implement features, write tests
3. **Progress updates** - Report status at milestones
4. **Completion notification** - Signal when done

**When do they activate?**
- Instances 2, 3, 4, 5... in the matrix
- Launch in parallel with leader

---

## Communication Protocol

### Message Format

All P2P messages are posted as GitHub Issue comments in structured JSON:

```markdown
<!-- INSTANCE_STATUS:START:1 -->
```json
{
  "instance_id": 1,
  "status": "in_progress",
  "role": "leader",
  "current_task": {
    "id": "task-1",
    "description": "Implement OAuth login",
    "progress": 75,
    "started_at": "2025-11-02T12:30:00Z"
  },
  "health": {
    "cpu_usage": 45,
    "memory_mb": 512,
    "last_heartbeat": "2025-11-02T12:35:00Z"
  },
  "logs_url": "https://github.com/owner/repo/actions/runs/456/jobs/789",
  "console_preview": [
    "Installing dependencies...",
    "Running tests (5/10 passed)",
    "Writing code..."
  ]
}
```
<!-- INSTANCE_STATUS:END:1 -->
```

### Message Types

| Status | Meaning | When Posted |
|--------|---------|-------------|
| `starting` | Instance initializing | On startup |
| `ready` | Waiting for task | After initialization (workers) |
| `in_progress` | Working on task | During execution |
| `completed` | Task finished | After success |
| `failed` | Task failed | After error |
| `stale` | No heartbeat >5min | Detected by leader |

---

## Health Monitoring

### Heartbeat System

**Worker reports:**
```bash
# Every progress milestone (0%, 25%, 50%, 75%, 100%)
report_status "in_progress" "task-2" "Working..." 50 "$(tail -10 /tmp/work.log)"
```

**Leader checks:**
```bash
# Every 30 seconds
for instance in 2 3 4 5; do
  health=$(check_instance_health $instance)
  if [ "$health" = "stale" ]; then
    echo "⚠️ Instance $instance not responding"
    # TODO: Reassign tasks
  fi
done
```

### Health Criteria

```bash
check_instance_health() {
  local instance_id="$1"

  # Get last heartbeat timestamp
  last_heartbeat=$(get_last_heartbeat $instance_id)

  # Calculate time since last heartbeat
  now=$(date +%s)
  heartbeat_ts=$(date -d "$last_heartbeat" +%s)
  diff=$((now - heartbeat_ts))

  # Mark stale if >5 minutes
  if [ $diff -gt 300 ]; then
    echo "stale"
  else
    echo "healthy"
  fi
}
```

**Stale detection threshold:** 5 minutes

---

## Task Assignment (Leader)

### 1. Wait for Workers

```bash
echo "👑 Acting as leader, waiting for workers..."
sleep 5  # Give workers time to start

# Check all workers
check_workers
```

### 2. Distribute Tasks

```bash
# Get worker capabilities from config
workers=$(get_available_workers)

# Assign tasks based on skills
for worker in $workers; do
  task=$(match_task_to_skills $worker)
  assign_task $worker $task
done
```

### 3. Monitor Progress

```bash
# Continuously monitor
while true; do
  check_workers
  check_task_progress
  sleep 30
done
```

### 4. Handle Failures

```bash
# Detect stale instance
if [ "$health" = "stale" ]; then
  echo "⚠️ Instance $i not responding"

  # Get assigned task
  task=$(get_assigned_task $i)

  # Reassign to healthy worker
  healthy_worker=$(find_healthy_worker)
  reassign_task $task $healthy_worker
fi
```

---

## Task Execution (Workers)

### 1. Report Ready

```bash
echo "👷 Acting as worker, waiting for task assignment..."
report_status "ready" "waiting" "Waiting for task assignment" 0
```

### 2. Poll for Assignment

```bash
# Check for task assignment from leader
while true; do
  task=$(check_assigned_task $INSTANCE_ID)

  if [ -n "$task" ]; then
    break
  fi

  sleep 5
done
```

### 3. Execute Task

```bash
echo "📋 Received task: $task_description"

# Report start
report_status "in_progress" "$task_id" "$task_description" 0

# Execute with progress reporting
for progress in 25 50 75; do
  # Do work...
  echo "⏳ Progress: $progress%"
  report_status "in_progress" "$task_id" "$task_description" $progress
done

# Report completion
report_status "completed" "$task_id" "$task_description" 100
```

---

## Dashboard Integration

### Real-Time Updates

Dashboard polls GitHub API every 5 seconds:

```javascript
async function fetchInstanceStatuses() {
  // Get all issue comments
  const comments = await octokit.rest.issues.listComments({
    owner: 'your-org',
    repo: 'your-repo',
    issue_number: issueNumber
  });

  // Parse instance statuses
  const statuses = comments
    .filter(c => c.body.includes('INSTANCE_STATUS'))
    .map(parseInstanceStatus);

  // Update UI
  updateInstanceGrid(statuses);
}

// Poll every 5 seconds
setInterval(fetchInstanceStatuses, 5000);
```

### Instance Detail View

Click on any instance to see:

```
┌─────────────────────────────────────────┐
│ Instance #2 (Worker)                    │
├─────────────────────────────────────────┤
│ Current Task: Implement login UI (75%)  │
│ ████████████████████░░░░░               │
│                                         │
│ Health:                                 │
│ - CPU: 45%                              │
│ - Memory: 512 MB                        │
│ - Last Heartbeat: 2 seconds ago         │
│                                         │
│ Console Output:                         │
│ $ npm install                           │
│ $ Creating LoginForm component...      │
│ $ Writing tests...                      │
└─────────────────────────────────────────┘
```

---

## Fault Tolerance

### Scenario 1: Worker Crashes

**Detection:**
```
Leader: Instance 3 last heartbeat: 6 minutes ago → STALE
```

**Recovery:**
```bash
# Leader reassigns task
echo "⚠️ Instance 3 crashed, reassigning task to Instance 4"
reassign_task "task-3" "instance-4"
```

### Scenario 2: Leader Crashes

**Detection:**
- Workers detect no task assignments after 10 minutes

**Recovery:**
```bash
# Worker promotes itself to leader
if [ "$(check_leader_alive)" = "false" ]; then
  echo "👑 Promoting self to leader"
  ROLE="leader"
  start_leader_duties
fi
```

### Scenario 3: GitHub Actions Timeout

**Detection:**
- Workflow exceeds 6-hour limit

**Recovery:**
- Workflow automatically cancelled
- User can restart with saved state (future feature)

---

## Metrics and Observability

### Tracked Metrics

Each instance reports:

```json
{
  "health": {
    "cpu_usage": 45,        // 0-100%
    "memory_mb": 512,       // MB used
    "last_heartbeat": "2025-11-02T12:35:00Z",
    "uptime_seconds": 1800  // Time since start
  }
}
```

### Aggregated View (Dashboard)

```
Overall System Health:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instances:     5 total, 4 healthy, 1 stale
Tasks:         10 total, 7 completed, 3 in progress
Success Rate:  85% (17/20 recent tasks)
Avg Duration:  42 minutes per task
```

---

## Best Practices

### For Users

1. **Start with fewer instances** for small tasks
   ```bash
   autonomous-dev start --instances=2 --task="Small fix"
   ```

2. **Monitor the dashboard** during execution
   ```bash
   autonomous-dev dashboard
   ```

3. **Check logs** if instances fail
   - Click instance in dashboard
   - View console output
   - Check GitHub Actions logs

### For Advanced Users

1. **Customize worker skills** in `.autonomous-dev/config.yaml`
   ```yaml
   agents:
     - name: "specialist-1"
       skills: ["react", "typescript"]
     - name: "specialist-2"
       skills: ["python", "django"]
   ```

2. **Adjust concurrency** for better resource usage
   ```yaml
   workflow:
     concurrency: 3  # Max 3 instances running simultaneously
   ```

3. **Set instance limits**
   ```yaml
   instances:
     default: 5
     max: 10  # Can request up to 10 instances
   ```

---

## Troubleshooting

### Issue: Instances not communicating

**Symptom:**
```
Workers stuck in "ready" state indefinitely
```

**Solution:**
1. Check GitHub Issue was created: `gh issue list`
2. Verify workers can post comments (check permissions)
3. Look for errors in GitHub Actions logs

### Issue: Leader not detecting workers

**Symptom:**
```
Leader logs: "No workers available"
```

**Solution:**
1. Increase leader wait time in workflow
2. Check worker startup logs for errors
3. Verify worker status messages in Issue

### Issue: High stale rate

**Symptom:**
```
Multiple workers marked as stale
```

**Solution:**
1. Reduce heartbeat timeout (currently 5 min)
2. Check GitHub Actions quota (may be throttled)
3. Reduce task complexity (workers timing out)

---

## Architecture Diagram

```
┌──────────────────────────────────────────────┐
│ GitHub Actions Workflow                      │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │ Instance 1 (Leader)                  │   │
│  │                                      │   │
│  │ while true; do                       │   │
│  │   check_workers                      │   │
│  │   assign_tasks                       │   │
│  │   monitor_progress                   │   │
│  │   sleep 30                           │   │
│  │ done                                 │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │Worker 2 │ │Worker 3 │ │Worker 4 │ ...   │
│  │         │ │         │ │         │       │
│  │ report_ │ │ report_ │ │ report_ │       │
│  │ status  │ │ status  │ │ status  │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│       ↓            ↓            ↓           │
└───────┼────────────┼────────────┼───────────┘
        │            │            │
        └────────────┴────────────┘
                     ↓
          ┌──────────────────────┐
          │ GitHub Issue         │
          │                      │
          │ Comment 1: Instance 1│
          │ Comment 2: Instance 2│
          │ Comment 3: Instance 3│
          │ ...                  │
          └──────────────────────┘
                     ↓
          ┌──────────────────────┐
          │ Dashboard            │
          │                      │
          │ Polls comments       │
          │ every 5 seconds      │
          │ Displays status      │
          └──────────────────────┘
```

---

## Summary

**P2P Monitoring provides:**
- ✅ Real-time instance coordination
- ✅ Automatic failure detection
- ✅ Task redistribution on failures
- ✅ Complete visibility via dashboard
- ✅ $0/month (no infrastructure needed)

**All communication through GitHub Issues:**
- Structured JSON comments
- Leader-worker coordination
- Health monitoring
- Progress tracking

**Result:** Reliable autonomous development with fault tolerance and observability.
