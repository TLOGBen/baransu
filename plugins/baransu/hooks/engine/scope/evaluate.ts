// Scope × facts → what a check acts on. The policy of scopes lives here and only here; the facts come from a
// Lens (lens.ts), which is the only part that asks the outside. Everything below that takes no Lens is pure.

import { namesSkill } from '../check'
import { globRe } from './glob'
import type { Check } from '../types'
import type { Lens } from './lens'
import { FACTS } from './lens'
import { TIMING_OF, toRegExp } from './parse'
import type { TimingKey } from '../timing'
import { fixedFiles } from './lens'
import type { ActionKind, Gate, Matcher, Occurrence, PathFilter, Scope, Subject, Targets } from './types'
import { MAX_TARGETS } from './types'

// ---------------------------------------------------------------- does it run at all

/** The actions an occurrence is. Pure. pre:bash with `deletes` → delete; with `worktrees` → worktree-remove. */
export function actionsOf(at: Occurrence): readonly ActionKind[] {
  if (at.key !== 'pre:bash') return []
  return [
    ...(at.deletes && at.deletes.length ? (['delete'] as const) : []),
    ...(at.worktrees && at.worktrees.length ? (['worktree-remove'] as const) : []),
  ]
}

/** The timings an occurrence is: its key, and for a git command that commits and pushes both (before or after;
 *  around has only commit — a push moves no HEAD). Pure. */
export function keysOf(at: Occurrence): readonly (TimingKey | 'manual')[] {
  if (at.key === 'pre:commit' && at.push) return ['pre:commit', 'pre:push']
  if (at.key === 'post:commit' && at.push) return ['post:commit', 'post:push']
  return [at.key]
}

/** Timings whose subject is not a file's content (subjectOf): a command line or its output, a commit's message
 *  or subjects, changed paths, a stop's, a subagent's or a compaction's words, an answer. A check that names only
 *  these has nothing to search at /lint. pre:edit and around:edit read what goes into a file — the same rule
 *  holds over the files /lint searches — so they are not here. */
const TEXT_ONLY: ReadonlySet<string> = new Set([
  'pre:bash', 'post:bash', 'around:bash', 'post:commit', 'post:push', 'around:commit', 'pre:stop', 'post:agent', 'around:agent',
  'pre:compact', 'post:compact', 'post:retry',
])

/** The timings a check is due at: its `on`, else what its actions imply. */
function dueKeys(c: Check): readonly (TimingKey | 'manual')[] {
  if (c.on.length) return c.on.map(t => t.key)
  return [...new Set(c.scope.actions.map(a => TIMING_OF[a]))]
}

/**
 * Whether a check is due at this occurrence, from its `on` and its actions. Pure.
 *   builtin      → its own timing decides (BUILTIN_AT, in the engine and moments.ts), true here
 *   manual       → every check with a timing on files (not only text: TEXT_ONLY), no actions — no act happened
 *   pre:skill    → the checks naming that skill (namesSkill), no actions
 *   otherwise    → its due timings meet keysOf(at); then, when it names actions, actionsOf(at) meets them
 */
export function runsAt(c: Check, at: Occurrence): boolean {
  if (c.action.kind === 'builtin') return true
  const acts = c.scope.actions
  if (at.key === 'manual') return acts.length === 0 && c.on.some(t => t.key === 'manual' || !TEXT_ONLY.has(t.key))
  if (at.key === 'pre:skill') return acts.length === 0 && namesSkill(c, at.skill)
  const due = dueKeys(c)
  const keys = keysOf(at)
  if (!due.some(k => keys.includes(k))) return false
  if (acts.length === 0) return true
  const is = actionsOf(at)
  return acts.some(a => is.includes(a))
}

/**
 * The `when` guards, every one through lens.fact (memoised per moment, so ten checks guarded by `tool:tlc`
 * ask once). All must hold. Short-circuits on the first that fails, in written order, so a cheap guard written
 * first (`git`) spares a costly one (`tool:x`).
 * A fact that cannot be read (lens.fact → undefined) fails its guard with a note — `tool:tlc` missing says
 * 「沒有 tlc，這條沒檢查」 — while a fact that reads false (`branch:main` on dev) fails silently.
 */
export async function admitted(scope: Scope, lens: Lens): Promise<Gate> {
  for (const g of scope.when) {
    const v = await lens.fact(g.name, g.arg)
    const fact = FACTS[g.name]
    if (v === undefined) return { kind: 'skip', say: fact?.missing?.(g.arg) ?? `讀不到「${g.written}」，這條沒檢查` }
    if ((g.negate ? !v : v) === false) {
      // A required tool that is missing is worth saying; any other condition that does not hold is silent.
      return !g.negate && fact?.missing ? { kind: 'skip', say: fact.missing(g.arg) } : { kind: 'skip' }
    }
  }
  return { kind: 'run' }
}

// ---------------------------------------------------------------- which files

/**
 * Pseudocode:
 *   base all:
 *     at edit                       → paths [the edited file] filtered        (edit never scans the tree)
 *     specs = asPathspecs(where, ignores)
 *     specs ≠ undefined             → { tree, specs }                          (no listing: today's cost)
 *     else                          → paths = filter(await lens.universe())   (one listing per moment, shared)
 *   base diff                       → paths = filter(await lens.changed())
 *   base related, at edit           → paths = filter(await lens.related(via, 1, 'oneHop'))   (decision 2: one hop)
 *   base related                    → paths = filter(await lens.related(via, depth, 'full'))  (commit/done/manual)
 *   paths empty → none; over MAX_TARGETS → first MAX_TARGETS (sorted: changed files first, then by hop
 *   distance, then by path) and `dropped`. MAX_TARGETS is the only cap: runPerFile ({file} checks) takes the
 *   paths as given and no longer applies its own MAX_FILES.
 * Running twice gives the same answer (the lens memoises; ordering is total). Stops halfway: no effect.
 */
export async function targets(scope: Scope, lens: Lens): Promise<Targets> {
  // An act that names its own files never scans the tree; related reaches one hop from them.
  const edit = fixedFiles(lens.at) !== undefined
  let listed: readonly string[]
  const b = scope.base
  if (b.kind === 'all') {
    if (!edit) {
      const specs = asPathspecs(scope.where, scope.ignores)
      if (specs) return { kind: 'tree', specs }
    }
    listed = await lens.universe()
  } else if (b.kind === 'diff') listed = await lens.changed()
  else listed = edit ? await lens.related(b.via, 1, 'oneHop') : await lens.related(b.via, b.depth, 'full')
  const paths = await keep(scope, lens, listed)
  if (!paths.length) return { kind: 'none' }
  return paths.length > MAX_TARGETS
    ? { kind: 'paths', paths: paths.slice(0, MAX_TARGETS), dropped: paths.length - MAX_TARGETS }
    : { kind: 'paths', paths, dropped: 0 }
}

/** The listed paths that pass the filter, in the lens's order; a `.cfg` beside a `.tla` for `@tla`. */
async function keep(scope: Scope, lens: Lens, listed: readonly string[]): Promise<string[]> {
  const out = listed.filter(p => passes(p, scope.where, scope.ignores))
  if (scope.where.trees.includes('@tla')) {
    for (const p of listed) {
      if (!/\.cfg$/i.test(p) || out.includes(p) || isIgnored(p, scope.ignores)) continue
      const tla = p.replace(/\.cfg$/i, '.tla')
      if (listed.includes(tla) || (await lens.exists(tla))) {
        if (passes(tla, scope.where, scope.ignores)) out.push(p)
      }
    }
  }
  return out
}

/** Whether the change touches the check's scope — the old `touched`, for a `changed` note and for `diff`
 *  runs. The diff filtered by where/ignores is non-empty. A plain folder outside a commit has no diff, so
 *  this is false (as today). */
export async function touches(scope: Scope, lens: Lens): Promise<boolean> {
  return (await keep(scope, lens, await lens.changed())).length > 0
}

/**
 * The text a check matches when its target is not a file, or undefined when it is files (targets()). Pure.
 *   pre:bash, actions ∋ delete          → the deleted paths that reach the scope (coversScope: `rm -rf .claude`
 *                                          deletes `.claude/hypothesis/`, so a check on that folder sees it)
 *   pre:bash, actions ∋ worktree-remove → the worktrees removed
 *   pre:bash                            → [the command line]
 *   post:bash                           → [the command line, its output]
 *   pre:edit / around:edit              → what is written / the lines added, when the file is in scope; else
 *                                          no lines (the check is silent for that file)
 *   around:bash / around:agent          → the changed paths in scope
 *   post:commit, post:push              → [the newest commit and the output]
 *   around:commit                       → the new commits' subjects
 *   pre:stop, post:agent, pre/post:compact, post:retry → [the text]
 */
export function subjectOf(scope: Scope, at: Occurrence): Subject | undefined {
  const inScope = (p: string) => passes(p, scope.where, scope.ignores)
  switch (at.key) {
    case 'pre:bash': {
      const lines: string[] = []
      if (scope.actions.includes('delete')) lines.push(...(at.deletes ?? []).filter(p => coversScope(p, scope.where, scope.ignores)))
      if (scope.actions.includes('worktree-remove')) lines.push(...(at.worktrees ?? []))
      return { lines: scope.actions.length ? lines : [at.command] }
    }
    case 'post:bash': return { lines: [at.command, at.output] }
    case 'pre:edit': return { lines: inScope(at.file) ? [at.text] : [] }
    case 'around:edit': return { lines: inScope(at.file) ? at.added : [] }
    case 'around:bash': case 'around:agent': return { lines: at.changed.filter(inScope) }
    case 'post:commit': case 'post:push': return { lines: [at.record] }
    case 'around:commit': return { lines: at.commits }
    case 'pre:stop': case 'post:agent': case 'pre:compact': case 'post:compact': case 'post:retry': return { lines: [at.text] }
    default: return undefined
  }
}

// ---------------------------------------------------------------- path predicates (pure)

const norm = (p: string) => p.replace(/\\/g, '/').replace(/^\.\//, '')
const dirOf = (p: string) => (p.includes('/') ? p.slice(0, p.lastIndexOf('/')) : '')
const extOf = (p: string) => {
  const base = p.slice(p.lastIndexOf('/') + 1)
  return base.includes('.') ? base.slice(base.lastIndexOf('.') + 1).toLowerCase() : ''
}

/** One path matcher. `folder`: prefix on the path, regex on its dirname. `file`: glob, regex on the path. */
function hit(path: string, m: Matcher, as: 'folder' | 'file'): boolean {
  if (m.kind === 'prefix') return (path + (as === 'folder' ? '/' : '')).toLowerCase().startsWith(m.prefix.toLowerCase())
  if (m.kind === 'regex') return toRegExp(m.source).test(as === 'folder' ? dirOf(path) : path)
  const base = path.slice(path.lastIndexOf('/') + 1)
  return globRe(m.glob).test(m.glob.includes('/') ? path : base)
}

function isIgnored(path: string, ignores: readonly Matcher[]): boolean {
  const p = norm(path)
  return ignores.some(m => hit(p, m, m.kind === 'prefix' ? 'folder' : 'file'))
}

/**
 * Whether deleting `path` (a file or a whole folder) removes something the scope names. Pure.
 *   passes(path, where, ignores)                                  → true
 *   path is a folder prefix of a folder Matcher's prefix            → true   (`.claude` above `.claude/hypothesis/`)
 *   where has only file globs / exts / regexes                      → a folder delete reaches them only through
 *                                                                     the deleted entries the preview lists
 *                                                                     (deletedPaths gives those), so false here
 */
export function coversScope(path: string, where: PathFilter, ignores: readonly Matcher[]): boolean {
  const p = norm(path).replace(/\/+$/, '')
  if (passes(p, where, ignores)) return true
  const unscoped = !where.folders.length && !where.files.length && !where.trees.length && !where.exts.length
  if (unscoped) return !isIgnored(p, ignores)
  // The whole root, or a folder that holds a scoped folder.
  return where.folders.some(m => m.kind === 'prefix' && (p === '' || p === '.' || m.prefix.toLowerCase().startsWith(`${p.toLowerCase()}/`)))
}

/** where AND-across-kinds, OR-within, minus ignores. The one place the composition rule is written. */
export function passes(path: string, where: PathFilter, ignores: readonly Matcher[]): boolean {
  const p = norm(path)
  if (where.folders.length && !where.folders.some(m => hit(p, m, 'folder'))) return false
  // `file` and the tree aliases are one kind: `@tla` names every .tla (its .cfg pairs are added by targets()).
  if ((where.files.length || where.trees.length) && !(where.files.some(m => hit(p, m, 'file')) || (where.trees.includes('@tla') && extOf(p) === 'tla')))
    return false
  if (where.exts.length && !where.exts.includes(extOf(p))) return false
  return !isIgnored(p, ignores)
}

/**
 * The filter as git pathspecs, when pathspecs can say it exactly; else undefined.
 * Git ORs include pathspecs, so AND across kinds is not expressible: only a filter with at most one kind set,
 * and no regex in it or in ignores, converts. (`:(exclude,glob)` handles glob/prefix ignores.)
 */
export function asPathspecs(where: PathFilter, ignores: readonly Matcher[]): string[] | undefined {
  if (where.trees.length) return undefined
  const kinds = [where.folders.length, where.files.length, where.exts.length].filter(n => n > 0).length
  if (kinds > 1) return undefined
  if ([...where.folders, ...where.files, ...ignores].some(m => m.kind === 'regex')) return undefined
  const glob = (g: string) => (g.includes('/') ? g : `**/${g}`)
  const spec = (m: Matcher) => (m.kind === 'prefix' ? `${m.prefix}**` : m.kind === 'glob' ? glob(m.glob) : '')
  const inc = where.folders.length
    ? where.folders.map(m => `:(glob,icase)${spec(m)}`)
    : where.files.length
      ? where.files.map(m => `:(glob)${spec(m)}`)
      : where.exts.length
        ? where.exts.map(e => `:(glob,icase)**/*.${e}`)
        : ['.']
  return [...inc, ...ignores.map(m => `:(exclude,glob)${spec(m)}`)]
}
