// Raw check fields → Scope. Called from readCheck only, so every converter gets the same meaning.
// Pure. Never throws. A scope it cannot fully read is never half-applied: the check stays off and every
// problem is reported — dropping one narrowing term would silently widen the check.

import type { ActionKind, Base, Guard, Matcher, PathFilter, RelationKind, Scope, ScopeRead } from './types'

/** The fields a check file uses for its scope. Every value is a string or a list of strings, so a converter
 *  that reads flat `key = value` (the TOML subset today) can carry all of them — no tables needed. */
export const SCOPE_FIELDS = ['scope', 'via', 'depth', 'folder', 'file', 'ext', 'ignores', 'actions', 'when'] as const

/** Named sets a user writes in place of a list. Each lives in the field it expands into, so an alias never
 *  changes the AND/OR rule: `ext = ["TLA+"]` is `ext = ["tla"]`; `file = ["@docs"]` is its globs.
 *  Adding an alias is one entry here. `.cfg` is not TLA+ by its extension alone (setup.cfg, tox.cfg): a check
 *  that wants a model's config too writes `file = ["@tla"]`, which takes only a .cfg beside a .tla of the same
 *  stem — that pairing is a fact of the tree, so `@tla` is resolved by the lens, not here. */
export const EXT_ALIASES: Readonly<Record<string, readonly string[]>> = {
  'TLA+': ['tla'],
}
/** File aliases the lens resolves from the tree rather than from globs. */
export const TREE_ALIASES = ['@tla'] as const
export const FILE_ALIASES: Readonly<Record<string, readonly string[]>> = {
  /** Document files. */
  '@docs': ['**/*.md', '**/*.mdx', '**/*.rst', '**/*.adoc', 'docs/**', '**/README*', '**/CHANGELOG*'],
  /** Environment config: secrets/env, containers, CI, dependency manifests. */
  '@env': [
    '**/.env', '**/.env.*', '**/Dockerfile*', '**/docker-compose*.yml', '**/compose*.yaml',
    '.github/workflows/**', '.gitlab-ci.yml', 'azure-pipelines.yml', '.circleci/**',
    '**/package.json', '**/pyproject.toml', '**/requirements*.txt', '**/Cargo.toml', '**/*.csproj',
    '**/pom.xml', '**/build.gradle*', '**/go.mod',
  ],
  /** How the project is run and deployed: task runners, the prove-it run recipe, deploy scripts. */
  '@run': ['**/Makefile', '**/justfile', '**/Procfile', '.claude/prove-it/recipe.md', 'deploy/**', '**/deploy*.*', 'scripts/**'],
}

const DEFAULT_DEPTH = 3
const MAX_DEPTH = 6

/**
 * Pseudocode:
 *   base    ← scope: "all" (default) | "diff" | "related"; anything else → problem.
 *             related: via ⊆ RelationKind (default ["imports"]), depth = int(depth) in 1..MAX_DEPTH
 *             (default 3; outside → problem). `via`/`depth` without `scope = "related"` → problem.
 *   files   ← the old field name: problem 「files 改名了：跑 /lint sync 就會改好（改成 file，慢的 run 檢查加上
 *             scope = "diff"）」 (sole user, no silent mapping; decision 1).
 *   where   ← folder: each "re:x" → regex, else prefix (normalised: no leading "./", trailing "/");
 *             file:   each "@alias" → FILE_ALIASES globs, "re:x" → regex, else glob;
 *             ext:    each alias → EXT_ALIASES, else lower-case without a leading dot.
 *   ignores ← like file (globs, re:, @alias).
 *   actions ← ⊆ ActionKind (delete, worktree-remove); the old push / redo → problem pointing to /lint sync.
 *   when    ← each "!"? name (":" arg)?; name not in FACTS → problem (so a typo does not silently gate).
 *   A regex that does not compile → problem.
 *   Any problem → { ok: false, problems }: readCheck keeps the check out of force and the config source shows
 *   each as 「設定讀不懂：checks/<id>：<text>」.
 */
export function scopeFrom(raw: Readonly<Record<string, unknown>>, factNames: readonly string[]): ScopeRead {
  const problems: string[] = []
  const list = (v: unknown): string[] =>
    Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : typeof v === 'string' ? [v] : []
  const regex = (field: string, source: string): Matcher | undefined => {
    if (!compiles(source)) {
      problems.push(`${field} 的正規式讀不懂：「${source}」`)
      return undefined
    }
    return { kind: 'regex', source }
  }

  if (raw.files !== undefined) problems.push('files 改名了：跑 /lint sync 就會改好（改成 file，慢的 run 檢查加上 scope = "diff"）')

  // base
  const scope = raw.scope === undefined ? 'all' : raw.scope
  let base: Base = { kind: 'all' }
  if (scope === 'all' || scope === 'diff') base = { kind: scope }
  else if (scope === 'related') {
    const via = raw.via === undefined ? ['imports'] : list(raw.via)
    const bad = via.filter(v => !RELATIONS.includes(v as RelationKind))
    if (bad.length) problems.push(`via 只能是 imports、mentions：「${bad.join('、')}」`)
    let depth = DEFAULT_DEPTH
    if (raw.depth !== undefined) {
      const text = typeof raw.depth === 'string' || typeof raw.depth === 'number' ? String(raw.depth) : ''
      const n = /^\d+$/.test(text) ? Number(text) : NaN
      if (!(n >= 1 && n <= MAX_DEPTH)) problems.push(`depth 要是 1 到 ${MAX_DEPTH} 的整數：「${text}」`)
      else depth = n
    }
    base = { kind: 'related', via: via.filter(v => RELATIONS.includes(v as RelationKind)) as RelationKind[], depth }
  } else problems.push(`scope 只能是 all、diff、related：「${String(scope)}」`)
  if (scope !== 'related' && (raw.via !== undefined || raw.depth !== undefined))
    problems.push('via、depth 只在 scope = "related" 時有意義')

  // where
  const folders: Matcher[] = []
  for (const f of list(raw.folder)) {
    if (f.startsWith('re:')) {
      const m = regex('folder', f.slice(3))
      if (m) folders.push(m)
    } else {
      const p = f.replace(/\\/g, '/').replace(/^\.\//, '').replace(/\/*$/, '/')
      folders.push({ kind: 'prefix', prefix: p })
    }
  }
  const trees: '@tla'[] = []
  const files = fileMatchers('file', list(raw.file), problems, regex, trees)
  const exts = list(raw.ext).flatMap(e => EXT_ALIASES[e] ?? [e.replace(/^\./, '').toLowerCase()])
  const ignored: '@tla'[] = []
  const ignores = fileMatchers('ignores', list(raw.ignores), problems, regex, ignored)
  if (ignored.length) problems.push('ignores 不能寫 @tla（它是要加進來的檔，不是排除的樣式）')

  // actions
  const actions = list(raw.actions)
  // push and redo became timings (pre:push, post:retry): the old words point to the migration.
  const moved = actions.filter(a => a === 'push' || a === 'redo')
  if (moved.length) problems.push(`舊寫法 actions = ["${moved.join('", "')}"]：跑 /lint sync 換成 on = ["pre:push"]／["post:retry"]`)
  const badActions = actions.filter(a => !ACTIONS.includes(a as ActionKind) && a !== 'push' && a !== 'redo')
  if (badActions.length) problems.push(`actions 只能是 delete、worktree-remove：「${badActions.join('、')}」`)

  // when
  const when: Guard[] = []
  for (const w of list(raw.when)) {
    const m = /^(!?)([A-Za-z]+)(?::(.*))?$/.exec(w.trim())
    if (!m || !factNames.includes(m[2])) {
      problems.push(`when 不認得「${w}」：可以用 ${factNames.join('、')}`)
      continue
    }
    // A regex argument (`branch:re:^release/`) is checked here like folder and file regexes: one that does not
    // compile would otherwise throw when the guard is read and take every check of that moment down with it.
    if (m[3]?.startsWith('re:') && !regex('when', m[3].slice(3))) continue
    when.push({ name: m[2], arg: m[3] === undefined || m[3] === '' ? undefined : m[3], negate: m[1] === '!', written: w })
  }

  if (problems.length) return { ok: false, problems }
  return {
    ok: true,
    scope: {
      base,
      where: { folders, files, trees, exts },
      ignores,
      actions: actions as ActionKind[],
      when,
    },
  }
}

const RELATIONS: readonly RelationKind[] = ['imports', 'mentions']
const ACTIONS: readonly ActionKind[] = ['delete', 'worktree-remove']

/** `file` and `ignores` entries: @alias → its globs (or a tree alias), re: → regex, else a glob. */
function fileMatchers(
  field: string,
  entries: readonly string[],
  problems: string[],
  regex: (field: string, source: string) => Matcher | undefined,
  trees: '@tla'[],
): Matcher[] {
  const out: Matcher[] = []
  for (const f of entries) {
    if (f.startsWith('@')) {
      if ((TREE_ALIASES as readonly string[]).includes(f)) trees.push(f as '@tla')
      else if (FILE_ALIASES[f]) out.push(...FILE_ALIASES[f].map(glob => ({ kind: 'glob' as const, glob })))
      else problems.push(`${field} 不認得別名「${f}」：可以用 ${[...Object.keys(FILE_ALIASES), ...TREE_ALIASES].join('、')}`)
    } else if (f.startsWith('re:')) {
      const m = regex(field, f.slice(3))
      if (m) out.push(m)
    } else out.push({ kind: 'glob', glob: f.replace(/\\/g, '/') })
  }
  return out
}

/** Whether a regex as written in a check compiles in JS; a leading (?i) becomes the i flag, as bash forbids do. */
export function compiles(source: string): boolean {
  try {
    toRegExp(source)
    return true
  } catch {
    return false
  }
}

/** A check's regex as JS: a leading (?i) is the i flag. Throws on a bad pattern (callers parse first). */
export function toRegExp(source: string): RegExp {
  return source.startsWith('(?i)') ? new RegExp(source.slice(4), 'i') : new RegExp(source)
}

/** The timing a check's actions imply when its `on` is empty. */
export const TIMING_OF: Readonly<Record<ActionKind, 'pre:bash'>> = {
  delete: 'pre:bash',
  'worktree-remove': 'pre:bash',
}

export type { Base, Guard, Matcher, PathFilter, RelationKind }
