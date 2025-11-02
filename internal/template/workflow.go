package template

import (
	"fmt"

	"github.com/autonomous-dev/cli/internal/config"
)

// WorkflowTemplate generates the GitHub Actions workflow YAML
func WorkflowTemplate(cfg *config.Config) string {
	return fmt.Sprintf(`name: Autonomous Development

on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number with task description'
        required: true
        type: string
      instance_count:
        description: 'Number of parallel instances'
        required: false
        default: '%d'
        type: string

jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - name: Generate instance matrix
        id: set-matrix
        run: |
          count=${{ inputs.instance_count }}
          matrix=$(seq 1 $count | jq -R . | jq -s -c .)
          echo "matrix=$matrix" >> $GITHUB_OUTPUT

  autonomous-dev:
    needs: setup
    runs-on: ubuntu-latest
    strategy:
      matrix:
        instance: ${{ fromJson(needs.setup.outputs.matrix) }}
      max-parallel: %d

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Claude Code environment
        run: |
          echo "Instance ${{ matrix.instance }} starting..."
          echo "Processing issue #${{ inputs.issue_number }}"

      - name: Setup status reporter
        run: |
          # Make status reporter executable
          chmod +x ./scripts/instance-status-reporter.sh

      - name: Run autonomous development
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          INSTANCE_ID: ${{ matrix.instance }}
          ISSUE_NUMBER: ${{ inputs.issue_number }}
          TOTAL_INSTANCES: ${{ inputs.instance_count }}
          ROLE: ${{ matrix.instance == 1 && 'leader' || 'worker' }}
        run: |
          # Source status reporter
          source ./scripts/instance-status-reporter.sh

          # Start logging
          exec > >(tee -a /tmp/instance-$INSTANCE_ID.log)
          exec 2>&1

          echo "🤖 Instance $INSTANCE_ID starting..."
          echo "📋 Task: Issue #$ISSUE_NUMBER"
          echo "👥 Total instances: $TOTAL_INSTANCES"
          echo "🎭 Role: $ROLE"

          # Report initial status
          report_status "starting" "init" "Initializing instance" 0 "$(tail -10 /tmp/instance-$INSTANCE_ID.log)"

          # Leader: Wait for workers to start
          if [ "$ROLE" = "leader" ]; then
            echo "👑 Acting as leader, waiting for workers..."
            sleep 5

            # Check worker instances
            check_workers

            # TODO: Distribute tasks based on worker availability
            echo "📋 Distributing tasks to workers..."
          fi

          # Worker: Wait for task assignment
          if [ "$ROLE" = "worker" ]; then
            echo "👷 Acting as worker, waiting for task assignment..."

            # Report ready status
            report_status "ready" "waiting" "Waiting for task assignment" 0 "$(tail -10 /tmp/instance-$INSTANCE_ID.log)"

            # TODO: Poll for task assignment from leader
            sleep 5
          fi

          # Simulate work with progress reporting
          for progress in 25 50 75; do
            echo "⏳ Progress: $progress%%"
            report_status "in_progress" "task-$INSTANCE_ID" "Working on assigned task" $progress "$(tail -10 /tmp/instance-$INSTANCE_ID.log)"
            sleep 5
          done

          # Report completion
          echo "✅ Instance $INSTANCE_ID: Task completed"
          report_status "completed" "task-$INSTANCE_ID" "Task completed successfully" 100 "$(tail -10 /tmp/instance-$INSTANCE_ID.log)"

          # Leader: Final check
          if [ "$ROLE" = "leader" ]; then
            echo "👑 Leader final check..."
            check_workers
            echo "✅ All workers completed"
          fi

      - name: Report status
        if: always()
        run: |
          if [ "${{ job.status }}" == "success" ]; then
            gh issue comment ${{ inputs.issue_number }} --body "✅ Instance ${{ matrix.instance }}: Success"
          else
            gh issue comment ${{ inputs.issue_number }} --body "❌ Instance ${{ matrix.instance }}: Failed"
          fi
`, cfg.Instances.Default, cfg.Workflow.Concurrency)
}
