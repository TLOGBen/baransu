// The ConfigSource on Claude Code: finds the project root, reads `.claude/lint/lint.json` if any, picks the
// converter by name, reads the check files. Its cache is a cache, not state: a reload just reads again.

import { checkFrom, type Check, type Config, type ConfigSource, type Finding } from '../../engine'
import { converterNamed } from '../../util/converters'
import type { Host } from './ports'

/** The one fixed path. Everything else is named inside it, relative to its folder. */
export const LINT_DIR = '.claude/lint'
export const LINT_JSON = `${LINT_DIR}/lint.json`

/** Where the rules for ast-grep live is not a setting here: sgconfig's own `ruleDirs` is its one owner. */
export type LintSettings = { converter: string; checks: string; sgconfig: string }
export const DEFAULTS: LintSettings = { converter: 'toml', checks: 'checks', sgconfig: 'sgconfig.yml' }

const problem = (text: string): Finding => ({ id: 'lint.json', severity: 'warn', text: `設定讀不懂：lint.json：${text}` })

/** `base/rel` with `.` and `..` folded; an absolute `rel` stands alone. Forward slashes. */
function join(base: string, rel: string): string {
  const r = rel.replace(/\\/g, '/')
  const start = /^([A-Za-z]:)?\//.test(r) ? r : `${base}/${r}`
  const out: string[] = []
  for (const part of start.split('/')) {
    if (part === '.' || (part === '' && out.length > 0)) continue
    if (part === '..') {
      if (out.length > 1) out.pop()
      continue
    }
    out.push(part)
  }
  return out.join('/')
}

/** Inside root, case-insensitive (as relTo reads paths). */
const inside = (root: string, p: string) => p.toLowerCase() === root.toLowerCase() || p.toLowerCase().startsWith(root.toLowerCase() + '/')
const rel = (root: string, p: string) => (p.toLowerCase().startsWith(root.toLowerCase() + '/') ? p.slice(root.length + 1) : p)

/**
 * lint.json's fields over the defaults, each path made absolute against `<root>/.claude/lint`. Pure.
 * A field that is not a string, or a path that resolves outside `root` (`..`, an absolute path elsewhere),
 * is dropped for its default and reported 「設定讀不懂：lint.json：<field> …」. Unknown fields are ignored.
 * `json` undefined (no lint.json) → the defaults, no problems.
 */
export function resolveSettings(root: string, json: unknown): { value: LintSettings; problems: Finding[] } {
  const base = `${root}/${LINT_DIR}`
  const problems: Finding[] = []
  const given: Record<string, unknown> =
    json === undefined ? {} : json !== null && typeof json === 'object' && !Array.isArray(json) ? (json as Record<string, unknown>) : (problems.push(problem('要是一個 JSON 物件')), {})
  const field = (name: keyof LintSettings): string | undefined => {
    const v = given[name]
    if (v === undefined) return undefined
    if (typeof v !== 'string') {
      problems.push(problem(`${name} 要是字串，改用預設的 ${DEFAULTS[name]}`))
      return undefined
    }
    return v
  }
  const converter = field('converter') ?? DEFAULTS.converter
  const path = (name: 'checks' | 'sgconfig'): string => {
    const v = field(name)
    if (v !== undefined) {
      const p = join(base, v)
      if (inside(root, p)) return p
      problems.push(problem(`${name} 指到專案外面（${v}），改用預設的 ${DEFAULTS[name]}`))
    }
    return join(base, DEFAULTS[name])
  }
  return { value: { converter, checks: path('checks'), sgconfig: path('sgconfig') }, problems }
}

/**
 * - root: the nearest folder from the session cwd upward holding `.claude/lint/`, else the git top level;
 *   a root the walk finds is kept per session cwd; with none found the walk is asked again on every load
 *   (only the git top level is kept), so a later /lint init is seen. `git`: whether the root is a work tree's top.
 * - no `<root>/.claude/lint` → null, checked on every load and never cached (today's hasLint asks each
 *   time), so null means exactly "this project has no .claude/lint/" for every engine method.
 * - cache: 5 s per root for the parsed checks; `edited` with a file under LINT_DIR, or under the checks folder / sgconfig lint.json names elsewhere, drops it at once.
 * - lint.json unreadable JSON → defaults + problem; unknown converter → no checks + problem.
 * - the checks folder missing → no checks, no problem (as 8.39's readChecks did).
 * - every `<checks>/*<converter.extension>` file: a parse throw → 「設定讀不懂：checks/<name>：<message>」
 *   (same words as today); otherwise checkFrom(id, fields), and an undefined result (an off check) is left out.
 * - sgconfig: its path, relative to root. Whether the file exists is asked when ast-grep is about to run
 *   (as today, per moment), not cached here.
 * Runs twice: same answer, or the cached one. Stops halfway: nothing written.
 */
export function hostConfig(): ConfigSource<Host> {
  // Caches, not state: a reload just looks again. rootByCwd holds only a root found by the walk.
  const rootByCwd = new Map<string, { root: string; git: boolean }>()
  const gitTopByCwd = new Map<string, string | undefined>()
  let cache: { root: string; at: number; settings: LintSettings; value: Config } | undefined

  // The root is the nearest folder, from the session's directory upward, that holds `.claude/lint/` — git or
  // not, so a workspace that is a plain folder over several repos gets its lint. When no such folder is found
  // (or the directory cannot be read), the git top level, as before. `git` says whether the root is a repo.
  async function rootOf(h: Host): Promise<{ root: string; git: boolean } | undefined> {
    let cwd = ''
    try { cwd = String(await h.cwd()).replace(/\\/g, '/').replace(/\/+$/, '') } catch {}
    if (rootByCwd.has(cwd)) return rootByCwd.get(cwd)
    const top = async (at?: string): Promise<string | undefined> => {
      try {
        const r = await (at ? h.run(['git', 'rev-parse', '--show-toplevel'], { cwd: at, timeoutMs: 10000 }) : h.run(['git', 'rev-parse', '--show-toplevel']))
        if (r.exitCode === 0) return String(r.stdout).trim().replace(/\\/g, '/')
      } catch {}
      return undefined
    }
    for (let dir = cwd; dir && dir.includes('/'); dir = dir.slice(0, dir.lastIndexOf('/'))) {
      if (await h.exists(`${dir}/${LINT_DIR}`)) {
        const t = await top(dir)
        const found = { root: dir, git: !!t && t.toLowerCase() === dir.toLowerCase() }
        rootByCwd.set(cwd, found)
        return found
      }
    }
    // No .claude/lint/ on the way up: the git top level, as before. Only that answer is kept (gitTopByCwd);
    // the walk is asked again on the next load, so a /lint init later in the session wakes the mod.
    if (!gitTopByCwd.has(cwd)) gitTopByCwd.set(cwd, await top())
    const t = gitTopByCwd.get(cwd)
    return t ? { root: t, git: true } : undefined
  }

  async function read(h: Host, root: string, git: boolean): Promise<{ settings: LintSettings; value: Config }> {
    const problems: Finding[] = []
    let json: unknown
    try {
      if (await h.exists(`${root}/${LINT_JSON}`)) json = JSON.parse(await h.read(`${root}/${LINT_JSON}`))
    } catch (err) {
      problems.push(problem((err as Error).message))
    }
    const resolved = resolveSettings(root, json)
    const settings = resolved.value
    problems.push(...resolved.problems)
    const checks: Check[] = []
    const value = (): Config => ({ root, git, checks, problems, sgconfig: rel(root, settings.sgconfig) })
    const converter = converterNamed(settings.converter)
    if (!converter) {
      problems.push(problem(`沒有叫 ${settings.converter} 的轉換器`))
      return { settings, value: value() }
    }
    const dir = settings.checks
    const label = rel(`${root}/${LINT_DIR}`, dir)
    if (!(await h.exists(dir))) return { settings, value: value() }
    for (const entry of await h.list(dir)) {
      if (entry.kind !== 'file' || !entry.name.endsWith(converter.extension)) continue
      const id = entry.name.slice(0, -converter.extension.length)
      let fields
      try {
        fields = converter.parse(await h.read(`${dir}/${entry.name}`))
      } catch (err) {
        problems.push({ id, severity: 'warn', text: `設定讀不懂：${label}/${entry.name}：${(err as Error).message}` })
        continue
      }
      const c = checkFrom(id, fields)
      if (c) checks.push(c)
    }
    return { settings, value: value() }
  }

  return {
    async load(h) {
      const found = await rootOf(h)
      if (!found || !(await h.exists(`${found.root}/${LINT_DIR}`))) return null
      const { root, git } = found
      if (cache && cache.root === root && Date.now() - cache.at < 5000) return cache.value
      const { settings, value } = await read(h, root, git)
      cache = { root, at: Date.now(), settings, value }
      return value
    },
    edited(_$, file) {
      // `file` is root-relative. Its own: under LINT_DIR, or under the checks folder / the sgconfig file the
      // cached lint.json named elsewhere in the project. Its own → drop the cache and say so (read it again).
      const f = file.replace(/\\/g, '/')
      const own =
        f.startsWith(`${LINT_DIR}/`) ||
        (!!cache && (f.startsWith(`${rel(cache.root, cache.settings.checks)}/`) || f === rel(cache.root, cache.settings.sgconfig)))
      if (own) cache = undefined
      return own
    },
  }
}
