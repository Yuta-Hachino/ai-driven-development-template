package config

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

// Config represents the autonomous-dev configuration
type Config struct {
	GitHub    GitHubConfig    `yaml:"github"`
	Instances InstancesConfig `yaml:"instances"`
	Agents    []Agent         `yaml:"agents"`
	Workflow  WorkflowConfig  `yaml:"workflow"`
}

// GitHubConfig represents GitHub-related settings
type GitHubConfig struct {
	Owner string `yaml:"owner"`
	Repo  string `yaml:"repo"`
	Token string `yaml:"token"`
}

// InstancesConfig represents instance settings
type InstancesConfig struct {
	Default int `yaml:"default"`
	Max     int `yaml:"max"`
}

// Agent represents an agent configuration
type Agent struct {
	Name   string   `yaml:"name"`
	Skills []string `yaml:"skills"`
}

// WorkflowConfig represents workflow settings
type WorkflowConfig struct {
	File        string `yaml:"file"`
	Concurrency int    `yaml:"concurrency"`
}

// DefaultConfig returns a default configuration
func DefaultConfig() *Config {
	return &Config{
		GitHub: GitHubConfig{
			Owner: "",
			Repo:  "",
			Token: "${GITHUB_TOKEN}",
		},
		Instances: InstancesConfig{
			Default: 5,
			Max:     10,
		},
		Agents: []Agent{
			{
				Name:   "frontend-specialist",
				Skills: []string{"react", "typescript", "css"},
			},
			{
				Name:   "backend-specialist",
				Skills: []string{"api", "database", "performance"},
			},
			{
				Name:   "test-specialist",
				Skills: []string{"testing", "e2e", "unit-test"},
			},
		},
		Workflow: WorkflowConfig{
			File:        ".github/workflows/autonomous-dev.yml",
			Concurrency: 5,
		},
	}
}

// Load loads configuration from file
func Load(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("failed to parse config file: %w", err)
	}

	// Expand environment variables in token
	if cfg.GitHub.Token != "" && cfg.GitHub.Token[0] == '$' {
		envVar := cfg.GitHub.Token[2 : len(cfg.GitHub.Token)-1] // Remove ${ and }
		cfg.GitHub.Token = os.Getenv(envVar)
	}

	return &cfg, nil
}

// Save saves configuration to file
func (c *Config) Save(path string) error {
	data, err := yaml.Marshal(c)
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	// Create directory if it doesn't exist
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// ConfigPath returns the path to the config file
func ConfigPath() string {
	return filepath.Join(".autonomous-dev", "config.yaml")
}

// Exists checks if config file exists
func Exists() bool {
	_, err := os.Stat(ConfigPath())
	return err == nil
}
