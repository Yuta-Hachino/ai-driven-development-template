#!/bin/bash
# Project Initialization Script
# Initializes the autonomous development repository system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Autonomous Development Repository System ===${NC}"
echo -e "${GREEN}=== Project Initialization ===${NC}"
echo

# Check arguments
ENV=${1:-development}
echo -e "Environment: ${YELLOW}${ENV}${NC}"

# Check if running in project directory
if [ ! -f "config/agents.yaml" ]; then
    echo -e "${RED}Error: Must run from project root directory${NC}"
    exit 1
fi

echo -e "\n${GREEN}Step 1: Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi
echo -e "✓ Python 3 found: $(python3 --version)"

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: Git is required${NC}"
    exit 1
fi
echo -e "✓ Git found: $(git --version)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is required${NC}"
    exit 1
fi
echo -e "✓ pip3 found"

echo -e "\n${GREEN}Step 2: Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "✓ Virtual environment created"
else
    echo -e "✓ Virtual environment already exists"
fi

echo -e "\n${GREEN}Step 3: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "✓ Virtual environment activated"

echo -e "\n${GREEN}Step 4: Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "✓ Dependencies installed"
else
    echo -e "${YELLOW}Warning: requirements.txt not found${NC}"
fi

echo -e "\n${GREEN}Step 5: Creating directory structure...${NC}"
mkdir -p logs
mkdir -p data
mkdir -p ../worktrees
echo -e "✓ Directory structure created"

echo -e "\n${GREEN}Step 6: Setting up Git configuration...${NC}"
# Configure git for worktree support
git config --local core.worktree true
echo -e "✓ Git configured for worktrees"

echo -e "\n${GREEN}Step 7: Verifying configuration files...${NC}"
if [ -f "config/agents.yaml" ]; then
    echo -e "✓ agents.yaml found"
fi
if [ -f "config/security.yaml" ]; then
    echo -e "✓ security.yaml found"
fi
if [ -f "config/worktree.yaml" ]; then
    echo -e "✓ worktree.yaml found"
fi

echo -e "\n${GREEN}Step 8: Running security setup...${NC}"
if [ -f "scripts/setup-security.sh" ]; then
    bash scripts/setup-security.sh
    echo -e "✓ Security setup completed"
else
    echo -e "${YELLOW}Warning: setup-security.sh not found${NC}"
fi

echo -e "\n${GREEN}=== Initialization Complete ===${NC}"
echo
echo -e "Next steps:"
echo -e "1. Activate virtual environment: ${YELLOW}source venv/bin/activate${NC}"
echo -e "2. Configure GCP credentials (if using GCP)"
echo -e "3. Update configuration files in config/"
echo -e "4. Run tests: ${YELLOW}pytest${NC}"
echo
echo -e "${GREEN}Ready to start autonomous development!${NC}"
