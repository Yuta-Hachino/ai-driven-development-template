# Troubleshooting Guide

Common issues and solutions for Autonomous Dev.

---

## Installation Issues

### "command not found: autonomous-dev"

**Problem:** Binary not in PATH

**Solutions:**

1. Check if installed:
   ```bash
   which autonomous-dev
   ls /usr/local/bin/autonomous-dev
   ```

2. Add to PATH:
   ```bash
   export PATH="/usr/local/bin:$PATH"
   echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
   ```

3. Reinstall:
   ```bash
   brew reinstall autonomous-dev
   # or
   npm install -g @autonomous-dev/cli
   ```

---

### "permission denied" when running

**Problem:** Binary not executable

**Solution:**
```bash
sudo chmod +x /usr/local/bin/autonomous-dev
```

Or install to user directory:
```bash
mkdir -p ~/.local/bin
mv autonomous-dev ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
```

---

## Configuration Issues

### "GITHUB_TOKEN not set"

**Problem:** GitHub token environment variable missing

**Solutions:**

1. Set temporarily:
   ```bash
   export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
   ```

2. Set permanently:
   ```bash
   echo 'export GITHUB_TOKEN="ghp_xxx..."' >> ~/.zshrc
   source ~/.zshrc
   ```

3. Set in config:
   ```bash
   autonomous-dev config set github.token "ghp_xxx..."
   ```

---

### "Failed to load config"

**Problem:** Config file missing or corrupted

**Solution:**

1. Check if config exists:
   ```bash
   ls -la .autonomous-dev/config.yaml
   ```

2. If missing, reinitialize:
   ```bash
   autonomous-dev init
   ```

3. If corrupted, regenerate:
   ```bash
   rm .autonomous-dev/config.yaml
   autonomous-dev init
   ```

---

## GitHub API Issues

### "Failed to create issue"

**Problem:** Insufficient permissions

**Solutions:**

1. Verify token has correct scopes:
   - Go to https://github.com/settings/tokens
   - Check token has `repo` and `workflow` scopes

2. Check repository access:
   - Ensure you have write access to the repository
   - For organizations, check if apps/tokens are allowed

3. Regenerate token:
   - Delete old token
   - Create new token with `repo` + `workflow` scopes
   - Update environment variable

---

### "API rate limit exceeded"

**Problem:** Too many API requests

**Solutions:**

1. Check rate limit status:
   ```bash
   curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/rate_limit
   ```

2. Wait for reset (shown in response)

3. Use authenticated requests (higher limit):
   - Unauthenticated: 60 requests/hour
   - Authenticated: 5,000 requests/hour

4. Reduce polling frequency in dashboard (change from 5s to 10s+)

---

### "Failed to trigger workflow"

**Problem:** Workflow file not found or invalid

**Solutions:**

1. Check workflow file exists:
   ```bash
   ls .github/workflows/autonomous-dev.yml
   ```

2. Validate YAML syntax:
   ```bash
   # Use GitHub Actions validator
   cat .github/workflows/autonomous-dev.yml | yamllint -
   ```

3. Push workflow file to repository:
   ```bash
   git add .github/workflows/autonomous-dev.yml
   git commit -m "Add autonomous dev workflow"
   git push
   ```

4. Check workflow permissions:
   - Repository settings → Actions → General
   - Ensure "Allow all actions and reusable workflows"

---

## Workflow Execution Issues

### Instances not starting

**Problem:** GitHub Actions not triggering

**Solutions:**

1. Check GitHub Actions tab:
   - Go to repository → Actions
   - Look for workflow runs
   - Check for errors in logs

2. Verify workflow_dispatch enabled:
   ```yaml
   # .github/workflows/autonomous-dev.yml
   on:
     workflow_dispatch:  # This line required
   ```

3. Trigger manually:
   ```bash
   gh workflow run autonomous-dev.yml
   ```

4. Check GitHub Actions enabled:
   - Repository settings → Actions → General
   - Select "Allow all actions"

---

### Instances stuck in "queued"

**Problem:** GitHub Actions quota exceeded or runners busy

**Solutions:**

1. Check Actions usage:
   - Account settings → Billing → Plans and usage
   - Free: 2,000 minutes/month
   - If exceeded, wait for next month or upgrade

2. Reduce concurrent instances:
   ```yaml
   # .autonomous-dev/config.yaml
   workflow:
     concurrency: 2  # Reduce from 5 to 2
   ```

3. Use self-hosted runners (advanced):
   - Settings → Actions → Runners → New self-hosted runner

---

### "Workflow failed immediately"

**Problem:** Syntax error or missing dependencies

**Solutions:**

1. Check workflow logs:
   - Actions tab → Click failed run → View logs

2. Common errors:
   - **Missing checkout step**: Add `uses: actions/checkout@v4`
   - **Missing gh CLI**: Already included in ubuntu-latest
   - **Permission denied**: Check GITHUB_TOKEN permissions

3. Test locally:
   ```bash
   # Simulate workflow step
   bash scripts/instance-status-reporter.sh
   ```

---

## Instance Communication Issues

### Workers not reporting status

**Problem:** P2P communication failing

**Solutions:**

1. Check Issue was created:
   ```bash
   gh issue list --label autonomous-dev
   ```

2. Verify workers can comment:
   - Check GITHUB_TOKEN has `repo` scope
   - Look for errors in worker logs (Actions tab)

3. Check Issue comment permissions:
   - Repository settings → General → Features
   - Ensure "Issues" enabled

---

### Leader not detecting workers

**Problem:** Timing issue or parsing error

**Solutions:**

1. Increase leader wait time:
   ```yaml
   # In workflow template
   sleep 10  # Increase from 5 to 10 seconds
   ```

2. Check worker status format:
   - View Issue comments
   - Ensure JSON format is correct
   - Look for `INSTANCE_STATUS:START:N` markers

3. Debug parsing:
   ```bash
   # Manually test parsing
   source scripts/instance-status-reporter.sh
   get_other_instances_status
   ```

---

### High stale rate (instances marked as stale)

**Problem:** Instances timing out

**Solutions:**

1. Increase heartbeat timeout:
   ```bash
   # In instance-status-reporter.sh
   if [ $diff -gt 600 ]; then  # Change from 300 to 600 (10 min)
     echo "stale"
   fi
   ```

2. Reduce task complexity:
   - Break large tasks into smaller ones
   - Use fewer instances (--instances=2 instead of 5)

3. Check GitHub Actions performance:
   - Slow runners → use self-hosted
   - Network issues → retry with delay

---

## Dashboard Issues

### Dashboard not loading

**Problem:** Missing files or incorrect path

**Solutions:**

1. Check dashboard exists:
   ```bash
   ls dashboard/index.html
   ```

2. Open directly:
   ```bash
   open dashboard/index.html
   # or
   firefox dashboard/index.html
   ```

3. Deploy to GitHub Pages:
   - Repository settings → Pages
   - Source: main branch → /dashboard folder
   - Save

---

### "No workflow runs found"

**Problem:** No runs yet or API error

**Solutions:**

1. Start a workflow first:
   ```bash
   autonomous-dev start --task="Test"
   ```

2. Check token has read access:
   ```bash
   curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/OWNER/REPO/actions/runs
   ```

3. Verify repository configured:
   - Open dashboard
   - Enter owner/repo and token
   - Click "Connect"

---

### Dashboard not auto-refreshing

**Problem:** JavaScript error or disabled

**Solutions:**

1. Check browser console (F12):
   - Look for errors
   - Fix CORS issues (use GitHub Pages or local server)

2. Enable auto-refresh:
   - Click toggle in dashboard
   - Ensure "Auto-refresh: ON"

3. Clear browser cache:
   ```bash
   # Force reload
   Ctrl+Shift+R (Windows/Linux)
   Cmd+Shift+R (macOS)
   ```

---

## Performance Issues

### Slow instance startup

**Problem:** GitHub Actions runner provisioning delay

**Solutions:**

1. Normal startup: 30-60 seconds
2. If >5 minutes, check GitHub status:
   - https://www.githubstatus.com/

3. Use self-hosted runners (instant startup):
   - Settings → Actions → Runners
   - Add self-hosted runner

---

### Tasks taking too long

**Problem:** Complex task or insufficient resources

**Solutions:**

1. Break into smaller tasks:
   ```bash
   # Instead of:
   autonomous-dev start --task="Rewrite entire app"

   # Do:
   autonomous-dev start --task="Refactor auth module"
   autonomous-dev start --task="Refactor API routes"
   ```

2. Increase instances:
   ```bash
   autonomous-dev start --instances=10 --task="Large task"
   ```

3. Monitor progress:
   ```bash
   autonomous-dev status
   autonomous-dev dashboard
   ```

---

## Error Messages

### "Error: Must run from project root directory"

**Problem:** Running from wrong directory

**Solution:**
```bash
cd /path/to/your/project
autonomous-dev init
```

---

### "Error: failed to detect git repository"

**Problem:** Not a git repository or no remote

**Solutions:**

1. Initialize git:
   ```bash
   git init
   git remote add origin https://github.com/user/repo.git
   ```

2. Check remote:
   ```bash
   git remote -v
   ```

---

### "Error: unsupported git URL format"

**Problem:** Non-GitHub remote or SSH URL not recognized

**Solutions:**

1. Use HTTPS URL:
   ```bash
   git remote set-url origin https://github.com/user/repo.git
   ```

2. Or manually set in config:
   ```bash
   autonomous-dev config set github.owner "user"
   autonomous-dev config set github.repo "repo"
   ```

---

## Advanced Debugging

### Enable verbose logging

**Add debug output to workflow:**
```yaml
# .github/workflows/autonomous-dev.yml
env:
  ACTIONS_RUNNER_DEBUG: true
  ACTIONS_STEP_DEBUG: true
```

**CLI debug mode (future):**
```bash
autonomous-dev --debug start --task="..."
```

---

### Inspect Issue comments

**View raw comments:**
```bash
gh api /repos/OWNER/REPO/issues/NUMBER/comments | jq .
```

**Filter instance statuses:**
```bash
gh api /repos/OWNER/REPO/issues/NUMBER/comments | \
  jq '.[] | select(.body | contains("INSTANCE_STATUS"))'
```

---

### Check workflow runs

**List recent runs:**
```bash
gh run list --workflow=autonomous-dev.yml --limit=10
```

**View specific run:**
```bash
gh run view RUN_ID --log
```

**Download logs:**
```bash
gh run download RUN_ID
```

---

## Getting Help

If none of the above solutions work:

1. **Check documentation:**
   - [Quick Start](QUICK_START.md)
   - [Installation](INSTALLATION.md)
   - [P2P Monitoring](P2P_MONITORING.md)

2. **Search existing issues:**
   - https://github.com/autonomous-dev/cli/issues

3. **Create new issue:**
   ```bash
   gh issue create --repo autonomous-dev/cli --title "Bug: ..." --body "..."
   ```

4. **Include in bug report:**
   - OS and version (`uname -a`)
   - CLI version (`autonomous-dev --version`)
   - Error message (full text)
   - Steps to reproduce
   - Workflow logs (if applicable)

---

## Common Misconceptions

### "I need to install Python/Node.js"

**False.** Autonomous Dev is a standalone binary with zero dependencies.

---

### "I need to run a server"

**False.** Everything runs on GitHub infrastructure ($0/month).

---

### "It only works with Python projects"

**False.** Language-agnostic. Works with any language/framework.

---

### "I need Kubernetes"

**False.** Uses GitHub Actions runners (provided by GitHub).

---

## Preventive Measures

**To avoid issues:**

1. ✅ Keep token scopes minimal (`repo` + `workflow` only)
2. ✅ Test with 1-2 instances first
3. ✅ Monitor dashboard during execution
4. ✅ Check GitHub Actions quota monthly
5. ✅ Keep workflow file in version control
6. ✅ Use meaningful task descriptions
7. ✅ Review PRs before merging

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Command not found | `export PATH="/usr/local/bin:$PATH"` |
| Token not set | `export GITHUB_TOKEN="ghp_xxx"` |
| Config missing | `autonomous-dev init` |
| Workflow not found | `git push` (push workflow file) |
| API rate limit | Wait 1 hour or use authenticated token |
| Instances queued | Check Actions quota, reduce concurrency |
| Dashboard not loading | Open `dashboard/index.html` directly |
| Workers not detected | Increase `sleep` time in workflow |

---

**Still stuck?** Open an issue: https://github.com/autonomous-dev/cli/issues/new
