# Pre-Commit Checklist

**MUST DO before every `git commit`**

---

## ✅ Quick Checklist

Copy-paste these commands and run them:

```bash
# 1. Tests pass
go test ./...

# 2. Build succeeds
go build ./cmd/autonomous-dev

# 3. Code is formatted
gofmt -s -w .

# 4. No vet warnings
go vet ./...

# 5. Check git status (no binaries!)
git status
```

**If all pass** → Safe to commit ✅

**If any fail** → Fix before committing ❌

---

## 📋 Detailed Checklist

### Step 1: Tests

```bash
go test ./...
```

**Expected output**:
```
?       github.com/autonomous-dev/cli/cmd/autonomous-dev    [no test files]
?       github.com/autonomous-dev/cli/internal/cli          [no test files]
...
```

**If fails**: Fix the failing tests before committing.

---

### Step 2: Build

```bash
go build ./cmd/autonomous-dev
```

**Expected output**: No errors, binary created

**If fails**:
- Check syntax errors
- Check imports
- Check type mismatches

---

### Step 3: Format

```bash
gofmt -s -w .
git diff
```

**Expected output**: `git diff` shows no changes

**If shows changes**:
```bash
git add .
# This is OK - gofmt made changes
# Include in your commit
```

---

### Step 4: Vet

```bash
go vet ./...
```

**Expected output**: No warnings

**If shows warnings**: Fix the issues before committing

---

### Step 5: Git Status

```bash
git status
```

**Check for**:
- ❌ `autonomous-dev` (binary file)
- ❌ `*.exe`, `*.dll`, `*.dylib` (binaries)
- ❌ `*.test`, `*.out` (test artifacts)

**If found**:
```bash
# These should NOT be committed
git restore autonomous-dev
# Or add to .gitignore if missing
```

---

## 🚀 One-Liner

```bash
go test ./... && go build ./cmd/autonomous-dev && gofmt -s -w . && go vet ./... && git status
```

**If all pass and git status looks clean** → `git commit` ✅

---

## 🛑 Common Mistakes

### Mistake 1: Committing without formatting

```bash
# ❌ BAD
git add .
git commit -m "Add feature"
# CI fails: "Check formatting" step

# ✅ GOOD
gofmt -s -w .
git add .
git commit -m "Add feature"
```

### Mistake 2: Committing broken code

```bash
# ❌ BAD
# Make changes
git commit -m "WIP"  # Tests might fail!

# ✅ GOOD
go test ./...  # Make sure tests pass
git commit -m "Add feature"
```

### Mistake 3: Committing binaries

```bash
# ❌ BAD
go build
git add .  # Adds autonomous-dev binary!
git commit

# ✅ GOOD
go build
git add internal/ cmd/ .github/  # Specific paths
git commit
```

---

## 💡 Pro Tips

### Tip 1: Use an alias

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias gopre="go test ./... && go build ./cmd/autonomous-dev && gofmt -s -w . && go vet ./..."
```

Usage:
```bash
gopre && git status
# If clean → git commit
```

### Tip 2: Git hooks

Save as `.git/hooks/pre-commit`:

```bash
#!/bin/bash
set -e

echo "🔍 Running pre-commit checks..."

gofmt -s -w .
go test ./...
go vet ./...

echo "✅ All checks passed!"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Tip 3: VS Code integration

Install "Go" extension, then add to `.vscode/settings.json`:

```json
{
  "go.formatOnSave": true,
  "go.lintOnSave": "workspace",
  "go.vetOnSave": "workspace"
}
```

---

## 📝 Checklist Template

Print this and check off manually:

```
[ ] go test ./...
[ ] go build ./cmd/autonomous-dev
[ ] gofmt -s -w .
[ ] go vet ./...
[ ] git status (no binaries)
[ ] Commit message follows convention
[ ] Branch name starts with claude/
```

---

**Remember**: 5 minutes of checking saves 30 minutes of fixing CI failures!

