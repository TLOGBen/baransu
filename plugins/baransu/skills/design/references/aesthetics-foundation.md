# Aesthetics Foundation — 色彩・構成・獨特性 (adopted)

Status: adopted 2026-07-11 — blind A/B experiment, 2 briefs × 2 conditions; the foundation-informed
condition won clearly-better ×2, unanimous.

Purpose: give `/design` a classical grounding that SHARPENS a user's unique aesthetic — never a
substitute for it. Every rule carries a named classical anchor（「— Albers:同色異境」 style）;
each section ends in executable 決策規則. OKLCH (`oklch(L C H)`, L∈0–1) is the derivation space
only — emitted `tokens.css` stays hex (Kami advisory footnote). Two meta-rules govern everything:

- Theory serves the weak moment: apply these rules when a decision stalls, never to override a
  working intuition — knowledge liberates, it does not imprison. — Itten:學理適用於軟弱時刻
- The user's inner palette is legitimate design input, not noise to normalize away. Derive FROM
  the brief; never regress toward the mean. — Itten:主觀色彩音色

## 1. 色彩 — Color

### 1.1 Harmony construction (OKLCH)

Harmony is geometric on the hue wheel, then verified in context — Itten:十二色環和弦:

| Chord | Construction | When |
|---|---|---|
| Dyad (complement) | accent H, counter-hue H±180 | tension between exactly two voices |
| Split-complement | H, H+180±30 | complement energy without vibration |
| Triad | H, H±120 | three equal semantic roles (rare in UI) |
| Analogous | H, H±20~30 | one mood, tonal variation only |

Chord membership says nothing about area: in a token system the chord's non-accent members
usually survive only as *hue-shifted neutrals* (C ≤ 0.02), not as second accents. — Itten:面積對比
Never accept a swatch judged in isolation — a color is only what its neighbors make it; test
every pair on the actual `--paper`/`--surface` it will sit on (a hue picked on white WILL read
differently on parchment). — Albers:同色異境（色彩持續欺騙）
Neutrals are never hue-free: give every gray the paper's (or accent's) hue at C 0.004–0.02 with
one consistent warm/cool direction across the whole ladder — mixed-temperature grays read as two
different papers. Kami's warm neutrals (~H 95) against ink-blue (~H 256) is a temperature
complement, not an accident. — Itten:冷暖對比 + Albers:相對性

### 1.2 Area proportion

Goethe/Itten weight ratios (黃:紅:藍 = 3:6:8) generalize to: the more intense a color, the less
area it may claim. Operational form: sole chromatic accent ≤ 5–8% of rendered surface; the rest
is the neutral ladder. A palette that "needs" a second chromatic accent is a hierarchy failure,
not a color shortage — restate the second emphasis as structural weight (size / value /
isolation). — Itten:面積對比

### 1.3 Contrast floors (value carries legibility)

Of the seven contrasts, 明暗 (light–dark) carries reading; hue contrast without value contrast is
decoration, not hierarchy — Itten:明暗對比. Floors in OKLCH ΔL against the surface behind:

| Role | ΔL floor |
|---|---|
| body / heading text (`--text-primary`) | ≥ 0.60 |
| secondary text (`--text-secondary`) | ≥ 0.50 |
| muted / faint text (`--text-muted` / `--text-faint`) | ≥ 0.40 |
| borders, disabled, decorative | 0.04–0.20 (must NOT reach text floors) |

### 1.4 溫度／文化 connotation table

Temperature is relational (a hue is warm *relative to* its neighbors), and cultural semantics are
the classics' documented blind spot — treat this table as an advisory prior, always overridden by
the brief's own culture. — Itten:冷暖對比；原研哉:白

| OKLCH hue | 溫度 | 西方常見義 | 東亞常見義 | Caution |
|---|---|---|---|---|
| 20–50 (red) | 暖 | 警示、熱情 | 喜慶、吉利 | error-red vs festive-red collision |
| 70–110 (yellow/gold) | 暖 | 警告、廉價 | 尊貴、皇權 | gold ≠ yellow: raise L, cut C |
| 130–170 (green) | 中偏冷 | 成功、環保 | 生機；股市「跌」 | TW/CN finance: 紅漲綠跌 |
| 230–280 (blue) | 冷 | 信任、企業 | 沉靜、墨 | "corporate navy" is the generic trap |
| 300–340 (purple) | 冷 | 奢華、科技 | 神祕 | default AI-gradient hue; avoid unless brief demands |
| achromatic white (L>0.95) | — | 純潔、婚禮 | 喪葬；受納的空 | white as active container, not absence — 原研哉:白 |

### 決策規則（色彩）

1. IF choosing a palette → pick ONE chord geometry (§1.1), THEN demote all non-accent chord
   members to C ≤ 0.02 neutrals. — Itten:和弦＋面積對比
2. IF any chromatic exceeds ~8% surface → it is background, not accent: cut C < 0.05 or
   re-budget. — Itten:面積對比
3. IF colors vibrate or a neutral looks tinted → context shifted it; adjust ON the real surface,
   never in the abstract picker. — Albers:同色異境
4. IF a text/surface pair misses its ΔL floor → fix L first; never "fix" contrast by raising C.
   — Itten:明暗對比
5. IF the brief's culture is East Asian → check semantic colors against the 東亞 column before
   locking `--delta-up`/`--delta-down` and error/success hues. — 原研哉:白（文化語境）
6. IF deriving a palette from scratch → run 採樣→收斂→論證: sample candidate hues from the
   brief's brand / content imagery / cultural context (§1.4), converge in OKLCH to one accent +
   one neutral ladder (per rules 1–2), then write a one-sentence justification per kept color —
   an unjustifiable swatch is not yet derived. — huashu:審美系統重構
7. IF setting chroma → hold the print-ink C bands: large-area base 0.01–0.04, brand/accent
   0.08–0.15, small accents 0.15–0.22; C > 0.25 reads screen-fluorescent — warn before shipping
   it on any paper-like surface. — huashu:審美系統重構

## 2. 構成 — Composition

### 2.1 Hierarchy & perceptual weight

Perception is active structuring: the eye assigns weight by size × value-contrast × isolation ×
position; a page is a field of forces to balance, not a stack of boxes. Cap: 1 primary focal node
per view (may carry the accent) + ≤1 secondary focal carried by structure (scale, weight,
isolation) — never by a second color. — Arnheim:知覺力／中心的力量
Centered symmetry is ceremonial and static (covers, closings); asymmetric flush-left is dynamic
and reads faster for content. Choose per page role; do not mix on one page. — Tschichold:不對稱齊左

### 2.2 Negative space

White space is a compositional ELEMENT with its own job, not leftover margin
— Tschichold:留白作為構圖元素 — and emptiness is a receptive container that generates
communicative energy: an empty region signals「即將被填滿」and concentrates attention on what
borders it. Measurable anchors: reading column ≤ ~68–72ch; section gap ≥ 2× intra-section gap; a
focal element earns emptiness proportional to its importance. — 原研哉:白／空（kizen）

### 2.3 Grouping (Gestalt, measurable)

- Proximity: intra-group gap : inter-group gap ≤ 1:2 — encode as adjacent `--space-*` steps ≥2
  apart. — Gestalt:接近性
- Similarity: same role ⇒ identical style tokens; a style difference IS a semantic claim — never
  vary radius/weight/color without meaning. — Gestalt:相似性
- Continuity: align edges so the eye travels one uninterrupted path; cap ≤ 3 vertical alignment
  axes per page. — Gestalt:連續性
- Figure–ground: every layer must resolve instantly (surface ladder `--paper`→`--surface`→
  `--surface-strong` plus the ΔL floors does this). — Gestalt:圖地關係
- Prägnanz: when two forms carry the same meaning, ship the simpler one. — Gestalt:簡潔律
- Common fate: things that move together read as one group — motion tokens (`--stagger-step`)
  are grouping statements, not garnish. — Gestalt:共同命運

### 2.4 Rhythm & grid

Rhythm = one modular scale (type) + one spacing unit (4pt grid) + deliberate repetition — scale,
rhythm, repetition are themselves the composition. The grid is a starting point that earns
clarity; rigid obedience kills the work — deviate on purpose, once, where the focal point is.
— Müller-Brockmann:節奏與重複（自承網格僵用扼殺創造力）

### 決策規則（構成）

1. IF a view has >2 competing focal nodes → demote by removing color/size, not by adding emphasis
   elsewhere. — Arnheim:知覺力
2. IF page role = cover/closing → symmetry allowed; ELSE asymmetric flush-left. — Tschichold:不對稱
3. IF two blocks are related → their gap ≤ ½ the gap to unrelated blocks; enforce with spacing
   tokens, not eyeballing. — Gestalt:接近性
4. IF an element deviates from the grid → it must be THE focal point and the page's only
   deviation; otherwise snap it back. — Müller-Brockmann:網格作為起點
5. IF a region feels empty → ask what the emptiness frames; add content only if it frames
   nothing. — 原研哉:空
6. IF two designs express the same meaning → ship the one with fewer forms. — Gestalt:簡潔律

## 3. 風格獨特性 — Deriving a UNIQUE aesthetic from the brief

Uniqueness is not added on top; it is what remains after honest subtraction plus one committed
material metaphor — re-seeing the ordinary as unknown is as creative as inventing from zero.
— 原研哉:RE-DESIGN；Rams:Less but better

### 3.1 Mood-to-token derivation (run in order)

1. **Extract** from the brief: 3 mood adjectives + 1 physical material/sense metaphor（紙、墨、
   拉絲金屬、霓虹玻璃、手感…）. If the brief has no material, ask for one — material precedes
   color: start from what it would FEEL like, then derive what it looks like.
   — 原研哉:HAPTIC（觸覺先於形色）
2. **Material → surface ladder**: the material fixes the paper's L and hue temperature
   (parchment → warm, L 0.96, H~95; slate → cool, L 0.25). Derive `--paper`→`--deep-dark` as one
   consistent-temperature L ladder. — Itten:明暗＋冷暖對比
3. **Mood → accent**: adjectives pick the hue region (§1.4); the material picks its C and L (ink
   on paper = low C, deep L; neon = high C, high L). One accent; verify ΔL floors in context.
   — Itten:和弦；Albers:語境驗證
4. **Commit to an extreme**: minimal / maximal / editorial / brutalist — chosen deliberately,
   never defaulted to "safe minimal"; a chosen restraint converges hard, an unchosen one is
   timidity. — Rams:盡可能少（as commitment）；Tschichold:晚年反絕對主義（無唯一有效形式系統）
5. **Write the 我不是什麼 list**: 3–6 anti-patterns this design refuses (cf. Kami's
   no-second-accent / no-italics / no-gradient-bg); every token value must trace to steps 1–4.
   — Rams:徹底到最後細節（沒有任何東西是任意或偶然的）
6. **Honesty check**: the visual promise must match what the product is — no borrowed prestige,
   no trend cosplay; stay quiet enough to leave room for the user's own expression.
   — Rams:誠實的／不張揚的

### 3.2 Anti-generic checklist

Rows below are direction defenses, not absolute bans: each guards the committed direction against
the generic default; a deliberate break is legitimate only when the direction genuinely calls for
the "tell" AND the tradeoff is named in DESIGN.md (a11y floors and CSS-pattern bans never move).

| AI-generic tell | Counter | Anchor |
|---|---|---|
| purple-blue gradient on pure white | flat material-derived paper; hue from brief, not priors | 原研哉:HAPTIC；Itten:主觀音色 |
| 2–3 accents「for variety」 | one accent ≤5–8%; second emphasis = structural weight | Itten:面積對比；Arnheim:知覺力 |
| cool-gray default neutrals | hue-shifted neutrals matching the material's temperature | Itten:冷暖對比 |
| everything centered | asymmetric flush-left except ceremonial pages | Tschichold:不對稱 |
| Inter/Roboto/Arial-first stack as the unexamined default voice | one committed type voice from the material metaphor | Tschichold:字體即立場 |
| cliché hero (giant centered heading + subtitle + two buttons) | layout derived from the content's own structure | 原研哉:RE-DESIGN |
| meaningless roundedness (radius as habit, not form language) | one form language; every radius traces to §3.1 | Gestalt:簡潔律 |
| evenly-weighted card grid, no focal point | 1 primary + ≤1 secondary focal per view | Arnheim:中心的力量 |
| glassmorphism blur / decorative depth | depth as restrained, systematic elevation only | Rams:不張揚；Gestalt:圖地 |
| filler space「因為留白是好的」 | emptiness must frame something; else it is waste | 原研哉:空（受納） |
| unexplained values（radius 12「感覺對」） | every token traces to derivation steps 1–4 | Rams:沒有任何東西是任意的 |

### 決策規則（獨特性）

1. IF the brief is thin → run §3.1 step 1 as questions to the USER; never substitute training-set
   defaults for a missing answer. — Itten:主觀色彩音色
2. IF a proposed value could appear unchanged in any random project → it is not yet derived;
   re-trace it to the material metaphor or delete it. — Rams:徹底到細節
3. IF tempted to add (a color, a font, an effect) → first try expressing it with what exists; add
   only when subtraction and restatement both fail. — Rams:Less but better
4. IF the system starts claiming universal validity（「這才是對的設計」）→ stop; it is a system
   FOR this brief, portable nowhere without re-derivation. — Tschichold:晚年反絕對主義
5. IF choosing type → pair one characterful display face (`--font-display`) with one refined body
   face (`--font-sans` / `--font-serif`); never let the same generic family serve both roles.
   — Tschichold:字體即立場

## 4. 與 tokens 的接線 — Wiring rules onto the canonical vocabulary

How each rule lands on the canonical 38(+5) names (see `canonical-tokens.md`):

| Token group | Governing rule | Anchor |
|---|---|---|
| `--paper` `--surface` `--surface-strong` `--dark-surface` `--deep-dark` | one L-ladder, single temperature, from the material metaphor (§3.1-2); figure–ground resolves at each step | Itten:明暗＋冷暖；Gestalt:圖地 |
| `--accent` `--accent-on` | sole chromatic, ≤5–8% surface; `--accent-on` clears ΔL ≥ 0.60 on accent fills | Itten:面積對比＋明暗 |
| `--ink` `--text-primary`…`--text-faint` | 4-step value hierarchy at ΔL floors 0.60/0.50/0.40/0.40; hierarchy by L, never by hue | Itten:明暗對比 |
| `--border` `--border-soft` | the sub-text contrast rung (ΔL 0.04–0.20): structure, not voice | Gestalt:圖地關係 |
| `--font-sans` `--font-serif` `--font-mono` `--font-display` | one committed voice per design; aliasing is the commitment mechanism (cf. Kami sans→serif) | Tschichold:字體即立場 |
| CJK 排印 (`--font-serif` stack + tracking + measure) | pair an explicit CJK serif after the Latin reading serif in the stack; scope negative letter-spacing to Latin runs only — never CJK; CJK line-length 22–38 漢字; line-height splits by context — screen reading 1.7–1.8 (Waza) vs print 1.50–1.55 (Kami), the preset context decides | Waza:CJK 排印；huashu:審美系統重構 |
| modular scale (perfect fourth r=1.333) | typographic rhythm = musical proportion; never flatten H1:body below ~2.3× | Müller-Brockmann:節奏與重複 |
| `--space-xs`…`--space-3xl` (4pt grid) | proximity ratios: related ≤ ½ unrelated, encoded as ≥2 scale steps apart; grid deviation only at THE focal point | Gestalt:接近性；Müller-Brockmann:網格作起點 |
| `--radius-*` | one consistent form language; a radius break is a semantic claim | Gestalt:簡潔律＋相似性 |
| `--shadow-ring` `--shadow-whisper` `--shadow-drama` | depth as restrained system (2 shadows + 1 declared drama), never decorative blur | Rams:不張揚 |
| `--grid-columns` `--grid-gutter` `--cover-title-align` | asymmetry default: `--cover-title-align: left` unless the page is ceremonial | Tschichold:不對稱；Arnheim:中心 |
| `--delta-up` `--delta-down` | semantic pair checked against the 文化 table（TW/CN 紅漲綠跌） | 原研哉:文化語境 |
| `--ease` `--duration` `--stagger-step` | motion groups elements — things moving together read as one; no ornamental loops | Gestalt:共同命運；Rams:盡可能少 |

### 決策規則（接線）

1. IF gen-mode derives token values → each value must cite which §3.1 step produced it; a value
   with no derivation line fails review. — Rams:沒有任何東西是任意或偶然的
2. IF a preset needs a second chromatic (semantic states aside) → refuse; restate as neutral
   structural weight, following the sanctioned-exception pattern (documented, scoped, singular —
   cf. Kami `.tag.breaking`). — Itten:面積對比
3. IF checking a finished tokens.css → run: neutral temperature consistency (§1.1), ΔL floors
   (§1.3), accent area budget (§1.2), focal-node cap (§2.1), and presence of the 我不是什麼 list
   (§3.1-5). Any miss = the aesthetic foundation is not yet wired. — Albers:在語境中驗證
