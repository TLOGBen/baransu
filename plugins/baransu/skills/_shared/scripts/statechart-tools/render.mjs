#!/usr/bin/env node
// Render a statechart .mmd to SVG with Pele, with colours for every mark the
// statechart program and compare-charts.mjs write. Light and dark follow the viewer.
//
//   node render.mjs CHART.mmd [--out CHART.svg]
//
// Pele is installed once outside the repo: npm install pele@1.9.0 in PELE_DIR
// (default ~/.local/share/pele). Exit 0 written, 2 failed.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const chart = args.find((a, i) => !a.startsWith("--") && args[i - 1] !== "--out");
const outAt = args.indexOf("--out");
if (!chart) {
  console.error("usage: node render.mjs CHART.mmd [--out CHART.svg]");
  process.exit(2);
}
const out = outAt >= 0 ? args[outAt + 1] : chart.replace(/\.mmd$/, "") + ".svg";
const peleDir = process.env.PELE_DIR || path.join(os.homedir(), ".local", "share", "pele");
const entry = path.join(peleDir, "node_modules", "pele", "dist", "pele.js");
if (!fs.existsSync(entry)) {
  console.error(`Pele is not installed: run \`npm install pele@1.9.0\` in ${peleDir}, or set PELE_DIR.`);
  process.exit(2);
}
const { render, PeleError } = await import(pathToFileURL(entry).href);

const FONT = "'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', system-ui, sans-serif";

// Marks: breaks / mayBreak / bugPath / repeats from the statechart program;
// fixed / stillBreaks / newBreak / onlyA / onlyB from compare-charts.mjs.
// A classDef in the .mmd becomes an inline style, so mark rules use !important.
// Border marks come first and fill marks last, so a breaking state keeps its red.
const CSS = `
.pele { --pele-bg:#ffffff; --pele-fg:#1c1c1c; --pele-muted:#656565; --pele-line:#808080;
  --pele-surface:#fcfcfc; --pele-surface-alt:#f1f1f1; --pele-border:#c9c9c9; --pele-font:${FONT}; }
.pele .blue rect{fill:#c3e0ff}.pele .orange rect{fill:#f0d3bf}.pele .purple rect{fill:#e3d5ff}
.pele .yellow rect{fill:#f0dcbf}.pele .teal rect{fill:#bfe3df}.pele .tan rect{fill:#e5d9ce}.pele .pink rect{fill:#ffcbe6}
.pele .bugPath rect{stroke:#1680f3!important;stroke-width:2.5px!important}
.pele .repeats rect{stroke:#9b35d6!important;stroke-width:2.5px!important;stroke-dasharray:6 3}
.pele .onlyA rect{stroke-dasharray:6 4!important;stroke:#808080!important;stroke-width:2px!important}
.pele .onlyB rect{stroke-dasharray:2 3!important;stroke:#2e7d4f!important;stroke-width:2px!important}
.pele .mayBreak rect{fill:#fff3e6!important;stroke:#e8730c!important;stroke-width:2.5px!important}
.pele .mayBreak text{fill:#b85a06!important}
.pele .breaks rect,.pele .stillBreaks rect{fill:#ffecee!important;stroke:#e72e3b!important;stroke-width:2.5px!important}
.pele .breaks text,.pele .stillBreaks text{fill:#cd2834!important}
.pele .newBreak rect{fill:#f3e8ff!important;stroke:#8a3fd1!important;stroke-width:2.5px!important}
.pele .newBreak text{fill:#6f2db0!important}
.pele .fixed rect{fill:#e6f6ec!important;stroke:#2e9d5b!important;stroke-width:2.5px!important}
.pele .fixed text{fill:#1f7a43!important}
@media (prefers-color-scheme: dark){
.pele{--pele-bg:#1f1f1f;--pele-fg:#f5f5f5;--pele-muted:#acacac;--pele-line:#939393;
  --pele-surface:#121212;--pele-surface-alt:#2c2c2c;--pele-border:#4e4e4e}
.pele .blue rect{fill:#1b3857}.pele .orange rect{fill:#573117}.pele .purple rect{fill:#3c2e57}
.pele .yellow rect{fill:#573d17}.pele .teal rect{fill:#174641}.pele .tan rect{fill:#3d3127}.pele .pink rect{fill:#57233e}
.pele .bugPath rect{stroke:#116dd2!important}.pele .repeats rect{stroke:#9a3fcf!important}
.pele .onlyB rect{stroke:#4fbf7e!important}
.pele .mayBreak rect{fill:#2e2619!important;stroke:#d0700f!important}.pele .mayBreak text{fill:#ffa257!important}
.pele .breaks rect,.pele .stillBreaks rect{fill:#2e2021!important;stroke:#cf2b35!important}
.pele .breaks text,.pele .stillBreaks text{fill:#ff6463!important}
.pele .newBreak rect{fill:#2a2136!important;stroke:#a66be6!important}.pele .newBreak text{fill:#c9a2f5!important}
.pele .fixed rect{fill:#18301f!important;stroke:#3fbf72!important}.pele .fixed text{fill:#7ee0a3!important}
}`;

let result;
try {
  result = render(fs.readFileSync(chart, "utf8"), {
    fontFamily: FONT,
    limit: 1_000_000,
    outputLimit: 8_000_000,
    maxEdges: 10_000,
  });
} catch (error) {
  if (error instanceof PeleError) {
    console.error(`Pele could not render ${chart} (${error.code}): ${error.message}`);
    process.exit(2);
  }
  throw error;
}
const svg = result.svg.replace(/^(<svg\b[^>]*>)/, `$1<style>${CSS}</style>`);
fs.writeFileSync(out, svg);
console.log(`wrote ${out} (${Math.round(result.width)}×${Math.round(result.height)})`);
