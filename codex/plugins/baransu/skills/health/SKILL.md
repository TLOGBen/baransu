---
name: health
description: 'Use When the user wants to audit a project''s agent configuration or
  AI-coding maintainability — instruction drift, hooks/MCP, verifier surfaces, code-rot
  signals. Do Run a budget-aware five-layer audit (agent config → instruction surfaces
  → tools/runtime → verifiers → maintainability): classify the project tier, collect
  data via scripts, escalate to inspector subagents only for deep audits. Trigger
  On ''/health'', ''健康檢查'', ''配置體檢'', ''檢查配置'', ''AI 可維護性'', ''agents ignoring instructions''.
  繁體中文輸出。

  '
metadata:
  version: 1.0.0
  scope: user-project-agent-config-and-maintainability
compatibility: Designed for Claude Code; ported to Codex.
---

# health — agent-assisted engineering health audit

## Codex Port Adapter - Inspector Isolation

This skill is countering the model's inertia to treat same-context self-audit as independent evidence. Before using inspector subagents for deep audits, run or consult a `codex-isolation-probe.md` conclusion for this Codex runtime. If native Codex subagents are isolated, use them directly. If not, run each inspector perspective in an independent Codex invocation or session, write the raw findings to files, then merge from those artifacts.

Do not treat same-context sequential prompts as independent inspection. Authorization PAUSE remains a hard stop; only input-selection PAUSE may degrade to direct text questions.


Audit the current project's agent setup and AI coding maintainability against this five-layer framework:

`agent config → instruction surfaces → tools/runtime → verifiers → maintainability`

Find violations. Identify the misaligned layer. Calibrate to project complexity only.

**Positioning**: structural validation of baransu itself belongs to `scripts/verify-skills.py`. `/health` audits the **user's project's** agent configuration and AI maintainability — it is not a baransu self-audit and does not overlap verify-skills.

The body below is English (agent-facing). All user-facing output is in **Traditional Chinese (繁體中文)**.

---

## Outcome Contract

- **Outcome**: One budget-aware health audit of the user's project, routing agent-config risk and AI-maintainability risk into two lanes of a single report.
- **Done when**: Every finding marks the misaligned layer (one of the five-layer framework), concrete evidence (file:line or a script-output section), and a directly copy-runnable action or diagnostic command; or a clean health attestation + residual risk is emitted.
- **Evidence**: collect-data.sh output sections, the tracked project instruction files, the runtime config summary, verifier logs, the hooks/MCP surface, and (deep mode) inspector subagent reports.
- **Output**: A Traditional Chinese health report in the conversation (graded by tier, two lanes, sorted by severity); not separately persisted to a file.
- **Automation**: ultracode=assist, loop=assisted（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）

## Invariants (hard red-lines)

These hard rules hold across every step, tier, and mode. They are non-negotiable; the per-step mentions below are reminders, not the source of authority.

1. **Secret redaction.** Secrets, tokens, keys, and passwords appear only as `[REDACTED]`. Full keys are never printed — when a key must be touched at all, only `head -c 5` is permitted.
2. **No raw config values.** Raw config values are never printed; report file:line and the key name instead.
3. **Subagent depth = 1.** Inspectors never call any `/baransu:` skill and never dispatch further subagents.
4. **No unconfirmed mutation.** Never auto-apply fixes or auto-run destructive actions without explicit user confirmation.

## Two lanes share one report

- **Agent config health**: instruction drift across runtimes (Claude / Codex / others), permissions, hooks, MCP, skills, and memory supply chain.
- **AI maintainability health**: project context surface, verifier wrapper, generated-artifact checks, hotspot ownership, and stale or misleading durable docs.

## Budget posture

Start with the summary audit. Escalate to a deep audit only when:

- the user asks for a deep, full, complete, thorough audit（「深入」「完整」「徹底」「跑完整套」）, or
- the user explicitly mentions AI coding code rot, agent config drift, unclear context, missing verification, verifier output pointing at stale paths, or 「程式碼變爛」, or
- tracked project instructions or a remembered user preference say to run deep health checks by default, or
- the project is Complex tier, or
- the summary pass exposes a critical ambiguity that cannot be resolved locally.

Otherwise do not read full conversation extracts or launch inspector subagents. **Tell the user before escalating**, because deep health audits can consume significant token quota:

> 「即將升級為 deep 審計（會讀取對話樣本並派遣 inspector 子代理人，token 消耗顯著）。」

## Step 0: Assess project tier

Pick one. Apply only that tier's requirements.

| Tier | Signal | What's expected |
|---|---|---|
| **Simple** | <500 files, 1 contributor, no CI | AGENTS.md only; 0-1 skills; hooks optional |
| **Standard** | 500-5K files, small team or CI | AGENTS.md + 1-2 rules; 2-4 skills; basic hooks |
| **Complex** | >5K files, multi-contributor, active CI | Full layered setup: instructions + rules + skills + hooks + executable verification |

## Step 1: Collect data

Run the collection script in summary mode first. Do not interpret yet.

```bash
# Resolve scripts from the installed skill dir, falling back to the repo layout.
HEALTH_SCRIPTS_DIR="./scripts"
if [ ! -f "${HEALTH_SCRIPTS_DIR:-}/collect-data.sh" ]; then
  HEALTH_SCRIPTS_DIR="./plugins/baransu/skills/health/scripts"
fi
if [ ! -f "$HEALTH_SCRIPTS_DIR/collect-data.sh" ]; then
  echo "找不到 health collect-data.sh；請設定 CLAUDE_SKILL_DIR 或重新安裝 baransu plugin"
  exit 1
fi
bash "$HEALTH_SCRIPTS_DIR/collect-data.sh"
```

Sections may show `(unavailable)` when tools are missing:

- `jq` missing → conversation sections unavailable
- `python3` missing → MCP/hooks/allowedTools sections unavailable
- `settings.local.json` absent → hooks/MCP may be unavailable (normal for global-only setups)

Treat `(unavailable)` as insufficient data, not a finding. Do not flag those areas.

The collector includes both runtime-specific and agent-agnostic surfaces:

- `AGENT CONFIG SUMMARY` / `AGENT CONFIG DETAIL` for runtime and project instruction files.
- `AI MAINTAINABILITY SUMMARY` / `AI MAINTAINABILITY DETAIL` for project shape, verification surface, hotspot ownership, wrappers, and doc links.

## Step 1b: MCP live check

Test every MCP server: call one harmless tool per server. Record `live=yes/no` with error detail. Respect `enabled: false` (skip without flagging). For API keys, only check if the env var is set (`echo $VAR | head -c 5`), never print full keys.

## Step 1c: Safety and security checks

These run after collection and before Step 2 analysis. The first two apply to every audit; the third only to projects with long-running or autonomous agents.

### Security baseline checks

Run these on every audit, regardless of tier. They are the floor, not the ceiling.

**Deny-list floor.** Apply this only when the project or runtime exposes agent permission settings, hook settings, MCP settings, allowed/denied tools, or a documented autonomous-agent launcher. In that case, the settings should deny, at minimum: credential and key directories (SSH, cloud providers, GPG, gh CLI), secret files (`.env`, `credentials*`, `secrets*`), pipe-to-shell installers (`curl ... | bash`, `wget ... | sh`), and outbound shells (`ssh`, `scp`, `nc`). Report this as one concise WARN with the missing categories and suggested fix; let the reviewer fill in exact local paths from the environment. If no agent settings surface exists, report the deny-list as not applicable rather than a failure.

**Environment override surface.** Treat the following as attack surface, report when set in tracked files or shipped settings without a justification comment: API base-URL overrides (redirect all traffic to a third party), auto-trust flags for project-local MCP servers, wildcard tool allowlists (`allowedTools: ["*"]`), and permission-skip flags (`--dangerously-skip-permissions` or equivalents). Print file:line and the key name only; never print secrets.

### Memory and skill supply chain

Treat agent memory and third-party skills as supply-chain artifacts. They run with the user's privileges.

**Memory hygiene.** Audit the project's long-term agent memory store for secrets, tokens, or credentials (Critical), and for entries written by untrusted runs (subagent invoked on attacker-controlled input, loop iteration over external content); recommend rotation after such runs. For high-risk one-off runs (untrusted PDFs, uncontrolled scraping, third-party scripts), recommend disabling memory persistence for that session entirely. Also flag durable memory problems when they affect behavior: oversized injected summaries, stale or contradictory entries, missing project entrypoint references, or private paths copied into public instructions. Keep these as context findings, not code-review findings.

**Skill supply chain.** Third-party skills, plugins, and MCP servers run with the user's privileges. For each one not authored in this repo, check: source pinned to a release tag or revision (not `main`, a branch, or a remote git marketplace left tracking its latest head), hook handlers do not write to credential directories, MCP servers have explicit user consent (not auto-trusted by wildcard). Report unpinned sources or unreviewed hook handlers as Structural, not Critical, unless an active exploit signal is present.

### Long-running agent stop conditions

For projects that use loops, autonomous agents, or any long-running agent flow, the project must define explicit stop conditions. An agent that never stops is a budget and safety incident waiting to happen.

Audit for these four hard stop signals; flag the absence of each as a Structural finding:

1. **No progress across two consecutive checkpoints.** Same files touched, same errors logged, no new commits/tests/output. Recommend killing the loop and surfacing the state, not retrying.
2. **Repeated identical failure.** Same stack trace, same error message, same failed assertion three times in a row means the hypothesis is wrong; more attempts will not help.
3. **Cost or token budget exceeded.** Project should declare a per-run budget (tokens, API spend, wall-clock minutes). Loop exits when the budget is hit, not when work is done.
4. **External blockers.** Merge conflict on the target branch, dependency lock the agent cannot resolve, missing credential, network unreachable. Any of these halt the loop and ask the user, not retry forever.

The stop conditions should live in tracked project docs (`AGENTS.md`, the loop's launch script, or a dedicated config), not only in the agent's prompt. Prompts are forgettable; tracked config is enforceable. Recommend hooks (PostToolUse on the relevant tools) over prompt instructions when the project supports them: a hook physically cannot be skipped, a prompt instruction can. Confirm the host's hook coverage before recommending one: some agents only fire PostToolUse for a subset of tools, so a fixup that must run after file edits may belong on a Stop or session-end hook instead.

## Step 2: Analyze

Confirm the tier. Then route:

- **Simple:** Analyze locally. No subagents.
- **Standard:** Analyze locally from the summary output. Do not launch subagents by default. If the user asks for a deep/full/thorough audit, or if local analysis cannot classify a security/control issue, escalate to deep mode and explain the likely token cost.
- **Complex, remembered deep preference, explicit deep audit, or explicit AI maintainability audit:** Re-run collection with `bash "$HEALTH_SCRIPTS_DIR/collect-data.sh" auto deep`, then launch the relevant inspector subagents in parallel by spawning Codex subagents. Redact credentials to `[REDACTED]`.
  - **Inspector 1** (Context + Security): `plugins/baransu/agents/health-inspector-context.md`. Feed the `CONVERSATION SIGNALS` section.
  - **Inspector 2** (Control + Behavior): `plugins/baransu/agents/health-inspector-control.md`. Feed the detected tier.
  - **Inspector 3** (AI Maintainability): `plugins/baransu/agents/health-inspector-maintainability.md`. Feed only `TIER METRICS`, `AI MAINTAINABILITY SUMMARY` or `AI MAINTAINABILITY DETAIL`, and the script hotspot lists. Launch this inspector only for deep health audits, Complex projects, or explicit code-rot/AI-maintainability requests.
- **Fallback:** If a subagent fails, analyze that layer locally and note 「（本層由主代理人就地分析）」.

Each inspector file defines `Perspective / Mission / Principles / Lane-keeping` — no persona, no character voice. Subagent depth = 1: inspectors never call any `/baransu:` skill and never dispatch further subagents.

## Step 3: Report

Report in 繁體中文, with this shape:

**健康報告：{專案}（{tier} 級，{file_count} 檔）**

### [PASS] 通過項目（表格，最多 5 列）

### Finding 格式

```
- [嚴重度] <症狀>（{file}:{line} 若已知）
  原因：<一行理由>
  行動：<可直接複製執行的指令或修改>
```

The 「行動」 (action) must be directly copy-runnable. Do not write 「調查 X」 (investigate X) or 「考慮 Y」 (consider Y). If the fix is unknown, give a diagnostic command.

**Destructive-action gate.** Apply this if-then check to every emitted 「行動」 command before it leaves the report: IF the copy-runnable action mutates git tracking (e.g. `git rm --cached`), deletes files (`rm`), rewrites or discards history (`git reset --hard`, `git rebase`, `git filter-branch`), force-pushes (`git push --force`/`-f`), or touches credential/secret paths, THEN prefix that action line with 「⚠ 破壞性 / 不可逆」 and present it for explicit user confirmation before running — do not auto-run it. Non-destructive diagnostic and read-only commands stay unmarked and need no confirmation.

### [!] 嚴重 — 立即修

Rules violated, dangerous allowedTools, MCP overhead >12.5%, security findings, leaked credentials.

Example:

```
- [!] `settings.local.json` 已提交進 git（暴露 MCP tokens）
  原因：外洩的 token 可經由已安裝的 MCP server 達成遠端執行
  行動：⚠ 破壞性 / 不可逆（需使用者確認後再執行）`git rm --cached .claude/settings.local.json && echo '.claude/settings.local.json' >> .gitignore`
```

### [~] 結構性 — 儘快修

Agent instructions in the wrong layer, missing hooks, oversized descriptions, verifier gaps.

**Instruction drift across runtimes.** Use `AGENT CONFIG SUMMARY` first. Report a Structural finding when `AGENTS.md` and runtime-specific files both contain substantial guidance without delegation, when a runtime config lacks trust for the current project, when settings or package metadata point at missing skill roots, when project agent instructions are missing, or when runtime-specific instructions contradict the shared project source of truth. Also report when important rules live only in ignored or private local instruction overlays but the tracked/public docs lack them; those overlays are private context, not durable project source of truth. Do not print raw config values. Secrets, tokens, keys, and passwords must appear only as `[REDACTED]`.

Quick check from the project root:

```bash
bash "$HEALTH_SCRIPTS_DIR/check-agent-context.sh" . summary
```

**AI-maintainability gaps.** Use `AI MAINTAINABILITY SUMMARY` in summary mode and `AI MAINTAINABILITY DETAIL` in deep mode. Report `FAIL` when the project has no executable verification command, no agent instruction surface for a non-trivial repo, or broken doc references. Report `WARN` when instructions exist but lack a project map, verification guidance, boundary/non-goal language, when TODO/HACK markers are concentrated, when large source hotspots lack ownership/boundary and verification guidance, or when durable docs contain raw one-off review reports, scorecards, dated line references, or diagnostic dumps instead of stable invariants. For missing `docs/`, `specs/`, `.specify/`, `HANDOFF.md`, `CHANGELOG`, issue templates, and PR templates, set the flag by Step 0's tier ladder without judgment: Simple tier → always informational; Standard tier → `WARN` only if active handoff is present (multi-contributor or CI detected), else informational; Complex tier → `FAIL` when absent. The action for stale reports is to extract stable rules into public instructions, rules, references, or verifier scripts, then remove or archive the transient report.

**Conversation-derived guidance.** When a health audit reads recent agent conversations, do not recommend copying the conversation or a scorecard into docs. Recommend a candidate-matrix pass instead:

| Field | Question |
|---|---|
| Repeated failure | Did this recur across fixes, releases, agents, or user reports? |
| Durable invariant | Can the lesson be stated as a stable rule, not a dated incident summary? |
| Target layer | Should it live in project instructions, a reusable skill, a global rule, or private memory? |
| Verifier | Is there a deterministic command, script, artifact check, or runtime smoke that can enforce it? |
| Redaction risk | Does the lesson require local paths, issue numbers, customer details, machine state, secrets, or unpublished release facts? |

Layering rule: project-specific commands, app names, artifact names, and release rituals stay in the project; reusable workflows belong in shared skills; universal honesty and verification rules belong in global CLAUDE/AGENTS instructions; private user preferences and one-machine facts stay in memory. If the lesson cannot pass the redaction-risk field, keep it out of public guidance.

**Concentrated fix chains.** Run `git log --oneline --since='2 weeks ago' | grep -i fix` and group by area (the prefix before `:` or `(`). When the same area has 3+ fix commits in a short window, it signals a missing structural invariant: each fix is a guess at a rule that was never written down. Report a Structural `WARN` with the area name, fix count, and recommend adding an explicit rule to `AGENTS.md` / `CLAUDE.md` / project rules that captures the invariant those fixes were converging toward. A concentrated fix chain that touches the same file 4+ times is a stronger signal than scattered fixes across different files.

**Hotspot ownership gaps.** In deep mode, read `HOTSPOT OWNERSHIP SURFACE`. If a largest source file exceeds the hotspot threshold and `AGENTS.md` / `CLAUDE.md` / shared instruction files do not name who owns the hotspot, what boundary should stay stable, and which verification command covers it, report a Structural `WARN`. Do not treat documented large files as code rot by size alone; some modules are intentionally large.

**Missing stable verifier wrapper.** If the repo exposes multiple verification commands through CI, scripts, or manifests but `Makefile` has no `check`, `test`, or `verify` target, report a Structural `WARN`. This is an AI-maintainability gap because agents need one stable default entrypoint, not because the project is broken.

Quick check from the project root:

```bash
bash "$HEALTH_SCRIPTS_DIR/check-maintainability.sh" . summary
```

For deep audits:

```bash
bash "$HEALTH_SCRIPTS_DIR/check-maintainability.sh" . deep
```

Keep actions concrete and non-invasive: add or fix the smallest useful instruction surface, add one executable validation command, document hotspot ownership and tests, split only when the boundary is already clear, or repair the broken reference. Do not propose broad rewrites from the script output alone.

**Broken doc references.** Scan `AGENTS.md`, `CLAUDE.md`, `.claude/rules/*.md`, and every `.claude/skills/*/SKILL.md` for references shaped like `@<path>`, `~/.claude/rules/<name>.md`, `~/.claude/skills/<name>/`, `docs/<name>.md`, or `references/<name>.md`. For each match, check that the target exists on disk. Report every "referenced but missing" pointer with the source file and line.

Common offenders:
- A project-level rule references a global rule file that was never created (e.g. `~/.claude/rules/swift.md`).
- A `CLAUDE.md` uses an `@AGENTS.md` placeholder but the actual `AGENTS.md` is missing or empty.
- A skill body references `references/<name>.md` but only `references/<name>-v2.md` exists.
- A rule file references a deleted skill path.

Quick check from the project root:

```bash
bash "$HEALTH_SCRIPTS_DIR/check-doc-refs.sh" .
```

The checker resolves `@...` and `docs/...` from the project root, expands `~`, resolves `references/...` from each `.claude/skills/<name>/SKILL.md` directory, checks every reference on a line, skips fenced code examples, and exits non-zero when any target is missing.

Report missing references as Structural findings, not Critical, unless the missing file is named as a hard dependency.

**Broken Markdown references.** In deep mode, `check-maintainability.sh` also scans repository Markdown links. Report these as Structural findings when they point to missing local files, especially design, security, release, or handoff docs that agents may follow during future work.

**Stale verifier cache output.** If validation output points at a deleted temp worktree or non-existent `/tmp` / `/private/tmp` file, parse the captured log with:

```bash
bash "$HEALTH_SCRIPTS_DIR/check-verifier-output.sh" . <log-file>
```

Only use this script for existing command output supplied by the user or generated during the current audit. Do not run project tests just to feed this checker. Known actions include `golangci-lint cache clean`, `go clean -cache -testcache`, and `npm cache verify`; unknown tools get a diagnostic rerun action.

### [-] 漸進 — 有空再修

Outdated items, global vs local placement, context hygiene, stale allowedTools entries.

---

If no issues: 「所有相關檢查通過，無需修正。」

## Non-goals

- Never audit the baransu plugin's own structure — that is `scripts/verify-skills.py`'s job.
- Never auto-apply fixes without confirmation.
- Never apply complex-tier checks to simple projects.
- Never act as a heavy lint, typecheck, duplication, or architecture-rewrite substitute; `/health` reports maintainability guardrails and concrete next actions only.

## Gotchas

| What happened | Rule |
|---|---|
| Missed the local override | Always read `settings.local.json` too; it shadows the committed file |
| Subagent timeout reported as MCP failure | MCP failures come from the live probe, not data collection |
| Flagged intentionally noisy hook as broken | Ask before calling a hook "broken" |
| Hook seemed not to fire, but it did — a later UI element rendered above it | Hook firing order is not visual order. Before re-editing the hook config: (a) confirm with `--debug` or by piping output, (b) check whether a diff dialog, permission prompt, or other UI element rendered on top and pushed the hook output offscreen, (c) only then suspect the hook itself. |
| `/health` burned too much quota on first run | Stay in summary mode first. Full conversation extracts and inspector subagents are deep-audit tools, not the default path for Standard projects. |
| Treated missing specs/docs as a failure | Decision artifacts are optional by default. Escalate missing docs/specs only when the tier, active handoff risk, or user request makes them necessary. |
| Treated an ignored AGENTS/CLAUDE file as durable project truth | Report whether the rule is tracked and distributed. Local overlays can inform the audit, but durable fixes belong in public repo docs or shipped skill/rule files. |
| Treated a review scorecard as maintainability documentation | Scorecards are snapshots. Extract the invariant and verification path, then remove or archive the report instead of calling the score itself a durable rule. |
