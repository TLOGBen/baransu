---
name: write
description: Use When the user wants bilingual zh/en writing help — refine existing text or generate from a prompt. Do Auto-classify input as Refine (Before/After + rule annotations) or Generate (finished piece with format/tone note); follow language prefix or auto-detect. Trigger On '/write', '潤稿', '寫一篇', '改寫這段'.
---

# write — bilingual copywriting assistant

The failure mode this skill prevents: a writer applies copywriting rules inconsistently — spacing around English terms in Chinese, passive constructions buried in prose, comma splices in lists — because the rules exist in a style guide nobody reads during drafting. `/write` is the enforcement pass: hand it existing text and it applies the rule set mechanically; hand it a prompt and it generates a conformant piece from the start.

The body below is English (agent-facing). Operational notifications are Traditional Chinese. Content output language follows the language prefix or auto-detection.

---

## User-facing language

**Exception to baransu default**: this skill does not output everything in Traditional Chinese.

- **Operational notifications** (mode detected, fallback used, error messages, rule application summary labels): Traditional Chinese (繁體中文).
- **Content output** (the revised text in Refine mode; the generated piece in Generate mode): follows the language prefix (`zh` → Chinese, `en` → English) or auto-detection result.

This exception is intentional. The skill's purpose is language-targeted copywriting; forcing all output to Traditional Chinese would defeat its own goal.

---

## Embedded rule sets

### zh rules (sparanoid compact)

**套用方式**：格式規則機械套用；文體規則依語義判斷。

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

### en rules (compact English copywriting)

1. **Oxford comma**: Include a serial comma before "and" or "or" in lists of three or more items (a, b, and c).
2. **Active voice**: Prefer "We updated X" over "X was updated." Passive is acceptable when the agent is unknown or irrelevant to the meaning.
3. **Sentence length**: Aim for ≤ 25 words per sentence. Split longer sentences at natural conjunctions (and, but, because, which, where).
4. **Parallel structure**: Align grammatical form across list items and paired phrases (all verbs, all nouns, or all adjectives — not mixed).

#### Anti-AI voice

5. **No binary opposition**: Avoid standalone "It's not X, it's Y" sentence constructions that exist purely as rhetorical contrast. Use specific context instead: "She wasn't mourning the past — she was grieving a childhood where stories still had endings."
6. **Anchor claims**: Replace vague time/place/person references ("a friend once told me", "one afternoon", "in this busy city") with specifics: a name, a date, a location. Vague anchors signal fabricated experience.
7. **No nominalization chains**: Prefer verbs and concrete phrases over noun-phrase stacks. "The exploration of one's identity" → "figuring out who you are". "The cultivation of resilience" → "learning to keep going".

---

## Stage 0 — Language detection

**Prefix parsing**: the user may prefix the invocation with `zh` or `en`:
- `/baransu:write zh [input]` → zh mode (zh rules + Chinese output)
- `/baransu:write en [input]` → en mode (en rules + English output)
- `/baransu:write [input]` (no prefix) → auto-detect

**Auto-detection rule**: if the input contains any Chinese character (any Unicode CJK block character) → zh. Otherwise → en. The threshold is one character — a single Chinese character is sufficient to trigger zh.

The prefix simultaneously determines the **rule set** and the **output language**. These cannot be set independently via this skill.

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

**Output format**:

```
**Before:**
[original text verbatim]

**After:**
[revised text]

**修正說明：**
- [規則標記]：[具體改動說明]
- [規則標記]：[具體改動說明]
```

Rule tag examples for zh: `空格規則`、`標點規則`、`數字規則`、`專有名詞`、`語氣調整`、`動詞直用`、`「的」克制`、`具象優先`、`空洞形容詞`、`密度克制`、`禁對仗句`、`感官錨點`、`禁排比`、`禁名詞化`、`敘事錨點`.
Rule tag examples for en: `Oxford comma`、`Active voice`、`Sentence length`、`Parallel structure`、`Tone`、`No stale metaphors`、`Cut filler`、`Short words`、`One idea`、`No binary opposition`、`Anchor claims`、`No nominalization chains`.

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

生成時同樣避免上述 zh 反 AI 腔 pattern（對仗句、純裝飾性排比、概念名詞化、飄浮錨點）。

---

## Constraints

- Single-pass only. No iterative refinement loop inside the skill. If the user wants a different result, they re-invoke.
- Content output language follows the prefix (or auto-detection). Operational notifications are always Traditional Chinese.
- Refine mode never silently applies rules to incompatible-language content. Report the mismatch; do not guess.
- Generate mode vague-topic fallback is always short prose. Do not ask the user to clarify before outputting — produce something and let the user re-invoke with a more specific prompt if needed.
