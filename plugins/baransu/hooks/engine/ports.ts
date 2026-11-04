// The engine's ports. portIn is what a host calls; portOut is what the engine needs from outside. Every
// outbound port takes the host handle `H` as its first argument and the engine never looks inside it: in
// Claude Code `H` is the dispatch's `$`, in a test it is whatever the fakes want. That is what lets one engine
// live at module scope (so its memory is shared by every dispatch of this module load) while each port call
// still reaches the right dispatch.

import type {
  Config, DoneSkillEvent, LintState, Outcome, PromptEvent, RawCheck, ReplyEvent, SkillPreface,
  SpokenEvent, SystemNote, ToolCallEvent, ToolVerdict, TurnEndEvent, TurnStartEvent, Card, Actor,
  AgentStartEvent, AgentStopEvent, CompactEvent, FileChangedEvent, StopEvent, StopVerdict,
} from './types'

// ================================================================ portOut

/** The project's checks and settings. Hides: where they live, which format, caching, the project root. */
export interface ConfigSource<H> {
  /** null: this project has no lint (no `.claude/lint/`); the engine idles and hands every call on.
   *  May cache; must not throw (an unreadable file is a `problems` entry, not an error). */
  load(h: H): Promise<Config | null>
  /** A file at this root-relative path was just edited. The source drops its cache when the file is its own
   *  (a rule file under .claude/lint) and says so: true → read it again. */
  edited(h: H, file: string): boolean
  /** Forget what was read: the next load reads the folder again. Called when /lint starts, the one place the
   *  rules are changed. */
  reload(): void
}

export type RunResult = { exitCode: number; stdout: string; stderr: string }
export type PathProbe =
  | { kind: 'missing' }
  | { kind: 'file' }
  | { kind: 'dir'; entries: number }
  | { kind: 'unreadable' }

/** The outside world the checks look at: commands (git, ast-grep, a check's own `run`) and paths. */
export interface Runner<H> {
  /** Never throws: a command that cannot start is `exitCode: -1` with `無法執行：<reason>` in stderr. `env`
   *  is added to the command's environment (LINT_TEXT, LINT_CHANGED, LINT_BEFORE). */
  run(h: H, argv: readonly string[], opts: { cwd: string; timeoutMs?: number; env?: Readonly<Record<string, string>> }): Promise<RunResult>
  /** What is at an absolute path, for the delete preview. Never throws. */
  probe(h: H, path: string): Promise<PathProbe>
  /** A file's text (around:edit's before and after); null when it does not exist or cannot be read. Never throws. */
  read(h: H, path: string): Promise<string | null>
}

/**
 * Time, and one wait. `after` runs `fn` once after `ms`; a reload of the mod cancels its waits, so the engine
 * keeps every deadline in LintState and arms them again when it loads. `fn` must not throw.
 */
export interface Clock<H> {
  now(h: H): Promise<number>
  after(h: H, ms: number, fn: () => void): void
}

/**
 * Host storage for the cross-event state. The engine holds the working copy in memory; this port is the
 * durable copy a module reload reads back.
 *
 * Invariant, and why `save` returns void: the engine takes owed items out of memory and saves in the same
 * synchronous stretch. A `Promise` here would invite `await store.save(...)` between take and return, and that
 * await is exactly where a second call in flight would see the same items. So `save` is fire-and-forget:
 * the implementation copies `s` synchronously (a later mutation of memory must not reach this write), starts
 * the write in call order, and swallows its failure. That the host applies writes in the order issued is a premise (as today), not a duty of this port.
 */
export interface StateStore<H> {
  /** Read once per engine (per module load). undefined: nothing stored, or the read failed. */
  load(h: H): Promise<LintState | undefined>
  save(h: H, s: Readonly<LintState>): void
}

/**
 * Every timing's result for the person is one Card. With a call (`at`) the engine has kept it and the view asks
 * for that call's row to be drawn again; with none, the view says it as a plain row. Never throws.
 */
export interface View<H> {
  show(h: H, card: Card, at?: string): Promise<void>
}

/** Reads one set file's text into raw fields. Throws with a short message the person reads. */
export interface RuleConverter {
  /** The name config.toml's `[settings] converter` selects. */
  readonly name: string
  parse(source: string): RawCheck
}

export type Ports<H> = {
  readonly config: ConfigSource<H>
  readonly runner: Runner<H>
  readonly state: StateStore<H>
  readonly view: View<H>
  readonly clock: Clock<H>
  /** The host's own setting for the language the person is answered in (Claude Code's `language`), or undefined. */
  readonly languageSetting: (h: H) => Promise<string | undefined>
  /** Where the what-now skill file is, for report-before-stop's default redo text. */
  readonly whatNowSkill: (h: H) => string
  /** For a check's `when` guards. */
  readonly machine: Machine<H>
  /** The languages `scope = "related"` reads imports of (util/languages LANGUAGES on Claude Code). */
  readonly languages: readonly Language[]
}

// ---------------------------------------------------------------- what scopes read (Ports.machine, Ports.languages)

/**
 * What only the host's machine knows, for `when` guards. Hides how the host exposes the platform, the
 * environment and PATH lookup (adapters/claude-code/machine.ts). Each answer is a domain value, never a raw
 * platform string. Never throws: an answer it cannot get is undefined.
 */
export interface Machine<H> {
  os(h: H): Promise<'windows' | 'linux' | 'mac' | undefined>
  /** undefined: not set. */
  env(h: H, name: string): Promise<string | undefined>
  /** Whether a command name resolves on the PATH of the shell the checks run in. */
  onPath(h: H, command: string): Promise<boolean | undefined>
}

/** One fact a source line states. `spec` is the specifier as written; resolution is the language's job. */
export type SourceFact =
  | { readonly kind: 'import'; readonly spec: string }
  /** A namespace (C#), package (Java), or module path (Rust `mod x;`) the file declares. */
  | { readonly kind: 'declare'; readonly name: string }
  /** A name other files can use (exported function, public class), for the mentions relation. */
  | { readonly kind: 'export'; readonly name: string }

/** What resolution may consult: the project's files of this language, and who declares what. */
export type TreeView = {
  readonly files: ReadonlySet<string>
  /** declare name → files declaring it (C# namespace → its files, Java package → its files). */
  readonly declared: ReadonlyMap<string, readonly string[]>
}

/**
 * One language's import syntax, like RuleConverter a pure reader the engine is handed: it sees text, never the
 * outside; the engine runs the git greps. Five adapters in util/languages/ cover six languages (TypeScript and
 * JavaScript share one). Adding a language is one file there and one line in its index.
 */
export interface Language {
  readonly id: string
  /** Lower-case extensions without the dot. Two languages never share one. */
  readonly exts: readonly string[]
  /** A PCRE (git grep -P) matching every line that can carry a SourceFact. Over-matching is fine. */
  readonly lines: string
  /**
   * A statement that may span lines (`use a::{` … `};` in Rust, `from x import (` … `)` in Python): given the
   * grepped line, the closing text that ends it, or null when the line is whole. The relation then greps with
   * `-A <CONTINUE_LINES>` for this language and joins the following lines up to and including the closer before
   * calling read. Absent: every statement is one line (TypeScript reads the `from '…'` line on its own).
   */
  continues?(line: string): string | null
  /** One grepped statement (a line, or lines joined by `continues`) → its facts. */
  read(path: string, line: string): readonly SourceFact[]
  /** A specifier → project files it names; [] for anything outside the project. */
  resolve(spec: string, from: string, tree: TreeView): readonly string[]
  /** A PCRE matching a line in another file that imports `path`, for the edit moment's one-hop search.
   *  null: not findable by name. */
  importerPattern(path: string, ownFacts: readonly SourceFact[]): string | null
}

// ================================================================ portIn

/** The engine as a module holds it: one per module load. */
export interface Engine<H> {
  /**
   * The engine with its state loaded, bound to this dispatch's host handle. The first call loads from
   * StateStore; every later call (and every concurrent one) waits on that same load, then resolves at once.
   * This is the only way to reach the methods that take owed items, so none of them can run on unloaded
   * memory — the type, not a comment, keeps "restore before take".
   */
  ready(h: H): Promise<Lint<H>>
}

/**
 * One dispatch's view of the engine. Methods return values; the only side effects are the engine's own
 * memory (saved through StateStore) and the outbound ports.
 *
 * Methods marked TAKES remove owed items (restates, an owed report, a preview approval) from memory and save,
 * synchronously, before their first await. They are plain functions that return a promise — not `async` —
 * so the take is visibly outside the async part. Two calls started back to back see disjoint owed items.
 */
export interface Lint<H> {
  sessionStarted(): Promise<void>
  /** What the system prompt carries: the repo's git habits, the user's language, and each `remind` check. */
  systemNotes(): Promise<SystemNote[]>
  /** The folders FileChanged should watch (the lint root), or none when no check reads post:file. */
  watchPaths(): Promise<readonly string[]>

  /** TAKES. Runs `proceed` with the notes the prompt should carry; gives back what it took if `proceed`
   *  throws or `dropped(result)` says the prompt never entered. */
  promptSubmit<R>(e: PromptEvent, proceed: (notes: readonly string[]) => Promise<R>, dropped: (r: R) => boolean): Promise<R>

  turnStarted(e: TurnStartEvent): void
  turnCompleted(e: TurnEndEvent): Promise<void>
  /** /clear: what was owed belongs to the old conversation. */
  cleared(): void

  stepBegan(actor: Actor): void
  textStreamed(e: SpokenEvent): void
  /** Synchronous part first (speech, slips, the 重新 answered, saved); then the redo checks on that answer. */
  replyAppended(e: ReplyEvent): Promise<void>

  /** TAKES. Gates the call, runs `proceed` unless denied, then runs the after-moment. Gives back what it took
   *  when the call is denied further down, errors, or anything throws. */
  toolCall<R>(e: ToolCallEvent, proceed: () => Promise<R>, outcome: (r: R) => Outcome): Promise<ToolVerdict<R>>

  skillPrompt(e: DoneSkillEvent): Promise<SkillPreface>
  /** A Skill call loading the skill `name` starts (callId) or ends (undefined), so its card hangs under that call. */
  skillCalling(name: string, callId: string | undefined): void
  cardFor(callId: string): Card | undefined
  /** The cards of the subagents an Agent or Workflow call started, one per subagent, in the order they ended. */
  agentCardsUnder(callId: string): readonly Card[]

  /** The main loop wants to end its turn: pre:stop. A hold re-prompts the model in the same turn. */
  stopping(e: StopEvent): Promise<StopVerdict>
  /** A subagent started: an around:agent snapshot, kept by its id. */
  agentStarted(e: AgentStartEvent): Promise<void>
  /** A subagent ended: post:agent and around:agent; lines for the model are queued. TAKES its snapshot. */
  agentStopped(e: AgentStopEvent): Promise<void>
  /** A compaction: pre:compact before `proceed`, post:compact after it with the summary `summary(r)` reads.
   *  TAKES what is owed and writes it into the instructions; gives it back when `skipped(r)`. */
  compacting<R>(e: CompactEvent, proceed: (instructions: string) => Promise<R>, skipped: (r: R) => boolean, summary: (r: R) => string): Promise<R>
  /** A file changed: post:file for a file Claude did not write this turn. */
  fileChanged(e: FileChangedEvent): Promise<void>
}
