// Read a Mermaid stateDiagram-v2 into one model, for charts the statechart program
// writes and for charts a person draws.
//
// A state is named by its label path: the groups above it and its own label. A group
// whose body holds `--` lines is a set of parallel regions; each child group is a region,
// and the group itself is not part of the path. Each step is { from, to, label, when },
// with from and to as label-path keys. A person's chart may also carry rules
// (`%% never NAME: A & B -- sentence`) and guards (`%% when ID, ID` or `%% when not ID, ID`
// on the line right after a step). The legend group is skipped.

export const SEP = " › ";

// The statechart program writes each character outside its safe set as `#<code point>;`
// and may join two characters with U+2060. decode() gives the words back; encode() writes
// new words the same way, so a merged chart stays valid Mermaid.
export const decode = (s) => s.replace(/#(\d+);/g, (_, n) => String.fromCodePoint(Number(n))).replaceAll("⁠", "");
const SAFE = /^[\p{L}\p{N} !'()+,\-./=?[\]"_|@{}:\\^%<>]$/u;
export const encode = (s) => [...s].map((c) => (SAFE.test(c) ? c : `#${c.codePointAt(0)};`)).join("");

export function parseChart(text) {
  const lines = text.split(/\r?\n/).map((l) => l.trim());
  const title = (text.match(/^title: (.*)$/m) || [])[1];
  const titleText = title ? decode(title.startsWith('"') ? JSON.parse(title) : title) : undefined;

  // Pass 1: which groups hold `--` at their own level (region containers).
  const containers = new Set();
  {
    const stack = [];
    for (const line of lines) {
      const g = line.match(/^state "(.*)" as (\w+) \{$/) || line.match(/^state (\w+) \{$/);
      if (g) stack.push(g[2] ?? g[1]);
      else if (line === "}") stack.pop();
      else if (line === "--" && stack.length) containers.add(stack[stack.length - 1]);
    }
  }

  const caption = new Map(); // id -> label
  const kinds = new Map(); // id -> { path: [...], region }
  const stack = []; // { id, title, container, region }
  const steps = [];
  const starts = [];
  const classes = [];
  const nevers = [];
  const order = [];
  const regions = [];
  let inLegend = false;
  const where = () => {
    const path = [];
    let region = null;
    for (const f of stack) {
      if (f.container) continue;
      if (f.region) region = f.title;
      path.push(f.title);
    }
    return { path, region };
  };
  const declare = (id, label) => {
    if (label !== undefined) label = decode(label);
    if (!caption.has(id)) caption.set(id, label ?? id);
    else if (label) caption.set(id, label);
    if (!kinds.has(id)) {
      kinds.set(id, where());
      order.push(id);
    }
  };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    let m;
    if (!line || line === "stateDiagram-v2" || line.startsWith("direction ") || line === "---" || line.startsWith("title:")) continue;
    if ((m = line.match(/^state "(.*)" as (\w+) \{$/) || line.match(/^state (\w+) \{$/))) {
      const id = m[2] ?? m[1];
      const titleOf = decode(m[1]);
      if (id === "legend") { inLegend = true; continue; }
      const parent = stack[stack.length - 1];
      const region = Boolean(parent?.container);
      if (region && !regions.includes(titleOf)) regions.push(titleOf);
      stack.push({ id, title: titleOf, container: containers.has(id), region });
      continue;
    }
    if (line === "}") {
      if (inLegend) inLegend = false;
      else stack.pop();
      continue;
    }
    if (inLegend || line === "--") continue;
    if ((m = line.match(/^%% never (\S+?):\s*(.+?)\s+--\s+(.+)$/))) {
      nevers.push({ name: m[1], parts: m[2].split("&").map((s) => s.trim()), sentence: m[3] });
      continue;
    }
    if ((m = line.match(/^%% when (not )?(.+)$/))) {
      const last = steps[steps.length - 1];
      if (last) last.when = { not: Boolean(m[1]), ids: m[2].split(",").map((s) => s.trim()) };
      continue;
    }
    if (line.startsWith("%%")) continue;
    if ((m = line.match(/^state "(.*)" as (\w+)$/))) { declare(m[2], m[1]); continue; }
    if ((m = line.match(/^\[\*\] --> (\w+)$/))) { declare(m[1]); starts.push(m[1]); continue; }
    if ((m = line.match(/^(\w+) --> \[\*\]/))) throw new Error(`final states are not supported (${line})`);
    if ((m = line.match(/^(\w+) --> (\w+)(?:\s*:\s*(.*))?$/))) {
      declare(m[1]);
      declare(m[2]);
      steps.push({ from: m[1], to: m[2], label: decode((m[3] ?? "").trim()) });
      continue;
    }
    if ((m = line.match(/^class (\w+) (\w+)$/))) { classes.push([m[1], m[2]]); continue; }
    if (line.startsWith("classDef ")) continue;
    if ((m = line.match(/^(\w+)\s*:\s*(.*)$/))) { declare(m[1], m[2]); continue; }
    if ((m = line.match(/^(\w+)$/))) { declare(m[1]); continue; }
    throw new Error(`cannot read line: ${line}`);
  }

  const key = (id) => [...kinds.get(id).path, caption.get(id)].join(SEP);
  const states = new Map();
  for (const id of order) {
    const k = key(id);
    if (!states.has(k)) states.set(k, { id, label: caption.get(id), path: [...kinds.get(id).path, caption.get(id)], region: kinds.get(id).region, marks: new Set(), color: undefined });
  }
  const MARKS = new Set(["breaks", "mayBreak", "bugPath", "repeats"]);
  for (const [id, cls] of classes) {
    const s = kinds.has(id) && states.get(key(id));
    if (!s) continue;
    if (MARKS.has(cls)) s.marks.add(cls);
    else s.color = cls;
  }
  return {
    title: titleText,
    regions,
    order: [...states.keys()],
    states,
    idKey: key,
    ids: order,
    caption,
    starts: new Set(starts.map(key)),
    steps: steps.map((s) => ({ from: key(s.from), to: key(s.to), label: s.label, when: s.when, fromId: s.from, toId: s.to })),
    nevers,
  };
}

// A step label without the condition in brackets at its end.
export const bareLabel = (label) => label.replace(/\s*\[[^\]]*\]\s*$/, "");
