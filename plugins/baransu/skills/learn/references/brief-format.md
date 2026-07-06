## Contents

- Example Placeholders

# brief-format.md — --brief five-column examples

Worked example placeholders for the `/baransu:learn --brief` output body.
The authoritative format contract — the five-column structure, order, and names,
the column (d) credibility anchor scale, the YAML frontmatter fields, and the
same-slug `.bak` rule — lives inline in SKILL.md Stage 2 §4. This file only
supplies examples; consult it when an example is needed. If this file and
SKILL.md ever disagree, SKILL.md wins.

---

## Example Placeholders

### (a) 核心主張列表

```
- [Source A] 主張：深度學習在小樣本場景的泛化能力不如傳統統計模型。
- [Source B] 主張：資料增強可將小樣本場景的泛化誤差降低 15%。
```

### (b) 來源矛盾點

```
- Source A 認為正則化是主要緩解手段；Source B 認為正則化效果有限，應優先增加標注量。
```

### (c) 缺少資訊/盲點

```
- 所有來源均未討論跨語言場景下的小樣本泛化。
- 缺少 2023 年後大型語言模型對此議題的影響評估。
```

### (d) 各來源信度評分

Scored per source on the authorship anchor scale in SKILL.md Stage 2 §4 step c.

```
| 來源 | 信度評分 | 依據 |
|------|---------|------|
| Source A | 5 | 同儕審查論文 |
| Source B | 3 | 具名作者，引用一篇佐證文獻 |
```

### (e) 建議 /think 入場角度

```
建議以「小樣本場景下，資料增強 vs. 增加標注量，哪條路徑的 ROI 更高？」作為 /think 的核心問題，
優先探索 Source A 與 Source B 的分歧點。
```
