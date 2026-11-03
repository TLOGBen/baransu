// The outbound ports, implemented on Claude Code's `$`. Each is a thin translation; none decides anything.

import type { LintState, Notify, PathProbe, Runner, RunResult, StateStore } from '../../engine'

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
  readonly run: (argv: readonly string[], opts?: { cwd: string; timeoutMs: number }) => Promise<any>
  readonly exists: (path: string) => Promise<any>
  readonly stat: (path: string) => Promise<any>
  readonly list: (path: string) => Promise<any>
  readonly read: (path: string) => Promise<any>
  readonly cwd: () => Promise<any>
  readonly append: (text: string) => Promise<any>
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
    cwd: () => $.session.cwd(),
    append: text => $.session.append({ message: { type: 'system', content: [{ type: 'text', text }] } }),
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
  async run(h, argv, { cwd, timeoutMs = 120000 }): Promise<RunResult> {
    try {
      return await h.run(argv, { cwd, timeoutMs })
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
}

/** A system row in the session. */
export const hostNotify: Notify<Host> = {
  async notice(h, text) {
    try {
      await h.append(text)
    } catch {}
  },
}

export const whatNowSkill = (h: Host): string => `${h.pluginRoot()}/skills/what-now/SKILL.md`
