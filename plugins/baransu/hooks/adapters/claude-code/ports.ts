// The outbound ports, implemented on Claude Code's `$`. Each is a thin translation; none decides anything.

import type { Clock, LintState, PathProbe, Runner, RunResult, StateStore } from '../../engine'

/** The dispatch's `$`. Typed loosely, as 8.39's lint.ts did. Only this adapter's own functions take it. */
export type Dollar = any

/**
 * The engine's `H` on Claude Code: one dispatch's `$`, reached through closures. The host loads a hooks module
 * only when `$` itself is never handed to a method call (it is spelled `$.noun.event(...)` at every call site,
 * or passed to a plain function of the module), so the engine cannot carry `$` as an opaque value into
 * `ports.x.y(h, …)`. `hostOf($)` closes over the dispatch's `$` instead: every port call still reaches that
 * dispatch, and the engine still never looks inside `H`.
 */
export type Host = {
  readonly stateGet: () => Promise<any>
  readonly stateSet: (value: unknown) => unknown
  readonly run: (argv: readonly string[], opts?: { cwd: string; timeoutMs: number; env?: Readonly<Record<string, string>> }) => Promise<any>
  readonly exists: (path: string) => Promise<any>
  readonly stat: (path: string) => Promise<any>
  readonly list: (path: string) => Promise<any>
  readonly read: (path: string) => Promise<any>
  readonly now: () => Promise<number>
  readonly after: (ms: number, fn: () => void) => unknown
  readonly cwd: () => Promise<any>
  readonly append: (text: string) => Promise<any>
  /** Claude Code's `language` setting, merged over every settings source; undefined when none sets it. */
  readonly language: () => Promise<string | undefined>
  /** Asks the host to draw this plugin's rows and band again, so a card kept just now shows. */
  readonly invalidate: () => void
  readonly pluginRoot: () => string
}

const STATE_REF = { plugin: 'baransu', key: 'lint' } as const

/** The handle for one dispatch. Build it inside the hook, from that hook's own `$`; never keep it past the dispatch. */
export function hostOf($: Dollar): Host {
  return {
    stateGet: () => $.state.get(STATE_REF),
    stateSet: value => $.state.set(STATE_REF, value),
    run: (argv, opts) => (opts ? $.process.run(argv, opts) : $.process.run(argv)),
    exists: path => $.fs.exists(path),
    stat: path => $.fs.stat(path),
    list: path => $.fs.list(path),
    read: path => $.fs.read(path),
    now: () => $.clock.now(),
    after: (ms, fn) => $.clock.after(ms, fn),
    cwd: () => $.session.cwd(),
    append: text => $.session.append({ message: { type: 'system', content: [{ type: 'text', text }] } }),
    language: async () => {
      const v = await $.settings.read({ key: 'language' })
      return typeof v === 'string' && v.trim() ? v.trim() : undefined
    },
    invalidate: () => $.ui.invalidate('ui.render'),
    pluginRoot: () => String($.plugin.root),
  }
}

/**
 * `$.state` under baransu/lint (declared in types/index.d.ts as PluginState.baransu.lint = LintState).
 * save: copies synchronously (JSON round trip) and issues `$.state.set` with this dispatch's `$` before it
 * returns, every time — as today's persist does. Never deferred, never queued behind an earlier write, never
 * sent with another dispatch's `$`: a write that has not left when the module reloads would be lost, and the
 * new engine would read the state from before the take (R1, R2). A failure is swallowed.
 * That the host applies two writes in the order they were issued is a premise (as today), not something
 * this port enforces: `ifVersion` cannot order writes issued side by side (all but the first would miss).
 */
export const hostState: StateStore<Host> = {
  async load(h) {
    try {
      return (await h.stateGet())?.value as LintState | undefined
    } catch {
      return undefined
    }
  },
  save(h, s) {
    try {
      Promise.resolve(h.stateSet(JSON.parse(JSON.stringify(s)))).catch(() => {})
    } catch {}
  },
}

/** `$.process.run` and `$.fs`. */
export const hostRunner: Runner<Host> = {
  async run(h, argv, { cwd, timeoutMs = 120000, env }): Promise<RunResult> {
    try {
      return await h.run(argv, { cwd, timeoutMs, ...(env ? { env } : {}) })
    } catch (err) {
      return { exitCode: -1, stdout: '', stderr: `無法執行：${(err as Error).message}` }
    }
  },
  async probe(h, path): Promise<PathProbe> {
    try {
      if (!(await h.exists(path))) return { kind: 'missing' }
      const s = await h.stat(path)
      if (s.kind === 'dir') return { kind: 'dir', entries: (await h.list(path)).length }
      return { kind: 'file' }
    } catch {
      return { kind: 'unreadable' }
    }
  },
  async read(h, path) {
    try {
      if (!(await h.exists(path))) return null
      const r = await h.read(path)
      return typeof r === 'string' ? r : typeof r?.text === 'string' ? r.text : null
    } catch {
      return null
    }
  },
}

/** `$.clock`. A wait armed with one dispatch's `$` runs its callback in the mod's environment; a reload
 *  cancels it (the engine re-arms from LintState). A failure to arm is swallowed: the deadline stays stored. */
export const hostClock: Clock<Host> = {
  async now(h) {
    try {
      return Number(await h.now())
    } catch {
      return Date.now()
    }
  },
  after(h, ms, fn) {
    try {
      h.after(ms, () => {
        try {
          fn()
        } catch {}
      })
    } catch {}
  },
}

export const whatNowSkill = (h: Host): string => `${h.pluginRoot()}/skills/what-now/SKILL.md`
