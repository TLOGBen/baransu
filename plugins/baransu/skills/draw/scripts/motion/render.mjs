#!/usr/bin/env node
// render.mjs — drive a seek(t) page through headless Chromium and ffmpeg.
//
// The page must expose `window.seek(t)` that paints the frame for time t and
// returns synchronously (or a promise). Optionally `window.timeline()` returns
// `{ duration, cues: [{t, type}] }`; cues are written to out/cues.json for sfx.mjs.
//
//   node render.mjs still   --html index.html --t 3.2                 → out/still-3.20.png
//   node render.mjs beats   --html index.html --beats beats.json      → out/beats.png (one frame per beat)
//   node render.mjs contact --html index.html --dur 15 [--per 2]      → out/contact.png (2 frames/s, 6 across)
//   node render.mjs strip   --html index.html --t 4.2 [--n 12]        → out/strip.png (n consecutive frames)
//   node render.mjs phone   --html index.html --dur 15                → out/phone.png (360px wide tiles)
//   node render.mjs hash    --html index.html --t 5                   → prints two md5s; they must match
//   node render.mjs full    --html index.html --dur 15 [--fps 60 --sub 4 --audio mix.wav] → out/final.mp4
//
// Common flags: --out DIR (default out), --w/--h viewport (default 1080×1920),
// --selector CSS (element to screenshot, default the <canvas> or #stage or body),
// --scale deviceScaleFactor (default 1), --workers N (full mode page workers).
//
// Needs: Node 18+, ffmpeg on PATH, the `playwright` package (local, global, or
// $PLAYWRIGHT_MODULE) and a Chromium it can launch (PLAYWRIGHT_BROWSERS_PATH /
// CHROME_PATH honoured). Fails loudly when any of these is missing.
import { createRequire } from 'node:module';
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const argv = process.argv.slice(2);
const mode = argv[0] && !argv[0].startsWith('--') ? argv[0] : 'contact';
const opt = {};
for (let i = mode === argv[0] ? 1 : 0; i < argv.length; i++) {
  const a = argv[i];
  if (!a.startsWith('--')) continue;
  const k = a.slice(2);
  const v = argv[i + 1] !== undefined && !argv[i + 1].startsWith('--') ? argv[++i] : true;
  opt[k] = v;
}
const num = (k, d) => (opt[k] !== undefined ? Number(opt[k]) : d);

if (!opt.html) die('usage: render.mjs <still|beats|contact|strip|phone|hash|full> --html index.html [flags]');
const HTML = path.resolve(opt.html);
if (!fs.existsSync(HTML)) die(`html not found: ${HTML}`);
const OUT = path.resolve(opt.out || 'out');
const W = num('w', 1080), H = num('h', 1920), SCALE = num('scale', 1);
const FPS = num('fps', 60), SUB = num('sub', 4);
fs.mkdirSync(OUT, { recursive: true });

function die(msg) { console.error(msg); process.exit(2); }

function haveFfmpeg() { return spawnSync('ffmpeg', ['-version'], { stdio: 'ignore' }).status === 0; }

async function loadPlaywright() {
  const candidates = [opt.playwright, process.env.PLAYWRIGHT_MODULE, 'playwright'];
  const req = createRequire(path.join(process.cwd(), 'package.json'));
  for (const c of candidates) {
    if (!c) continue;
    try { const m = await import(c === 'playwright' ? req.resolve('playwright') : c); if (m.chromium || m.default?.chromium) return m.chromium ? m : m.default; } catch {}
  }
  const g = spawnSync('npm', ['root', '-g'], { encoding: 'utf8' }).stdout?.trim();
  if (g) { try { const m = await import(path.join(g, 'playwright', 'index.mjs')); return m.chromium ? m : m.default; } catch {} }
  die('playwright not found: npm i -D playwright && npx playwright install chromium');
}

function chromiumPath() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  const roots = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(os.homedir(), '.cache', 'ms-playwright')].filter(Boolean);
  for (const r of roots) {
    if (!fs.existsSync(r)) continue;
    const dirs = fs.readdirSync(r).filter((n) => /^chromium-\d+$/.test(n)).sort((a, b) => b.split('-')[1] - a.split('-')[1]);
    for (const d of dirs) {
      for (const rel of ['chrome-linux/chrome', 'chrome-linux64/chrome', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-win/chrome.exe']) {
        const p = path.join(r, d, rel);
        if (fs.existsSync(p)) return p;
      }
    }
  }
  return undefined; // let playwright use its own default
}

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: SCALE });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  page.on('console', (m) => { if (m.type() === 'error') console.error('[console]', m.text()); });
  await page.addInitScript(() => { window.__RENDER__ = true; });
  await page.goto(pathToFileURL(HTML).href);
  await page.evaluate(() => document.fonts && document.fonts.ready);
  const ok = await page.evaluate(() => typeof window.seek === 'function');
  if (!ok) die('page does not define window.seek(t)');
  return page;
}

async function target(page) {
  if (opt.selector) return page.locator(opt.selector).first();
  for (const sel of ['#stage', 'canvas', 'body']) {
    if (await page.locator(sel).count()) return page.locator(sel).first();
  }
  return page.locator('body');
}

async function shot(page, t) {
  await page.evaluate((tt) => window.seek(tt), t);
  return (await target(page)).screenshot({ type: 'png', animations: 'disabled' });
}

async function timeline(page) {
  const tl = await page.evaluate(() => (typeof window.timeline === 'function' ? window.timeline() : null));
  const duration = num('dur', tl?.duration ?? (await page.evaluate(() => window.DUR)) ?? NaN);
  if (!Number.isFinite(duration)) die('duration unknown: pass --dur or define window.timeline()/window.DUR');
  if (tl?.cues) fs.writeFileSync(path.join(OUT, 'cues.json'), JSON.stringify({ duration, cues: tl.cues }, null, 2));
  return { duration, cues: tl?.cues ?? [] };
}

function run(cmd, args) {
  return new Promise((res, rej) => {
    const p = spawn(cmd, args, { stdio: 'inherit' });
    p.on('exit', (c) => (c === 0 ? res() : rej(new Error(`${cmd} exited ${c}`))));
  });
}

async function tile(frames, dir, outFile, { scale = 270, cols = 6 }) {
  const rows = Math.max(1, Math.ceil(frames / cols));
  await run('ffmpeg', ['-v', 'error', '-y', '-framerate', '1', '-i', path.join(dir, '%04d.png'),
    '-vf', `scale=${scale}:-1,tile=${cols}x${rows}`, '-frames:v', '1', outFile]);
  console.log(`wrote ${outFile} (${frames} frames)`);
}

async function framesTo(page, times, dir) {
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  for (let i = 0; i < times.length; i++) {
    fs.writeFileSync(path.join(dir, `${String(i).padStart(4, '0')}.png`), await shot(page, times[i]));
  }
}

const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'draw-render-'));

async function main() {
  if (!haveFfmpeg() && mode !== 'still' && mode !== 'hash') die('ffmpeg not found on PATH');
  const pw = await loadPlaywright();
  const exe = chromiumPath();
  const browser = await pw.chromium.launch(exe ? { executablePath: exe } : {});
  try {
    const page = await openPage(browser);
    if (mode === 'still') {
      const t = num('t', 0);
      const f = path.join(OUT, `still-${t.toFixed(2)}.png`);
      fs.writeFileSync(f, await shot(page, t));
      console.log(`wrote ${f}`);
    } else if (mode === 'hash') {
      const t = num('t', 0);
      const a = createHash('md5').update(await shot(page, t)).digest('hex');
      await page.evaluate((tt) => window.seek(tt + 1), t); // disturb, then come back
      const b = createHash('md5').update(await shot(page, t)).digest('hex');
      console.log(`${a}\n${b}\n${a === b ? 'DETERMINISTIC' : 'NOT DETERMINISTIC — frame depends on history'}`);
      process.exitCode = a === b ? 0 : 1;
    } else if (mode === 'beats') {
      let beats;
      if (opt.beats) beats = JSON.parse(fs.readFileSync(path.resolve(opt.beats), 'utf8')).beats;
      else if (opt.bpm) { const { duration } = await timeline(page); beats = []; for (let b = 0; b < duration; b += 60 / num('bpm', 120)) beats.push(b); }
      else die('beats mode needs --beats beats.json or --bpm N');
      const offset = num('offset', 0.7); // sample late in the beat so the state has settled
      const beat = beats[1] - beats[0];
      const d = tmp();
      await framesTo(page, beats.map((b) => b + offset * beat), d);
      await tile(beats.length, d, path.join(OUT, 'beats.png'), { scale: 270, cols: num('cols', 8) });
    } else if (mode === 'contact' || mode === 'phone') {
      const { duration } = await timeline(page);
      const per = num('per', mode === 'phone' ? 1 : 2);
      const times = []; for (let t = 0; t < duration; t += 1 / per) times.push(t);
      const d = tmp();
      await framesTo(page, times, d);
      await tile(times.length, d, path.join(OUT, `${mode}.png`), mode === 'phone' ? { scale: 360, cols: 5 } : { scale: 270, cols: 6 });
    } else if (mode === 'strip') {
      const t = num('t', 0), n = num('n', 12);
      const times = []; for (let i = 0; i < n; i++) times.push(t + i / FPS);
      const d = tmp();
      await framesTo(page, times, d);
      await tile(n, d, path.join(OUT, 'strip.png'), { scale: 320, cols: n });
    } else if (mode === 'full') {
      const { duration } = await timeline(page);
      const total = Math.round(duration * FPS * SUB);
      const workers = Math.max(1, num('workers', 1));
      const pages = [page];
      for (let i = 1; i < workers; i++) pages.push(await openPage(browser));
      const d = tmp();
      let done = 0;
      await Promise.all(pages.map(async (p, w) => {
        for (let i = w; i < total; i += workers) {
          // subframes centred on each output frame: the shutter spans one full frame
          const t = (i - (SUB - 1) / 2) / (FPS * SUB);
          fs.writeFileSync(path.join(d, `${String(i).padStart(6, '0')}.png`), await shot(p, Math.max(0, t)));
          if (++done % (FPS * SUB) === 0) console.log(`rendered ${(done / (FPS * SUB)).toFixed(0)}s / ${duration}s`);
        }
      }));
      const audio = opt.audio ? path.resolve(opt.audio) : null;
      const outFile = path.join(OUT, opt.name || 'final.mp4');
      const vf = SUB > 1 ? `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/(${FPS}*TB)` : `setpts=N/(${FPS}*TB)`;
      await run('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS * SUB), '-i', path.join(d, '%06d.png'),
        ...(audio ? ['-i', audio] : []),
        '-vf', vf, '-r', String(FPS), '-c:v', 'libx264', '-preset', opt.preset || 'medium', '-crf', String(num('crf', 16)), '-pix_fmt', 'yuv420p',
        ...(audio ? ['-c:a', 'aac', '-b:a', '256k', '-shortest'] : []),
        '-movflags', '+faststart', outFile]);
      fs.rmSync(d, { recursive: true, force: true });
      console.log(`wrote ${outFile}`);
    } else {
      die(`unknown mode: ${mode}`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
