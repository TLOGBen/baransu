# Answer key — /hypothesis known-answer exams

Not for the agent taking the exam. Grade its `.claude/hypothesis/` output against this file.

## approval-code

Source: `approval-code/naive/approval.py` and `approval-code/fixed/approval.py`. Each HTTP request runs one function; requests may run at once, so `load` → check → `save` without a lock is a read-check-write in separate steps (H1), on a state machine with guarded transitions (H3), with money (H4) and a payment (H6).

Naive — must find all three, each a path whose every step the code can take, citing `file:line`:

1. **Stuck after a resubmit at a lower amount.** Manager approves 2000, finance rejects, applicant edits to 500 and submits: the old manager approval is still in `approvals` (`submit` does not clear it), so `next_role` is `None` while the status is `pending`; nobody can approve or reject.
2. **Paid after withdrawal.** `withdraw` and `approve` both `load` a pending request; `withdraw` saves `withdrawn`, then `approve` saves its copy with `approved` (lost update); `pay` pays a withdrawn request. (Any equivalent interleaving counts.)
3. **Paid an amount someone never approved.** An approval recorded at one amount is counted for another: e.g. manager approves 2000, finance's approve and reject overlap or the request is rejected, edited and resubmitted, and the stale approvals complete the set; payment goes out for an amount the manager never approved at. (Any path where `paid_amount` ≠ the amount some required role approved counts.)

Fixed — must hold every rule above within the stated bounds (no path), with seen failing on a broken variant per rule (e.g. removing the `approvals = []` line, or making `save` skip the version check) and seen succeeding (a request reaches payment; unreachable once the payment step is removed).

Must not: report a bug that needs a step the code cannot take; fall back to tests; skip a reason record for anything left unformalized (e.g. the HTTP layer, real concurrency of the dict).

## approval-doc

Source: `approval-doc/SA-簽核需求.md` (one document).

Must find, each quoting the passage and its location:

1. **Contradiction** — §3.6 「已撤回的申請，申請人可以修改金額後重新送出」 against §4.1 「已撤回是終止狀態，進入之後不能再有任何動作」, with the path withdraw → edit/resubmit that collides them.
2. **Gap** — §3.4 lets any approver reject, but nothing says what can happen to a 「已退回」 request: it has no way out (and §2 lists no step from it).
3. **Ambiguity** — §4.2 binds payment to 「每一位需要的簽核人核准時看到的金額」 and §4.3 says 「主管核准之後，金額不得變更」, but the document never says whether an approval belongs to the amount or to the submission (does an approval survive a rejection and resubmit at the same amount?) — a question for 王經理 or 陳主任, never filled in.

Comparison:

- `SD-照規則.md --satisfies SA-簽核需求.md` — refinement holds for §3.1–3.5 and §4.2–4.4 (the SD omits §3.6's resubmit, which is allowed by §4.1; the agent should say the contradiction in the SA is resolved one way by this SD, as a note, not a break).
- `SD-漏財務.md --satisfies SA-簽核需求.md` — refinement break: an amount ≥ 1000 is approved by the manager alone and paid, violating §3.2 (and §4.2). The path must cite both documents.
