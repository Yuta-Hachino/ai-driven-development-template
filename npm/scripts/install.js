#!/usr/bin/env node

const { execSync } = require('child_process');
const os = require('os');
const fs = require('fs');
const path = require('path');
const https = require('https');

// Read version from package.json
const packageJson = require('../package.json');
const VERSION = packageJson.version;
const REPO = 'Yuta-Hachino/ai-driven-development-template';

function getPlatformInfo() {
  const platform = os.platform();
  const arch = os.arch();

  let osName, archName;

  // Map platform (match GoReleaser naming: Darwin, Linux, Windows)
  if (platform === 'darwin') {
    osName = 'Darwin';
  } else if (platform === 'linux') {
    osName = 'Linux';
  } else if (platform === 'win32') {
    osName = 'Windows';
  } else {
    throw new Error(`Unsupported platform: ${platform}`);
  }

  // Map architecture
  if (arch === 'x64') {
    archName = 'amd64';
  } else if (arch === 'arm64') {
    archName = 'arm64';
  } else {
    throw new Error(`Unsupported architecture: ${arch}`);
  }

  return { osName, archName };
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301) {
        // Follow redirect
        return download(response.headers.location, dest).then(resolve).catch(reject);
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

async function install() {
  try {
    const { osName, archName } = getPlatformInfo();

    const ext = osName === 'Windows' ? 'zip' : 'tar.gz';
    const filename = `autonomous-dev_${VERSION}_${osName}_${archName}.${ext}`;
    const downloadUrl = `https://github.com/${REPO}/releases/download/v${VERSION}/${filename}`;

    console.log(`Downloading autonomous-dev binary for ${osName}/${archName}...`);
    console.log(`URL: ${downloadUrl}`);

    const tmpFile = path.join(os.tmpdir(), filename);
    await download(downloadUrl, tmpFile);

    console.log('Extracting binary...');
    const binDir = path.join(__dirname, '..', 'bin');

    if (!fs.existsSync(binDir)) {
      fs.mkdirSync(binDir, { recursive: true });
    }

    if (osName === 'windows') {
      execSync(`unzip -q "${tmpFile}" -d "${binDir}"`);
    } else {
      execSync(`tar -xzf "${tmpFile}" -C "${binDir}"`);
    }

    // Make executable
    const binaryPath = path.join(binDir, osName === 'Windows' ? 'autonomous-dev.exe' : 'autonomous-dev');
    if (osName !== 'Windows') {
      fs.chmodSync(binaryPath, 0o755);
    }

    // Clean up
    fs.unlinkSync(tmpFile);

    console.log('✓ autonomous-dev installed successfully!');
  } catch (error) {
    console.error('Failed to install autonomous-dev:', error.message);
    console.error('\nYou can download manually from:');
    console.error(`https://github.com/${REPO}/releases`);
    process.exit(1);
  }
}

install();
