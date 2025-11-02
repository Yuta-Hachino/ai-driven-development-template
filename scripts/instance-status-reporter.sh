#!/bin/bash
# Instance Status Reporter
# Posts structured status updates to GitHub Issue for P2P coordination

set -e

INSTANCE_ID="${INSTANCE_ID:-1}"
ISSUE_NUMBER="${ISSUE_NUMBER:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
ROLE="${ROLE:-worker}"  # leader or worker

if [ -z "$ISSUE_NUMBER" ] || [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: ISSUE_NUMBER and GITHUB_TOKEN required"
  exit 1
fi

# Get current metrics
get_cpu_usage() {
  top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'
}

get_memory_mb() {
  free -m | awk 'NR==2{printf "%.0f", $3}'
}

# Report status to issue
report_status() {
  local status="$1"
  local task_id="$2"
  local task_desc="$3"
  local progress="$4"
  local console_output="$5"

  # Get job URL
  local job_url="https://github.com/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}/job/${GITHUB_JOB}"

  # Extract last 3 lines of console output
  local console_preview
  console_preview=$(echo "$console_output" | tail -3 | jq -R . | jq -s .)

  # Build JSON status
  local status_json
  status_json=$(cat <<EOF
{
  "instance_id": $INSTANCE_ID,
  "status": "$status",
  "role": "$ROLE",
  "current_task": {
    "id": "$task_id",
    "description": "$task_desc",
    "progress": $progress,
    "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  },
  "health": {
    "cpu_usage": $(get_cpu_usage),
    "memory_mb": $(get_memory_mb),
    "last_heartbeat": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  },
  "logs_url": "$job_url",
  "console_preview": $console_preview
}
EOF
)

  # Post to issue
  local comment_body
  comment_body=$(cat <<EOF
<!-- INSTANCE_STATUS:START:$INSTANCE_ID -->
\`\`\`json
$status_json
\`\`\`
<!-- INSTANCE_STATUS:END:$INSTANCE_ID -->
EOF
)

  gh issue comment "$ISSUE_NUMBER" --body "$comment_body"
}

# Read other instances' status
get_other_instances_status() {
  # Fetch all comments
  gh api "/repos/${GITHUB_REPOSITORY}/issues/${ISSUE_NUMBER}/comments" \
    --jq '.[] | select(.body | contains("INSTANCE_STATUS")) | .body' \
    | grep -A 20 "INSTANCE_STATUS:START" \
    | grep -v "INSTANCE_STATUS:START:$INSTANCE_ID" \
    | sed -n '/```json/,/```/p' \
    | grep -v '```'
}

# Check if instance is healthy
check_instance_health() {
  local instance_id="$1"
  local status_json
  status_json=$(get_other_instances_status | jq "select(.instance_id == $instance_id)")

  if [ -z "$status_json" ]; then
    echo "unknown"
    return
  fi

  local last_heartbeat
  last_heartbeat=$(echo "$status_json" | jq -r '.health.last_heartbeat')

  local now
  now=$(date -u +%s)

  local heartbeat_ts
  heartbeat_ts=$(date -d "$last_heartbeat" +%s)

  local diff=$((now - heartbeat_ts))

  if [ $diff -gt 300 ]; then
    echo "stale"  # No update for 5 minutes
  else
    echo "healthy"
  fi
}

# Leader: Check all workers
if [ "$ROLE" = "leader" ]; then
  check_workers() {
    local total_instances="${TOTAL_INSTANCES:-5}"

    echo "🔍 Checking worker instances..."

    for i in $(seq 2 $total_instances); do
      local health
      health=$(check_instance_health "$i")

      echo "  Instance $i: $health"

      if [ "$health" = "stale" ]; then
        echo "  ⚠️  Instance $i is not responding, may need to reassign tasks"
        # TODO: Implement task reassignment logic
      fi
    done
  }
fi

# Export functions
export -f report_status
export -f get_other_instances_status
export -f check_instance_health

# Example usage in workflow:
# source ./instance-status-reporter.sh
# report_status "in_progress" "task-1" "Implement feature X" 50 "$(tail -100 /tmp/work.log)"
