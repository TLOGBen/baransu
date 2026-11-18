// The engine's domain: checks, findings, cards, the cross-event state, and the events and verdicts of its
// inbound port. Nothing here names Claude Code, a file system or a process.
//
// The stored shapes — the cross-event state, a finding, a card — have one owner: the plugin's own contract
// `types/index.d.ts`, which the host requires to import nothing. The engine imports them from there (types
// only, erased at run time) rather than writing a second copy.

import type { LintCard, LintFinding, LintPathRow, LintState } from '../../types'
import type { EditSnap, HeadSnap, Store, TreeSnap } from './around'
import type { RedoKind } from './scope/types'
import type { PreviewLine } from './shell'

export type { LintState }

// ---------------------------------------------------------------- checks

/** A check that is in force. `off` never reaches the engine: the config source drops an off check, so a
 *  check the user turned off cannot fire anywhere (today: readChecks' last line). */
/**
 * A check's level (format.md, 等級). What it does depends on the timing: one cell of timing.ts TABLE per
 * level and timing, and nothing else decides it. `off` never reaches the engine. The mapping to a finding is
 * moments.ts `level`.
 */
export type Severity = 'error' | 'check' | 'retry' | 'warn' | 'info'
/** When a check runs: `<side>:<act>[:<arg>]` or `manual`, parsed (timing.ts). */
export type { Timing } from './timing'
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
  /** When it runs. Empty only for a check whose actions imply the timing, and for a built-in (BUILTIN_AT). */
  readonly on: readonly import('./timing').Timing[]
  readonly severity: Severity
  /** `remind = true`: its message is in the system prompt from the start (prompt.compose), not only after a
   *  slip. Only on a check with no file scope (readCheck refuses it otherwise). */
  readonly remind?: boolean
  /** Which files, acts and environments the check covers (scopeFrom; format.md, 範圍). */
  readonly scope: import('./scope/types').Scope
  readonly action: CheckAction
  readonly message: string
  readonly changed?: string
  readonly language?: string
  /** On a 重新 built-in: the instruction that replaces the default. */
  readonly redo?: string
}

/** A check file's fields as a converter read them, before the engine fills defaults. */
/** A value a converter reads: a string, a list of strings, a table, or a list of tables (`[[extends]]`). */
export type RawValue = string | readonly string[] | RawTable | readonly RawTable[]
/** One table of a check file or a collection; a whole file is one too. */
export type RawTable = { readonly [key: string]: RawValue }
export type RawCheck = RawTable

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
/** One path of the delete preview, drawn as a row of the card's path list. */
export type PathRow = LintPathRow

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
  /** `text`: what the call writes (Write's content, Edit's and MultiEdit's new strings joined). */
  | { readonly kind: 'edit'; readonly file: string; readonly text: string }
  | { readonly kind: 'shell'; readonly shell: 'sh' | 'ps'; readonly command: string; readonly background: boolean }
)

/** How the host's own handling of a call ended. `ran` false: refused further down. `output`: a shell
 *  command's stdout and stderr ('' for an edit or when the host gave none), for post:bash. */
export type Outcome = { readonly ran: boolean; readonly isError: boolean; readonly isReadOnly: boolean; readonly output?: string }

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
export type ReplyEvent = Actor & {
  readonly text: string
  /** What the person sees of the row: its text blocks plus thinking blocks that carry text (the same reading
   *  as streamedText). '' for a row of only a tool_use or an empty thinking — such a row answers no 重新.
   *  The redo checks run on this, not on `text` (lint-scope sketch, postcondition 12). Required once filled. */
  readonly visible: string
}
/** A skill starting. `skill`: /ship and /review read the done moment's record, /lint the manual run; any other
 *  skill ('other') gets a record only from the checks whose `on` names it. `name` is the skill as invoked;
 *  `args` what was typed after it (`/lint help` → 'help'), '' when nothing was. */
export type DoneSkillEvent = { readonly skill: 'ship' | 'review' | 'lint' | 'other'; readonly name: string; readonly args: string }

/** The main loop wants to end its turn (classic.Stop). `text`: last_assistant_message. The host's stop_hook_active
 *  is not read: each check's one hold is the engine's own record (an error's hold must not use up the report's). */
export type StopEvent = { readonly text: string }
/** A subagent starting (agent.spawn, after the host started it: `agent` is its id). */
export type AgentStartEvent = { readonly agent: string; readonly agentType: string; readonly callId?: string }
/** A subagent ended (classic.SubagentStop). `agentType` '' is the host's own compaction. */
export type AgentStopEvent = { readonly agent: string; readonly agentType: string; readonly text: string }
/** A compaction of the main conversation (session.compact; a subagent's own is not one). */
export type CompactEvent = { readonly instructions: string }
/** A file the host saw change (classic.FileChanged), absolute or root-relative. */
export type FileChangedEvent = { readonly file: string; readonly change: 'change' | 'add' | 'unlink' }

/** A stop's answer: go on ending, or `hold` with the reason the model reads in the same turn. */
export type StopVerdict = { readonly kind: 'stop' } | { readonly kind: 'hold'; readonly reason: string }

// ---------------------------------------------------------------- verdicts

/**
 * What the half of a call before the act leaves for the half after it: plain data (JSON), so a host that runs
 * the two halves in separate processes (Codex's PreToolUse and PostToolUse) keeps it on disk between them.
 * `slips`/`queued`: what the call took, given back when the act did not run. `noConfig`: no lint here.
 */
export type PendingCall = {
  readonly e: ToolCallEvent
  readonly slips: readonly string[]
  readonly queued: readonly string[]
  readonly at: { readonly editSeq: number; readonly step: number }
  readonly context: string[]
  readonly inline: Finding[]
  readonly redo: RedoKind[]
  readonly gitWrite: boolean
  readonly file: string
  readonly editSnap?: EditSnap
  readonly treeSnap?: TreeSnap
  readonly headSnap?: HeadSnap
  readonly store?: Store
  readonly touchedFile?: string
  readonly preview: readonly PreviewLine[]
  readonly noConfig?: boolean
}

/** What a compaction's before half leaves for its after half: plain data, like PendingCall. `slips`/`queued`:
 *  what it took, given back when the compaction does not happen. `carry`: the lines the summary must keep, ''
 *  when nothing was owed (then it holds nothing to give back). */
export type PendingCompact = { readonly slips: readonly string[]; readonly queued: readonly string[]; readonly carry: string }

/** The before half's answer: refuse, or go on with the record the after half reads. */
export type CallStart = { readonly kind: 'deny'; readonly reason: string } | { readonly kind: 'go'; readonly pending: PendingCall }

/** tool.call's answer. A deny's card is already kept in state under the call id. */
export type ToolVerdict<R> =
  | { readonly kind: 'deny'; readonly reason: string }
  | { readonly kind: 'ran'; readonly result: R; readonly notes: readonly string[] }

export type SystemNote = { readonly id: string; readonly text: string }

/** What /ship or /review reads before its own text. null: no lint here. */
export type SkillPreface = { readonly text: string } | null
