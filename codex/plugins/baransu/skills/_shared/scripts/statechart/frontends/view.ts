import { type CheckedView, checked, list, type Value, type Vars } from "../ir.ts";

type Json = boolean | number | string | Json[] | { [key: string]: Json };

const projected = new WeakMap<object, Json>();

export const json = (v: Value): Json => {
  if (typeof v !== "object") return v;
  if (v.kind === "model") return v.name;
  let j = projected.get(v);
  if (j === undefined) {
    if (v.kind === "interval") {
      const members: Json[] = [];
      for (let k = v.lo; k <= v.hi; k++) members.push(k);
      j = members;
    } else if (v.kind === "set") {
      const members: Json[] = [];
      for (const m of v.members) members.push(json(m));
      j = members;
    } else {
      const fields: [string, Json][] = [];
      for (let i = 0; i < v.keys.length; i++) {
        const k = json(v.keys[i]);
        fields.push([typeof k === "object" ? JSON.stringify(k) : String(k), json(v.values[i])]);
      }
      j = Object.fromEntries(fields);
    }
    projected.set(v, j);
  }
  return j;
};

const projectedVars = new WeakMap<Vars, { [name: string]: Json }>();

const jsonVars = (vars: Vars) => {
  let j = projectedVars.get(vars);
  if (j === undefined) {
    const fields: [string, Json][] = [];
    for (const [name, v] of Object.entries(vars)) fields.push([name, json(v)]);
    j = Object.fromEntries(fields);
    projectedVars.set(vars, j);
  }
  return j;
};

const THEME_COLORS = ["blue", "orange", "purple", "yellow", "teal", "tan", "pink"];

const isFunction = (v: unknown): v is (...args: unknown[]) => unknown => typeof v === "function";

const isPlainObject = (v: unknown): v is { [key: string]: unknown } => {
  if (typeof v !== "object" || v === null) return false;
  const proto = Object.getPrototypeOf(v);
  return proto === Object.prototype || proto === null;
};

const isString = (v: unknown) => typeof v === "string";

const VIEW_EXPORTS = ["state", "step", "group", "colors", "title", "rules"]; // baransu: rules

type Inspect = (value: unknown, options: { breakLength: number }) => string;

export function checkView(
  view: { readonly [name: string]: unknown },
  inspect: Inspect,
): CheckedView {
  const literal = (v: unknown) =>
    typeof v === "string" ? JSON.stringify(v) : inspect(v, { breakLength: Infinity });
  const extra: string[] = [];
  for (const name of Object.keys(view)) if (!VIEW_EXPORTS.includes(name)) extra.push(name);
  if (extra.length)
    throw new Error(
      `The view exports ${list(extra)}, which the command does not read. Export only ${list(VIEW_EXPORTS)}.`,
    );
  const wrong: string[] = [];
  const pick = <T>(name: string, kind: string, fits: (v: unknown) => v is T) => {
    const v = view[name];
    if (v === undefined || fits(v)) return v;
    wrong.push(`${name} must be ${kind}`);
    return undefined;
  };
  const state = pick("state", "a function", isFunction);
  const step = pick("step", "a function", isFunction);
  const group = pick("group", "a function", isFunction);
  const exported = pick("colors", "a plain object", isPlainObject);
  const title = pick("title", "a string", isString);
  const named_rules = pick("rules", "a plain object", isPlainObject); // baransu
  if (wrong.length) throw new Error(`The view's ${list(wrong)}.`);
  // baransu: each rule name maps to the reader's words for it
  const rules: { [rule: string]: string } = Object.create(null);
  const notWords: string[] = [];
  for (const [name, words] of Object.entries(named_rules ?? {})) {
    if (typeof words === "string" && words.trim()) rules[name] = words;
    else notWords.push(JSON.stringify(name));
  }
  if (notWords.length) throw new Error(`The view's rules give ${list(notWords)} no words. Give each rule a non-empty string.`);
  if (group !== undefined && exported === undefined)
    throw new Error("The view exports group() but no colors. Give each group a color in colors.");
  const colors: { [group: string]: string } = Object.create(null);
  const bad: string[] = [];
  for (const [name, color] of Object.entries(exported ?? {})) {
    if (typeof color === "string" && THEME_COLORS.includes(color)) colors[name] = color;
    else bad.push(`${JSON.stringify(name)} the color ${literal(color)}`);
  }
  if (bad.length)
    throw new Error(
      `The view's colors give ${list(bad)}. Give each group ${list(THEME_COLORS, "or")}.`,
    );
  const named =
    group &&
    ((vars: Vars) => {
      const g = group(jsonVars(vars));
      if (g !== undefined && !Object.hasOwn(colors, typeof g === "symbol" ? g : String(g)))
        throw new Error(
          `The view's group() returned ${literal(g)}, which colors does not name. Give each group a color in colors.`,
        );
      return g;
    });
  return {
    state: state && ((vars: Vars) => state(jsonVars(vars))),
    step:
      step &&
      ((action: string, from: Vars, to: Vars) => step(action, jsonVars(from), jsonVars(to))),
    group: named,
    colors,
    title,
    rules, // baransu
    [checked]: true,
  };
}
