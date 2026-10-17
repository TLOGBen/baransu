# CLAUDE.md

`baransu` is a Claude Code plugin distributing fourteen governance skills. Theme: バランス — deliberate before executing, verify after.

## Philosophy — バランス (Balance)

**Origin.** The market is full of skills, but they all feel wrong to use: either they govern nothing — the model just runs on its own reading of the request — or the ceremony is so heavy that a one-line change needs five forms filled before any work starts. The first attempt was a home-grown `everything-cli`; finishing it revealed the opposite extreme — it burned tokens fast, and every small task had to clear seven gates before touching the code. Useful, but too heavy. `baransu` is the second attempt.

**Core principle.** Balance is not compromise — the point is knowing *when* to go light and when lightness is not allowed. A small task doesn't need three rounds of alignment; an important decision can't skip thinking. Tools fit the shape of the task: a small task takes the lightweight path, a large one takes the full spec — never the reverse, forcing the task to bend to the tool's process. Every skill carries a clear trigger boundary — what may be skipped, what must always happen. Since v2.1.0 this line is written down as five acceptance-testable principles (README 核心理念). Each binds to an in-repo mechanism — a clause with no anchor is not admitted, and whether the anchor exists is enforced by the structural verifier.

**Fix at the root, and the worth-it test.** Balance is also about *where* a fix lands. A failure is handled at the highest layer that can make it impossible: structure first (what a skill can and cannot do — review never writes, ship acts only when named, an Authorization PAUSE cannot be defaulted), then the principle a skill aims at, and only last a rule it must obey. A rule written where structure would have served is interest paid on a design decision. Before any line is added to a skill, three questions decide whether it is worth it: (1) is there evidence in this repo — a real failure, or a guard already patched onto a symptom — that an existing clause or flow produced the wrong judgment; (2) does the change replace that clause with a more fitting, clearer one — not necessarily more, not necessarily less — rather than add a guard beside it; (3) would the line still change behaviour against today's model default — every instruction has a half-life, routes decay fastest, targets, red lines, evidence and authorization slowest. A line that fails any of the three is not admitted. Mechanism anchor: `/evolve`'s one-finding shape (implicated clause → origin → replacement) and its subtraction gate. Worked example: contract and seal were retired in 8.0.0 not because they were wrong but because their half-life ran out — too much force for a problem the model had stopped having.

## Layout

```
.claude-plugin/
  marketplace.json             # marketplace catalog
plugins/
  baransu/
    .claude-plugin/
      plugin.json              # plugin manifest
    skills/
      think/ review/ write/ ship/ hunt/ health/ read/ learn/ draw/ ui/ codex-skill-transfer/ evolve/ huh/ sayagain/
      _shared/                 # cross-skill references (tdd.md, loop-contract.md, output-journal.md, fact-check.md, modeling.md, selection-telemetry.md, distillation-candidate-matrix.md) + evals/ scripts/
    rules/
      anti-patterns.md         # cross-skill behavioral guardrails
    agents/
      # Perspective: architecture-reviewer.md  quality-reviewer.md  security-reviewer.md  domain-reviewer.md
      # Verify:      verifier.md  (dispatched by review)
      # Health:      health-inspector-context.md  health-inspector-control.md  health-inspector-maintainability.md
      # Evolve:      evolve-diagnostician.md  evolve-judge.md
```

**Critical**: `.claude-plugin/marketplace.json` at repo root is the catalog; `plugins/baransu/.claude-plugin/plugin.json` is the plugin manifest. Never merge them. Components (`skills/`, `agents/`) go at the plugin root (`plugins/baransu/`), not inside `.claude-plugin/`.

## Skills

Invoke with `/baransu:<name>`. Each row says only when to reach for a skill; its flow, outputs and design constraints live in `plugins/baransu/skills/<name>/SKILL.md`, not here — read that file before editing a skill.

| Skill | When to invoke | Not for（易混淆） |
|-------|---------------|------------------|
| `/think` | Deliberate before building: align on a restatement, borrow the discipline that already solved this shape of problem (writing the model per `_shared/modeling.md` when a quantity is at stake), take a stance, verify premises, attack for breakage and for size, present, and leave a five-section plan under `.claude/think/` — never code, never a handoff; a settled decision can be brought for testing (拷問我) | 報錯/debugging → `/hunt`；已定案的中型工作 → 直接實作（`_shared/tdd.md` 紅綠）再 `/review`；單檔小修 → `_shared/tdd.md` §7 |
| `/review` | Independent re-verification of any model output — code, plan, claim — by a fresh verifier agent that never edits the target and asks whether the work did what was asked, added what was not asked, or solved a smaller problem; closes with a verdict computed by a printed rule (PROVEN / PARTLY PROVEN / NOT PROVEN) and 「若只能改一處」; a clean review is a valid result | 審「使用者專案」的 agent 配置與 AI 可維護性 → `/health`；找根因 → `/hunt` |
| `/write` | Bilingual copywriting: `zh`/`en` prefix; Refine (existing text), Generate (new), or Proofread (findings table → `錯字修改.html`) | 寫完要 commit/push 的收尾 → `/ship` |
| `/ship` | Session cleanup: archive `.claude/` working dirs, commit, push, optional worktree removal | 只收尾；不寫作、不審查 |
| `/hunt` | Bug diagnosis: symptom → root cause via observability-first investigation | 「值不值得修」是價值判斷 → `/think` 存廢判決 (Kill/Keep/Pivot) |
| `/health` | Audit the user project's agent configuration and AI-maintainability: budget-aware five-layer audit (config → instructions → tools → verifiers → maintainability), calibrated to evidence and risk rather than repository size | baransu 自身結構驗證 → `scripts/verify-skills.py`；審單次模型輸出 → `/review` |
| `/read` | Read any content into the conversation as Markdown — URL, path, glob, Chrome, `--topic`, `--web`, `--gh`, `--x`; keeps an offline copy under `.claude/read/` only with `--save` | 要消化成筆記 → `/learn`；要畫成圖或動畫 → `/draw` |
| `/ui` | The design lead for the UI in your repo: builds or reshapes web UI with deliberate palette / type / layout / motion choices and writes the files directly; learns a design language from a reference into `.claude/design/reference-<slug>.md`; designs the explanatory pages that embed the components `/draw` produces (handed over automatically in the same turn, or called directly to adjust) | Claude Design 畫布 mockup → 內建 `design` skill；單件圖、影片、機構、互動元件 → `/draw`；小寫 `design.md` 技術架構文件不歸這裡管 |
| `/learn` | Research pipeline: Collect→Digest→Outline→Fill In→Refine; `--brief` stops at Digest | 只要離線原文不要筆記 → `/read --save` |
| `/draw` | Draw one piece as a self-contained visual under `.claude/draw/`: an editorial static diagram (45 types), an explorable interactive map (ten types, validated by `archify finalize`), a code-rendered film, or an interactive component; the only entry point for "draw X" — a request that needs a whole page builds the components and hands them to `/ui` in the same turn without asking | 版面、內文與多圖頁面 → `/ui`（draw 自動交棒；想單獨調整時直接叫 `/ui`）；抓網頁成 Markdown → `/read`；整理成筆記 → `/learn` |
| `/codex-skill-transfer` | Porting reference + parity checklist for hand-maintained Claude Code / Codex copies of a skill, plugin, or marketplace: default mode audits a pair and reports gaps; port-by-hand mode edits the Codex copy on request; optional draft script (`transfer.py`) writes only to a scratch dir | Claude→Codex 對照；不做反向移植 |
| `/evolve` | Improve a SKILL.md against a fixed 9-dim rubric by subtraction: one finding per round names the clause behind an observed failure, the problem it was added for, and a shorter replacement — a new rule must displace one and append-only candidates are refused before judging; forward-only ratchet, blind multi-judge, held-out validation | 寫新 skill 是 authoring 非演化 → 直接撰寫；存廢/價值判斷 → `/think` 存廢判決 (Kill/Keep/Pivot) |
| `/huh` | Restate the last message in plain human language, with no jargon | 潤飾使用者自己的文字 → `/write` |
| `/sayagain` | Restate in plain words what the user's goal is and what problem they are solving, so the user can confirm it was understood | 方向未定、要審議怎麼做 → `/think` |

## Three-band routing

| Band | Route | Closure evidence |
|------|-------|------------------|
| Small — single-file, clear scope | Implement directly under the red/green discipline in `_shared/tdd.md` §7 (維5: behavior tests assert named values, never tautological "responds/all-green"; a broken feature MUST turn a test red); no skill ceremony | red → green run |
| Medium — one feature, few files | Implement directly under the red/green discipline in `_shared/tdd.md`, then `/review` for independent re-verification by a fresh verifier agent (perspectives only for distinct consequential risks); findings are fixed in the main session | red → green run + review verdict |
| Large — ≥2 interdependent modules, context rot is real | Chart the effort as a decision map, slice it, then run each slice through the medium band: implement under `_shared/tdd.md` red/green → `/review` closes it. When the common suite (wayfinder / delegate / strategic-advance) is installed, the charting and the execution MAY route through it — detect first, never assume it is present | per-slice red → green run + review verdict |

Never force a task up-band (a small fix does not deserve a spec) or down-band (a cross-module change does not get to skip criteria pinning).

## Conventions

- **English body.** All agent-facing prose — every `SKILL.md` body, every file under `references/`, the cross-skill docs in `skills/_shared/`, `rules/`, and the agent system prompts in `agents/` — MUST be written in English. The only sanctioned Traditional Chinese is: (1) user-facing output — completion / error / status messages, output-template content, 「」-quoted user strings, sample rendered output; (2) trigger keywords and routing cues in the frontmatter `description` and 易混淆 tables; (3) example artifacts demonstrating Chinese content; (4) the `/write` skill's bilingual-writing content (rules, before/after samples, voice presets). Instructional prose, conditions, branching logic, rationale, and internal headings are English everywhere. Do not change this convention in any skill.
- **Versioning.** `plugins/baransu/.claude-plugin/plugin.json` holds the authoritative version and wins over `marketplace.json`. **Bump on every distributed change** — plugin caching means users won't see updates without a bump. Pick the smallest bump that is true: **major only when an existing user workflow breaks** (a command the user types stops working, or an output they rely on changes shape with no way back); adding a skill, new rules inside a skill, reshaping a skill while its command keeps working, and new tests are minor; fixes are patch. Never lower the version to tidy the history — the plugin cache is keyed by the version string.
- **Commit style.** Conventional commits (`feat`, `fix`, `refactor`, `docs`, `chore`). Attribution lines disabled globally. For new skills, dogfood `/baransu:think`.

## Non-obvious Invariants

These have each caused regressions — do not "optimize" them away:

- **No `skills` array in `plugin.json`**: Claude Code discovers skills from the filesystem. Adding one was done in v0.3.0 and immediately reverted.
- **`/ship` branch deletion uses `-D` not `-d`**: after push the branch is unmerged locally, so `-d` always fails. Both steps need `git -C "$MAIN_REPO" branch -D`.
- **learn's full digest ends with the 批判層 four sections** (來源矛盾點／盲點／信度評分／後續角度): silence is non-compliant — 「查無矛盾」 must be stated affirmatively.
- **read `raw/` is immutable by construction**: recaptures version to `raw/{slug}_vN`, cascade fetches go through `/tmp` then move — never write `raw/` twice.
- **verify-skills.py Gate 10 is the contract** for loop-pauses registry completeness: adding or revising a skill's Automation line must clear it (a `loop=drivable`/`assisted` skill ships `references/loop-pauses.md` and owns a canonical row in `_shared/loop-contract.md` §4 — no orphan files, no dead rows; retiring a skill removes its row in the same change). Gate 11 (`green_proof` field-name consistency) was retired in v4.0.0: all four of its surfaces went with the large-band pipeline, so the gate had nothing left to check. Its number is not reused — the gate list stops at 10.
- **No-git projects: ship fast-fails BEFORE any archive move** — archiving without git would strand the moved files with no commit to anchor them.
- **Cross-skill guardrails**: behavioral anti-patterns that apply across skills live in `plugins/baransu/rules/anti-patterns.md`; the skill-specific invariants above stay here.

## Verification

此 plugin 不寫單元測試，但測試照做。A skill working well has nothing to do with unit tests, a skill failing has nothing to do with them, and when skills change it is the tests that break, not the skills — so since v8.0.0 the repo deliberately keeps no unit tests, ships no build toolchain, and keeps A/B blind-evaluation material out of the repo. Testing still happens, in the forms that do track whether a skill works:

- `make test` — the single stable entrypoint; runs only `scripts/verify-skills.py`, the structural verifier. It is the mechanism anchor the principles above bind to, not a unit test.
- `make parity-check` — runs `scripts/verify-codex-parity.py`, the Codex parity gate.
- `make ship-check` — runs both, in that order, before a release.
- Each skill's `evals/` prompt set, run through `claude plugin eval`.
- A real dogfood run of the changed skill, with its output looked at.

## Install

```
# Local:  /plugin marketplace add /home/vakarve/projects/baransu
# Remote: /plugin marketplace add https://git.hy-tech.com.tw/ben.tsai/baransu.git
/plugin install baransu@baransu
/plugin validate
```
