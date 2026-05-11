#!/usr/bin/env -S npx tsx
import { spawnSync } from "node:child_process";

function check(cmd: string, args: string[]): boolean {
  return spawnSync(cmd, args, { encoding: "utf8" }).status === 0;
}

function install(label: string, attempts: [string, string[]][]): void {
  for (const [cmd, args] of attempts) {
    const r = spawnSync(cmd, args, { stdio: "inherit" });
    if (r.status === 0) return;
    console.error(`${[cmd, ...args].join(" ")} failed, trying next...`);
  }
  console.error(`Error: failed to install ${label}.`);
  process.exit(1);
}

// ── markitdown ──────────────────────────────────────────────────────────────
const markitdownOk = check("python3", ["-m", "markitdown", "--version"]);
if (markitdownOk) {
  console.log("markitdown OK");
} else {
  console.error("markitdown not found, installing...");
  install("markitdown. Run manually: python3 -m pip install markitdown", [
    ["python3", ["-m", "pip", "install", "markitdown"]],
    ["pip3", ["install", "markitdown"]],
  ]);
  if (!check("python3", ["-m", "markitdown", "--version"])) {
    console.error("Error: markitdown still not available after install.");
    process.exit(1);
  }
  console.log("markitdown OK");
}

// ── browser-use ─────────────────────────────────────────────────────────────
const browserUseOk = check("browser-use", ["--version"]);
if (browserUseOk) {
  console.log("browser-use OK");
} else {
  console.error("browser-use not found, installing...");
  install("browser-use. Run manually: pip install browser-use", [
    ["python3", ["-m", "pip", "install", "browser-use"]],
    ["pip3", ["install", "browser-use"]],
    ["pipx", ["install", "browser-use"]],
  ]);
  if (!check("browser-use", ["--version"])) {
    console.error("Error: browser-use still not available after install.");
    process.exit(1);
  }
  console.log("browser-use OK");
}
