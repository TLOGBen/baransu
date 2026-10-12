#!/usr/bin/env node
// doctor.mjs — preflight before any motion, page or map work: the route with the fewest surprises.
//
//   node scripts/motion/doctor.mjs            check everything, print the fix for each miss, exit 0 only when READY
//   node scripts/motion/doctor.mjs --install  also run the official install command for each miss, then check again
//
// Checks, in order: Node ≥ 18, ffmpeg + ffprobe, Playwright, a Chromium it can launch, Python 3 (and the
// UTF-8 mode Windows needs), then a smoke test that exercises the real chain: open seek-template.html in
// headless Chromium, render the same frame twice and compare hashes (determinism), encode two frames
// with ffmpeg. A READY here means render.mjs, verify-page.mjs and grab.mjs will run.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadPlaywright, chromiumPath } from './browser.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ASSETS = path.join(HERE, '..', '..', 'assets', 'motion');
const WIN = process.platform === 'win32', MAC = process.platform === 'darwin';
const INSTALL = process.argv.includes('--install');
// Executables run without a shell; only a whole command line (npm, npx, winget) goes through one.
const run = (cmd, args) => spawnSync(cmd, args, { encoding: 'utf8', timeout: 600000 });
const ok = (cmd, args = ['--version']) => run(cmd, args).status === 0;

const FIX = {
  node: WIN ? 'winget install --id OpenJS.NodeJS.LTS -e' : MAC ? 'brew install node' : 'sudo apt-get install -y nodejs npm',
  ffmpeg: WIN ? 'winget install --id Gyan.FFmpeg -e' : MAC ? 'brew install ffmpeg' : 'sudo apt-get install -y ffmpeg',
  playwright: 'npm i -g playwright',
  chromium: WIN || MAC ? 'npx playwright install chromium' : 'npx playwright install --with-deps chromium',
  python: WIN ? 'winget install --id Python.Python.3.12 -e' : MAC ? 'brew install python' : 'sudo apt-get install -y python3',
};

async function check() {
  const rows = [];
  const add = (name, pass, detail, fix) => rows.push({ name, pass, detail, fix });

  const major = Number(process.versions.node.split('.')[0]);
  add('node', major >= 18, `v${process.versions.node}`, major >= 18 ? '' : FIX.node);

  const ff = ok('ffmpeg', ['-version']) && ok('ffprobe', ['-version']);
  add('ffmpeg', ff, ff ? run('ffmpeg', ['-version']).stdout.split('\n')[0].slice(0, 60) : 'not on PATH', ff ? '' : FIX.ffmpeg + (WIN ? '   (then open a new terminal)' : ''));

  const pw = await loadPlaywright();
  add('playwright', !!pw, pw ? 'found' : 'not found', pw ? '' : FIX.playwright + ' && ' + FIX.chromium);

  const exe = chromiumPath();
  add('chromium', !!exe || !!pw, exe ? exe : pw ? "playwright's default build" : 'not found', exe ? '' : FIX.chromium);

  const py = ['python3', 'python'].find((c) => ok(c, ['--version']));
  add('python', !!py, py ? run(py, ['--version']).stdout.trim() || run(py, ['--version']).stderr.trim() : 'not found', py ? '' : FIX.python);
  if (WIN) {
    const utf8 = process.env.PYTHONUTF8 === '1';
    add('python utf-8', utf8, utf8 ? 'PYTHONUTF8=1' : 'not set (cp950 / code-page errors on UTF-8 files)', utf8 ? '' : 'set PYTHONUTF8=1 and PYTHONIOENCODING=utf-8 for every python call (or in the user environment)');
  }

  // smoke test: the real chain on the shipped template
  if (pw && ff) {
    let detail = '', pass = false;
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'draw-doctor-'));
    try {
      fs.copyFileSync(path.join(ASSETS, 'seek-template.html'), path.join(dir, 'index.html'));
      fs.copyFileSync(path.join(ASSETS, 'motion.js'), path.join(dir, 'motion.js'));
      const browser = await pw.chromium.launch(exe ? { executablePath: exe } : {});
      const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
      await page.addInitScript(() => { window.__RENDER__ = true; });
      await page.goto(pathToFileURL(path.join(dir, 'index.html')).href + '?f=9:16');
      // warm-up, as render.mjs does: sweep the timeline once so every canvas font and weight has loaded
      await page.evaluate(async () => { const d = (window.timeline && window.timeline().duration) || 8; for (let t = 0; t <= d; t += 0.25) window.seek(t); await document.fonts.ready; for (let t = 0; t <= d; t += 0.25) window.seek(t); });
      const shot = async (t) => { await page.evaluate((x) => window.seek(x), t); return page.locator('canvas').screenshot(); };
      const a = await shot(1.2), b = await shot(1.2);
      fs.writeFileSync(path.join(dir, 'f0.png'), a); fs.writeFileSync(path.join(dir, 'f1.png'), await shot(4.6));
      await browser.close();
      const same = createHash('md5').update(a).digest('hex') === createHash('md5').update(b).digest('hex');
      const enc = run('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '2', '-i', path.join(dir, 'f%d.png'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', path.join(dir, 'smoke.mp4')]);
      pass = same && enc.status === 0;
      detail = `${same ? 'deterministic' : 'NOT deterministic'}; encode ${enc.status === 0 ? 'ok' : 'failed: ' + (enc.stderr || '').trim().slice(0, 80)}`;
    } catch (e) {
      detail = String(e.message || e).split('\n')[0].slice(0, 140);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
    add('smoke render', pass, detail, pass ? '' : 'see pipeline.md § Known environment failures for this message');
  } else {
    add('smoke render', false, 'skipped: needs playwright and ffmpeg', 'fix the rows above first');
  }
  return rows;
}

function report(rows) {
  for (const r of rows) console.log(`${r.pass ? '✓' : '✗'} ${r.name.padEnd(13)} ${r.detail}${r.fix ? `\n    fix: ${r.fix}` : ''}`);
  const ready = rows.every((r) => r.pass);
  console.log(ready ? 'READY' : 'NOT READY');
  return ready;
}

let rows = await check();
if (!report(rows) && INSTALL) {
  const steps = [];
  const miss = (n) => rows.find((r) => r.name === n && !r.pass);
  if (miss('ffmpeg')) steps.push(FIX.ffmpeg);
  if (miss('playwright')) steps.push(FIX.playwright);
  if (miss('playwright') || miss('chromium') || /Executable doesn't exist/.test(rows.find((r) => r.name === 'smoke render')?.detail || '')) steps.push(FIX.chromium);
  if (miss('python')) steps.push(FIX.python);
  for (const s of steps) {
    console.log(`\n$ ${s}`);
    const r = spawnSync(s, { stdio: 'inherit', shell: true, timeout: 900000 });
    if (r.status !== 0) console.log(`  install step exited ${r.status}; run it by hand and rerun the doctor`);
  }
  if (steps.length) {
    if (WIN && steps.includes(FIX.ffmpeg)) console.log('\nffmpeg was just installed: open a new terminal (or add the WinGet Links folder to PATH) before rerunning.');
    console.log('\nrechecking…');
    rows = await check();
    process.exit(report(rows) ? 0 : 1);
  }
}
process.exit(rows.every((r) => r.pass) ? 0 : 1);
