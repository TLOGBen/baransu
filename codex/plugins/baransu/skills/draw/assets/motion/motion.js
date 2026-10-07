// motion.js — closed-form motion primitives for seek(t) films.
//
// Every function is a pure function of time: the same t always gives the same
// value, so frame 812 renders without simulating frames 0–811, renders are
// identical across runs, and a headless browser can sample any instant.
//
// Load it as a classic script (`<script src="motion.js">` → window.Motion) or
// require() it from Node for tests.
(function (root) {
  'use strict';

  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, p) => a + (b - a) * p;

  // Damped spring step response 0 → 1. k = stiffness, d = damping.
  // z < 1 overshoots a little (the "expensive" feel); z ≥ 1 is critically damped.
  function spring(t, k = 170, d = 26) {
    if (t <= 0) return 0;
    const w0 = Math.sqrt(k), z = d / (2 * w0);
    if (z < 1) {
      const wd = w0 * Math.sqrt(1 - z * z);
      return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + (z * w0 / wd) * Math.sin(wd * t));
    }
    return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
  }

  // A value that changes target several times: sum one spring per change,
  // each starting at its own time. keys = [[time, value], ...] sorted by time.
  function track(t, keys, k = 170, d = 26) {
    let v = keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      v += (keys[i][1] - keys[i - 1][1]) * spring(t - keys[i][0], k, d);
    }
    return v;
  }

  // Named spring feels. Use the feel that matches the mass of the thing moving.
  const FEEL = {
    snappy: [320, 30],   // buttons, toggles, leading edges
    ui: [170, 26],       // cards, containers, camera
    heavy: [120, 24],    // big type, 3D objects, logo lockups
    playful: [200, 14],  // mascots, stickers (visible overshoot)
  };
  const feel = (name, t) => spring(t, ...(FEEL[name] || FEEL.ui));

  // A tab indicator or any element whose two edges should stretch apart while
  // moving: the leading edge is stiffer than the trailing edge.
  function stretch(t, stops, lead = FEEL.snappy, trail = [140, 22]) {
    const a = track(t, stops, lead[0], lead[1]);
    const b = track(t, stops, trail[0], trail[1]);
    return { from: Math.min(a, b), to: Math.max(a, b) };
  }

  // Text inside a morphing container: in after the morph starts, out before the
  // next morph starts, so two labels never overlap.
  function swapAlpha(t, tIn, tOut, lag = 0.08, fade = 0.12, lead = 0.1) {
    return Math.min(clamp((t - tIn - lag) / fade), clamp((tOut - lead - t) / lead));
  }

  // Seamless loop: pin the last frame to the first.
  const loopT = (t, dur) => ((t % dur) + dur) % dur;

  // Deterministic PRNG. Never Math.random in a film.
  function rng(seed) {
    seed |= 0;
    return function () {
      seed = seed + 0x6D2B79F5 | 0;
      let x = Math.imul(seed ^ seed >>> 15, 1 | seed);
      x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x;
      return ((x ^ x >>> 14) >>> 0) / 4294967296;
    };
  }

  // Easing for the few places a fixed curve is right (camera settles, fades).
  const ease = {
    out: (x) => 1 - Math.pow(1 - clamp(x), 3),
    in: (x) => Math.pow(clamp(x), 3),
    inOut: (x) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; },
    back: (x, s = 1.7) => { x = clamp(x) - 1; return 1 + (s + 1) * x * x * x + s * x * x; },
  };

  // Beat helpers for a measured grid: beat length in seconds, downbeat every `bar` beats.
  function beatGrid(bpm, bar = 4) {
    const beat = 60 / bpm;
    return {
      beat,
      bar: beat * bar,
      at: (n) => n * beat,                      // time of beat n
      index: (t) => Math.floor(t / beat),       // beat index at t
      phase: (t) => (t % beat) / beat,          // 0..1 inside the beat
      pulse: (t, decay = 6) => Math.exp(-((t % beat)) * decay), // 1 on the beat, decays
      isDown: (n) => n % bar === 0,
    };
  }

  const M = { clamp, lerp, spring, track, FEEL, feel, stretch, swapAlpha, loopT, rng, ease, beatGrid };
  if (typeof module !== 'undefined' && module.exports) module.exports = M;
  else root.Motion = M;
})(typeof globalThis !== 'undefined' ? globalThis : this);
