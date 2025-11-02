#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

const binName = os.platform() === 'win32' ? 'autonomous-dev.exe' : 'autonomous-dev';
const binPath = path.join(__dirname, binName);

const child = spawn(binPath, process.argv.slice(2), {
  stdio: 'inherit',
  shell: false
});

child.on('exit', (code) => {
  process.exit(code);
});
