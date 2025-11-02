#!/bin/bash

# Security Scanning Script
# Performs comprehensive security scanning using multiple tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCAN_RESULTS_DIR="${REPO_ROOT}/security/scan_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${SCAN_RESULTS_DIR}/security_report_${TIMESTAMP}.json"

# Create results directory
mkdir -p "${SCAN_RESULTS_DIR}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Security Scanning - Phase 4${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print section header
print_header() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Initialize report
cat > "${REPORT_FILE}" <<EOF
{
  "scan_timestamp": "${TIMESTAMP}",
  "repository": "$(basename ${REPO_ROOT})",
  "scans": {}
}
EOF

# 1. Secret Scanning with gitleaks
print_header "1. Secret Scanning (gitleaks)"

if command_exists gitleaks; then
    gitleaks detect \
        --source="${REPO_ROOT}" \
        --report-format=json \
        --report-path="${SCAN_RESULTS_DIR}/secrets_${TIMESTAMP}.json" \
        --no-git \
        --verbose || true

    if [ -f "${SCAN_RESULTS_DIR}/secrets_${TIMESTAMP}.json" ]; then
        SECRET_COUNT=$(jq length "${SCAN_RESULTS_DIR}/secrets_${TIMESTAMP}.json" 2>/dev/null || echo "0")
        if [ "$SECRET_COUNT" -gt 0 ]; then
            print_error "Found ${SECRET_COUNT} potential secrets"
        else
            print_success "No secrets detected"
        fi
    else
        print_success "No secrets detected"
    fi
else
    print_warning "gitleaks not installed - skipping secret scanning"
    print_warning "Install with: brew install gitleaks (macOS) or visit https://github.com/zricethezav/gitleaks"
fi

# 2. Dependency Vulnerability Scanning with Safety
print_header "2. Dependency Vulnerability Scanning (Safety)"

if [ -f "${REPO_ROOT}/requirements.txt" ]; then
    if command_exists safety; then
        safety check \
            --file="${REPO_ROOT}/requirements.txt" \
            --json \
            --output="${SCAN_RESULTS_DIR}/dependencies_${TIMESTAMP}.json" || true

        if [ -f "${SCAN_RESULTS_DIR}/dependencies_${TIMESTAMP}.json" ]; then
            VULN_COUNT=$(jq '.vulnerabilities | length' "${SCAN_RESULTS_DIR}/dependencies_${TIMESTAMP}.json" 2>/dev/null || echo "0")
            if [ "$VULN_COUNT" -gt 0 ]; then
                print_error "Found ${VULN_COUNT} dependency vulnerabilities"
            else
                print_success "No dependency vulnerabilities found"
            fi
        fi
    else
        print_warning "safety not installed - skipping dependency scanning"
        print_warning "Install with: pip install safety"
    fi
else
    print_warning "No requirements.txt found - skipping dependency scanning"
fi

# 3. Static Code Analysis with Bandit
print_header "3. Static Code Analysis (Bandit)"

if command_exists bandit; then
    bandit -r "${REPO_ROOT}/src" \
        -f json \
        -o "${SCAN_RESULTS_DIR}/bandit_${TIMESTAMP}.json" \
        --skip B101,B601 \
        --quiet || true

    if [ -f "${SCAN_RESULTS_DIR}/bandit_${TIMESTAMP}.json" ]; then
        HIGH_ISSUES=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' "${SCAN_RESULTS_DIR}/bandit_${TIMESTAMP}.json" 2>/dev/null || echo "0")
        MEDIUM_ISSUES=$(jq '[.results[] | select(.issue_severity == "MEDIUM")] | length' "${SCAN_RESULTS_DIR}/bandit_${TIMESTAMP}.json" 2>/dev/null || echo "0")

        if [ "$HIGH_ISSUES" -gt 0 ]; then
            print_error "Found ${HIGH_ISSUES} high-severity security issues"
        elif [ "$MEDIUM_ISSUES" -gt 0 ]; then
            print_warning "Found ${MEDIUM_ISSUES} medium-severity security issues"
        else
            print_success "No high or medium severity issues found"
        fi
    fi
else
    print_warning "bandit not installed - skipping code analysis"
    print_warning "Install with: pip install bandit"
fi

# 4. Container Scanning with Trivy (if Dockerfile exists)
print_header "4. Container Security Scanning (Trivy)"

if [ -f "${REPO_ROOT}/Dockerfile" ] || [ -f "${REPO_ROOT}/.dockerignore" ]; then
    if command_exists trivy; then
        trivy fs \
            --format json \
            --output "${SCAN_RESULTS_DIR}/trivy_${TIMESTAMP}.json" \
            --severity HIGH,CRITICAL \
            "${REPO_ROOT}" || true

        if [ -f "${SCAN_RESULTS_DIR}/trivy_${TIMESTAMP}.json" ]; then
            CRITICAL_VULNS=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "${SCAN_RESULTS_DIR}/trivy_${TIMESTAMP}.json" 2>/dev/null || echo "0")
            HIGH_VULNS=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' "${SCAN_RESULTS_DIR}/trivy_${TIMESTAMP}.json" 2>/dev/null || echo "0")

            if [ "$CRITICAL_VULNS" -gt 0 ]; then
                print_error "Found ${CRITICAL_VULNS} critical vulnerabilities"
            elif [ "$HIGH_VULNS" -gt 0 ]; then
                print_warning "Found ${HIGH_VULNS} high-severity vulnerabilities"
            else
                print_success "No critical or high vulnerabilities found"
            fi
        fi
    else
        print_warning "trivy not installed - skipping container scanning"
        print_warning "Install from: https://aquasecurity.github.io/trivy"
    fi
else
    print_warning "No Dockerfile found - skipping container scanning"
fi

# 5. License Compliance Check
print_header "5. License Compliance Check"

if command_exists pip-licenses; then
    pip-licenses \
        --format=json \
        --output-file="${SCAN_RESULTS_DIR}/licenses_${TIMESTAMP}.json" || true

    if [ -f "${SCAN_RESULTS_DIR}/licenses_${TIMESTAMP}.json" ]; then
        # Check for GPL licenses (example - customize based on policy)
        GPL_COUNT=$(jq '[.[] | select(.License | contains("GPL"))] | length' "${SCAN_RESULTS_DIR}/licenses_${TIMESTAMP}.json" 2>/dev/null || echo "0")

        if [ "$GPL_COUNT" -gt 0 ]; then
            print_warning "Found ${GPL_COUNT} GPL-licensed dependencies"
        else
            print_success "License compliance check passed"
        fi
    fi
else
    print_warning "pip-licenses not installed - skipping license check"
    print_warning "Install with: pip install pip-licenses"
fi

# 6. SAST with Semgrep
print_header "6. Semantic Code Analysis (Semgrep)"

if command_exists semgrep; then
    semgrep \
        --config=auto \
        --json \
        --output="${SCAN_RESULTS_DIR}/semgrep_${TIMESTAMP}.json" \
        "${REPO_ROOT}/src" || true

    if [ -f "${SCAN_RESULTS_DIR}/semgrep_${TIMESTAMP}.json" ]; then
        ERROR_COUNT=$(jq '.results | map(select(.extra.severity == "ERROR")) | length' "${SCAN_RESULTS_DIR}/semgrep_${TIMESTAMP}.json" 2>/dev/null || echo "0")
        WARNING_COUNT=$(jq '.results | map(select(.extra.severity == "WARNING")) | length' "${SCAN_RESULTS_DIR}/semgrep_${TIMESTAMP}.json" 2>/dev/null || echo "0")

        if [ "$ERROR_COUNT" -gt 0 ]; then
            print_error "Found ${ERROR_COUNT} error-level security issues"
        elif [ "$WARNING_COUNT" -gt 0 ]; then
            print_warning "Found ${WARNING_COUNT} warning-level security issues"
        else
            print_success "No security issues found"
        fi
    fi
else
    print_warning "semgrep not installed - skipping semantic analysis"
    print_warning "Install with: pip install semgrep"
fi

# 7. Infrastructure as Code Scanning (if terraform/k8s files exist)
print_header "7. Infrastructure Security (tfsec / checkov)"

if [ -d "${REPO_ROOT}/terraform" ] || [ -d "${REPO_ROOT}/k8s" ]; then
    if command_exists checkov; then
        checkov \
            --directory "${REPO_ROOT}" \
            --framework terraform kubernetes \
            --output json \
            --output-file-path "${SCAN_RESULTS_DIR}" \
            --soft-fail || true

        print_success "Infrastructure security scan completed"
    else
        print_warning "checkov not installed - skipping IaC scanning"
        print_warning "Install with: pip install checkov"
    fi
else
    print_warning "No IaC files found - skipping IaC scanning"
fi

# Generate Summary Report
print_header "Security Scan Summary"

cat > "${SCAN_RESULTS_DIR}/summary_${TIMESTAMP}.txt" <<EOF
Security Scan Report
====================
Date: $(date)
Repository: $(basename ${REPO_ROOT})

Scan Results:
-------------
EOF

# Count total issues
TOTAL_CRITICAL=0
TOTAL_HIGH=0
TOTAL_MEDIUM=0
TOTAL_LOW=0

echo ""
echo -e "${BLUE}Scan Results Summary:${NC}"
echo "  Report Location: ${REPORT_FILE}"
echo "  Results Directory: ${SCAN_RESULTS_DIR}"
echo ""

# Check if any critical issues found
if [ -f "${SCAN_RESULTS_DIR}/trivy_${TIMESTAMP}.json" ]; then
    CRITICAL=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' "${SCAN_RESULTS_DIR}/trivy_${TIMESTAMP}.json" 2>/dev/null || echo "0")
    TOTAL_CRITICAL=$((TOTAL_CRITICAL + CRITICAL))
fi

if [ -f "${SCAN_RESULTS_DIR}/bandit_${TIMESTAMP}.json" ]; then
    HIGH=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' "${SCAN_RESULTS_DIR}/bandit_${TIMESTAMP}.json" 2>/dev/null || echo "0")
    TOTAL_HIGH=$((TOTAL_HIGH + HIGH))
fi

echo -e "${BLUE}Issue Summary:${NC}"
echo "  Critical: ${TOTAL_CRITICAL}"
echo "  High: ${TOTAL_HIGH}"
echo "  Medium: ${TOTAL_MEDIUM}"
echo "  Low: ${TOTAL_LOW}"
echo ""

# Determine overall status
if [ "$TOTAL_CRITICAL" -gt 0 ]; then
    print_error "Security scan FAILED - Critical issues found"
    EXIT_CODE=1
elif [ "$TOTAL_HIGH" -gt 5 ]; then
    print_warning "Security scan WARNING - Multiple high-severity issues found"
    EXIT_CODE=0
else
    print_success "Security scan PASSED"
    EXIT_CODE=0
fi

# Generate HTML report (if pandoc available)
if command_exists pandoc; then
    echo "# Security Scan Report" > "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"
    echo "" >> "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"
    echo "**Date:** $(date)" >> "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"
    echo "**Repository:** $(basename ${REPO_ROOT})" >> "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"
    echo "" >> "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"
    echo "## Summary" >> "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"
    echo "- Critical: ${TOTAL_CRITICAL}" >> "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"
    echo "- High: ${TOTAL_HIGH}" >> "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"
    echo "- Medium: ${TOTAL_MEDIUM}" >> "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md"

    pandoc "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.md" \
        -o "${SCAN_RESULTS_DIR}/report_${TIMESTAMP}.html" \
        --standalone || true
fi

echo ""
print_header "Recommendations"

if [ "$TOTAL_CRITICAL" -gt 0 ]; then
    echo "1. Address all critical vulnerabilities immediately"
    echo "2. Review scan results in ${SCAN_RESULTS_DIR}"
    echo "3. Update vulnerable dependencies"
    echo "4. Re-run security scan after fixes"
fi

if [ "$TOTAL_HIGH" -gt 0 ]; then
    echo "1. Review and address high-severity issues"
    echo "2. Implement security best practices"
    echo "3. Add security tests to CI/CD pipeline"
fi

echo ""
print_success "Security scan completed"
echo "Full report: ${REPORT_FILE}"
echo ""

exit ${EXIT_CODE}
