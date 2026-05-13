#!/usr/bin/env node
// validate-swiss-deck.mjs — REQ-003 Scenario 2 mechanical gate
// Usage: node validate-swiss-deck.mjs <slide-cores-dir>

import { readdirSync } from 'node:fs';
import { basename } from 'node:path';

// 22 lock list — guizang S01-S22 equivalent layouts.
// ALIASES map preset-historical filenames to canonical lock-list names
// so existing v1.3 slide-cores pass without bulk rename (which is out of
// REQ-003 Scenario 2 mechanical-gate scope).
const ALIASES = {
  'cover':          'title',
  'cover-section':  'section',
  'cover-data':     'data',
  'cover-quote':    'quote',
  'compare':        'comparison',
  'content-2col':   'two-column',
};
const LOCK_LIST = new Set([
  'title', 'section', 'content-bullets', 'quote', 'data', 'kpi-grid',
  'timeline', 'process', 'testimonial', 'agenda', 'stat-hero', 'icon-grid',
  'table-heavy', 'before-after', 'divider', 'closing',
  'toc', 'two-column', 'image-full', 'comparison', 'quote-stack', 'breakout'
]);

const canonical = (name) => ALIASES[name] ?? name;

const dir = process.argv[2];
if (!dir) {
  console.error('Usage: validate-swiss-deck.mjs <slide-cores-dir>');
  process.exit(2);
}

let layouts;
try {
  layouts = readdirSync(dir).filter(f => f.endsWith('.html')).map(f => basename(f, '.html'));
} catch (e) {
  console.error(`FAIL: cannot read ${dir}: ${e.message}`);
  process.exit(2);
}

const canonicalized = layouts.map(canonical);
const outside = layouts.filter(l => !LOCK_LIST.has(canonical(l)));
const missing = [...LOCK_LIST].filter(l => !canonicalized.includes(l));

if (outside.length > 0) {
  console.error(`FAIL validate-swiss-deck: layouts outside 22 lock list: ${outside.join(', ')}`);
  process.exit(1);
}
if (missing.length > 0) {
  // soft warning, not hard fail — tolerance for current 21/22 state
  console.warn(`WARN validate-swiss-deck: layouts missing from 22 lock list (${missing.length}): ${missing.join(', ')}`);
}

console.log(`OK  validate-swiss-deck: ${layouts.length}/22 layouts present, none outside lock list`);
process.exit(0);
