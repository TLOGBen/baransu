# Writing Principles — Claude Default Deviations

These principles correct Claude's observed defaults in Chinese and English prose. Each entry names the default pattern to avoid and shows a concrete before/after correction. Apply during composition — not as a post-generation checklist.

---

## zh principles — 中文

Source: 余光中《怎樣改進英式中文？──論中文的常態與變態》

Claude's zh defaults: nominalizing verbs, stacking 「的」 modifiers, reaching for abstract nouns instead of concrete ones, filling emotional beats with content-free adjectives, and piling multiple images into one sentence.

---

**1. 動詞直用 — Use verbs directly; do not nominalize**

Claude defaults to wrapping verbs in 「進行」「作出」「給予」 constructions.

| Before (default) | After (correction) |
|---|---|
| 進行討論 | 討論 |
| 作出決定 | 決定 |
| 給予支持 | 支持 |
| 進行分析 | 分析 |
| 進行修改 | 修改 |

---

**2. 「的」克制 — Restrain 「的」 modifier chains**

Three consecutive 「的」 in one sentence is the signal to restructure.

| Before (default) | After (correction) |
|---|---|
| 他作出的決定是正確的 | 他的決定是對的 |
| 這是一個重要的、深刻的、值得關注的問題 | 這個問題值得深思（選一個角度說清楚）|

---

**3. 具象優先 — Prefer concrete nouns over abstract ones**

Claude defaults to abstract summary nouns (「氛圍」「情境」「空間感」「質感」「意境」) when concrete images are available.

| Before (default) | After (correction) |
|---|---|
| 整個空間充滿了溫馨的氛圍 | 桌上還亮著一盞燈，杯子還沒收 |
| 這個地方有一種獨特的情境 | 說具體發生了什麼、看見了什麼 |
| 展現出濃厚的文化意境 | 說哪個文化元素、在哪裡出現 |

---

**4. 空洞形容詞禁用 — No content-free adjectives**

Claude defaults to prefixing with 「充滿」「洋溢」「滿滿的」「無比」「超」「極」 when the underlying feeling has not been earned by the surrounding text.

| Before (default) | After (correction) |
|---|---|
| 充滿活力的演講 | 說演講者做了什麼、讓人記住什麼 |
| 洋溢著青春氣息 | 說是誰、做了什麼動作 |
| 無比珍貴的回憶 | 說哪一個回憶、它發生了什麼 |

---

**5. 密度克制 — One image per sentence**

Claude defaults to stacking parallel images in one sentence ("在靜謐的午後，陽光斜照，微風吹來，空氣中瀰漫著花香"). Choose one; let the others go or give them their own sentence.

| Before (default) | After (correction) |
|---|---|
| 在溫柔的燈光下，咖啡香氣瀰漫，輕柔的音樂流淌 | 選一個：燈光、咖啡香、或音樂。把那一個說清楚。|

---

## en principles — English

Source: George Orwell, "Politics and the English Language" (1946)

Claude's en defaults: stale metaphors borrowed from tech/business discourse, filler phrases that pad word count without adding meaning, and long synonyms where short words exist.

---

**1. No stale metaphors — Find the specific thing**

Claude defaults to figures of speech worn smooth by overuse in professional writing.

| Before (default) | After (correction) |
|---|---|
| leverage our expertise | use our expertise / apply what we know |
| seamless experience | describe what actually happens |
| going forward | from now on / starting next quarter |
| at the end of the day | ultimately / (cut it entirely) |
| synergize across teams | teams work together on X |

---

**2. Cut filler phrases — Every word must earn its place**

Claude defaults to transitional phrases that add length without meaning.

| Before (default) | After (correction) |
|---|---|
| in order to | to |
| due to the fact that | because |
| at this point in time | now |
| it is important to note that | (cut; state the fact directly) |
| in the event that | if |
| with regard to | about |

---

**3. Short words over long — Plain English first**

Claude defaults to latinate vocabulary when a common word exists.

| Before (default) | After (correction) |
|---|---|
| utilize | use |
| facilitate | help |
| subsequently | then |
| endeavor | try |
| commence | start |
| demonstrate | show |

---

**4. One idea per sentence — Split compound claims**

Claude defaults to joining two distinct claims with "and." If a sentence has two main verbs with separate subjects or objects, split it.

| Before (default) | After (correction) |
|---|---|
| We rebuilt the auth flow and this reduced login errors by 40%. | We rebuilt the auth flow. Login errors dropped by 40%. |
| The tool is fast and it also handles edge cases well. | The tool is fast. It handles edge cases well. |
