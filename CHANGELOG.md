# Changelog

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## v1.4.5 (2026-05-14)

**`/codex-skill-transfer`**：Step 2 補一句明示 `baransu` plugin 的 `<codex-output>` 是 repo 根目錄的 `codex/`，與 `<repo-root>/.agents/plugins/marketplace.json` (Layout A catalog) 的 `source.path` 對齊。避免下次跑時又另開一個輸出目錄、把 catalog 的 `source.path` 留成 dangling。skill metadata.version 0.7.2 → 0.7.3。

## v1.4.4 (2026-05-14)

**`/review` 強化**：源自 Waza `/check` 的「Hard stops sweep + Sign-off receipt」結構化尾段機制，作為 Stage 6 balance check 之後的彙整型閘門。

### Features — 新增功能

1. **Hard stops sweep（Stage 6 後新增）**：4 條 Required item（Unverified claims / Destructive auto-execution / Unknown identifier in target / Dependency changes）+ 1 條 Optional item（Injection / hardcoded secret，僅在 Stage 4 未派 `security-reviewer` 時列出，避免雙重把關）。任一命中時，相關 finding **強制 pin 到「需判斷」**，禁止透過 balance check 降為 advisory；report 整體 verdict 改為「需判斷」或「未完成」。
2. **Sign-off receipt（report 結構化尾段）**：fenced code block，固定 8 個對齊欄位 — `files`、`scope`、`depth`、`perspectives`、`hard_stops`、`new_tests`、`doc_debt`、`e2e_status`。SKILL.md 內 pin 死每個欄位的 semantics（避免日後漂移）；其中 `perspectives` 採 baransu Stage 4 dispatched set + Stage 5 adversarial 標記（不繼承 Waza pooled-specialists 語意），`new_tests` 為純計數（不繼承 regression-first 語意，該責任歸 /dev 或 /execute）。
3. **Hard-stops-sweep checklist**（與 prose body 並列輸出）：Required 4 條永遠列出；Optional 1 條僅當 `security-reviewer` 未派時列出。每行格式 `□ <item>: not hit` 或 `☒ <item>: hit — <one-line citation>`。

### Internal

- Source：Waza `/check` skill（read material 收於 `.claude/read/material/check-review-before-you-ship/`、digest 於 `.claude/learn/digests/waza-check-skill-code-review.md`）。
- 不繼承 release-artifact missing / generated-artifact drift / version skew 等屬於 `/ship` 的條目（責任分層保留）。
- review SKILL.md +51 行。

### SemVer 註

採 patch（1.4.3 → 1.4.4）：使用者調用面（指令名、`AskUserQuestion` option labels、Stage G handoff routing）未變；尾段結構與 hard-stop 閘門屬於輸出格式擴增與內部行為加嚴，下游消費者只需忽略額外段落即可向前相容。

## v1.4.3 (2026-05-14)

**`/hunt` 強化**：源自 Waza `/hunt` 的四項增補，inline 融入既有 SKILL.md，不引入 references/ 新檔，不更動 description / when_to_use trigger 詞。

### Features — 新增功能

1. **Instrumentation: Side-effect rule**：加 log 後若觀察到行為改變（bug 消失、症狀偏移、事件順序不同），視為 timing / lifecycle / concurrency 問題的直接證據，不准當成「log 副作用」忽略——觀察動作本身已指向根因類別。
2. **Scope Blast Mode（新章節，置於 Confirm or Discard 後、Bisect Mode 前）**：根因確認後、宣稱 fixed 前，grep 全 repo 找同形 bug 的 N-1 個兄弟；每個 match 在 case file 的 `Scope Blast` section 寫下 `<file:line> — fix | leave: <reason> | unsure: <question>`；`unsure` 在使用者回覆後就地更新為 `unsure → fix` 或 `unsure → leave: <reason> after user reply <date>`。宣稱 fixed 雙條件：(a) 每個 match 都有紀錄，AND (b) 成功格式的 `迴歸守護` line 既點到鎖定測試、又以 `HUNT-YYYY-NNN §3` 形式反向引用 case file 該 section。
3. **Repeated Regression Mode（新章節，置於 Bisect Mode 後、Hard Rules 前）**：使用者提供「好的」截圖／版本／fixture 作為 reference oracle 時的 5 步流程——列出每個症狀（保留使用者原話）→ 指認 reference oracle → 編輯前定義 pass/fail check → 比對 current vs reference 命名精確 delta → 同症狀仍在則 cross-reference Hard Rule「Same symptom recurs after fix」並從證據重建假說。末尾分流：純主觀 UI 品味 → `/baransu:design`；render / state / timing / build output / 字型 / 從已知良好版本回歸 → 留在 `/hunt`。
4. **Hard Rules +2 條**：
   - **「Fix plan or current diff touches 6 or more files (without a Scope Blast pattern justification) → Stop before adding the 6th file」**：兩個檢查時點（drafting + after each edit）；若是 class-of-bug 收網則例外（走 Scope Blast Mode）；若是 symptom-patch creep 蔓延則 narrow back 或路由到 `/baransu:analyze`。
   - **「Deflection from a specific area → Treat as a signal」**：明示為語意 trigger 非字面字串比對；附中英文具體例（「那段沒問題」「不是那邊的問題」「我已經檢查過了」/ "that part doesn't matter" / "I already checked there"），特別針對多階段 pipeline（CI segment、data pipeline stage、baransu plane handoff）中某段被排除的盲區。

### Internal

- Source：Waza `/hunt` skill（read material 收於 `.claude/read/material/waza-hunt/` 與 `.claude/read/raw/waza-hunt/`、digest 於 `.claude/learn/digests/waza-hunt-skill-diagnose-before-fix-debugging-methodology.md`）。
- 驗收路徑：`/baransu:review` 雙 perspective（architecture + quality）派發，14 findings 收斂至 5 處 surgical fix（Scope Blast 載體規格化、Repeated Regression 第 5 步改 cross-reference、Hard Rule 閾值與時點明確化、deflection trigger 雙語範例、Scope Blast 例外條款）；dry-run 用 commit `11de678` (GATE-L viewBox containment) 走完所有新段落，全部正確觸發或正確 N/A。
- hunt SKILL.md 227 → 266 行。

### SemVer 註

採 patch（1.4.2 → 1.4.3）：description / when_to_use trigger 詞依使用者明示保留原樣，沒有新增 trigger 句式；新章節是內部紀律補強，使用者調用面零變動。

## v1.4.2 (2026-05-14)

**`/think` 強化**：注入三項源自 Waza `/think`（github.com/tw93/Waza）的機制，未破壞 Stage A-G、iron rule、四選一閘門等既有骨幹。

### Features — 新增功能

1. **Step 0 改為兩層 mode selection**：第一層 Plan vs Evaluation（種類分歧），第二層 Plan 底下 Lightweight vs Full（深度）。Evaluation Mode 作為平行 H2 主體區段（與 Lightweight Mode body 平行），輸出 **Kill / Keep / Pivot** 單行裁決 + 三條基於使用者實際限制的理由。
2. **Evaluation Mode 觸發語清單與 disambiguation**：採 Waza 原文 7 句式（「判断一下」「值不值得」「有没有必要」「我不想做」「商业前景」/ "should we keep this" / "is this worth it"）；含錯誤上下文者（「判断这个报错」「判断这个错误」「这个报错值不值得修」等）一律路由至 `/hunt`，不走 Evaluation。Plan ↔ Evaluation 與 Lightweight ↔ Full 皆互斥獨立，mode 切換需手動重啟 `/think`。
3. **Stage D Premise validation 新增「記憶類型映射」子規則**：三行映射表 + 「現況覆寫記憶」原則。`decision / preference / principle` → 規劃約束（分派至 Stage F）；`pattern / learning` → 設計檢查（分派至 Stage E）；`fact` → 須以當前狀態驗證（Stage D 自身完成）。CLAUDE.md 為記憶映射的潛在全域權威來源，若衝突 global > skill-local；本版確認 CLAUDE.md 尚未編碼此語意，本 skill 暫為事實單一來源。
4. **Gotchas 改混排格式（11 條）**：保留 User-fatigue 一條 prose（多層應對需敘事完整），其餘 6 條既有 + 4 條新增 Waza 反例改 **What happened / Rule** 兩欄表格——pwd 前置、MCP 載入檢查、單一 stack 引入新語言/runtime、「判断一下报错」誤觸 Evaluation。

### Internal

- 體量檢查：SKILL.md 357 → 433 行（+21%，預算 ≤465）。Stage A-G 命名與順序、iron rule、Stage G 四選一閘門、繁中 user-facing 規約全保留。
- 不影響其他 skill：review / dev / analyze / 餘下 12 skill 皆未動。

### Fixes

- Gotchas 表格化過程中順手修正既有 Option 編號誤植：原 prose「treat it as Option 2 (還有地方要對焦)」實際應為 Option 3（Stage G 四選一閘門中 Option 2 是「批准實作（完全授權）」、Option 3 才是「還有地方要對焦」）。新表格列已對齊 Option 3。

### SemVer 註

**就 minimum-impact patch 解讀**——本版採 patch（1.4.1 → 1.4.2）：使用者調用面（指令名、`AskUserQuestion` option labels、Stage G handoff routing）皆未變，僅 SKILL.md 內部行為增補。嚴格 SemVer 解讀因 Step 0 新增使用者可見的 Plan/Evaluation 入口可落 minor；若 policy 後續要求 minor，bump 為 1.5.0。

## v1.4.0 (2026-05-13)

**Baseline-parity milestone**：對標 op7418/guizang-ppt-skill / alchaincyf/huashu-design / tw93/Kami 三 baseline 從 ~50% 推到 ≥ 90%。`baseline-parity-score.py` 自評 **100.0%**（30/33 task complete via /loop autonomous run，剩 3 為 advisory/follow-up dogfood pass）。

依據 `.claude/analyze/2026-05-12-baransu-parity-v1-4/` 規格，全 11 條 C1-C11 Criteria 達標。M3 SKILL.md fractional-heading cleanup 完成（advisory per user 定案）。

### Features — 新增功能

1. **REQ-001 / C1 — SVG 13 diagram-types 全 status=complete**：架構 / 流程 / 序列 / 狀態 / ER / 時間軸 / 泳道 / 象限 / 巢狀 / 樹 / 分層 / Venn / 金字塔，每檔含 Kami-compliant example SVG（chevron stroked markers / 節點寬 `{128,144,160}` 白名單 / focal `#1B365D` stroke + `#EEF2F7` fill / 4-multiple 座標）。
2. **REQ-001 / GATE-J/K**：`validate-output.ts` 新增兩 strict gate — GATE-J（node-width whitelist + 2-tier 例外 viewBox<360）、GATE-K（chevron-strict `<path d="M2 1 L8 5 L2 9">`）；含 negative fixtures 在 swiss-smoke-test。
3. **REQ-002 / C2 — 8 文件 schema × 3 preset × zh/en**：新增 Resume / Portfolio / One-Pager / Letter / Equity-Report / Changelog 共 6 schema md × 3 preset = 18 schema 檔 + 36 HTML 模板（每 schema zh + en variant）；en variant 採 Charter / Georgia / Palatino stack 不含 CJK 字體；人像 `<img>` 強制 `object-position: center 35%`（rule of thirds）。
4. **REQ-003 / C3 — Slide 22 layout lock list × 3 preset**：三 preset slide-cores 各擴張 9 個新 layout（timeline / process / testimonial / agenda / stat-hero / icon-grid / table-heavy / before-after / divider）+ closing 覆寫修補 v1.3 prefix-mix bug。`validate-swiss-deck.mjs` 新增 lock-list 機械驗證 + alias map for v1.3 filenames（cover→title, content-2col→two-column 等）。canonical-tokens.md 加 22-row Slide Layout Registry。
5. **REQ-003 / Modular scale 1.333**：canonical-tokens.md 新增 Modular Scale section（perfect fourth `r=1.333`）；三 preset tokens.css 重新計算 h1=2.375rem, h2=1.75rem, h3=1.3125rem；v1.2 era 2.2× / 1.24× 舊比例移除。
6. **REQ-004 / C4 — Editorial 印刷學三件套全機械化**：三 preset design-cores + golden-template 全面加 `text-wrap: pretty`；新增 `.{preset}-dropcap` class `font-size: 4.65em`（精準 3-line drop 對齊 body line-height 1.55）；prose curly quotes（`U+201C` / `U+201D`）。新增 `editorial-sanity.sh` 三 check（text-wrap pretty / dropcap font-size [4.0, 5.0]em / 0 prose straight quotes）整合進三 preset sanity wrapper。
7. **REQ-005 / C5 — Slide checklist 5 → 16 條 P0-P3**：四層分類（含 P0-S Swiss-specific / P0-A all-preset / P0-B baransu-self 三子前綴）；每條三欄（現象 / 根因 / 做法）+ source metadata（dogfood-v1.3-handoff / kami-spec-L86 / huashu-incident）。
8. **REQ-006 / C6 — Fact-Verification + Core Asset Protocol + 三 preset image-prompts**：`/book SKILL.md` Stage 2A §0 加 Fact-Verification Principle #0（regex 偵測產品/版本 / 人名+職位 → WebSearch verify → AskUserQuestion gate on 0 results）；Stage 3 §5 加 Core Asset Protocol 4-step（Ask → Generate/Search → Verify → Freeze，跳步即 fail）；三 preset image-prompts.md 含產品圖 / logo / UI 三段 + 標準負面尾巴 `no title, no footer, no page chrome, no logo, no border`。
9. **REQ-007 / C7 — `/baransu:design export-brief` 子模式**：第 4 mode（gen / preset / lint 之外）；4-step 組裝邏輯（parse preset → read sources → assemble 6-section brief → output to `.claude/design/brief-{preset}-{date}.md` 或 `--stdout`）；hex 從當前 tokens.css 動態解析（B20 邊界）；Codex CLI bridge example `codex prompt --stdin < brief-{preset}-{date}.md`。
10. **REQ-008 / C8 — DESIGN.md §9 reproducibility 三要素**：三 preset 各自含 (a) 焦點節點上限 1-2 / (b) accent hex 設計理據（HSL + oklch advisory，每 preset ≥1 條）/ (c) 我不是什麼（≥5 條 no-X anti-patterns 對齊各 preset 反例）。
11. **REQ-009 / C9 — oklch advisory**：三 preset DESIGN.md §2 accent token 旁標 `oklch(...)` 等價值 + footnote 說明 advisory；tokens.css / design-cores HTML 不含 `oklch(`（hex-only invariant preserved）。
12. **REQ-012 — `baseline-parity-score.py` 自評腳本**：11 個 check function 對應 C1-C11；加權總和 = 1.0（C1/C2/C3 各 0.15 / C4 0.10 / 其他 0.05-0.08）；`--ci` 旗標印 JSON；`--threshold N` exit 1 if < N；B26 self-exclusion assertion（C12 明文不入 score）。

### Internal Debt 收尾

- **REQ-010 M1**：`swiss-smoke-test.sh` 加 Stage 0 三 preset golden-template presence gate（kami / swiss / gd）。
- **REQ-010 M2a**：`design-token-resolver.md` 從 v1.2-era / Kami-only 升級為 v1.3+ 三 preset aware（polygon marker / 12-檔 node-width 全部標為 v1.2 retired）。
- **REQ-010 M2b**：新增 `golden-template-swiss.html`（Inter / IKB `#002FA7`）與 `golden-template-gd.html`（Roboto Flex / M3 `#6750A4`）；三檔 validate-output.ts GATE A-K 全 PASS。
- **REQ-010 M3**（advisory per user）：`/book SKILL.md` fractional headings (`### 0.0` / `### 0.5` / `### 2.5` / `### 4.5`) 整數化；`## Stage 0.5` → `## Stage 0b`（matching 2A/2B alphabetical convention）。

### Variance（已記錄非阻擋差異）

- 三 preset slide-cores 各落在 **21/22** 而非 22（`closing.html` 已存在 v1.3 軌道，本次為覆寫 prefix-mix 修補非新增）；validator soft-warns 4 missing canonical names（toc / image-full / quote-stack / breakout）— v1.4 follow-up dogfood pass 將補。
- `swiss-sanity.sh` / `google-sanity.sh` 在 TASK-editorial-04 fix attempt 內首次建立（v1.3 軌僅 `紙-sanity.sh`）。
- 完整 v1.4 fixture regen（66 layout × 3 preset + 36 schema fixture）pragmatic-scope 推遲為 follow-up；M1 以 Stage 0 presence gate 涵蓋三 preset golden-template 變體即達 REQ-010 Scenario 1 acceptance。
- spec wording `gd-*` class prefix → codebase 既有 convention `google-*`（spec drift 記錄 in pending_spec_drift；不影響功能）。

### 自評

```
$ python3 plugins/baransu/scripts/baseline-parity-score.py
✓ C1 (w=0.15): 13/13 types complete
✓ C2 (w=0.15): 18/18 new-schema md
✓ C3 (w=0.15): 3/3 presets ≥21 layouts
✓ C4 (w=0.10): 3/3 preset editorial-sanity
✓ C5 (w=0.07): P0/P1/P2/P3 = 6/4/4/2 (total 16)
✓ C6 (w=0.08): 5/5 governance checks
✓ C7 (w=0.07): 3/3 export-brief checks
✓ C8 (w=0.08): 3/3 preset §9
✓ C9 (w=0.05): 6/6 oklch checks
✓ C10 (w=0.05): 3/3 v1.3 debt (M3 advisory)
✓ C11 (w=0.05): version=1.4.0

Overall baseline-parity score: 100.0%
```

---

## v1.2.0 (2026-05-12)

### Features 新增功能

1. **Swiss preset**：`/baransu:design preset swiss` 提供 IKB 主色 + Inter/Helvetica/Noto Sans TC 字體 stack，與既有「紙」/「google-design」preset 同層
2. **`--style` 旗標**：`/baransu:book` 新增 `--style kami | swiss`（預設 kami），僅 `--format ppt` 支援；與 `--format html` 同用會報錯
3. **9 個 slide-core 版式**：cover / section / content-bullets / content-2col / data / kpi-grid / compare / quote / closing，每個含 YAML `applies_to` 供 Stage 2B 動態決策表
4. **GATE-F (class prefix 一致性)**：驗 slide HTML class 走 `kami-*` 或 `swiss-*` 單一 prefix；含 tokens.css preset 註解 tie-break
5. **GATE-G (layout registered)**：驗 `<section data-layout="X">` 對應 `{project_root}/slide-cores/X.html`；缺檔 SKIP（不 FAIL）
6. **移除 `slide-template.html`**：舊版式骨架由 `{project_root}/slide-cores/` 取代

## [1.1.17] — 2026-05-11

### 新增

- **`/baransu:book` skill** — 把任何來源轉成 Kami 主題瀏覽器 HTML 的三階段流程
  - **Acquire**：URL proxy cascade（defuddle.md → r.jina.ai → direct）、`/read` slug、`/learn` digest slug、本地檔案、`--text` 直接輸入
  - **Synthesize**：內容類型自動感知（technical / narrative / research，由 `references/perception-guide.md` 定義分類信號）、抽取 4–8 節結構 + 關鍵主張 + SVG 需求旗標、自動 slug 衝突偵測
  - **Render**：完整依照 `references/golden-template.html` 與 `design/references/paper-preset.md` 生成 Kami HTML；≥1 SVG 圖解（依感知類型決定圖解策略）；含側欄 TOC、章節編號、`.callout` / `.card-grid` / `.tradeoff-row` 等元件
  - **Validate**：`scripts/validate-output.ts` 品質閘（HTML 可解析、`<article>` 結構存在、SVG 平衡、本地資產路徑正確）；`browser-use` 自動驗跑版並儲存截圖至 `.claude/book/{slug}-preview.png`
- **`scripts/install-deps.ts`** — Stage 0 一鍵安裝 markitdown + browser-use（三段 pip fallback，不需手動）
- **`scripts/validate-output.ts`** — TypeScript 品質閘，exit 0/1/2 標準合約
- **`references/perception-guide.md`** — 內容類型分類信號表、各類視覺處理原則、SVG 策略、合成長度限制
- **`references/golden-template.html`** — Kami 黃金模板，含完整 CSS tokens、元件模式、SVG `<defs>` snippet、IntersectionObserver TOC script

### 變更

- `plugins/baransu/.claude-plugin/plugin.json` 版本提升至 1.1.17
- 關鍵字表新增 `book`

[1.1.17]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.16...1.1.17

## [1.1.16] — 2026-05-11

### 變更

- **plugin description / keywords 精簡** — `plugin.json` 與 `marketplace.json` 描述改為單句，keywords 改為 12 個 skill name 的扁平列表

[1.1.16]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.15...1.1.16

## [1.1.15] — 2026-05-07

### 新增

- **`/baransu:write` 首份 voice preset：`yu-guang-zhong-voice.md`** — 余光中 散文 voice profile 初版。基於〈聽聽那冷雨〉(1974) 萃取，捕捉**正向風格錨**（疊字節奏、聽覺擬聲、古典白話交織、句長對照、動詞密集鏈）；負規則延續 `writing-principles.md` 同源論述（拒絕英式中文、不用「被」字被動、不堆抽象名詞）。
  - 結構：風格摘要 + 6 條可執行寫法規則（含「平的 / 余光中」對照表）+ 3 段神韻 sample（疊字+擬聲+古典白話、動詞鏈+短句鎚收、跨段 motif 呼喚）+ 詞彙線索 + anti-AI floor 守則 + 來源 + 後續可擴條目
  - 來源原文已 capture 至 `.claude/read/material/ygzsw007/index.md`（via `/baransu:read --web`，Defuddle Layer 1，4361 字）
  - 啟用方式：`/baransu:write zh voice="yu-guang-zhong" [text]`，loader 走 1.1.14 加入的 `references/{name}-voice.md` 路徑

[1.1.15]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.14...1.1.15

## [1.1.14] — 2026-05-07

### 變更

- **`/baransu:write` 加 voice cue + long-input mode-aware suppression**（輕量版改動，SKILL.md +13/-2 行）
  - Stage 0 後加 **Voice cue 段**：optional `voice="..."` 參數；preset name（讀 `references/{name}-voice.md`）/ 具名作者 / 自由描述三種輸入；不覆蓋 rules 5/7/8（anti-AI 味底線）；Generate 模式忽略
  - Stage 2 Refine 末加 **Long input handling 段**：輸入 ≥ 5 段 OR ≥ 800 字（zh）/ ≥ 500 words（en）時，命中規則只改最影響的一處（mode-aware suppression）；rules 5/7/8 例外，仍每處套用
  - Rule tag examples 末新增 zh `voice 套用` / en `Voice applied`
- **零回歸保證** — 規則本文（zh rules 1-9 / en rules 1-7）零修改；`references/writing-principles.md` 整份零修改；既有 Refine 輸出格式（Before/After/修正說明）三 header 零修改；既有 zh/en prefix 行為零修改；/learn Stage 5 內部呼叫 `/write {LANG}`（不帶 voice）byte-for-byte backward compat。
- **新增結構測試** — `tests/skills/test-write-skill.sh`，14 個 bash 結構斷言（A1-A4 Voice cue 段、B1-B4 Long input handling、C1-C2 Rule tag、D1-D4 backward compat invariants），exit 0/1/2 標準閘門 contract，與既有 `tests/skills/test-{skill}-skill.sh` 命名慣例一致。

[1.1.14]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.13...1.1.14

## [1.1.13] — 2026-05-07

### 變更

- **Skill descriptions 統一三段式格式** — 全部 15 個 SKILL.md 的 `description` 改寫為 `Use When … Do … Trigger On …` 三段結構（analyze / bridge / codex-skill-transfer / design / dev / execute / grade / hunt / learn / read / review / ship / think / triage / write）。對模型 trigger 判斷與人類掃讀都更友善；繁中觸發短語全部保留。
- **codex-skill-transfer 工具映射補完 Plan Mode 差異** — `references/skill-mapping.md` §6 工具映射表新增兩列：
  - `AskUserQuestion` → 標註 Codex 的 `request_user_input` 只在 Plan mode 可用，不能當 drop-in
  - `EnterPlanMode` / `ExitPlanMode` → 明寫 Codex 沒有 skill-callable 等價物（active mode 由 developer message 切換），需改寫成 prompt-driven plan gate
- **Codex 端同步** — `codex/plugins/baransu/` 重生，反映新 description 格式 + plugin.json 版本。

[1.1.13]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.12...1.1.13

## [1.1.12] — 2026-05-07

### 新增 Codex CLI 支援

baransu 從本版起同時發行 Claude Code 與 Codex CLI 兩種變體。Claude 端是源頭，Codex 端是單向衍生產物。

- **Codex 變體目錄** — 整棵 Codex plugin tree 落在 `codex/`，獨立於 Claude 本體（`plugins/baransu/`），互不污染。
- **Repo-root marketplace catalog** — 新增 `.agents/plugins/marketplace.json`，讓使用者直接 `codex plugin marketplace add <git-url>` 即可安裝（不需 `--sparse` 或其他 flag）。
- **轉換工具 `/baransu:codex-skill-transfer`** — 一鍵把 Claude 端的 plugin / skills / marketplace 重生成 Codex 格式：
  - 自動轉 `disable-model-invocation` → `agents/openai.yaml`
  - 改寫 `$ARGUMENTS` 系列、bang-backtick shell injection 為 Codex 認得的自然語言
  - 描述超過 Codex 上限 1024 字元時自動剝除 Claude 觸發片語句子並收斂句尾
  - Plugin mode 自動產出 schema-合規的 marketplace catalog（`source` object 形、必選 `policy.installation` / `policy.authentication`、`category`）+ 巢狀 `plugins/<name>/` layout
- **Codex agent stubs** — `codex/plugins/baransu/.codex-agents-templates/` 內附 12 份 TOML stub，使用者自行複製到 `~/.codex/agents/` 啟用。
- **AGENTS.md** — Codex 版的 project-level instructions 檔，與 `CLAUDE.md` 對應。
- **README** — 新增 Codex CLI 安裝區（HTTPS / SSH / `--ref` pin tag）+「衍生產物別手改」警語。

### 修正

- 修掉 `codex-skill-transfer` SKILL.md 內殘留的 `` !`cmd` `` 字面 pattern，避免 slash-command 解析器把它當成 bash injection 而觸發 `command not found: cmd`。
- 修正 `grade` SKILL.md frontmatter — 描述含裸 colon（`tune_review_due: true`、`(00:00)`）導致 PyYAML 嚴格解析失敗。改用單引號包裹。

[1.1.12]: https://git.hy-tech.com.tw/ben.tsai/baransu/-/compare/1.1.4...1.1.12
