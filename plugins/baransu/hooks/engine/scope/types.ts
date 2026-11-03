// A check's scope as data: what the user composed in the check file, parsed once by `scopeFrom` (parse.ts).
// The engine evaluates this data against facts a Lens supplies (lens.ts); nothing here asks the outside.
//
// Composition, the one rule a user learns:
//   1. `base` picks the starting set of files: the whole project, this change, or this change and its relatives.
//   2. `where` narrows it: AND across folder / file / ext, OR within each.
//   3. `ignores` subtracts.
//   4. `actions` narrows which occurrences of a moment the check sees (and what its target is).
//   5. `when` gates the check on the environment it runs in; every guard must hold.
// A field left out constrains nothing. There is no other combination rule.

// ---------------------------------------------------------------- paths

/** One way to match a root-relative, forward-slash path. A `re:` prefix in the check file makes a regex;
 *  anything else is the kind's native form (a prefix for folders, a glob for files). Case-insensitive
 *  regexes are written with `(?i)`, as `bash` forbids are today. */
export type Matcher =
  | { readonly kind: 'prefix'; readonly prefix: string } // folder: "src/billing/" — matched on segment boundaries
  | { readonly kind: 'glob'; readonly glob: string }     // file: today's glob rules (no "/" → the name anywhere)
  | { readonly kind: 'regex'; readonly source: string }  // folder: tested on the dirname; file: on the whole path

/** Narrowing by path. An empty list constrains nothing; a non-empty one must match (OR inside it).
 *  `exts` are lower-case, without the dot, aliases already expanded (`TLA+` → tla). `trees` holds file aliases
 *  only the tree can answer (`@tla`: every .tla, and each .cfg beside a .tla of the same stem); the lens lists
 *  them, and they OR with `files`. */
export type PathFilter = {
  readonly folders: readonly Matcher[]
  readonly files: readonly Matcher[]
  readonly trees: readonly ('@tla')[]
  readonly exts: readonly string[]
}

// ---------------------------------------------------------------- the starting set

/** How a file is related to another. Each kind is one Relation adapter (relations.ts). */
export type RelationKind = 'imports' | 'mentions'

export type Base =
  | { readonly kind: 'all' }
  /** Working tree + staged vs HEAD; at edit, the edited file; at a push, the files the push sends. */
  | { readonly kind: 'diff' }
  /** The diff plus, per relation, files reached from it within `depth` hops in each direction separately
   *  (upstream: what it imports; downstream: what imports it). Never mixes directions within one walk. */
  | { readonly kind: 'related'; readonly via: readonly RelationKind[]; readonly depth: number }

// ---------------------------------------------------------------- non-file targets

/** What a pre:bash command is, beyond running: it deletes or moves paths away, or removes a git worktree.
 *  Each implies pre:bash when `on` is left out (parse.ts: TIMING_OF). A push is the timing `pre:push` and a
 *  redo answer the timing `post:retry`: neither is an action any more. */
export type ActionKind = 'delete' | 'worktree-remove'

/** The 重新 requests lint delivers: restate in the user's language (user-language), say how the change will be
 *  made before editing (explain-before-edit), report before stopping (report-before-stop). */
export type RedoKind = 'restate' | 'explain' | 'report' | 'retry'

/**
 * One 重新 delivered and not yet answered: `LintState.answering` holds these (types/index.d.ts owns the field;
 * design-time hypothesis lint-mod-state R14–R17, .claude/draft/lint-scope.md postcondition 12).
 * Set when the request is delivered, not when it is taken: `take`'s 'prompt' / 'call' modes once the call or
 * prompt carrying it goes on; explain-before-edit when its deny or warn is sent; an offered copy when
 * turnStarted settles `offered`. A give-back removes the same `id`.
 * `step`: `steps.main` at delivery. A main-loop row answers it only when `steps.main > step` (a later response
 * than the one it was delivered in) and the row has visible content; turnCompleted drops only entries with
 * `step < steps.main` (the model read them), so one delivered with a queued prompt waits for the next turn.
 */
export type Answering = { readonly id: number; readonly kinds: readonly RedoKind[]; readonly step: number }

/** A fact about the environment the check runs in. `name` is a key of FACTS (lens.ts); `arg` its argument
 *  (`tool:tlc` → tlc, `env:NODE_ENV=production` → NODE_ENV=production). `negate`: the `!` prefix. */
export type Guard = { readonly name: string; readonly arg?: string; readonly negate: boolean; readonly written: string }

// ---------------------------------------------------------------- the whole scope

export type Scope = {
  readonly base: Base
  readonly where: PathFilter
  readonly ignores: readonly Matcher[]
  /** Empty: every occurrence of the check's moments. */
  readonly actions: readonly ActionKind[]
  readonly when: readonly Guard[]
}

// ---------------------------------------------------------------- what evaluation yields

/**
 * The files a check acts on, in the form the cheapest search can take.
 * - `tree`: the whole universe narrowed by git pathspecs — no listing needed (base all, and a filter that
 *   pathspecs can say exactly: at most one of folder/file/ext set, no regex). This is today's path, and stays
 *   the common one.
 * - `paths`: an explicit list (diff, related, or a filter pathspecs cannot say). Never more than MAX_TARGETS;
 *   `dropped` counts the rest so the finding can say so.
 * - `none`: the scope selects nothing this time — the check is silent (not a pass, not a failure).
 */
export type Targets =
  | { readonly kind: 'tree'; readonly specs: readonly string[] }
  | { readonly kind: 'paths'; readonly paths: readonly string[]; readonly dropped: number }
  | { readonly kind: 'none' }

export const MAX_TARGETS = 500

/** Text a non-file check matches against: the command line, the deleted paths, or the redo reply. */
export type Subject = { readonly lines: readonly string[] }

/** Why `when` stopped a check. `say` set: a note the person sees (a tool the check needs is missing);
 *  unset: a deliberate condition such as `branch:main` that simply does not hold, said nothing. */
export type Gate = { readonly kind: 'run' } | { readonly kind: 'skip'; readonly say?: string }

/** What `scopeFrom` makes of a check's scope fields. A scope it cannot read is never half-applied: the
 *  whole check stays off and the problems say why — a dropped narrowing must not widen a check to the
 *  whole project (grafted from the other candidate; .claude/draft/lint-scope.md). */
export type ScopeRead =
  | { readonly ok: true; readonly scope: Scope }
  | { readonly ok: false; readonly problems: readonly string[] }

// ---------------------------------------------------------------- occurrences (replaces runMoment's loose opts)

/** A push's refspecs as `pushRefs` (shell.ts) reads them. */
export type PushRef = { readonly remote: string; readonly src: string; readonly dst: string }

type Git = {
  readonly command: string
  /** null for a command that only commits; refs null for a push that names no refspec (its upstream decides). */
  readonly push: { readonly refs: readonly PushRef[] | null } | null
}

/**
 * One occurrence of a timing: what happened, carried to the checks. `key` is the timing (timing.ts TABLE);
 * each variant holds exactly what that side of that act can know, so "a file before a stop" is unwritable.
 * A git command that commits and pushes is one occurrence keyed `<side>:commit` with `push` set; it is due for
 * checks on either key (keysOf, evaluate.ts). The action it is (delete, worktree-remove) is read by actionsOf.
 */
export type Occurrence =
  /** `text`: what the call will write (Write's content, Edit's new text), before it is written. */
  | { readonly key: 'pre:edit'; readonly file: string; readonly text: string }
  | { readonly key: 'post:edit'; readonly file: string }
  /** `added`: the lines the write added (forbid matches only these). */
  | { readonly key: 'around:edit'; readonly file: string; readonly added: readonly string[] }
  /** `deletes` / `worktrees`: root-relative paths the command would delete, or worktrees it removes; null: none. */
  | { readonly key: 'pre:bash'; readonly command: string; readonly deletes: readonly string[] | null; readonly worktrees: readonly string[] | null }
  | { readonly key: 'post:bash'; readonly command: string; readonly output: string; readonly failed: boolean }
  /** The paths the command added or changed. */
  | { readonly key: 'around:bash'; readonly command: string; readonly changed: readonly string[] }
  | ({ readonly key: 'pre:commit' | 'pre:push' } & Git)
  /** `record`: the newest commit as `git log -1` prints it (author, message), then the command's output. */
  | ({ readonly key: 'post:commit' | 'post:push'; readonly record: string } & Git)
  /** The commits HEAD gained (subjects) and the files they touch. */
  | ({ readonly key: 'around:commit'; readonly commits: readonly string[]; readonly changed: readonly string[] } & Git)
  | { readonly key: 'pre:skill'; readonly skill: string }
  /** `text`: the turn's last words the person saw. */
  | { readonly key: 'pre:stop'; readonly text: string }
  /** `text`: the subagent's last words, when the host gave them. */
  | { readonly key: 'post:agent'; readonly agentType: string; readonly text: string }
  | { readonly key: 'around:agent'; readonly agentType: string; readonly changed: readonly string[] }
  /** `text`: the compaction's instructions (pre) or the summary it wrote (post). */
  | { readonly key: 'pre:compact' | 'post:compact'; readonly text: string }
  /** Files changed outside Claude since the last look. */
  | { readonly key: 'post:file'; readonly files: readonly string[] }
  | { readonly key: 'post:retry'; readonly redo: readonly RedoKind[]; readonly text: string }
  /** A wait after an act ran out with no such act since. */
  | { readonly key: 'after:edit' | 'after:bash' | 'after:commit' | 'after:push' }
  | { readonly key: 'manual' }

export type OccurrenceAt<K extends Occurrence['key']> = Extract<Occurrence, { key: K }>
