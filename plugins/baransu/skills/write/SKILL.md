---
name: write
description: Use When the user wants bilingual zh/en writing help — refine existing text, generate from a prompt, or proofread a document into an error-report HTML. Do Auto-classify input as Refine (Before/After + rule annotations), Generate (finished piece with format/tone note), or Proofread (scan for 錯別字／用語不妥／語句不通順 and emit a book-styled 錯字修改.html table); follow language prefix or auto-detect. Trigger On '/write', '潤稿', '寫一篇', '改寫這段', '校對', '找錯字', '抓錯字', 'proofread'. Not for committing or pushing finished text (use /ship) or digesting source material into notes (use /learn or /read).
argument-hint: "[zh|en] [voice=\"…\"] <text=潤稿 | prompt=生成 | file/path=校對>"
user-invocable: true
---

# write — bilingual copywriting assistant

The failure mode this skill prevents: a writer applies copywriting rules inconsistently — spacing around English terms in Chinese, passive constructions buried in prose, comma splices in lists — because the rules exist in a style guide nobody reads during drafting. `/write` is the enforcement pass: hand it existing text and it applies the rule set mechanically; hand it a prompt and it generates a conformant piece from the start; hand it a finished document and it proofreads — surfacing 錯別字／用語不妥／語句不通順 as a reviewable error report rather than silently rewriting.

The body below is English (agent-facing). Operational notifications are Traditional Chinese. Content output language follows the language prefix or auto-detection.

---

## Outcome Contract

- **Outcome**: Per the language prefix (zh/en) or auto-detection, complete one rule-driven refine (Refine), generation (Generate), or document proofread (Proofread), with rule application traceable rule by rule (Refine/Generate) or finding by finding (Proofread).
- **Done when**: Refine output contains Before/After plus per-rule 修正說明 (or Generate output carries a format/tone note), and no rules 5/7/8 (禁對仗句/禁排比/禁名詞化) violations remain; or Proofread has written `錯字修改.html` containing the six-column findings table and reported the file path plus a finding count.
- **Evidence**: The structure of the output body — Refine's Before / After / 修正說明 three sections with rule tags (or the format/tone note attached to the Generate piece), each item cross-checkable against the embedded rule sets; for Proofread, every table row's 錯誤類型 maps to one of the three fixed labels (錯別字／用語不妥／語句不通順) and carries a 建議修正 plus 修改原因.
- **Output**: The revised or generated piece output in the conversation, or — for Proofread — a self-contained `錯字修改.html` file styled with the project's book/Kami design tokens; operational notifications are Traditional Chinese, content language follows the prefix or detection result.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## User-facing language

**Exception to baransu default**: this skill does not output everything in Traditional Chinese.

- **Operational notifications** (mode detected, fallback used, error messages, rule application summary labels): Traditional Chinese (繁體中文).
- **Content output** (the revised text in Refine mode; the generated piece in Generate mode): follows the language prefix (`zh` → Chinese, `en` → English) or auto-detection result.

This exception is intentional. The skill's purpose is language-targeted copywriting; forcing all output to Traditional Chinese would defeat its own goal.

---

## Embedded rule sets

### zh rules (sparanoid compact)

**Application method**: format rules are applied mechanically; style rules are applied by semantic judgment.

#### 格式規則

1. **Spacing**: Add one half-width space between a Chinese character and adjacent half-width ASCII (letters, digits, symbols such as `+`, `%`, `$`). No space before or after full-width punctuation.
2. **Punctuation**: Use full-width punctuation （，。！？；：「」） inside Chinese sentences. Use half-width punctuation in English-only phrases embedded within Chinese text.
3. **Numbers**: Use half-width Arabic numerals (123, not 一二三) for quantities, measurements, dates, and percentages.
4. **Proper nouns**: Preserve original capitalization for brand names, product names, and technical terms (iPhone, GitHub, macOS, Claude Code).

#### 文體規則 — 反 AI 腔

5. **禁用二元對仗句**：「不是X，而是Y」做獨立完整句式時禁用。改用「而」加上具體脈絡（例：「她哀悼的不是過去，而是再也回不去的、還相信故事有結局的童年」）。
6. **避免無感官錨點的抽象金句**：「成長是孤獨的旅程」「內在的真實」這類缺乏感官細節的金句。改法：加入具體可視覺化的細節。檢驗：這段文字能拍成電影嗎？不能 → 缺少感官錨點。
7. **避免純裝飾性的三段排比**：「不是A，不是B，而是C」「願妳X，願妳Y，願妳Z」這類以節奏感為目的的排比。若排比各項有實質內容差異則可保留；純裝飾性的節奏堆疊須打散改寫。
8. **禁用概念名詞化**：「○○感」「○○性」「○○化」的組合（自我的探索、認同感的建構、孤獨的覺察）。改法：改用動詞或具體短語（「找自己」「知道自己是誰」「發現自己很寂寞」）。
9. **禁用飄浮敘事錨點**：「某個午後」「在這個忙碌的城市裡」「我認識一個朋友她」「曾經有個人告訴我」。改法：換成具體時間（上禮拜三下午三點）、具體地點（台北車站三樓的星巴克）、具體人名（我大學同學阿芳）。
10. **「——」軟規則（voice-overridable）**：避免以破折號「——」充當邏輯連接詞（佔據「因為」「所以」「也就是」的位置）。改法：改用明確連接詞，或拆成兩句。此為軟規則，屬 voice cue 段定義的 voice-overridable 類別：voice preset 來源文體正當使用「——」（如節奏停頓、聲音延宕）時，依 preset 保留，不視為違規。

### en rules (compact English copywriting)

1. **Oxford comma**: Include a serial comma before "and" or "or" in lists of three or more items (a, b, and c).
2. **Active voice**: Prefer "We updated X" over "X was updated." Passive is acceptable when the agent is unknown or irrelevant to the meaning.
3. **Sentence length**: Aim for ≤ 25 words per sentence. Split longer sentences at natural conjunctions (and, but, because, which, where).
4. **Parallel structure**: Align grammatical form across list items and paired phrases (all verbs, all nouns, or all adjectives; never mixed).

#### Anti-AI voice

5. **No binary opposition**: Avoid standalone "It's not X, it's Y" sentence constructions that exist purely as rhetorical contrast. Use specific context instead: "She wasn't mourning the past. She was grieving a childhood where stories still had endings."
6. **Anchor claims**: Replace vague time/place/person references ("a friend once told me", "one afternoon", "in this busy city") with specifics: a name, a date, a location. Vague anchors signal fabricated experience.
7. **No nominalization chains**: Prefer verbs and concrete phrases over noun-phrase stacks. "The exploration of one's identity" → "figuring out who you are". "The cultivation of resilience" → "learning to keep going".
8. **Em-dash tiering**: the em-dash U+2014 (—) is hard-banned in en output, with no exceptions. The en-dash U+2013 (–) is banned except inside numeric ranges (pages 3–5, 2010–2020). When a dash would join two clauses, use a period, a colon, or a comma, or restructure into two sentences. (The dash characters in this rule are mentions of the banned glyphs, not uses.)

---

## Stage 0 — Language detection

**Prefix parsing**: the user may prefix the invocation with `zh` or `en`:
- `/baransu:write zh [input]` → zh mode (zh rules + Chinese output)
- `/baransu:write en [input]` → en mode (en rules + English output)
- `/baransu:write [input]` (no prefix) → auto-detect

**Auto-detection rule**: if the input contains any Chinese character (any Unicode CJK block character) → zh. Otherwise → en. The threshold is one character — a single Chinese character is sufficient to trigger zh.

The prefix simultaneously determines the **rule set** and the **output language**. These cannot be set independently via this skill.

**Voice cue (optional, Refine mode)**: alongside the prefix, the user may pass an optional `voice="..."` cue:

- preset name (e.g. `voice="he-cai-tou"`) → if `references/{name}-voice.md` exists, read it as a stylistic reference
- named author or descriptor (e.g. `voice="和菜頭"` or `voice="像和菜頭那種口語部落格"`) → use the string directly as a stylistic reference

When provided, Refine adjusts wording toward the voice while still applying the rule set. Voice cue is **optional**; when omitted, Refine behaves as before. In Generate mode, voice cue is silently ignored.

Rules interact with voice in two semantic classes:

- **Must-not-override floor**: rules 5, 7, 8 (anti-AI 味 floor: 禁對仗句 / 禁排比 / 禁名詞化). Voice cue never overrides these — they continue to apply at every match regardless of voice.
- **Voice-overridable rules**: rules explicitly marked as soft. Currently only zh rule 10 (the 「——」 soft rule) belongs to this class. When the active voice preset's source style legitimately uses the flagged construction (e.g., a preset whose author employs 「——」 as a rhythmic pause), the preset overrides the soft rule for those instances; without such a preset, the soft rule applies normally. A rule joins this class only by being explicitly labeled voice-overridable in its own text — unlabeled rules are never overridable.

**Prefix–content mismatch (Refine mode only)**: if the user's prefix language does not match the actual language of the input text (e.g., `en` prefix with a Chinese-language body, or `zh` prefix with an English-only body), the selected rule set cannot be meaningfully applied. In this case respond:

> 「前綴語言與內容語言不一致，規則集無法套用。請重新呼叫並指定正確前綴，或移除前綴改用自動偵測。」

Do not apply the rule set to incompatible content. Generate mode is **not** affected by mismatch — the prefix determines the language of the generated piece, not the language of the request prompt itself.

---

## Stage 1 — Mode classification

Classify the input as **Refine**, **Generate**, or **Proofread**.

**Refine** when:
- The input is an existing text body (declarative prose, an email draft, a paragraph, a product description).
- The input contains an explicit refine keyword (潤色、改寫、修改、revise、edit、improve、polish) **paired with** an attached text body.

**Generate** when:
- The input is a request prompt with no attached text body ("幫我寫一封…", "write a…", "draft a…", "compose a…").
- The input is imperative/request in tone and contains no existing text to work on.

**Proofread** when:
- The input contains an explicit proofread keyword (校對、校稿、找錯字、抓錯字、挑錯、錯別字、proofread) **paired with** a document or text body to scan.
- The input is a document file path or inline body whose stated intent is to find errors and produce an error report (not to rewrite the text). The defining signal is **report, don't rewrite**: the user wants a list of what's wrong, where, and why — not a corrected version of the prose.

**Conflict resolution** (highest priority wins): **Proofread > Refine > Generate**.
- A proofread keyword paired with a document → **Proofread**, even if a refine keyword is also present (proofreading "report the errors" is a stronger intent signal than "polish this"). Example: 「幫我校對這份文件，找出錯字」→ Proofread.
- Request-tone phrasing AND a refine keyword paired with an existing text body → **Refine wins** over Generate. The presence of a refine keyword plus existing content signals user intent more reliably than surface grammatical tone. Example: 「幫我潤色這段：[paragraph]」→ Refine.

When genuinely uncertain (no explicit keyword, no clear existing body) → default to **Generate**. The cost of generating something new is lower than silently discarding user content.

Report classification to the user in one line before proceeding:
- 「偵測到潤色模式（zh／en）」
- 「偵測到生成模式（zh／en）」
- 「偵測到校對模式（zh／en）」

---

## Stage 2 — Execute: Refine path

Apply the rule set for the detected language (zh rules or en rules from the embedded sets above).

Also read `references/writing-principles.md` for the detected language and, for each principle listed there, apply it if and only if the input contains at least one matching instance; when a principle matches, it MUST emit a style tag to the 修正說明 (e.g., `動詞直用`、`具象優先`、`Cut filler`、`Short words`) — a principle that matched but produced no tag is a missed application.

Additionally, read context cues (salutation style, register of existing vocabulary, audience implied by content) to derive tone, then apply that tone by substituting **register-bearing tokens only** — salutations, closings, and modal/politeness words (e.g. 您好／嗨、敬上／掰、請／麻煩；Dear/Hi, Regards/Cheers, kindly/please). Do NOT alter content nouns or verbs (the words that carry the message's subject matter and actions) for tone reasons — those change only when a mechanical rule dictates it. This bounds tone adjustment to a determinate edit set: the Formal/Conversational Signal→Tone mapping rewrites only the register-bearing slots, never the substance. Derive tone by applying the **same Signal→Tone mapping as Stage 3's Tone-detection table** (no separate criterion): a 正式／商務／business signal → Formal; a 朋友／輕鬆／casual／口語 signal → Conversational; no signal → leave word choice unchanged and apply the mechanical rules only. Tone adjustment is supplementary — it does not override mechanical rule application.

**Long input handling**: when the input has ≥ 5 paragraphs OR ≥ 800 characters (zh) / ≥ 500 words (en), apply rule changes only to the most-impacted instance per rule, not to every match. Example: if rule 2「『的』克制」 finds three sentences each with ≥ 3 「的」, change only the densest sentence and leave the other two alone. This preserves long-form rhythm and prevents the over-trim ("省詞略字") symptom from rule cascades.

Rules 5 / 7 / 8 (anti-AI 味 floor: 禁對仗句 / 禁排比 / 禁名詞化) are exempt from suppression and apply to every match regardless of input length.

**Long-form output: change-points list**: when the Refine output would be roughly 300 lines or longer, do not emit the whole-block Before/After rewrite. A whole rewrite at that size cannot be reviewed as a diff, and re-emitting the full text silently overwrites hand-tuned wording the rules never touched. Instead, emit a change-points list and let the user pick which changes to apply:

```
**變更點清單：**

1. 位置：[第 N 段／約第 X–Y 行]
   原文：[原句逐字引用]
   建議：[修改後的句子]
   理由：[規則標記＋一句說明]

2. …

請回覆要套用的編號（例：「1 3」），或「全部」。
```

After the user replies with their selection, apply only the chosen change points and output the affected fragments (not the full text). If the reply contains numbers outside the listed change-point range, or no parseable selection (non-numeric / empty), then re-display the numbered change-points list once with the operational notification 「選擇編號無效，請回覆清單內的編號（例：『1 3』）或『全部』」 and apply nothing until a valid selection is received; ignore out-of-range numbers within an otherwise-valid reply rather than aborting. This re-display is a within-same-pass clarification of the selection step, not a new iteration. This selection step is part of the same Refine pass, not an iterative refinement loop.

**Boundary between the two long-form mechanisms**: the input thresholds above (≥ 5 paragraphs OR ≥ 800 characters zh / ≥ 500 words en) govern **per-rule suppression** — how many instances each rule may touch. The ~300-line threshold governs **output form** — whole-block Before/After versus change-points list, measured on the would-be output. They are independent and can co-occur: a 6-paragraph, 80-line text gets per-rule suppression with the inline Before/After format; a 350-line text gets per-rule suppression and the change-points format.

**Output format** (outputs below the ~300-line threshold; longer outputs use the change-points list above):

```
**Before:**
[original text verbatim]

**After:**
[revised text]

**修正說明：**
- [規則標記]：[具體改動說明]
- [規則標記]：[具體改動說明]
```

Rule tag examples for zh: `空格規則`、`標點規則`、`數字規則`、`專有名詞`、`語氣調整`、`動詞直用`、`「的」克制`、`具象優先`、`空洞形容詞`、`密度克制`、`禁對仗句`、`感官錨點`、`禁排比`、`禁名詞化`、`敘事錨點`、`破折號軟規則`、`段末總結`、`升華句`、`套話連接`、`voice 套用`.
Rule tag examples for en: `Oxford comma`、`Active voice`、`Sentence length`、`Parallel structure`、`Tone`、`No stale metaphors`、`Cut filler`、`Short words`、`One idea`、`No binary opposition`、`Anchor claims`、`No nominalization chains`、`Em-dash`、`Voice applied`.

If no rules were triggered and no tone adjustment is needed, output:
> 「文字已符合規則，無需修改。」

---

## Stage 3 — Execute: Generate path

Before generating, read `references/writing-principles.md` for the detected language. Apply those principles while composing — do not generate first and revise after.

**Format detection** from topic keywords in the request:

| Signal keywords | Format |
|---|---|
| email, 信, 郵件, 電子郵件, letter | Email (subject line + body) |
| 簡訊, 短訊, SMS, text, message | Short message (≤ 3 sentences) |
| 貼文, post, caption, 社群 | Social post (concise, platform-neutral) |
| All other topics | Short prose (3–5 sentences) |

**Tone detection** from context:

| Signal | Tone |
|---|---|
| 正式, 商務, business, report, proposal, 報告 | Formal |
| 朋友, friend, 輕鬆, casual, chat, 口語 | Conversational |
| No signal | Neutral / professional |

**Vague topic fallback**: if the topic is too vague to determine what to write about (the request gives no subject matter, e.g., "write something" with no further context), generate a short prose piece (3–5 sentences) and append:
> 「主題未明，以短文嘗試呈現。如需調整，請補充主題再重新呼叫。」

When format is not identifiable but the topic is clear, silently default to Short prose (the table row "All other topics" already covers this — no notification needed).

**Output format**:

```
[generated piece]

---
格式：[Email／短訊／短文／社群貼文] ｜ 語氣：[正式／輕鬆／中性]
```

When generating, equally avoid the zh anti-AI-voice patterns above (對仗句、純裝飾性排比、概念名詞化、飄浮錨點).

---

## Stage 4 — Execute: Proofread path

Proofread does not rewrite the document — it **reports** errors as a reviewable table and renders that table to a self-contained HTML file. The primary target is Traditional Chinese (Taiwan) text; en input is supported for the typo / word-choice subset.

### 1. Acquire the source (page tracking is mandatory)

The 頁數 column must be precise, so acquisition must preserve page provenance:

- **PDF** (`.pdf`): read page by page with the Read tool's `pages` parameter, recording each finding's page verbatim from the page being read. If the PDF exceeds 20 pages, read in successive 20-page windows (`pages: "1-20"`, then `"21-40"`, and so on) and accumulate findings from every window into one ordered list keyed by **absolute** page number — never reset the page counter per window, and never stop after the first window. If any window's Read returns no extractable text (scanned or image-only pages), record that page range as 「無法擷取」 in the completion report rather than dropping it silently.
- **Markdown / plain text / inline body**: there is no pagination. Set 頁數 = 「—」 and make 段落／上下文 carry the locating anchor (nearest heading + a verbatim snippet) so the user can still jump to the spot.
- **DOCX / PPTX / other office formats**: convert with `markitdown` (same tool /book Stage 1 uses). If `markitdown` errors out or returns empty / no extractable text for the file (a total conversion failure, distinct from the page-loss case below), do NOT proceed to scan an empty body — that would emit an empty findings table that falsely reads as a clean document. Instead emit the completion-report line 「✅ 校對未執行：{file} 轉換失敗（markitdown 無法擷取內容），請改提供 PDF／Markdown／純文字」 and stop. When conversion succeeds, markitdown drops page boundaries (the usual case), so do NOT attempt to recover or guess a page: set 頁數 = 「—」 for every finding and locate each one entirely through 段落／上下文 (nearest heading + a verbatim snippet). State the page-boundary limitation in the completion report rather than fabricating page numbers.

Never invent a page number. If a finding's page cannot be determined with confidence, write 「—」, not a guess.

### 2. Scan against the error taxonomy

Six author-facing concerns collapse into the **three fixed 錯誤類型 labels** that the output table uses — every finding must carry exactly one:

| Author concern | 錯誤類型 label |
|---|---|
| 錯別字（用錯的字）、漏字（缺字） | **錯別字** |
| 用詞不妥、不符合繁體中文（台灣）商業習慣 | **用語不妥** |
| 贅字（多餘字詞）、語意模糊、語句不通順 | **語句不通順** |

For zh, apply the **Taiwan business-usage lens** on top of typo detection — flag mainland-Chinese or non-idiomatic vocabulary and suggest the Taiwan business-standard term. Anchor examples (not exhaustive): 質量→品質、信息→資訊、軟件→軟體、硬件→硬體、視頻→影片、默認→預設、用戶→使用者、激活→啟用、登錄→登入、屏幕→螢幕、打印→列印、網絡→網路、數據→資料／數據（依語境）、項目→專案、優化→最佳化／優化（依語境）. The zh format/style rule sets embedded above (spacing, punctuation, numbers, anti-AI-voice) are also valid sources of 語句不通順 / 用語不妥 findings.

For en, scan the typo / word-choice subset only (misspellings, wrong-word, awkward phrasing) and map to the same three labels.

**Precision over recall — no false positives.** Report only genuine issues a professional editor would mark. Stylistic preference that is already correct is not an error. If the scan finds nothing, still render the HTML with an explicit 「未發現問題」 state rather than padding the table.

### 3. Build the findings

Each finding is a six-field record matching the output columns exactly:

- **頁數** — precise page, or 「—」 (per §1).
- **段落／上下文** — a verbatim, Ctrl+F-friendly snippet of the surrounding text (the sentence or clause the error sits in), so the user can locate it fast. Include the nearest heading when pages are unavailable.
- **原文內容** — the exact problematic 字詞 only (the smallest span that is wrong), not the whole sentence.
- **錯誤類型** — exactly one of 錯別字 ／ 用語不妥 ／ 語句不通順.
- **建議修正** — the corrected wording.
- **修改原因** — one concise sentence on why (e.g. 「『質量』為大陸用語，台灣商業慣用『品質』」).

### 4. Render to `錯字修改.html` (book visual language, self-contained)

Match /book's Kami visual style **without** routing through the /book pipeline — a proofreading table is analysis output (which /book's "no LLM commentary" red line forbids) and carries no SVG (which /book's quality gate requires). So render directly here:

1. **Palette / type tokens**: read `{project_root}/tokens.css` first line for the preset slug and reuse its canonical color/type tokens, inlined into a `<style>` block so the file opens standalone. If `tokens.css` is absent, fall back to a clean, modern, light-theme palette (neutral paper background, one restrained accent, system-ui / serif reading font) — do not abort; proofread does not depend on `/baransu:design preset` having been run.
2. **Structure**: a single self-contained HTML document — a header (document title + scan summary: total findings and a per-type count), then one `<table>` with the six columns in this order: 頁數 ｜ 段落／上下文 ｜ 原文內容 ｜ 錯誤類型 ｜ 建議修正 ｜ 修改原因. Render 錯誤類型 as a color-coded badge (one hue per label) and wrap the problematic span in 原文內容 with `<mark>` so it stands out. Keep the reading column comfortable and the table zebra-striped for scanability.
3. **No validate-output.ts**: that gate enforces SVG presence and long-form section structure, neither of which applies to a report table. Do not run it; do not add a decorative SVG just to satisfy a gate that is not invoked here.
4. **Write target**: `.claude/write/錯字修改.html` (create `.claude/write/` if absent). Write the full file in one operation. If `.claude/write/錯字修改.html` already exists (a prior proofread of a possibly different document), do NOT silently clobber it: write to `.claude/write/錯字修改-2.html` (then `-3`, …, first free suffix) and report the renamed path in the completion line, so an earlier report is never lost.

### 5. Completion report (Traditional Chinese)

```
✅ 校對完成：.claude/write/錯字修改.html
共 {N} 處：錯別字 {a}｜用語不妥 {b}｜語句不通順 {c}
頁數來源：{PDF 逐頁 ／ 無分頁（以段落上下文定位）}
```

When nothing was found, report 「✅ 校對完成：未發現問題（已產出空表 HTML）」.

## Constraints

- Single-pass only. No iterative refinement loop inside the skill. If the user wants a different result, they re-invoke. (The change-points selection reply in long-form Refine is part of the same pass — a pick step, not a refinement loop.)
- Content output language follows the prefix (or auto-detection). Operational notifications are always Traditional Chinese.
- Refine mode never silently applies rules to incompatible-language content. Report the mismatch; do not guess.
- Generate mode vague-topic fallback is always short prose. Do not ask the user to clarify before outputting — produce something and let the user re-invoke with a more specific prompt if needed.
- Proofread mode reports, never rewrites: it emits the findings table, not a corrected document. It never fabricates a page number — unknown page → 「—」. It never routes through the /book pipeline (analysis output + no SVG would fail book's red line and quality gate); it renders the HTML directly, reusing tokens.css when present and a clean modern fallback when not. Precision over recall: an empty table is correct when the document is clean.
