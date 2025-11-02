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

      - name: Run autonomous development
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          INSTANCE_ID: ${{ matrix.instance }}
          ISSUE_NUMBER: ${{ inputs.issue_number }}
          TOTAL_INSTANCES: ${{ inputs.instance_count }}
        run: |
          # This is where Claude Code execution logic would go
          # For now, this is a placeholder that demonstrates the structure

          echo "🤖 Instance $INSTANCE_ID starting..."
          echo "📋 Task: Issue #$ISSUE_NUMBER"
          echo "👥 Total instances: $TOTAL_INSTANCES"

          # Post to issue for P2P coordination
          gh issue comment $ISSUE_NUMBER --body "🤖 Instance $INSTANCE_ID: Starting work..."

          # Simulate work (in production, this would be Claude Code execution)
          sleep 10

          # Report completion
          gh issue comment $ISSUE_NUMBER --body "✅ Instance $INSTANCE_ID: Task completed"

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
