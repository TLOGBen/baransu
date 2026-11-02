#!/usr/bin/env node
// Turn a chart the reader agreed to into a TLA+ skeleton, check it, and compare the chart
// the spec draws with the agreed one.
//
//   node chart-to-spec.mjs CHART.mmd --module NAME [--dir DIR] --out RUN_DIR
//
// The chart is a Mermaid stateDiagram-v2 with ASCII state ids and the reader's words as
// labels (`s1: 購物車`, or `state "購物車" as cart`). It is flat, or one top group split
// by `--` into named regions; each region becomes one variable. Each step label is one
// action: it moves every region whose current state has a step with that label, and the
// other regions stay. `%% never NAME: A & B -- sentence` is a rule (A, B are state ids or
// labels, each from a different region); `%% when ID, ID` or `%% when not ID, ID` right
// after a step is its guard on other regions. A state with no step out is an intended end.
//
// Writes NAMERules.tla (the rules), NAME.tla (the model, extending it), NAME.cfg and
// NAME.view.mjs in DIR (default: the chart's folder) unless
// NAME.tla is already there — then it keeps your edited spec and only checks and compares.
// Runs the statechart program into RUN_DIR and prints every difference.
// Exit 0: no rule broke and no difference; 1: a rule broke or a difference; 2: failed.
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { bareLabel, parseChart, SEP } from "./chart-model.mjs";

const argv = process.argv.slice(2);
const flag = (k) => {
  const i = argv.indexOf(`--${k}`);
  return i >= 0 ? argv[i + 1] : undefined;
};
const chartFile = argv.find((a, i) => !a.startsWith("--") && !argv[i - 1]?.startsWith("--"));
const mod = flag("module");
const runDir = flag("out");
if (!chartFile || !/^[A-Za-z][A-Za-z0-9_]*$/.test(mod ?? "") || !runDir) {
  console.error("usage: node chart-to-spec.mjs CHART.mmd --module NAME [--dir DIR] --out RUN_DIR");
  process.exit(2);
}
const dir = flag("dir") ?? path.dirname(chartFile);
const fail = (msg) => {
  console.error(msg);
  process.exit(2);
};

let chart;
try {
  chart = parseChart(fs.readFileSync(chartFile, "utf8"));
} catch (e) {
  fail(`${chartFile}: ${e.message}`);
}

// --- regions and their states ---
const regionNames = chart.regions.length ? chart.regions : [null];
const regionOf = (id) => chart.states.get(chart.idKey(id)).region;
for (const id of chart.ids) {
  const s = chart.states.get(chart.idKey(id));
  const depth = s.path.length - 1 - (s.region ? 1 : 0);
  if (depth > 0) fail(`${chartFile}: state ${id} sits in a group; draw a flat chart or regions only`);
  if (chart.regions.length && !s.region) fail(`${chartFile}: state ${id} is outside every region`);
}
const vars = regionNames.map((name, i) => ({
  name,
  v: name === null ? "st" : `r${i + 1}`,
  ids: chart.ids.filter((id) => regionOf(id) === name),
}));
const varOf = (id) => vars.find((x) => x.ids.includes(id));
for (const x of vars) {
  if (!x.ids.length) fail(`${chartFile}: region ${x.name} has no states`);
  if (!x.ids.some((id) => chart.starts.has(chart.idKey(id)))) fail(`${chartFile}: region ${x.name ?? "(chart)"} has no [*] --> start`);
}
const resolve = (word) => {
  if (chart.caption.has(word)) return word;
  const hits = chart.ids.filter((id) => chart.caption.get(id) === word);
  if (hits.length === 1) return hits[0];
  fail(`${chartFile}: "${word}" names ${hits.length ? "more than one state" : "no state"}; use the state id`);
};
const str = (s) => `"${s}"`;
const inSet = (v, ids) => (ids.length === 1 ? `${v} = ${str(ids[0])}` : `${v} \\in {${ids.map(str).join(", ")}}`);
const byRegion = (ids) => {
  const m = new Map();
  for (const id of ids) {
    const x = varOf(id);
    if (!m.has(x.v)) m.set(x.v, []);
    m.get(x.v).push(id);
  }
  return m;
};

// --- actions ---
const asciiName = (label, n) => {
  const words = label.normalize("NFKD").replace(/[^A-Za-z0-9]+/g, " ").trim().split(" ").filter(Boolean);
  const id = words.map((w) => w[0].toUpperCase() + w.slice(1)).join("");
  return /^[A-Za-z]/.test(id) && words.join(" ").length === label.replace(/\s+/g, " ").trim().length ? id : `Act${n}`;
};
const labels = [];
for (const s of chart.steps) if (s.label && !labels.includes(bareLabel(s.label))) labels.push(bareLabel(s.label));
const taken = new Set(["Init", "Next", "Spec", "TypeOK", "Done", "vars"]);
const actions = [];
labels.forEach((label, i) => {
  let name = asciiName(label, i + 1);
  while (taken.has(name)) name += "X";
  taken.add(name);
  actions.push({ name, label, steps: chart.steps.filter((s) => s.label && bareLabel(s.label) === label) });
});
chart.steps.filter((s) => !s.label).forEach((s, i) => {
  const name = `Step${i + 1}`;
  taken.add(name);
  actions.push({ name, label: null, steps: [s] });
});

const guardOf = (when) => {
  if (!when) return null;
  const parts = [...byRegion(when.ids.map(resolve))].map(([v, ids]) => inSet(v, ids));
  return when.not ? parts.map((p) => `~(${p})`).join(" /\\ ") : parts.join(" /\\ ");
};
function actionText(a) {
  const moves = [];
  for (const x of vars) {
    const mine = a.steps.filter((s) => x.ids.includes(s.fromId));
    if (!mine.length) continue;
    const from = [...new Set(mine.map((s) => s.fromId))];
    const arms = from.map((f) => {
      const targets = mine.filter((s) => s.fromId === f).map((s) => {
        const g = guardOf(s.when);
        return g ? `(IF ${g} THEN {${str(s.toId)}} ELSE {})` : `{${str(s.toId)}}`;
      });
      return `${x.v} = ${str(f)} -> ${targets.join(" \\cup ")}`;
    });
    moves.push({ x, expr: `CASE ${arms.join("\n          [] ")}\n          [] OTHER -> {}` });
  }
  const lets = moves.map((m, i) => `      M${i + 1} == ${m.expr}`).join("\n");
  const enabled = moves.map((_, i) => `M${i + 1} # {}`).join(" \\/ ");
  const assigns = moves.map((m, i) => `       /\\ ${m.x.v}' \\in (IF M${i + 1} = {} THEN {${m.x.v}} ELSE M${i + 1})`);
  const still = vars.filter((x) => !moves.some((m) => m.x === x)).map((x) => x.v);
  return [
    `\\* ${a.label ?? "a step with no label"}`,
    `${a.name} ==`,
    "  LET",
    lets,
    `  IN /\\ (${enabled})`,
    ...assigns,
    ...(still.length ? [`       /\\ UNCHANGED <<${still.join(", ")}>>`] : []),
  ].join("\n");
}

const ends = vars.map((x) => ({ x, ids: x.ids.filter((id) => !chart.steps.some((s) => s.fromId === id)) }));
const hasDone = ends.every((e) => e.ids.length);
const rules = chart.nevers.map((r, i) => {
  const name = /^[A-Za-z][A-Za-z0-9_]*$/.test(r.name) ? r.name : `Rule${i + 1}`;
  const ids = r.parts.map(resolve);
  const groups = byRegion(ids);
  if ([...groups.values()].some((g) => g.length > 1)) fail(`${chartFile}: rule ${r.name} names two states of one region`);
  return { ...r, tla: name, body: [...groups].map(([v, g]) => inSet(v, g)).join(" /\\ ") };
});

const tlaPath = path.join(dir, `${mod}.tla`);
const rulesPath = path.join(dir, `${mod}Rules.tla`);
const cfgPath = path.join(dir, `${mod}.cfg`);
const viewPath = path.join(dir, `${mod}.view.mjs`);
if (fs.existsSync(tlaPath)) {
  console.log(`${tlaPath} exists; keeping it, its rules module, config and view, checking only.`);
} else {
  // The rules live in a module of their own, which the model extends: the judge shares
  // nothing with the behaviour it judges.
  const rulesTla = [
    `---- MODULE ${mod}Rules ----`,
    `\\* Generated by chart-to-spec.mjs from ${path.basename(chartFile)}: the rules the reader agreed to.`,
    `VARIABLES ${vars.map((x) => x.v).join(", ")}`,
    ...vars.map((x) => `\\* ${x.v}: ${x.name ?? "the chart"} — ${x.ids.map((id) => `${id} ${chart.caption.get(id)}`).join("; ")}`),
    `vars == <<${vars.map((x) => x.v).join(", ")}>>`,
    "",
    `TypeOK == ${vars.map((x) => `${x.v} \\in {${x.ids.map(str).join(", ")}}`).join(" /\\ ")}`,
    "",
    ...rules.flatMap((r) => [`\\* ${r.name}: ${r.sentence}`, `${r.tla} == ~(${r.body})`, ""]),
    "====",
    "",
  ].join("\n");
  const tla = [
    `---- MODULE ${mod} ----`,
    `\\* Generated by chart-to-spec.mjs from ${path.basename(chartFile)}. Edit freely: add the real code's`,
    "\\* guards and variables, each condition with the file and line it comes from.",
    `EXTENDS ${mod}Rules`,
    "",
    `Init == ${vars.map((x) => inSet(x.v, x.ids.filter((id) => chart.starts.has(chart.idKey(id))))).join(" /\\ ")}`,
    "",
    ...actions.flatMap((a) => [actionText(a), ""]),
    ...(hasDone ? ["\\* Every region is in an intended end state; the step changes nothing.", `Done == ${ends.map((e) => inSet(e.x.v, e.ids)).join(" /\\ ")} /\\ UNCHANGED vars`, ""] : []),
    `Next == ${[...actions.map((a) => a.name), ...(hasDone ? ["Done"] : [])].join(" \\/ ")}`,
    "",
    "Spec == Init /\\ [][Next]_vars",
    "====",
    "",
  ].join("\n");
  const cfg = ["SPECIFICATION Spec", "INVARIANT TypeOK", ...rules.map((r) => `INVARIANT ${r.tla}`), ""].join("\n");
  const maps = vars.map((x) => `const ${x.v.toUpperCase()} = ${JSON.stringify(Object.fromEntries(x.ids.map((id) => [id, chart.caption.get(id)])))};`);
  const stateFn = chart.regions.length
    ? `export const state = (v) => ({ ${vars.map((x) => `${JSON.stringify(x.name)}: ${x.v.toUpperCase()}[v.${x.v}]`).join(", ")} });`
    : `export const state = (v) => ST[v.st];`;
  const steps = JSON.stringify(Object.fromEntries(actions.filter((a) => a.label).map((a) => [a.name, a.label])));
  const view = [
    `// Generated by chart-to-spec.mjs: the reader's words for ${mod}.tla.`,
    ...maps,
    stateFn,
    `const STEPS = ${steps};`,
    `export const step = (action) => (action === "Done" ? null : STEPS[action] ?? action);`,
    ...(chart.title ? [`export const title = ${JSON.stringify(chart.title)};`] : []),
    "",
  ].join("\n");
  fs.mkdirSync(dir, { recursive: true });
  if (fs.existsSync(rulesPath)) fail(`${rulesPath} exists but ${tlaPath} does not; move it away or restore ${mod}.tla`);
  fs.writeFileSync(rulesPath, rulesTla);
  fs.writeFileSync(tlaPath, tla);
  fs.writeFileSync(cfgPath, cfg);
  fs.writeFileSync(viewPath, view);
  console.log(`wrote ${rulesPath}, ${tlaPath}, ${cfgPath}, ${viewPath}`);
}
for (const r of rules) console.log(`rule ${r.tla}: ${r.sentence}`);

// --- check with the statechart program ---
const here = path.dirname(fileURLToPath(import.meta.url));
const program = path.join(here, "..", "statechart", "statechart.ts");
const run = spawnSync(process.execPath, [program, tlaPath, "--config", cfgPath, "--view", viewPath, "--out", runDir], {
  encoding: "utf8",
  windowsHide: true,
});
process.stdout.write(run.stdout ?? "");
process.stderr.write(run.stderr ?? "");
if (run.status === 2 || run.status === null) fail("the statechart program did not finish; see above.");
const drawn = path.join(runDir, "chart.mmd");
if (!fs.existsSync(drawn)) fail(`${runDir} has no chart.mmd; make the chart smaller to compare it.`);

// --- compare the agreed chart with the chart the spec draws ---
const got = parseChart(fs.readFileSync(drawn, "utf8"));
const keyOf = (s) => s.path.join(SEP);
// Steps match by from, to and label; the condition in brackets at the label's end is
// compared on its own, since in a regions chart it is where a guard shows.
const cond = (label) => (label.match(/\[([^\]]*)\]\s*$/) || [])[1] ?? "";
const stepMap = (steps) => new Map(steps.map((s) => [`${s.from} → ${s.to}: ${bareLabel(s.label)}`, cond(s.label)]));
const want = { states: new Set(chart.order), starts: chart.starts, steps: stepMap(chart.steps.filter((s) => s.from !== s.to && s.label)) };
const have = { states: new Set([...got.states.values()].map(keyOf)), starts: got.starts, steps: stepMap(got.steps) };
const diff = [];
for (const k of want.states) if (!have.states.has(k)) diff.push(`state only on the agreed chart (the spec never reaches it): ${k}`);
for (const k of have.states) if (!want.states.has(k)) diff.push(`state only in the spec: ${k}`);
for (const k of want.starts) if (!have.starts.has(k)) diff.push(`start only on the agreed chart: ${k}`);
for (const k of have.starts) if (!want.starts.has(k)) diff.push(`start only in the spec: ${k}`);
for (const [k, c] of want.steps) {
  if (!have.steps.has(k)) diff.push(`step only on the agreed chart: ${k}`);
  else if (have.steps.get(k) !== c) diff.push(`condition differs on ${k}: the chart says [${c}], the spec draws [${have.steps.get(k)}]`);
}
for (const k of have.steps.keys()) if (!want.steps.has(k)) diff.push(`step only in the spec: ${k}`);
const loops = chart.steps.filter((s) => s.from === s.to);
if (loops.length) console.log(`(${loops.length} step(s) that stay in one state are not compared: the program does not draw them)`);
console.log(diff.length ? `\n${diff.length} difference(s) between the agreed chart and the spec:\n${diff.map((d) => `  ${d}`).join("\n")}` : "\nsame: the spec draws the agreed chart");
process.exit(run.status === 1 || diff.length ? 1 : 0);
