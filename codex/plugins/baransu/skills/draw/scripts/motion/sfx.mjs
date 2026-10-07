#!/usr/bin/env node
// sfx.mjs — synthesize UI sounds from a cue list and mix them (optionally over a bed).
//
//   node sfx.mjs cues.json out/mix.wav [--bed song.wav] [--bed-gain 0.8] [--loop] [--sr 48000]
//
// cues.json: { "duration": 15, "cues": [ { "t": 0.5, "type": "click", "gain": 1, "pan": 0 }, ... ] }
//   (render.mjs writes this from window.timeline(); or write it by hand from the beat grid)
// Types: click tick key pop press release toggle whoosh impact riser chime success
// Each sound is placed so its *measured peak* lands on the cue time, which is
// where the ear hears the hit. --loop wraps tails past the end to the start so a
// seamless loop stays seamless. Output: 16-bit stereo WAV, peak-normalised to -1 dBFS
// and RMS-trimmed toward roughly -14 LUFS (a simple RMS stand-in, not K-weighted).
// A bed must be a 16-bit PCM WAV (convert anything else with ffmpeg first).
import fs from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
const pos = argv.filter((a) => !a.startsWith('--'));
const flag = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? (argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : true) : d; };
if (pos.length < 2) { console.error('usage: sfx.mjs cues.json out.wav [--bed song.wav] [--bed-gain 0.8] [--loop]'); process.exit(2); }
const SR = Number(flag('sr', 48000));
const cuesDoc = JSON.parse(fs.readFileSync(pos[0], 'utf8'));
const dur = Number(cuesDoc.duration);
if (!Number.isFinite(dur) || dur <= 0) { console.error('cues.json needs a positive duration'); process.exit(2); }

// deterministic noise
let seed = 7;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 2147483648 - 1; };
const axis = (d) => Float64Array.from({ length: Math.round(SR * d) }, (_, i) => i / SR);
const env = (t, attack, decay) => t.map((x) => (attack > 0 ? Math.min(1, x / attack) : 1) * Math.exp(-Math.max(0, x - attack) / decay));
const mul = (a, b) => a.map((v, i) => v * b[i]);
const add = (...xs) => xs[0].map((_, i) => xs.reduce((s, x) => s + (x[i] || 0), 0));
const scale = (a, k) => a.map((v) => v * k);
const sine = (t, f) => t.map((x) => Math.sin(2 * Math.PI * f * x));
const sweep = (t, f0, f1, tau) => { let ph = 0, out = new Float64Array(t.length); for (let i = 0; i < t.length; i++) { const f = f1 + (f0 - f1) * Math.exp(-t[i] / tau); ph += 2 * Math.PI * f / SR; out[i] = Math.sin(ph); } return out; };
const noise = (n) => Float64Array.from({ length: n }, rnd);
function highpass(x, fc) { const rc = 1 / (2 * Math.PI * fc), a = rc / (rc + 1 / SR); const y = new Float64Array(x.length); for (let i = 1; i < x.length; i++) y[i] = a * (y[i - 1] + x[i] - x[i - 1]); return y; }
function lowpass(x, fc) { const a = Math.exp(-2 * Math.PI * fc / SR); const y = new Float64Array(x.length); let acc = 0; for (let i = 0; i < x.length; i++) { acc = (1 - a) * x[i] + a * acc; y[i] = acc; } return y; }
const norm = (x, peak) => { let m = 0; for (const v of x) m = Math.max(m, Math.abs(v)); return scale(x, peak / (m + 1e-9)); };

function click(f = 2100, d = 0.05, body = 0.012, peak = 0.5) {
  const t = axis(d);
  return norm(add(scale(mul(highpass(noise(t.length), 3000), env(t, 0.0004, 0.0025)), 0.6), mul(sine(t, f), env(t, 0.0008, body))), peak);
}
const SOUNDS = {
  click: () => click(),
  tick: () => { const t = axis(0.08); return norm(add(mul(sine(t, 2900), env(t, 0.0006, 0.012)), click(4200, 0.08, 0.004, 0.3)), 0.25); },
  key: () => click(3200, 0.035, 0.006, 0.22),
  press: () => click(1500, 0.05, 0.008, 0.24),
  release: () => click(2500, 0.05, 0.006, 0.2),
  pop: () => { const t = axis(0.12); return norm(mul(sweep(t, 380, 1100, 0.02), env(t, 0.004, 0.03)), 0.32); },
  toggle: () => { const t = axis(0.09); return norm(add(mul(sweep(t, 1200, 700, 0.01), env(t, 0.001, 0.02)), click(2600, 0.09, 0.012, 0.5)), 0.45); },
  whoosh: () => { const t = axis(0.32); const n = lowpass(highpass(noise(t.length), 700), 4500); return norm(mul(n, t.map((x) => Math.pow(Math.sin(Math.PI * Math.min(1, x / 0.32)), 2))), 0.12); },
  impact: () => { const t = axis(0.35); return norm(add(mul(sweep(t, 160, 48, 0.05), env(t, 0.002, 0.12)), scale(mul(lowpass(noise(t.length), 1800), env(t, 0.001, 0.03)), 0.5)), 0.6); },
  riser: () => { const t = axis(0.9); const n = lowpass(highpass(noise(t.length), 300), 6000); return norm(mul(n, t.map((x) => Math.pow(x / 0.9, 2))), 0.2); },
  chime: () => { const t = axis(0.7); return norm(add(mul(sine(t, 1318.5), env(t, 0.002, 0.18)), scale(mul(sine(t, 2637), env(t, 0.002, 0.08)), 0.3)), 0.28); },
  success: () => { const t = axis(0.6); const t2 = t.map((x) => Math.max(0, x - 0.075)); const a = mul(sine(t, 1318.5), env(t, 0.002, 0.12)); const b = mul(mul(sine(t2, 1975.5), env(t2, 0.002, 0.18)), t.map((x) => (x >= 0.075 ? 1 : 0))); return norm(add(a, scale(b, 0.9)), 0.26); },
};

function peakIndex(x) { const k = Math.max(1, Math.round(SR * 0.002)); let best = 0, bi = 0, acc = 0; const q = []; for (let i = 0; i < x.length; i++) { acc += Math.abs(x[i]); q.push(Math.abs(x[i])); if (q.length > k) acc -= q.shift(); if (acc > best) { best = acc; bi = i; } } return bi; }

function readWav(file) {
  const b = fs.readFileSync(file);
  if (b.toString('ascii', 0, 4) !== 'RIFF' || b.toString('ascii', 8, 12) !== 'WAVE') throw new Error('bed is not a WAV');
  let p = 12, fmt = null, data = null;
  while (p < b.length) { const id = b.toString('ascii', p, p + 4), sz = b.readUInt32LE(p + 4); if (id === 'fmt ') fmt = { ch: b.readUInt16LE(p + 10), sr: b.readUInt32LE(p + 12), bits: b.readUInt16LE(p + 22) }; if (id === 'data') data = b.subarray(p + 8, p + 8 + sz); p += 8 + sz + (sz & 1); }
  if (!fmt || !data) throw new Error('bad WAV');
  if (fmt.bits !== 16) throw new Error('bed must be 16-bit PCM (convert with ffmpeg -c:a pcm_s16le)');
  if (fmt.sr !== SR) throw new Error(`bed sample rate ${fmt.sr} ≠ ${SR}; resample with ffmpeg -ar ${SR}`);
  const n = data.length / 2 / fmt.ch; const L = new Float64Array(n), R = new Float64Array(n);
  for (let i = 0; i < n; i++) { L[i] = data.readInt16LE(i * 2 * fmt.ch) / 32768; R[i] = fmt.ch > 1 ? data.readInt16LE(i * 2 * fmt.ch + 2) / 32768 : L[i]; }
  return { L, R };
}
function writeWav(file, L, R) {
  const n = L.length, b = Buffer.alloc(44 + n * 4);
  b.write('RIFF', 0); b.writeUInt32LE(36 + n * 4, 4); b.write('WAVE', 8); b.write('fmt ', 12); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(2, 22);
  b.writeUInt32LE(SR, 24); b.writeUInt32LE(SR * 4, 28); b.writeUInt16LE(4, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 4, 40);
  for (let i = 0; i < n; i++) { b.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[i])) * 32767), 44 + i * 4); b.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[i])) * 32767), 46 + i * 4); }
  fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, b);
}

const n = Math.round(dur * SR);
const L = new Float64Array(n), R = new Float64Array(n);
if (flag('bed')) {
  const bed = readWav(flag('bed')), g = Number(flag('bed-gain', 0.8));
  for (let i = 0; i < n; i++) { L[i] = (bed.L[i] || 0) * g; R[i] = (bed.R[i] || 0) * g; }
}
const cache = {}, peaks = {};
const loop = !!flag('loop');
let placed = 0;
for (const cue of cuesDoc.cues || []) {
  const type = cue.type || 'click';
  if (!SOUNDS[type]) { console.error(`unknown sound type "${type}" (have: ${Object.keys(SOUNDS).join(' ')})`); continue; }
  cache[type] ||= SOUNDS[type](); peaks[type] ??= peakIndex(cache[type]);
  const x = cache[type], start = Math.round(cue.t * SR) - peaks[type], g = cue.gain ?? 1, pan = cue.pan ?? 0;
  for (let i = 0; i < x.length; i++) {
    let j = start + i; if (j < 0 || j >= n) { if (!loop) continue; j = ((j % n) + n) % n; }
    L[j] += x[i] * g * (1 - Math.max(0, pan)); R[j] += x[i] * g * (1 + Math.min(0, pan));
  }
  placed++;
}
// loudness: RMS toward ~-14 dBFS, then peak ceiling -1 dBFS
let rms = 0; for (let i = 0; i < n; i++) rms += L[i] * L[i] + R[i] * R[i]; rms = Math.sqrt(rms / (2 * n)) || 1e-9;
let g = Math.min(4, Math.pow(10, -14 / 20) / rms);
let pk = 0; for (let i = 0; i < n; i++) pk = Math.max(pk, Math.abs(L[i] * g), Math.abs(R[i] * g));
if (pk > Math.pow(10, -1 / 20)) g *= Math.pow(10, -1 / 20) / pk;
writeWav(pos[1], scale(L, g), scale(R, g));
console.log(`wrote ${pos[1]}: ${placed} cues, ${dur}s, gain ${g.toFixed(3)}`);
