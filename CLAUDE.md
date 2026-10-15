# CLAUDE.md


`baransu` is a Claude Code plugin distributing twelve governance skills. Theme: バランス — deliberate before executing, verify after.

## Philosophy — バランス (Balance)

**Origin.** The market is full of skills, but they all feel wrong to use. Either they govern nothing — the model just runs on its own reading of the request — or the ceremony is so heavy that a one-line change needs five forms filled before any work starts. The first attempt was a home-grown `everything-cli`. Finishing it revealed the opposite extreme: it burned tokens fast, and every small task had to clear seven gates before touching the code. Useful, but too heavy. `baransu` is the second attempt.

**Core principle.** Balance is not compromise — the point is knowing *when* to go light and when lightness is not allowed. A small task doesn't need three rounds of alignment; an important decision can't skip thinking. Tools fit the shape of the task: a small task takes the lightweight path, a large one takes the full spec — never the reverse, forcing the task to bend to the tool's process. Every skill carries a clear trigger boundary — what may be skipped, what must always happen. Since v2.1.0 this line is written down as five acceptance-testable principles. Each binds to an in-repo mechanism — a clause with no anchor is not admitted, and whether the anchor exists is enforced by the structure verifier.

## Layout

```
.claude-plugin/
  marketplace.json             # marketplace catalog
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # plugin manifest
    skills/
      think/ review/ write/ ship/ hunt/ health/ read/ learn/ draw/ ui/ codex-skill-transfer/ evolve/
      _shared/                 # cross-skill references (tdd.md, loop-contract.md, output-journal.md, fact-check.md, selection-telemetry.md, distillation-candidate-matrix.md) + evals/ scripts/
    rules/
      anti-patterns.md         # cross-skill behavioral guardrails
    agents/
      # Perspective: architecture-reviewer.md  quality-reviewer.md  security-reviewer.md  style-reviewer.md  domain-reviewer.md
      # Verify:      verifier.md  (dispatched by review)
      # Health:      health-inspector-context.md  health-inspector-control.md  health-inspector-maintainability.md
      # Evolve:      evolve-diagnostician.md  evolve-judge.md
```

**Critical**: `.claude-plugin/marketplace.json` at repo root is the catalog; `plugins/baransu/.claude-plugin/plugin.json` is the plugin manifest. Never merge them. Components (`skills/`, `agents/`) go at the plugin root (`plugins/baransu/`), not inside `.claude-plugin/`.

## Skills

Invoke with `/baransu:<name>`. To edit a skill, read its `SKILL.md` — design constraints live there, not here.

| Skill | When to invoke | Not for（易混淆） |
|-------|---------------|------------------|
| `/think` | Deliberate before building: align on a restatement of what the user wants, borrow the discipline that already solved that shape of problem (verbs → field → instrument → outside judge → what it changes; skipped for parameter choices and single-file changes), take a stance that names the goal behind the goal, the design's one idea and cost against effect, verify premises, attack for breakage and for size (excess hiding in abstraction or defence, and under-reach), present, and leave a five-section plan under `.claude/think/` — never code, never a handoff; a settled decision can be brought for testing (拷問我) | 報錯/debugging → `/hunt`；已定案的中型工作 → 直接實作（`_shared/tdd.md` 紅綠）再 `/review`；單檔小修 → `_shared/tdd.md` §7 |
| `/review` | After any model output — code, plan, claim — for independent re-verification: a fresh verifier agent asks whether the work did what was asked, added what was not asked (guards, layers, options), or solved a smaller problem than asked; perspectives only for distinct consequential risks; a one-screen diff takes the fast path; never edits the target; a clean review is a valid result | 審「使用者專案」的 agent 配置與 AI 可維護性 → `/health`；找根因 → `/hunt` |
| `/write` | Bilingual copywriting: `zh`/`en` prefix; Refine (existing text), Generate (new), or Proofread (findings table → `錯字修改.html`) | 寫完要 commit/push 的收尾 → `/ship` |
| `/ship` | Session cleanup: archive `.claude/` working dirs, commit, push, optional worktree removal | 只收尾；不寫作、不審查 |
| `/hunt` | Bug diagnosis: symptom → root cause via observability-first investigation | 「值不值得修」是價值判斷 → `/think` 存廢判決 (Kill/Keep/Pivot) |
| `/health` | Audit the user project's agent configuration and AI-maintainability: budget-aware five-layer audit (config → instructions → tools → verifiers → maintainability) | baransu 自身結構驗證 → `scripts/verify-skills.py`；審單次模型輸出 → `/review` |
| `/read` | Read any content into the conversation as Markdown — URL, path, glob, Chrome, `--topic`, `--web`, `--gh`, `--x`; keeps an offline copy under `.claude/read/` only with `--save` | 要消化成筆記 → `/learn`；要畫成圖或動畫 → `/draw` |
| `/ui` | The design lead for the UI in your repo: builds or reshapes web UI with deliberate palette / type / layout / motion choices and writes the files directly; learns a design language from a reference (site, screenshot, art style) into `.claude/design/reference-<slug>.md` and refines an existing UI against it; designs explanatory pages (explain X with figures, a tutorial, several figures read together) that embed the components `/draw` produces — taken over from `/draw` automatically in the same turn, or called directly to adjust | Claude Design 畫布 mockup → 內建 `design` skill；單件圖、影片、機構、互動元件 → `/draw`；小寫 `design.md` 技術架構文件不歸這裡管 |
| `/learn` | Research pipeline: Collect→Digest→Outline→Fill In→Refine; `--brief` stops at Digest | 只要離線原文不要筆記 → `/read --save` |
| `/draw` | Draw one piece as a self-contained visual: an editorial static diagram (44 types, HTML + inline SVG → `<slug>.html` + `.svg`/`.png`), an explorable interactive map (architecture / workflow / sequence / data flow / lifecycle, validated by `archify finalize` → `<slug>.map.html`), a code-rendered film (`<slug>.film.html` with `seek(t)` → `<slug>.mp4`, camera moves, springs, beat grid, synthesized sound), or an interactive component (mechanism figure, draggable or animated figure → `<slug>.html`); the only entry point for "draw X" — when the request needs a whole page (explain X, a tutorial, several figures read together) it builds the components and hands them to `/ui` in the same turn without asking; state the plan in one status line, build, look (contact sheet / screenshots / receipt), score, fix, deliver under `.claude/draw/` | 版面、內文與多圖頁面 → `/ui`（draw 自動交棒；想單獨調整時直接叫 `/ui`）；抓網頁成 Markdown → `/read`；整理成筆記 → `/learn` |
| `/codex-skill-transfer` | Porting reference + parity checklist for hand-maintained Claude Code / Codex copies of a skill, plugin, or marketplace: default mode audits a pair and reports gaps; port-by-hand mode edits the Codex copy on request; optional draft script (`transfer.py`) writes only to a scratch dir. | Claude→Codex 對照；不做反向移植 |
| `/evolve` | Improve a SKILL.md against a fixed 9-dim rubric by subtraction: each round names the clause behind an observed failure, the problem it was added for, and a shorter replacement — a new rule must displace one and append-only candidates are refused before judging; forward-only ratchet, blind multi-judge, held-out validation | 寫新 skill 是 authoring 非演化 → 直接撰寫；存廢/價值判斷 → `/think` 存廢判決 (Kill/Keep/Pivot) |

**12 is the skill-count ceiling** — adding a 13th requires retiring one first (以裁換建). Mechanism anchor: the skill-count check in `scripts/verify-skills.py`. The ceiling was 14 until v8.0.0, when the contract and seal skills were retired without replacement. Falsifiable amendment clause (2026-07-19, originally 14→15, carried over): if selection telemetry shows `/codex-skill-transfer` at zero use for three consecutive months, retire it and restore the ceiling to 11.

**Three-band routing**:

| Band | Route | Closure evidence |
|------|-------|------------------|
| Small — single-file, clear scope | Implement directly under the red/green discipline in `_shared/tdd.md` §7 (維5: behavior tests assert named values, never tautological "responds/all-green"; a broken feature MUST turn a test red); no skill ceremony | red → green run |
| Medium — one feature, few files | Implement directly under the red/green discipline in `_shared/tdd.md`, then `/review` for independent re-verification by a fresh verifier agent (perspectives only for distinct consequential risks); findings are fixed in the main session | red → green run + review verdict |
| Large — ≥2 interdependent modules, context rot is real | Chart the effort as a decision map, slice it, then run each slice through the medium band as defined above: implement that slice under `_shared/tdd.md` red/green → `/review` closes it. When the common suite (wayfinder / delegate / strategic-advance) is installed, the charting and the execution MAY route through it — detect first, never assume it is present | per-slice red → green run + review verdict |

Never force a task up-band (a small fix does not deserve a spec) or down-band (a cross-module change does not get to skip criteria pinning).

**English-body convention.** All agent-facing prose — every `SKILL.md` body, every file under `references/`, the cross-skill docs in `skills/_shared/`, `rules/`, and the agent system prompts in `agents/` — MUST be written in English. The only sanctioned Traditional Chinese is: (1) user-facing output — completion / error / status messages, output-template content, 「」-quoted user strings, sample rendered output; (2) trigger keywords and routing cues in the frontmatter `description` and 易混淆 tables; (3) example artifacts demonstrating Chinese content; (4) the `/write` skill's bilingual-writing content (rules, before/after samples, voice presets). Instructional prose, conditions, branching logic, rationale, and internal headings are English everywhere. Do not change this convention in any skill.

## Non-obvious Invariants

These have each caused regressions — do not "optimize" them away:

- **No `skills` array in `plugin.json`**: Claude Code discovers skills from the filesystem. Adding one was done in v0.3.0 and immediately reverted.
- **`/ship` branch deletion uses `-D` not `-d`**: after push the branch is unmerged locally, so `-d` always fails. Both steps need `git -C "$MAIN_REPO" branch -D`.
- **learn's full digest ends with the 批判層 four sections** (來源矛盾點／盲點／信度評分／後續角度): silence is non-compliant — 「查無矛盾」 must be stated affirmatively.
- **read `raw/` is immutable by construction**: recaptures version to `raw/{slug}_vN`, cascade fetches go through `/tmp` then move — never write `raw/` twice.
- **verify-skills.py Gate 10 is the contract** for loop-pauses registry completeness: adding or revising a skill's Automation line must clear it (a `loop=drivable`/`assisted` skill ships `references/loop-pauses.md` and owns a canonical row in `_shared/loop-contract.md` §4 — no orphan files, no dead rows; retiring a skill removes its row in the same change). Gate 11 (`green_proof` field-name consistency) was retired in v4.0.0: all four of its surfaces went with the large-band pipeline, so the gate had nothing left to check. Its number is not reused — the gate list stops at 10.
- **No-git projects: ship fast-fails BEFORE any archive move** — archiving without git would strand the moved files with no commit to anchor them.
- **Cross-skill guardrails**: behavioral anti-patterns that apply across skills live in `plugins/baransu/rules/anti-patterns.md`; the skill-specific invariants above stay here.

## Install

```
# Local:  /plugin marketplace add /home/vakarve/projects/baransu
# Remote: /plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git
/plugin install baransu@baransu
/plugin validate
```

## Versioning

`plugins/baransu/.claude-plugin/plugin.json` holds the authoritative version. **Bump on every distributed change** — plugin caching means users won't see updates without a bump. `plugin.json` wins over `marketplace.json`.

Pick the smallest bump that is true. **Major only when an existing user workflow breaks**: a command the user types stops working, or an output they rely on changes shape with no way back. Adding a skill, new rules inside a skill, reshaping a skill while its command keeps working, and new tests are minor; fixes are patch. Never lower the version to tidy the history — the plugin cache is keyed by the version string.

## Verification

此 plugin 不做任何單元測試。A skill working well has nothing to do with unit tests, a skill failing has nothing to do with them, and when skills change it is the tests that break, not the skills — so since v8.0.0 the repo deliberately keeps none (the `tests/ab/` A/B blind-evaluation material for `/ui` is prompts and results, not tests). The plugin ships no build toolchain. `make test` is the single stable entrypoint and now runs only `scripts/verify-skills.py`, the structural verifier — it is the mechanism anchor the principles above bind to, not a unit test. `make parity-check` runs `scripts/verify-codex-parity.py`; `make ship-check` runs both.

## Commit Style

Conventional commits (`feat`, `fix`, `refactor`, `docs`, `chore`). Attribution lines disabled globally. For new skills, dogfood `/baransu:think`.
