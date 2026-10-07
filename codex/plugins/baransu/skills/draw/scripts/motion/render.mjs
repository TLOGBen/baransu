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
//   node render.mjs stills  --html index.html --at 0,3.2,6.0              → out/stills.png (one tile per listed time)
//   node render.mjs animatic --html index.html --dur 15                   → out/animatic.mp4 (24 fps, no blur, half size: pacing only)
//   node render.mjs full    --html index.html --dur 15 [--fps 60 --sub 4 --audio mix.wav] → out/final.mp4
//   node render.mjs full    --html index.html --from 10 --to 20 [--keep]  → out/part-10.00-20.00.mp4 (a chunk; concat with ffmpeg -f concat)
//   node render.mjs full    --html index.html --format 1:1 | --all        → one format (?f= passed to the page) or all three from one timeline
//
// Common flags: --out DIR (default out), --w/--h viewport (default 1080×1920),
// --format 9:16|1:1|16:9 (sets the viewport and opens the page with ?f=<format> so its layout reflows),
// --all (full/animatic/contact/phone/stills: every format, output suffixed -9x16 / -1x1 / -16x9),
// --safe (contact/phone/stills/beats: draw the format's safe area on every tile — nothing readable may sit outside it),
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

if (!opt.html) die('usage: render.mjs <still|stills|beats|contact|strip|phone|hash|animatic|full> --html index.html [flags]');
const HTML = path.resolve(opt.html);
if (!fs.existsSync(HTML)) die(`html not found: ${HTML}`);
const OUT = path.resolve(opt.out || 'out');
const FORMATS = { '9:16': [1080, 1920], '1:1': [1440, 1440], '16:9': [1920, 1080] };
if (opt.format && !FORMATS[opt.format]) die(`unknown --format ${opt.format}; use 9:16, 1:1 or 16:9`);
let FORMAT = opt.format;
let W = num('w', FORMAT ? FORMATS[FORMAT][0] : 1080), H = num('h', FORMAT ? FORMATS[FORMAT][1] : 1920);
const SCALE = mode === 'animatic' ? num('scale', 0.5) : num('scale', 1);
const FPS = mode === 'animatic' ? num('fps', 24) : num('fps', 60), SUB = mode === 'animatic' ? 1 : num('sub', 4);
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
  const url = pathToFileURL(HTML).href + (FORMAT ? `?f=${encodeURIComponent(FORMAT)}` : '');
  await page.goto(url, { waitUntil: 'networkidle' }); // web fonts and any linked assets are in before the first frame
  await page.evaluate(() => document.fonts && document.fonts.ready);
  const ok = await page.evaluate(() => typeof window.seek === 'function');
  if (!ok) die('page does not define window.seek(t)');
  // Warm up. A canvas only requests a web font the first time `ctx.font` names that
  // face/weight, and fonts.ready does not know about those: the first frame that uses a
  // weight draws its fallback. Sweep the whole timeline once (no screenshots) so every
  // glyph the film draws has asked for its font, then wait for the fonts again and let the
  // first paint settle; one discarded screenshot keeps the first measured frame honest.
  const sweepDur = num('dur', await page.evaluate(() => (typeof window.timeline === 'function' ? window.timeline().duration : window.DUR) || 10));
  await page.evaluate(async (d) => { for (let t = 0; t <= d; t += 0.25) await window.seek(t); }, sweepDur);
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.evaluate(() => window.seek(0));
  await (await target(page)).screenshot({ type: 'png', animations: 'disabled' });
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

// The platform's own UI covers these margins (9:16: caption + action bar); --safe draws them on every tile.
function safeArea() {
  const vertical = FORMAT ? FORMAT === '9:16' : H > W * 1.5;
  return vertical ? { top: 220, bottom: 340, left: 60, right: 120 } : { top: H * 0.05, bottom: H * 0.05, left: W * 0.05, right: W * 0.05 };
}

async function tile(frames, dir, outFile, { scale = 270, cols = 6 }) {
  const rows = Math.max(1, Math.ceil(frames / cols));
  const s = safeArea(), k = SCALE;
  const safe = opt.safe ? `drawbox=x=${Math.round(s.left * k)}:y=${Math.round(s.top * k)}:w=${Math.round((W - s.left - s.right) * k)}:h=${Math.round((H - s.top - s.bottom) * k)}:color=red@0.7:t=6,` : '';
  await run('ffmpeg', ['-v', 'error', '-y', '-framerate', '1', '-i', path.join(dir, '%04d.png'),
    '-vf', `${safe}scale=${scale}:-1,tile=${cols}x${rows}`, '-frames:v', '1', outFile]);
  console.log(`wrote ${outFile} (${frames} frames)`);
}

// contact / phone / stills: a sheet to look at; `suffix` names the format under --all.
async function renderSheet(page, suffix = '') {
  const d = tmp();
  if (mode === 'stills') {
    const times = String(opt.at || '0').split(',').map(Number).filter(Number.isFinite);
    if (!times.length) die('stills mode needs --at t1,t2,...');
    await framesTo(page, times, d);
    await tile(times.length, d, path.join(OUT, `stills${suffix}.png`), { scale: 320, cols: Math.min(times.length, 6) });
  } else {
    const { duration } = await timeline(page);
    const per = num('per', mode === 'phone' ? 1 : 2);
    const times = []; for (let t = 0; t < duration; t += 1 / per) times.push(t);
    await framesTo(page, times, d);
    await tile(times.length, d, path.join(OUT, `${mode}${suffix}.png`), mode === 'phone' ? { scale: 360, cols: 5 } : { scale: 270, cols: 6 });
  }
  fs.rmSync(d, { recursive: true, force: true });
}

async function framesTo(page, times, dir) {
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  for (let i = 0; i < times.length; i++) {
    fs.writeFileSync(path.join(dir, `${String(i).padStart(4, '0')}.png`), await shot(page, times[i]));
  }
}

const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'draw-render-'));

// full / animatic: every frame (or the --from/--to chunk) through subframes, tmix and libx264.
async function renderFull(browser, page) {
  const { duration } = await timeline(page);
  const from = num('from', 0), to = Math.min(num('to', duration), duration);
  if (!(to > from)) die(`empty range --from ${from} --to ${to}`);
  const first = Math.round(from * FPS * SUB), total = Math.round(to * FPS * SUB);
  const workers = Math.max(1, num('workers', 1));
  const pages = [page];
  for (let i = 1; i < workers; i++) pages.push(await openPage(browser));
  const d = opt.keep ? path.join(OUT, `frames-${from.toFixed(2)}-${to.toFixed(2)}`) : tmp();
  fs.mkdirSync(d, { recursive: true });
  let done = 0;
  await Promise.all(pages.map(async (p, w) => {
    for (let i = first + w; i < total; i += workers) {
      // subframes centred on each output frame: the shutter spans one full frame
      const t = (i - (SUB - 1) / 2) / (FPS * SUB);
      fs.writeFileSync(path.join(d, `${String(i - first).padStart(6, '0')}.png`), await shot(p, Math.max(0, t)));
      if (++done % (FPS * SUB) === 0) console.log(`rendered ${(from + done / (FPS * SUB)).toFixed(0)}s / ${to}s`);
    }
  }));
  const audio = opt.audio && !opt.from && !opt.to ? path.resolve(opt.audio) : null; // chunks get audio at concat time
  const chunk = opt.from !== undefined || opt.to !== undefined;
  const base = mode === 'animatic' ? 'animatic' : chunk ? `part-${from.toFixed(2)}-${to.toFixed(2)}` : 'final';
  const outFile = path.join(OUT, opt.name || `${base}${FORMAT && opt.all ? '-' + FORMAT.replace(':', 'x') : ''}.mp4`);
  const vf = SUB > 1 ? `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/(${FPS}*TB)` : `setpts=N/(${FPS}*TB)`;
  await run('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS * SUB), '-i', path.join(d, '%06d.png'),
    ...(audio ? ['-i', audio] : []),
    '-vf', vf, '-r', String(FPS), '-c:v', 'libx264', '-preset', opt.preset || 'medium', '-crf', String(num('crf', mode === 'animatic' ? 23 : 16)), '-pix_fmt', 'yuv420p',
    ...(audio ? ['-c:a', 'aac', '-b:a', '256k', '-shortest'] : []),
    '-movflags', '+faststart', outFile]);
  if (opt.keep) console.log(`kept frames in ${d}`); else fs.rmSync(d, { recursive: true, force: true });
  console.log(`wrote ${outFile}`);
  if (chunk) console.log('join chunks: printf "file \'%s\'\\n" out/part-*.mp4 > out/parts.txt && ffmpeg -f concat -safe 0 -i out/parts.txt -i out/mix.wav -c:v copy -c:a aac -shortest out/final.mp4');
}

async function main() {
  if (!haveFfmpeg() && mode !== 'still' && mode !== 'hash') die('ffmpeg not found on PATH');
  const pw = await loadPlaywright();
  const exe = chromiumPath();
  const browser = await pw.chromium.launch(exe ? { executablePath: exe } : {});
  try {
    if (opt.all && ['full', 'animatic', 'contact', 'phone', 'stills'].includes(mode)) {
      // every format from the one timeline: the page reflows on ?f=, the viewport follows;
      // a sheet per format, because "reflow, never crop" is only checkable by looking at the reflow
      for (const f of Object.keys(FORMATS)) {
        FORMAT = f; [W, H] = FORMATS[f];
        const page = await openPage(browser);
        if (mode === 'full' || mode === 'animatic') await renderFull(browser, page);
        else await renderSheet(page, '-' + f.replace(':', 'x'));
        await page.close();
      }
      return;
    }
    const page = await openPage(browser);
    if (mode === 'still') {
      const t = num('t', 0);
      const f = path.join(OUT, `still-${t.toFixed(2)}.png`);
      fs.writeFileSync(f, await shot(page, t));
      console.log(`wrote ${f}`);
    } else if (mode === 'hash') {
      const t = num('t', 0);
      const pa = await shot(page, t);
      await page.evaluate((tt) => window.seek(tt + 1), t); // disturb, then come back
      const pb = await shot(page, t);
      const a = createHash('md5').update(pa).digest('hex'), b = createHash('md5').update(pb).digest('hex');
      let verdict = a === b ? 'DETERMINISTIC' : 'NOT DETERMINISTIC — frame depends on history';
      let ok = a === b;
      if (!ok && haveFfmpeg()) {
        // SVG/DOM frames can differ by a few anti-aliased pixels after an element toggles
        // visibility (rasterizer cache), without any history in the page. Decode both and
        // measure: ≥ 80 dB PSNR is sub-visible noise, not a state leak.
        const d = tmp();
        fs.writeFileSync(path.join(d, 'a.png'), pa); fs.writeFileSync(path.join(d, 'b.png'), pb);
        const r = spawnSync('ffmpeg', ['-v', 'info', '-i', path.join(d, 'a.png'), '-i', path.join(d, 'b.png'), '-filter_complex', 'psnr', '-f', 'null', '-'], { encoding: 'utf8' });
        const m = /average:([\d.]+|inf)/.exec(r.stderr || '');
        const psnr = m ? (m[1] === 'inf' ? Infinity : Number(m[1])) : NaN;
        fs.rmSync(d, { recursive: true, force: true });
        if (psnr >= 80) { ok = true; verdict = `DETERMINISTIC (raster noise only, PSNR ${psnr.toFixed(1)} dB)`; }
        else if (Number.isFinite(psnr)) verdict += ` (PSNR ${psnr.toFixed(1)} dB)`;
      }
      console.log(`${a}\n${b}\n${verdict}`);
      process.exitCode = ok ? 0 : 1;
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
    } else if (mode === 'contact' || mode === 'phone' || mode === 'stills') {
      await renderSheet(page);
    } else if (mode === 'strip') {
      const t = num('t', 0), n = num('n', 12);
      const times = []; for (let i = 0; i < n; i++) times.push(t + i / FPS);
      const d = tmp();
      await framesTo(page, times, d);
      await tile(n, d, path.join(OUT, 'strip.png'), { scale: 320, cols: n });
    } else if (mode === 'full' || mode === 'animatic') {
      await renderFull(browser, page);
    } else {
      die(`unknown mode: ${mode}`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
