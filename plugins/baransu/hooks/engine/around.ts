// Before/after snapshots for around:<act>, and their difference. Everything outside goes through the Runner.
//
// Where a snapshot lives: a tool call's before and after happen inside ONE engine call (toolCall wraps
// `proceed`), so its snapshot is a local of that call — never in LintState, never shared between calls, gone
// when the call returns. Only an agent's snapshot spans two host events (agent.spawn → SubagentStop); that one
// is kept in LintState.spans by agent id, at most MAX_SPANS, removed synchronously when taken.
//
// A tree snapshot writes each dirty file's content into git's object store (`git hash-object -w`), so the
// before copy of a file a command then changes can be read back for LINT_BEFORE without copying anything up
// front; a file clean before is HEAD's.
//
// Nothing is snapshotted unless a check in force reads around:<act> (wantsAround), so the common case costs
// nothing. (.claude/draft/lint-timing.md, 〈around〉)

import type { Look } from './moments'
import type { Check } from './types'
import { MAX_TARGETS } from './scope/types'

export const MAX_SPANS = 8
/** A file larger than this is not snapshotted: around:edit says so on the card and skips. */
export const MAX_EDIT_BYTES = 1 << 20
/** Where around's LINT_BEFORE copies go, under the lint root; a `.gitignore` of `*` keeps them out of git. */
export const CACHE = '.claude/lint/.cache'

export type AroundAct = 'edit' | 'bash' | 'commit' | 'agent'

/** around:edit: the file's text before the write (null: it did not exist), BOM kept as U+FEFF. */
export type EditSnap = { readonly kind: 'edit'; readonly file: string; readonly text: string | null } | { readonly kind: 'too-big'; readonly file: string }
/** around:bash / around:agent: every path `git status --porcelain -z` lists, with its content hash. */
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

export async function snapEdit<H>(look: Look<H>, file: string): Promise<EditSnap> {
  const text = await look.runner.read(look.h, abs(look, file))
  if (text !== null && text.length > MAX_EDIT_BYTES) return { kind: 'too-big', file }
  return { kind: 'edit', file, text }
}

/** The dirty paths and their hashes; their content is written into the object store. Empty outside a repo. */
export async function snapTree<H>(look: Look<H>): Promise<TreeSnap> {
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
  if (present.length) {
    const r = await git(look, ['hash-object', '-w', '--', ...present])
    const hashes = String(r.stdout).trim().split(/\r?\n/)
    present.forEach((p, i) => (entries[p] = hashes[i] ?? '?'))
  }
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

/** What changed between the snapshot and now: a path whose hash moved, a new dirty path, a path dirty before
 *  and clean now (reverted); `removed` the ones that no longer exist. */
export async function diffTree<H>(look: Look<H>, before: TreeSnap): Promise<TreeDiff> {
  const after = await snapTree(look)
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
  const commits = String((await git(look, ['log', '--format=%s', range])).stdout).trim().split(/\r?\n/).filter(Boolean)
  const changed = String((await git(look, ['diff', '--name-only', before.sha, now.sha])).stdout).trim().split(/\r?\n/).filter(Boolean)
  return { from: before.sha, to: now.sha, commits, changed }
}

/**
 * The environment an around `run` gets: LINT_CHANGED, the changed paths one per line; LINT_BEFORE, a folder
 * holding each changed file as it was before (from the snapshot's object, else HEAD; a new file is absent).
 * Written only when an around `run` is due (`wanted`), into a folder of its own per act (`tag`: the call or
 * agent id), so no copy from an earlier act is read as this one's. Old folders stay under CACHE, which git
 * ignores; the Runner has no delete.
 */
export async function aroundEnv<H>(look: Look<H>, changed: readonly string[], before: (path: string) => Promise<string | null>, wanted: boolean, tag: string): Promise<Record<string, string>> {
  const env: Record<string, string> = { LINT_CHANGED: changed.join('\n') }
  if (!wanted) return env
  const dir = `${look.config.root}/${CACHE}/before/${tag.replace(/[^\w-]/g, '_')}`
  await look.runner.write(look.h, `${look.config.root}/${CACHE}/.gitignore`, '*\n')
  for (const p of changed.slice(0, MAX_TARGETS)) {
    const text = await before(p)
    if (text !== null) await look.runner.write(look.h, `${dir}/${p}`, text)
  }
  env.LINT_BEFORE = dir
  return env
}

/** A tree snapshot's before copy of `path`: its stored object, else HEAD's, else null (new). */
export const treeBefore = <H>(look: Look<H>, snap: TreeSnap) => async (path: string): Promise<string | null> => {
  const hash = snap.entries[path]
  if (hash === 'missing') return null
  const r = hash ? await git(look, ['cat-file', 'blob', hash]) : await git(look, ['show', `HEAD:${path}`])
  return r.exitCode === 0 ? String(r.stdout) : null
}
