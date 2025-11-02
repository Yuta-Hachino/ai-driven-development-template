#!/bin/bash

# Production Deployment Automation Script
# Deploys Autonomous Development System to production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="autonomous-dev-prod"
VERSION="${VERSION:-latest}"
REGISTRY="ghcr.io/autonomous-dev"
IMAGE_NAME="autonomous-dev"
KUBECTL_CONTEXT="${KUBECTL_CONTEXT:-production-cluster}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Production Deployment - Phase 5${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Version: ${VERSION}"
echo "Namespace: ${NAMESPACE}"
echo "Context: ${KUBECTL_CONTEXT}"
echo ""

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

# Pre-deployment checks
print_header "Pre-Deployment Checks"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl."
    exit 1
fi
print_success "kubectl found"

# Set context
kubectl config use-context "${KUBECTL_CONTEXT}"
print_success "Context set to ${KUBECTL_CONTEXT}"

# Verify cluster access
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot access cluster. Check your kubeconfig."
    exit 1
fi
print_success "Cluster access verified"

# Confirmation
print_header "Deployment Confirmation"
echo "You are about to deploy to PRODUCTION"
echo "Namespace: ${NAMESPACE}"
echo "Version: ${VERSION}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    print_error "Deployment cancelled"
    exit 1
fi

# Create namespace
print_header "Step 1: Create Namespace"
kubectl apply -f k8s/production/namespace.yaml
print_success "Namespace created/updated"

# Deploy storage
print_header "Step 2: Deploy Storage"
kubectl apply -f k8s/production/storage.yaml
print_success "Storage deployed"

# Wait for PVCs
echo "Waiting for PVCs to be bound..."
kubectl wait --for=condition=Bound pvc/autonomous-dev-data-pvc -n ${NAMESPACE} --timeout=300s
print_success "PVCs bound"

# Deploy ConfigMaps
print_header "Step 3: Deploy ConfigMaps"
kubectl apply -f k8s/production/configmap.yaml
print_success "ConfigMaps deployed"

# Deploy Secrets
print_header "Step 4: Deploy Secrets"
if [ -f ".env.production" ]; then
    kubectl create secret generic autonomous-dev-secrets \
        --from-env-file=.env.production \
        --namespace=${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -
    print_success "Secrets deployed from .env.production"
else
    print_warning "No .env.production file found. Skipping secrets creation."
    print_warning "Please create secrets manually."
fi

# Deploy application
print_header "Step 5: Deploy Application"
kubectl apply -f k8s/production/deployment.yaml
print_success "Deployment created/updated"

# Wait for deployment
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/autonomous-dev -n ${NAMESPACE} --timeout=600s
print_success "Deployment ready"

# Deploy services
print_header "Step 6: Deploy Services"
kubectl apply -f k8s/production/service.yaml
print_success "Services deployed"

# Deploy ingress
print_header "Step 7: Deploy Ingress"
kubectl apply -f k8s/production/ingress.yaml
print_success "Ingress deployed"

# Deploy monitoring
print_header "Step 8: Deploy Monitoring"
kubectl apply -f k8s/production/monitoring/prometheus-deployment.yaml
kubectl apply -f k8s/production/monitoring/grafana-deployment.yaml
kubectl apply -f k8s/production/monitoring/grafana-dashboards.yaml
print_success "Monitoring deployed"

# Wait for monitoring
echo "Waiting for monitoring to be ready..."
kubectl rollout status deployment/prometheus -n ${NAMESPACE} --timeout=300s
kubectl rollout status deployment/grafana -n ${NAMESPACE} --timeout=300s
print_success "Monitoring ready"

# Health checks
print_header "Step 9: Health Checks"

# Check pods
echo "Checking pod status..."
kubectl get pods -n ${NAMESPACE}

# Wait for all pods to be ready
kubectl wait --for=condition=Ready pods -l app=autonomous-dev -n ${NAMESPACE} --timeout=300s
print_success "All application pods ready"

# Get service endpoints
print_header "Deployment Complete"

echo ""
echo "Services:"
kubectl get svc -n ${NAMESPACE}

echo ""
echo "Pods:"
kubectl get pods -n ${NAMESPACE}

echo ""
echo "Ingress:"
kubectl get ingress -n ${NAMESPACE}

echo ""
print_success "Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Verify health: curl https://autonomous-dev.example.com/health/live"
echo "2. Check logs: kubectl logs -n ${NAMESPACE} deployment/autonomous-dev"
echo "3. Access Grafana: https://grafana.autonomous-dev.example.com"
echo "4. Run smoke tests"
echo ""

exit 0
