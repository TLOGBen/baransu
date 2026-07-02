#!/usr/bin/env python3
"""Color-distance validation tool (REQ-002, TASK-shared-01).

Advisory-only, non-blocking colorblind-simulation distinguishability check
for a list of hex colors. Called by both `/design` (baking candidate
chart-category colors into tokens.css) and `/book` (re-validating the
color subset actually selected for one chart) — see
plugins/baransu/skills/_shared/scripts/ as the shared home for a tool
genuinely used by two skills.

Usage:
    python3 color_distance.py "#hex1,#hex2,..."

Prints a single JSON object to stdout and always exits 0 — this is an
advisory tool; it has no mechanism to abort the caller's generation
pipeline (goal.md: 建議優先, not a hard gate).

Methodology (independently reimplemented; no runtime dependency on any
resource outside baransu): convert each color from hex to linear sRGB,
apply the Machado/Oliveira/Fernandes (2009) full-severity protanopia /
deuteranopia / tritanopia simulation matrices, convert the simulated
color to CIELAB (D65 white point), and compute CIE76 dE (Euclidean
distance in Lab) between each adjacent pair under each simulation. The
reported per-pair "distance" is the worst (minimum) dE across the three
simulations — a pair must survive every deficiency type to be genuinely
safe.

Reference thresholds (methodology adapted from the dataviz bundled
skill's validate_palette.py CVD check; only the raw dE computation and a
non-blocking qualitative label are ported here, not its full six-check
suite):
    distance >= 12.0  -> "adequate" (comfortably distinct)
    distance >=  8.0  -> "marginal" (usable only with secondary encoding)
    distance <   8.0  -> "low"      (not reliably distinguishable)

Fewer than 2 colors, or any invalid hex token, short-circuits to a
status of "unverifiable" with a human-readable reason — this path never
raises, per the "MUST NOT throw an unexpected error" constraint.
"""
from __future__ import annotations

import json
import re
import sys

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

CVD_TARGET = 12.0
CVD_FLOOR = 8.0

# Machado, Oliveira & Fernandes (2009) full-severity (1.0) CVD simulation
# matrices, applied to linear sRGB.
_CVD_MATRICES = {
    "protan": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deutan": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritan": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}

# Linear sRGB -> XYZ, D65 white point.
_RGB_TO_XYZ = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)

_D65_WHITE = (0.95047, 1.0, 1.08883)


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _hex_to_linear_rgb(hex_color: str) -> tuple[float, float, float]:
    r = int(hex_color[1:3], 16) / 255.0
    g = int(hex_color[3:5], 16) / 255.0
    b = int(hex_color[5:7], 16) / 255.0
    return (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b))


def _apply_matrix(matrix, rgb) -> tuple[float, float, float]:
    a, b, c = (
        max(0.0, min(1.0, sum(matrix[row][col] * rgb[col] for col in range(3))))
        for row in range(3)
    )
    return (a, b, c)


def _lab_f(t: float) -> float:
    delta = 6.0 / 29.0
    if t > delta ** 3:
        return t ** (1.0 / 3.0)
    return t / (3 * delta ** 2) + 4.0 / 29.0


def _linear_rgb_to_lab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = _apply_matrix(_RGB_TO_XYZ, rgb)
    xn, yn, zn = _D65_WHITE
    fx, fy, fz = _lab_f(x / xn), _lab_f(y / yn), _lab_f(z / zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return (L, a, b)


def _delta_e_76(lab1: tuple[float, float, float], lab2: tuple[float, float, float]) -> float:
    return sum((c1 - c2) ** 2 for c1, c2 in zip(lab1, lab2)) ** 0.5


def _worst_case_distance(hex_a: str, hex_b: str) -> float:
    rgb_a = _hex_to_linear_rgb(hex_a)
    rgb_b = _hex_to_linear_rgb(hex_b)
    distances = []
    for matrix in _CVD_MATRICES.values():
        lab_a = _linear_rgb_to_lab(_apply_matrix(matrix, rgb_a))
        lab_b = _linear_rgb_to_lab(_apply_matrix(matrix, rgb_b))
        distances.append(_delta_e_76(lab_a, lab_b))
    return min(distances)


def _advisory_label(distance: float) -> str:
    if distance >= CVD_TARGET:
        return "adequate"
    if distance >= CVD_FLOOR:
        return "marginal"
    return "low"


def compute_color_distances(colors: list[str]) -> dict:
    """Pure computation: colors in -> advisory distinguishability data out.

    Never raises. Fewer than 2 colors, or any invalid hex token, returns a
    "unverifiable" status with pairs=[] and a human-readable reason.
    """
    if len(colors) < 2:
        return {
            "status": "unverifiable",
            "reason": f"fewer than 2 colors provided (received {len(colors)})",
            "colors": colors,
            "pairs": [],
        }

    for token in colors:
        if not HEX_RE.match(token):
            return {
                "status": "unverifiable",
                "reason": f"invalid hex color format: {token!r}",
                "colors": colors,
                "pairs": [],
            }

    pairs = []
    for color_a, color_b in zip(colors, colors[1:]):
        distance = _worst_case_distance(color_a, color_b)
        pairs.append({
            "color_a": color_a,
            "color_b": color_b,
            "distance": round(distance, 2),
            "advisory_label": _advisory_label(distance),
        })

    return {
        "status": "computed",
        "colors": colors,
        "pairs": pairs,
    }


def _parse_colors(raw: str) -> list[str]:
    return [token.strip() for token in raw.split(",") if token.strip()]


def main() -> int:
    raw = sys.argv[1] if len(sys.argv) > 1 else ""
    colors = _parse_colors(raw)
    result = compute_color_distances(colors)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
