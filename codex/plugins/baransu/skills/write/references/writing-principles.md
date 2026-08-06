## Contents

- zh principles — 中文
- en principles — English

# Writing Principles — Claude Default Deviations

These principles correct Claude's observed defaults in Chinese and English prose. Each entry names the default pattern to avoid and shows a concrete before/after correction. Apply during composition — not as a post-generation checklist.

---

## zh principles — 中文

Source: 余光中《怎樣改進英式中文？──論中文的常態與變態》

Claude's zh defaults: nominalizing verbs, stacking 「的」 modifiers, reaching for abstract nouns instead of concrete ones, filling emotional beats with content-free adjectives, piling multiple images into one sentence, writing sentences of uniform length, over-connecting clauses, and dodging word repetition with synonyms.

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

Entries 6–15 below are Chinese AI-flavor fingerprints (中文 AI 腔指紋) — recurring tells of machine-generated zh prose, folded in alongside the 余光中 deviations. Entries 10–15 come from behavioral analysis of model prose habits (rhythm, lexicon, connective density — the measurable tells, not just banned words). They complement, and never relax, the SKILL.md anti-AI 味 floor (zh rules 5 / 7 / 8); where a fingerprint borders a floor rule, the boundary is stated in the entry.

---

**6. 段末總結句 — No paragraph-final summary sentences**

Claude defaults to closing a paragraph by restating it: 「這說明」「由此可見」「綜上所述」. The restatement adds no information. Cut the closer and end on the concrete point.

| Before (default) | After (correction) |
|---|---|
| ……錯誤率降了四成。這說明流程改造是有效的。 | ……錯誤率降了四成。（句號收尾，不再覆述）|
| 由此可見，使用者更在意速度。 | 直接給出證據那一句，刪掉「由此可見」|
| 綜上所述，本方案可行。 | 刪去；若全文需要收束，改寫成帶新資訊的結語 |

---

**7. 三段式排比鷹架 — No "首先…其次…最後" scaffolding**

Claude defaults to forcing content into the 「首先…其次…最後」 enumeration scaffold even when the points are not sequential. Boundary with SKILL.md zh rule 7: that floor rule bans decorative rhetorical parallelism (「不是A，不是B，而是C」) and is never relaxed; this entry targets the procedural enumeration scaffold specifically.

| Before (default) | After (correction) |
|---|---|
| 首先，成本太高；其次，時程太緊；最後，人力不足。 | 成本太高，時程太緊，人也不夠。（或改用真正的條列）|

---

**8. 升華句 — No elevation closers**

Claude defaults to ending with an abstract elevation: 「這體現了…精神」「這正是…的意義所在」. The closer inflates a concrete fact into an empty ideal. End on the fact itself.

| Before (default) | After (correction) |
|---|---|
| 團隊週末加班修完了漏洞，這體現了敬業精神。 | 團隊週末加班，把漏洞修完了。|
| 這正是開源協作的意義所在。 | 說那次協作具體發生了什麼 |

---

**9. 套話連接詞與洞察路標 — Cut boilerplate connectives and insight signposts**

Claude defaults to padding transitions with 「值得注意的是」「從而」「進而」. 「值得注意的是」 is the zh twin of "it is important to note that" (en principle 2): cut it and state the fact. 「從而」「進而」 belong to bureaucratic register; replace with plain connectives or split the sentence.

Also cut **insight signposts** — phrases whose only job is to announce that the next sentence is deep: 「說白了」「說穿了」「先說結論」「更微妙的是」「還有一層」「只說對了一半」「從某種意義上說」. The same goes for the **prompting colon** (「一句話總結：」「核心是：」): in prose, a colon introduces a person's direct quotation only; format fields, URLs, and code are exempt. When the words carry their literal sense (an actual floor count, an actual layer), they stay.

| Before (default) | After (correction) |
|---|---|
| 值得注意的是，快取命中率只有六成。 | 快取命中率只有六成。|
| 重構介面，從而降低耦合 | 重構介面，降低耦合（或拆成兩句）|
| 先壓縮資源，進而縮短載入時間 | 先壓縮資源，載入時間就短了 |
| 說白了，這功能沒人用。 | 這功能沒人用。|
| 一句話總結：快取才是瓶頸。 | 瓶頸在快取。|

---

**10. 句長齊一與固定鼓點 — Vary sentence length; no drumbeat closers**

A measurable model habit: sentences of near-uniform length, and every paragraph closing on a short punchy verdict. Human paragraphs put a 10-character sentence next to a 40-character one. When every sentence in a paragraph runs about the same length, compress one below ~10 characters or let one run past 30. When several consecutive paragraphs each end on a short judgment sentence, keep only the one with the hardest material behind it — ordinary paragraphs end on ordinary sentences.

| Before (default) | After (correction) |
|---|---|
| 每句 18–25 字整齊排列，段段等長 | 十個字的句子挨著四十個字的句子，段落有高低差 |
| 每段末尾都補一句短判斷收尾 | 只留材料最硬的那一處；其他段平常收 |

---

**11. 連接詞過密 — Cut half the connectives**

Claude defaults to 「因為」「所以」「但是」「同時」「此外」「然而」 every second clause. Chinese clauses connect by word order and sense; delete half the connectives, and only restore one where the reading actually breaks.

| Before (default) | After (correction) |
|---|---|
| 因為店裡生意不好，所以他決定把下午的時間用來學修錶，同時也能多一門手藝 | 店裡生意不好，他下午閒著，就學起了修錶，多一門手藝總沒壞處 |

---

**12. 同義詞迴避 — Repeat the word**

Claude defaults to elegant variation: the second mention of 「修錶」 becomes 「這門手藝」, the third 「這項技能」. The swapping reads slick, not fluent. Humans repeat the word — 「修錶」 can appear four times in one paragraph.

| Before (default) | After (correction) |
|---|---|
| 修錶……這門手藝……這項技能 | 該重複就重複：修錶、修錶、修錶 |

---

**13. 動作後補解釋 — Stop after the action**

Claude defaults to appending an emotional explanation after an action, object, or quote that already carries the feeling. When the reader can already see the hesitation, fear, or attachment, the trailing explanation dissipates it. Cut it; keep only what the reader cannot infer (key facts, causality, choices).

| Before (default) | After (correction) |
|---|---|
| 走到門口，他又回來，把星期三那格打開看了一遍。他很擔心母親記錯藥。 | 走到門口，他又回來，把星期三那格打開看了一遍。|

---

**14. 抒情詞與借喻包裝 — No lyric-lexicon dressing of abstractions**

Claude defaults to a favored lyric lexicon (安放、抵達、微光、褶皺、豐盈、滾燙、輕盈、剝開、鋒利、柔軟), stock metaphor kits for abstract concepts (倉庫、抽屜、溫度、死亡、坍塌、浪潮、鑰匙、底座), and pairing abstract nouns with concrete verbs (時間不會保管細節，焦慮不會顯出形狀，歲月不會磨平什麼). All fine when the text is about the actual thing; strip them when they only dress up a concept. 「」-quoted self-coined phrases three or more times in one piece is 金句 manufacturing — dismantle.

| Before (default) | After (correction) |
|---|---|
| 把記憶安放在時間的褶皺裡 | 說那件事後來怎麼被想起、被誰提起 |
| 時間會替我們保管這些細節 | 這些細節他一直記得 |
| 這個功能是整個產品的底座 | 說其他功能哪裡依賴它、壞了會怎樣 |

---

**15. 商業黑話 — Jargon back to people, actions, money, time**

Claude defaults to 賦能、抓手、閉環、底層邏輯、頂層設計、降本增效、組合拳、全鏈路、內容矩陣、認知躍遷、打開想像空間 when describing ordinary work — the zh twin of en principle 1's stale metaphors. Rewrite into who did what, what it cost, what changed. Context-dependent words (沉澱、對齊、鏈路、閉環) stay when used in their literal sense (chemical sediment, layout alignment, a control loop); rewrite only when they inflate ordinary matters.

| Before (default) | After (correction) |
|---|---|
| 透過流程再造實現降本增效 | 流程改掉以後，每單少花二十分鐘，省下兩個人 |
| 打造內容矩陣、形成商業閉環 | 說開了哪些帳號、錢從哪裡進來 |
| 以 AI 賦能客服團隊 | 客服先讓 AI 擬回覆草稿，再自己改 |

---

## en principles — English

Source: George Orwell, "Politics and the English Language" (1946)

Claude's en defaults: stale metaphors borrowed from tech/business discourse, filler phrases that pad word count without adding meaning, long synonyms where short words exist, synonym-swapping on repeated mentions, and uniform sentence rhythm.

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

---

**5. Repeat the word — No elegant variation**

Claude defaults to swapping in a synonym at each repeated mention: "the parser" becomes "this component", then "the module". The variation forces the reader to re-verify that all three names point at one thing. Repetition is clearer; repeat the word.

| Before (default) | After (correction) |
|---|---|
| the parser … this component … the module | the parser, every time |
| the migration … this effort … the initiative | the migration, every time |

---

**6. Vary sentence rhythm — No uniform length, no drumbeat closers**

Claude defaults to sentences of near-uniform length and a short verdict sentence closing every paragraph. Put a five-word sentence next to a thirty-word one. Let ordinary paragraphs end plainly; save the short closer for the one paragraph with the hardest material behind it.

| Before (default) | After (correction) |
|---|---|
| Every sentence runs 15–20 words; every paragraph ends on a punchy verdict. | One sentence lands in five words. The next unwinds across thirty, carrying the conditions and the cost, before the paragraph ends on an ordinary sentence. |
