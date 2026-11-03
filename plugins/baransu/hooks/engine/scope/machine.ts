// The Machine port read through the Runner: one process per question, kept for the module load. A host that
// can answer directly may implement Machine itself; one that cannot read an arbitrary variable or its platform
// uses this (adapters/claude-code/machine.ts says why it does).
//
// os: `cmd /c ver` exits 0 only on Windows; else `uname -s` (Darwin → mac, Linux → linux).
// env: the whole environment once — `cmd /c set` on Windows, `env` elsewhere — parsed NAME=VALUE.
// onPath: `where.exe <name>` on Windows, else `sh -c 'command -v "$1"' _ <name>`; memoised per name.
// Facts do not change within a session; a reload reads again. Installing a tool mid-session needs a reload.

import type { Machine, Runner } from '../ports'

export function runnerMachine<H>(runner: Runner<H>): Machine<H> {
  let os: Promise<'windows' | 'linux' | 'mac' | undefined> | undefined
  let env: Promise<Map<string, string> | undefined> | undefined
  const onPath = new Map<string, Promise<boolean | undefined>>()
  const run = (h: H, argv: readonly string[]) => runner.run(h, argv, { cwd: '.', timeoutMs: 15000 })

  const osOf = (h: H) =>
    (os ??= (async () => {
      if ((await run(h, ['cmd', '/c', 'ver'])).exitCode === 0) return 'windows' as const
      const u = await run(h, ['uname', '-s'])
      if (u.exitCode !== 0) return undefined
      const s = String(u.stdout).trim().toLowerCase()
      return s.startsWith('darwin') ? ('mac' as const) : s.startsWith('linux') ? ('linux' as const) : undefined
    })())

  return {
    os: osOf,
    async env(h, name) {
      env ??= (async () => {
        const kind = await osOf(h)
        const r = await run(h, kind === 'windows' ? ['cmd', '/c', 'set'] : ['env'])
        if (r.exitCode !== 0) return undefined
        const m = new Map<string, string>()
        for (const line of String(r.stdout).split(/\r?\n/)) {
          const eq = line.indexOf('=')
          if (eq > 0) m.set(kind === 'windows' ? line.slice(0, eq).toUpperCase() : line.slice(0, eq), line.slice(eq + 1))
        }
        return m
      })()
      const all = await env
      if (!all) return undefined
      return all.get((await osOf(h)) === 'windows' ? name.toUpperCase() : name)
    },
    onPath(h, command) {
      let p = onPath.get(command)
      if (!p) {
        p = (async () => {
          const r = (await osOf(h)) === 'windows'
            ? await run(h, ['where.exe', command])
            : await run(h, ['sh', '-c', 'command -v "$1"', '_', command])
          return r.exitCode === -1 ? undefined : r.exitCode === 0
        })()
        onPath.set(command, p)
      }
      return p
    },
  }
}
