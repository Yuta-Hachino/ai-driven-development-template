package cli

import (
	"fmt"

	"github.com/autonomous-dev/cli/internal/config"
	"github.com/autonomous-dev/cli/internal/github"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

func StatusCmd() *cobra.Command{
	return &cobra.Command{
		Use:   "status",
		Short: "Check status of running instances",
		Long: `Check the status of autonomous development by querying:
- Latest GitHub Actions workflow runs
- P2P messages in issues
- Overall progress

Shows a summary of all running instances and their current tasks.`,
		RunE: runStatus,
	}
}

func runStatus(cmd *cobra.Command, args []string) error {
	yellow := color.New(color.FgYellow).SprintFunc()
	cyan := color.New(color.FgCyan).SprintFunc()
	bold := color.New(color.Bold).SprintFunc()

	// Load config
	cfg, err := config.Load(config.ConfigPath())
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	// Create GitHub client
	client := github.NewClient(cfg.GitHub.Token, cfg.GitHub.Owner, cfg.GitHub.Repo)

	// Get latest workflow run
	run, err := client.GetLatestWorkflowRun()
	if err != nil {
		return fmt.Errorf("failed to get workflow run: %w", err)
	}

	if run == nil {
		fmt.Println(yellow("No workflow runs found"))
		fmt.Println("Start development with: autonomous-dev start --task=\"...\"")
		return nil
	}

	// Print status
	fmt.Println(bold("Workflow Run #"), run.ID)
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Printf("Status: %s\n", statusColor(run.Status))
	fmt.Printf("Started: %s\n", run.CreatedAt)
	fmt.Printf("URL: %s\n", cyan(run.URL))
	fmt.Println()

	// Get jobs
	jobs, err := client.GetWorkflowJobs(run.ID)
	if err != nil {
		return fmt.Errorf("failed to get workflow jobs: %w", err)
	}

	fmt.Println(bold("Instances:"))
	for i, job := range jobs {
		status := statusIcon(job.Status)
		fmt.Printf("%s Instance %d (%s) %s\n", status, i+1, job.Name, statusColor(job.Status))
	}
	fmt.Println()

	// Calculate progress
	completed := 0
	total := len(jobs)
	for _, job := range jobs {
		if job.Status == "completed" {
			completed++
		}
	}
	progress := 0
	if total > 0 {
		progress = (completed * 100) / total
	}

	fmt.Printf("Overall Progress: %d/%d instances completed (%d%%)\n", completed, total, progress)

	if run.Status == "in_progress" {
		fmt.Println()
		fmt.Println("Watch in real-time:")
		fmt.Println("  autonomous-dev dashboard")
	}

	return nil
}

func statusColor(status string) string {
	switch status {
	case "completed", "success":
		return color.GreenString(status)
	case "in_progress", "queued":
		return color.YellowString(status)
	case "failed", "failure":
		return color.RedString(status)
	default:
		return status
	}
}

func statusIcon(status string) string {
	switch status {
	case "completed", "success":
		return color.GreenString("✓")
	case "in_progress":
		return color.YellowString("⏳")
	case "queued":
		return color.CyanString("⏸")
	case "failed", "failure":
		return color.RedString("✗")
	default:
		return "•"
	}
}
