#!/usr/bin/env node
"use strict";

const { spawnSync } = require("node:child_process");

const python = process.env.PYTHON || (process.platform === "win32" ? "python" : "python3");

function hasPhonenumbers() {
  const probe = spawnSync(python, ["-c", "import phonenumbers"], { stdio: "ignore" });
  return probe.status === 0;
}

if (process.env.VIRGOYT_SKIP_PIP === "1" || hasPhonenumbers()) {
  process.exit(0);
}

const attempts = [
  ["-m", "pip", "install", "--user", "--quiet", "phonenumbers>=8.12.0"],
  ["-m", "pip", "install", "--quiet", "phonenumbers>=8.12.0"],
];

for (const args of attempts) {
  const result = spawnSync(python, args, { stdio: "inherit" });
  if (result.status === 0 && hasPhonenumbers()) {
    console.log("numbertrackervy: phonenumbers installed");
    process.exit(0);
  }
}

console.warn(`numbertrackervy: install the Python dependency manually:`);
console.warn(`  ${python} -m pip install "phonenumbers>=8.12.0"`);
process.exit(0);
