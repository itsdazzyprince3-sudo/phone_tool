#!/usr/bin/env node
"use strict";

const { spawn } = require("node:child_process");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const script = path.join(root, "phone_tool.py");
const python = process.env.PYTHON || (process.platform === "win32" ? "python" : "python3");

const env = { ...process.env };
env.PYTHONPATH = env.PYTHONPATH ? `${root}${path.delimiter}${env.PYTHONPATH}` : root;

const child = spawn(python, [script, ...process.argv.slice(2)], {
  stdio: "inherit",
  cwd: process.cwd(),
  env,
});

child.on("error", (error) => {
  console.error(`numbertrackervy: could not start ${python}: ${error.message}`);
  console.error("Install Python 3.8+ and run: pip install phonenumbers");
  process.exit(127);
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code === null ? 1 : code);
});
