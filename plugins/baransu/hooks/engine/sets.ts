// Collections: config.toml's `extends` and its own [check.<id>] tables → the checks in force, each field with the
// layer it came from. Pure; the one place the merge rule is written (lint-collections plan). The adapter only
// reads the files; readCheck then turns each resolved table into a Check, as for a single check file.

import type { RawTable } from './types'

export type ResolvedCheck = {
  readonly id: string
  /** The merged fields, as one check file would hold them (no `strict`; `severity` already chosen). */
  readonly raw: RawTable
  /** Field → the layer that set it: a collection's path, `<path>（strict）`, `extends[n].severity`, or `config.toml`. */
  readonly origin: Readonly<Record<string, string>>
}

export type Resolved = {
  readonly checks: readonly ResolvedCheck[]
  /** A definition replaced by a later one: what `/lint show` lists as shadowed. */
  readonly shadowed: readonly { readonly id: string; readonly by: string; readonly was: string }[]
  readonly problems: readonly string[]
}

const ACTIONS = ['forbid', 'run', 'builtin']

const table = (v: unknown): RawTable | undefined => (v && typeof v === 'object' && !Array.isArray(v) ? (v as RawTable) : undefined)
const tables = (v: unknown): readonly RawTable[] => (Array.isArray(v) ? v.filter(x => table(x)) as RawTable[] : [])
const strings = (v: unknown): string[] | undefined =>
  Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : typeof v === 'string' ? [v] : undefined

/**
 * The merge rule, the same at every layer, in order: each `extends` entry in written order, then config.toml's own
 * [check.<id>] tables.
 * - Every table in a set is a definition: it replaces the whole check of that id (a check of only a message is
 *   one too). In config.toml a table with an action (forbid, run, builtin) is a definition; one without is a patch.
 *   A patch: each field it writes replaces that field (a list or `options` whole); a
 *   patch naming no check loaded so far is a problem.
 * - Severity, strongest first: config.toml's patch > the extends entry's `severity` > the collection's `strict`
 *   (with `level = "strict"`) or `severity`. A check the collection ships `off` stays off under an extends
 *   severity; only config.toml turns it on.
 * - `only` / `except` choose which ids of a collection load; an id they name that the collection lacks is a
 *   problem.
 */
export function resolveSets(main: RawTable, sets: ReadonlyMap<string, RawTable>): Resolved {
  const problems: string[] = []
  const shadowed: { id: string; by: string; was: string }[] = []
  const acc = new Map<string, { raw: Record<string, unknown>; origin: Record<string, string> }>()

  const actionLayer = (o: Record<string, string>) => ACTIONS.map(a => o[a]).find(Boolean) ?? ''
  const apply = (id: string, raw: Record<string, unknown>, origin: Record<string, string>, layer: string, define = false) => {
    if (define || ACTIONS.some(a => a in raw)) {
      const had = acc.get(id)
      if (had) shadowed.push({ id, by: layer, was: actionLayer(had.origin) })
      acc.set(id, { raw: { ...raw }, origin: { ...origin } })
      return
    }
    const had = acc.get(id)
    if (!had) {
      problems.push(`${layer} 的 [check.${id}] 只改欄位，但 ${id} 不在任何載入的合集裡（名稱打錯，或要先 extends 它的合集）`)
      return
    }
    for (const [k, v] of Object.entries(raw)) {
      had.raw[k] = v
      had.origin[k] = origin[k]
    }
  }

  tables(main.extends).forEach((e, n) => {
    const at = `extends[${n + 1}]`
    const path = typeof e.set === 'string' ? e.set : ''
    const doc = sets.get(path)
    if (!doc) {
      problems.push(`${at} 找不到合集「${path}」`)
      return
    }
    const level = e.level === undefined ? 'normal' : e.level
    if (level !== 'normal' && level !== 'strict') problems.push(`${at} 的 level 只能是 normal 或 strict：「${String(level)}」`)
    const checks = table(doc.check) ?? {}
    const only = strings(e.only)
    const except = strings(e.except) ?? []
    for (const id of [...(only ?? []), ...except]) if (!(id in checks)) problems.push(`${at} 的 only／except 寫了「${id}」，${path} 裡沒有這條`)
    for (const [id, v] of Object.entries(checks)) {
      const t = table(v)
      if (!t || (only && !only.includes(id)) || except.includes(id)) continue
      const raw: Record<string, unknown> = { ...t }
      const origin: Record<string, string> = Object.fromEntries(Object.keys(t).map(k => [k, path]))
      const useStrict = level === 'strict' && typeof t.strict === 'string'
      delete raw.strict
      delete origin.strict
      if (useStrict) {
        raw.severity = t.strict
        origin.severity = `${path}（strict）`
      }
      if (typeof e.severity === 'string' && raw.severity !== 'off') {
        raw.severity = e.severity
        origin.severity = `${at}.severity`
      }
      apply(id, raw, origin, path, true)
    }
  })

  for (const [id, v] of Object.entries(table(main.check) ?? {})) {
    const t = table(v)
    if (!t) continue
    const raw: Record<string, unknown> = { ...t }
    delete raw.strict
    apply(id, raw, Object.fromEntries(Object.keys(raw).map(k => [k, 'config.toml'])), 'config.toml')
  }

  return {
    checks: [...acc.entries()].map(([id, c]) => ({ id, raw: c.raw as RawTable, origin: c.origin })),
    shadowed,
    problems,
  }
}
