package cli

import (
	"fmt"

	"github.com/autonomous-dev/cli/internal/config"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

func ConfigCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "config",
		Short: "Manage configuration",
		Long:  "View and modify autonomous-dev configuration",
	}

	cmd.AddCommand(configSetCmd())
	cmd.AddCommand(configGetCmd())
	cmd.AddCommand(configListCmd())

	return cmd
}

func configSetCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "set <key> <value>",
		Short: "Set a configuration value",
		Args:  cobra.ExactArgs(2),
		RunE: func(cmd *cobra.Command, args []string) error {
			key := args[0]
			value := args[1]

			cfg, err := config.Load(config.ConfigPath())
			if err != nil {
				return fmt.Errorf("failed to load config: %w", err)
			}

			// Set value based on key
			switch key {
			case "github.owner":
				cfg.GitHub.Owner = value
			case "github.repo":
				cfg.GitHub.Repo = value
			case "github.token":
				cfg.GitHub.Token = value
			default:
				return fmt.Errorf("unknown config key: %s", key)
			}

			// Save config
			if err := cfg.Save(config.ConfigPath()); err != nil {
				return fmt.Errorf("failed to save config: %w", err)
			}

			green := color.New(color.FgGreen).SprintFunc()
			fmt.Printf("%s Set %s = %s\n", green("✓"), key, value)

			return nil
		},
	}
}

func configGetCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "get <key>",
		Short: "Get a configuration value",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			key := args[0]

			cfg, err := config.Load(config.ConfigPath())
			if err != nil {
				return fmt.Errorf("failed to load config: %w", err)
			}

			// Get value based on key
			var value string
			switch key {
			case "github.owner":
				value = cfg.GitHub.Owner
			case "github.repo":
				value = cfg.GitHub.Repo
			case "github.token":
				value = cfg.GitHub.Token
			default:
				return fmt.Errorf("unknown config key: %s", key)
			}

			fmt.Println(value)
			return nil
		},
	}
}

func configListCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "list",
		Short: "List all configuration values",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := config.Load(config.ConfigPath())
			if err != nil {
				return fmt.Errorf("failed to load config: %w", err)
			}

			bold := color.New(color.Bold).SprintFunc()
			cyan := color.New(color.FgCyan).SprintFunc()

			fmt.Println(bold("Configuration:"))
			fmt.Println()
			fmt.Printf("GitHub:\n")
			fmt.Printf("  owner: %s\n", cyan(cfg.GitHub.Owner))
			fmt.Printf("  repo: %s\n", cyan(cfg.GitHub.Repo))
			fmt.Printf("  token: %s\n", maskToken(cfg.GitHub.Token))
			fmt.Println()
			fmt.Printf("Instances:\n")
			fmt.Printf("  default: %s\n", cyan(fmt.Sprint(cfg.Instances.Default)))
			fmt.Printf("  max: %s\n", cyan(fmt.Sprint(cfg.Instances.Max)))
			fmt.Println()
			fmt.Printf("Workflow:\n")
			fmt.Printf("  file: %s\n", cyan(cfg.Workflow.File))
			fmt.Printf("  concurrency: %s\n", cyan(fmt.Sprint(cfg.Workflow.Concurrency)))

			return nil
		},
	}
}

func maskToken(token string) string {
	if token == "" || token == "${GITHUB_TOKEN}" {
		return color.YellowString("(not set)")
	}
	if len(token) < 8 {
		return "***"
	}
	return token[:4] + "..." + token[len(token)-4:]
}
