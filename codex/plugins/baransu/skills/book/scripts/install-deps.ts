#!/usr/bin/env -S npx tsx
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));

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

// ── Playwright (headless Chromium for Stage 4 visual verification) ──────────
// Why Playwright (not browser-use): browser-use's headless Chromium silently
// fails on file:// URLs (DOM stays empty even when readyState=complete).
// Playwright handles file:// correctly and is the project-standard E2E driver.
const playwrightOk = check("python3", ["-c", "import playwright"]);
if (playwrightOk) {
  console.log("playwright OK");
} else {
  console.error("playwright not found, installing...");
  install("playwright (python). Run manually: pip install playwright && playwright install chromium", [
    ["python3", ["-m", "pip", "install", "playwright"]],
    ["pip3", ["install", "playwright"]],
  ]);
  if (!check("python3", ["-c", "import playwright"])) {
    console.error("Error: playwright still not importable after install.");
    process.exit(1);
  }
  // Ensure Chromium browser binary is present (idempotent: skips when already installed)
  install("playwright chromium browser. Run manually: playwright install chromium", [
    ["python3", ["-m", "playwright", "install", "chromium"]],
    ["playwright", ["install", "chromium"]],
  ]);
  console.log("playwright OK");
}

// ── cheerio (always required by validate-output.ts) ─────────────────────────
// Installed locally next to the script so `npx tsx validate-output.ts` resolves
// it regardless of the caller's cwd. Match: user reports first GATE run fails
// without this dep.
const cheerioOk =
  spawnSync("node", ["-e", "require('cheerio')"], {
    cwd: SCRIPT_DIR,
    encoding: "utf8",
  }).status === 0;
if (cheerioOk) {
  console.log("cheerio OK");
} else {
  console.error("cheerio not found, installing...");
  const r = spawnSync("npm", ["install", "cheerio"], {
    cwd: SCRIPT_DIR,
    stdio: "inherit",
  });
  const stillMissing =
    spawnSync("node", ["-e", "require('cheerio')"], {
      cwd: SCRIPT_DIR,
      encoding: "utf8",
    }).status !== 0;
  if (r.status !== 0 || stillMissing) {
    console.error(
      `❌ cheerio 安裝失敗。請手動執行：cd ${SCRIPT_DIR} && npm install cheerio`
    );
    process.exit(1);
  }
  console.log("cheerio OK");
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
