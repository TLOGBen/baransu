// The engine's ports. portIn is what a host calls; portOut is what the engine needs from outside. Every
// outbound port takes the host handle `H` as its first argument and the engine never looks inside it: in
// Claude Code `H` is the dispatch's `$`, in a test it is whatever the fakes want. That is what lets one engine
// live at module scope (so its memory is shared by every dispatch of this module load) while each port call
// still reaches the right dispatch.

import type {
  Config, DoneSkillEvent, LintState, Outcome, PromptEvent, RawCheck, ReplyEvent, SkillPreface,
  SpokenEvent, SystemNote, ToolCallEvent, ToolVerdict, TurnEndEvent, TurnStartEvent, Card, Actor,
} from './types'

// ================================================================ portOut

/** The project's checks and settings. Hides: where they live, which format, caching, the project root. */
export interface ConfigSource<H> {
  /** null: this project has no lint (no `.claude/lint/`); the engine idles and hands every call on.
   *  May cache; must not throw (an unreadable file is a `problems` entry, not an error). */
  load(h: H): Promise<Config | null>
  /** A file at this root-relative path was just edited. The source drops its cache when the file is its own
   *  (under .claude/lint, or the checks folder / sgconfig lint.json named) and says so: true → read it again. */
  edited(h: H, file: string): boolean
}

export type RunResult = { exitCode: number; stdout: string; stderr: string }
export type PathProbe =
  | { kind: 'missing' }
  | { kind: 'file' }
  | { kind: 'dir'; entries: number }
  | { kind: 'unreadable' }

/** The outside world the checks look at: commands (git, ast-grep, a check's own `run`) and paths. */
export interface Runner<H> {
  /** Never throws: a command that cannot start is `exitCode: -1` with `無法執行：<reason>` in stderr. */
  run(h: H, argv: readonly string[], opts: { cwd: string; timeoutMs?: number }): Promise<RunResult>
  /** What is at an absolute path, for the delete preview. Never throws. */
  probe(h: H, path: string): Promise<PathProbe>
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
 * A notice row the person sees in the session, not tied to one call's card. Earns its place because its
 * order against the host's own step is behaviour: the correction notice lands before the user's prompt row,
 * the worktree list at session start, the record before /ship's text. Never throws.
 */
export interface Notify<H> {
  notice(h: H, text: string): Promise<void>
}

/** Reads one check file's text into raw fields. Throws with a short message the person reads. */
export interface RuleConverter {
  /** The name `lint.json`'s `converter` field selects. */
  readonly name: string
  /** The file ending of a check file, dot included (`.toml`); the id is the file name without it. */
  readonly extension: string
  parse(source: string): RawCheck
}

export type Ports<H> = {
  readonly config: ConfigSource<H>
  readonly runner: Runner<H>
  readonly state: StateStore<H>
  readonly notify: Notify<H>
  /** Where the what-now skill file is, for report-before-stop's default redo text. */
  readonly whatNowSkill: (h: H) => string
}

// ---------------------------------------------------------------- scope types (sketch: not wired into Ports yet)
// Wiring adds `machine: Machine<H>` and `languages: readonly Language[]` to Ports (.claude/draft/lint-scope.md).

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
  /** One grepped line → its facts. */
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
  systemNotes(): SystemNote[]

  /** TAKES. Runs `proceed` with the notes the prompt should carry; gives back what it took if `proceed`
   *  throws or `dropped(result)` says the prompt never entered. */
  promptSubmit<R>(e: PromptEvent, proceed: (notes: readonly string[]) => Promise<R>, dropped: (r: R) => boolean): Promise<R>

  turnStarted(e: TurnStartEvent): void
  turnCompleted(e: TurnEndEvent): Promise<void>
  /** /clear: what was owed belongs to the old conversation. */
  cleared(): void

  stepBegan(actor: Actor): void
  textStreamed(e: SpokenEvent): void
  replyAppended(e: ReplyEvent): void

  /** TAKES. Gates the call, runs `proceed` unless denied, then runs the after-moment. Gives back what it took
   *  when the call is denied further down, errors, or anything throws. */
  toolCall<R>(e: ToolCallEvent, proceed: () => Promise<R>, outcome: (r: R) => Outcome): Promise<ToolVerdict<R>>

  skillPrompt(e: DoneSkillEvent): Promise<SkillPreface>
  cardFor(callId: string): Card | undefined
}
