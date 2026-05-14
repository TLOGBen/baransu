# slide-image-prompts.md

> **Scope: PPT only.** This document governs image handling and external AI image-generation prompt templates for `/design` PPT outputs (slide-cores). It does **not** apply to long-form output (`--format longform`). The `/book` skill's image-generation capability is out of scope here — this file regulates user-supplied image placement and prompt templates only; it never calls an external image API.
>
> Audience: `/design` slide-core authors and `check.py` lint source.

---

## 1. Scope 宣告

- **適用**: 所有 `--format ppt` slide-core HTML（9 版式）。
- **不適用**: `--format longform`（單欄長文不受本文件約束）。
- **不涵蓋**: 外部 AI 生圖工具的實際呼叫；本文件僅提供 prompt 模板供使用者複製貼上。

---

## 2. 使用者圖片處理規則

使用者貼入 slide-core 的 `<img>` 或 `background-image` 必須遵守以下 `object-fit` / `object-position` 預設。不同版式因 image_slot 寬高比與內容焦點不同，預設值不同。

### 對照表

| Layout       | 預設 object-fit | 預設 object-position | fit-contain fallback | 備註 |
|--------------|-----------------|----------------------|----------------------|------|
| cover        | `cover`         | `center 40%`         | 允許切換 `contain`  | 全幅鋪滿；人物頭像偏上時用 `center 35%` |
| section      | `cover`         | `center center`      | 允許切換 `contain`  | 章節分隔頁，純背景或裝飾用 |
| content-bullets | `cover`      | `center center`      | 允許 `contain`       | 條列頁；若有右側 image_slot 視同 2col |
| content-2col | `cover`         | `center 35%`         | 不建議 `contain`     | 雙欄人物 / 場景照；禁用 `top center`（P0-2） |
| data         | `contain`       | `center center`      | 預設即 contain       | 圖表 / 截圖；不可裁切，保留完整邊框 |
| kpi-grid     | `cover`         | `center center`      | 允許 `contain`       | 多格 KPI，背景圖通常為紋理或抽象 |
| compare      | `cover`         | `center 35%`         | 允許 `contain`       | 並列對比；兩側焦點需一致（皆 `center 35%`） |
| quote        | `cover`         | `center center`      | 允許 `contain`       | 引言頁背景，避免人物臉部置中 |
| closing      | `cover`         | `center 40%`         | 允許 `contain`       | 結語頁；與 cover 一致 |

### 共通規則

- **P0-2 對齊**: 含人物或主視覺焦點的場景一律使用 `center 35%`，**不可** `top center`（會切掉下巴與身體）。
- **fit-contain**: 圖表類（data 版式）一律 `contain`，避免裁切；其他版式若使用者圖片比例異常，允許手動切換為 `contain`，但需在 HTML 註解標註原因。
- **背景色 fallback**: `object-fit: contain` 時 `<figure>` 父層 background 走 `--swiss-canvas-muted` token，避免出現透明色洞。
- **`<figcaption>` 必填**: 含 image_slot 的版式（content-2col / data / kpi-grid / compare）必須有 `<figure>` + `<figcaption>` wrapping（即使 caption 為空白，也保留 DOM 結構以利 lint）。

---

## 3. 對外部 AI 生圖工具 Prompt 模板

以下 9 條 prompt 對應 9 個 slide-core 版式（每版式一條 H2 區段）。每條為「正向描述 + 風格錨點」，使用者複製到任一外部 AI 生圖工具（Midjourney / DALL·E / Stable Diffusion / nano-banana 等）後，**必須**在尾端附加共用負面尾巴（見第 4 節）。

## Layout: cover

```
Editorial hero image for a presentation cover slide: clean composition, single focal subject offset to the right third, generous negative space on the left for title overlay, Swiss-poster aesthetic, muted neutral palette with one bold accent color, soft natural light, photographic realism, 16:9.
```

## Layout: section

```
Abstract chapter-divider visual: minimal geometric composition, two-tone palette, large flat color field with a single linear element crossing the frame, no figurative content, suitable as a subtle backdrop behind a large numeral or section title, 16:9.
```

## Layout: content-bullets

```
Subtle textural background for a bulleted content slide: low-contrast paper-grain or fine grid texture, off-white base with one muted accent tint at 10% opacity, no central subject, no competing focal point, designed to sit behind body text without distraction, 16:9.
```

## Layout: content-2col

```
Documentary-style photograph for a two-column content slide right pane: human subject or scene, eye-line approximately 35% from the top of the frame, shallow depth of field, neutral environmental context, editorial color grade, no text, 4:5 portrait crop.
```

## Layout: data

```
Clean infographic-style chart illustration for a data slide: single chart type (bar or line), minimal axes, two-color palette aligned with Swiss preset accent, no decorative elements, no 3D effects, flat vector aesthetic, generous margins so the chart reads at slide-distance, 16:9.
```

## Layout: kpi-grid

```
Abstract textural background for a KPI-grid slide: very low-contrast geometric pattern (dot grid or thin lines), single muted tint, designed to recede behind four to six numeric tiles, no figurative content, no focal point, 16:9.
```

## Layout: compare

```
Side-by-side documentary photograph pair for a comparison slide: two subjects of the same category, identical framing and lighting, both with eye-line at approximately 35% from the top, consistent color grade across both halves, neutral backgrounds, 16:9 split into two 4:5 panes.
```

## Layout: quote

```
Atmospheric backdrop for a quotation slide: soft out-of-focus environmental texture, low-contrast neutral palette, no figurative content, no human face, designed to sit behind a large pull-quote without competing for attention, 16:9.
```

## Layout: closing

```
Editorial closing-slide hero image: open horizon or forward-looking composition, single focal element offset to lower-right third, generous upper-left negative space for closing message, warm neutral palette with one accent tint, photographic realism, 16:9.
```

---

## 4. 共用負面尾巴

所有 9 條 prompt 在送進外部 AI 生圖工具前，**必須**在尾端附加以下字串（逐字，不可改寫）：

```
no title, no footer, no page chrome, no logo, no border
```

理由：slide-core 的 chrome（標題、頁尾、邊框、Logo）由 HTML + tokens.css 負責繪製。若生成圖本身內嵌了這些元素，會與 slide-core chrome 雙重疊加、破版。負面尾巴強制 AI 工具產出「純內容」圖片，由 slide-core 自行包裝。
