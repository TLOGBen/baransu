#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const MAX_ATTEMPT = 2;
const KINDS = ["scout", "worker", "guard", "measurer", "lint"];
const FIELDS = ["id", "title", "kind", "paths", "depends"];
const USAGE = `usage: node board.mjs <command> <board-dir> ...
  init <dir> [seats]                         seats <dir> <n>
  add <dir> <task-json>                      split <dir> <id> <parts-json-array>
  dispatch <dir> <id> <bee> <model> <effort>
  ask <dir> <id> queen|user|env <question>   answer <dir> <id> <answer>
  resume <dir> <id>                          accept <dir> <id> <report-name> <evidence>
  fail <dir> <id> <reason>                   show <dir>
`;

const [cmd, dir, ...rest] = process.argv.slice(2);
const out = [];
const say = (line) => out.push(line);
const refuse = (why) => {
  process.stdout.write(out.map((l) => l + "\n").join(""));
  process.stderr.write(`refused: ${why}\n`);
  process.exit(1);
};
if (!cmd || !dir) refuse(`no command or board folder\n${USAGE}`);

const P = (...p) => path.join(dir, ...p);
const writeAtomic = (file, text) => {
  fs.writeFileSync(`${file}.tmp`, text, "utf8");
  fs.renameSync(`${file}.tmp`, file);
};
const load = () => {
  if (!fs.existsSync(P("tasks.jsonl"))) refuse(`no board in ${dir}: init it first`);
  const tasks = fs.readFileSync(P("tasks.jsonl"), "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
  const settings = fs.existsSync(P("board.json")) ? JSON.parse(fs.readFileSync(P("board.json"), "utf8")) : {};
  return { tasks, settings };
};
const save = ({ tasks, settings }) => {
  writeAtomic(P("tasks.jsonl"), tasks.map((t) => JSON.stringify(t) + "\n").join(""));
  writeAtomic(P("board.json"), JSON.stringify(settings, null, 2) + "\n");
};
const text = (words, what) => {
  const s = words.join(" ").replace(/[\r\n\t]+/g, " ").trim();
  if (!s) refuse(`${what} is empty`);
  return s;
};

// The board lives at <root>/.claude/swarm/<slug>/, so a path inside the project is written relative to <root>.
const ROOT = path.resolve(dir, "..", "..", "..");
// One spelling per path: forward slashes, no `.` or `..` segments, no `./` or trailing slash, and relative to the
// root when it lies inside it — so `./src/a.ts`, `src\a.ts` and the absolute path are one path. `.` is the root.
const clean = (p) => {
  let s = String(p).trim().replace(/\\/g, "/");
  if (path.isAbsolute(s)) {
    const rel = path.relative(ROOT, s).replace(/\\/g, "/");
    if (rel !== ".." && !rel.startsWith("../") && !path.isAbsolute(rel)) s = rel || ".";
  }
  return path.posix.normalize(s).replace(/^(\.\/)+/, "").replace(/(.)\/+$/, "$1");
};
// Compared in one case: on Windows and macOS `Src/A.ts` and `src/a.ts` are one file; elsewhere it only errs safe.
const key = (p) => {
  const k = clean(p).toLowerCase();
  return k === "." ? "" : k;
};
const overlap = (a, b) => {
  const x = key(a), y = key(b);
  return !x || !y || x === y || x.startsWith(y + "/") || y.startsWith(x + "/");
};
const held = (t) => t.state === "running" || t.state === "blocked";
const shared = (t, u) => (t.paths ?? []).find((p) => (u.paths ?? []).some((q) => overlap(p, q)));
const holder = (tasks, t) => tasks.find((u) => u !== t && held(u) && shared(t, u));
const find = (tasks, id) => tasks.find((t) => t.id === id) ?? refuse(`no task ${id} on the board`);
const move = (t, to, why) => {
  say(`${t.id}: ${t.state} → ${to}${why ? ` (${why})` : ""}`);
  t.state = to;
};
const seats = (settings) => settings.seats ?? refuse("the board has no seat count: set it with seats");
const running = (tasks) => tasks.filter((t) => t.state === "running");

const recheck = (tasks) => {
  for (let changed = true; changed; ) {
    changed = false;
    for (const t of tasks.filter((t) => t.state === "waiting")) {
      const deps = t.depends.map((d) => find(tasks, d));
      const gap = deps.find((d) => d.state === "gap");
      if (gap) {
        move(t, "gap", `depends on the gap ${gap.id}`);
        t.evidence = `depends on the gap ${gap.id}`;
        changed = true;
      } else if (deps.every((d) => d.state === "verified")) {
        move(t, "ready");
        changed = true;
      }
    }
  }
};
const failAttempt = (tasks, t, why) => {
  t.awaits = null;
  t.evidence = `attempt ${t.attempt} failed: ${why}`;
  move(t, t.attempt < MAX_ATTEMPT ? "ready" : "gap", t.evidence);
  recheck(tasks);
};

// A report stays where its bee wrote it. Read is what board.json's `read` records: each report's name with a hash
// of what it held when a command acted on it, so a report written again under the same name is unread again.
const hash = (name) => crypto.createHash("sha256").update(fs.readFileSync(P("reports", name))).digest("hex").slice(0, 16);
const unread = () =>
  fs.existsSync(P("reports"))
    ? fs.readdirSync(P("reports"), { withFileTypes: true }).filter((e) => e.isFile() && settings.read?.[e.name] !== hash(e.name)).map((e) => e.name)
    : [];
const ofTask = (id) => unread().filter((n) => n.startsWith(`${id}-`) || n === `${id}.md`);
const markRead = (names) => {
  settings.read ??= {};
  for (const name of names) {
    settings.read[name] = hash(name);
    say(`read reports/${name}`);
  }
};

const chain = (tasks) => {
  const memo = new Map();
  const len = (t) => {
    if (!memo.has(t.id)) {
      memo.set(t.id, 0);
      const behind = tasks.filter((u) => (u.depends ?? []).includes(t.id) && !["verified", "gap", "split"].includes(u.state));
      memo.set(t.id, behind.length ? 1 + Math.max(...behind.map(len)) : 0);
    }
    return memo.get(t.id);
  };
  return len;
};
const startable = (tasks) => {
  const len = chain(tasks);
  return tasks
    .filter((t) => t.state === "ready" && t.attempt < MAX_ATTEMPT && !holder(tasks, t))
    .sort((a, b) => len(b) - len(a))
    .map((t) => (len(t) ? `${t.id} (${len(t)} behind)` : t.id));
};
const status = ({ tasks, settings }) => {
  const live = tasks.filter((t) => t.state !== "split");
  const n = (s) => live.filter((t) => t.state === s).length;
  const onUser = live.filter((t) => t.state === "blocked" && t.awaits?.from === "user").length;
  const free = settings.seats === undefined ? "?" : Math.max(0, settings.seats - n("running"));
  const can = startable(tasks);
  return (
    `${live.length} tasks: ${n("verified")} verified, ${n("running")} running, ${n("blocked")} blocked (${onUser} on the user), ` +
    `${n("ready")} ready, ${n("waiting")} waiting, ${n("gap")} gap · free seats ${free}` + (can.length ? ` · can start: ${can.join(", ")}` : "")
  );
};
const cell = (v, max = 70) => {
  const s = String(v ?? "").replace(/[\r\n\t]+/g, " ").replace(/\|/g, "\\|");
  return s.length > max ? s.slice(0, max - 1) + "…" : s;
};
const table = (head, rows) => [head, head.map(() => "---"), ...rows].map((r) => `| ${r.map((c) => cell(c)).join(" | ")} |`).join("\n");
const note = (tasks, t) => {
  if (t.state === "waiting") return `needs ${t.depends.filter((d) => find(tasks, d).state !== "verified").join(", ")}`;
  const h = t.state === "ready" && holder(tasks, t);
  if (h) return `waits for ${h.id} (path ${shared(t, h)})`;
  if (t.state === "blocked" && t.awaits) return `${t.awaits.from}: ${t.awaits.question}${t.awaits.answer ? " · answered" : ""}`;
  return t.evidence ?? "";
};
const boardTable = (tasks) =>
  table(
    ["id", "state", "try", "bee", "note", "title"],
    tasks.map((t) => [t.id, t.state, t.attempt, t.owner ? `${t.owner}${t.model ? ` ${t.model}/${t.effort}` : ""}` : "", note(tasks, t), t.title])
  );
const newRows = (settings) => {
  if (!fs.existsSync(P("decisions.tsv"))) return [];
  const rows = fs.readFileSync(P("decisions.tsv"), "utf8").split("\n").filter((l) => l.trim()).slice(1).map((l) => l.split("\t"));
  const from = settings.reported_rows ?? 0;
  settings.reported_rows = rows.length;
  return rows.slice(from).map(([ts, ...r]) => [String(ts).slice(11, 16), ...r]);
};

const validate = (tasks, spec, extraIds = []) => {
  if (typeof spec !== "object" || spec === null || Array.isArray(spec)) refuse("a task is one JSON object");
  const extra = Object.keys(spec).filter((k) => !FIELDS.includes(k));
  if (extra.length) refuse(`unknown field ${extra.join(", ")}: a task has only ${FIELDS.join(", ")}`);
  const nums = tasks.map((t) => /^T(\d+)$/.exec(t.id)).filter(Boolean).map((m) => Number(m[1]));
  const id = spec.id ?? `T${Math.max(0, ...nums) + 1}`;
  if (typeof id !== "string" || !/^[A-Za-z0-9][A-Za-z0-9_.]*$/.test(id)) refuse(`id ${JSON.stringify(id)}: letters, digits, _ and . only`);
  if (tasks.some((t) => t.id === id)) refuse(`${id} is already on the board`);
  if (typeof spec.title !== "string" || !spec.title.trim()) refuse(`${id} has no title`);
  if (!KINDS.includes(spec.kind)) refuse(`${id}: kind is one of ${KINDS.join(", ")}`);
  const given = spec.paths ?? [];
  if (!Array.isArray(given) || given.some((p) => typeof p !== "string" || !p.trim())) refuse(`${id}: paths is a list of non-empty strings`);
  for (const p of given) {
    if (/[*?[]/.test(p)) refuse(`${id}: path ${p} is a glob, which the board cannot compare: name the files, or the folder that holds them`);
    const c = clean(p);
    if (c === ".." || c.startsWith("../")) refuse(`${id}: path ${p} leaves the project`);
  }
  const paths = [...new Map(given.map((p) => [key(p), clean(p)])).values()];
  const depends = spec.depends ?? [];
  if (!Array.isArray(depends)) refuse(`${id}: depends is a list of task ids`);
  for (const d of depends) {
    const dep = tasks.find((t) => t.id === d);
    if (!dep && !extraIds.includes(d)) refuse(`${id} depends on ${d}, which is not on the board: add ${d} first`);
    if (dep?.state === "split") refuse(`${id} depends on ${d}, which was split: depend on its parts`);
  }
  return {
    id, title: spec.title.trim(), kind: spec.kind, owner: null, model: null, effort: null, paths, depends: [...new Set(depends)],
    state: depends.length ? "waiting" : "ready", attempt: 0, resumed: false, questions: 0, env_fixed: false,
    awaits: null, evidence: null,
  };
};
const enter = (tasks, t) => {
  tasks.push(t);
  const others = tasks.filter((u) => u !== t && !["verified", "gap", "split"].includes(u.state) && shared(t, u));
  say(`+ ${t.id} ${t.state} ${t.title}${others.length ? ` (shares ${shared(t, others[0])} with ${others.map((u) => u.id).join(", ")})` : ""}`);
};
const cycle = (tasks) => {
  const seen = new Map();
  const visit = (t, trail) => {
    if (seen.get(t.id) === "done") return null;
    if (seen.get(t.id) === "open") return [...trail, t.id];
    seen.set(t.id, "open");
    for (const d of t.depends ?? []) {
      const dep = tasks.find((u) => u.id === d);
      const found = dep && visit(dep, [...trail, t.id]);
      if (found) return found;
    }
    seen.set(t.id, "done");
    return null;
  };
  for (const t of tasks) {
    const found = visit(t, []);
    if (found) return found;
  }
  return null;
};

const board = cmd === "init" ? null : load();
const { tasks, settings } = board ?? { tasks: [], settings: {} };
let rows = [];

if (cmd === "init") {
  if (fs.existsSync(P("tasks.jsonl"))) refuse(`${dir} already has a board`);
  const n = Number(rest[0] ?? 3);
  if (!Number.isInteger(n) || n < 1) refuse("seats is a whole number of at least 1");
  fs.mkdirSync(P("reports"), { recursive: true });
  settings.seats = n;
  settings.reported_rows = 0;
  settings.read = {};
  say(`board ${path.basename(path.resolve(dir))}: ${n} seats`);
} else if (cmd === "seats") {
  const n = Number(rest[0]);
  if (!Number.isInteger(n) || n < 1) refuse("seats is a whole number of at least 1");
  say(`seats: ${settings.seats ?? "?"} → ${n}`);
  settings.seats = n;
} else if (cmd === "add") {
  let spec;
  try {
    spec = JSON.parse(rest.join(" "));
  } catch (e) {
    refuse(`not JSON: ${e.message}`);
  }
  enter(tasks, validate(tasks, spec));
  recheck(tasks);
} else if (cmd === "split") {
  const [id, ...json] = rest;
  const t = find(tasks, id);
  if (!["ready", "waiting", "running", "blocked"].includes(t.state)) refuse(`${id} is ${t.state}: only a task not yet ended can be split`);
  // Too big is split from the report that says so, never retried whole; a bee still at work has left no report.
  if (t.state === "running" && !ofTask(id).length)
    refuse(`${id} is running and its bee has left no report: split it once the bee has ended and reported; if it vanished, record it with fail`);
  let specs;
  try {
    specs = JSON.parse(json.join(" "));
  } catch (e) {
    refuse(`not JSON: ${e.message}`);
  }
  if (!Array.isArray(specs) || specs.length < 2) refuse("a split is a JSON list of at least two tasks");
  const parts = [];
  for (const spec of specs) {
    if ((spec?.depends ?? []).includes(id)) refuse(`a part cannot depend on ${id}, which it replaces`);
    const p = validate([...tasks, ...parts], spec);
    parts.push(p);
  }
  markRead(ofTask(id));
  move(t, "split", `into ${parts.map((p) => p.id).join(", ")}`);
  t.awaits = null;
  t.evidence = `split into ${parts.map((p) => p.id).join(", ")}`;
  for (const p of parts) enter(tasks, p);
  for (const u of tasks.filter((u) => u.depends?.includes(id))) {
    u.depends = [...new Set(u.depends.flatMap((d) => (d === id ? parts.map((p) => p.id) : [d])))];
    say(`${u.id}: depends on ${u.depends.join(", ")}`);
  }
  const loop = cycle(tasks);
  if (loop) refuse(`the split makes a dependency cycle: ${loop.join(" → ")}`);
  recheck(tasks);
} else if (cmd === "dispatch") {
  const [id, bee, model, effort] = rest;
  if (!effort) refuse("dispatch <dir> <id> <bee> <model> <effort>: pin the model and effort");
  const t = find(tasks, id);
  if (t.state !== "ready") refuse(`${id} is ${t.state}, not ready${t.state === "waiting" ? ` (${note(tasks, t)})` : ""}`);
  if (t.attempt >= MAX_ATTEMPT) refuse(`${id} has used its ${MAX_ATTEMPT} attempts`);
  const h = holder(tasks, t);
  if (h) refuse(`${id}: path ${shared(t, h)} is held by ${h.id} (${h.state}); ${id} waits for ${h.id}`);
  const busy = running(tasks);
  if (busy.length >= seats(settings)) refuse(`all ${settings.seats} seats are taken (${busy.map((u) => u.id).join(", ")}): wait for a bee to end`);
  move(t, "running", `attempt ${t.attempt + 1}, ${bee} on ${model}/${effort}`);
  Object.assign(t, { attempt: t.attempt + 1, owner: bee, model, effort, resumed: false, questions: 0, awaits: null });
  rows = newRows(settings);
} else if (cmd === "ask") {
  const [id, from, ...words] = rest;
  if (!["queen", "user", "env"].includes(from)) refuse("ask <dir> <id> queen|user|env <question>");
  const question = text(words, "the question");
  const t = find(tasks, id);
  if (t.state !== "running") refuse(`${id} is ${t.state}: only a running task's bee can ask`);
  markRead(ofTask(id));
  if (from === "env") {
    if (t.env_fixed) failAttempt(tasks, t, `its environment broke again: ${question}`);
    else {
      move(t, "blocked", `awaits the queen: its environment — ${question}`);
      t.awaits = { from, question, answer: null };
    }
  } else if (t.questions >= 1) failAttempt(tasks, t, `a second question in one attempt: ${question}`);
  else {
    t.questions = 1;
    t.awaits = { from, question, answer: null };
    move(t, "blocked", `awaits the ${from}`);
    say(from === "user" ? `ask the user (${id}): ${question}` : `decide (${id}): ${question}`);
  }
} else if (cmd === "answer") {
  const [id, ...words] = rest;
  const answer = text(words, "the answer");
  const t = find(tasks, id);
  if (t.state !== "blocked" || !t.awaits) refuse(`${id} is ${t.state}: there is no question to answer`);
  if (t.awaits.answer) refuse(`${id} is already answered: resume it`);
  t.awaits.answer = answer;
  say(`${id}: answered (${t.awaits.from}) — ${answer}`);
} else if (cmd === "resume") {
  const [id] = rest;
  const t = find(tasks, id);
  if (t.state !== "blocked" || !t.awaits?.answer) refuse(`${id} is ${t.state}${t.state === "blocked" ? " with no answer yet" : ""}: nothing to resume with`);
  const busy = running(tasks);
  if (busy.length >= seats(settings)) refuse(`all ${settings.seats} seats are taken (${busy.map((u) => u.id).join(", ")}): wait for a bee to end`);
  const { from, answer } = t.awaits;
  if (from === "env") t.env_fixed = true;
  move(t, "running", "resumed");
  t.awaits = null;
  say(`send ${t.owner} only this: ${answer}`);
} else if (cmd === "accept") {
  const [id, name, ...words] = rest;
  const t = find(tasks, id);
  if (t.state !== "running") refuse(`${id} is ${t.state}: only a running task is accepted`);
  if (!name || /[\\/]/.test(name) || !name.startsWith(`${id}-`)) refuse(`the report is a file name in reports/ starting with ${id}-`);
  if (!fs.existsSync(P("reports", name)))
    refuse(`no report reports/${name}: ${id} is not accepted. If its bee has ended, record it with fail; the first time, the bee is resumed once to write its report`);
  if (!ofTask(id).includes(name)) refuse(`reports/${name} was already acted on: accept the report its bee wrote since`);
  const evidence = text(words, "the evidence");
  markRead(ofTask(id));
  move(t, "verified");
  t.evidence = `reports/${name}: ${evidence}`;
  recheck(tasks);
} else if (cmd === "fail") {
  const [id, ...words] = rest;
  const reason = text(words, "the reason");
  const t = find(tasks, id);
  if (t.state !== "running") refuse(`${id} is ${t.state}: only a running task's attempt can fail`);
  const files = ofTask(id);
  if (files.length) {
    markRead(files);
    failAttempt(tasks, t, reason);
  } else if (!t.resumed) {
    t.resumed = true;
    say(`${id}: no report — resume ${t.owner} once to write it (${reason})`);
  } else failAttempt(tasks, t, `no report after one resume: ${reason}`);
} else if (cmd === "show") {
  const waitingOnUser = tasks.filter((t) => t.state === "blocked" && t.awaits?.from === "user");
  const files = unread();
  process.stdout.write(
    `${status({ tasks, settings })}\n\n${boardTable(tasks)}\n` +
      waitingOnUser.map((t) => `\nwaiting on the user (${t.id}): ${t.awaits.question}${t.awaits.answer ? ` — answered: ${t.awaits.answer}` : ""}`).join("") +
      (files.length ? `\nunread in reports/: ${files.join(", ")}\n` : "\n")
  );
  process.exit(0);
} else refuse(`unknown command ${cmd}\n${USAGE}`);

save({ tasks, settings });
say(status({ tasks, settings }));
if (cmd === "init") say(`\n${boardTable(tasks)}`);
if (rows.length) say(`\ndecisions since the last report:\n${table(["time", "phase", "decision", "why", "evidence", "result"], rows)}`);
process.stdout.write(out.map((l) => l + "\n").join(""));
