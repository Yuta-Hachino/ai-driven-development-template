package cli

import (
	"fmt"

	"github.com/autonomous-dev/cli/internal/config"
	"github.com/autonomous-dev/cli/internal/github"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

var (
	instances int
	task      string
)

func StartCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "start",
		Short: "Start parallel development with multiple Claude Code instances",
		Long: `Start autonomous development by triggering GitHub Actions workflow
with multiple Claude Code instances running in parallel.

This command will:
1. Create a GitHub Issue with the task description
2. Trigger the GitHub Actions workflow
3. Pass the number of instances as parameter

The instances will coordinate through P2P messaging in the issue comments.`,
		RunE: runStart,
	}

	cmd.Flags().IntVarP(&instances, "instances", "n", 0, "Number of parallel instances (default from config)")
	cmd.Flags().StringVarP(&task, "task", "t", "", "Task description (required)")
	cmd.MarkFlagRequired("task")

	return cmd
}

func runStart(cmd *cobra.Command, args []string) error {
	green := color.New(color.FgGreen).SprintFunc()
	cyan := color.New(color.FgCyan).SprintFunc()
	bold := color.New(color.Bold).SprintFunc()

	// Load config
	cfg, err := config.Load(config.ConfigPath())
	if err != nil {
		return fmt.Errorf("failed to load config (run 'autonomous-dev init' first): %w", err)
	}

	// Use default instances if not specified
	if instances == 0 {
		instances = cfg.Instances.Default
	}

	// Validate instances
	if instances > cfg.Instances.Max {
		return fmt.Errorf("instances (%d) exceeds maximum (%d)", instances, cfg.Instances.Max)
	}

	// Create GitHub client
	client := github.NewClient(cfg.GitHub.Token, cfg.GitHub.Owner, cfg.GitHub.Repo)

	fmt.Println(bold("Starting autonomous development..."))
	fmt.Println()

	// Create GitHub Issue
	fmt.Printf("Creating issue with task: %s\n", cyan(task))
	issue, err := client.CreateIssue(task, fmt.Sprintf(`# Autonomous Development Task

%s

## Configuration
- Instances: %d
- Repository: %s/%s

This issue will be used for P2P coordination between Claude Code instances.
`, task, instances, cfg.GitHub.Owner, cfg.GitHub.Repo))
	if err != nil {
		return fmt.Errorf("failed to create issue: %w", err)
	}
	fmt.Printf("%s Created issue #%d\n", green("✓"), issue.Number)

	// Trigger workflow
	fmt.Printf("Triggering workflow with %d instances...\n", instances)
	run, err := client.TriggerWorkflow(issue.Number, instances)
	if err != nil {
		return fmt.Errorf("failed to trigger workflow: %w", err)
	}
	fmt.Printf("%s Triggered workflow run #%d\n", green("✓"), run.ID)

	// Print success
	fmt.Println()
	fmt.Println(green("✓"), bold("Autonomous development started!"))
	fmt.Println()
	fmt.Println("Monitor progress:")
	fmt.Printf("  Issue: %s\n", issue.URL)
	fmt.Printf("  Workflow: %s\n", run.URL)
	fmt.Printf("  Dashboard: autonomous-dev dashboard\n")
	fmt.Println()
	fmt.Println("Check status:")
	fmt.Println("  autonomous-dev status")

	return nil
}
