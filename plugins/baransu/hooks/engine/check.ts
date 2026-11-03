// From raw fields to a Check. Shared by every converter: a converter only parses its format; the meaning of the
// fields (defaults, one action per check, the scope, the timings) is decided once, here. Which paths a check
// covers is the scope's business (scope/evaluate.ts); what a level does at a timing is timing.ts's.

import { FACTS } from './scope/lens'
import { scopeFrom, TIMING_OF } from './scope/parse'
import { INVALID, parseTiming, timingText, verdictOf, type Timing, type TimingKey } from './timing'
import type { Builtin, Check, CheckAction, RawCheck, Severity } from './types'

/** What readCheck makes of one check file. */
export type CheckRead =
  | { readonly kind: 'check'; readonly check: Check }
  | { readonly kind: 'off' }
  | { readonly kind: 'problems'; readonly problems: readonly string[] }

/**
 * Where each built-in runs: fixed; its file's `on` may only add a wait (after:*). Its level is checked against
 * every timing here, so a level a timing refuses is a problem. A built-in tied to no act — the session start
 * (worktree-cleanup), the person's message (correction-to-lint), the model's rows and the system prompt
 * (user-language; git-facts' prompt part) — has no cell to refuse it: its own code reads the level. For
 * user-language and correction-to-lint, `info` is the person's card (or notice) only; any other level asks the
 * model (a 重新 to restate, a note to consider a check) — nothing there can be held.
 * explain-before-edit runs before the first file change of a turn: an edit, or a command that writes files.
 */
export const BUILTIN_AT: Readonly<Record<Builtin, readonly TimingKey[]>> = {
  'git-facts': ['pre:commit', 'pre:push'],
  'secret-files': ['pre:commit'],
  'built-before-commit': ['pre:commit', 'pre:push'],
  'up-to-date': ['pre:commit', 'pre:push'],
  'session-record': ['pre:skill'],
  'worktree-cleanup': [],
  'destructive-preview': ['pre:bash'],
  'explain-before-edit': ['pre:edit', 'pre:bash'],
  'report-before-stop': ['pre:stop'],
  'correction-to-lint': [],
  'user-language': [],
}

const SEVERITIES: readonly Severity[] = ['error', 'check', 'retry', 'warn', 'info']

/**
 * `on` accepts a string or a list of timings (timing.ts parseTiming); a timing it cannot read — an old name
 * included — is a problem, and so is a level whose cell at one of the timings is INVALID (`check` after an
 * act, `error` on post:agent). A check whose `on` is empty runs where its actions imply (TIMING_OF).
 * A severity other than the five (and off) is warn; message defaults to ''.
 * `severity = "off"` → off: the check is not in force, and the config source leaves it out.
 * The action: `builtin` wins, then `forbid`, then `run`. None of the three → `{ kind: 'none' }`: it carries only
 * its message (and a `changed` note). An unknown builtin name is kept as is and matches no built-in.
 * `remind = "true"`: its message goes into the system prompt; refused on a check with a file scope.
 * Any problem keeps the whole check out of force; each comes back so the config source shows it as
 * 「設定讀不懂：checks/<id>：<text>」. Never throws.
 */
export function readCheck(id: string, raw: RawCheck, factNames: readonly string[] = Object.keys(FACTS)): CheckRead {
  const t = raw as Record<string, unknown>
  if (t.severity === 'off') return { kind: 'off' }
  const list = (v: unknown): string[] =>
    (Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : typeof v === 'string' ? [v] : [])
  const str = (v: unknown) => (typeof v === 'string' ? v : undefined)
  const problems: string[] = []
  const scope = scopeFrom(t, factNames)
  if (!scope.ok) problems.push(...scope.problems)
  // A builtin or forbid that is an empty string is no action, while a run list counts even when empty.
  const builtin = str(t.builtin)
  const forbid = str(t.forbid)
  const action: CheckAction = builtin
    ? { kind: 'builtin', name: builtin }
    : forbid
      ? { kind: 'forbid', pattern: forbid }
      : Array.isArray(t.run)
        ? { kind: 'run', argv: list(t.run) }
        : { kind: 'none' }
  const severity: Severity = SEVERITIES.find(s => s === t.severity) ?? 'warn'

  const on: Timing[] = []
  for (const w of list(t.on)) {
    const p = parseTiming(w)
    if (!p.ok) problems.push(p.problem)
    // A built-in runs where BUILTIN_AT says; its `on` may only add a wait (session-record after:edit:10m).
    else if (action.kind === 'builtin' && !p.timing.key.startsWith('after:')) problems.push(`內建檢查的時機是固定的：「${w}」拿掉，只能另外加 after:<動作>:<多久>`)
    else on.push(p.timing)
  }
  // The level against every timing it runs at: written, implied by its actions, or a built-in's own.
  const keys: (TimingKey | 'manual')[] =
    action.kind === 'builtin'
      ? [...(BUILTIN_AT[action.name as Builtin] ?? []), ...on.map(x => x.key)]
      : on.length
        ? on.map(x => x.key)
        : scope.ok ? [...new Set(scope.scope.actions.map(a => TIMING_OF[a]))] : []
  for (const k of keys) {
    if (verdictOf(k, severity) === INVALID) {
      const said = on.find(x => x.key === k)
      problems.push(`${severity} 不能用在 ${said ? timingText(said) : k}：${WHY[k] ?? '這個時機沒有東西可以擋或重做'}`)
    }
  }

  const remind = t.remind === true || t.remind === 'true'
  if (remind && scope.ok) {
    const w = scope.scope.where
    if (w.folders.length || w.files.length || w.trees.length || w.exts.length || scope.scope.base.kind !== 'all')
      problems.push('remind 只能用在沒有檔案範圍的檢查：有 folder／file／ext／scope 的提醒，放進系統提示會對每個檔都說')
  }

  if (problems.length || !scope.ok) return { kind: 'problems', problems }
  return {
    kind: 'check',
    check: {
      id,
      on,
      severity,
      scope: scope.scope,
      action,
      message: str(t.message) ?? '',
      changed: str(t.changed),
      language: str(t.language),
      redo: str(t.redo),
      ...(remind ? { remind: true } : {}),
    },
  }
}

/** Why a level is refused at a timing, in the person's words. */
const WHY: Partial<Record<TimingKey | 'manual', string>> = {
  'post:edit': '改完了才檢查，沒有東西可以擋；要擋一次請用 pre:edit',
  'post:bash': '指令跑完了才檢查，沒有東西可以擋；要擋一次請用 pre:bash',
  'post:commit': 'commit 完了才檢查；要擋請用 pre:commit',
  'post:push': 'push 完了才檢查；要擋請用 pre:push',
  'post:agent': 'subagent 結束後擋不住它，也沒辦法要它重做，只能 warn 或 info',
  'around:agent': 'subagent 結束後擋不住它，也沒辦法要它重做，只能 warn 或 info',
  'pre:compact': '擋下壓縮會讓對話塞滿，也沒有一步可以重做，只能 warn 或 info',
  'post:compact': '壓縮後沒有一步可以重做',
  'post:file': '檔案是在 Claude 之外改的，只能 warn 或 info',
  'post:retry': '回答「重新」之後再要它重做，會一直要下去；用 error 或 warn',
  'pre:skill': 'skill 只叫一次，沒有「下一次同樣的動作」可以放行或重做；要它先停下就用 error',
  'after:edit': '時間到了只能提醒，只能 warn 或 info',
  'after:bash': '時間到了只能提醒，只能 warn 或 info',
  'after:commit': '時間到了只能提醒，只能 warn 或 info',
  'after:push': '時間到了只能提醒，只能 warn 或 info',
}

export const BUILTINS: readonly Builtin[] = Object.keys(BUILTIN_AT) as Builtin[]

/** Whether a check runs before the skill invoked as `name`: `pre:skill:baransu:hypothesis` names it exactly,
 *  and `pre:skill:hypothesis` names it by its own part after the plugin. Pure. */
export const namesSkill = (c: Check, name: string): boolean =>
  c.on.some(t => t.key === 'pre:skill' && (t.skill === name || name.endsWith(`:${t.skill}`)))

/** The built-in a check runs, or undefined when its action is not a built-in. */
export const builtinOf = (c: Check): string | undefined => (c.action.kind === 'builtin' ? c.action.name : undefined)

/** A path relative to root when it is inside it (case-insensitive prefix, as today), else unchanged. */
export function relTo(root: string, file: string): string {
  const f = file.replace(/\\/g, '/')
  return f.toLowerCase().startsWith(root.toLowerCase() + '/') ? f.slice(root.length + 1) : f
}
