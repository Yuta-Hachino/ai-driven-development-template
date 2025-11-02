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

### 1. Homebrew (macOS/Linux) - Recommended

**Install Homebrew first** (if not installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Install Autonomous Dev:**
```bash
brew tap autonomous-dev/tap
brew install autonomous-dev
```

**Verify:**
```bash
autonomous-dev --version
```

**Update:**
```bash
brew upgrade autonomous-dev
```

**Uninstall:**
```bash
brew uninstall autonomous-dev
brew untap autonomous-dev/tap
```

---

### 2. npm (All Platforms)

**Install via npm:**
```bash
npm install -g @autonomous-dev/cli
```

**Verify:**
```bash
autonomous-dev --version
```

**Update:**
```bash
npm update -g @autonomous-dev/cli
```

**Uninstall:**
```bash
npm uninstall -g @autonomous-dev/cli
```

**How it works:**
- Downloads pre-built binary for your platform
- Creates wrapper script in `node_modules/.bin/`
- No Node.js runtime needed after installation

---

### 3. Direct Binary Download

#### macOS (Apple Silicon)

```bash
curl -L https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_arm64.tar.gz -o autonomous-dev.tar.gz
tar -xzf autonomous-dev.tar.gz
sudo mv autonomous-dev /usr/local/bin/
sudo chmod +x /usr/local/bin/autonomous-dev
rm autonomous-dev.tar.gz
```

#### macOS (Intel)

```bash
curl -L https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_darwin_amd64.tar.gz -o autonomous-dev.tar.gz
tar -xzf autonomous-dev.tar.gz
sudo mv autonomous-dev /usr/local/bin/
sudo chmod +x /usr/local/bin/autonomous-dev
rm autonomous-dev.tar.gz
```

#### Linux (Ubuntu/Debian/WSL)

```bash
curl -L https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_linux_amd64.tar.gz -o autonomous-dev.tar.gz
tar -xzf autonomous-dev.tar.gz
sudo mv autonomous-dev /usr/local/bin/
sudo chmod +x /usr/local/bin/autonomous-dev
rm autonomous-dev.tar.gz
```

#### Windows

```powershell
# PowerShell
Invoke-WebRequest -Uri "https://github.com/autonomous-dev/cli/releases/download/v1.0.0/autonomous-dev_1.0.0_windows_amd64.zip" -OutFile "autonomous-dev.zip"
Expand-Archive -Path "autonomous-dev.zip" -DestinationPath "C:\Program Files\autonomous-dev"
# Add to PATH manually
```

---

### 4. Build from Source

**Prerequisites:**
- Go 1.21+
- Make (optional)

**Clone and build:**
```bash
git clone https://github.com/autonomous-dev/cli.git
cd cli
go mod download
go build -o autonomous-dev ./cmd/autonomous-dev
sudo mv autonomous-dev /usr/local/bin/
```

**Or use Make:**
```bash
git clone https://github.com/autonomous-dev/cli.git
cd cli
make build
sudo make install
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

**Homebrew on Apple Silicon:**

Ensure Homebrew is in PATH:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

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

### Issue: Homebrew installation fails

**Solution:**

1. Update Homebrew:
   ```bash
   brew update
   ```

2. Try again:
   ```bash
   brew install autonomous-dev
   ```

3. Check tap:
   ```bash
   brew tap autonomous-dev/tap
   brew install autonomous-dev/tap/autonomous-dev
   ```

---

### Issue: npm installation fails

**Solution:**

1. Clear npm cache:
   ```bash
   npm cache clean --force
   ```

2. Install with sudo (if permissions error):
   ```bash
   sudo npm install -g @autonomous-dev/cli
   ```

3. Or use npx (no global install):
   ```bash
   npx @autonomous-dev/cli --version
   ```

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

### Homebrew

```bash
brew upgrade autonomous-dev
```

### npm

```bash
npm update -g @autonomous-dev/cli
```

### Manual

Download latest release and replace binary:
```bash
# Backup current version
mv /usr/local/bin/autonomous-dev /usr/local/bin/autonomous-dev.bak

# Download and install new version
curl -L https://github.com/autonomous-dev/cli/releases/download/v2.0.0/... | tar xz
sudo mv autonomous-dev /usr/local/bin/

# Verify
autonomous-dev --version
```

---

## Uninstalling

### Homebrew

```bash
brew uninstall autonomous-dev
brew untap autonomous-dev/tap
```

### npm

```bash
npm uninstall -g @autonomous-dev/cli
```

### Manual

```bash
sudo rm /usr/local/bin/autonomous-dev
rm -rf ~/.autonomous-dev  # Optional: remove config
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
- 🐛 [Issues](https://github.com/autonomous-dev/cli/issues)
- 💬 [Discussions](https://github.com/autonomous-dev/cli/discussions)
