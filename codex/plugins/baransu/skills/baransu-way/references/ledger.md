# Ledger

One file per chained run at `.codex/baransu-way/<slug>.md`, the run's only memory between turns. Write it when the authorization is recorded — the grounding done before the route is its first row — update it after every leg, stop, and substituted default, and never rewrite a finished leg's row. If the file already exists for another run, use `<slug>-2.md` and count up.

```markdown
# {goal in one line}

- 狀態：進行中 | 停在 {leg} | 卡住 | 交給 ship | 完成
- 路線：{route name} — {leg} → {leg} → …
- 授權：「{the user's sentence, verbatim}」
- 終點：{last authorized leg}
- 開始：{ISO time}，HEAD {short sha}

## 各段

| # | 段 | 狀態 | 產出 | HEAD | 工作樹 hash |
|---|---|---|---|---|---|
| 1 | $baransu:how（打底） | 完成 | （對話內） | a1b2c3d | 9f8e… |
| 2 | $baransu:think | 完成 | .codex/think/{slug}.md | a1b2c3d | 9f8e… |
| 3 | $baransu:draft | 進行中 | | | |

## 此處採預設

- 第 {n} 段 {leg}：{the default taken and the assumption behind it}

## 停點

- 第 {n} 段 {leg}：{which stop, (a)–(e)}；需要你：{one sentence}
```

The working-tree hash is the SHA-1 of `git status --porcelain` output; the status column is one of 完成, 進行中, 停下, 卡住, 跳過（{reason}）. The product column is a path or 「（對話內）」 — a verdict that lives only in the conversation is copied in one line here, because the conversation may not survive.
