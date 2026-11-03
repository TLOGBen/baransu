// One moment's facts. A Lens is opened per runMoment call and lives only as a local of that call: it asks the
// outside lazily, at most once per question, and every check of the moment shares the answer. It holds no
// cross-event state, so it never touches LintState and a reload loses nothing.
//
// Three things vary behind it, each behind its own seam:
//   ChangeSource — what "this change" is: a repo's status, a plain folder (none), a push's range.
//   Relation     — how files relate: imports (one Language adapter per language) or mentions (relations.ts).
//   FACTS        — environment facts, each one entry reading the Machine port, git, or the config.

import type { Look } from '../moments'
import type { Machine } from '../ports'
import type { GraphCache, Relations } from './relations'
import { graphCache } from './relations'
import { toRegExp } from './parse'
import type { Occurrence, PushRef, RelationKind } from './types'

/** The files an act names itself, or undefined when "this change" is the repo's. An edit at any side is its
 *  file; post:file the files changed outside; around:bash / around:agent / around:commit what changed. Pure. */
export function fixedFiles(at: Occurrence): readonly string[] | undefined {
  switch (at.key) {
    case 'pre:edit': case 'post:edit': case 'around:edit': return [at.file]
    case 'post:file': return at.files
    case 'around:bash': case 'around:agent': case 'around:commit': return at.changed
    default: return undefined
  }
}

export interface Lens {
  readonly at: Occurrence
  /** Every file the checks may search, root-relative. Listed at most once per moment, only when a scope needs
   *  a list over the whole tree (a filter pathspecs cannot say). For an act with its own files: those (fixedFiles). */
  universe(): Promise<readonly string[]>
  /** This change (the ChangeSource for this occurrence). Memoised. */
  changed(): Promise<readonly string[]>
  /** changed() plus relatives, per relation, within depth. Memoised per (via, depth, mode). `mode` is chosen
   *  by targets() (evaluate.ts): 'oneHop' at edit, 'full' elsewhere. */
  related(via: readonly RelationKind[], depth: number, mode: 'full' | 'oneHop'): Promise<readonly string[]>
  /** One environment fact. undefined: could not be read (the guard fails with a note). Memoised per written guard. */
  fact(name: string, arg: string | undefined): Promise<boolean | undefined>
  /** Whether a root-relative path exists (for `@tla`'s .tla beside a .cfg). Memoised. */
  exists(path: string): Promise<boolean>
}

// ================================================================ seam 1: the change set

/**
 * What "this change" is. Hides: git status parsing, the commit repo's path rewriting (`repo.rel` /
 * `repo.inner`), the push range. Varies: repo vs plain folder vs push vs a test fake.
 * Root-relative paths, forward slashes, de-duplicated. Never throws: a git failure is [] (as today).
 */
export interface ChangeSource<H> {
  changed(look: Look<H>): Promise<readonly string[]>
}

const gitIn = <H>(look: Look<H>, argv: readonly string[], timeoutMs = 120000) =>
  look.runner.run(look.h, argv, { cwd: look.repo?.top ?? look.config.root, timeoutMs })

/** A repo-relative path as the lint root reads it ([] when it falls outside the lint root). */
function toRoot<H>(look: Look<H>, p: string): string[] {
  const repo = look.repo
  if (!repo) return [p]
  if (repo.rel) return [`${repo.rel}/${p}`]
  const inner = `${repo.inner ?? ''}/`
  return p.toLowerCase().startsWith(inner.toLowerCase()) ? [p.slice(inner.length)] : []
}
const lines = (s: unknown) => String(s ?? '').split(/\0|\r?\n/).filter(Boolean)

/** The paths of `git status --porcelain -z`: each entry `XY path`, NUL-ended; a rename or copy (X or Y is R or
 *  C) is followed by the old path as one more NUL-ended field, which is skipped. Pure. */
export function statusPaths(out: string): string[] {
  const fields = out.split('\0')
  const paths: string[] = []
  for (let i = 0; i < fields.length; i++) {
    const f = fields[i]
    if (f.length < 4) continue
    paths.push(f.slice(3))
    if (/[RC]/.test(f.slice(0, 2))) i++
  }
  return paths
}
const unique = (xs: readonly string[]) => [...new Set(xs)]

/** A repo (the lint root, or the commit's repo): `git status --porcelain -z --untracked-files=all`, renames to
 *  their new name, rewritten to the lint root. -z: names as they are — without it git quotes a name with
 *  non-ASCII letters (報表.csv → "\345\240\261..."), and a check would be handed a path that does not exist. */
export const workingTree: ChangeSource<any> = {
  async changed(look) {
    const r = await gitIn(look, ['git', 'status', '--porcelain', '-z', '--untracked-files=all'])
    if (r.exitCode !== 0) return []
    return unique(statusPaths(String(r.stdout)).flatMap(p => toRoot(look, p)))
  },
}

/** A plain folder outside a commit: no change of its own → []. `diff` / `related` checks stay silent there
 *  and wait for a commit in a sub-repo (which has a repo look) — the same rule `changed` notes follow today. */
export const noChange: ChangeSource<any> = {
  changed: async () => [],
}

/** A push: the files the commits it sends touch — `git diff --name-only <remote>/<dst>...<src>` per refspec,
 *  `@{u}...HEAD` without one; a branch with no upstream yet → `git diff --name-only <default>...HEAD`.
 *  Working-tree edits are not sent, so they are not in it. */
export const pushRange = (at: { readonly push: { readonly refs: readonly PushRef[] | null } | null }): ChangeSource<any> => ({
  async changed(look) {
    const refs = at.push?.refs
    const ranges = refs ? refs.filter(r => r.src).map(r => `${r.remote}/${r.dst}...${r.src}`) : ['@{u}...HEAD']
    const out: string[] = []
    for (const range of ranges) {
      let r = await gitIn(look, ['git', 'diff', '--name-only', '-z', range])
      if (r.exitCode !== 0) {
        const head = String((await gitIn(look, ['git', 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD'])).stdout).trim()
        const base = head || 'main'
        r = await gitIn(look, ['git', 'diff', '--name-only', '-z', `${base}...${refs ? range.split('...')[1] : 'HEAD'}`])
      }
      if (r.exitCode === 0) out.push(...lines(r.stdout).flatMap(p => toRoot(look, p)))
    }
    return unique(out)
  },
})

/** An act that names its own files (an edit, a file changed outside, what a command or a subagent changed):
 *  those files, asked of nothing. */
export const editedFile = (files: readonly string[]): ChangeSource<any> => ({ changed: async () => [...files] })

/** Which ChangeSource an occurrence uses. Pure; the only place the choice is made.
 *   an act with its own files (fixedFiles) → editedFile; a push → pushRange; plain folder with no commit repo →
 *   noChange; otherwise → workingTree. */
export function changeSourceFor<H>(look: Look<H>, at: Occurrence): ChangeSource<H> {
  const fixed = fixedFiles(at)
  if (fixed) return editedFile(fixed)
  if ('push' in at && at.push) return pushRange(at)
  if (!look.config.git && !look.repo) return noChange
  return workingTree
}

// ================================================================ seam 3: environment facts

/** What a fact may read. `machine` is the outbound port for things only the host knows. */
export type FactContext<H> = { readonly look: Look<H>; readonly machine: Machine<H> }

/**
 * One environment fact: `when = ["<name>:<arg>"]`. Adding a fact is one entry; a fact that needs a new
 * machine question also adds that question to Machine (and its adapter) — the outside it really depends on.
 * read → true/false when known; undefined when it could not be read.
 */
export type Fact = {
  readonly read: <H>(ctx: FactContext<H>, arg: string | undefined) => Promise<boolean | undefined>
  /** The note when a required thing is missing, e.g. 「沒有 {arg}」. */
  readonly missing?: (arg: string | undefined) => string
}

export const FACTS: Readonly<Record<string, Fact>> = {
  /** os:windows | os:linux | os:mac — machine.os. */
  os: {
    async read(ctx, arg) {
      const os = await ctx.machine.os(ctx.look.h)
      return os === undefined ? undefined : os === (arg ?? '').toLowerCase()
    },
  },
  /** tool:tlc — machine.onPath(tlc); false → the guard fails with 「沒有 tlc，這條沒檢查」. */
  tool: {
    read: (ctx, arg) => (arg ? ctx.machine.onPath(ctx.look.h, arg) : Promise.resolve(undefined)),
    missing: arg => `沒有 ${arg}，這條沒檢查`,
  },
  /** env:CI (set and non-empty) | env:NODE_ENV=production (equal) — machine.env. */
  env: {
    async read(ctx, arg) {
      if (!arg) return undefined
      const eq = arg.indexOf('=')
      const name = eq < 0 ? arg : arg.slice(0, eq)
      const v = await ctx.machine.env(ctx.look.h, name)
      return eq < 0 ? v !== undefined && v !== '' : v === arg.slice(eq + 1)
    },
  },
  /** branch:main | branch:re:^release/ — `git rev-parse --abbrev-ref HEAD` in the look's repo. */
  branch: {
    async read(ctx, arg) {
      if (!ctx.look.config.git && !ctx.look.repo) return false
      const r = await gitIn(ctx.look, ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 10000)
      if (r.exitCode !== 0) return undefined
      const b = String(r.stdout).trim()
      if (!arg) return b !== ''
      return arg.startsWith('re:') ? toRegExp(arg.slice(3)).test(b) : b === arg
    },
  },
  /** git — the look is a repo (config.git, or a commit repo). `!git` — a plain folder. */
  git: { read: async ctx => ctx.look.config.git || !!ctx.look.repo },
  /** exists:<root-relative path> — runner.probe; e.g. a check that only applies once a Dockerfile exists. */
  exists: {
    async read(ctx, arg) {
      if (!arg) return undefined
      const at = await ctx.look.runner.probe(ctx.look.h, `${ctx.look.config.root}/${arg}`)
      return at.kind === 'unreadable' ? undefined : at.kind !== 'missing'
    },
  },
}

// ================================================================ the lens itself

/**
 * Open the lens for one moment. Nothing is asked until a check needs it.
 * Memo: a Map per question holding the Promise (not the value), so two checks awaiting the same question in
 * the same moment share one run. A rejected promise is not kept: the next ask tries again (a Runner never
 * throws, so this is for a Machine or Language bug).
 * Twice: a second openLens for the same moment asks again — memo is per moment by design, so a commit right
 * after an edit sees the edit. The import indexes (GraphCache) are per moment too: openLens makes a fresh one.
 */
export function openLens<H>(look: Look<H>, at: Occurrence, deps: { machine: Machine<H>; relations: (graphs: GraphCache) => Relations<H> }): Lens {
  const memo = new Map<string, Promise<any>>()
  const once = <T>(key: string, make: () => Promise<T>): Promise<T> => {
    const had = memo.get(key)
    if (had) return had
    const p = make()
    memo.set(key, p)
    p.catch(() => memo.delete(key))
    return p
  }
  const relations = deps.relations(graphCache())
  const lens: Lens = {
    at,
    universe: () =>
      once('universe', async () => {
        const fixed = fixedFiles(at)
        if (fixed) return fixed
        const scope = look.config.git ? ['--untracked'] : ['--no-index', '--exclude-standard']
        const r = await look.runner.run(look.h, ['git', 'grep', '-lIz', ...scope, '-e', '', '--', '.'], { cwd: look.config.root, timeoutMs: 120000 })
        return r.exitCode === 0 || r.exitCode === 1 ? lines(r.stdout).map(p => p.replace(/\\/g, '/')) : []
      }),
    changed: () => once('changed', () => changeSourceFor(look, at).changed(look)),
    related: (via, depth, mode) =>
      once(`related:${[...via].sort().join(',')}:${depth}:${mode}`, async () => {
        const seeds = await lens.changed()
        if (!seeds.length) return []
        const hops = new Map<string, number>()
        for (const kind of via) {
          const found = await relations[kind].expand(look, seeds, depth, mode)
          for (const [p, h] of found) hops.set(p, Math.min(h, hops.get(p) ?? Infinity))
        }
        // Changed files first, then by hop distance, then by path (targets() cuts from the end).
        return [...hops.entries()].sort((a, b) => a[1] - b[1] || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0)).map(([p]) => p)
      }),
    fact: (name, arg) =>
      once(`fact:${name}:${arg ?? ''}`, async () => {
        const f = FACTS[name]
        return f ? f.read({ look, machine: deps.machine }, arg) : undefined
      }),
    exists: path =>
      once(`exists:${path}`, async () => (await look.runner.probe(look.h, `${look.config.root}/${path}`)).kind !== 'missing'),
  }
  return lens
}
