#!/usr/bin/env node
// perf-check.mjs — headless performance check for a component (<slug>.html), e.g. a mechanism figure.
//
//   node scripts/motion/perf-check.mjs <slug>.html [--selector "figure, .fig"] [--backend auto|d3d11|swiftshader]
//                                                [--timeout 60] [--dwell 2000] [--out report.json] [--chrome-arg flag]
//
// Opens the page in headless Chromium (never a visible window) and measures what freezes a reader's
// browser: WebGL shader link time, long tasks, rAF callback time per figure, a loop that never rests,
// and GPU draw cost. Each figure (--selector, default "figure, .fig") is scrolled into view alone,
// then all of them together in one tall viewport, then the page is scrolled past every figure to
// check that drawing stops.
//
// Backend: auto = ANGLE D3D11 on Windows (where Chrome really compiles shaders; SwiftShader timings
// say nothing about it), SwiftShader elsewhere.
//
// Budgets (from the 2026-10 "Two big machines" freeze investigation):
//   shader-link      every program's linkProgram + getProgramParameter(LINK_STATUS) <= 200 ms (WARN up to 1 s, FAIL above)
//   page-load        the longest task while the page loads (parse, web-font swap, figures built at load)
//                    <= 200 ms (WARN up to 1 s, FAIL above)
//   mount-task       the longest task while a figure first enters view, or while the viewport resizes, <= 200 ms
//   longtask         no task > 50 ms at any other time
//   raf <figure>     rAF callback time while that figure is in view: p90 <= 4 ms, p99 <= 16 ms
//   raf all-together every figure in view at once: p90 <= 16 ms, p99 <= 33 ms (the frame still fits 60 Hz)
//   rest             no canvas or WebGL draw call and no rAF callback once every figure has been out of view
//                    for 2 s (a frame loop that keeps re-arming with nothing visible fails)
//   gl-draw <ctx>    draw + readPixels on each live WebGL context <= 8 ms (median of 3)
//   deadline         the run finished inside --timeout; a page that blocks is killed and named
//   renderer         the WebGL renderer string (UNMASKED_RENDERER_WEBGL, else RENDERER) of a probe context
//                    opened before the page and of every live context the page creates. On Windows, whatever
//                    --backend says, a string without "D3D11" (or no WebGL at all) means the run did not use
//                    the rasterizer Windows Chrome uses (a fallback, or --backend swiftshader), so the numbers
//                    say nothing about Windows Chrome: the row is NOT-EVIDENCE, the result is NOT-EVIDENCE,
//                    and the exit code is 1.
//
// --chrome-arg <flag> appends one more Chromium switch (repeat the option for more); used by the tests to
// force a fallback renderer. Never pass --disable-gpu: it makes every d3d11 run NOT-EVIDENCE.
//
// Hard deadline: the browser process tree is killed and the report printed before --timeout seconds,
// whatever the page does. A blocked page names the last GL call that entered and never returned.
// A page with no WebGL skips the shader-link and gl-draw rows. A figure that drew no frames skips its
// raf row (a static figure costs nothing per frame).
// Prints the JSON report, then one PASS / WARN / FAIL / SKIP / NOT-EVIDENCE line per budget, then RESULT.
// Exit 0 only when no row is FAIL or NOT-EVIDENCE; 1 otherwise; 2 when Playwright is missing or the
// usage is wrong.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { loadPlaywright, chromiumPath, launchChromium, INSTALL_HINT } from './browser.mjs';

const argv = process.argv.slice(2);
const opt = { _: [] }, EXTRA_ARGS = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--chrome-arg') { if (argv[i + 1]) EXTRA_ARGS.push(argv[++i]); }   // its value itself starts with --
  else if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
  else opt._.push(argv[i]);
}
const target = opt._[0];
if (!target) { console.error('usage: perf-check.mjs <slug.html|url> [--selector css] [--backend auto|d3d11|swiftshader] [--timeout 60] [--dwell ms] [--out report.json] [--chrome-arg flag]'); process.exit(2); }
const URL_ = /^(https?|file):/i.test(target) ? target : pathToFileURL(path.resolve(target)).href;
if (URL_.startsWith('file:') && !fs.existsSync(new URL(URL_))) { console.error(`perf-check: no such file ${target}`); process.exit(2); }
const SEL = typeof opt.selector === 'string' ? opt.selector : 'figure, .fig';
const WIN = process.platform === 'win32';
const BACKEND = opt.backend === 'd3d11' || opt.backend === 'swiftshader' ? opt.backend : WIN ? 'd3d11' : 'swiftshader';
if (opt.backend && !['auto', 'd3d11', 'swiftshader'].includes(opt.backend)) { console.error(`perf-check: unknown --backend ${opt.backend}`); process.exit(2); }
const TIMEOUT_MS = Math.max(15, Number(opt.timeout) || 60) * 1000;
const STALL_MS = Math.min(15000, Math.max(5000, TIMEOUT_MS / 4));   // one page call that takes this long = the page is blocked
const VIEW = { width: 1280, height: 900 };
const LIMIT = { linkWarn: 200, linkFail: 1000, mount: 200, loadFail: 1000, longtask: 50, rafP90: 4, rafP99: 16, rafAllP90: 16, rafAllP99: 33, glDraw: 8, restGrace: 2000 };
const FLAGS = {
  d3d11: ['--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=d3d11', '--enable-gpu-rasterization'],
  swiftshader: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=swiftshader'],
};

const T0 = Date.now();
const report = {
  file: URL_, backend: BACKEND, renderer: null, probeRenderer: null, renderers: [], chromeArgs: [], chromium: null, timeoutS: TIMEOUT_MS / 1000, elapsedMs: 0,
  completed: false, stopReason: null, pendingGlCall: null,
  programs: [], shaders: [], contexts: [], longtasks: [], figures: [], all: null, rest: null, bench: [], pageErrors: [], budgets: [],
};
// `launching` holds launchChromium()'s promise until it settles: a deadline that fires mid-launch has
// no browser to kill yet, so finish() waits for the launch and kills it (profile dir included) then.
let browser = null, launching = null, finished = false;

// ---- GL timeline, rebuilt in Node from out-of-band console markers, so it survives a blocked page ----
const gl = { programs: new Map(), shaders: new Map(), contexts: new Map(), pending: new Map() };
function onMarker(text) {
  let m; try { m = JSON.parse(text.slice(8)); } catch { return; }
  const key = `${m.frame}|${m.call}|${m.obj}`;
  if (m.ph === 'B') { gl.pending.set(key, m); return; }
  gl.pending.delete(key);
  if (m.call === 'getContext') { gl.contexts.set(`${m.frame}|${m.obj}`, { id: m.obj, frame: m.frame, kind: m.kind, getContextMs: m.ms, renderer: m.renderer || null, firstDrawMs: null }); if (m.renderer && !report.renderer) report.renderer = m.renderer; return; }
  if (m.call === 'firstDraw') { const c = gl.contexts.get(`${m.frame}|${m.ctx}`); if (c) c.firstDrawMs = m.ms; return; }
  const pk = `${m.frame}|${m.obj}`;
  const shader = m.call === 'compileShader' || m.call === 'COMPILE_STATUS';
  const map = shader ? gl.shaders : gl.programs;
  const p = map.get(pk) || (shader ? { id: m.obj, frame: m.frame, chars: 0, compileMs: 0 } : { id: m.obj, frame: m.frame, fragChars: 0, linkMs: 0 });
  if (shader) { p.chars = Math.max(p.chars, m.chars || 0); p.compileMs = round(p.compileMs + m.ms); }
  else { p.fragChars = Math.max(p.fragChars, m.chars || 0); p.linkMs = round(p.linkMs + m.ms); }
  map.set(pk, p);
}
function pendingCall() {
  let last = null;
  for (const m of gl.pending.values()) if (!last || m.at > last.at) last = m;
  if (!last) return null;
  const name = last.call === 'LINK_STATUS' ? 'getProgramParameter(LINK_STATUS)' : last.call === 'COMPILE_STATUS' ? 'getShaderParameter(COMPILE_STATUS)' : last.call;
  return { call: name, object: last.obj, frame: last.frame, fragChars: last.chars || null, blockedMs: Date.now() - last.at };
}

// ---- In-page instrumentation (runs before any page script, in every frame) ----
function instrument() {
  const W = window, now = () => performance.timeOrigin + performance.now();
  const log = console.log.bind(console);
  const frame = (location.pathname.split('/').pop() || location.host || 'page').slice(0, 60);
  const P = W.__perf = { raf: [], long: [], draws: 0, ctxs: [], load: null };
  const mark = (o) => log('[perfgl] ' + JSON.stringify({ frame, ...o }));
  let seq = 0;
  const idOf = (o, pfx) => o.__perfId || (o.__perfId = pfx + ++seq);
  const shaderChars = new WeakMap(), progChars = new WeakMap();
  const timed = (o, fn) => { const at = Date.now(); mark({ ph: 'B', at, ...o }); const s = performance.now(); const r = fn(); mark({ ph: 'E', ...o, ms: Math.round((performance.now() - s) * 100) / 100 }); return r; };
  const LINK_STATUS = 0x8B82, COMPILE_STATUS = 0x8B81;
  for (const C of [W.WebGLRenderingContext, W.WebGL2RenderingContext]) {
    if (!C) continue;
    const p = C.prototype;
    const shaderSource = p.shaderSource, attach = p.attachShader, compile = p.compileShader, link = p.linkProgram;
    const getSP = p.getShaderParameter, getPP = p.getProgramParameter;
    p.shaderSource = function (sh, src) { if (sh) shaderChars.set(sh, String(src).length); return shaderSource.call(this, sh, src); };
    p.attachShader = function (pr, sh) { progChars.set(pr, Math.max(progChars.get(pr) || 0, shaderChars.get(sh) || 0)); return attach.call(this, pr, sh); };
    p.compileShader = function (sh) { return timed({ call: 'compileShader', obj: idOf(sh, 's'), chars: shaderChars.get(sh) || 0 }, () => compile.call(this, sh)); };
    p.linkProgram = function (pr) { return timed({ call: 'linkProgram', obj: idOf(pr, 'p'), chars: progChars.get(pr) || 0 }, () => link.call(this, pr)); };
    p.getShaderParameter = function (sh, pn) { return pn === COMPILE_STATUS ? timed({ call: 'COMPILE_STATUS', obj: idOf(sh, 's'), chars: shaderChars.get(sh) || 0 }, () => getSP.call(this, sh, pn)) : getSP.call(this, sh, pn); };
    p.getProgramParameter = function (pr, pn) { return pn === LINK_STATUS ? timed({ call: 'LINK_STATUS', obj: idOf(pr, 'p'), chars: progChars.get(pr) || 0 }, () => getPP.call(this, pr, pn)) : getPP.call(this, pr, pn); };
    for (const n of ['drawArrays', 'drawElements', 'drawArraysInstanced', 'drawElementsInstanced']) {
      const orig = p[n]; if (!orig) continue;
      p[n] = function (...a) {
        P.draws++;
        if (!this.__perfDrawn) { this.__perfDrawn = true; return timed({ call: 'firstDraw', obj: idOf(this, 'c') + ':draw', ctx: idOf(this, 'c') }, () => orig.apply(this, a)); }
        return orig.apply(this, a);
      };
    }
  }
  const C2 = W.CanvasRenderingContext2D && W.CanvasRenderingContext2D.prototype;
  if (C2) for (const n of ['fillRect', 'strokeRect', 'clearRect', 'fill', 'stroke', 'fillText', 'strokeText', 'drawImage', 'putImageData']) {
    const orig = C2[n]; if (!orig) continue;
    C2[n] = function (...a) { P.draws++; return orig.apply(this, a); };
  }
  const getContext = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (kind, ...rest) {
    const isGL = /webgl/i.test(String(kind));
    if (!isGL || this.__perfCtx) return getContext.call(this, kind, ...rest);
    const at = Date.now(), s = performance.now();
    const id = 'c' + ++seq;
    mark({ ph: 'B', at, call: 'getContext', obj: id, kind: String(kind) });
    const c = getContext.call(this, kind, ...rest);
    let renderer = null;
    if (c) { c.__perfId = id; this.__perfCtx = c; try { const e = c.getExtension('WEBGL_debug_renderer_info'); renderer = e ? c.getParameter(e.UNMASKED_RENDERER_WEBGL) : c.getParameter(c.RENDERER); } catch {} P.ctxs.push({ id, canvas: this, gl: c }); }
    mark({ ph: 'E', call: 'getContext', obj: id, kind: String(kind), ms: Math.round((performance.now() - s) * 100) / 100, renderer });
    return c;
  };
  const raf = W.requestAnimationFrame.bind(W);
  W.requestAnimationFrame = (cb) => raf((t) => {
    const s = performance.now();
    try { return cb(t); } finally { P.raf.push([Math.round(performance.timeOrigin + s), Math.round((performance.now() - s) * 100) / 100]); if (P.raf.length > 40000) P.raf.splice(0, 10000); }
  });
  try { new PerformanceObserver((l) => { for (const e of l.getEntries()) P.long.push([Math.round(performance.timeOrigin + e.startTime), Math.round(e.duration)]); }).observe({ type: 'longtask', buffered: true }); } catch {}
  W.addEventListener('load', () => { P.load = now(); });
  W.__perfBench = (n) => P.ctxs.map(({ id, canvas, gl: g }) => {
    try {
      if (g.isContextLost()) return { ctx: id, skipped: 'context lost' };
      if (!g.getParameter(g.CURRENT_PROGRAM)) return { ctx: id, skipped: 'no program in use' };
      if (!canvas.isConnected) return { ctx: id, skipped: 'canvas detached' };
      const px = new Uint8Array(4), ms = [];
      g.finish();
      for (let i = 0; i < n; i++) {
        const s = performance.now();
        g.drawArrays(g.TRIANGLES, 0, 3);
        g.readPixels(0, 0, 1, 1, g.RGBA, g.UNSIGNED_BYTE, px);
        ms.push(Math.round((performance.now() - s) * 100) / 100);
      }
      return { ctx: id, w: g.drawingBufferWidth, h: g.drawingBufferHeight, ms, glError: g.getError() || 0 };
    } catch (e) { return { ctx: id, skipped: String(e).slice(0, 100) }; }
  });
}

// ---- helpers ----
const round = (x) => Math.round(x * 100) / 100;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function stats(a) {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y), q = (p) => s[Math.min(s.length - 1, Math.floor(p * s.length))];
  return { n: s.length, p50: q(0.5), p90: q(0.9), p99: q(0.99), max: s[s.length - 1] };
}
class Stall extends Error {}
// Every page call goes through this: a call that does not return within STALL_MS means the page is blocked.
async function guard(promise, label, ms = STALL_MS) {
  let t;
  const stall = new Promise((_, rej) => { t = setTimeout(() => rej(new Stall(`${label} did not return in ${ms / 1000} s`)), ms); });
  try { return await Promise.race([promise, stall]); } finally { clearTimeout(t); }
}
function killBrowser() {
  const proc = browser && browser.process && browser.process();
  if (!proc) { if (browser && browser.kill) browser.kill(); return; }
  if (proc.exitCode !== null) return;
  if (WIN) spawnSync('taskkill', ['/PID', String(proc.pid), '/T', '/F'], { stdio: 'ignore', timeout: 8000 });
  else { try { process.kill(-proc.pid, 'SIGKILL'); } catch {} try { proc.kill('SIGKILL'); } catch {} }
}

function budgets(data) {
  const rows = [];
  const add = (name, status, value, limit, note = '') => rows.push({ name, status, value, limit, note });
  const progs = report.programs;
  // Renderer first: on Windows d3d11 every other number is only evidence when ANGLE really ran on D3D11.
  {
    const seen = [['probe', report.probeRenderer], ...report.contexts.map((c) => [c.id, c.renderer])];
    const named = seen.map(([k, r]) => `${k}: ${r || 'no WebGL'}`).join('; ');
    if (WIN) {
      const off = seen.filter(([, r]) => !r || !/D3D11/.test(r));
      add('renderer', off.length ? 'NOT-EVIDENCE' : 'PASS', off.length ? off.map(([k]) => k).join(', ') : seen.length, 'every renderer string contains "D3D11"', off.length ? `${named} — ${BACKEND === 'd3d11' ? 'Chromium fell back from ANGLE D3D11' : '--backend swiftshader on Windows'}; these numbers say nothing about Windows Chrome (${BACKEND === 'd3d11' ? 'check the GPU driver; never pass --disable-gpu' : 'rerun with --backend auto or d3d11'})` : named);
    } else add('renderer', 'SKIP', seen.length, '"D3D11" required only on Windows', named);
  }
  const notEvidence = BACKEND === 'swiftshader' && WIN ? ' (SwiftShader: not evidence for Windows Chrome)' : '';
  if (!progs.length && !report.pendingGlCall) add('shader-link', 'SKIP', null, `<= ${LIMIT.linkWarn} ms`, 'no WebGL program linked');
  else {
    const worst = progs.reduce((a, p) => (p.linkMs > (a ? a.linkMs : -1) ? p : a), null);
    const pend = report.pendingGlCall && /link|LINK/.test(report.pendingGlCall.call) ? report.pendingGlCall : null;
    const v = pend ? pend.blockedMs : worst.linkMs;
    const st = pend || v > LIMIT.linkFail ? 'FAIL' : v > LIMIT.linkWarn ? 'WARN' : 'PASS';
    add('shader-link', st, v, `<= ${LIMIT.linkWarn} ms (FAIL > ${LIMIT.linkFail} ms)`, (pend ? `program ${pend.object} (${pend.fragChars} chars) still linking when stopped` : `worst ${worst.id} (${worst.fragChars} chars) of ${progs.length}`) + notEvidence);
  }
  if (!data) return rows;
  const of = (k) => data.long.filter((l) => l.kind === k), max = (a) => a.reduce((m, l) => Math.max(m, l.ms), 0);
  const load = of('load'), mount = of('mount'), after = of('after');
  const lMax = max(load), mMax = max(mount), aMax = max(after);
  add('page-load', lMax > LIMIT.loadFail ? 'FAIL' : lMax > LIMIT.mount ? 'WARN' : 'PASS', lMax, `<= ${LIMIT.mount} ms (FAIL > ${LIMIT.loadFail} ms)`, `${load.length} long task(s) while the page loaded (parse, web-font swap, figures built at load)`);
  add('mount-task', mMax > LIMIT.mount ? 'FAIL' : 'PASS', mMax, `<= ${LIMIT.mount} ms`, `${mount.length} long task(s) while a figure first entered view or the viewport resized`);
  add('longtask', aMax > LIMIT.longtask ? 'FAIL' : 'PASS', aMax, `<= ${LIMIT.longtask} ms`, `${after.length} long task(s) after mount`);
  const rows_ = report.figures.map((f) => ({ ...f, p90: LIMIT.rafP90, p99: LIMIT.rafP99 }));
  // All figures drawing in one frame: the frame must still fit 60 Hz.
  if (report.all) rows_.push({ label: `all-together (${report.all.inView}/${report.all.of} in view)`, raf: report.all.raf, p90: LIMIT.rafAllP90, p99: LIMIT.rafAllP99 });
  for (const f of rows_) {
    const lim = `p90 <= ${f.p90} ms, p99 <= ${f.p99} ms`;
    if (!f.raf || f.raf.n < 5) { add(`raf ${f.label}`, 'SKIP', null, lim, 'no frames drawn (static)'); continue; }
    const bad = f.raf.p90 > f.p90 || f.raf.p99 > f.p99;
    add(`raf ${f.label}`, bad ? 'FAIL' : 'PASS', `p90 ${f.raf.p90} / p99 ${f.raf.p99}`, lim, `${f.raf.n} callbacks`);
  }
  if (report.rest) add('rest', report.rest.draws > 0 || report.rest.rafPerSec > 0 ? 'FAIL' : 'PASS', report.rest.draws, '0 draw calls and 0 rAF callbacks', `${report.rest.figuresInView} figure(s) in view; rAF ${report.rest.rafPerSec}/s costing ${report.rest.rafMsPerSec} ms/s${report.rest.rafPerSec > 0 && report.rest.draws === 0 ? ' (the frame loop never stops: it must stop within 2 s of rest and re-arm on visibility or play)' : ''}`);
  if (!report.contexts.length) add('gl-draw', 'SKIP', null, `<= ${LIMIT.glDraw} ms`, 'no WebGL context');
  for (const b of report.bench) {
    if (b.skipped) { add(`gl-draw ${b.ctx}`, 'SKIP', null, `<= ${LIMIT.glDraw} ms`, b.skipped); continue; }
    const med = [...b.ms].sort((x, y) => x - y)[Math.floor(b.ms.length / 2)];
    add(`gl-draw ${b.ctx}`, med > LIMIT.glDraw ? 'FAIL' : 'PASS', med, `<= ${LIMIT.glDraw} ms`, `${b.w}x${b.h}, runs ${b.ms.join(' / ')} ms${b.glError ? `, GL error ${b.glError} (the bench draw does not match the figure's geometry setup)` : ''}`);
  }
  return rows;
}

function finish(stopReason, data = null) {
  if (finished) return;
  finished = true;
  clearTimeout(deadlineTimer);
  report.elapsedMs = Date.now() - T0;
  report.stopReason = stopReason;
  report.completed = !stopReason;
  report.pendingGlCall = stopReason ? pendingCall() : null;
  report.programs = [...gl.programs.values()];
  report.shaders = [...gl.shaders.values()];
  report.contexts = [...gl.contexts.values()];
  report.renderer = report.renderer || report.probeRenderer;
  report.renderers = [...new Set([report.probeRenderer, ...report.contexts.map((c) => c.renderer)].filter(Boolean))];
  const rows = budgets(data);
  if (stopReason) rows.push({ name: 'deadline', status: 'FAIL', value: report.elapsedMs, limit: `${TIMEOUT_MS / 1000} s`, note: stopReason + (report.pendingGlCall ? `; last GL call entered and never returned: ${report.pendingGlCall.call} on ${report.pendingGlCall.object}${report.pendingGlCall.fragChars ? ` (${report.pendingGlCall.fragChars} chars)` : ''}, blocked ${report.pendingGlCall.blockedMs} ms` : '') });
  else rows.push({ name: 'deadline', status: 'PASS', value: report.elapsedMs, limit: `${TIMEOUT_MS / 1000} s`, note: 'run completed' });
  report.budgets = rows;
  killBrowser();
  const out = JSON.stringify(report, null, 2);
  if (typeof opt.out === 'string') { try { fs.writeFileSync(path.resolve(opt.out), out); } catch {} }
  console.log(out);
  for (const r of rows) console.log(`${r.status.padEnd(4)} ${r.name}: ${r.value ?? '-'} (budget ${r.limit})${r.note ? ' — ' + r.note : ''}`);
  const fail = rows.some((r) => r.status === 'FAIL');
  const notEv = rows.some((r) => r.status === 'NOT-EVIDENCE');
  console.log(`RESULT: ${notEv ? 'NOT-EVIDENCE' : fail ? 'FAIL' : 'PASS'} (${BACKEND}, ${round(report.elapsedMs / 1000)} s)`);
  const code = fail || notEv ? 1 : 0;
  if (launching && !browser) {
    // The report is already out; give the pending launch a few seconds to settle, then kill what it started.
    const bail = setTimeout(() => process.exit(code), 4000);
    launching.then((b) => { browser = b; killBrowser(); }, () => {}).finally(() => { clearTimeout(bail); process.exit(code); });
    return;
  }
  process.exit(code);
}

// The deadline fires a little before --timeout so the kill and the report fit inside it.
const deadlineTimer = setTimeout(() => finish(`hard deadline ${TIMEOUT_MS / 1000} s reached`), Math.max(5000, TIMEOUT_MS - 2500));

// ---- the run ----
const pw = await loadPlaywright();
if (!pw) { console.error(INSTALL_HINT); process.exit(2); }
const exe = chromiumPath();
report.chromium = exe || "playwright's default build";

async function run() {
  report.chromeArgs = [...FLAGS[BACKEND], ...EXTRA_ARGS];
  launching = launchChromium(pw, { headless: true, args: report.chromeArgs, executablePath: exe });
  const launched = await launching;
  if (finished) return null;   // the deadline fired mid-launch: finish() owns the kill
  browser = launched; launching = null;
  // Probe the backend on a blank page with no instrumentation, so the renderer is known even when the
  // page itself has no WebGL or blocks before its first context returns.
  const probe = await browser.newPage();
  report.probeRenderer = await guard(probe.evaluate(() => {
    const g = document.createElement('canvas').getContext('webgl');
    if (!g) return null;
    const e = g.getExtension('WEBGL_debug_renderer_info');
    return String(e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : g.getParameter(g.RENDERER));
  }), 'renderer probe');
  await probe.close();
  const context = await browser.newContext({ viewport: VIEW, deviceScaleFactor: 1 });
  await context.addInitScript(instrument);
  const page = await context.newPage();
  page.on('console', (m) => { const t = m.text(); if (t.startsWith('[perfgl] ')) onMarker(t); else if (m.type() === 'error') report.pageErrors.push(t.slice(0, 200)); });
  page.on('pageerror', (e) => report.pageErrors.push(String(e.message || e).slice(0, 200)));

  // Long tasks are classed by when they start: page load (parse, web-font swap, figures built at load),
  // mount (a figure first scrolled into view, or every figure re-laid out by the tall viewport), after.
  const loadWindow = [Date.now(), Infinity];
  const mountWindows = [];
  await guard(page.goto(URL_, { waitUntil: 'load', timeout: TIMEOUT_MS }), 'page load', Math.max(STALL_MS, 20000));
  await guard(page.evaluate(() => document.fonts && document.fonts.ready.then(() => 0)), 'fonts');
  await sleep(1000);
  loadWindow[1] = Date.now();
  await guard(page.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; }), 'setup');

  const n = await guard(page.evaluate((sel) => document.querySelectorAll(sel).length, SEL), 'count figures');
  const dwell = Number(opt.dwell) || Math.max(800, Math.min(2000, Math.floor((TIMEOUT_MS - 25000) / (n + 2))));
  const phases = [];
  for (let i = 0; i < n; i++) {
    const t = Date.now();
    mountWindows.push([t, t + 1000]);
    const label = await guard(page.evaluate(({ sel, i }) => {
      const el = document.querySelectorAll(sel)[i];
      el.scrollIntoView({ block: 'center', behavior: 'instant' });
      const id = el.dataset.fig || el.id || (el.querySelector('figcaption,h2,h3') || {}).textContent || '';
      return `#${i + 1}${id ? ' ' + String(id).trim().slice(0, 32) : ''}`;
    }, { sel: SEL, i }), `scroll to figure ${i + 1}`);
    await sleep(dwell);
    await guard(page.evaluate(() => 0), `figure ${i + 1} liveness`);
    phases.push({ label, from: t, to: Date.now() });
  }

  // All figures at once: one viewport tall enough to show the whole page (capped).
  const tall = await guard(page.evaluate(() => document.documentElement.scrollHeight), 'page height');
  const tResize = Date.now();
  await page.setViewportSize({ width: VIEW.width, height: Math.min(Math.max(tall, VIEW.height), 10000) });
  await guard(page.evaluate(() => scrollTo({ top: 0, behavior: 'instant' })), 'scroll top');
  const tAll = Date.now();
  mountWindows.push([tResize, tAll + 1000]);
  await sleep(Math.max(dwell, 1500));
  const inView = await guard(page.evaluate((sel) => [...document.querySelectorAll(sel)].filter((e) => { const r = e.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; }).length, SEL), 'all in view');
  const allPhase = { from: tAll + 1000, to: Date.now(), inView };

  // Rest: scroll past every figure (a spacer guarantees an empty screen), wait, then count draw calls.
  const tBack = Date.now();
  mountWindows.push([tBack, tBack + 1000]);
  await page.setViewportSize(VIEW);
  await guard(page.evaluate(() => { const s = document.createElement('div'); s.id = '__perf_spacer'; s.style.cssText = `height:${innerHeight * 3}px;pointer-events:none`; document.body.appendChild(s); scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }); }), 'rest scroll');
  await sleep(LIMIT.restGrace);
  const d0 = await guard(page.evaluate(() => ({ draws: window.__perf.draws, t: Date.now() })), 'rest start');
  await sleep(1000);
  const d1 = await guard(page.evaluate((sel) => ({ draws: window.__perf.draws, t: Date.now(), inView: [...document.querySelectorAll(sel)].filter((e) => { const r = e.getBoundingClientRect(); return r.bottom > -120 && r.top < innerHeight + 120; }).length }), SEL), 'rest end');

  // Collect every frame's samples, then bench each live WebGL context.
  const raf = [], long = [];
  for (const f of page.frames()) {
    const p = await guard(f.evaluate(() => window.__perf ? { raf: window.__perf.raf, long: window.__perf.long, load: window.__perf.load } : null), 'collect').catch((e) => { if (e instanceof Stall) throw e; return null; });
    if (p) { raf.push(...p.raf); long.push(...p.long); }
  }
  for (const f of page.frames()) {
    const b = await guard(f.evaluate(() => (window.__perfBench ? window.__perfBench(3) : [])), 'gl draw bench').catch((e) => { if (e instanceof Stall) throw e; return []; });
    report.bench.push(...b);
  }

  const inside = (t, ws) => ws.some(([a, b]) => t >= a && t <= b);
  const longOut = long.map(([at, ms]) => ({ at: at - T0, ms, kind: inside(at, [loadWindow]) ? 'load' : inside(at, mountWindows) ? 'mount' : 'after' }));
  report.longtasks = longOut;
  report.figures = phases.map((p) => ({ label: p.label, at: p.from - T0, dwellMs: p.to - p.from, raf: stats(raf.filter(([at]) => at >= p.from && at <= p.to).map(([, d]) => d)) }));
  report.all = { inView: allPhase.inView, of: n, raf: stats(raf.filter(([at]) => at >= allPhase.from && at <= allPhase.to).map(([, d]) => d)) };
  const restRaf = raf.filter(([at]) => at >= d0.t && at <= d1.t);
  const secs = Math.max(0.001, (d1.t - d0.t) / 1000);
  report.rest = { draws: d1.draws - d0.draws, figuresInView: d1.inView, rafPerSec: round(restRaf.length / secs), rafMsPerSec: round(restRaf.reduce((a, [, d]) => a + d, 0) / secs) };
  if (!n) report.figures = [];
  return { long: longOut };
}

try {
  const data = await run();
  finish(null, data);
} catch (e) {
  finish(e instanceof Stall ? `page blocked: ${e.message}` : `error: ${String(e.message || e).split('\n')[0].slice(0, 200)}`);
}
