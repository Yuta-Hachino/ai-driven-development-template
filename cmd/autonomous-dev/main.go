package main

import (
	"fmt"
	"os"

	"github.com/autonomous-dev/cli/internal/cli"
	"github.com/autonomous-dev/cli/pkg/version"
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "autonomous-dev",
	Short: "Multi-instance Claude Code orchestrator",
	Long: `Autonomous Dev is a CLI tool that orchestrates multiple Claude Code instances
for parallel development on any project, regardless of programming language.

It works by:
1. Creating GitHub Actions workflows in your repository
2. Triggering parallel Claude Code instances via GitHub API
3. Coordinating work through GitHub Issues and P2P messaging

Example usage:
  autonomous-dev init                    Initialize in current project
  autonomous-dev start --instances=5     Start 5 parallel instances
  autonomous-dev status                  Check progress
  autonomous-dev dashboard               Open monitoring dashboard`,
	Version: version.Version,
}

func main() {
	// Add commands
	rootCmd.AddCommand(cli.InitCmd())
	rootCmd.AddCommand(cli.StartCmd())
	rootCmd.AddCommand(cli.StatusCmd())
	rootCmd.AddCommand(cli.DashboardCmd())
	rootCmd.AddCommand(cli.ConfigCmd())

	// Execute
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
