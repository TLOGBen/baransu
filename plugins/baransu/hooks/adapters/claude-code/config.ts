// The ConfigSource on Claude Code: finds the project root, scans `.claude/lint/` once and hands the files to the
// engine (configFromFiles), which says what they mean. What it read is kept in memory, never in a file: a reload
// of the mod just scans again.

import { configFromFiles, type Config, type ConfigSource, type Finding } from '../../engine'
import { converterNamed } from '../../util/converters'
import type { Host } from './ports'

/** The one fixed path. Everything else is named inside its config.toml, relative to it. */
export const LINT_DIR = '.claude/lint'

/** A root-relative path with `.` and `..` folded; a leading `..` stays (it leaves the project). */
function fold(path: string): string {
  const out: string[] = []
  for (const part of path.split('/')) {
    if (part === '' || part === '.') continue
    if (part === '..' && out.length && out[out.length - 1] !== '..') out.pop()
    else out.push(part)
  }
  return out.join('/')
}

/**
 * - root: the nearest folder from the session cwd upward holding `.claude/lint/`, else the git top level;
 *   a root the walk finds is kept per session cwd; with none found the walk is asked again on every load
 *   (only the git top level is kept), so a later /lint init is seen. `git`: whether the root is a work tree's top.
 * - no `<root>/.claude/lint` → null, so null means exactly "this project has no .claude/lint/" for every engine
 *   method.
 * - read once and kept in memory: one scan of the folder's files (dot folders skipped: they are no rules), given
 *   to configFromFiles. Rules change only through /lint, so `reload` (each /lint call) and `edited` (Claude's
 *   edit of a file under the folder, made while /lint runs) drop what was kept; the next load scans again.
 * - sgconfig: config.toml's, relative to root. Whether the file exists is asked when ast-grep is about to run.
 * Runs twice: same answer. Stops halfway: nothing written.
 */
export function hostConfig(): ConfigSource<Host> {
  // Kept in memory, not state: a reload just looks again. rootByCwd holds only a root found by the walk.
  const rootByCwd = new Map<string, { root: string; git: boolean }>()
  const gitTopByCwd = new Map<string, string | undefined>()
  let kept: { root: string; value: Config } | undefined

  // The root is the nearest folder, from the session's directory upward, that holds `.claude/lint/` — git or
  // not, so a workspace that is a plain folder over several repos gets its lint. When no such folder is found
  // (or the directory cannot be read), the git top level. `git` says whether the root is a repo.
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
    if (!gitTopByCwd.has(cwd)) gitTopByCwd.set(cwd, await top())
    const t = gitTopByCwd.get(cwd)
    return t ? { root: t, git: true } : undefined
  }

  /** Every text file under the lint folder, by path relative to it; dot folders skipped. */
  async function scan(h: Host, base: string, problems: Finding[]): Promise<Map<string, string>> {
    const files = new Map<string, string>()
    const walk = async (dir: string, key: string) => {
      for (const entry of await h.list(dir)) {
        const name = String(entry.name)
        const k = key ? `${key}/${name}` : name
        if (entry.kind === 'dir') {
          if (!name.startsWith('.')) await walk(`${dir}/${name}`, k)
        } else if (entry.kind === 'file' && /\.(toml|json)$/i.test(name)) {
          try {
            files.set(k, String(await h.read(`${dir}/${name}`)))
          } catch (err) {
            problems.push({ id: name, severity: 'warn', text: `設定讀不懂：${k}：${(err as Error).message}` })
          }
        }
      }
    }
    await walk(base, '')
    return files
  }

  return {
    async load(h) {
      const found = await rootOf(h)
      if (!found || !(await h.exists(`${found.root}/${LINT_DIR}`))) return null
      const { root, git } = found
      if (kept && kept.root === root) return kept.value
      const problems: Finding[] = []
      const files = await scan(h, `${root}/${LINT_DIR}`, problems)
      const r = configFromFiles(files, converterNamed)
      // sgconfig is relative to .claude/lint and may reach the project's own, never outside the project.
      let sgconfig = fold(`${LINT_DIR}/${r.settings.sgconfig}`)
      if (sgconfig === '..' || sgconfig.startsWith('../')) {
        problems.push({ id: 'config.toml', severity: 'warn', text: `設定讀不懂：config.toml：[settings] sgconfig 指到專案外面（${r.settings.sgconfig}），改用預設的 sgconfig.yml` })
        sgconfig = `${LINT_DIR}/sgconfig.yml`
      }
      const value: Config = { root, git, checks: r.checks, problems: [...problems, ...r.problems], sgconfig }
      kept = { root, value }
      return value
    },
    reload() {
      kept = undefined
    },
    edited(_$, file) {
      // `file` is root-relative. A file under the lint folder (not a dot folder) is a rule file: drop what was kept.
      const f = file.replace(/\\/g, '/')
      const own = f.startsWith(`${LINT_DIR}/`) && !f.slice(LINT_DIR.length + 1).split('/').some(s => s.startsWith('.'))
      if (own) kept = undefined
      return own
    },
  }
}
