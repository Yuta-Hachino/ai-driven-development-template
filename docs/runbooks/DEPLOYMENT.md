# Deployment Runbook - Autonomous Development System

## Overview

This runbook provides step-by-step instructions for deploying the Autonomous Development System to production.

**Last Updated:** 2025-11-01
**Environment:** Production
**Audience:** DevOps, SRE

---

## Prerequisites

### Required Tools
- `kubectl` (v1.28+)
- `helm` (v3.12+)
- `gcloud` CLI (for GCP) or `aws` CLI (for AWS)
- `docker` (v24.0+)
- Access to container registry

### Required Access
- Kubernetes cluster admin access
- Container registry push permissions
- Cloud provider credentials
- Secrets management system access

### Pre-Deployment Checklist
- [ ] All tests passing in CI/CD
- [ ] Security scan completed with no critical issues
- [ ] Performance benchmarks meet requirements
- [ ] Backup of current production state completed
- [ ] Rollback plan prepared
- [ ] Stakeholders notified
- [ ] Change request approved

---

## Deployment Process

### Step 1: Build and Push Container Image

```bash
# Set variables
export VERSION="1.0.0"
export REGISTRY="ghcr.io/autonomous-dev"
export IMAGE_NAME="autonomous-dev"

# Build the Docker image
docker build -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} .

# Tag as latest
docker tag ${REGISTRY}/${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:latest

# Push to registry
docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
docker push ${REGISTRY}/${IMAGE_NAME}:latest

# Verify the image
docker pull ${REGISTRY}/${IMAGE_NAME}:${VERSION}
```

**Expected Duration:** 10-15 minutes

**Validation:**
```bash
# Verify image exists
docker images | grep ${IMAGE_NAME}

# Check image size (should be < 500MB)
docker images ${REGISTRY}/${IMAGE_NAME}:${VERSION} --format "{{.Size}}"
```

---

### Step 2: Prepare Kubernetes Cluster

```bash
# Set cluster context
kubectl config use-context production-cluster

# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Create namespace (if not exists)
kubectl apply -f k8s/production/namespace.yaml

# Verify namespace
kubectl get namespace autonomous-dev-prod
```

**Expected Duration:** 2-3 minutes

**Validation:**
```bash
# Check namespace resource quotas
kubectl describe resourcequota -n autonomous-dev-prod

# Check limit ranges
kubectl describe limitrange -n autonomous-dev-prod
```

---

### Step 3: Configure Secrets

```bash
# Create secrets from environment variables
kubectl create secret generic autonomous-dev-secrets \
  --from-literal=database-url="${DATABASE_URL}" \
  --from-literal=redis-url="${REDIS_URL}" \
  --from-literal=api-key="${API_KEY}" \
  --from-literal=github-token="${GITHUB_TOKEN}" \
  --namespace=autonomous-dev-prod \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify secrets
kubectl get secrets -n autonomous-dev-prod
kubectl describe secret autonomous-dev-secrets -n autonomous-dev-prod
```

**Expected Duration:** 2 minutes

**Security Notes:**
- Never commit secrets to version control
- Use a secrets management system (e.g., HashiCorp Vault, AWS Secrets Manager)
- Rotate secrets regularly
- Limit access to secrets

---

### Step 4: Deploy Storage

```bash
# Apply StorageClass
kubectl apply -f k8s/production/storage.yaml

# Wait for PVCs to be bound
kubectl get pvc -n autonomous-dev-prod --watch

# Expected status: Bound
```

**Expected Duration:** 3-5 minutes

**Validation:**
```bash
# Check PVC status
kubectl get pvc -n autonomous-dev-prod

# Check PV status
kubectl get pv | grep autonomous-dev-prod
```

---

### Step 5: Deploy ConfigMaps

```bash
# Apply ConfigMaps
kubectl apply -f k8s/production/configmap.yaml

# Verify ConfigMaps
kubectl get configmap -n autonomous-dev-prod
kubectl describe configmap autonomous-dev-config -n autonomous-dev-prod
```

**Expected Duration:** 1 minute

---

### Step 6: Deploy Application

```bash
# Apply deployment
kubectl apply -f k8s/production/deployment.yaml

# Watch deployment progress
kubectl rollout status deployment/autonomous-dev -n autonomous-dev-prod

# Expected output: "deployment "autonomous-dev" successfully rolled out"
```

**Expected Duration:** 5-10 minutes

**Validation:**
```bash
# Check pod status
kubectl get pods -n autonomous-dev-prod -l app=autonomous-dev

# Check deployment status
kubectl get deployment autonomous-dev -n autonomous-dev-prod

# View logs
kubectl logs -n autonomous-dev-prod deployment/autonomous-dev --tail=50
```

---

### Step 7: Deploy Services and Ingress

```bash
# Deploy services
kubectl apply -f k8s/production/service.yaml

# Deploy ingress
kubectl apply -f k8s/production/ingress.yaml

# Verify services
kubectl get svc -n autonomous-dev-prod

# Verify ingress
kubectl get ingress -n autonomous-dev-prod
```

**Expected Duration:** 2-3 minutes

**Validation:**
```bash
# Check service endpoints
kubectl get endpoints -n autonomous-dev-prod

# Get external IP (if LoadBalancer)
kubectl get svc autonomous-dev-lb -n autonomous-dev-prod
```

---

### Step 8: Deploy Monitoring

```bash
# Deploy Prometheus
kubectl apply -f k8s/production/monitoring/prometheus-deployment.yaml

# Deploy Grafana
kubectl apply -f k8s/production/monitoring/grafana-deployment.yaml
kubectl apply -f k8s/production/monitoring/grafana-dashboards.yaml

# Wait for monitoring to be ready
kubectl rollout status deployment/prometheus -n autonomous-dev-prod
kubectl rollout status deployment/grafana -n autonomous-dev-prod
```

**Expected Duration:** 5-7 minutes

**Validation:**
```bash
# Check Prometheus
kubectl get pods -n autonomous-dev-prod -l app=prometheus

# Check Grafana
kubectl get pods -n autonomous-dev-prod -l app=grafana

# Access Grafana (port-forward for testing)
kubectl port-forward -n autonomous-dev-prod svc/grafana 3000:3000
# Open http://localhost:3000
```

---

### Step 9: Health Checks

```bash
# Check all pods are running
kubectl get pods -n autonomous-dev-prod

# Check application health endpoint
INGRESS_IP=$(kubectl get ingress autonomous-dev-ingress -n autonomous-dev-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl https://autonomous-dev.example.com/health/live
curl https://autonomous-dev.example.com/health/ready

# Expected: HTTP 200 with {"status": "healthy"}
```

**Expected Duration:** 2 minutes

**Validation Checklist:**
- [ ] All pods in Running state
- [ ] Health check endpoints return 200
- [ ] No errors in application logs
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards loading

---

### Step 10: Smoke Tests

```bash
# Run basic API tests
curl -X GET https://autonomous-dev.example.com/api/v1/status
curl -X POST https://autonomous-dev.example.com/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{"type": "backend", "task": "test"}'

# Check metrics endpoint
curl https://autonomous-dev.example.com/metrics

# Verify worktree creation
kubectl exec -it -n autonomous-dev-prod deployment/autonomous-dev -- \
  python -c "from worktree import WorktreeManager; print('Worktree system: OK')"
```

**Expected Duration:** 5 minutes

---

## Post-Deployment

### Monitoring Setup

1. **Configure Alerts**
   ```bash
   # Verify alerting rules
   kubectl get prometheusrules -n autonomous-dev-prod
   ```

2. **Access Dashboards**
   - Grafana: `https://grafana.autonomous-dev.example.com`
   - Prometheus: `https://prometheus.autonomous-dev.example.com`

3. **Set up On-Call**
   - Update PagerDuty/Opsgenie rotation
   - Test alert delivery

### Documentation

1. Update deployment log
2. Document any issues encountered
3. Update runbook with lessons learned

### Communication

1. Notify stakeholders of successful deployment
2. Post in team Slack channel
3. Update status page

---

## Rollback Procedure

If issues are detected, follow the rollback procedure:

```bash
# Rollback to previous deployment
kubectl rollout undo deployment/autonomous-dev -n autonomous-dev-prod

# Check rollback status
kubectl rollout status deployment/autonomous-dev -n autonomous-dev-prod

# Verify previous version is running
kubectl get deployment autonomous-dev -n autonomous-dev-prod -o jsonpath='{.spec.template.spec.containers[0].image}'
```

**When to Rollback:**
- Critical errors in application logs
- Health checks failing
- Error rate > 5%
- P95 latency > 2x baseline
- Security vulnerability discovered

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n autonomous-dev-prod

# Common issues:
# - Image pull errors: Check registry access
# - CrashLoopBackOff: Check application logs
# - Pending: Check resource quotas and node capacity
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints autonomous-dev -n autonomous-dev-prod

# Check ingress
kubectl describe ingress autonomous-dev-ingress -n autonomous-dev-prod

# Test service internally
kubectl run -it --rm debug --image=busybox --restart=Never -n autonomous-dev-prod -- \
  wget -O- http://autonomous-dev:80/health
```

### High Memory Usage

```bash
# Check memory usage
kubectl top pods -n autonomous-dev-prod

# Increase memory limits if needed
kubectl set resources deployment autonomous-dev -n autonomous-dev-prod \
  --limits=memory=16Gi
```

---

## Contacts

- **On-Call Engineer:** See PagerDuty schedule
- **Team Lead:** [Name/Slack]
- **Platform Team:** platform-team@example.com
- **Security Team:** security@example.com

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-01 | 1.0.0 | Initial production deployment | DevOps Team |

---

## Additional Resources

- [Architecture Documentation](../ARCHITECTURE.md)
- [API Reference](../API_REFERENCE.md)
- [Incident Response Runbook](./INCIDENT_RESPONSE.md)
- [Scaling Runbook](./SCALING.md)
- [Backup and Restore](./BACKUP_RESTORE.md)
