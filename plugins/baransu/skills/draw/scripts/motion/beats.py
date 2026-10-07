#!/usr/bin/env python3
"""beats.py — measure a track's beat grid with numpy only.

    python3 beats.py song.wav [--bpm 120] [--out beats.json] [--start 0] [--dur 15]

Writes {bpm, beat, start, duration, beats, downbeats, hits}:
  beats     — every beat time (seconds, relative to --start)   → small state changes
  downbeats — first beat of every bar                           → big transitions
  hits      — strongest onsets (not only on the grid)           → SFX placement

Decoding goes through ffmpeg (any format ffmpeg reads). No librosa, no scipy.
Exit 2 on usage / decode errors.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

import numpy as np

SR = 22050
HOP = 256
FPS = SR / HOP


def load(path: str, start: float, dur: float | None) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.4f}"]
    if dur:
        cmd += ["-t", f"{dur + 1:.4f}"]
    cmd += ["-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    try:
        raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"ffmpeg decode failed: {exc}")
    y = np.frombuffer(raw, dtype=np.float32).copy()
    if len(y) < SR:
        sys.exit("audio shorter than one second")
    return y


def frames(y: np.ndarray, n_fft: int) -> np.ndarray:
    n = 1 + (len(y) - n_fft) // HOP
    idx = np.arange(n_fft)[None, :] + HOP * np.arange(n)[:, None]
    win = np.hanning(n_fft).astype(np.float32)
    return np.abs(np.fft.rfft(y[idx] * win, axis=1))


def onset_envelope(y: np.ndarray) -> np.ndarray:
    spec = np.log1p(100 * frames(y, 1024))
    flux = np.maximum(0, np.diff(spec, axis=0)).sum(axis=1)
    flux = np.concatenate([[0.0], flux])
    k = int(FPS * 0.5)
    trend = np.convolve(flux, np.ones(k) / k, mode="same")
    env = np.maximum(0, flux - trend)
    return env / (env.max() + 1e-9)


def low_energy(y: np.ndarray) -> np.ndarray:
    spec = frames(y, 2048)
    cutoff = int(150 / (SR / 2048))
    e = spec[:, 1:cutoff].sum(axis=1)
    return e / (e.max() + 1e-9)


def estimate_bpm(env: np.ndarray, lo: float, hi: float) -> float:
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    ac = ac / (ac[0] + 1e-9)
    best, best_score = lo, -1.0
    for bpm in np.arange(lo, hi, 0.05):
        score = 0.0
        for m in (1, 2, 4):
            lag = 60 / bpm * FPS * m
            i = int(lag)
            if i + 1 >= len(ac):
                break
            f = lag - i
            score += (ac[i] * (1 - f) + ac[i + 1] * f) / m
        if score > best_score:
            best, best_score = float(bpm), score
    return best


def beat_phase(env: np.ndarray, bpm: float) -> float:
    period = 60 / bpm
    total = len(env) / FPS
    best, best_score = 0.0, -1.0
    for phase in np.arange(0, period, 0.002):
        t = np.arange(phase, total, period)
        f = np.round(t * FPS).astype(int)
        f = f[f < len(env)]
        if not len(f):
            continue
        s = env[f].mean()
        if s > best_score:
            best, best_score = float(phase), s
    return best


def pick_hits(env: np.ndarray, min_gap: float = 0.12, floor: float = 0.35) -> list[float]:
    gap = int(min_gap * FPS)
    hits = []
    last = -gap
    for i in range(1, len(env) - 1):
        if env[i] >= floor and env[i] >= env[i - 1] and env[i] >= env[i + 1] and i - last >= gap:
            hits.append(round(i / FPS, 3))
            last = i
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--bpm", type=float, help="tempo hint; search ±4 around it")
    ap.add_argument("--out", default="beats.json")
    ap.add_argument("--start", type=float, default=0.0, help="offset into the file (seconds)")
    ap.add_argument("--dur", type=float, help="clip length to analyse (seconds)")
    ap.add_argument("--bar", type=int, default=4, help="beats per bar")
    a = ap.parse_args()

    y = load(a.audio, a.start, a.dur)
    env = onset_envelope(y)
    lo, hi = (a.bpm - 4, a.bpm + 4) if a.bpm else (70, 190)
    bpm = estimate_bpm(env, lo, hi)
    phase = beat_phase(env, bpm)
    period = 60 / bpm
    total = (a.dur if a.dur else len(y) / SR)
    beats = np.arange(phase, total, period)

    low = low_energy(y)
    bf = np.round(beats * FPS).astype(int)
    bf = bf[bf < len(low)]
    kick = low[bf]
    offset = int(np.argmax([kick[o::a.bar].mean() if len(kick[o::a.bar]) else 0 for o in range(a.bar)]))
    downbeats = beats[offset::a.bar]

    data = {
        "source": a.audio,
        "bpm": round(bpm, 3),
        "beat": round(period, 5),
        "start": a.start,
        "duration": round(float(total), 3),
        "beats": [round(float(b), 4) for b in beats],
        "downbeats": [round(float(b), 4) for b in downbeats],
        "hits": pick_hits(env),
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print(f"bpm={bpm:.2f} beat={period:.4f}s beats={len(beats)} downbeats={len(downbeats)} hits={len(data['hits'])} → {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
