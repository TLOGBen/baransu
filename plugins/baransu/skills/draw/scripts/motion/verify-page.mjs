#!/usr/bin/env node
// verify-page.mjs — screenshot an explainer page the way a reviewer sees it.
//
//   node verify-page.mjs page.html [--out shots] [--selector "figure, .fig"] [--phone 400]
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

const argv = process.argv.slice(2);
const file = argv.find((a) => !a.startsWith('--'));
const flag = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
if (!file) { console.error('usage: verify-page.mjs page.html [--out shots] [--selector css] [--phone 400]'); process.exit(2); }
const HTML = path.resolve(file), OUT = path.resolve(flag('out', 'shots')), SEL = flag('selector', 'figure, .fig'), PHONE = Number(flag('phone', 400));
fs.mkdirSync(OUT, { recursive: true });

async function loadPlaywright() {
  const req = createRequire(path.join(process.cwd(), 'package.json'));
  for (const c of [process.env.PLAYWRIGHT_MODULE, 'playwright']) {
    if (!c) continue;
    try { const m = await import(c === 'playwright' ? req.resolve('playwright') : c); if (m.chromium || m.default?.chromium) return m.chromium ? m : m.default; } catch {}
  }
  const g = spawnSync('npm', ['root', '-g'], { encoding: 'utf8' }).stdout?.trim();
  if (g) { try { const m = await import(path.join(g, 'playwright', 'index.mjs')); return m.chromium ? m : m.default; } catch {} }
  console.error('playwright not found'); process.exit(2);
}
function chromiumPath() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  for (const r of [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(os.homedir(), '.cache', 'ms-playwright')].filter(Boolean)) {
    if (!fs.existsSync(r)) continue;
    for (const d of fs.readdirSync(r).filter((n) => /^chromium-\d+$/.test(n)).sort((a, b) => b.split('-')[1] - a.split('-')[1])) {
      for (const rel of ['chrome-linux/chrome', 'chrome-linux64/chrome', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-win/chrome.exe']) {
        const p = path.join(r, d, rel); if (fs.existsSync(p)) return p;
      }
    }
  }
  return undefined;
}

const pw = await loadPlaywright();
const exe = chromiumPath();
const browser = await pw.chromium.launch(exe ? { executablePath: exe } : {});
const report = { file: HTML, schemes: {}, phone: {}, errors: [] };
try {
  for (const scheme of ['light', 'dark']) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, colorScheme: scheme, reducedMotion: 'reduce' });
    page.on('pageerror', (e) => report.errors.push(`${scheme}: ${e.message}`));
    page.on('console', (m) => { if (m.type() === 'error') report.errors.push(`${scheme} console: ${m.text()}`); });
    await page.goto(pathToFileURL(HTML).href);
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
