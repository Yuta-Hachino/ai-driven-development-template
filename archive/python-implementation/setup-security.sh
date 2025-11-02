#!/bin/bash
# Security Setup Script
# Sets up enterprise-grade security configurations

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Security Setup ===${NC}"
echo

echo -e "${GREEN}Step 1: Creating security directories...${NC}"
mkdir -p .secrets
mkdir -p logs/security
chmod 700 .secrets
echo -e "✓ Security directories created"

echo -e "\n${GREEN}Step 2: Generating secure random secrets...${NC}"
# Generate random secrets for development
if [ ! -f ".secrets/encryption_key" ]; then
    openssl rand -hex 32 > .secrets/encryption_key
    chmod 600 .secrets/encryption_key
    echo -e "✓ Encryption key generated"
else
    echo -e "✓ Encryption key already exists"
fi

if [ ! -f ".secrets/session_secret" ]; then
    openssl rand -hex 32 > .secrets/session_secret
    chmod 600 .secrets/session_secret
    echo -e "✓ Session secret generated"
else
    echo -e "✓ Session secret already exists"
fi

echo -e "\n${GREEN}Step 3: Setting up .gitignore for secrets...${NC}"
if ! grep -q ".secrets" .gitignore 2>/dev/null; then
    echo ".secrets/" >> .gitignore
    echo "*.key" >> .gitignore
    echo "*.pem" >> .gitignore
    echo -e "✓ Updated .gitignore"
else
    echo -e "✓ .gitignore already configured"
fi

echo -e "\n${GREEN}Step 4: Setting secure file permissions...${NC}"
chmod 600 config/security.yaml
echo -e "✓ Secure permissions set"

echo -e "\n${GREEN}Step 5: Verifying security configuration...${NC}"
if [ -f "config/security.yaml" ]; then
    echo -e "✓ Security configuration found"

    # Check for required security settings
    if grep -q "encryption:" config/security.yaml; then
        echo -e "✓ Encryption configured"
    fi

    if grep -q "authentication:" config/security.yaml; then
        echo -e "✓ Authentication configured"
    fi

    if grep -q "audit:" config/security.yaml; then
        echo -e "✓ Audit logging configured"
    fi
else
    echo -e "${RED}Error: security.yaml not found${NC}"
    exit 1
fi

echo -e "\n${GREEN}Step 6: Security tools check...${NC}"
# Check for security tools (optional)
if command -v trivy &> /dev/null; then
    echo -e "✓ Trivy (vulnerability scanner) found"
else
    echo -e "${YELLOW}! Trivy not found - install for vulnerability scanning${NC}"
fi

if command -v bandit &> /dev/null; then
    echo -e "✓ Bandit (Python security linter) found"
else
    echo -e "${YELLOW}! Bandit not found - install for Python security checks${NC}"
fi

echo -e "\n${GREEN}=== Security Setup Complete ===${NC}"
echo
echo -e "Security checklist:"
echo -e "✓ Encryption keys generated"
echo -e "✓ Secure directories created"
echo -e "✓ File permissions set"
echo -e "✓ Configuration verified"
echo
echo -e "${YELLOW}Important:${NC}"
echo -e "1. Never commit files in .secrets/ directory"
echo -e "2. Use environment variables for production secrets"
echo -e "3. Enable MFA for all users"
echo -e "4. Regularly rotate encryption keys"
echo -e "5. Review audit logs regularly"
echo
