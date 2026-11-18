// The Codex hook's state on disk: one file per session under PLUGIN_DATA, guarded by a lock file.
// Rules (.claude/hypothesis/codex-lint-state, LockMode "code"): one holder at a time (C1); a dead or stalled holder's lock is reclaimed (C6);
// the answer goes to Codex before the state is written back (reading D2); a hook that cannot get the lock lets
// the act through (C5).

import { linkSync, mkdirSync, readdirSync, readFileSync, renameSync, statSync, unlinkSync, utimesSync, writeFileSync } from 'node:fs'
import type { LintState, PendingCall, PendingCompact } from '../../engine'

/** A holder touches its lock every BEAT_MS while it holds it, so a lock untouched this long belongs to a holder
 *  that is dead or stalled, whatever its pid says (Windows reuses pids; Codex's timeout kills the shell, not
 *  always the node under it). The model's LockMode "code": a stalled holder is declared dead (owns() turns false). */
const MAX_HOLD_MS = 150_000
const BEAT_MS = 10_000
/** A reaper holds its own lock for a few file operations; older means it died there. */
const MAX_REAP_MS = 10_000

/** What one session keeps between hook processes. */
export type Saved = {
  lint?: LintState
  /** The before halves waiting for their PostToolUse, by tool_use_id (a patch: one per file it touches). */
  pending: Record<string, PendingCall[]>
  /** The turn the last hook ran in. */
  turn?: string
  /** How far each rollout transcript has been read (bytes), by path: a subagent's hooks may name its own. */
  reads?: Record<string, number>
  /** The system notes as last given to the model (SessionStart, or a prompt after they changed). */
  notes?: string
  /** A compaction's before half, waiting for PostCompact. */
  compact?: PendingCompact
  /** What that compaction carries, until SessionStart (compact) tells it to the model. */
  carry?: string
  /** The last compaction's summary, read from the transcript. */
  summary?: string
  /** The skills already run this turn ($name typed, or a SKILL.md read): each runs once. */
  skills?: { turn: string; names: string[] }
  /** post:file: the modified time of each file git reports changed or new, at the last hook. */
  files?: Record<string, number>
}

/** Session files untouched this long belong to sessions no one resumes; their leftovers go at a session's start. */
const KEEP_MS = 14 * 24 * 3600_000

/** Remove other sessions' state older than KEEP_MS and temp files older than a day. Never throws. */
export function pruneOld(dir: string) {
  const now = Date.now()
  let names: string[]
  try {
    names = readdirSync(dir)
  } catch {
    return
  }
  for (const n of names) {
    const age = (() => {
      try {
        return now - statSync(`${dir}/${n}`).mtimeMs
      } catch {
        return 0
      }
    })()
    if (n.endsWith('.json') && age > KEEP_MS && !names.includes(`${n.slice(0, -5)}.lock`)) tryUnlink(`${dir}/${n}`)
    else if (/\.\d+(\.\w+)?\.tmp$|\.lock\.\d+\.\w+$/.test(n) && age > 24 * 3600_000) tryUnlink(`${dir}/${n}`)
  }
}

export class SessionFile {
  readonly #path: string
  readonly #lock: string
  readonly #token = `${process.pid}:${Math.random().toString(36).slice(2)}`
  #held = false
  #beat: ReturnType<typeof setInterval> | undefined

  constructor(dir: string, session: string) {
    mkdirSync(dir, { recursive: true })
    const safe = session.replace(/[^\w.-]/g, '_') || 'none'
    this.#path = `${dir}/${safe}.json`
    this.#lock = `${dir}/${safe}.lock`
  }

  /** Take the lock: true when held. Behind a live holder, give up after `waitMs` (the caller lets the act through). */
  async lock(waitMs: number): Promise<boolean> {
    const until = Date.now() + waitMs
    for (;;) {
      if (this.#create(this.#lock)) {
        // The heartbeat: a live holder's lock never looks stale, however long its checks run.
        this.#beat = setInterval(() => {
          if (this.owns()) {
            const now = new Date()
            try {
              utimesSync(this.#lock, now, now)
            } catch {}
          }
        }, BEAT_MS)
        this.#beat.unref()
        return (this.#held = true)
      }
      if (this.#stale(this.#lock, MAX_HOLD_MS)) this.#reap()
      else if (Date.now() >= until) return false
      else await new Promise(r => setTimeout(r, 25))
    }
  }

  /** The lock is still this process's own: false once a waiter took it away (this holder looked dead). A process
   *  that lost it neither answers with what it computed nor writes back (the model's WriteGuard). */
  owns(): boolean {
    return this.#held && readText(this.#lock) === this.#token
  }

  unlock() {
    if (this.#beat) clearInterval(this.#beat)
    if (!this.#held) return
    this.#held = false
    // Only our own lock: a reaper may have taken a lock we held too long, and another hook may hold it now.
    if (readText(this.#lock) === this.#token) tryUnlink(this.#lock)
  }

  read(): Saved {
    try {
      return { pending: {}, ...JSON.parse(readFileSync(this.#path, 'utf8')) }
    } catch {
      return { pending: {} }
    }
  }

  /** Atomic replace: a reader sees the old file or the new one. */
  write(v: Saved) {
    const tmp = `${this.#path}.${process.pid}.tmp`
    writeFileSync(tmp, JSON.stringify(v))
    renameSync(tmp, this.#path)
  }

  /** Create `path` holding our token in one step: the file never exists empty. */
  #create(path: string): boolean {
    const tmp = `${path}.${process.pid}.${Math.random().toString(36).slice(2)}`
    try {
      writeFileSync(tmp, this.#token)
      linkSync(tmp, path)
      return true
    } catch {
      // EEXIST, or a lock being deleted (Windows: EPERM): someone holds it; retry.
      return false
    } finally {
      tryUnlink(tmp)
    }
  }

  /** A lock whose holder is dead, or older than any live holder keeps it. */
  #stale(path: string, maxAge: number): boolean {
    let age: number
    try {
      age = Date.now() - statSync(path).mtimeMs
    } catch {
      return false
    }
    if (age > maxAge) return true
    const pid = Number(readText(path).split(':')[0])
    return Number.isInteger(pid) && pid > 0 && !alive(pid)
  }

  /** Remove a stale lock, under the reaper's own lock so two waiters never remove each other's fresh lock:
   *  while the stale lock exists no one can create a new one, so the check and the removal see the same file. */
  #reap() {
    const reap = `${this.#lock}.reap`
    if (!this.#create(reap)) {
      if (this.#stale(reap, MAX_REAP_MS)) tryUnlink(reap)
      return
    }
    try {
      if (this.#stale(this.#lock, MAX_HOLD_MS)) tryUnlink(this.#lock)
    } finally {
      if (readText(reap) === this.#token) tryUnlink(reap)
    }
  }
}

function readText(path: string): string {
  try {
    return readFileSync(path, 'utf8')
  } catch {
    return ''
  }
}

function tryUnlink(path: string) {
  try {
    unlinkSync(path)
  } catch {}
}

function alive(pid: number): boolean {
  try {
    process.kill(pid, 0)
    return true
  } catch (err: any) {
    return err?.code === 'EPERM'
  }
}
