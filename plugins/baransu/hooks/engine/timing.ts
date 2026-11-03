// When a check runs, and what its severity means there. THE one place: "what does severity X do at side Y
// of act Z" is one cell of TABLE below, and nothing else decides it.
//
// Three readers, one table:
//   - readCheck (check.ts): a timing that is not a row of TABLE, or a severity whose cell is INVALID, is
//     「設定讀不懂」 and keeps the check out of force. No other code decides validity.
//   - the engine (engine.ts): `settle(key, findings)` turns findings into one Settled — does the act go on,
//     what the model hears. Every entry point calls it; none re-derives a severity's meaning.
//   - format.md's 時機 section is this table in words; `/lint show` prints each check's row.
//
// Pure: no outside, no state. (.claude/draft/lint-timing.md)

import type { Finding, Severity } from './types'

// ---------------------------------------------------------------- the vocabulary

/** pre: before the act, it can still be stopped. post: after it. around: after it, reading the difference
 *  between a snapshot before and one after. after: a set time after the last such act, if none followed. */
export type Side = 'pre' | 'post' | 'around' | 'after'
export type Act = 'edit' | 'bash' | 'commit' | 'push' | 'skill' | 'stop' | 'agent' | 'compact' | 'file' | 'retry'

/**
 * What one severity does at one timing, as two answers:
 *   gate — does the act go on?  pass | hold (refused; at pre:stop at most STOP_HOLDS times a turn) |
 *          hold-once (refused once; the same act in a later response of the same actor passes)
 *   tell — what the model hears: fix (repair what was done) | redo (a 重新 request; its answer is checked at
 *          post:retry) | line (one line) | card (nothing: the person's card only)
 */
export type Verdict = { readonly gate: 'pass' | 'hold' | 'hold-once'; readonly tell: 'fix' | 'redo' | 'line' | 'card' }
export const INVALID = 'invalid' as const
export type Row = { readonly [S in Severity]: Verdict | typeof INVALID }

const v = (gate: Verdict['gate'], tell: Verdict['tell']): Verdict => ({ gate, tell })

/** Before an act: it can still be stopped. */
const PRE: Row = { error: v('hold', 'line'), check: v('hold-once', 'line'), retry: v('pass', 'redo'), warn: v('pass', 'line'), info: v('pass', 'card') }
/** After an act (around too: it runs after). Nothing is left to stop, so `check` is a config problem rather
 *  than silently read as warn (the user's words keep their meaning; one cell to change if that ever flips). */
const POST: Row = { error: v('pass', 'fix'), check: INVALID, retry: v('pass', 'redo'), warn: v('pass', 'line'), info: v('pass', 'card') }
/** Only telling: no act to stop and nothing the model can redo in place. */
const TELL: Row = { error: INVALID, check: INVALID, retry: INVALID, warn: v('pass', 'line'), info: v('pass', 'card') }

/** Every timing a check may name. Per-act exceptions are written as a difference from the side's row. A key
 *  absent here (`post:skill`, `pre:agent`, `around:stop` …) is not a timing. */
export const TABLE = {
  'pre:edit': PRE,
  'post:edit': POST,
  'around:edit': POST,
  'pre:bash': PRE,
  'post:bash': POST,
  'around:bash': POST,
  'pre:commit': PRE,
  'post:commit': POST,
  'around:commit': POST,
  'pre:push': PRE,
  'post:push': POST,
  // No around:push: a push does not move HEAD, so a snapshot of it before and after never differs.
  // A skill has no end the host shows, so only its start. `hold` here is an instruction in the skill's text to
  // stop (skill.prompt can only add text); `check` has no "same act in a later response" — a skill is invoked
  // once — so it is a config problem rather than a silent error.
  'pre:skill': { ...PRE, check: INVALID, retry: INVALID },
  // The turn may not end yet: classic.Stop's block re-prompts the model in the same turn (measured
  // 2026-11-03). check and retry hold once (the host's stop_hook_active says "held already"); retry carries
  // a 重新. A pass line cannot ride a Stop (its additionalContext is unmeasured): it is queued.
  'pre:stop': { ...PRE, retry: v('hold-once', 'redo') },
  // SubagentStop's block does not make the subagent go on (measured 2026-11-03): only telling.
  'post:agent': TELL,
  'around:agent': TELL,
  // Refusing a compaction leaves the conversation full: worse than a missed check.
  // Nothing to redo before a compaction either: warn and info only (the mod's own carry-over of what is owed
  // into the instructions is not a check's level).
  'pre:compact': TELL,
  'post:compact': { ...POST, retry: INVALID },
  // FileChanged cannot reach the model: error reads as warn, the line is queued.
  'post:file': { ...TELL, error: v('pass', 'line') },
  // A retry on the answer to a 重新 would ask again for every answer, with no end: not a level here. The
  // answer's warn stays on the person's card (as since 8.41): the model already redid the step once.
  'post:retry': { ...POST, retry: INVALID, warn: v('pass', 'card') },
  'after:edit': TELL,
  'after:bash': TELL,
  'after:commit': TELL,
  'after:push': TELL,
} as const satisfies Record<string, Row>

export type TimingKey = keyof typeof TABLE
export type AfterKey = Extract<TimingKey, `after:${string}`>

/** pre:stop with `error`: the turn is held at most this many times; after that its findings read as warn
 *  and the person is told, so a check that cannot pass never traps the turn. */
export const STOP_HOLDS = 3
/** The shortest `after:` wait: one timer per act, so a shorter one would pile up in a burst of edits. */
export const MIN_AFTER_MS = 60_000

// ---------------------------------------------------------------- a check's timing

/** One parsed entry of `on`. `skill` only on pre:skill; `ms` only on after:*. `manual` (/lint) runs every
 *  check on files, whatever its timing, and is written on its own for a check that runs only then. */
export type Timing = { readonly written: string } & (
  | { readonly key: Exclude<TimingKey, 'pre:skill' | AfterKey> }
  | { readonly key: 'pre:skill'; readonly skill: string }
  | { readonly key: AfterKey; readonly ms: number }
  | { readonly key: 'manual' }
)

/** The names before this change; read as a problem that points to the migration, never as the new meaning. */
const OLD = new Set(['edit', 'bash', 'commit', 'done', 'reply'])
const UNIT: Record<string, number> = { s: 1000, m: 60_000, h: 3_600_000 }

/**
 * `"<side>:<act>[:<arg>]"` | `"manual"` → a Timing, or the problem the person reads.
 *   an old name (edit, bash, commit, done, skill:x, reply) → 「舊寫法 x：跑 /lint sync」
 *   pre:skill:<name>                → the skill (a name is required)
 *   after:<act>:<n>(s|m|h)          → the wait (at least MIN_AFTER_MS)
 *   any other <side>:<act> in TABLE → itself; an argument there is a problem
 */
export function parseTiming(written: string): { ok: true; timing: Timing } | { ok: false; problem: string } {
  const w = written.trim()
  if (w === 'manual') return { ok: true, timing: { key: 'manual', written: w } }
  if (OLD.has(w) || /^skill:/.test(w)) return { ok: false, problem: `舊寫法「${w}」：跑 /lint sync 換成 pre／post／around` }
  if (!w.includes(':')) return { ok: false, problem: `「${w}」看不懂：要寫成 pre／post／around／after:<動作>，例如 pre:bash` }
  const [side, act, ...rest] = w.split(':')
  const key = `${side}:${act}`
  if (!Object.hasOwn(TABLE, key)) return { ok: false, problem: `沒有「${key}」這個時機` }
  const arg = rest.join(':')
  if (key === 'pre:skill') {
    if (!arg) return { ok: false, problem: 'pre:skill 要寫 skill 名字，例如 pre:skill:ship' }
    return { ok: true, timing: { key, skill: arg, written: w } }
  }
  if (side === 'after') {
    const m = /^(\d+)(s|m|h)$/.exec(arg)
    if (!m) return { ok: false, problem: `${key} 要寫等多久，例如 ${key}:10m` }
    const ms = Number(m[1]) * UNIT[m[2]]
    if (ms < MIN_AFTER_MS) return { ok: false, problem: `${key} 至少要等 1 分鐘` }
    return { ok: true, timing: { key: key as AfterKey, ms, written: w } }
  }
  if (arg) return { ok: false, problem: `${key} 後面不接參數：「${w}」` }
  return { ok: true, timing: { key, written: w } as Timing }
}

/** The cell for a severity at a timing. manual (/lint) reads as the pre row: it runs before /lint's own work,
 *  and every level means what it does before an act, so a check's level is never refused for running there. */
export function verdictOf(key: TimingKey | 'manual', severity: Severity): Verdict | typeof INVALID {
  return key === 'manual' ? PRE[severity] : TABLE[key][severity]
}

/** A Timing as the person wrote it (`pre:skill:ship`, `after:edit:90s`), for messages and /lint show. */
export const timingText = (t: Timing): string => t.written

// ---------------------------------------------------------------- settling an act

/** A finding's severity as written. A quiet note is info (the card only); a plain note — a `changed` note, the
 *  session record, the paths a delete would touch — is for the model to read, so it is told like warn. */
const severityOf = (f: Finding): Severity => (f.severity === 'note' ? (f.quiet ? 'info' : 'warn') : f.severity)

/**
 * What the findings at one timing come to: `gate` is the strongest gate among them (hold > hold-once >
 * pass); each finding lands in the list of its cell's tell, and every one is on the card. A cell that is
 * INVALID cannot be reached by a check (readCheck refused it) — a finding the mod made itself that still lands
 * there (an ast-grep error at post:file, its own retry at a stop) reads as `line`, never throws.
 */
export type Settled = {
  readonly gate: Verdict['gate']
  readonly fix: readonly Finding[]
  readonly redo: readonly Finding[]
  readonly line: readonly Finding[]
  readonly card: readonly Finding[]
}

const RANK: Record<Verdict['gate'], number> = { pass: 0, 'hold-once': 1, hold: 2 }

export function settle(key: TimingKey | 'manual', findings: readonly Finding[]): Settled {
  let gate: Verdict['gate'] = 'pass'
  const out = { fix: [] as Finding[], redo: [] as Finding[], line: [] as Finding[], card: [] as Finding[] }
  for (const f of findings) {
    const cell = verdictOf(key, severityOf(f))
    const c = cell === INVALID ? v('pass', 'line') : cell
    if (RANK[c.gate] > RANK[gate]) gate = c.gate
    if (c.tell !== 'card') out[c.tell].push(f)
    out.card.push(f)
  }
  return { gate, ...out }
}
