.PHONY: build install test clean run dev

# Binary name
BINARY_NAME=autonomous-dev
VERSION=$(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
GIT_COMMIT=$(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE=$(shell date +%Y-%m-%d)

# Build flags
LDFLAGS=-ldflags "-X github.com/autonomous-dev/cli/pkg/version.Version=$(VERSION) \
	-X github.com/autonomous-dev/cli/pkg/version.GitCommit=$(GIT_COMMIT) \
	-X github.com/autonomous-dev/cli/pkg/version.BuildDate=$(BUILD_DATE)"

# Default target
all: build

# Build the binary
build:
	@echo "Building $(BINARY_NAME)..."
	go build $(LDFLAGS) -o $(BINARY_NAME) ./cmd/autonomous-dev

# Build for all platforms
build-all:
	@echo "Building for all platforms..."
	GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o dist/$(BINARY_NAME)-darwin-amd64 ./cmd/autonomous-dev
	GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o dist/$(BINARY_NAME)-darwin-arm64 ./cmd/autonomous-dev
	GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o dist/$(BINARY_NAME)-linux-amd64 ./cmd/autonomous-dev
	GOOS=linux GOARCH=arm64 go build $(LDFLAGS) -o dist/$(BINARY_NAME)-linux-arm64 ./cmd/autonomous-dev
	GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o dist/$(BINARY_NAME)-windows-amd64.exe ./cmd/autonomous-dev

# Install dependencies
deps:
	@echo "Installing dependencies..."
	go mod download
	go mod tidy

# Run tests
test:
	@echo "Running tests..."
	go test -v ./...

# Run with coverage
test-coverage:
	@echo "Running tests with coverage..."
	go test -v -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

# Install binary to $GOPATH/bin
install:
	@echo "Installing $(BINARY_NAME)..."
	go install $(LDFLAGS) ./cmd/autonomous-dev

# Clean build artifacts
clean:
	@echo "Cleaning..."
	rm -f $(BINARY_NAME)
	rm -rf dist/
	rm -f coverage.out coverage.html

# Run locally
run:
	go run ./cmd/autonomous-dev

# Development mode with hot reload (requires air: go install github.com/cosmtrek/air@latest)
dev:
	air

# Format code
fmt:
	@echo "Formatting code..."
	go fmt ./...

# Lint code
lint:
	@echo "Linting code..."
	golangci-lint run

# Show version
version:
	@echo "Version: $(VERSION)"
	@echo "Commit: $(GIT_COMMIT)"
	@echo "Build date: $(BUILD_DATE)"

# Help
help:
	@echo "Available targets:"
	@echo "  build         - Build the binary"
	@echo "  build-all     - Build for all platforms"
	@echo "  deps          - Install dependencies"
	@echo "  test          - Run tests"
	@echo "  test-coverage - Run tests with coverage"
	@echo "  install       - Install binary to $$GOPATH/bin"
	@echo "  clean         - Clean build artifacts"
	@echo "  run           - Run locally"
	@echo "  dev           - Development mode with hot reload"
	@echo "  fmt           - Format code"
	@echo "  lint          - Lint code"
	@echo "  version       - Show version info"
