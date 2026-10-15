#!/usr/bin/env node
// verify-page.mjs — screenshot a component (<slug>.html) or a diagram the way a reviewer sees it.
//
//   node verify-page.mjs <slug>.html [--out shots] [--selector "figure, .fig"] [--phone 400]
//
// For light and dark colour schemes: screenshots every element matching
// --selector (default: figures) and the full page; then a phone-width full page.
// Prints JSON: console errors, page errors, horizontal overflow, figure count.
// Exit 1 when the page errors or scrolls sideways at phone width — those are
// the two defects a reviewer never forgives.
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadPlaywright as findPlaywright, chromiumPath, launchChromium, INSTALL_HINT } from './browser.mjs';

const argv = process.argv.slice(2);
const file = argv.find((a) => !a.startsWith('--'));
const flag = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
if (!file) { console.error('usage: verify-page.mjs <slug>.html [--out shots] [--selector css] [--phone 400]'); process.exit(2); }
const HTML = path.resolve(file), OUT = path.resolve(flag('out', 'shots')), SEL = flag('selector', 'figure, .fig'), PHONE = Number(flag('phone', 400));
fs.mkdirSync(OUT, { recursive: true });

async function loadPlaywright() {
  const pw = await findPlaywright();
  if (!pw) { console.error(INSTALL_HINT); process.exit(2); }
  return pw;
}

const pw = await loadPlaywright();
const exe = chromiumPath();
const browser = await launchChromium(pw, { executablePath: exe });
const report = { file: HTML, schemes: {}, phone: {}, errors: [] };
try {
  for (const scheme of ['light', 'dark']) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, colorScheme: scheme, reducedMotion: 'reduce' });
    page.on('pageerror', (e) => report.errors.push(`${scheme}: ${e.message}`));
    page.on('console', (m) => { if (m.type() === 'error') report.errors.push(`${scheme} console: ${m.text()}`); });
    await page.goto(pathToFileURL(HTML).href, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts && document.fonts.ready);
    await page.waitForTimeout(600);
    const figs = page.locator(SEL);
    const count = await figs.count();
    for (let i = 0; i < count; i++) await figs.nth(i).screenshot({ path: path.join(OUT, `${scheme}-fig-${i + 1}.png`) });
    await page.screenshot({ path: path.join(OUT, `${scheme}-page.png`), fullPage: true });
    report.schemes[scheme] = { figures: count, hscroll: await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth) };
    await page.close();
  }
  const page = await browser.newPage({ viewport: { width: PHONE, height: 800 }, reducedMotion: 'reduce' });
  await page.goto(pathToFileURL(HTML).href);
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(OUT, 'phone-page.png'), fullPage: true });
  report.phone = { width: PHONE, hscroll: await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth) };
} finally {
  await browser.close();
}
console.log(JSON.stringify(report, null, 2));
process.exit(report.errors.length || report.phone.hscroll ? 1 : 0);
