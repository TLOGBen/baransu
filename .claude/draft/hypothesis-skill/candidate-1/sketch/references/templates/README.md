---
area: approval
input: code
verdict: broken
sync: 3f2a1c9
covers:
  - src/approval/service.py 8e1f0c2a9d4b7e6f5a3c2b1d0e9f8a7b6c5d4e3f
  - src/approval/models.py 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b
rules:
  - R1 safety broken｜付出去的錢，一定等於最後一次核准時的金額
  - R2 safety broken｜撤回之後，不會再付款
  - R3 safety broken｜送出後一定有人能處理，不會卡住
  - R4 goal holds｜金額 ≥1000 的單子，經理和財務都核准後會付款
  - R5 goal holds｜金額 <1000 的單子，經理核准後會付款
findings:
  - P1 bug → R1｜退回改金額再送出，舊核准還在，照舊金額付款
  - P2 bug → R2｜撤回和核准同時按，撤回生效，款項照付
  - P3 bug → R3｜財務核准時單子剛好被退回，停在審核中沒人能處理
checks:
  - R1 tlc -config R1.cfg Approval.tla
  - R2 tlc -config R2.cfg Approval.tla
  - R3 tlc -config R3.cfg Approval.tla
  - R4 tlc-reach -config R4.cfg Approval.tla
  - R5 tlc-reach -config R5.cfg Approval.tla
tool: TLC 2.19
bounds: 金額 {500, 2000, 9000}；最多送出 3 次；角色 經理、財務
---

<!-- (unimplemented) Template. The front matter above is the contract `scripts/hypothesis.py` reads (schema: references/area.md §The contract). Values shown are the approval known-answer example. The body below is for people and for --maintain; the script reads none of it. Headings are fixed; body text is Traditional Chinese. -->

# 簽核：付款一定對得上核准

## 主張

(unimplemented) One paragraph: the claim in plain words, the input it came from (for a symptom, the symptom quoted; for documents, which is rules and which is behaviour).

## 發現

(unimplemented) One subsection per `findings` id. For code: the steps in the code's words, each with `file:line`, and the harm in one sentence. For documents: the colliding passages quoted with their locations, or the question and who should answer it.

### P1 → R1

1. (unimplemented) 申請人送出（`src/approval/service.py:41`）…

## 對照表

(unimplemented) Coverage map: one row per model part — model part | what it stands for in plain words | source citation (`file:line`, or quoted passage + file, section, page). `covers` above is derived from this table's files; every row's file appears there.

| 模型的部分 | 代表什麼 | 來源 |
|---|---|---|
| `Submit` | 申請人送出 | `src/approval/service.py:41-58` |

## 範圍與假設

(unimplemented) Bounds, assumptions, what is left out; a pass holds only inside these. For an unbounded request, the proof tool used instead.

## 證明它可信

(unimplemented) Seen failing: per safety rule, the broken variant (`evidence/broken-R1.diff`) and the output that caught it. Seen succeeding: per goal rule, the reaching trace and the transition whose removal made it unreachable (`evidence/goal-R4-*.out`). Each with the tool version and states explored.

## 沒有形式化的部分

(unimplemented) Reason records, schema in references/formal.md §Reason record. Required even when empty: write 「無」. Every field filled.

| 哪一段 | 原因 | 具體情況 | 何時可形式化 | 現在改走 |
|---|---|---|---|---|
| `src/approval/notify.py:12-30` | 無法建模 | 外部郵件服務 | 有可替身的郵件介面時 | 紅綠測試 |

## 維護紀錄

(unimplemented) One line per `--maintain` or migration: date (queried, not assumed), old sync → new sync, outcome (in sync, updated, bug, blocked), and for a rule rewritten on purpose its old and new wording with the evidence cited.
