package version

// Version is the current version of the CLI
var Version = "1.0.0"

// GitCommit is the git commit hash (set during build)
var GitCommit = "dev"

// BuildDate is the build date (set during build)
var BuildDate = "unknown"

// GetFullVersion returns the full version string
func GetFullVersion() string {
	return Version + " (" + GitCommit + ") built on " + BuildDate
}
