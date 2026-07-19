# analyze + execute 改革規格（動刀清單）— 驗證 arm 注入源

依據：十格矩陣實驗 + 決策日誌因果分析。目標：讓 Opus+Sonnet 組合（p2-os′ / p3-os′）
追平或超越 p3-f（20/21 釘死、0 引入 bug）。驗證通過後移植到 baransu SKILL.md。

---

## A. 兩個 skill 對不同模型的價值結算（含「反而拖後腿」清單）

### 對 Sonnet（實作者角色）
- **真價值**：外部化的不變量 + 規定死的輸出格式（前饋兩招）。Sonnet 逐字照辦的
  服從性是資產——格式裡沒有數字欄位，它就寫不出 idx+1。
- **拖後腿**：儀式性文書（red_proof 謄寫、checklist 填表）稀釋注意力卻不改變盲點；
  鬆條文給了它「我全過了」的虛假完成感（p3-os 的 Sonnet 真心以為自己達標）。

### 對 Opus（規格／審查角色）
- **真價值**：審查授權——但唯有條文釘死時才兌現。Opus 4.7+ 的字面主義是雙面刃：
  條文死＝最忠實的執法者；條文鬆＝最守規矩的橡皮圖章（p3-os：看見缺陷仍按契約放行）。
- **拖後腿**：四層語意判級在鬆條文下反而成為「合法放行」的正當化管道；
  Opus 寫規格的本能是「警語」不是「條文」（p2-os 警語救了場但靠運氣）——
  需要結構強制它昇華成可斷言條文。

### 對 Fable（或任何頂級單體）
- **真價值**：只剩獨立審查（抓自盲）。規格對它是把腦內狀態重新序列化一遍——
  p2-f 用 $16.45 證明了自寫自用的規格增量趨近於零。
- **拖後腿**：整套 analyze 五層為自用而寫是負報酬；p1-f 16 分鐘 vs p2-f 25 分鐘，
  品質同樣是 1 個 med bug。

### 通用死重（實測零效果，全模型）
design.md 完整技術設計層（架構分全體天花板）、Stage 6 三 subagent 規格審查（單自審
無損失）、summarize-agent 與逐 task ctx 檔（直讀規格無損失＋轉抄鏈引入新錯誤類別）、
Red gate 儀式本身（測試品質由 test.md 驅動；P2 無 Red gate 同得 9 分）、
worktree DAG（檔案不相交時純開銷）、smart-friend（零發動）、重試上限 >1（僅用過一次）。

### 主動有害（比沒有更糟）
1. 鬆條文 + 全套流程 ＝ 虛假信心機器（p3-os：全綠儀表板 + 全場唯一 HIGH）。
2. 同模型自寫自用五層規格 ＝ 純成本（p2-f）。
3. 常數轉抄鏈（brief→spec→ctx→impl 逐層重打字）＝ 新增錯誤類別（「节」消失）。

---

## B. 改革條款（注入驗證 arm 的英文原文）

### B1. analyze 五刀

**R1 — Criteria Assertability Gate (goal.md C{n})**
> Every acceptance criterion MUST name an assertable value. For any criterion about
> user-facing text (CLI output, TUI toast, error message): substring-contains wording
> is FORBIDDEN — the criterion must either (a) prescribe the EXACT output format with
> placeholders (e.g. 「進度已遷移：{chapter_name}」, no other numeric field permitted)
> or (b) carry an explicit prohibition list (e.g. "the message MUST NOT contain any
> number derived from a chapter idx"). A criterion that a reviewer could not use to
> REJECT a defective implementation is a spec bug — rewrite it before handoff.

**R2 — Trap-to-Criterion Promotion**
> Every hidden invariant or data-shape trap you discover while reading the code
> (non-dense indexes, abort semantics, encoding quirks) MUST be promoted into BOTH:
> (a) a prohibition-style criterion in goal.md, and (b) a required pinning test named
> in test.md. A warning sentence in the handoff prose alone is NON-COMPLIANT — warnings
> depend on the implementer's memory; criteria empower rejection.

**R3 — Verbatim Constants Block**
> Collect every fixed algorithm string given by the requirements (regexes, format
> strings, character classes, magic literals) into a fenced block titled
> `## Verbatim Constants` in design.md. The implementer MUST copy-paste from this
> block, never retype. The final reviewer MUST byte-diff each constant in the
> implementation against this block.

**R4 — User-Facing Surface Inventory**
> Enumerate EVERY user-facing output surface the change touches (each CLI println,
> each TUI toast, each error path) in a table: surface → exact format (per R1) →
> pinning test name. Include a cross-UI consistency row: when CLI and TUI express the
> same outcome, the spec MUST require a single shared formatting helper, pinned by
> tests on BOTH call paths (a test that mirrors the format function without invoking
> the real handler path does not count as pinning).

**R5 — Ceremony Cuts**
> design.md is reduced to: a layer-placement table (which file/layer each change
> lives in), the data-model delta, and the Verbatim Constants block. No prose
> architecture narrative. Stage-6 review is ONE self-review pass with a checklist:
> every C{n} passes R1; every discovered trap passed R2; surface inventory complete
> (R4); constants block complete (R3). No per-task ctx files — the handoff is the
> spec itself plus a ≤20-line summary.

### B2. execute 四刀

**R6 — Review Mandate Rewrite (the reviewer's job description)**
> Review each task in this order:
> 1. Criteria audit: check every acceptance criterion by its LITERAL wording.
> 2. Untested-surface scan (MANDATORY): enumerate user-visible behaviors introduced
>    by this task (messages, toasts, error paths, wiring). For each, verify at least
>    one test would FAIL if that behavior broke — verify by reasoning about the test's
>    call path (a mirror-test that reimplements the format function does not count);
>    when in doubt, run a quick mutation. Any unpinned user-visible behavior =
>    `packaged confirm (correctness)` — NEVER advisory.
> 3. Cross-UI consistency: same outcome on CLI and TUI must route through the shared
>    helper required by the spec; divergent copies = correctness finding.
> 4. Verbatim-constant byte-diff: diff every constant against the spec's Verbatim
>    Constants block; any drift = correctness finding.

**R7 — Loose-Criterion Escalation (kills the p3-os failure mode)**
> If you observe a REAL defect (wrong user-visible output, self-contradicting message,
> data-shape misuse) but the acceptance criteria are too loose to justify rejection:
> this is a SPEC BUG, not a pass. Return `packaged confirm (correctness)` citing both
> the defect AND the loose criterion; the orchestrator records a criteria patch.
> "The spec doesn't forbid it" is never grounds to pass an observed defect.

**R8 — Ceremony Cuts (execute side)**
> Red gate demoted to advisory: capture a failing-first run when natural (it is free
> evidence), but its absence is not a blocker; test quality is enforced by test.md
> anchors + the reviewer's mutation spot-checks. No summarize-agent, no per-task ctx.
> Retry cap = 1 per task (a second failure escalates to the orchestrator).

**R9 — Final Review Additions**
> Besides REQ/C{n} coverage: (a) re-run the verbatim-constant byte-diff across the
> whole tree; (b) audit the R4 surface inventory — every row's pinning test exists,
> is green, and pins the REAL call path.

---

## C. 驗證設計

- 基線：同 bfa0f46、同 EXPERIMENT-BRIEF.md、新 worktree exp2-p2os / exp2-p3os。
- p2-os′ ＝ Opus 規格（含 R1–R5）→ Sonnet 實作。不設審查——檢驗改革後的純前饋上限。
- p3-os′ ＝ 同上規格 → Sonnet 實作（R8 紀律）→ Opus 審查（R6–R7 任務書）→ final（R9）。
- 盲評：同評審協定（fable、四維、突變抽查），代號 ARM-11 / ARM-12。
- 成功判準：p3-os′ ≥ p3-f（20/21、0 bug）；p2-os′ 視為前饋上限的觀測值。
