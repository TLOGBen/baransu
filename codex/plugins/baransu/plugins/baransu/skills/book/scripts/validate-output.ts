#!/usr/bin/env -S npx tsx
/**
 * validate-output.ts — book skill HTML quality gate
 * Usage: npx tsx validate-output.ts <path-to-html-file>
 * Exit 0 = GATE PASS, Exit 1 = one or more checks failed, Exit 2 = usage error
 */
import { readFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const htmlFile = process.argv[2];
if (!htmlFile || !existsSync(htmlFile)) {
  console.error("Usage: npx tsx validate-output.ts <path-to-html-file>");
  process.exit(2);
}

const htmlDir = dirname(resolve(htmlFile));
const content = readFileSync(htmlFile, "utf8");
let fail = 0;

// (a) HTML parseable via Python
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

// (b) <main> or <article> structure present
if (/<(main|article)[^>]*>/i.test(content)) {
  console.log("OK  structure");
} else {
  console.log("FAIL structure: no <main> or <article> element found");
  fail = 1;
}

// (c) SVG tags balanced
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

// (d) Local asset paths exist
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

if (fail === 0) console.log(`GATE PASS: ${htmlFile}`);
process.exit(fail);
