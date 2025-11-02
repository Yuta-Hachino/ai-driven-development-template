package cli

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/autonomous-dev/cli/internal/config"
	"github.com/autonomous-dev/cli/internal/template"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

func InitCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "init",
		Short: "Initialize autonomous development in current project",
		Long: `Initialize autonomous development by creating configuration files and
GitHub Actions workflow in the current project.

This command will:
1. Create .autonomous-dev/config.yaml with default settings
2. Create .github/workflows/autonomous-dev.yml workflow
3. Update .gitignore to include .autonomous-dev/ directory

After initialization, you can customize the config and start development.`,
		RunE: runInit,
	}
}

func runInit(cmd *cobra.Command, args []string) error {
	green := color.New(color.FgGreen).SprintFunc()
	yellow := color.New(color.FgYellow).SprintFunc()
	bold := color.New(color.Bold).SprintFunc()

	// Check if already initialized
	if config.Exists() {
		return fmt.Errorf("%s already initialized (found %s)", yellow("Warning:"), config.ConfigPath())
	}

	// Detect repository info from git
	owner, repo, err := detectGitRepo()
	if err != nil {
		return fmt.Errorf("failed to detect git repository: %w\nMake sure you're in a git repository", err)
	}

	// Create default config
	cfg := config.DefaultConfig()
	cfg.GitHub.Owner = owner
	cfg.GitHub.Repo = repo

	// Save config
	if err := cfg.Save(config.ConfigPath()); err != nil {
		return fmt.Errorf("failed to save config: %w", err)
	}
	fmt.Printf("%s Created %s\n", green("✓"), config.ConfigPath())

	// Create workflow file
	workflowPath := ".github/workflows/autonomous-dev.yml"
	if err := os.MkdirAll(filepath.Dir(workflowPath), 0755); err != nil {
		return fmt.Errorf("failed to create .github/workflows directory: %w", err)
	}

	workflowContent := template.WorkflowTemplate(cfg)
	if err := os.WriteFile(workflowPath, []byte(workflowContent), 0644); err != nil {
		return fmt.Errorf("failed to write workflow file: %w", err)
	}
	fmt.Printf("%s Created %s\n", green("✓"), workflowPath)

	// Update .gitignore
	if err := updateGitignore(); err != nil {
		fmt.Printf("%s Warning: failed to update .gitignore: %v\n", yellow("⚠"), err)
	} else {
		fmt.Printf("%s Updated .gitignore\n", green("✓"))
	}

	// Print next steps
	fmt.Println()
	fmt.Println(bold("Next steps:"))
	fmt.Println("1. Review and edit", config.ConfigPath())
	fmt.Println("2. Set GITHUB_TOKEN environment variable:")
	fmt.Println("   export GITHUB_TOKEN=ghp_xxxxxxxxxxxx")
	fmt.Println("3. Commit and push the workflow file")
	fmt.Println("4. Start development:")
	fmt.Println("   autonomous-dev start --task=\"Your feature description\"")

	return nil
}

func detectGitRepo() (owner, repo string, err error) {
	// Try to get remote URL
	output, err := execCommand("git", "config", "--get", "remote.origin.url")
	if err != nil {
		return "", "", err
	}

	// Parse GitHub URL
	// Supports: https://github.com/owner/repo.git and git@github.com:owner/repo.git
	url := string(output)
	owner, repo, err = parseGitHubURL(url)
	if err != nil {
		return "", "", err
	}

	return owner, repo, nil
}

func parseGitHubURL(url string) (owner, repo string, err error) {
	// Remove .git suffix
	url = removeGitSuffix(url)

	// Handle different URL formats
	if len(url) > 19 && url[:19] == "https://github.com/" {
		parts := splitPath(url[19:])
		if len(parts) >= 2 {
			return parts[0], parts[1], nil
		}
	} else if len(url) > 15 && url[:15] == "git@github.com:" {
		parts := splitPath(url[15:])
		if len(parts) >= 2 {
			return parts[0], parts[1], nil
		}
	}

	return "", "", fmt.Errorf("unsupported git URL format: %s", url)
}

func removeGitSuffix(url string) string {
	if len(url) > 4 && url[len(url)-4:] == ".git" {
		return url[:len(url)-4]
	}
	return url
}

func splitPath(path string) []string {
	var parts []string
	current := ""
	for _, c := range path {
		if c == '/' {
			if current != "" {
				parts = append(parts, current)
				current = ""
			}
		} else {
			current += string(c)
		}
	}
	if current != "" {
		parts = append(parts, current)
	}
	return parts
}

func updateGitignore() error {
	gitignorePath := ".gitignore"
	entry := ".autonomous-dev/\n"

	// Read existing .gitignore
	var content []byte
	if _, err := os.Stat(gitignorePath); err == nil {
		var readErr error
		content, readErr = os.ReadFile(gitignorePath)
		if readErr != nil {
			return readErr
		}
	}

	// Check if entry already exists
	contentStr := string(content)
	for i := 0; i < len(contentStr); {
		end := i
		for end < len(contentStr) && contentStr[end] != '\n' {
			end++
		}
		line := contentStr[i:end]
		if line == ".autonomous-dev/" {
			return nil // Already exists
		}
		i = end + 1
	}

	// Append entry
	content = append(content, []byte(entry)...)
	return os.WriteFile(gitignorePath, content, 0644)
}

func execCommand(name string, args ...string) ([]byte, error) {
	// Simple command execution (avoiding os/exec for now)
	// In production, use os/exec.Command
	return nil, fmt.Errorf("not implemented")
}
