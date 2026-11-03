// The engine's domain: checks, findings, cards, the cross-event state, and the events and verdicts of its
// inbound port. Nothing here names Claude Code, a file system or a process.
//
// The stored shapes — the cross-event state, a finding, a card — have one owner: the plugin's own contract
// `types/index.d.ts`, which the host requires to import nothing. The engine imports them from there (types
// only, erased at run time) rather than writing a second copy.

import type { LintCard, LintFinding, LintState } from '../../types'

export type { LintState }

// ---------------------------------------------------------------- checks

/** A check that is in force. `off` never reaches the engine: the config source drops an off check, so a
 *  check the user turned off cannot fire anywhere (today: readChecks' last line). */
export type Severity = 'error' | 'warn'
export type Moment = 'edit' | 'commit' | 'done' | 'bash' | 'manual'
export type Builtin =
  | 'git-facts' | 'secret-files' | 'built-before-commit' | 'up-to-date' | 'session-record' | 'worktree-cleanup'
  | 'destructive-preview' | 'explain-before-edit' | 'report-before-stop' | 'correction-to-lint' | 'user-language'

/** What a check does: at most one of forbid, run, builtin (format.md). The union makes "two" unwritable;
 *  `none` is a check that only carries a `changed` note. `builtin` keeps an unknown name as written — it
 *  matches no built-in and does nothing, as today. */
export type CheckAction =
  | { kind: 'forbid'; pattern: string }
  | { kind: 'run'; argv: readonly string[] }
  | { kind: 'builtin'; name: Builtin | (string & {}) }
  | { kind: 'none' }

/** One check as the engine uses it, whatever file format it came from. */
export type Check = {
  readonly id: string
  readonly on: readonly Moment[]
  readonly severity: Severity
  readonly files: readonly string[]
  readonly ignores: readonly string[]
  readonly action: CheckAction
  readonly message: string
  readonly changed?: string
  readonly language?: string
  /** On a 重新 built-in: the instruction that replaces the default. */
  readonly redo?: string
}

/** A check file's fields as a converter read them, before the engine fills defaults. */
export type RawCheck = Readonly<Record<string, string | readonly string[]>>

/** Everything the engine reads about a project. `null` from the config source means: no lint here, idle. */
export type Config = {
  /** The project root, forward slashes: the folder that holds `.claude/lint/`. Paths in events are made
   *  relative to it. */
  readonly root: string
  /** Whether `root` is the top of a git work tree. false: a plain folder, such as a workspace holding several
   *  repos. Checks still run there — `forbid` searches the folder with `git grep --no-index` — and the checks
   *  that only mean something in a repo (git facts, the commit-time git built-ins, worktree cleanup, what the
   *  change touched) are skipped, not reported as failures. */
  readonly git: boolean
  /** The checks in force: no off check is here (see Severity). */
  readonly checks: readonly Check[]
  /** Files that could not be read, shown as warn findings at every moment. */
  readonly problems: readonly Finding[]
  /** ast-grep's config path, relative to root. Whether the file exists is asked when ast-grep is about to run (per moment, as today), not when the config is read. */
  readonly sgconfig?: string
}

// ---------------------------------------------------------------- what the engine says

export type Finding = LintFinding

/** A card drawn under one call. A value only: drawing it is the adapter's job. `replace`: drawn in place of
 *  the call's own error text (a held or refused call). */
export type Card = LintCard

// ---------------------------------------------------------------- cross-event state
// `LintState` (re-exported above) is kept in host storage through the StateStore port, unchanged in shape,
// so a stored value from 8.39 loads as is. Writer of every field: the engine alone.

// ---------------------------------------------------------------- inbound events (portIn)
// `agent` absent = the main loop; present = a subagent's id. The engine, not the adapter, decides what a
// subagent's event may change (R3).

export type Actor = { readonly agent?: string }

export type ToolCallEvent = Actor & {
  /** The call's id; its card is kept under it. */
  readonly id: string
  /** The directory the actor's shell is in now, read inside the hook. Forward slashes, no trailing slash.
   *  '' when the host could not tell: the engine then uses `Config.root` (today: `… || root`), for the delete
   *  preview's paths and its key alike. */
  readonly cwd: string
} & (
  | { readonly kind: 'edit'; readonly file: string }
  | { readonly kind: 'shell'; readonly shell: 'sh' | 'ps'; readonly command: string; readonly background: boolean }
)

/** How the host's own handling of a call ended. `ran` false: refused further down. */
export type Outcome = { readonly ran: boolean; readonly isError: boolean; readonly isReadOnly: boolean }

export type PromptEvent = {
  /** What the person typed, tags and a leading slash command removed. */
  readonly typed: string
  /** True when this message reaches the model now (plain text, or typed into a running turn); false for a
   *  slash command that may open no turn (/cost) — it carries a copy, settled at turnStart. */
  readonly opensTurnNow: boolean
}

export type TurnStartEvent = Actor & { readonly text?: string }
/** `answered`: the turn ended with an answer, not stopped — only then does a /review it ran count. */
export type TurnEndEvent = Actor & { readonly answered: boolean }
/** Text the model streamed (turn.step) — counts as speaking and as text after the last step. */
export type SpokenEvent = Actor & { readonly text: string }
/** A whole assistant row as it is kept (session.append) — counts as speaking and is read for its language. */
export type ReplyEvent = Actor & { readonly text: string }
/** A skill that reads lint's record before its own text: /ship and /review (the done moment), /lint (the manual run). */
export type DoneSkillEvent = { readonly skill: 'ship' | 'review' | 'lint' }

// ---------------------------------------------------------------- verdicts

/** tool.call's answer. A deny's card is already kept in state under the call id. */
export type ToolVerdict<R> =
  | { readonly kind: 'deny'; readonly reason: string }
  | { readonly kind: 'ran'; readonly result: R; readonly notes: readonly string[] }

export type SystemNote = { readonly id: string; readonly text: string }

/** What /ship or /review reads before its own text. null: no lint here. */
export type SkillPreface = { readonly text: string } | null
