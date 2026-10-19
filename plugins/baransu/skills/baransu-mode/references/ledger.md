# Ledger

One file per run at `.claude/baransu-mode/<slug>.md`, the run's only memory between turns. Write it when the playbook is matched, update it after every step, stop, and substituted default, and never rewrite a finished step's row. If the file already exists for another run, use `<slug>-2.md` and count up.

```markdown
# {task in one line}

- 狀態：進行中 | 停在 {step} | 卡住 | 交給 ship | 完成
- Playbook：{name} — {step} → {step} → …
- 授權：「{the user's sentence, verbatim}」
- 終點：{last authorized step}
- 開始：{ISO time}，HEAD {short sha}

## 各步

| # | 步驟 | 叫用 | 狀態 | 產出 | HEAD | 工作樹 hash |
|---|---|---|---|---|---|---|
| 1 | /how | baransu:how | 完成 | （對話內） | a1b2c3d | 9f8e… |
| 2 | /why | — | skip：git log 顯示這塊三個月沒動 | | | |
| 3 | /hunt | baransu:hunt | 完成 | .claude/hunt-report/HUNT-2026-007.md | a1b2c3d | 9f8e… |

## 此處採預設

- 第 {n} 步 {step}：{the default taken and the assumption behind it}

## 停點

- 第 {n} 步 {step}：{which stop, (a)–(f)}；需要你：{one sentence}
```

- **叫用** is the skill name passed to the Skill tool, or `—` for a skipped step and for Build (whose 產出 is the quoted red → green output).
- **狀態** is one of 完成, 進行中, 停下, 卡住, 未執行, skip：{the quoted grounding fact}.
- **產出** is a path, or 「（對話內）」 only when the step's skill defines no file; a step whose skill writes a file (think's plan, review's report, hunt's case file, prove-it's record) is not 完成 without that path.
- **工作樹 hash** is the SHA-1 of `git status --porcelain` output.
- Ship archives this file before it pushes, so before the ship step starts set 狀態 to 交給 ship; ship's outcome goes into the final report, which names the ledger at its archived path.
