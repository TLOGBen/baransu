# reason record — one row per part not formalized

Lives in `hypothesis.json` `unformalized[]` (rendered into README § 沒有形式化的部分), or, when no area is written at all, in the output of the skill that declined (the hunt case file) in the same five fields.

| field | content |
|---|---|
| `where` | `file:line` range, or the claim's or document's own words with location |
| `class` | exactly one of the seven below |
| `detail` | the concrete situation, naming the missing tool, the dependency, the bounds tried and time taken, the non-trigger row, or the user's words |
| `until` | what would have to be true for it to become formalizable |
| `instead` | `hunt 推測` \| `red/green test` \| `none` — the route it takes now |

Classes (closed set; the slug is what goes in `class`):

| slug | 中文 | `detail` must name |
|---|---|---|
| `no-tool` | 沒有工具 | the verifier missing for this language, or the tool not installed |
| `cannot-model` | 無法建模 | the outside dependency (external service, hardware timing, clock precision) |
| `out-of-scope` | 超出範圍 | the bounds tried and how long the run took |
| `non-trigger` | 符合不觸發條件 | which non-trigger row in `references/formal.md` |
| `no-truth` | 沒有對錯可證 | look, preference, copy |
| `user-declined` | 使用者決定不做 | the user's words, quoted |
| `handed-off` | 交給別份假說 | which hypothesis (its name) or which slice of which plan will formalize it; a hand-off that names neither is incomplete |

A record with an empty field, or a class outside this set, makes the area `draft`.
