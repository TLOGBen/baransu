---
name: contract
description: 'Pins observable acceptance for a medium-band change before implementation:
  a CONTRACT.md at the project root with goal and scope, premises tagged verified
  or inferred, stable criterion IDs each carrying an expected result, a consequential
  counterexample and a real evidence path, exact requirement constants, and recorded
  decisions. Owns the sealed-marker grammar and archives a sealed contract before
  writing over it. Trigger On ''$contract'', ''寫合約'', ''一頁合約'', ''開工合約'', ''pin the
  criteria''. Not for an unsliced multi-module effort (slice it first, then one contract
  per slice) or post-hoc verification (use $seal). 繁體中文輸出。'
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# contract — pin what must hold, then let implementation judge how

## Codex Port Adapter - Bundled Agent Resolution

This plugin does not assume package-local TOMLs are auto-registered as custom
agents. The required definitions for this skill are bundled at
`../../.codex-agents/<agent-name>.toml`: `verifier`.

Before every named-agent dispatch:

1. Resolve the exact bundled TOML from this `SKILL.md` directory (strip a
   leading `baransu:` namespace from the requested name).
2. Verify the file exists, then pass its absolute path and the task input to a
   generic Codex subagent. The first instruction to that subagent is to read
   the TOML's `developer_instructions` completely before doing any task work
   and to treat relative paths as relative to the TOML file.
3. If the TOML is missing or unreadable, stop with
   `AGENT_DEFINITION_MISSING: <path>`. Never invent, summarize, or substitute a
   role from the agent name.


Write criteria strong enough to reject a broken result, then let implementation judgment operate. The contract records WHAT must hold; it does not prescribe HOW.

All user-facing output and the contract itself are in Traditional Chinese; keep code, identifiers, and requirement constants exactly as supplied.

## Outcome Contract

- **Outcome**: One `CONTRACT.md` for the stated task — goal and scope, premises, criteria with stable IDs, requirement constants, decisions — written to rejection strength, at the project root (or the path the user names).
- **Done when**: The contract is on disk with every section filled from evidence or explicitly marked as awaiting evidence; every criterion has an observable expected result, a consequential counterexample or exclusion, and a real evidence path; the user has seen the contract and any unresolved decision that is theirs to make.
- **Evidence**: The written `CONTRACT.md` and, in the conversation, the list of criteria with each one's evidence path and required/optional status.
- **Output**: `CONTRACT.md` (~35 lines) in the conversation and on disk; operational messages in Traditional Chinese.
- **Automation**: ultracode=neutral, loop=drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

PAUSE classification for non-interactive drivers: `references/loop-pauses.md`. Read `references/acceptance.md` before writing or materially revising a contract — it says what each section needs and what it must not contain.

## Step 1 — Ground

Read the code or authoritative material on which the criteria depend. Separate verified premises (source cited) from assumptions and from missing evidence. For greenfield work, state that no existing implementation was available; do not fabricate code facts.

An uncertain data source, schema, permission rule, or domain premise remains uncertain until supported. Isolate the criterion that depends on it; still pin the adjacent independent filters, mappings, and authorization dimensions. Missing evidence is not a blanket waiver.

## Step 2 — Write CONTRACT.md

```markdown
# CONTRACT — {task title}
> STATUS: sealed（{ISO 日期}）— {五點結果一行摘要}

## 目標與範圍
{1-3 lines: the observable difference when this is done; explicit user choices and authority limits}

## 前提
{each premise the criteria rest on, tagged `已驗`(source cited) / `推論` / `待證`; name which criteria depend on each uncertain one}

## 條文
{stable IDs; each: expected observable result, consequential counterexample or exclusion, real evidence path, required/optional and the impact of a violation when that changes verification}
- [ ] A1: ...
- [ ] A2: ...

## 需求常數
{requirement constants exactly as supplied, when any exist; fenced, copy-paste source of truth}

## 決策與修正
{material decisions or corrections, with evidence and authority, without rewriting unrelated criteria}
```

**Sealed-marker grammar (single authority).** The `> STATUS: sealed` line shown under the H1 above is the one and only grammar authority for the sealed marker: `$seal` writes it, `$seal` and `$ship` detect it, and both cite this template as the single source. Position: line 2 of CONTRACT.md, immediately after the H1. Idempotent single line: a re-seal overwrites the existing marker in place — never appends a second line. The marker certifies only that the contract was clean at seal time; it says nothing about later changes. `$contract` itself never writes this line — a freshly written contract has no STATUS line; it appears only after `$seal` passes.

**What to pin.** Observable outcomes, consequential failure cases, affected boundaries, and the exact constants the requirement supplied. Use exact text or explicit exclusions when extra fields would be a defect; do not pin arbitrary wording, a shared helper, or a test name merely to prescribe HOW. A test plan is a method, not a product requirement. The assertability rules in `../_shared/contract-gate.md` remain the reference for what counts as assertable.

**Traps become criteria.** Turn a discovered consequential trap into an independently assertable condition with an evidence path, and check that the path exercises the real behavior rather than a mock of the very layer being certified.

**Required is not the same as costly.** Separate whether a criterion is required from how costly its violation is. Preserve explicit requirements even when their implementation is small; do not silently downgrade a user requirement to optional because it is low impact. Describe the protected outcome and consequence so `$seal` can size its verification: visual prominence is not importance, and a hidden authorization or data-integrity defect can outweigh visible polish. A requirement constant such as a color value is pinned exactly, and its evidence path is an exact comparison — not a mutation exercise.

**Do not invent.** No numeric targets to fill the form, no premises the material did not support. An unknown premise never waives adjacent independent criteria.

## Step 3 — Confirm

Present the contract and any material unresolved decision. Existing clear user choices and applicable authorization count; do not demand a ceremonial reconfirmation. Pause only where a changed outcome, an authority boundary, or a user-owned tradeoff requires a new decision.

If a CONTRACT.md already exists at the target path, first check for the sealed marker (detection form — never grep the whole file):

```bash
head -3 "$f" | grep -qF '> STATUS: sealed'
```

If sealed: it is a completed artifact — `mv` it to `.codex/archived/{filename}-{unix_timestamp}` (create the directory if needed), then write the new contract without asking, outputting:
「偵測到已封緘合約，已先歸檔至 .codex/archived/{filename}-{unix_timestamp}，續寫新合約。」
If unsealed: if its content belongs to the same task, revise it in place; if it belongs to a different task, stop and ask the user to name a new path (e.g. `CONTRACT-{slug}.md`) — silent overwrite is forbidden.

On write, output:
「合約已釘死：{path}（{N} 條條文、{K} 個需求常數）。實作時照抄需求常數；完工後跑 $seal 驗收。」

## Revisions

Preserve a task's record and its evidence history. If scope changes, revise only the affected criteria, recording the evidence and authority for that revision. An evidence-backed premise correction is a narrow revision, not a new goal: when it changes a user-owned value, scope, or authority decision, pause for that decision; when it only corrects an observed implementation fact, record it and continue within the original authorization.

Contract creation does not certify implementation. Hand the same record to implementation or to `$seal` only when the user's request includes that work.

## Not-for boundaries

- An effort spanning several interdependent modules → slice it first; one contract per slice.
- Verifying finished work → `$seal`; a second opinion on any artifact → `$review`.
- A single-file fix with a clear scope → implement directly under `../_shared/tdd.md` §7; a contract would be ceremony.
