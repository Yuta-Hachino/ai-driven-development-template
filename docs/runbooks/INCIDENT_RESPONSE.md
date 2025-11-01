# Incident Response Runbook

## Overview

This runbook provides procedures for responding to incidents in the Autonomous Development System.

**Last Updated:** 2025-11-01
**Environment:** Production
**Severity Levels:** P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)

---

## Incident Severity Definitions

### P0 - Critical
- **Impact:** Complete service outage
- **Response Time:** 15 minutes
- **Examples:**
  - All pods down
  - Database unavailable
  - Security breach
- **Escalation:** Immediately page on-call + team lead

### P1 - High
- **Impact:** Significant degradation affecting >50% of users
- **Response Time:** 30 minutes
- **Examples:**
  - Error rate > 10%
  - Latency > 5x normal
  - Critical feature broken
- **Escalation:** Page on-call

### P2 - Medium
- **Impact:** Minor degradation affecting <50% of users
- **Response Time:** 2 hours
- **Examples:**
  - Error rate 5-10%
  - Single agent type failing
  - Non-critical feature broken
- **Escalation:** Slack notification to team

### P3 - Low
- **Impact:** Minor issues with no user impact
- **Response Time:** Next business day
- **Examples:**
  - Warning logs increasing
  - Resource usage trending up
  - Cosmetic issues
- **Escalation:** Create ticket

---

## Incident Response Process

### 1. Detection

**Automated Alerts:**
- Prometheus alerts
- Health check failures
- Error rate threshold breaches
- Resource exhaustion warnings

**Manual Detection:**
- User reports
- Monitoring dashboard anomalies
- Team member observations

**Initial Actions:**
```bash
# Check overall system health
kubectl get pods -n autonomous-dev-prod
kubectl top pods -n autonomous-dev-prod

# Check recent events
kubectl get events -n autonomous-dev-prod --sort-by='.lastTimestamp' | tail -20

# Check application logs
kubectl logs -n autonomous-dev-prod deployment/autonomous-dev --tail=100
```

---

### 2. Assessment

**Determine Severity:**
1. How many users/instances affected?
2. Is data at risk?
3. Is security compromised?
4. What's the business impact?

**Gather Information:**
```bash
# Check deployment status
kubectl get deployment autonomous-dev -n autonomous-dev-prod -o yaml

# Check recent changes
kubectl rollout history deployment/autonomous-dev -n autonomous-dev-prod

# Check Prometheus metrics
# Access Prometheus UI and check:
# - Error rate: rate(http_requests_total{status=~"5.."}[5m])
# - Latency: histogram_quantile(0.95, http_request_duration_seconds_bucket)
# - Resource usage: container_memory_usage_bytes, container_cpu_usage_seconds_total
```

**Create Incident Ticket:**
```markdown
Title: [P0] Production Outage - <Brief Description>

Description:
- Time detected: <timestamp>
- Affected components: <list>
- User impact: <description>
- Initial symptoms: <description>
- Relevant metrics/logs: <links>
```

---

### 3. Communication

**Start Incident Channel:**
```bash
# Create dedicated Slack channel
#incident-2025-11-01-<brief-name>

# Post initial status
**INCIDENT DECLARED - P0**
Time: 14:30 UTC
Impact: All services unavailable
Status: Investigating
Incident Commander: @username
```

**Notify Stakeholders:**
- **P0:** CEO, CTO, Product Lead, All Engineers
- **P1:** CTO, Engineering Lead, On-Call Team
- **P2:** Engineering Lead, On-Call Engineer
- **P3:** Create ticket, no immediate notification

**Status Updates:**
- **P0/P1:** Every 15-30 minutes
- **P2:** Every 1-2 hours
- **P3:** Daily or when resolved

---

### 4. Investigation

#### Common Issues and Diagnostics

**Issue: Pods Crashing**
```bash
# Check pod status
kubectl get pods -n autonomous-dev-prod -l app=autonomous-dev

# Describe failed pod
kubectl describe pod <pod-name> -n autonomous-dev-prod

# Check logs
kubectl logs <pod-name> -n autonomous-dev-prod --previous

# Common causes:
# - Out of memory: Check memory limits
# - Configuration error: Check ConfigMap/Secrets
# - Image pull failure: Check registry access
# - Startup probe failure: Check application startup time
```

**Issue: High Error Rate**
```bash
# Check application logs for errors
kubectl logs -n autonomous-dev-prod deployment/autonomous-dev --tail=500 | grep ERROR

# Check Prometheus
# Error rate by endpoint
rate(http_requests_total{status=~"5..",namespace="autonomous-dev-prod"}[5m])

# Top errors
topk(10, sum by (endpoint, status) (rate(http_requests_total{status=~"5.."}[5m])))

# Common causes:
# - Dependent service down: Check external dependencies
# - Database issues: Check database connectivity
# - Bad deployment: Consider rollback
# - Rate limiting: Check rate limit configuration
```

**Issue: High Latency**
```bash
# Check P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Check database query time
histogram_quantile(0.95, rate(database_query_duration_seconds_bucket[5m]))

# Check resource usage
kubectl top pods -n autonomous-dev-prod

# Common causes:
# - Resource exhaustion: Scale up
# - Database slow queries: Check slow query log
# - Network issues: Check network latency
# - External API slow: Check third-party status
```

**Issue: Resource Exhaustion**
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n autonomous-dev-prod

# Check resource limits
kubectl describe deployment autonomous-dev -n autonomous-dev-prod | grep -A 5 "Limits"

# Check for OOMKilled pods
kubectl get pods -n autonomous-dev-prod -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].lastState.terminated.reason}{"\n"}{end}' | grep OOMKilled

# Common causes:
# - Memory leak: Check for memory leaks in application
# - Traffic spike: Scale horizontally
# - Inefficient queries: Optimize queries
# - Too many worktrees: Clean up old worktrees
```

---

### 5. Mitigation

#### Quick Wins

**Rollback Deployment**
```bash
# Rollback to previous version
kubectl rollout undo deployment/autonomous-dev -n autonomous-dev-prod

# Verify rollback
kubectl rollout status deployment/autonomous-dev -n autonomous-dev-prod
```

**Scale Up**
```bash
# Increase replicas
kubectl scale deployment autonomous-dev -n autonomous-dev-prod --replicas=5

# Verify scaling
kubectl get deployment autonomous-dev -n autonomous-dev-prod
```

**Restart Pods**
```bash
# Rolling restart
kubectl rollout restart deployment/autonomous-dev -n autonomous-dev-prod

# Force delete stuck pod
kubectl delete pod <pod-name> -n autonomous-dev-prod --force --grace-period=0
```

**Increase Resources**
```bash
# Increase memory limit
kubectl set resources deployment autonomous-dev -n autonomous-dev-prod \
  --limits=memory=16Gi,cpu=8

# Verify change
kubectl rollout status deployment/autonomous-dev -n autonomous-dev-prod
```

#### Workarounds

**Disable Feature Flag**
```bash
# Update ConfigMap to disable problematic feature
kubectl edit configmap autonomous-dev-config -n autonomous-dev-prod
# Set ENABLE_<FEATURE>=false

# Restart deployment
kubectl rollout restart deployment/autonomous-dev -n autonomous-dev-prod
```

**Drain Traffic**
```bash
# Remove pod from service
kubectl label pod <pod-name> -n autonomous-dev-prod app-

# Pod will be replaced by deployment controller
```

**Database Failover**
```bash
# If using Cloud SQL or RDS
# Follow cloud provider's failover procedure

# Update connection string in secret
kubectl patch secret autonomous-dev-secrets -n autonomous-dev-prod \
  -p '{"data":{"database-url":"<new-base64-encoded-url>"}}'

# Restart application
kubectl rollout restart deployment/autonomous-dev -n autonomous-dev-prod
```

---

### 6. Resolution

**Verify Fix**
```bash
# Check all pods healthy
kubectl get pods -n autonomous-dev-prod -l app=autonomous-dev

# Check error rate
# Should be < 1%

# Check latency
# P95 should be < 500ms

# Run smoke tests
curl https://autonomous-dev.example.com/health/live
curl https://autonomous-dev.example.com/api/v1/status
```

**Confirm User Impact Resolved**
- Monitor error rate for 15 minutes
- Check customer success channel for reports
- Review metrics against baseline

**Close Incident**
```bash
# Post in incident channel
**INCIDENT RESOLVED**
Time resolved: 15:45 UTC
Duration: 75 minutes
Root cause: <brief description>
Fix applied: <description>
Action items: <link to post-mortem>
```

---

### 7. Post-Incident

**Post-Mortem (Required for P0/P1)**

Template:
```markdown
# Incident Post-Mortem

**Date:** 2025-11-01
**Duration:** 75 minutes (14:30 - 15:45 UTC)
**Severity:** P0
**Impact:** Complete service outage, 0 requests served

## Timeline
- 14:30: Alert triggered - all pods down
- 14:32: On-call engineer paged
- 14:35: Investigation started
- 14:45: Root cause identified - bad deployment
- 14:50: Rollback initiated
- 15:00: Rollback completed
- 15:15: Service restored, monitoring
- 15:45: Incident closed

## Root Cause
Deployment v1.2.3 introduced a configuration error that caused all pods to crash on startup.

## What Went Well
- Alert triggered immediately
- Response time under SLA
- Rollback procedure worked smoothly
- Communication was clear and timely

## What Didn't Go Well
- No pre-deployment validation caught the config error
- Rollout was too fast (all pods updated simultaneously)
- Backup system did not activate

## Action Items
1. [P0] Add configuration validation to CI/CD - @owner - Due: 2025-11-03
2. [P1] Implement gradual rollout (10% → 50% → 100%) - @owner - Due: 2025-11-08
3. [P1] Set up canary deployment - @owner - Due: 2025-11-15
4. [P2] Review and test backup system - @owner - Due: 2025-11-10
5. [P2] Update runbook with lessons learned - @owner - Due: 2025-11-03

## Lessons Learned
- Configuration changes are as risky as code changes
- Gradual rollouts prevent total outages
- Need better pre-production validation
```

**Follow-up Actions:**
1. Schedule post-mortem meeting within 48 hours
2. Track action items in issue tracker
3. Update runbooks
4. Share learnings with team

---

## Playbooks by Incident Type

### Database Outage

1. **Check database status**
   ```bash
   # For Cloud SQL
   gcloud sql instances describe <instance-name>

   # Check connectivity
   kubectl run -it --rm debug --image=postgres:14 --restart=Never -- \
     psql $DATABASE_URL -c "SELECT 1"
   ```

2. **Failover to replica**
   - Follow cloud provider documentation
   - Update connection string
   - Restart application

3. **Restore from backup**
   - See [BACKUP_RESTORE.md](./BACKUP_RESTORE.md)

### Memory Leak

1. **Identify leaking pod**
   ```bash
   kubectl top pods -n autonomous-dev-prod --sort-by=memory
   ```

2. **Capture heap dump**
   ```bash
   kubectl exec -it <pod-name> -n autonomous-dev-prod -- \
     python -m memory_profiler <script>
   ```

3. **Restart pod**
   ```bash
   kubectl delete pod <pod-name> -n autonomous-dev-prod
   ```

4. **Investigate offline**
   - Analyze heap dump
   - Review code changes
   - Check for circular references

### Security Breach

1. **Isolate affected components**
   ```bash
   # Remove from load balancer
   kubectl label pod <pod-name> -n autonomous-dev-prod app-

   # Block network access
   kubectl apply -f network-policy-lockdown.yaml
   ```

2. **Collect evidence**
   ```bash
   # Capture logs
   kubectl logs <pod-name> -n autonomous-dev-prod > evidence.log

   # Capture pod state
   kubectl get pod <pod-name> -n autonomous-dev-prod -o yaml > pod-state.yaml
   ```

3. **Notify security team**
   - Email: security@example.com
   - Slack: #security-incidents
   - Follow security incident response plan

4. **Rotate all credentials**
   ```bash
   # Rotate secrets
   kubectl delete secret autonomous-dev-secrets -n autonomous-dev-prod
   # Recreate with new credentials
   ```

### Third-Party Service Outage

1. **Check service status**
   - Visit status page
   - Check Twitter/status accounts

2. **Enable circuit breaker**
   ```bash
   # Update feature flags
   kubectl edit configmap autonomous-dev-config -n autonomous-dev-prod
   # Set CIRCUIT_BREAKER_ENABLED=true
   ```

3. **Switch to backup provider (if available)**
   - Update configuration
   - Restart application

4. **Communicate with users**
   - Update status page
   - Post notification

---

## Emergency Contacts

| Role | Name | Slack | Phone | Timezone |
|------|------|-------|-------|----------|
| On-Call Primary | See PagerDuty | @oncall | - | - |
| On-Call Secondary | See PagerDuty | @oncall-backup | - | - |
| Engineering Lead | - | @eng-lead | - | PST |
| CTO | - | @cto | - | EST |
| Security Lead | - | @security-lead | - | UTC |

**Escalation Path:**
1. On-Call Engineer
2. On-Call Lead
3. Engineering Manager
4. CTO

---

## Tools and Resources

- **Monitoring:** https://grafana.autonomous-dev.example.com
- **Logs:** `kubectl logs -n autonomous-dev-prod`
- **Metrics:** https://prometheus.autonomous-dev.example.com
- **Status Page:** https://status.autonomous-dev.example.com
- **Runbooks:** `docs/runbooks/`
- **PagerDuty:** https://autonomous-dev.pagerduty.com

---

## Training

All on-call engineers must:
- Complete incident response training
- Practice with tabletop exercises quarterly
- Participate in at least one incident response
- Review post-mortems from past incidents

---

## Appendix

### Useful Commands Cheat Sheet

```bash
# Quick health check
kubectl get pods -n autonomous-dev-prod
kubectl top pods -n autonomous-dev-prod
kubectl get events -n autonomous-dev-prod --sort-by='.lastTimestamp' | tail -20

# Logs
kubectl logs -n autonomous-dev-prod deployment/autonomous-dev --tail=100 -f
kubectl logs -n autonomous-dev-prod deployment/autonomous-dev --previous

# Describe resources
kubectl describe deployment autonomous-dev -n autonomous-dev-prod
kubectl describe pod <pod-name> -n autonomous-dev-prod

# Emergency actions
kubectl rollout undo deployment/autonomous-dev -n autonomous-dev-prod
kubectl scale deployment autonomous-dev -n autonomous-dev-prod --replicas=<N>
kubectl rollout restart deployment/autonomous-dev -n autonomous-dev-prod

# Debug
kubectl exec -it <pod-name> -n autonomous-dev-prod -- /bin/bash
kubectl run -it --rm debug --image=busybox --restart=Never -n autonomous-dev-prod -- sh
```

---

**Remember:** Stay calm, communicate clearly, and follow the process. We have runbooks, backups, and rollback procedures for a reason.
