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

  // ---- What the viewer sees: cursor, typing, drag, camera, type, transitions, data ----

  // A cursor that travels between positions on a UI spring and presses on clicks.
  // keys = [[time, x, y], ...]; clicks = [time, ...]. Draw it yourself (an arrow or a
  // 2-px ring); `down` is true during the press and `scale` dips so the press reads at 360 px.
  function cursor(t, keys, clicks = [], press = 0.12) {
    const x = track(t, keys.map(([k, px]) => [k, px]), ...FEEL.ui);
    const y = track(t, keys.map(([k, , py]) => [k, py]), ...FEEL.ui);
    const dt = clicks.reduce((m, c) => (t >= c ? Math.min(m, t - c) : m), Infinity);
    const down = dt < press;
    const scale = 1 - 0.18 * (down ? 1 - dt / press : 0) + 0.06 * (dt >= press && dt < press * 2 ? 1 - (dt - press) / press : 0);
    return { x, y, down, scale };
  }

  // Text typed in at `cps` characters per second with seeded per-character jitter;
  // the caret stays solid while typing and blinks at 2 Hz afterwards.
  function typed(t, text, t0, cps = 14, seed = 1) {
    const r = rng(seed), times = [];
    let acc = t0;
    for (let i = 0; i < text.length; i++) { acc += (1 / cps) * (0.6 + 0.8 * r()); times.push(acc); }
    let n = 0; while (n < text.length && t >= times[n]) n++;
    const typing = t >= t0 && n < text.length;
    return { text: text.slice(0, n), done: n === text.length, caret: typing || Math.floor((t - t0) * 2) % 2 === 0 };
  }

  // Direct manipulation: before grab the value rests; while held it follows held(t)
  // exactly (the hand is the truth); on release it springs from where it was let go back to rest.
  function drag(t, grabT, releaseT, held, rest, feelName = 'ui') {
    if (t < grabT) return rest;
    if (t < releaseT) return held(t);
    const at = held(releaseT);
    return at + (rest - at) * feel(feelName, t - releaseT);
  }

  // A camera that re-frames each state: keys = [[time, {x, y, w, h}], ...] are the rects that
  // should fill the W×H frame; a push-in is a later key with a smaller rect. Apply with
  //   g.translate(W/2, H/2); g.scale(cam.s, cam.s); g.translate(-cam.cx, -cam.cy)
  function camera(t, keys, W, H, feelName = 'ui') {
    const [k, d] = FEEL[feelName] || FEEL.ui;
    const f = (p) => track(t, keys.map(([kt, r]) => [kt, r[p]]), k, d);
    const x = f('x'), y = f('y'), w = f('w'), h = f('h');
    return { cx: x + w / 2, cy: y + h / 2, s: Math.min(W / w, H / h) };
  }

  // Kinetic type: one spring per word, staggered by `gap`; returns progress 0..1 per word.
  function words(t, text, t0, gap = 0.06, feelName = 'heavy') {
    return text.split(/\s+/).filter(Boolean).map((word, i) => ({ word, p: feel(feelName, t - t0 - i * gap) }));
  }

  // Transitions as geometry, so a seam is drawn rather than faded. Each returns what to clip
  // or offset for the incoming scene; the outgoing scene is drawn underneath.
  function wipe(t, t0, dur, W, H, dir = 'right') {
    const p = ease.inOut((t - t0) / dur);
    if (dir === 'right') return { x: 0, y: 0, w: W * p, h: H, p };
    if (dir === 'left') return { x: W * (1 - p), y: 0, w: W * p, h: H, p };
    if (dir === 'down') return { x: 0, y: 0, w: W, h: H * p, p };
    return { x: 0, y: H * (1 - p), w: W, h: H * p, p };
  }
  function iris(t, t0, dur, W, H, cx = W / 2, cy = H / 2) {
    const p = ease.inOut((t - t0) / dur);
    return { cx, cy, r: Math.hypot(Math.max(cx, W - cx), Math.max(cy, H - cy)) * p, p };
  }
  // Whip pan: the outgoing scene slides out by `out`, the incoming slides in by `inn`; blur follows speed.
  function whip(t, t0, dur, W, dir = -1) {
    const x = clamp((t - t0) / dur), p = ease.inOut(x);
    const speed = x > 0 && x < 1 ? Math.sin(Math.PI * x) : 0;
    return { out: dir * W * p, inn: -dir * W * (1 - p), blur: 24 * speed, p };
  }

  // Data that draws itself: progress for setLineDash([len, len]) with lineDashOffset = len * (1 - p).
  const drawOn = (t, t0, dur = 1.2) => ease.out((t - t0) / dur);

  // The content swap behind a morph hides under a short blur: `px` at tIn and at tOut, 0 between.
  function swapBlur(t, tIn, tOut, px = 6, len = 0.15) {
    const a = t >= tIn ? 1 - clamp((t - tIn) / len) : 0;
    const b = t <= tOut ? clamp((t - (tOut - len)) / len) : 0;
    return px * Math.max(a, b);
  }

  // One number that proves it works: a count-up that decelerates into the real value.
  const countUp = (t, from, to, t0, dur = 1.2) => from + (to - from) * ease.out((t - t0) / dur);

  const M = { clamp, lerp, spring, track, FEEL, feel, stretch, swapAlpha, loopT, rng, ease, beatGrid,
    cursor, typed, drag, camera, words, wipe, iris, whip, drawOn, swapBlur, countUp };
  if (typeof module !== 'undefined' && module.exports) module.exports = M;
  else root.Motion = M;
})(typeof globalThis !== 'undefined' ? globalThis : this);
