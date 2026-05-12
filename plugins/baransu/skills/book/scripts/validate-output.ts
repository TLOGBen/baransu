#!/usr/bin/env -S npx tsx
/**
 * validate-output.ts — book skill HTML quality gate
 * Usage: npx tsx validate-output.ts <path-to-html-file>
 * Exit 0 = GATE PASS, Exit 1 = one or more checks failed, Exit 2 = usage error
 *
 * Existing checks (preserved):
 *   - html-parse        : HTML parseable via Python html.parser
 *   - structure         : <main> or <article> present
 *   - svg-balance       : <svg> / </svg> tag counts match, ≥ 1 SVG
 *   - asset-path        : local src="…" files exist on disk
 *
 * New gates (cheerio-based, per REQ-004):
 *   - GATE-A focal-cap          : ≤ 2 [data-role="focal"] per SVG
 *   - GATE-B paper-mask         : first child of SVG is <rect width="100%"…fill="#hex">
 *   - GATE-C legend-strip       : SVGs with viewBox height ≥ 400 carry a bottom hairline + LEGEND text
 *   - GATE-D marker-integrity   : marker defs ↔ marker-end refs are bijective (no dangling / no unused)
 *   - GATE-E deny-list          : no <script>, <foreignObject>, on{click,load,error,mouseover,mousedown},
 *                                 no href/xlink:href starting with "javascript:"
 *   - GATE-F class-prefix (PPT) : every class token's prefix MUST be in the
 *                                 v1.3 whitelist {kami, google, swiss} ∪ {dynamic gen slug
 *                                 from tokens.css line 1}; single prefix per file;
 *                                 matches {project_root}/tokens.css preset header.
 *                                 `/* preset: <name> *\/` comment when present
 *   - GATE-J node-width-whitelist: top-level node <rect> widths must ∈ {128, 144, 160};
 *                                  max 2 distinct tiers per SVG (full viewBox ≥ 360);
 *                                  viewBox width < 360 still capped at 2 tiers.
 *                                  Sub-primitives (width < 40, width="100%", inside
 *                                  <pattern> or <defs>) are excluded.
 *   - GATE-K chevron-strict     : every <marker> defs must contain exactly one
 *                                  <path d="M2 1 L8 5 L2 9" fill="none"
 *                                  stroke-width="1.5">; <polygon> markers forbidden.
 */
import { readFileSync, existsSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { load, type CheerioAPI, type Cheerio } from "cheerio";
import type { Element as DomElement } from "domhandler";

const htmlFile = process.argv[2];
if (!htmlFile || !existsSync(htmlFile)) {
  console.error("Usage: npx tsx validate-output.ts <path-to-html-file>");
  process.exit(2);
}

const htmlDir = dirname(resolve(htmlFile));
const content = readFileSync(htmlFile, "utf8");
let fail = 0;
// Module-level warnings sink. Every `WARN …` line we log also gets pushed here
// so the end-of-run summary can list them together (soft_warn levels would
// also land here once the html2pptx rule levels relax). Hard failures stay
// out of this array — they show up via `fail = 1` and individual FAIL logs.
const warnings: string[] = [];

// ── project root resolver (shared by GATE-F + GATE-G) ──────────────────────
// Try `git rev-parse --show-toplevel` from the HTML file's directory first
// (slide HTML normally lives inside the project); fall back to the same
// command from process.cwd(); final fallback = process.cwd() itself.
// Memoized per htmlDir so multiple gates share the same lookup.
const projectRootCache = new Map<string, string>();
function gitToplevel(cwd: string): string | null {
  const r = spawnSync("git", ["rev-parse", "--show-toplevel"], {
    encoding: "utf8",
    cwd,
  });
  return r.status === 0 ? r.stdout.trim() : null;
}
function resolveProjectRoot(htmlDir: string): string {
  const cached = projectRootCache.get(htmlDir);
  if (cached !== undefined) return cached;
  const root =
    gitToplevel(htmlDir) ?? gitToplevel(process.cwd()) ?? process.cwd();
  projectRootCache.set(htmlDir, root);
  return root;
}

// ── (a) HTML parseable via Python ───────────────────────────────────────────
const parseResult = spawnSync(
  "python3",
  ["-c", `from html.parser import HTMLParser\np=HTMLParser()\np.feed(open(${JSON.stringify(htmlFile)}).read())\nprint('ok')`],
  { encoding: "utf8" }
);
if (parseResult.status === 0) {
  console.log("OK  html-parse");
} else {
  console.log("FAIL html-parse: file cannot be parsed as HTML");
  fail = 1;
}

// ── (b) <main> or <article> structure present ───────────────────────────────
if (/<(main|article)[^>]*>/i.test(content)) {
  console.log("OK  structure");
} else {
  console.log("FAIL structure: no <main> or <article> element found");
  fail = 1;
}

// ── (c) SVG tags balanced ───────────────────────────────────────────────────
const openSvg  = (content.match(/<svg/gi)  ?? []).length;
const closeSvg = (content.match(/<\/svg>/gi) ?? []).length;
if (openSvg >= 1 && openSvg === closeSvg) {
  console.log(`OK  svg-balance (${openSvg} diagram(s))`);
} else if (openSvg === 0) {
  console.log("FAIL svg-balance: no SVG diagram found (at least 1 required)");
  fail = 1;
} else {
  console.log(`FAIL svg-balance: ${openSvg} <svg> vs ${closeSvg} </svg>`);
  fail = 1;
}

// ── (d) Local asset paths exist ─────────────────────────────────────────────
const srcPattern = /src="([^"]+)"/g;
let match: RegExpExecArray | null;
while ((match = srcPattern.exec(content)) !== null) {
  const src = match[1];
  if (src.startsWith("data:") || src.startsWith("http://") || src.startsWith("https://")) continue;
  const abs = resolve(htmlDir, src);
  if (!existsSync(abs)) {
    console.log(`FAIL asset-path: missing '${src}'`);
    fail = 1;
  }
}

// ── cheerio load (xml mode preserves SVG namespaces) ────────────────────────
// `xmlMode: false` keeps HTML semantics for <main>/<article>; we use attribute
// selectors that work in both modes. We disable `lowerCaseAttributeNames` so
// xlink:href survives.
const $: CheerioAPI = load(content, {
  xml: { lowerCaseAttributeNames: false, xmlMode: false } as never,
} as never);

const svgs = $("svg").toArray() as DomElement[];

function svgLabel(idx: number, el: DomElement): string {
  const vb = $(el).attr("viewBox") ?? "(no viewBox)";
  return `svg#${idx + 1} [viewBox=${vb}]`;
}

function parseViewBoxHeight(vb: string | undefined): number | null {
  if (!vb) return null;
  const parts = vb.trim().split(/[\s,]+/);
  if (parts.length < 4) return null;
  const h = Number(parts[3]);
  return Number.isFinite(h) ? h : null;
}

// ── GATE-A: focal cap (≤ 2 per SVG) ─────────────────────────────────────────
svgs.forEach((svg, i) => {
  const focals = $(svg).find('[data-role="focal"]');
  if (focals.length > 2) {
    console.log(
      `FAIL GATE-A focal-cap: ${svgLabel(i, svg)} has ${focals.length} [data-role="focal"] (max 2)`
    );
    fail = 1;
  } else {
    console.log(`OK  GATE-A focal-cap (${svgLabel(i, svg)}, count=${focals.length})`);
  }
});

// ── GATE-B: first-layer paper-mask ──────────────────────────────────────────
// First direct child of <svg> must be <rect width="100%" height="100%" fill="#hex">
// (defs/title/desc/metadata are skipped — they are containers, not visual layers.)
svgs.forEach((svg, i) => {
  const visualChildren = $(svg)
    .children()
    .toArray()
    .filter((c) => {
      const tag = (c as DomElement).tagName?.toLowerCase();
      return tag && !["defs", "title", "desc", "metadata", "style"].includes(tag);
    }) as DomElement[];

  const first = visualChildren[0];
  const firstTag = first?.tagName?.toLowerCase();
  const width = first ? $(first).attr("width") : undefined;
  const fill = first ? $(first).attr("fill") : undefined;
  const isHexFill = !!fill && /^#[0-9a-fA-F]{3,8}$/.test(fill);

  if (firstTag === "rect" && width === "100%" && isHexFill) {
    console.log(`OK  GATE-B paper-mask (${svgLabel(i, svg)}, fill=${fill})`);
  } else {
    console.log(
      `FAIL GATE-B paper-mask: ${svgLabel(i, svg)} first child is <${firstTag ?? "none"}` +
        ` width="${width ?? ""}" fill="${fill ?? ""}"> — expected <rect width="100%" fill="#hex">`
    );
    fail = 1;
  }
});

// ── GATE-C: legend strip (only when viewBox height ≥ 400) ───────────────────
svgs.forEach((svg, i) => {
  const vbH = parseViewBoxHeight($(svg).attr("viewBox"));
  if (vbH === null || vbH < 400) {
    console.log(
      `SKIP GATE-C legend-strip (${svgLabel(i, svg)}, height=${vbH ?? "n/a"} < 400)`
    );
    return;
  }
  // Look for a <line> within bottom 60px AND a <text> containing "LEGEND".
  const hasLegendText = $(svg)
    .find("text")
    .toArray()
    .some((t) => /LEGEND/.test($(t).text()));
  const hasBottomLine = $(svg)
    .find("line")
    .toArray()
    .some((l) => {
      const y1 = Number($(l).attr("y1"));
      const y2 = Number($(l).attr("y2"));
      if (!Number.isFinite(y1) || !Number.isFinite(y2)) return false;
      const yMax = Math.max(y1, y2);
      return yMax >= vbH - 60 && yMax <= vbH;
    });
  if (hasLegendText && hasBottomLine) {
    console.log(`OK  GATE-C legend-strip (${svgLabel(i, svg)})`);
  } else {
    console.log(
      `FAIL GATE-C legend-strip: ${svgLabel(i, svg)} missing bottom hairline (${hasBottomLine}) or LEGEND text (${hasLegendText})`
    );
    fail = 1;
  }
});

// ── GATE-D: marker reference integrity ──────────────────────────────────────
svgs.forEach((svg, i) => {
  const defIds = new Set<string>();
  $(svg)
    .find("marker[id]")
    .each((_, m) => {
      const id = $(m).attr("id");
      if (id) defIds.add(id);
    });

  const refIds = new Set<string>();
  // collect from marker-end / marker-start / marker-mid url(#id) values
  ["marker-end", "marker-start", "marker-mid"].forEach((attr) => {
    $(svg)
      .find(`[${attr}]`)
      .each((_, el) => {
        const v = $(el).attr(attr) ?? "";
        const m = v.match(/^url\(#([^)]+)\)$/);
        if (m) refIds.add(m[1]);
      });
  });

  const dangling = [...refIds].filter((id) => !defIds.has(id));
  const unused = [...defIds].filter((id) => !refIds.has(id));

  if (dangling.length === 0 && unused.length === 0) {
    console.log(
      `OK  GATE-D marker-integrity (${svgLabel(i, svg)}, defs=${defIds.size}, refs=${refIds.size})`
    );
  } else {
    if (dangling.length > 0) {
      console.log(
        `FAIL GATE-D marker-integrity: ${svgLabel(i, svg)} dangling marker reference(s): ${dangling
          .map((id) => `#${id}`)
          .join(", ")}`
      );
    }
    if (unused.length > 0) {
      console.log(
        `FAIL GATE-D marker-integrity: ${svgLabel(i, svg)} unused marker definition(s): ${unused
          .map((id) => `#${id}`)
          .join(", ")}`
      );
    }
    fail = 1;
  }
});

// ── GATE-E: SVG deny-list (script / foreignObject / on* / javascript: href) ─
const ON_ATTRS = ["onclick", "onload", "onerror", "onmouseover", "onmousedown"];
svgs.forEach((svg, i) => {
  let violated = false;

  const scripts = $(svg).find("script");
  if (scripts.length > 0) {
    console.log(
      `FAIL GATE-E deny-list: ${svgLabel(i, svg)} contains <script> (${scripts.length}×)`
    );
    violated = true;
  }

  const fo = $(svg).find("foreignObject, foreignobject");
  if (fo.length > 0) {
    console.log(
      `FAIL GATE-E deny-list: ${svgLabel(i, svg)} contains <foreignObject> (${fo.length}×)`
    );
    violated = true;
  }

  ON_ATTRS.forEach((attr) => {
    const els = $(svg).find(`[${attr}]`);
    if (els.length > 0) {
      const tagNames = (els.toArray() as DomElement[])
        .map((e) => e.tagName?.toLowerCase() ?? "?")
        .join(", ");
      console.log(
        `FAIL GATE-E deny-list: ${svgLabel(i, svg)} has ${attr} attribute on <${tagNames}>`
      );
      violated = true;
    }
  });

  // href / xlink:href starting with "javascript:" (prefix-only; case-insensitive)
  const allEls = $(svg).find("*").toArray() as DomElement[];
  for (const el of allEls) {
    const $el = $(el);
    const href = $el.attr("href");
    const xhref = $el.attr("xlink:href");
    const tag = el.tagName?.toLowerCase() ?? "?";
    const isJs = (v: string | undefined) => !!v && /^\s*javascript:/i.test(v);
    if (isJs(href)) {
      console.log(
        `FAIL GATE-E deny-list: ${svgLabel(i, svg)} <${tag} href="${href}"> starts with javascript:`
      );
      violated = true;
    }
    if (isJs(xhref)) {
      console.log(
        `FAIL GATE-E deny-list: ${svgLabel(i, svg)} <${tag} xlink:href="${xhref}"> starts with javascript:`
      );
      violated = true;
    }
  }

  if (!violated) {
    console.log(`OK  GATE-E deny-list (${svgLabel(i, svg)})`);
  } else {
    fail = 1;
  }
});

// ── GATE-J: node-width whitelist (top-level node <rect> tier discipline) ───
// Top-level node <rect> widths must ∈ {128, 144, 160} (Kami spec §4.7).
// Sub-primitives are filtered out:
//   - width = "100%"  (paper-mask layer; covered by GATE-B)
//   - width < 40      (type-tag pip, legend pip, marker visuals)
//   - inside <pattern>   (background pattern primitives)
//   - inside <defs>      (template definitions, not visual nodes)
// Single SVG: at most 2 distinct width tiers (3-tier mix = anti-slop FAIL).
// viewBox width < 360 still caps at 2 tiers per §4.7 exception clause.
const NODE_WIDTH_WHITELIST = new Set([128, 144, 160]);

function parseViewBoxWidth(vb: string | undefined): number | null {
  if (!vb) return null;
  const parts = vb.trim().split(/[\s,]+/);
  if (parts.length < 4) return null;
  const w = Number(parts[2]);
  return Number.isFinite(w) ? w : null;
}

function hasAncestor(el: DomElement, tagNames: Set<string>, stopAt: DomElement): boolean {
  let p = el.parent as DomElement | null;
  while (p && p !== stopAt) {
    const tag = p.tagName?.toLowerCase();
    if (tag && tagNames.has(tag)) return true;
    p = p.parent as DomElement | null;
  }
  return false;
}

svgs.forEach((svg, i) => {
  const label = svgLabel(i, svg);
  const vbW = parseViewBoxWidth($(svg).attr("viewBox"));
  const allRects = $(svg).find("rect").toArray() as DomElement[];
  const skipAncestors = new Set(["pattern", "defs"]);

  const nodeWidths: number[] = [];
  const offendingWidths: number[] = [];
  for (const r of allRects) {
    const wAttr = $(r).attr("width");
    if (!wAttr) continue;
    if (wAttr === "100%") continue;
    if (hasAncestor(r, skipAncestors, svg)) continue;
    const wNum = Number(wAttr);
    if (!Number.isFinite(wNum)) continue;
    if (wNum < 40) continue;
    nodeWidths.push(wNum);
    if (!NODE_WIDTH_WHITELIST.has(wNum)) offendingWidths.push(wNum);
  }

  const distinctTiers = new Set(nodeWidths.filter((w) => NODE_WIDTH_WHITELIST.has(w)));

  if (offendingWidths.length > 0) {
    console.log(
      `FAIL GATE-J node-width-whitelist (${label}, offending widths=[${offendingWidths.join(", ")}]) — expected ∈ {128, 144, 160}`
    );
    fail = 1;
    return;
  }

  // Tier count rule: full viewBox (≥ 360) max 2 tiers; < 360 also max 2 tiers
  // (§4.7 exception keeps the same 2-tier cap but allows the 2-of-3 subset).
  if (distinctTiers.size > 2) {
    const tierList = [...distinctTiers].sort((a, b) => a - b).join(", ");
    const vbNote = vbW !== null && vbW < 360 ? `, viewBox width=${vbW}<360` : "";
    console.log(
      `FAIL GATE-J node-width-whitelist (${label}, tiers used=[${tierList}]${vbNote}) — max 2 tiers per diagram`
    );
    fail = 1;
    return;
  }

  console.log(
    `OK  GATE-J node-width-whitelist (${label}, node rects=${nodeWidths.length}, tiers=[${[...distinctTiers].sort((a, b) => a - b).join(", ") || "none"}])`
  );
});

// ── GATE-K: chevron-strict (marker defs must be Kami stroked chevron) ──────
// Every <marker> inside <defs> must contain exactly one <path> whose `d` is
// the canonical chevron `M2 1 L8 5 L2 9`, with `fill="none"` and
// `stroke-width="1.5"` (§4.3). <polygon> inside a <marker> is forbidden.
const CHEVRON_PATH_D = "M2 1 L8 5 L2 9";
function normalizePathD(d: string | undefined): string {
  if (!d) return "";
  return d.replace(/,/g, " ").replace(/\s+/g, " ").trim();
}

svgs.forEach((svg, i) => {
  const label = svgLabel(i, svg);
  const markers = $(svg).find("marker").toArray() as DomElement[];
  if (markers.length === 0) {
    console.log(`OK  GATE-K chevron-strict (${label}, markers checked=0)`);
    return;
  }

  let violated = false;
  for (const m of markers) {
    const mid = $(m).attr("id") ?? "(no id)";
    const polygons = $(m).find("polygon");
    if (polygons.length > 0) {
      console.log(
        `FAIL GATE-K chevron-strict: ${label} marker '${mid}' violation: contains <polygon> (forbidden; use stroked <path> chevron)`
      );
      violated = true;
      continue;
    }
    const paths = $(m).find("path").toArray() as DomElement[];
    if (paths.length !== 1) {
      console.log(
        `FAIL GATE-K chevron-strict: ${label} marker '${mid}' violation: expected exactly 1 <path>, found ${paths.length}`
      );
      violated = true;
      continue;
    }
    const p = paths[0];
    const d = normalizePathD($(p).attr("d"));
    const pFill = $(p).attr("fill");
    const sw = $(p).attr("stroke-width");
    if (d !== CHEVRON_PATH_D) {
      console.log(
        `FAIL GATE-K chevron-strict: ${label} marker '${mid}' violation: path d="${d}" — expected "${CHEVRON_PATH_D}"`
      );
      violated = true;
      continue;
    }
    if (pFill !== "none") {
      console.log(
        `FAIL GATE-K chevron-strict: ${label} marker '${mid}' violation: path fill="${pFill ?? ""}" — expected "none"`
      );
      violated = true;
      continue;
    }
    if (sw !== "1.5") {
      console.log(
        `FAIL GATE-K chevron-strict: ${label} marker '${mid}' violation: path stroke-width="${sw ?? ""}" — expected "1.5"`
      );
      violated = true;
      continue;
    }
  }

  if (violated) {
    fail = 1;
  } else {
    console.log(`OK  GATE-K chevron-strict (${label}, markers checked=${markers.length})`);
  }
});

// ── Mode detection (shared by 4 html2pptx pre-checks + GATE-F + GATE-G) ─────
//   PPT       → contains `<section data-layout="...">`
//   long-form → contains `<article class="paper">`
//   otherwise → unknown; PPT-only gates skipped (preserves backwards-compat
//   with the existing SVG-only fixtures used in scripts/validate-fixtures/).
const isPpt = /<section\b[^>]*\bdata-layout\s*=/i.test(content);
const isLongForm = /<article\b[^>]*\bclass\s*=\s*"[^"]*\bpaper\b[^"]*"/i.test(content);

// ── html2pptx 4-rule pre-check (PPT mode only) ──────────────────────────────
// Fixture-calibrated rule levels (TASK-book-validator-03 / REQ-003-S1).
// Calibration source: fixture-result.md (hardcoded — not read at runtime so
// that archiving .claude/analyze/<date>/ does not break the validator).
const HTML2PPTX_RULE_LEVELS = {
  rule1_div_text: "hard_fail",
  rule2_gradient: "hard_fail",     // fixture-calibrated up from soft_warn
  rule3_bg_on_text: "hard_fail",   // fixture-calibrated up from soft_warn
  rule4_div_bg_image: "hard_fail",
} as const;

type RuleId = keyof typeof HTML2PPTX_RULE_LEVELS;

interface RuleViolation {
  rule: RuleId;
  line: number;
  selector: string;
  detail: string;
}

// Parse <style> blocks into a map: className → joined-property-text.
// Supports simple selectors like `.swiss-foo { ... }` and `.a, .b { ... }`.
// Pseudo-classes / nested combinators are not unrolled; for those we still
// capture the property text under each leading class token, which is enough
// for the html2pptx rule checks (we only inspect property substrings).
function parseStyleBlocks(html: string): Map<string, string> {
  const classProps = new Map<string, string>();
  const styleBlockRe = /<style\b[^>]*>([\s\S]*?)<\/style>/gi;
  let blockMatch: RegExpExecArray | null;
  while ((blockMatch = styleBlockRe.exec(html)) !== null) {
    const cssText = blockMatch[1];
    // Strip CSS comments first so they don't confuse the rule scanner.
    const noComments = cssText.replace(/\/\*[\s\S]*?\*\//g, "");
    const ruleRe = /([^{}]+)\{([^{}]*)\}/g;
    let ruleMatch: RegExpExecArray | null;
    while ((ruleMatch = ruleRe.exec(noComments)) !== null) {
      const selectors = ruleMatch[1].split(",");
      const props = ruleMatch[2];
      for (const sel of selectors) {
        const trimmed = sel.trim();
        // Pick the leading class token in the selector, e.g. `.swiss-foo:hover` → swiss-foo.
        const classMatches = trimmed.match(/\.([A-Za-z0-9_-]+)/g);
        if (!classMatches) continue;
        for (const cm of classMatches) {
          const cls = cm.slice(1);
          const prev = classProps.get(cls) ?? "";
          classProps.set(cls, prev + ";" + props);
        }
      }
    }
  }
  return classProps;
}

function elementSelector(el: DomElement): string {
  const tag = el.tagName?.toLowerCase() ?? "?";
  const cls = ($(el).attr("class") ?? "").trim();
  return cls ? `<${tag} class="${cls}">` : `<${tag}>`;
}

// `lines` is shared with GATE-F. Defined once here, reused below.
const lines = content.split(/\r?\n/);

function elementLineNumber(el: DomElement): number {
  // domhandler exposes startIndex when withStartIndices is on; cheerio's
  // default loader does NOT set it. As a pragmatic fallback we locate the
  // first occurrence of `<tag` matching the element's class signature in
  // the raw source. Imperfect for repeated structures but good enough for
  // user-facing diagnostics.
  const tag = el.tagName?.toLowerCase() ?? "";
  if (!tag) return 1;
  const cls = ($(el).attr("class") ?? "").trim();
  const needle = cls
    ? new RegExp(`<${tag}\\b[^>]*class\\s*=\\s*"${cls.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&")}"`, "i")
    : new RegExp(`<${tag}\\b`, "i");
  for (let i = 0; i < lines.length; i += 1) {
    if (needle.test(lines[i])) return i + 1;
  }
  return 1;
}

function detect_rule1_div_text(cls: Map<string, string>): RuleViolation[] {
  const out: RuleViolation[] = [];
  const allowedParents = new Set(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]);
  $("div").each((_, el) => {
    const divEl = el as DomElement;
    // Look for direct text-node children with non-whitespace content.
    const kids = divEl.children ?? [];
    for (const kid of kids) {
      // domhandler text node type === "text"
      if ((kid as { type?: string }).type === "text") {
        const text = (kid as { data?: string }).data ?? "";
        if (text.trim().length === 0) continue;
        // div allows wrapping text in <p>/<h*>/<li>; bare text is the violation.
        out.push({
          rule: "rule1_div_text",
          line: elementLineNumber(divEl),
          selector: elementSelector(divEl),
          detail: `<div> contains direct text node '${text.trim().slice(0, 40)}…' not wrapped in <${[...allowedParents].join("|")}>`,
        });
        break; // one violation per div is enough for the report
      }
    }
  });
  return out;
}

function detect_rule2_gradient(cls: Map<string, string>): RuleViolation[] {
  const out: RuleViolation[] = [];
  const gradientRe = /(linear|radial)-gradient\(/i;
  // (a) inline style="" attribute on any element
  $("[style]").each((_, el) => {
    const domEl = el as DomElement;
    const style = $(domEl).attr("style") ?? "";
    if (gradientRe.test(style)) {
      out.push({
        rule: "rule2_gradient",
        line: elementLineNumber(domEl),
        selector: elementSelector(domEl),
        detail: `inline style="" contains CSS gradient`,
      });
    }
  });
  // (b) <style> blocks → any class rule containing gradient
  for (const [cName, props] of cls.entries()) {
    if (gradientRe.test(props)) {
      // Locate the first element on the page using this class as our report anchor.
      const anchor = $(`.${cName}`).get(0) as DomElement | undefined;
      const line = anchor ? elementLineNumber(anchor) : 1;
      const selector = anchor ? elementSelector(anchor) : `.${cName}`;
      out.push({
        rule: "rule2_gradient",
        line,
        selector,
        detail: `<style> rule for .${cName} contains CSS gradient`,
      });
    }
  }
  return out;
}

const BG_ON_TEXT_PROP_RE = /(background\s*:|background-color\s*:|border\s*:|border-color\s*:|box-shadow\s*:)/i;

function detect_rule3_bg_on_text(cls: Map<string, string>): RuleViolation[] {
  const out: RuleViolation[] = [];
  const textTags = ["p", "h1", "h2", "h3", "h4", "h5", "h6"];
  for (const tag of textTags) {
    $(tag).each((_, el) => {
      const domEl = el as DomElement;
      const inlineStyle = $(domEl).attr("style") ?? "";
      if (BG_ON_TEXT_PROP_RE.test(inlineStyle)) {
        out.push({
          rule: "rule3_bg_on_text",
          line: elementLineNumber(domEl),
          selector: elementSelector(domEl),
          detail: `<${tag}> inline style="" contains background/border/shadow`,
        });
        return;
      }
      // Class-applied via <style>: check each class on the element.
      const elementClasses = ($(domEl).attr("class") ?? "").split(/\s+/).filter(Boolean);
      for (const c of elementClasses) {
        const props = cls.get(c);
        if (props && BG_ON_TEXT_PROP_RE.test(props)) {
          out.push({
            rule: "rule3_bg_on_text",
            line: elementLineNumber(domEl),
            selector: elementSelector(domEl),
            detail: `<${tag} class="${c}"> applies background/border/shadow via <style> rule .${c}`,
          });
          return;
        }
      }
    });
  }
  return out;
}

function detect_rule4_div_bg_image(cls: Map<string, string>): RuleViolation[] {
  const out: RuleViolation[] = [];
  const bgImgRe = /background-image\s*:/i;
  $("div").each((_, el) => {
    const domEl = el as DomElement;
    const inlineStyle = $(domEl).attr("style") ?? "";
    if (bgImgRe.test(inlineStyle)) {
      out.push({
        rule: "rule4_div_bg_image",
        line: elementLineNumber(domEl),
        selector: elementSelector(domEl),
        detail: `<div> inline style="" contains background-image:`,
      });
      return;
    }
    const elementClasses = ($(domEl).attr("class") ?? "").split(/\s+/).filter(Boolean);
    for (const c of elementClasses) {
      const props = cls.get(c);
      if (props && bgImgRe.test(props)) {
        out.push({
          rule: "rule4_div_bg_image",
          line: elementLineNumber(domEl),
          selector: elementSelector(domEl),
          detail: `<div class="${c}"> applies background-image via <style> rule .${c}`,
        });
        return;
      }
    }
  });
  return out;
}

if (!isPpt) {
  console.log(
    `SKIP html2pptx pre-check rule1_div_text (mode=${isLongForm ? "long-form" : "non-ppt"})`
  );
  console.log(
    `SKIP html2pptx pre-check rule2_gradient (mode=${isLongForm ? "long-form" : "non-ppt"})`
  );
  console.log(
    `SKIP html2pptx pre-check rule3_bg_on_text (mode=${isLongForm ? "long-form" : "non-ppt"})`
  );
  console.log(
    `SKIP html2pptx pre-check rule4_div_bg_image (mode=${isLongForm ? "long-form" : "non-ppt"})`
  );
} else {
  const classProps = parseStyleBlocks(content);
  const detectors: Array<{ id: RuleId; fn: (m: Map<string, string>) => RuleViolation[] }> = [
    { id: "rule1_div_text", fn: detect_rule1_div_text },
    { id: "rule2_gradient", fn: detect_rule2_gradient },
    { id: "rule3_bg_on_text", fn: detect_rule3_bg_on_text },
    { id: "rule4_div_bg_image", fn: detect_rule4_div_bg_image },
  ];
  for (const { id, fn } of detectors) {
    const violations = fn(classProps);
    const level = HTML2PPTX_RULE_LEVELS[id];
    if (violations.length === 0) {
      console.log(`OK  html2pptx pre-check ${id}`);
      continue;
    }
    for (const v of violations) {
      const tag = level === "hard_fail" ? "FAIL" : "WARN";
      const msg = `${tag} html2pptx pre-check ${v.rule}: ${htmlFile}:${v.line} ${v.selector} — ${v.detail}`;
      console.log(msg);
      if (level !== "hard_fail") warnings.push(msg);
    }
    if (level === "hard_fail") fail = 1;
  }
}

// ── GATE-F: class prefix consistency (PPT mode only) ────────────────────────
if (!isPpt) {
  console.log(
    `SKIP GATE-F class-prefix (mode=${isLongForm ? "long-form" : "non-ppt"})`
  );
} else {
  // {project_root} via shared resolver (memoized).
  const projectRoot = resolveProjectRoot(htmlDir);
  const tokensPath = resolve(projectRoot, "tokens.css");

  // Read tokens.css preset comment (F-c source). Missing file or missing comment
  // is a warning, never a FAIL.
  let presetName: string | null = null;
  let presetWarning: string | null = null;
  if (existsSync(tokensPath)) {
    const tokensHead = readFileSync(tokensPath, "utf8").slice(0, 4096);
    const m = tokensHead.match(/\/\*\s*preset\s*:\s*([A-Za-z0-9_-]+)\s*\*\//);
    if (m) {
      presetName = m[1];
    } else {
      presetWarning = `tokens.css has no '/* preset: <name> */' header — F-c tie-break skipped`;
    }
  } else {
    presetWarning = `tokens.css not found at ${tokensPath} — F-c tie-break skipped`;
  }

  // v1.3 GATE-F prefix 白名單：
  //   STATIC_PREFIXES (invariant) ∪ {dynamic preset slug from tokens.css line 1}.
  //   Header malformed → 白名單退化為 STATIC_PREFIXES (Inv-4 of design.md).
  const STATIC_PREFIXES = ["kami", "google", "swiss"] as const;
  const dynamicSlug = presetName && /^[a-z][a-z0-9-]{1,15}$/.test(presetName)
    ? presetName
    : null;
  const allowedPrefixes = new Set<string>([...STATIC_PREFIXES, ...(dynamicSlug ? [dynamicSlug] : [])]);

  // Scan every `class="..."` occurrence line-by-line for file:line precision.
  const classAttr = /class\s*=\s*"([^"]*)"/gi;
  const seenPrefixes = new Set<string>();
  const prefixFirstSeen: Record<string, { line: number; token: string }> = {};
  const aFailures: string[] = []; // F-a (no-prefix-in-allowlist) failures
  let totalTokens = 0;

  lines.forEach((lineText, idx) => {
    const lineNo = idx + 1;
    classAttr.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = classAttr.exec(lineText)) !== null) {
      const tokens = m[1].split(/\s+/).filter((t) => t.length > 0);
      for (const tok of tokens) {
        totalTokens += 1;
        const dashIdx = tok.indexOf("-");
        const tokPrefix = dashIdx > 0 ? tok.substring(0, dashIdx) : null;
        if (tokPrefix && allowedPrefixes.has(tokPrefix)) {
          if (!seenPrefixes.has(tokPrefix)) {
            seenPrefixes.add(tokPrefix);
            prefixFirstSeen[tokPrefix] = { line: lineNo, token: tok };
          }
        } else {
          aFailures.push(
            `${htmlFile}:${lineNo} class token '${tok}' prefix not in whitelist {${[...allowedPrefixes].join(", ")}}`
          );
        }
      }
    }
  });

  let gateFailed = false;

  // F-a: prefix not in allowlist
  if (aFailures.length > 0) {
    for (const msg of aFailures) {
      console.log(
        `FAIL GATE-F class-prefix (F-a): ${msg} — 請重跑 \`/baransu:design preset <name>\``
      );
    }
    gateFailed = true;
  }

  // F-b: mixed prefixes in the same file
  if (seenPrefixes.size > 1) {
    const prefixList = [...seenPrefixes];
    const samples = prefixList
      .map((p) => `${prefixFirstSeen[p].line}:'${prefixFirstSeen[p].token}'`)
      .join(", ");
    console.log(
      `FAIL GATE-F class-prefix (F-b): ${htmlFile} mixed prefixes ${prefixList.join("/")} ` +
        `at ${samples} — 同檔需單一 prefix；請重跑 \`/baransu:design preset <name>\` 統一前綴`
    );
    gateFailed = true;
  }

  // F-c: tokens.css preset vs dominant prefix (only meaningful when exactly one prefix is present)
  let dominantPrefix: string | null = null;
  if (seenPrefixes.size === 1) {
    dominantPrefix = [...seenPrefixes][0];
  }

  if (presetWarning) {
    const msg = `WARN GATE-F class-prefix (F-c skipped): ${presetWarning}`;
    console.log(msg);
    warnings.push(msg);
  } else if (presetName && dominantPrefix && presetName !== dominantPrefix) {
    const first =
      prefixFirstSeen[dominantPrefix] ?? { line: 1, token: `${dominantPrefix}-*` };
    console.log(
      `FAIL GATE-F class-prefix (F-c): ${htmlFile}:${first.line} dominant prefix '${dominantPrefix}-' ` +
        `does not match tokens.css preset '${presetName}' (${tokensPath}) — ` +
        `請重跑 \`/baransu:design preset ${dominantPrefix}\``
    );
    gateFailed = true;
  }

  if (gateFailed) {
    fail = 1;
  } else if (totalTokens === 0) {
    // No class attributes at all in a PPT-shaped doc: treat as benign skip.
    console.log(`OK  GATE-F class-prefix (${htmlFile}, no class attributes found)`);
  } else if (dominantPrefix) {
    console.log(
      `OK  GATE-F class-prefix (${htmlFile}, ${dominantPrefix}- consistent, ` +
        `preset=${presetName ?? "n/a"})`
    );
  } else {
    // Reached only if seenPrefixes.size === 0 yet totalTokens > 0, which is
    // impossible given F-a would have caught it. Safe-guard fallthrough.
    console.log(
      `OK  GATE-F class-prefix (${htmlFile}, no prefixed classes, preset=${presetName ?? "n/a"})`
    );
  }
}

// ── GATE-G: data-layout set membership (PPT mode only) ─────────────────────
// Mode reuses GATE-F's `isPpt` detection. For each <section data-layout="X">,
// verify that {project_root}/slide-cores/X.html exists. Source of truth is the
// filesystem listing — the user must have run `/baransu:design preset <style>`
// to populate slide-cores/.
//   - Missing directory (ENOENT)         → SKIP + warning, exit 0
//   - Empty directory (no .html files)   → SKIP + warning, exit 0
//   - Unregistered layout                → FAIL (exit 1) with available set
//   - PASS                               → log current layout id set for debug
if (!isPpt) {
  console.log(`SKIP GATE-G layout-registered (mode=non-ppt)`);
} else {
  const projectRootG = resolveProjectRoot(htmlDir);
  const slideCoresDir = resolve(projectRootG, "slide-cores");

  // Extract the data-layout value set from the slide HTML via cheerio.
  const layoutValues = new Set<string>();
  $("section[data-layout]").each((_, el) => {
    const v = $(el).attr("data-layout");
    if (v) layoutValues.add(v);
  });

  let availableHtml: string[] = [];
  let dirState: "missing" | "empty" | "ok" = "ok";
  try {
    const entries = readdirSync(slideCoresDir);
    availableHtml = entries
      .filter((f) => f.toLowerCase().endsWith(".html"))
      .map((f) => f.replace(/\.html$/i, ""));
    if (availableHtml.length === 0) dirState = "empty";
  } catch (e) {
    const err = e as NodeJS.ErrnoException;
    if (err && err.code === "ENOENT") {
      dirState = "missing";
    } else {
      throw e;
    }
  }

  if (dirState === "missing") {
    const msg =
      `WARN GATE-G layout-registered: slide-cores/ not found at ${slideCoresDir} — ` +
      `請先跑 \`/baransu:design preset <style>\``;
    console.log(msg);
    warnings.push(msg);
    console.log(`SKIP GATE-G layout-registered (slide-cores/ missing)`);
  } else if (dirState === "empty") {
    const msg =
      `WARN GATE-G layout-registered: slide-cores/ at ${slideCoresDir} is empty (no .html) — ` +
      `slide-cores/ 為空，請重跑 preset`;
    console.log(msg);
    warnings.push(msg);
    console.log(`SKIP GATE-G layout-registered (slide-cores/ empty)`);
  } else {
    const available = new Set(availableHtml);
    const unregistered: string[] = [];
    for (const v of layoutValues) {
      if (!available.has(v)) unregistered.push(v);
    }
    if (unregistered.length === 0) {
      console.log(
        `OK  GATE-G layout-registered (${htmlFile}, layouts=[${[...layoutValues].sort().join(", ")}])`
      );
    } else {
      const availList = [...available].sort().join(", ");
      for (const v of unregistered) {
        console.log(
          `FAIL GATE-G layout-registered: data-layout="${v}" not in ${slideCoresDir}/; available: [${availList}]`
        );
      }
      fail = 1;
    }
  }
}

if (warnings.length > 0) {
  console.log(`SUMMARY warnings: ${warnings.length}`);
}
if (fail === 0) console.log(`GATE PASS: ${htmlFile}`);
process.exit(fail);
