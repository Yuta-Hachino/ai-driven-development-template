# Installation Guide

Complete installation instructions for all platforms.

---

## System Requirements

**Minimum:**
- Git 2.20+
- Internet connection
- GitHub account

**NO requirements for:**
- ❌ Python
- ❌ Node.js
- ❌ Docker
- ❌ Kubernetes
- ❌ Database

---

## Installation Methods

### 1. Direct Binary Download (Recommended)

**Latest version:** v0.2.1

Pre-built binaries are available for all major platforms.

#### macOS (Apple Silicon - M1/M2/M3)

```bash
curl -L https://github.com/Yuta-Hachino/ai-driven-development-template/releases/download/v0.2.1/autonomous-dev_0.2.1_Darwin_arm64.tar.gz -o autonomous-dev.tar.gz
tar -xzf autonomous-dev.tar.gz
sudo mv autonomous-dev /usr/local/bin/
sudo chmod +x /usr/local/bin/autonomous-dev
rm autonomous-dev.tar.gz
autonomous-dev --version
```

#### macOS (Intel)

```bash
curl -L https://github.com/Yuta-Hachino/ai-driven-development-template/releases/download/v0.2.1/autonomous-dev_0.2.1_Darwin_amd64.tar.gz -o autonomous-dev.tar.gz
tar -xzf autonomous-dev.tar.gz
sudo mv autonomous-dev /usr/local/bin/
sudo chmod +x /usr/local/bin/autonomous-dev
rm autonomous-dev.tar.gz
autonomous-dev --version
```

#### Linux (Ubuntu/Debian/WSL)

**Via package manager (Debian/Ubuntu):**
```bash
wget https://github.com/Yuta-Hachino/ai-driven-development-template/releases/download/v0.2.1/autonomous-dev_0.2.1_amd64.deb
sudo dpkg -i autonomous-dev_0.2.1_amd64.deb
autonomous-dev --version
```

**Via tar.gz:**
```bash
curl -L https://github.com/Yuta-Hachino/ai-driven-development-template/releases/download/v0.2.1/autonomous-dev_0.2.1_Linux_amd64.tar.gz -o autonomous-dev.tar.gz
tar -xzf autonomous-dev.tar.gz
sudo mv autonomous-dev /usr/local/bin/
sudo chmod +x /usr/local/bin/autonomous-dev
rm autonomous-dev.tar.gz
autonomous-dev --version
```

#### Linux (Red Hat/Fedora/CentOS)

```bash
wget https://github.com/Yuta-Hachino/ai-driven-development-template/releases/download/v0.2.1/autonomous-dev_0.2.1_amd64.rpm
sudo rpm -i autonomous-dev_0.2.1_amd64.rpm
autonomous-dev --version
```

#### Windows

```powershell
# PowerShell
Invoke-WebRequest -Uri "https://github.com/Yuta-Hachino/ai-driven-development-template/releases/download/v0.2.1/autonomous-dev_0.2.1_Windows_amd64.zip" -OutFile "autonomous-dev.zip"
Expand-Archive -Path "autonomous-dev.zip" -DestinationPath "C:\Program Files\autonomous-dev"
# Add to PATH manually or use via full path
```

**Note:** Windows support is limited. WSL is recommended for best experience.

---

### 2. Build from Source

**Prerequisites:**
- Go 1.21+

**Clone and build:**
```bash
git clone https://github.com/Yuta-Hachino/ai-driven-development-template.git
cd ai-driven-development-template
go mod download
go build -o autonomous-dev ./cmd/autonomous-dev
sudo mv autonomous-dev /usr/local/bin/
autonomous-dev --version
```

---

## Post-Installation Setup

### 1. Create GitHub Token

**Required scopes:**
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows

**Steps:**

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name: `autonomous-dev`
4. Select scopes: `repo`, `workflow`
5. Click **"Generate token"**
6. Copy token (starts with `ghp_`)

### 2. Set Environment Variable

**Temporary (current session):**
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Permanent (add to shell config):**

**Bash:**
```bash
echo 'export GITHUB_TOKEN="ghp_xxx..."' >> ~/.bashrc
source ~/.bashrc
```

**Zsh:**
```bash
echo 'export GITHUB_TOKEN="ghp_xxx..."' >> ~/.zshrc
source ~/.zshrc
```

**Fish:**
```bash
echo 'set -gx GITHUB_TOKEN "ghp_xxx..."' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_xxx...', 'User')
```

### 3. Verify Installation

```bash
# Check version
autonomous-dev --version

# Check token is set
autonomous-dev config get github.token
```

---

## Platform-Specific Notes

### macOS

**Gatekeeper Warning:**

If you see *"autonomous-dev cannot be opened because the developer cannot be verified"*:

```bash
xattr -d com.apple.quarantine /usr/local/bin/autonomous-dev
```

Or go to **System Preferences** → **Security & Privacy** → click **"Allow Anyway"**.

---

### Linux

**Permissions:**

Ensure `/usr/local/bin` is writable or use `sudo`:
```bash
sudo mv autonomous-dev /usr/local/bin/
sudo chmod +x /usr/local/bin/autonomous-dev
```

**Add to PATH:**

If `/usr/local/bin` not in PATH:
```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### WSL (Windows Subsystem for Linux)

**Recommended approach:**

1. Use Linux installation method (same as Ubuntu)
2. Binary works natively in WSL
3. No Windows-specific configuration needed

**Access from Windows:**

```bash
# In WSL
autonomous-dev --version

# From Windows PowerShell
wsl autonomous-dev --version
```

---

### Windows (Native)

**PATH Setup:**

1. Extract `autonomous-dev.exe` to `C:\Program Files\autonomous-dev\`
2. Add to PATH:
   - Right-click **This PC** → **Properties**
   - **Advanced system settings** → **Environment Variables**
   - Under **System variables**, edit **Path**
   - Add `C:\Program Files\autonomous-dev`
   - Click **OK**

**Git Bash:**

Works best in Git Bash or PowerShell (not cmd.exe):
```bash
autonomous-dev --version
```

**Note:** Windows support is limited. WSL recommended.

---

## Docker (Optional)

**Use pre-built image:**
```bash
docker run --rm -it \
  -v $(pwd):/workspace \
  -e GITHUB_TOKEN="ghp_xxx..." \
  autonomous-dev/cli:latest \
  autonomous-dev --version
```

**Build your own:**
```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /build
COPY . .
RUN go build -o autonomous-dev ./cmd/autonomous-dev

FROM alpine:latest
RUN apk add --no-cache git
COPY --from=builder /build/autonomous-dev /usr/local/bin/
ENTRYPOINT ["autonomous-dev"]
```

```bash
docker build -t autonomous-dev .
docker run --rm autonomous-dev --version
```

---

## Dev Container (VS Code)

**Use the provided Dev Container:**

1. Open project in VS Code
2. Install **"Dev Containers"** extension
3. Press `F1` → **"Dev Containers: Reopen in Container"**
4. Wait for container to build
5. `autonomous-dev --version` works inside container

**Configuration:**

`.devcontainer/devcontainer.json` (already included):
```json
{
  "name": "Autonomous Dev CLI (Go)",
  "image": "mcr.microsoft.com/devcontainers/go:1-1.21-bullseye",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "make deps"
}
```

---

## Troubleshooting Installation

### Issue: "command not found: autonomous-dev"

**Solution:**

1. Check installation location:
   ```bash
   which autonomous-dev
   ```

2. If empty, binary not in PATH. Add manually:
   ```bash
   export PATH="/usr/local/bin:$PATH"
   ```

3. Or reinstall with correct path.

---

### Issue: "permission denied"

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

---

### Issue: Windows binary won't run

**Solution:**

1. Disable Windows Defender (if blocking):
   - Windows Security → Virus & threat protection
   - Manage settings → Add exclusion
   - Add `autonomous-dev.exe`

2. Use WSL instead (recommended):
   ```bash
   wsl --install
   # Then follow Linux installation
   ```

---

## Updating

Download the latest release and replace the binary:

```bash
# Check current version
autonomous-dev --version

# Backup current version
sudo mv /usr/local/bin/autonomous-dev /usr/local/bin/autonomous-dev.bak

# Download and install new version (example: v0.3.0)
curl -L https://github.com/Yuta-Hachino/ai-driven-development-template/releases/download/v0.3.0/autonomous-dev_0.3.0_Linux_amd64.tar.gz | tar xz
sudo mv autonomous-dev /usr/local/bin/

# Verify new version
autonomous-dev --version
```

**Check for updates:**
- Visit: https://github.com/Yuta-Hachino/ai-driven-development-template/releases

---

## Uninstalling

Remove the binary and optional configuration:

```bash
# Remove binary
sudo rm /usr/local/bin/autonomous-dev

# Optional: remove configuration
rm -rf ~/.autonomous-dev

# If installed via package manager
sudo dpkg -r autonomous-dev  # Debian/Ubuntu
sudo rpm -e autonomous-dev   # Red Hat/Fedora/CentOS
```

---

## Next Steps

After installation:

1. ✅ [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
2. ✅ [Configuration](../README.md#configuration) - Customize settings
3. ✅ [Dashboard Guide](DASHBOARD_GUIDE.md) - Monitor your instances
4. ✅ [Troubleshooting](TROUBLESHOOTING.md) - Fix common issues

---

## Support

- 📖 [Documentation](../README.md)
- 🐛 [Issues](https://github.com/Yuta-Hachino/ai-driven-development-template/issues)
- 🚀 [Releases](https://github.com/Yuta-Hachino/ai-driven-development-template/releases)
- 📦 [Latest: v0.2.1](https://github.com/Yuta-Hachino/ai-driven-development-template/releases/tag/v0.2.1)
