// Seam 2: how files relate. A Relation expands a seed set (the change) into its relatives. Two adapters:
// `imports`, built on the Language adapters (util/languages/, one per language), and `mentions`, which reads
// document text. Every outside look is a `git grep` / `git ls-files` through the Runner — never a file read
// per file.

import type { Look } from '../moments'
import type { Language, SourceFact, TreeView } from '../ports'
import type { RelationKind } from './types'

export interface Relation<H> {
  readonly kind: RelationKind
  /**
   * Seeds plus every file reached within `depth` hops, upstream and downstream each walked on its own
   * (an import of an import is related; an importer of an import is a sibling, not related).
   * `hop`: each returned path's distance (0 for a seed), so targets() can keep the nearest when it must cut.
   * `oneHop`: the edit moment's cheap form — no index for TS, Python and Rust (three git processes); C# and
   * Java build the index (two), since their imports name namespaces only the whole tree can resolve.
   */
  expand(look: Look<H>, seeds: readonly string[], depth: number, mode: 'full' | 'oneHop'): Promise<ReadonlyMap<string, number>>
}

export type Relations<H> = Readonly<Record<RelationKind, Relation<H>>>

// ---------------------------------------------------------------- the import index

/**
 * The project's import graph for one language, built from one `git grep -nIPz -e <language.lines> -- <its
 * exts>` over the tree plus the tree's file list — two git processes per language, whatever the size.
 * forward: file → files it imports (resolved, inside the project); reverse: the transpose.
 * A specifier that resolves to nothing (a package, a std module, an alias we cannot read) is dropped: the
 * graph is the project's own files only.
 */
export type ImportIndex = {
  readonly language: string
  readonly forward: ReadonlyMap<string, readonly string[]>
  readonly reverse: ReadonlyMap<string, readonly string[]>
  /** What each file declares (namespace, package, module path) and exports, for `mentions` and resolution. */
  readonly facts: ReadonlyMap<string, readonly SourceFact[]>
}

/** How far a multi-line statement is followed (Language.continues). */
export const CONTINUE_LINES = 40

/**
 * Indexes built within one moment and shared by its checks. No index outlives the moment: no fingerprint of
 * the tree can tell that a file already modified gained an import (its status line stays ` M`), and a plain
 * folder has no fingerprint at all, so a cross-moment cache would hand out a stale graph. The cost is two git
 * processes per language per moment that asks for `related` at depth > 1 (commit, done, manual).
 * Owner: the lens of the moment; it dies with the moment.
 */
export interface GraphCache {
  get(language: string): Promise<ImportIndex> | undefined
  put(language: string, index: Promise<ImportIndex>): void
}

/** A per-moment cache: the lens makes one in openLens; the Promise is stored so two checks share one build. */
export function graphCache(): GraphCache {
  const m = new Map<string, Promise<ImportIndex>>()
  return {
    get: language => m.get(language),
    put(language, index) {
      m.set(language, index)
      // A failed build is not kept, so the next check of the moment tries again.
      index.catch(() => m.delete(language))
    },
  }
}

/** The language a path belongs to, by extension (lower-cased). */
export function languageOf(path: string, languages: readonly Language[]): Language | undefined {
  const base = path.slice(path.lastIndexOf('/') + 1)
  const ext = base.includes('.') ? base.slice(base.lastIndexOf('.') + 1).toLowerCase() : ''
  return languages.find(l => l.exts.includes(ext))
}

// ---- git, through the look's runner; root-relative paths ----

const BATCH = 200 // paths per git command (Windows command-line length; lint-scope postcondition 3)
const scopeFlags = <H>(look: Look<H>) => (look.config.git ? ['--untracked'] : ['--no-index', '--exclude-standard'])
const specsOf = (L: Language) => L.exts.map(e => `:(glob,icase)**/*.${e}`)
const run = <H>(look: Look<H>, argv: readonly string[]) => look.runner.run(look.h, argv, { cwd: look.config.root, timeoutMs: 120000 })
const fwd = (p: string) => p.replace(/\\/g, '/')

/** The project's files of one language. */
async function treeFiles<H>(look: Look<H>, L: Language): Promise<string[]> {
  const r = look.config.git
    ? await run(look, ['git', 'ls-files', '-co', '--exclude-standard', '-z', '--', ...specsOf(L)])
    : await run(look, ['git', 'grep', '-lIz', ...scopeFlags(look), '-e', '', '--', ...specsOf(L)])
  if (r.exitCode !== 0 && r.exitCode !== 1) return []
  return String(r.stdout).split(/\0|\r?\n/).filter(Boolean).map(fwd)
}

/**
 * Every statement of one language in `paths` (or the whole tree), read into facts. With `-z` both matching and
 * context lines are `path\0line\0text`; a statement that continues (Language.continues) takes the following
 * lines of the same file up to the closer, and lines it took are not read again.
 */
async function grepFacts<H>(look: Look<H>, L: Language, paths?: readonly string[]): Promise<Map<string, SourceFact[]>> {
  const out = new Map<string, SourceFact[]>()
  const ctx = L.continues ? ['-A', String(CONTINUE_LINES)] : []
  const batches = paths ? chunk(paths, BATCH) : [specsOf(L)]
  let lineRe: RegExp | undefined
  try {
    lineRe = new RegExp(L.lines)
  } catch {
    lineRe = undefined
  }
  for (const batch of batches) {
    if (!batch.length) continue
    const r = await run(look, ['git', 'grep', '-nIPz', ...ctx, ...scopeFlags(look), '-e', L.lines, '--', ...batch])
    if (r.exitCode !== 0) continue
    const rows = String(r.stdout)
      .split(/\r?\n/)
      .map(l => l.split('\0'))
      .filter(p => p.length >= 3)
      .map(([path, n, ...rest]) => ({ path: fwd(path), n: Number(n), text: rest.join('\0') }))
    const taken = new Set<string>()
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i]
      const key = `${row.path}:${row.n}`
      if (taken.has(key)) continue
      if (lineRe && !lineRe.test(row.text)) continue
      let stmt = row.text
      const closer = L.continues?.(row.text)
      if (closer) {
        for (let j = i + 1; j < rows.length && rows[j].path === row.path && rows[j].n === rows[j - 1].n + 1; j++) {
          stmt += '\n' + rows[j].text
          taken.add(`${rows[j].path}:${rows[j].n}`)
          if (rows[j].text.includes(closer)) break
        }
      }
      const facts = L.read(row.path, stmt)
      if (facts.length) out.set(row.path, [...(out.get(row.path) ?? []), ...facts])
    }
  }
  return out
}

function chunk<T>(xs: readonly T[], n: number): T[][] {
  const out: T[][] = []
  for (let i = 0; i < xs.length; i += n) out.push(xs.slice(i, i + n))
  return out
}

function treeView(files: readonly string[], facts: ReadonlyMap<string, readonly SourceFact[]>): TreeView {
  const declared = new Map<string, string[]>()
  for (const [f, fs] of facts) for (const x of fs) if (x.kind === 'declare') declared.set(x.name, [...(declared.get(x.name) ?? []), f])
  return { files: new Set(files), declared }
}

/** The whole language's graph: the file list and one grep. */
async function build<H>(look: Look<H>, L: Language): Promise<ImportIndex> {
  const files = await treeFiles(look, L)
  const facts = await grepFacts(look, L)
  const tree = treeView(files, facts)
  const forward = new Map<string, string[]>()
  const reverse = new Map<string, string[]>()
  for (const [f, fs] of facts) {
    const to = new Set<string>()
    for (const x of fs) if (x.kind === 'import') for (const t of L.resolve(x.spec, f, tree)) if (t !== f) to.add(t)
    if (!to.size) continue
    forward.set(f, [...to])
    for (const t of to) reverse.set(t, [...(reverse.get(t) ?? []), f])
  }
  return { language: L.id, forward, reverse, facts }
}

/** Each direction walked on its own, up to depth; the smallest hop seen wins. */
function walk(seeds: readonly string[], depth: number, edges: ReadonlyMap<string, readonly string[]>, into: Map<string, number>) {
  let frontier = [...seeds]
  const seen = new Set(seeds)
  for (let hop = 1; hop <= depth && frontier.length; hop++) {
    const next: string[] = []
    for (const f of frontier)
      for (const t of edges.get(f) ?? []) {
        if (seen.has(t)) continue
        seen.add(t)
        next.push(t)
        into.set(t, Math.min(hop, into.get(t) ?? Infinity))
      }
    frontier = next
  }
}

/**
 * Pseudocode, per language L whose exts appear among the seeds (no seed of L → L is never indexed):
 *   idx ← cache.get(L) ?? put(L, build(L))
 *   build(L):
 *     tree  ← git ls-files -co --exclude-standard -z -- <L.exts pathspecs>   (plain folder: git grep -lIz --no-index)
 *     hits  ← git grep -nIPz <scope flags> [-A CONTINUE_LINES when L.continues] -e L.lines -- <L.exts pathspecs>
 *     stmts ← per hit: the line, or, when L.continues(line) gives a closer, the line joined with the following
 *             context lines up to the one holding the closer (at most CONTINUE_LINES; not found → the lines read)
 *     facts ← per statement: L.read(path, stmt)
 *     edges ← per import fact: L.resolve(spec, path, { files: tree, declared: from facts })
 *   up   ← BFS over forward from seeds, ≤ depth
 *   down ← BFS over reverse from seeds, ≤ depth
 *   return seeds(0) ∪ up ∪ down with the smallest hop seen
 * oneHop (edit), TS / Python / Rust: no index. tree ← the file list; candidates ← `git grep -lIz` of the
 *   seeds' importer patterns; facts ← one grep over seeds + candidates; forward ← the seeds' imports resolved;
 *   reverse ← candidates whose imports resolve to a seed. Three git processes. C# and Java: the full index
 *   (two), since a namespace import resolves only against every file's declarations.
 * Stops halfway: nothing written; a failed build is not kept, so the next check of the moment tries again.
 */
export function importsRelation<H>(languages: readonly Language[], cache: GraphCache): Relation<H> {
  return {
    kind: 'imports',
    async expand(look, seeds, depth, mode) {
      const out = new Map<string, number>(seeds.map(s => [s, 0]))
      for (const L of languages) {
        const own = seeds.filter(s => languageOf(s, [L]))
        if (!own.length) continue
        const indexed = mode === 'full' || L.id === 'csharp' || L.id === 'java'
        if (indexed) {
          let idx = cache.get(L.id)
          if (!idx) {
            idx = build(look, L)
            cache.put(L.id, idx)
          }
          const g = await idx
          const d = mode === 'oneHop' ? 1 : depth
          walk(own, d, g.forward, out)
          walk(own, d, g.reverse, out)
          continue
        }
        const files = await treeFiles(look, L)
        const seedFacts = await grepFacts(look, L, own)
        const patterns = own.map(s => L.importerPattern(s, seedFacts.get(s) ?? [])).filter((p): p is string => !!p)
        let candidates: string[] = []
        if (patterns.length) {
          const r = await run(look, ['git', 'grep', '-lIzP', ...scopeFlags(look), ...patterns.flatMap(p => ['-e', p]), '--', ...specsOf(L)])
          if (r.exitCode === 0) candidates = String(r.stdout).split(/\0|\r?\n/).filter(Boolean).map(fwd).filter(c => !own.includes(c))
        }
        const facts = candidates.length ? new Map([...seedFacts, ...(await grepFacts(look, L, candidates))]) : seedFacts
        const tree = treeView(files, facts)
        const resolved = (f: string) => (facts.get(f) ?? []).flatMap(x => (x.kind === 'import' ? L.resolve(x.spec, f, tree) : []))
        for (const s of own) for (const t of resolved(s)) if (!out.has(t)) out.set(t, 1)
        for (const c of candidates) if (resolved(c).some(t => own.includes(t)) && !out.has(c)) out.set(c, 1)
      }
      return out
    },
  }
}

/**
 * Files that mention the seeds: their base names without extension (≥ 4 letters, so `a.ts` does not match
 * every "a") and the names the seeds export (Language facts of kind 'export', from the moment's index when
 * one was built, else one grep of the seeds). One `git grep -lIzF -e n1 -e n2 …`; names beyond 200 are cut.
 * depth beyond 1 is ignored — a doc that mentions a doc is not a relative of the code (design: trade-offs).
 */
export function mentionsRelation<H>(languages: readonly Language[], cache: GraphCache): Relation<H> {
  return {
    kind: 'mentions',
    async expand(look, seeds) {
      const out = new Map<string, number>(seeds.map(s => [s, 0]))
      const names = new Set<string>()
      for (const s of seeds) {
        const base = s.slice(s.lastIndexOf('/') + 1)
        const stem = base.includes('.') ? base.slice(0, base.lastIndexOf('.')) : base
        if (stem.length >= 4) names.add(stem)
      }
      for (const L of languages) {
        const own = seeds.filter(s => languageOf(s, [L]))
        if (!own.length) continue
        const idx = cache.get(L.id)
        const facts = idx ? (await idx).facts : await grepFacts(look, L, own)
        for (const s of own) for (const x of facts.get(s) ?? []) if (x.kind === 'export' && x.name.length >= 4) names.add(x.name)
      }
      const list = [...names].slice(0, 200)
      if (!list.length) return out
      const r = await run(look, ['git', 'grep', '-lIzF', ...scopeFlags(look), ...list.flatMap(n => ['-e', n]), '--', '.'])
      if (r.exitCode !== 0) return out
      for (const f of String(r.stdout).split(/\0|\r?\n/).filter(Boolean).map(fwd)) if (!out.has(f)) out.set(f, 1)
      return out
    },
  }
}

/** The two relations over one moment's cache. */
export function relationsFor<H>(languages: readonly Language[]): (graphs: GraphCache) => Relations<H> {
  return graphs => ({ imports: importsRelation<H>(languages, graphs), mentions: mentionsRelation<H>(languages, graphs) })
}
