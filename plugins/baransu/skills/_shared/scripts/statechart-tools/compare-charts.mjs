#!/usr/bin/env node
// Compare two statechart runs drawn with the same view, and write one merged chart.
//
//   node compare-charts.mjs A_DIR B_DIR --mode fixed|against [--a WORDS] [--b WORDS] [--title WORDS] --out DIR
//
// A_DIR and B_DIR are --out folders of the statechart program (chart.mmd and report.md).
//   --mode fixed    A is the model today, B the model with the change.
//                   States: fixed (breaks in A, not in B), stillBreaks, newBreak (only in B).
//   --mode against  A models the code, B is the agreed spec.
//                   States and steps only one side has are marked; a state takes the worse mark.
// States match by their label path (groups, regions and the state's own label); steps match
// by from, to and label. Writes DIR/chart.mmd and DIR/report.md. Exit 0 written, 2 failed.
import fs from "node:fs";
import path from "node:path";
import { encode, parseChart, SEP } from "./chart-model.mjs";
const quoted = (s) => `"${encode(s).replaceAll("\"", "#34;")}"`;

const argv = process.argv.slice(2);
const flag = (k) => {
  const i = argv.indexOf(`--${k}`);
  return i >= 0 ? argv[i + 1] : undefined;
};
const dirs = argv.filter((a, i) => !a.startsWith("--") && !argv[i - 1]?.startsWith("--"));
const mode = flag("mode");
const out = flag("out");
if (dirs.length !== 2 || !["fixed", "against"].includes(mode) || !out) {
  console.error("usage: node compare-charts.mjs A_DIR B_DIR --mode fixed|against [--a WORDS] [--b WORDS] --out DIR");
  process.exit(2);
}
const A = flag("a") ?? (mode === "fixed" ? "修正前" : "程式");
const B = flag("b") ?? (mode === "fixed" ? "修正後" : "spec");

function readRun(dir) {
  const mmd = path.join(dir, "chart.mmd");
  if (!fs.existsSync(mmd)) {
    console.error(`${dir} has no chart.mmd (the model passed the chart budget); make the model smaller.`);
    process.exit(2);
  }
  const report = path.join(dir, "report.md");
  return { chart: parseChart(fs.readFileSync(mmd, "utf8")), rules: parseReport(fs.existsSync(report) ? fs.readFileSync(report, "utf8") : "") };
}

function parseReport(text) {
  const broken = new Set([...text.matchAll(/^## (\S+) breaks$/gm)].map((m) => m[1]));
  const list = (head) => {
    const m = text.match(new RegExp(`^## ${head}\\n([^\\n#]+)`, "m"));
    return new Set(m ? m[1].split(",").map((s) => s.trim()).filter(Boolean) : []);
  };
  return { broken, hold: list("Rules that hold"), unchecked: list("Rules not checked") };
}

const a = readRun(dirs[0]);
const b = readRun(dirs[1]);
const warnings = [];
if (a.chart.title !== b.chart.title) warnings.push(`the two charts have different titles (${a.chart.title} / ${b.chart.title}); check that both used the same view`);

// --- merge ---
const bad = (s) => s && (s.marks.has("breaks") || s.marks.has("mayBreak"));
const worse = (x, y) => (x?.marks.has("breaks") || y?.marks.has("breaks") ? "breaks" : bad(x) || bad(y) ? "mayBreak" : null);
const keys = [...a.chart.order, ...b.chart.order.filter((k) => !a.chart.states.has(k))];
const marks = new Map();
const counts = {};
const bump = (k) => (counts[k] = (counts[k] ?? 0) + 1);
for (const k of keys) {
  const sa = a.chart.states.get(k), sb = b.chart.states.get(k);
  const m = new Set();
  if (!sb) m.add("onlyA");
  if (!sa) m.add("onlyB");
  if (mode === "fixed") {
    if (bad(sa) && !bad(sb)) m.add("fixed");
    else if (bad(sa) && bad(sb)) m.add("stillBreaks");
    else if (!bad(sa) && bad(sb)) m.add("newBreak");
    if (sb?.marks.has("bugPath")) m.add("bugPath");
    if (sb?.marks.has("repeats")) m.add("repeats");
  } else {
    const w = worse(sa, sb);
    if (w) m.add(w);
    if (sa?.marks.has("bugPath") || sb?.marks.has("bugPath")) m.add("bugPath");
    if (sa?.marks.has("repeats") || sb?.marks.has("repeats")) m.add("repeats");
  }
  for (const x of m) bump(x);
  marks.set(k, { set: m, color: (sb ?? sa).color, path: (sb ?? sa).path, region: (sb ?? sa).region });
}
const ekey = (e) => `${e.from}\u0000${e.to}\u0000${e.label}`;
const ea = new Map(a.chart.steps.map((e) => [ekey(e), e]));
const eb = new Map(b.chart.steps.map((e) => [ekey(e), e]));
const onlyWord = mode === "fixed" ? { A: `${A}才有`, B: `${B}才有` } : { A: `只有${A}有`, B: `只有${B}有` };
const edges = [];
for (const [k, e] of ea) edges.push({ ...e, label: eb.has(k) ? e.label : `${onlyWord.A}：${e.label}`, side: eb.has(k) ? null : "A" });
for (const [k, e] of eb) if (!ea.has(k)) edges.push({ ...e, label: `${onlyWord.B}：${e.label}`, side: "B" });
const startKeys = new Set([...a.chart.starts, ...b.chart.starts]);

// --- write the merged chart ---
const id = new Map(keys.map((k, i) => [k, `s${i}`]));
const regions = [...new Set([...a.chart.regions, ...b.chart.regions])];
const lines = [];
const title = flag("title") ?? (mode === "fixed" ? `${(b.chart.title ?? "")}（${A} 對 ${B}）` : `${(a.chart.title ?? "")}（${A} 對照 ${B}）`);
lines.push("---", `title: ${JSON.stringify(title)}`, "---", "stateDiagram-v2");
if (regions.length) lines.push("  direction LR");
const LEGEND = mode === "fixed"
  ? [["fixed", `已修好：${A}會打破規則，${B}不會`], ["stillBreaks", `還在壞：${A}、${B}都會打破規則`], ["newBreak", `${B}才打破規則`], ["onlyA", `只有${A}有這個狀態`], ["onlyB", `只有${B}有這個狀態`], ["bugPath", `${B}通往出錯的最短路徑`], ["repeats", `${B}會一直重複，終究會發生的規則被打破`]]
  : [["breaks", "會打破規則（兩邊取較嚴重的）"], ["mayBreak", "某些情況會打破規則"], ["onlyA", `只有${A}有這個狀態`], ["onlyB", `只有${B}有這個狀態`], ["bugPath", "通往出錯的最短路徑"], ["repeats", "會一直重複，終究會發生的規則被打破"]];
const used = LEGEND.filter(([c]) => counts[c]);
if (used.length) {
  lines.push('  state "圖例" as legend {');
  used.forEach(([, t], i) => lines.push(`    lg${i}: ${encode(t)}`));
  lines.push("  }");
  used.forEach(([c], i) => lines.push(`  class lg${i} ${c}`));
}
function emitTree(keysHere, depth, indent, out) {
  const heads = new Map();
  for (const k of keysHere) {
    const p = marks.get(k).path;
    const h = p[depth];
    if (!heads.has(h)) heads.set(h, []);
    heads.get(h).push(k);
  }
  let n = 0;
  for (const [h, ks] of heads) {
    const leaf = ks.find((k) => marks.get(k).path.length === depth + 1);
    const inner = ks.filter((k) => marks.get(k).path.length > depth + 1);
    if (inner.length) {
      out.push(`${indent}state ${quoted(h)} as g${depth}_${n++}_${id.get(inner[0])} {`);
      emitTree(inner, depth + 1, indent + "  ", out);
      out.push(`${indent}}`);
    }
    if (leaf) out.push(`${indent}${id.get(leaf)}: ${encode(h)}`);
  }
}
function emitSteps(keysHere, indent, out) {
  const here = new Set(keysHere);
  for (const k of keysHere) if (startKeys.has(k)) out.push(`${indent}[*] --> ${id.get(k)}`);
  for (const e of edges) if (here.has(e.from) && here.has(e.to)) out.push(`${indent}${id.get(e.from)} --> ${id.get(e.to)}: ${encode(e.label)}`);
}
if (regions.length) {
  lines.push('  state "同時" as all {');
  regions.forEach((r, i) => {
    if (i) lines.push("    --");
    const ks = keys.filter((k) => marks.get(k).region === r);
    lines.push(`    state ${quoted(r)} as r${i} {`);
    emitTree(ks, 1, "      ", lines);
    emitSteps(ks, "      ", lines);
    lines.push("    }");
  });
  lines.push("  }");
} else {
  emitTree(keys, 0, "  ", lines);
  emitSteps(keys, "  ", lines);
}
const CLASSDEF = {
  fixed: "fill:#e6f6ec,stroke:#2e9d5b,stroke-width:2.5px,color:#1f7a43",
  stillBreaks: "fill:#ffecee,stroke:#e72e3b,stroke-width:2.5px,color:#cd2834",
  newBreak: "fill:#f3e8ff,stroke:#8a3fd1,stroke-width:2.5px,color:#6f2db0",
  breaks: "fill:#ffecee,stroke:#e72e3b,stroke-width:2.5px,color:#cd2834",
  mayBreak: "fill:#fff3e6,stroke:#e8730c,stroke-width:2.5px,color:#b85a06",
  onlyA: "stroke-dasharray:6 4,stroke:#808080,stroke-width:2px",
  onlyB: "stroke-dasharray:2 3,stroke:#2e7d4f,stroke-width:2px",
  bugPath: "stroke:#1680f3,stroke-width:2.5px",
  repeats: "stroke:#9b35d6,stroke-width:2.5px,stroke-dasharray:6 3",
};
// Border-only marks first, fill marks last, so a red, green or purple state keeps its border.
for (const c of ["onlyA", "onlyB", "bugPath", "repeats", "mayBreak", "breaks", "stillBreaks", "newBreak", "fixed"])
  if (counts[c] || used.some(([u]) => u === c)) lines.push(`  classDef ${c} ${CLASSDEF[c]}`);
for (const k of keys) {
  const { set, color } = marks.get(k);
  if (color) lines.push(`  class ${id.get(k)} ${color}`);
  for (const c of set) lines.push(`  class ${id.get(k)} ${c}`);
}

// --- report ---
const rules = [...new Set([...a.rules.broken, ...a.rules.hold, ...a.rules.unchecked, ...b.rules.broken, ...b.rules.hold, ...b.rules.unchecked])].sort();
const state = (r, x) => (x.broken.has(r) ? "被打破" : x.hold.has(r) ? "守住" : x.unchecked.has(r) ? "沒檢查完" : "沒有這條");
const change = (r) => {
  const [sa, sb] = [state(r, a.rules), state(r, b.rules)];
  if (mode === "against") return sa === sb ? "一樣" : "不一樣";
  if (sa === "被打破" && sb === "守住") return "修好";
  if (sa === "被打破" && sb === "被打破") return "還在壞";
  if (sa !== "被打破" && sb === "被打破") return `${B}才壞`;
  return sa === sb ? "一樣" : "不一樣";
};
const rep = [`# ${title}`, "", `| 規則 | ${A} | ${B} | 變化 |`, "|---|---|---|---|"];
for (const r of rules) rep.push(`| ${r} | ${state(r, a.rules)} | ${state(r, b.rules)} | ${change(r)} |`);
rep.push("", "## 狀態", "");
const sayCount = (c, words) => counts[c] && rep.push(`- ${words}：${counts[c]}`);
if (mode === "fixed") {
  sayCount("fixed", "已修好");
  sayCount("stillBreaks", "還在壞");
  sayCount("newBreak", `${B}才打破規則`);
}
sayCount("onlyA", `只有${A}有`);
sayCount("onlyB", `只有${B}有`);
if (!["fixed", "stillBreaks", "newBreak", "onlyA", "onlyB"].some((c) => counts[c])) rep.push("無：兩邊的狀態與標記相同。");
const sideA = edges.filter((e) => e.side === "A"), sideB = edges.filter((e) => e.side === "B");
rep.push("", "## 只有一邊有的步驟", "");
if (!sideA.length && !sideB.length) rep.push("無：兩邊的步驟完全相同。");
for (const e of [...sideA, ...sideB]) rep.push(`- ${e.label}：${marks.get(e.from).path.join(SEP)} → ${marks.get(e.to).path.join(SEP)}`);
if (warnings.length) rep.push("", "## 注意", "", ...warnings.map((w) => `- ${w}`));

fs.mkdirSync(out, { recursive: true });
if (fs.readdirSync(out).length) {
  console.error(`${out} is not empty; pass --out with a new folder.`);
  process.exit(2);
}
fs.writeFileSync(path.join(out, "chart.mmd"), lines.join("\n") + "\n");
fs.writeFileSync(path.join(out, "report.md"), rep.join("\n") + "\n");
console.log(rep.join("\n"));
console.log(`\nWrote ${out}`);
