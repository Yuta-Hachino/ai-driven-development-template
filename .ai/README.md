# .ai/ Directory

**Purpose**: Guidelines and documentation for AI assistants working on this project

**Target Audience**: Claude Code, GitHub Copilot, and other AI development tools

---

## 📚 Contents

### [DEVELOPMENT_GUIDELINES.md](DEVELOPMENT_GUIDELINES.md)

**Main reference document** - Comprehensive guide covering:

- Project overview and architecture
- Technology stack (Go 1.21+)
- Development workflow
- Common pitfalls and solutions
- CI/CD understanding
- Release process
- Troubleshooting guide

**Read this first** if you're new to the project.

**Size**: ~500 lines, 15-20 minute read

---

### [PRE_COMMIT_CHECKLIST.md](PRE_COMMIT_CHECKLIST.md)

**Quick reference checklist** - Run before every commit:

```bash
go test ./...                    # Tests
go build ./cmd/autonomous-dev    # Build
gofmt -s -w .                   # Format
go vet ./...                    # Lint
git status                      # No binaries
```

**Use this** before every `git commit` to prevent CI failures.

**Size**: ~200 lines, 5 minute read

---

## 🎯 Quick Start for AI Assistants

### First Time Working on This Project?

1. **Read**: [DEVELOPMENT_GUIDELINES.md](DEVELOPMENT_GUIDELINES.md) (Section 1-3)
2. **Bookmark**: [PRE_COMMIT_CHECKLIST.md](PRE_COMMIT_CHECKLIST.md)
3. **Remember**: Branch names must start with `claude/`

### Before Every Commit

1. **Run**: Commands in [PRE_COMMIT_CHECKLIST.md](PRE_COMMIT_CHECKLIST.md)
2. **Verify**: All checks pass
3. **Commit**: With conventional commit format

### When Something Goes Wrong

1. **Check**: [DEVELOPMENT_GUIDELINES.md](DEVELOPMENT_GUIDELINES.md) Section 5 (Common Pitfalls)
2. **Consult**: [DEVELOPMENT_GUIDELINES.md](DEVELOPMENT_GUIDELINES.md) Section 8 (Troubleshooting)
3. **Search**: GitHub Issues for similar problems

---

## 📖 Additional Resources

### Project Documentation

- User docs: [`../docs/`](../docs/)
- Installation: [`../docs/INSTALLATION.md`](../docs/INSTALLATION.md)
- Quick start: [`../docs/QUICK_START.md`](../docs/QUICK_START.md)
- Release workflow: [`../docs/RELEASE_WORKFLOW.md`](../docs/RELEASE_WORKFLOW.md)

### Technical References

- Main README: [`../README.md`](../README.md)
- Go modules: [`../go.mod`](../go.mod)
- CI config: [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml)
- Release config: [`../.github/workflows/release.yml`](../.github/workflows/release.yml)

---

## 🚨 Critical Information

### Things to ALWAYS Remember

1. **Branch naming**: Must start with `claude/` + session ID
2. **Run tests**: `go test ./...` before every commit
3. **Format code**: `gofmt -s -w .` before every commit
4. **No binaries**: Never commit `autonomous-dev` or `*.exe` files
5. **Check CI**: Verify GitHub Actions pass after push

### Things to NEVER Do

1. ❌ Commit without running tests
2. ❌ Push to `main` directly (use PRs)
3. ❌ Modify archived Python code (in `archive/`)
4. ❌ Add Python dependencies (this is a Go project)
5. ❌ Commit binary files

---

## 🔄 Update History

### Version 1.0.0 (2025-11-03)

**Created by**: Claude Code session 011CUgao5VMcJ1Du3197VsFD

**Reason**: Multiple CI failures during initial development:
- Old Python workflows causing failures
- Build errors (type mismatches)
- Formatting errors
- Binary files tracked in git
- Release workflow issues

**Goal**: Prevent these issues from recurring

**Changes**:
- Created DEVELOPMENT_GUIDELINES.md (comprehensive guide)
- Created PRE_COMMIT_CHECKLIST.md (quick reference)
- Created this README.md (overview)

---

## 📝 Maintenance

### When to Update These Guidelines

Update when:
- New common pitfalls are discovered
- Development workflow changes
- New tools or processes are added
- CI/CD configuration changes

### How to Update

1. Edit the relevant file in `.ai/`
2. Update version number and date
3. Add entry to "Update History" section
4. Commit with message: `docs(ai): Update development guidelines`

---

## 💬 Feedback

If you're an AI assistant and find these guidelines:
- **Helpful**: Great! They're working as intended.
- **Missing info**: Note it in commit message when you encounter issues.
- **Incorrect**: This means the project has changed - update the docs!

If you're a human developer:
- **Useful**: Consider creating similar guides for your projects.
- **Need improvements**: PRs welcome! These docs help AI assistants help you.

---

## 🎓 Philosophy

### Why These Guidelines Exist

AI assistants (like Claude Code) are powerful but can make repeated mistakes without memory across sessions. These guidelines serve as:

1. **Institutional memory**: Lessons learned from past issues
2. **Best practices**: Codified development standards
3. **Safety net**: Prevent common mistakes before they reach CI
4. **Efficiency**: Reduce back-and-forth fixing avoidable issues

### Design Principles

1. **Actionable**: Every guideline has concrete steps
2. **Searchable**: Organized by topic and symptom
3. **Examples**: Show both wrong ❌ and correct ✅ approaches
4. **Concise**: Quick to scan, detailed when needed
5. **Maintained**: Updated when project evolves

---

**Remember**: 5 minutes reading these guidelines saves hours of debugging! 📚✨

