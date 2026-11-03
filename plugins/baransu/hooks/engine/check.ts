// From raw fields to a Check, and which paths a check covers. Shared by every converter: a converter only
// parses its format; the meaning of the fields (defaults, one action per check) is decided once, here.

import type { Builtin, Check, CheckAction, Moment, RawCheck } from './types'

const MOMENTS: readonly Moment[] = ['edit', 'commit', 'done', 'bash', 'manual']

/**
 * Fill defaults exactly as readChecks does today: `on`/`files`/`ignores` accept a string or a list;
 * a severity other than error/off is warn; message defaults to ''.
 * `severity = "off"` → undefined: the check is not in force, and the config source leaves it out (today:
 * `checks.filter(c => c.severity !== 'off')`).
 * The action: `builtin` wins, then `forbid`, then `run` — today's precedence in runMoment. None of the three →
 * `{ kind: 'none' }`: still valid, it carries only a `changed` note (as today). An unknown builtin name is kept
 * as is and matches no built-in, so it does nothing (as today).
 * Never throws: a field of the wrong shape (`run` given as a string, `on` as a number) is dropped and the
 * check kept, with no problem reported — as today's reader does. Only a converter's parse error makes a
 * 「設定讀不懂」 problem.
 */
export function checkFrom(id: string, raw: RawCheck): Check | undefined {
  const t = raw as Record<string, unknown>
  if (t.severity === 'off') return undefined
  const list = (v: unknown): string[] =>
    (Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : typeof v === 'string' ? [v] : [])
  const str = (v: unknown) => (typeof v === 'string' ? v : undefined)
  // Today a builtin or forbid that is an empty string is no action (`if (c.builtin)`, `if (c.forbid)`),
  // while a run list counts even when empty (`else if (c.run)`).
  const builtin = str(t.builtin)
  const forbid = str(t.forbid)
  const action: CheckAction = builtin
    ? { kind: 'builtin', name: builtin }
    : forbid
      ? { kind: 'forbid', pattern: forbid }
      : Array.isArray(t.run)
        ? { kind: 'run', argv: list(t.run) }
        : { kind: 'none' }
  return {
    id,
    on: list(t.on).filter((m): m is Moment => (MOMENTS as readonly string[]).includes(m)),
    skills: list(t.on).filter(m => m.startsWith('skill:')).map(m => m.slice('skill:'.length)).filter(Boolean),
    severity: t.severity === 'error' ? 'error' : 'warn',
    files: list(t.files),
    ignores: list(t.ignores),
    action,
    message: str(t.message) ?? '',
    changed: str(t.changed),
    language: str(t.language),
    redo: str(t.redo),
  }
}

export const BUILTINS: readonly Builtin[] = [
  'git-facts', 'secret-files', 'built-before-commit', 'up-to-date', 'session-record', 'worktree-cleanup',
  'destructive-preview', 'explain-before-edit', 'report-before-stop', 'correction-to-lint', 'user-language',
]

/** Whether a check runs before the skill invoked as `name`: `skill:baransu:hypothesis` names it exactly, and
 *  `skill:hypothesis` names it by its own part after the plugin. Pure. */
export const namesSkill = (c: Check, name: string): boolean =>
  c.skills.some(s => s === name || name.endsWith(`:${s}`))

/** The built-in a check runs, or undefined when its action is not a built-in. */
export const builtinOf = (c: Check): string | undefined => (c.action.kind === 'builtin' ? c.action.name : undefined)

// ---- globs: no "/" matches the file name anywhere; with "/" the repo path ----
function globRe(g: string): RegExp {
  let r = ''
  for (let i = 0; i < g.length; i++) {
    const c = g[i]
    if (c === '*') {
      if (g[i + 1] === '*') {
        i++
        if (g[i + 1] === '/') { i++; r += '(?:.*/)?' } else r += '.*'
      } else r += '[^/]*'
    } else if (c === '?') r += '[^/]'
    else r += c.replace(/[.+^${}()|[\]\\]/g, '\\$&')
  }
  return new RegExp('^' + r + '$')
}
function matches(rel: string, globs: readonly string[]): boolean {
  const base = rel.slice(rel.lastIndexOf('/') + 1)
  return globs.some(g => globRe(g).test(g.includes('/') ? rel : base))
}

/** A glob with no "/" matches the file name anywhere; with "/" the root-relative path. */
export function inScope(rel: string, c: Check): boolean {
  return (c.files.length === 0 || matches(rel, c.files)) && !matches(rel, c.ignores)
}

/** The check's scope as git pathspecs, for `git grep` at commit and done. */
export function pathspecs(c: Check): string[] {
  const glob = (g: string) => (g.includes('/') ? g : `**/${g}`)
  const inc = c.files.length ? c.files.map(g => `:(glob)${glob(g)}`) : ['.']
  return [...inc, ...c.ignores.map(g => `:(exclude,glob)${glob(g)}`)]
}

/** A path relative to root when it is inside it (case-insensitive prefix, as today), else unchanged. */
export function relTo(root: string, file: string): string {
  const f = file.replace(/\\/g, '/')
  return f.toLowerCase().startsWith(root.toLowerCase() + '/') ? f.slice(root.length + 1) : f
}
