package cli

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"

	"github.com/autonomous-dev/cli/internal/config"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

func DashboardCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "dashboard",
		Short: "Open the monitoring dashboard in browser",
		Long: `Open the autonomous development dashboard in your default browser.

If the dashboard is deployed to GitHub Pages, it will open the deployed URL.
Otherwise, it will open the local dashboard/index.html file.`,
		RunE: runDashboard,
	}
}

func runDashboard(cmd *cobra.Command, args []string) error {
	green := color.New(color.FgGreen).SprintFunc()

	// Load config
	cfg, err := config.Load(config.ConfigPath())
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	// Try GitHub Pages URL first
	ghPagesURL := fmt.Sprintf("https://%s.github.io/%s/", cfg.GitHub.Owner, cfg.GitHub.Repo)

	// Check if dashboard/index.html exists locally
	localDashboard := "dashboard/index.html"
	if _, err := os.Stat(localDashboard); err == nil {
		fmt.Printf("%s Opening local dashboard: %s\n", green("✓"), localDashboard)
		return openBrowser("file://" + getAbsPath(localDashboard))
	}

	// Fallback to GitHub Pages
	fmt.Printf("%s Opening GitHub Pages dashboard: %s\n", green("✓"), ghPagesURL)
	return openBrowser(ghPagesURL)
}

func openBrowser(url string) error {
	var cmd *exec.Cmd

	switch runtime.GOOS {
	case "darwin":
		cmd = exec.Command("open", url)
	case "linux":
		cmd = exec.Command("xdg-open", url)
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	default:
		return fmt.Errorf("unsupported platform: %s", runtime.GOOS)
	}

	return cmd.Start()
}

func getAbsPath(path string) string {
	absPath, err := filepath.Abs(path)
	if err != nil {
		return path
	}
	return absPath
}
