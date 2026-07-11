#!/usr/bin/env -S npx tsx
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
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

// ── --dry-run: probe-only mode (SKILL.md Stage 0 §6 step 1 contract) ─────────
// "list, no install": probes run, installers do NOT. The probe→confirm→install
// gate depends on this — a --dry-run invocation must never mutate the
// environment (no pip/npm install, no browser download). Missing deps are
// collected into `missing` and listed at the end (exit 0 either way).
const dryRun = process.argv.includes("--dry-run");
const missing: string[] = [];

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
} else if (dryRun) {
  console.log("markitdown MISSING");
  missing.push("markitdown");
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
} else if (dryRun) {
  console.log("playwright (python) MISSING");
  missing.push("playwright (python) + chromium");
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
} else if (dryRun) {
  console.log("cheerio MISSING");
  missing.push("cheerio");
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
  } else if (dryRun) {
    console.log("weasyprint MISSING");
    missing.push("weasyprint");
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

// A passing `npx playwright --version` only proves the CLI wrapper resolves —
// the chromium BINARY download is a separate step, and html2pptx.js fails at
// first launch ("Executable doesn't exist at …/ms-playwright/…") when it is
// absent. `playwright install --dry-run` prints each browser's install
// location WITHOUT mutating anything; require every listed location to exist.
function chromiumBrowsersReady(): boolean {
  const r = spawnSync("npx", ["playwright", "install", "--dry-run", "chromium"], {
    encoding: "utf8",
  });
  if (r.status !== 0) return false;
  const locs = [...`${r.stdout}${r.stderr}`.matchAll(/Install location:\s*(\S+)/gi)].map(
    (m) => m[1]
  );
  return locs.length > 0 && locs.every((p) => existsSync(p));
}

if (format === "ppt" || format === "all") {
  // playwright (node) + chromium browser binary
  if (chromiumBrowsersReady()) {
    console.log("playwright OK");
  } else if (dryRun) {
    console.log("playwright chromium browser MISSING");
    missing.push("playwright chromium browser");
  } else {
    console.error("playwright chromium not found, installing...");
    const r = spawnSync(
      "npx",
      ["playwright", "install", "--with-deps", "chromium"],
      { stdio: "inherit" }
    );
    if (r.status !== 0 || !chromiumBrowsersReady()) {
      console.error(
        "❌ playwright 安裝失敗。請手動執行：npx playwright install --with-deps chromium"
      );
      process.exit(1);
    }
    console.log("playwright OK");
  }

  // pptxgenjs — install AND verify in the SAME resolution context (cwd:
  // SCRIPT_DIR, exactly like cheerio above; html2pptx.js lives in SCRIPT_DIR
  // so its require() resolves from SCRIPT_DIR/node_modules regardless of the
  // caller's cwd). A global `npm install -g` paired with a cwd-relative
  // `node -e require(…)` verification can NEVER pass on a clean machine —
  // global node_modules are not on node's default require path.
  const pptxCheck = () =>
    spawnSync("node", ["-e", "require('pptxgenjs')"], {
      cwd: SCRIPT_DIR,
      encoding: "utf8",
    }).status === 0;
  if (pptxCheck()) {
    console.log("pptxgenjs OK");
  } else if (dryRun) {
    console.log("pptxgenjs MISSING");
    missing.push("pptxgenjs");
  } else {
    console.error("pptxgenjs not found, installing...");
    const r = spawnSync("npm", ["install", "pptxgenjs"], {
      cwd: SCRIPT_DIR,
      stdio: "inherit",
    });
    if (r.status !== 0 || !pptxCheck()) {
      console.error(
        `❌ pptxgenjs 安裝失敗。請手動執行：cd ${SCRIPT_DIR} && npm install pptxgenjs`
      );
      process.exit(1);
    }
    console.log("pptxgenjs OK");
  }
}

// ── success ──────────────────────────────────────────────────────────────────
if (dryRun) {
  if (missing.length === 0) {
    console.log(`DRY-RUN：所有依賴已就緒，無需安裝（format: ${format}）`);
  } else {
    console.log(
      `DRY-RUN（僅列出，未安裝）需新安裝：${missing.join(", ")}（format: ${format}）`
    );
  }
  process.exit(0);
}
console.log(`✅ 依賴已就緒（format: ${format}）`);
