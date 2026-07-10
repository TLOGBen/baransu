# loop-pauses — /health PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/health is `loop=assisted`: an audit runs end-to-end without a human. It has
two Authorization mutation checkpoints that never take a default (INV-4), plus
one sanctioned report write (the non-interactive report persist below — an
Input-class output obligation, not a gated mutation). The audit itself
continues past all of them — only the Authorization mutations are withheld.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Budget posture — deep-audit escalation notice（「即將升級為 deep 審計…」） | Input | Escalate per the Step 2 routing rules, record the notice in the report, annotate 「此處採預設：依路由規則升級 deep 審計」 |
| Non-interactive report persist — write the report to `.claude/health/report-{date}.md`（loop-contract obligation 2） | Input | Always write it — this is the sanctioned loop-mode output write into the project dir, exempt from INV-4 gating; annotate 「loop 模式規定輸出：報告已寫入 .claude/health/report-{date}.md」 |
| Step 3 baseline-principles append offer（「是否將缺少的原則從 baseline 範本補上？」— writes into `~/.claude/CLAUDE.md` or project `CLAUDE.md`/`AGENTS.md`） | **Authorization (not standing-authorizable)** | Never append. Report the missing-principles `WARN` finding as usual and annotate the append offer as `needs input`. Standing authorization is not accepted here: the write target is the user's own instruction surface (a self-modifying write-back), so only an interactive confirmation satisfies it. The audit continues |
| Step 3 destructive-action gate（「⚠ 破壞性 / 不可逆」 actions: `git rm --cached`, `rm`, history rewrites, force-push, credential paths） | **Authorization (not standing-authorizable)** | Never run the action. Emit the action line in the report with its ⚠ marker for the user to run later. The audit continues |
