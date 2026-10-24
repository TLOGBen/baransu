<!-- Template: .claude/hypothesis/<area>/paths/P<n>.md — one counterexample, as a script in the source's words. Read by /hunt (probes) and /prove-it (forced-order replay). -->

# P{n}　{summary}

(unimplemented) — First layer, plain words in the voice of `/huh`: what happened and what the user loses, readable by someone who never met formal methods (a business owner, in document mode). None of these words may appear in it: 活性、安全性、精化、不變式、同步點、TLC、模型、狀態空間. `{summary}` and this paragraph are that layer; everything below is the second layer.

- **破壞的規則**：R{k}　{rule text}
- **傷害**：(unimplemented) one sentence, the user's loss
- **發現類型**：bug | 矛盾 | 缺漏 | 精化不成立
- **圖**：diagrams.html#dN

## 劇本

(unimplemented) — Numbered steps, one per model step, each one line in the source's words with its citation; the actor and what they see:

1. (unimplemented) 申請人送出 2000 元的申請。— `src/approval/submit.ts:18`
2. (unimplemented) …

## 每一步都走得到嗎

(unimplemented) — Per step: 「是，因為 …」 with the citation, or the step the source cannot take (then this is a model error, fixed before publish, never published as a path).

## 給讀者的探針

(unimplemented) — One yes/no question per step boundary where the order matters, ready for `/hunt` (e.g. 「`withdraw.ts:33` 寫入之後，`approve.ts:58` 有沒有重新讀狀態？」), and the forced order `/prove-it` needs to replay it (which step to slow or hold).
