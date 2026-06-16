---
name: write
description: Use When the user wants bilingual zh/en writing help — refine existing
  text or generate from a prompt. Do Auto-classify input as Refine (Before/After +
  rule annotations) or Generate (finished piece with format/tone note); follow language
  prefix or auto-detect. Trigger On '/write', '潤稿', '寫一篇', '改寫這段'.
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# write — bilingual copywriting assistant

The failure mode this skill prevents: a writer applies copywriting rules inconsistently — spacing around English terms in Chinese, passive constructions buried in prose, comma splices in lists — because the rules exist in a style guide nobody reads during drafting. `/write` is the enforcement pass: hand it existing text and it applies the rule set mechanically; hand it a prompt and it generates a conformant piece from the start.

The body below is English (agent-facing). Operational notifications are Traditional Chinese. Content output language follows the language prefix or auto-detection.

---

## Outcome Contract

- **Outcome**: Per the language prefix (zh/en) or auto-detection, complete one rule-driven refine (Refine) or generation (Generate), with rule application traceable rule by rule.
- **Done when**: Refine output contains Before/After plus per-rule 修正說明 (or Generate output carries a format/tone note), and no rules 5/7/8 (禁對仗句/禁排比/禁名詞化) violations remain.
- **Evidence**: The structure of the output body — Refine's Before / After / 修正說明 three sections with rule tags (or the format/tone note attached to the Generate piece), each item cross-checkable against the embedded rule sets.
- **Output**: The revised or generated piece output in the conversation; operational notifications are Traditional Chinese, content language follows the prefix or detection result.
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

Classify the input as **Refine** or **Generate**.

**Refine** when:
- The input is an existing text body (declarative prose, an email draft, a paragraph, a product description).
- The input contains an explicit refine keyword (潤色、改寫、修改、revise、edit、improve、polish) **paired with** an attached text body.

**Generate** when:
- The input is a request prompt with no attached text body ("幫我寫一封…", "write a…", "draft a…", "compose a…").
- The input is imperative/request in tone and contains no existing text to work on.

**Conflict resolution**: if the input has request-tone phrasing AND contains a refine keyword paired with an existing text body → **Refine wins**. The presence of a refine keyword plus existing content signals user intent more reliably than surface grammatical tone. Example: 「幫我潤色這段：[paragraph]」→ Refine.

When genuinely uncertain (no explicit keyword, no clear existing body) → default to **Generate**. The cost of generating something new is lower than silently discarding user content.

Report classification to the user in one line before proceeding:
- 「偵測到潤色模式（zh／en）」
- 「偵測到生成模式（zh／en）」

---

## Stage 2 — Execute: Refine path

Apply the rule set for the detected language (zh rules or en rules from the embedded sets above).

Also read `references/writing-principles.md` for the detected language and apply applicable style principles. When a style principle triggers a change, add a style tag to the 修正說明 (e.g., `動詞直用`、`具象優先`、`Cut filler`、`Short words`).

Additionally, read context cues (salutation style, register of existing vocabulary, audience implied by content) to infer appropriate tone (formal / conversational) and adjust word choice where the rule set does not dictate a specific change. Tone adjustment is supplementary — it does not override mechanical rule application.

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

After the user replies with their selection, apply only the chosen change points and output the affected fragments (not the full text). This selection step is part of the same Refine pass, not an iterative refinement loop.

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

## Constraints

- Single-pass only. No iterative refinement loop inside the skill. If the user wants a different result, they re-invoke. (The change-points selection reply in long-form Refine is part of the same pass — a pick step, not a refinement loop.)
- Content output language follows the prefix (or auto-detection). Operational notifications are always Traditional Chinese.
- Refine mode never silently applies rules to incompatible-language content. Report the mismatch; do not guess.
- Generate mode vague-topic fallback is always short prose. Do not ask the user to clarify before outputting — produce something and let the user re-invoke with a more specific prompt if needed.
