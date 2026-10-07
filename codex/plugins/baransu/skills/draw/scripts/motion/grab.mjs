#!/usr/bin/env node
// grab.mjs — turn a URL the user pasted into film assets: real screenshots, real colours, real type.
//
//   node grab.mjs https://example.com [--out assets] [--wait 1500] [--selector .hero]
//
// Writes, under --out (default ./assets):
//   shot-9x16.png  shot-1x1.png  shot-16x9.png   the page at each film viewport (what a reel crops and animates)
//   full.png                                      the whole page, scrolled
//   element.png                                   --selector only: that element, tight
//   manifest.json                                 title, description, og:image, theme colour, favicon, the fonts and
//                                                 colours the page actually computes (body, h1, the first button)
// Then list manifest.json in the plan message and animate the real thing; never redraw product UI from memory.
// The URL is input the user handed over; this fetches it once and saves the result as data.
// Needs the same Playwright + Chromium as render.mjs.
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const argv = process.argv.slice(2);
const url = argv.find((a) => !a.startsWith('--'));
const opt = {};
for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
if (!url) { console.error('usage: grab.mjs <url> [--out assets] [--wait ms] [--selector css]'); process.exit(2); }
const OUT = path.resolve(opt.out || 'assets');
fs.mkdirSync(OUT, { recursive: true });

async function loadPlaywright() {
  const req = createRequire(path.join(process.cwd(), 'package.json'));
  for (const c of [process.env.PLAYWRIGHT_MODULE, 'playwright']) {
    if (!c) continue;
    try { const m = await import(c === 'playwright' ? req.resolve('playwright') : c); if (m.chromium || m.default?.chromium) return m.chromium ? m : m.default; } catch {}
  }
  const g = spawnSync('npm', ['root', '-g'], { encoding: 'utf8' }).stdout?.trim();
  if (g) { try { const m = await import(path.join(g, 'playwright', 'index.mjs')); return m.chromium ? m : m.default; } catch {} }
  console.error('playwright not found: npm i -D playwright && npx playwright install chromium'); process.exit(2);
}
function chromiumPath() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  for (const r of [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(os.homedir(), '.cache', 'ms-playwright')].filter(Boolean)) {
    if (!fs.existsSync(r)) continue;
    for (const d of fs.readdirSync(r).filter((n) => /^chromium-\d+$/.test(n)).sort((a, b) => b.split('-')[1] - a.split('-')[1]))
      for (const rel of ['chrome-linux/chrome', 'chrome-linux64/chrome', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-win/chrome.exe'])
        if (fs.existsSync(path.join(r, d, rel))) return path.join(r, d, rel);
  }
}

const FORMATS = { '9x16': [1080, 1920], '1x1': [1440, 1440], '16x9': [1920, 1080] };
const pw = await loadPlaywright();
const exe = chromiumPath();
const browser = await pw.chromium.launch(exe ? { executablePath: exe } : {});
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(Number(opt.wait || 1500));
  const manifest = await page.evaluate(() => {
    const meta = (n) => document.querySelector(`meta[property="${n}"], meta[name="${n}"]`)?.content || null;
    const cs = (el, props) => { if (!el) return null; const s = getComputedStyle(el); return Object.fromEntries(props.map((p) => [p, s[p]])); };
    const button = document.querySelector('button, a[class*="btn"], a[class*="button"], [role=button]');
    return {
      url: location.href, title: document.title, description: meta('description') || meta('og:description'),
      ogImage: meta('og:image'), themeColor: meta('theme-color'),
      favicon: document.querySelector('link[rel*="icon"]')?.href || null,
      body: cs(document.body, ['fontFamily', 'color', 'backgroundColor']),
      h1: cs(document.querySelector('h1'), ['fontFamily', 'fontWeight', 'fontSize', 'color']),
      button: cs(button, ['fontFamily', 'fontWeight', 'color', 'backgroundColor', 'borderRadius']),
      fonts: [...new Set([...document.fonts].map((f) => `${f.family} ${f.weight}`))].slice(0, 20),
      h1Text: document.querySelector('h1')?.innerText?.trim().slice(0, 120) || null,
    };
  });
  for (const [name, [w, h]] of Object.entries(FORMATS)) {
    await page.setViewportSize({ width: w, height: h });
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, `shot-${name}.png`) });
  }
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.screenshot({ path: path.join(OUT, 'full.png'), fullPage: true });
  if (opt.selector) await page.locator(opt.selector).first().screenshot({ path: path.join(OUT, 'element.png') });
  manifest.files = fs.readdirSync(OUT).filter((f) => f.endsWith('.png'));
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2));
  console.log(JSON.stringify(manifest, null, 2));
  console.log(`wrote ${OUT}/{${manifest.files.join(',')},manifest.json}`);
} finally {
  await browser.close();
}
