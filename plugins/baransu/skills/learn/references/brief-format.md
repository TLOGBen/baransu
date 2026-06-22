## Contents

- YAML Frontmatter Specification
- Five-Column Markdown Template
- Constraints

# brief-format.md — --brief 五欄格式合約

This file is the **format contract** for `/baransu:learn --brief` output.
Stage 2 (Digest phase) of SKILL.md reads this file to produce brief reports.
The column count, order, and names are fixed — do not add or remove columns.

---

## YAML Frontmatter Specification

Every brief file (`.claude/learn/briefs/{slug}.md`) MUST begin with the following
frontmatter. All four fields are required; no field may be omitted.

```yaml
---
topic: "{研究主題}"
sources:
  - slug: "{slug}"
    url: "{原始 URL}"
created_at: "{ISO 8601 timestamp}"
type: "brief"
---
```

Field definitions:

| Field | Type | Description |
|-------|------|-------------|
| `topic` | string | The research subject as given by the user |
| `sources` | list | Each source that passed the Digest credibility filter; each entry has `slug` (URL-safe identifier) and `url` (original URL) |
| `created_at` | string | ISO 8601 timestamp when the brief was generated |
| `type` | literal `"brief"` | Fixed discriminator — always `"brief"` |

---

## Five-Column Markdown Template

After the YAML frontmatter, the brief body follows this fixed five-column structure.
Each column is a level-3 heading (`###`) followed by a one-line definition and an
example placeholder. The order is canonical and must not be changed.

---

### (a) 核心主張列表

**Definition:** Key claims or conclusions extracted from the filtered sources — what
each source asserts as its central argument.

**Example placeholder:**

```
- [Source A] 主張：深度學習在小樣本場景的泛化能力不如傳統統計模型。
- [Source B] 主張：資料增強可將小樣本場景的泛化誤差降低 15%。
```

---

### (b) 來源矛盾點

**Definition:** Points where two or more filtered sources contradict each other —
conflicting claims, opposing evidence, or incompatible conclusions.

**Example placeholder:**

```
- Source A 認為正則化是主要緩解手段；Source B 認為正則化效果有限，應優先增加標注量。
```

---

### (c) 缺少資訊/盲點

**Definition:** Gaps not covered by any filtered source — missing evidence, unstated
assumptions, or dimensions that none of the sources address.

**Example placeholder:**

```
- 所有來源均未討論跨語言場景下的小樣本泛化。
- 缺少 2023 年後大型語言模型對此議題的影響評估。
```

---

### (d) 各來源信度評分

**Definition:** Visual credibility score (1–5) for each filtered source, evaluated
across three criteria: multi-context applicability, predictive power, and generality.
Quantitative formula is TBD; v1 uses visual judgment within the 1–5 range.

Scoring scale: 1 = very low credibility, 5 = very high credibility.

**Example placeholder:**

```
| 來源 | 多情境適用性 | 預測力 | 通用性 | 綜合評分 |
|------|-------------|--------|--------|---------|
| Source A | ★★★★☆ | ★★★☆☆ | ★★★★☆ | 3.7 |
| Source B | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | 3.3 |
```

---

### (e) 建議 /think 入場角度

**Definition:** Recommended framing angle for feeding this brief into `/think` Stage A —
what question or hypothesis to lead with, based on the contradictions and gaps found above.

**Example placeholder:**

```
建議以「小樣本場景下，資料增強 vs. 增加標注量，哪條路徑的 ROI 更高？」作為 /think 的核心問題，
優先探索 Source A 與 Source B 的分歧點。
```

---

## Constraints

- **Column count is fixed at five.** Do not add or remove columns.
- **Column order is fixed.** (a) → (b) → (c) → (d) → (e).
- **Column names are fixed.** Do not rename headings.
- **Credibility scoring is visual (1–5).** Quantitative formula deferred to a future version.
- **YAML frontmatter fields are all required.** `topic`, `sources`, `created_at`, `type: "brief"` — none may be omitted.
- **Conflict resolution.** If a brief with the same slug already exists, overwrite with the new version.
- **Zero sources passing Digest.** If all sources score below the credibility threshold, `/learn` stops and prompts the user to supply additional sources — no brief is emitted.
