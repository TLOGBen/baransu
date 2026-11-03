// Before/after snapshots for around:<act>, and their difference. Everything outside goes through the Runner.
//
// Where a snapshot lives: a tool call's before and after happen inside ONE engine call (toolCall wraps
// `proceed`), so its snapshot is a local of that call — never in LintState, never shared between calls, gone
// when the call returns. Only an agent's snapshot spans two host events (agent.spawn → SubagentStop); that one
// is kept in LintState.spans by agent id, at most MAX_SPANS, removed synchronously when taken.
//
// A file's content before the act is kept in a bare git of the mod's own, in the system's temp folder (the
// Store; LintState.objects): `git hash-object -w` writes it there, and a `run` check reads it back with
// `git --git-dir="$LINT_GIT_DIR" cat-file blob <hash>`. Nothing is written into the project. A file the project's
// own git already holds (clean before the act, or in the commit before) is named by its blob there, which the
// same command reaches through GIT_ALTERNATE_OBJECT_DIRECTORIES.
//
// Nothing is snapshotted unless a check in force reads around:<act> (wantsAround), so the common case costs
// nothing. (.claude/draft/lint-timing.md, 〈around〉)

import type { Look } from './moments'
import type { Check } from './types'
import { MAX_TARGETS } from './scope/types'

export const MAX_SPANS = 8
/** A file larger than this is not snapshotted: around:edit says so on the card and skips. */
export const MAX_EDIT_BYTES = 1 << 20

export type AroundAct = 'edit' | 'bash' | 'commit' | 'agent'

/** The mod's own object store: a bare git in the temp folder, made once a session (engine.ts storeOf). */
export type Store = { readonly dir: string }

/** around:edit: the file's text before the write (null: it did not exist) and its blob in the Store ('' for a new
 *  file; null when the Store could not keep it). */
export type EditSnap =
  | { readonly kind: 'edit'; readonly file: string; readonly text: string | null; readonly hash: string | null }
  | { readonly kind: 'too-big'; readonly file: string }
/** around:bash / around:agent: every path `git status --porcelain -z` lists, with its blob in the Store. */
export type TreeSnap = { readonly kind: 'tree'; readonly entries: Readonly<Record<string, string>> }
/** around:commit: HEAD's sha. */
export type HeadSnap = { readonly kind: 'head'; readonly sha: string }

export type TreeDiff = { readonly changed: readonly string[]; readonly removed: readonly string[] }
export type HeadDiff = { readonly from: string; readonly to: string; readonly commits: readonly string[]; readonly changed: readonly string[] }

/** Whether any check in force reads around:<act>. Pure. */
export function wantsAround(checks: readonly Check[], act: AroundAct): boolean {
  const key = `around:${act}`
  return checks.some(c => c.on.some(t => t.key === key))
}

const abs = <H>(look: Look<H>, file: string) => (/^([A-Za-z]:)?\//.test(file) ? file : `${look.config.root}/${file}`)
const git = <H>(look: Look<H>, argv: readonly string[]) => look.runner.run(look.h, ['git', ...argv], { cwd: look.config.root, timeoutMs: 30000 })
const lines = (s: string) => String(s).trim().split(/\r?\n/).filter(Boolean)

/** Write files' current content into the Store; their blob hashes, in order. Where the Store could not keep
 *  them, the hash is still worked out (nothing written) and marked unknown, `?<hash>`, so a before and an after
 *  can be compared while the content is not readable; '' where even that failed. */
async function keep<H>(look: Look<H>, store: Store | undefined, paths: readonly string[]): Promise<string[]> {
  if (!paths.length) return []
  if (store) {
    const r = await git(look, [`--git-dir=${store.dir}`, 'hash-object', '-w', '--', ...paths])
    const out = r.exitCode === 0 ? lines(r.stdout) : []
    if (out.length === paths.length) return out
  }
  const r = await git(look, ['hash-object', '--', ...paths])
  const out = r.exitCode === 0 ? lines(r.stdout) : []
  return paths.map((_, i) => (out[i] ? `?${out[i]}` : ''))
}
const unknown = (hash: string) => hash === '' || hash.startsWith('?')

export async function snapEdit<H>(look: Look<H>, file: string, store: Store | undefined): Promise<EditSnap> {
  const text = await look.runner.read(look.h, abs(look, file))
  if (text !== null && text.length > MAX_EDIT_BYTES) return { kind: 'too-big', file }
  // A new file has no before (''); a store that could not keep the content leaves it unknown (null).
  const [hash] = text === null ? [''] : await keep(look, store, [abs(look, file)])
  return { kind: 'edit', file, text, hash: text === null ? '' : unknown(hash) ? null : hash }
}

/** The dirty paths and their blobs, their content kept in the Store. Empty outside a repo. */
export async function snapTree<H>(look: Look<H>, store: Store | undefined): Promise<TreeSnap> {
  if (!look.config.git) return { kind: 'tree', entries: {} }
  const st = await git(look, ['status', '--porcelain', '-z', '--untracked-files=all'])
  if (st.exitCode !== 0) return { kind: 'tree', entries: {} }
  const paths: string[] = []
  const parts = String(st.stdout).split('\0')
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i]
    if (p.length < 4) continue
    const code = p.slice(0, 2)
    paths.push(p.slice(3))
    if (code[0] === 'R' || code[0] === 'C') i++ // the rename's source follows
  }
  const entries: Record<string, string> = {}
  const present: string[] = []
  for (const p of paths.slice(0, MAX_TARGETS)) {
    if ((await look.runner.probe(look.h, abs(look, p))).kind === 'file') present.push(p)
    else entries[p] = 'missing'
  }
  const hashes = await keep(look, store, present)
  present.forEach((p, i) => (entries[p] = hashes[i] || '?'))
  return { kind: 'tree', entries }
}

export async function snapHead<H>(look: Look<H>): Promise<HeadSnap> {
  const r = await git(look, ['rev-parse', 'HEAD'])
  return { kind: 'head', sha: r.exitCode === 0 ? String(r.stdout).trim() : '' }
}

/** Pure: the lines the after text has that the before text did not (a multiset difference, not an ordered
 *  diff — forbid only needs what is new). A whole new file is all added. */
export function addedLines(before: string | null, after: string | null): string[] {
  const count = new Map<string, number>()
  for (const l of (before ?? '').split(/\r?\n/)) count.set(l, (count.get(l) ?? 0) + 1)
  const out: string[] = []
  for (const l of (after ?? '').split(/\r?\n/)) {
    const n = count.get(l) ?? 0
    if (n > 0) count.set(l, n - 1)
    else if (l !== '') out.push(l)
  }
  return out
}

/** What changed between the snapshot and now: a path whose blob moved, a new dirty path, a path dirty before
 *  and clean now (reverted); `removed` the ones that no longer exist. */
export async function diffTree<H>(look: Look<H>, before: TreeSnap, store: Store | undefined): Promise<TreeDiff> {
  const after = await snapTree(look, store)
  const changed: string[] = []
  const removed: string[] = []
  for (const [p, hash] of Object.entries(after.entries)) {
    if (before.entries[p] === hash) continue
    if (hash === 'missing') removed.push(p)
    else changed.push(p)
  }
  for (const p of Object.keys(before.entries)) {
    if (p in after.entries) continue
    if ((await look.runner.probe(look.h, abs(look, p))).kind === 'missing') removed.push(p)
    else changed.push(p)
  }
  return { changed, removed }
}

export async function diffHead<H>(look: Look<H>, before: HeadSnap): Promise<HeadDiff> {
  const now = await snapHead(look)
  if (!before.sha || !now.sha || before.sha === now.sha) return { from: before.sha, to: now.sha, commits: [], changed: [] }
  const range = `${before.sha}..${now.sha}`
  const commits = lines((await git(look, ['log', '--format=%s', range])).stdout)
  const changed = lines((await git(look, ['diff', '--name-only', before.sha, now.sha])).stdout)
  return { from: before.sha, to: now.sha, commits, changed }
}

/** A blob in the project's own git (`<rev>:<path>`), or '' when it has none (a new file). */
async function blobAt<H>(look: Look<H>, rev: string, path: string): Promise<string> {
  const r = await git(look, ['rev-parse', '--verify', '--quiet', `${rev}:${path}`])
  return r.exitCode === 0 ? String(r.stdout).trim() : ''
}

/** Where each changed path's content before the act is: a tree snapshot's blob in the Store, else HEAD's; null
 *  when the Store could not keep a dirty file. */
export const treeBefore = <H>(look: Look<H>, snap: TreeSnap) => async (path: string): Promise<string | null> => {
  const h = snap.entries[path]
  if (h === 'missing') return ''
  if (h === '?' || h?.startsWith('?')) return null
  return h || blobAt(look, 'HEAD', path)
}
/** Before a commit: the blob in the commit HEAD was. */
export const headBefore = <H>(look: Look<H>, snap: HeadSnap) => (path: string): Promise<string> => blobAt(look, snap.sha, path)

/**
 * The environment an around `run` gets, written to no file:
 *   LINT_CHANGED                       the changed paths, one per line
 *   LINT_BEFORE                        `<path>\t<blob>` per changed path (an empty blob: the file is new); left out
 *                                      when a before could not be kept, so a script never reads "new" for "unknown"
 *   LINT_GIT_DIR                       the git holding the blobs: the Store, else the project's own git (a commit's
 *                                      before is there); `git --git-dir="$LINT_GIT_DIR" cat-file blob <blob>`
 *   GIT_ALTERNATE_OBJECT_DIRECTORIES   the project's objects beside the Store, so a blob from HEAD is found the same way
 * Only when an around `run` is due (`wanted`); otherwise LINT_CHANGED alone.
 */
export async function aroundEnv<H>(look: Look<H>, changed: readonly string[], before: (path: string) => Promise<string | null>, wanted: boolean, store: Store | undefined): Promise<Record<string, string>> {
  const env: Record<string, string> = { LINT_CHANGED: changed.join('\n') }
  if (!wanted) return env
  const rows: string[] = []
  let known = true
  for (const p of changed.slice(0, MAX_TARGETS)) {
    const b = await before(p)
    if (b === null) known = false
    rows.push(`${p}\t${b ?? ''}`)
  }
  let project = ''
  if (look.config.git) {
    const r = await git(look, ['rev-parse', '--path-format=absolute', '--git-common-dir'])
    if (r.exitCode === 0) project = String(r.stdout).trim()
  }
  const dir = store?.dir ?? project
  if (known && dir) env.LINT_BEFORE = rows.join('\n')
  if (dir) env.LINT_GIT_DIR = dir
  if (store && project) env.GIT_ALTERNATE_OBJECT_DIRECTORIES = `${project}/objects`
  return env
}
