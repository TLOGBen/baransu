#!/usr/bin/env -S npx tsx
import { spawnSync } from "node:child_process";

// ── --format argument parsing ────────────────────────────────────────────────
const VALID_FORMATS = ["html", "pdf", "ppt", "all"] as const;
type Format = (typeof VALID_FORMATS)[number];

function parseFormat(): Format {
  const idx = process.argv.indexOf("--format");
  if (idx === -1) return "html";
  const value = process.argv[idx + 1];
  if (!value || !VALID_FORMATS.includes(value as Format)) {
    console.error(
      `❌ 不合法的 --format 值：「${value ?? ""}」。有效值為：${VALID_FORMATS.join(", ")}`
    );
    process.exit(1);
  }
  return value as Format;
}

const format = parseFormat();

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

// ── WeasyPrint (pdf | all) ───────────────────────────────────────────────────
if (format === "pdf" || format === "all") {
  const weasyOk = check("python3", ["-m", "weasyprint", "--version"]);
  if (weasyOk) {
    console.log("weasyprint OK");
  } else {
    console.error("weasyprint not found, installing...");
    const r = spawnSync("pip", ["install", "weasyprint"], { stdio: "inherit" });
    if (r.status !== 0 || !check("python3", ["-m", "weasyprint", "--version"])) {
      console.error(
        "❌ WeasyPrint 安裝失敗。請手動執行：pip install weasyprint"
      );
      process.exit(1);
    }
    console.log("weasyprint OK");
  }
}

// ── playwright + pptxgenjs (ppt | all) ──────────────────────────────────────
if (format === "ppt" || format === "all") {
  // playwright
  const playwrightOk = check("npx", ["playwright", "--version"]);
  if (playwrightOk) {
    console.log("playwright OK");
  } else {
    console.error("playwright not found, installing...");
    const r = spawnSync(
      "npx",
      ["playwright", "install", "--with-deps"],
      { stdio: "inherit" }
    );
    if (r.status !== 0 || !check("npx", ["playwright", "--version"])) {
      console.error(
        "❌ playwright 安裝失敗。請手動執行：npx playwright install --with-deps"
      );
      process.exit(1);
    }
    console.log("playwright OK");
  }

  // pptxgenjs
  const pptxOk = check("node", ["-e", "require('pptxgenjs')"]);
  if (pptxOk) {
    console.log("pptxgenjs OK");
  } else {
    console.error("pptxgenjs not found, installing...");
    const r = spawnSync("npm", ["install", "-g", "pptxgenjs"], {
      stdio: "inherit",
    });
    if (r.status !== 0 || !check("node", ["-e", "require('pptxgenjs')"])) {
      console.error(
        "❌ pptxgenjs 安裝失敗。請手動執行：npm install -g pptxgenjs"
      );
      process.exit(1);
    }
    console.log("pptxgenjs OK");
  }
}

// ── success ──────────────────────────────────────────────────────────────────
console.log(`✅ 依賴已就緒（format: ${format}）`);
