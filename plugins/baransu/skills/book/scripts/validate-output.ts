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
 */
import { readFileSync, existsSync } from "node:fs";
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

if (fail === 0) console.log(`GATE PASS: ${htmlFile}`);
process.exit(fail);
