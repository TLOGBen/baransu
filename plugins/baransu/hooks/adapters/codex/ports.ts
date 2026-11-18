// The outbound ports on Codex: plain Node, one hook process per event. `H` is the hook's own context.

import { spawn } from 'node:child_process'
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { homedir } from 'node:os'
import {
  configFromFiles, type Clock, type Config, type ConfigSource, type Finding, type LintState, type PathProbe, type Ports,
  type Runner, type RunResult, type StateStore,
} from '../../engine'
import { runnerMachine } from '../../engine/scope/machine'
import { converterNamed } from '../../util/converters'
import { LANGUAGES } from '../../util/languages'

/** One hook call: where its shell is, and the state the engine works on for this process. */
export type Hook = {
  readonly cwd: string
  readonly pluginRoot: string
  /** The engine's working copy, as last saved; written to disk by main after Codex has its answer. */
  saved?: LintState
}

const LINT_DIR = '.claude/lint'
const slash = (p: string) => p.replace(/\\/g, '/').replace(/\/+$/, '')

function fold(path: string): string {
  const out: string[] = []
  for (const part of path.split('/')) {
    if (part === '' || part === '.') continue
    if (part === '..' && out.length && out[out.length - 1] !== '..') out.pop()
    else out.push(part)
  }
  return out.join('/')
}

/** Runs a program. Never throws. On Windows a name that is a .cmd/.bat shim (npm CLIs) runs through cmd. */
export const nodeRunner: Runner<Hook> = {
  run(_h, argv, { cwd, timeoutMs = 120000, env }): Promise<RunResult> {
    return new Promise(resolve => {
      const start = (useShell: boolean) => {
        let out = ''
        let err = ''
        let done = false
        const finish = (r: RunResult) => {
          if (!done) {
            done = true
            resolve(r)
          }
        }
        let child
        try {
          child = useShell
            ? spawn(argv.map(a => (/[\s"&|<>^]/.test(a) ? `"${a.replace(/"/g, '""')}"` : a)).join(' '), { cwd, shell: true, windowsHide: true, env: { ...process.env, ...env } })
            : spawn(argv[0], argv.slice(1), { cwd, windowsHide: true, env: { ...process.env, ...env } })
        } catch (e) {
          return finish({ exitCode: -1, stdout: '', stderr: `無法執行：${(e as Error).message}` })
        }
        const timer = setTimeout(() => {
          child.kill()
          finish({ exitCode: -1, stdout: out, stderr: `${err}\n無法執行：逾時 ${timeoutMs} ms` })
        }, timeoutMs)
        child.stdout?.on('data', d => (out += d))
        child.stderr?.on('data', d => (err += d))
        child.on('error', (e: any) => {
          clearTimeout(timer)
          if (!useShell && e?.code === 'ENOENT' && process.platform === 'win32') {
            done = true
            start(true)
          } else finish({ exitCode: -1, stdout: out, stderr: `無法執行：${e?.message ?? e}` })
        })
        child.on('close', code => {
          clearTimeout(timer)
          finish({ exitCode: code ?? -1, stdout: out, stderr: err })
        })
      }
      start(false)
    })
  },
  async probe(_h, path): Promise<PathProbe> {
    try {
      if (!existsSync(path)) return { kind: 'missing' }
      const s = statSync(path)
      return s.isDirectory() ? { kind: 'dir', entries: readdirSync(path).length } : { kind: 'file' }
    } catch {
      return { kind: 'unreadable' }
    }
  },
  async read(_h, path) {
    try {
      return existsSync(path) ? readFileSync(path, 'utf8') : null
    } catch {
      return null
    }
  },
}

/**
 * Whether Codex trusts the project at `root` or a folder above it: a `[projects."<path>"]` table with
 * `trust_level = "trusted"` in `$CODEX_HOME/config.toml` (codex-rs core/src/config set_project_trust_level).
 * Paths compare case-insensitively with either slash. Unreadable: not trusted.
 */
export function codexTrusts(root: string): boolean {
  const home = slash(process.env.CODEX_HOME || `${homedir()}/.codex`)
  let text: string
  try {
    text = readFileSync(`${home}/config.toml`, 'utf8')
  } catch {
    return false
  }
  const want = slash(root).toLowerCase()
  let table: string | undefined
  for (const line of text.split(/\r?\n/)) {
    const head = /^\s*\[projects\.(?:'([^']*)'|"((?:[^"\\]|\\.)*)")\]\s*$/.exec(line)
    if (head) table = slash(head[1] ?? head[2].replace(/\\\\/g, '\\')).toLowerCase()
    else if (/^\s*\[/.test(line)) table = undefined
    else if (table && /^\s*trust_level\s*=\s*"trusted"/.test(line) && (want === table || want.startsWith(`${table}/`))) return true
  }
  return false
}

/** The root and `.claude/lint/` as hostConfig reads them on Claude Code; read once per process. */
export function nodeConfig(): ConfigSource<Hook> {
  let kept: Config | null | undefined
  async function top(h: Hook, at: string): Promise<string | undefined> {
    const r = await nodeRunner.run(h, ['git', 'rev-parse', '--show-toplevel'], { cwd: at, timeoutMs: 10000 })
    return r.exitCode === 0 ? slash(String(r.stdout).trim()) : undefined
  }
  async function rootOf(h: Hook): Promise<{ root: string; git: boolean } | undefined> {
    const cwd = slash(h.cwd)
    for (let dir = cwd; dir && dir.includes('/'); dir = dir.slice(0, dir.lastIndexOf('/'))) {
      if (existsSync(`${dir}/${LINT_DIR}`)) {
        const t = await top(h, dir)
        return { root: dir, git: !!t && t.toLowerCase() === dir.toLowerCase() }
      }
    }
    const t = await top(h, cwd)
    return t ? { root: t, git: true } : undefined
  }
  function scan(base: string, problems: Finding[]): Map<string, string> {
    const files = new Map<string, string>()
    const walk = (dir: string, key: string) => {
      for (const ent of readdirSync(dir, { withFileTypes: true })) {
        const k = key ? `${key}/${ent.name}` : ent.name
        if (ent.isDirectory()) {
          if (!ent.name.startsWith('.')) walk(`${dir}/${ent.name}`, k)
        } else if (ent.isFile() && /\.(toml|json)$/i.test(ent.name)) {
          try {
            files.set(k, readFileSync(`${dir}/${ent.name}`, 'utf8'))
          } catch (err) {
            problems.push({ id: ent.name, severity: 'warn', text: `設定讀不懂：${k}：${(err as Error).message}` })
          }
        }
      }
    }
    walk(base, '')
    return files
  }
  return {
    async load(h) {
      if (kept !== undefined) return kept
      const found = await rootOf(h)
      if (!found || !existsSync(`${found.root}/${LINT_DIR}`)) return (kept = null)
      const problems: Finding[] = []
      const r = configFromFiles(scan(`${found.root}/${LINT_DIR}`, problems), converterNamed)
      let sgconfig = fold(`${LINT_DIR}/${r.settings.sgconfig}`)
      if (sgconfig === '..' || sgconfig.startsWith('../')) {
        problems.push({ id: 'config.toml', severity: 'warn', text: `設定讀不懂：config.toml：[settings] sgconfig 指到專案外面（${r.settings.sgconfig}），改用預設的 sgconfig.yml` })
        sgconfig = `${LINT_DIR}/sgconfig.yml`
      }
      // A `run` check runs a program the project names: only where Codex itself trusts the project.
      let checks = r.checks
      const runs = checks.filter(c => c.action.kind === 'run')
      if (runs.length && !codexTrusts(found.root)) {
        checks = checks.filter(c => c.action.kind !== 'run')
        problems.push({ id: 'config.toml', severity: 'warn', text: `Codex 還沒信任這個專案，會執行程式的檢查先不跑：${runs.map(c => c.id).join('、')}` })
      }
      return (kept = { root: found.root, git: found.git, checks, problems: [...problems, ...r.problems], sgconfig })
    },
    reload() {
      kept = undefined
    },
    edited(_h, file) {
      const f = file.replace(/\\/g, '/')
      const own = f.startsWith(`${LINT_DIR}/`) && !f.slice(LINT_DIR.length + 1).split('/').some(s => s.startsWith('.'))
      if (own) kept = undefined
      return own
    },
  }
}

/** The engine saves synchronously and often; the process keeps the latest copy and main writes it once. */
export const hookState: StateStore<Hook> = {
  async load(h) {
    return h.saved
  },
  save(h, s) {
    h.saved = JSON.parse(JSON.stringify(s))
  },
}

/** No wait is armed: a wait firing inside a short hook process would take its deadline and may be cut off before
 *  its result is saved. Deadlines stay in LintState; main calls the engine's wake() inside the lock at every
 *  hook, so a due after:* runs at the next event. */
export const hookClock: Clock<Hook> = {
  async now() {
    return Date.now()
  },
  after() {},
}

export function codexPorts(): Ports<Hook> {
  return {
    config: nodeConfig(),
    runner: nodeRunner,
    state: hookState,
    view: { async show() {} },
    clock: hookClock,
    languageSetting: async () => undefined,
    whatNowSkill: h => `${h.pluginRoot}/skills/what-now/SKILL.md`,
    machine: runnerMachine<Hook>(nodeRunner),
    languages: LANGUAGES,
  }
}
