// The Codex hook: one process per hook event (hooks.json runs `node lint.mjs` in the turn's shell).
// Reads Codex's JSON on stdin, runs the engine under the session's lock, answers Codex on stdout once, then
// writes the state back. Every event Claude Code's adapter reads has its Codex counterpart here
// (.claude/think/codex-lint-adapter.md, the mapping table); cards have no surface on Codex and are dropped.
// Anything that goes wrong lets the act through (a failing mod never blocks the user's own step).

import { closeSync, openSync, readdirSync, readFileSync, readSync, statSync } from 'node:fs'
import { homedir } from 'node:os'
import { posix } from 'node:path'
import { createEngine, type DoneSkillEvent, type Lint, type Outcome, type PendingCall, type ToolCallEvent } from '../../engine'
import { segments, writesFiles } from '../../engine/shell'
import { patchOps } from './patch'
import { codexPorts, nodeRunner, type Hook } from './ports'
import { pruneOld, SessionFile, type Saved } from './store'

const LOCK_WAIT_MS = 5000
/** Codex clamps an Interrupt hook to 3 s (codex-rs hooks discovery.rs): wait less, so the hook answers before it. */
const INTERRUPT_LOCK_WAIT_MS = 1500

type Input = {
  hook_event_name?: string
  session_id?: string
  turn_id?: string
  transcript_path?: string | null
  cwd?: string
  source?: string
  prompt?: string
  agent_id?: string | null
  agent_type?: string | null
  tool_name?: string
  tool_input?: { command?: unknown }
  tool_use_id?: string
  tool_response?: unknown
  last_assistant_message?: string | null
}

const slash = (p: string) => p.replace(/\\/g, '/').replace(/\/+$/, '')
/** An absolute path with `.` and `..` folded: a patch path may be relative to the session's directory. */
const absolute = (p: string, cwd: string) => {
  const f = slash(p)
  return posix.normalize(/^([A-Za-z]:)?\//.test(f) ? f : `${cwd}/${f}`)
}
const quote = (p: string) => `'${p.replace(/'/g, `'\\''`)}'`
const context = (event: string, parts: readonly string[]) =>
  (parts.length ? { hookSpecificOutput: { hookEventName: event, additionalContext: parts.join('\n\n') } } : {})

/** Read-only commands, as Claude Code's host marks them: every segment only looks (a later hook counts no work). */
const LOOKS = new Set(['ls', 'dir', 'cat', 'type', 'head', 'tail', 'less', 'more', 'pwd', 'echo', 'wc', 'which', 'where', 'rg', 'grep',
  'get-childitem', 'gci', 'get-content', 'gc', 'get-location', 'select-string', 'sls', 'get-command', 'test-path', 'write-output', 'get-item'])
const GIT_LOOKS = new Set(['status', 'log', 'diff', 'show', 'rev-parse', 'ls-files', 'blame', 'describe', 'grep'])
function readOnly(command: string): boolean {
  if (writesFiles(command)) return false
  const segs = segments(command).map(s => s.trim()).filter(Boolean)
  return segs.length > 0 && segs.every(s => {
    const w = s.split(/\s+/)
    const prog = (w[0] ?? '').replace(/^.*[\\/]/, '').replace(/\.exe$/i, '').toLowerCase()
    if (prog === 'git') return GIT_LOOKS.has((w.find((x, i) => i > 0 && !x.startsWith('-')) ?? '').toLowerCase())
    return LOOKS.has(prog)
  })
}

function outcomeOf(i: Input): Outcome {
  const text = typeof i.tool_response === 'string' ? i.tool_response : JSON.stringify(i.tool_response ?? '')
  const code = /Exit code:\s*(-?\d+)/.exec(text)
  const command = typeof i.tool_input?.command === 'string' ? i.tool_input.command : ''
  return { ran: true, isError: !!code && code[1] !== '0', isReadOnly: i.tool_name === 'Bash' && readOnly(command), output: text }
}

/** The calls one PreToolUse makes. A patch: a write per file it writes; a delete or a move's source as the shell
 *  command Claude Code would have run for it, so the engine's delete checks and preview see it. */
function callsOf(i: Input, cwd: string): ToolCallEvent[] {
  const id = String(i.tool_use_id ?? '')
  const actor = i.agent_id ? { agent: String(i.agent_id) } : {}
  const command = typeof i.tool_input?.command === 'string' ? i.tool_input.command : ''
  const shell = (n: number, cmd: string, sh: 'sh' | 'ps'): ToolCallEvent => ({ ...actor, id: `${id}#${n}`, cwd, kind: 'shell', shell: sh, command: cmd, background: false })
  if (i.tool_name === 'apply_patch')
    return patchOps(command).map((op, n): ToolCallEvent =>
      op.kind === 'write' ? { ...actor, id: `${id}#${n}`, cwd, kind: 'edit', file: absolute(op.file, cwd), text: op.text }
      : op.kind === 'delete' ? shell(n, `rm ${quote(absolute(op.file, cwd))}`, 'sh')
      : shell(n, `mv ${quote(absolute(op.from, cwd))} ${quote(absolute(op.to, cwd))}`, 'sh'))
  if (i.tool_name === 'Bash') return [{ ...actor, id, cwd, kind: 'shell', shell: process.platform === 'win32' ? 'ps' : 'sh', command, background: false }]
  return []
}

// ---------------------------------------------------------------- skills

/** Claude Code's DONE_SKILLS (adapters/claude-code/translate.ts): the skills whose start reads a record. */
const DONE: Record<string, DoneSkillEvent['skill']> = { ship: 'ship', review: 'review', lint: 'lint' }
const skillEvent = (name: string, args: string): DoneSkillEvent =>
  ({ skill: DONE[name.replace(/^baransu:/, '')] ?? 'other', name, args })

/** The skills a prompt names as Codex writes them (`$baransu:lint help`), each with the rest of its line. */
function mentioned(prompt: string): DoneSkillEvent[] {
  const out: DoneSkillEvent[] = []
  for (const m of prompt.matchAll(/(?<![\w$])\$([A-Za-z][\w-]*(?::[\w-]+)?)([^\n]*)/g)) out.push(skillEvent(m[1], m[2].replace(/\$[A-Za-z][\w:-]*.*$/, '').trim()))
  return out
}
/** The skill a command reads the SKILL.md of: how the model loads a skill on its own. */
function readsSkill(command: string): DoneSkillEvent | undefined {
  const m = /[\\/]skills[\\/]([\w.-]+)[\\/]SKILL\.md\b/i.exec(command)
  return m ? skillEvent(m[1], '') : undefined
}

/** Run a skill's start once per turn (a typed $name and the model then reading its SKILL.md are one start). */
async function skillStart(lint: Lint<Hook>, saved: Saved, turn: string, e: DoneSkillEvent): Promise<string | undefined> {
  const key = e.name.replace(/^baransu:/, '')
  if (saved.skills?.turn !== turn) saved.skills = { turn, names: [] }
  if (saved.skills.names.includes(key)) return undefined
  saved.skills.names.push(key)
  return (await lint.skillPrompt(e))?.text
}

// ---------------------------------------------------------------- what the transcript says

/** A compaction's text for post:compact. Codex's own summary is encrypted (`message` is empty): what stays
 *  readable is the conversation it kept — the user's and the model's messages in `replacement_history`, not the
 *  developer ones (system text, which a check on the summary does not mean). */
function summaryOf(payload: any): string {
  if (typeof payload?.message === 'string' && payload.message.trim()) return payload.message
  const kept = Array.isArray(payload?.replacement_history) ? payload.replacement_history : []
  return kept
    .filter((m: any) => m?.type === 'message' && (m.role === 'user' || m.role === 'assistant'))
    .map((m: any) => (Array.isArray(m.content) ? m.content : []).map((c: any) => (typeof c?.text === 'string' ? c.text : '')).join('\n'))
    .filter((t: string) => t.trim())
    .join('\n\n')
    .slice(0, 200_000)
}

/**
 * What the model did since the last hook, read from the rollout transcript in order (reading D1): a new turn
 * (turn_context), the words it said (an assistant message: Claude Code's streamed text and its kept row), the
 * end of each model response (token_usage_record: turn.step), and a compaction's summary. Reads only new bytes.
 */
async function followTranscript(i: Input, lint: Lint<Hook>, saved: Saved): Promise<boolean> {
  const path = i.transcript_path
  if (!path) return false
  let fd: number
  try {
    fd = openSync(path, 'r')
  } catch {
    return false
  }
  let lines: string[]
  const reads = (saved.reads ??= {})
  try {
    const size = statSync(path).size
    const from = reads[path] !== undefined && reads[path] <= size ? reads[path] : 0
    const buf = Buffer.alloc(size - from)
    readSync(fd, buf, 0, buf.length, from)
    const end = buf.lastIndexOf(0x0a) + 1 // a line still being written waits for the next hook
    lines = buf.subarray(0, end).toString('utf8').split('\n')
    reads[path] = from + end
  } finally {
    closeSync(fd)
  }
  const actor = i.agent_id ? { agent: String(i.agent_id) } : {}
  for (const line of lines) {
    if (!line) continue
    let r: any
    try {
      r = JSON.parse(line)
    } catch {
      continue
    }
    if (r?.type === 'turn_context') {
      lint.turnStarted(actor)
      lint.stepBegan(actor)
    } else if (r?.type === 'token_usage_record') lint.stepBegan(actor)
    else if (r?.type === 'compacted') saved.summary = summaryOf(r.payload)
    else if (r?.type === 'response_item' && r.payload?.type === 'message' && r.payload?.role === 'assistant') {
      const text = (Array.isArray(r.payload.content) ? r.payload.content : []).map((c: any) => (typeof c?.text === 'string' ? c.text : '')).join('\n')
      if (!text.trim()) continue
      lint.textStreamed({ ...actor, text })
      await lint.replyAppended({ ...actor, text, visible: text })
    }
  }
  return true
}

// ---------------------------------------------------------------- files changed outside the model (post:file)

const MAX_SCAN = 5000
/** The files under `root` that may have changed, with their modified time, relative to `root`. In a git work tree
 *  (the root itself, or a folder inside one): what git lists as modified or new, paths relative to the root. In a
 *  plain folder: every file, skipping dot folders and node_modules, at most MAX_SCAN. */
async function changedFiles(h: Hook, root: string): Promise<Record<string, number>> {
  const out: Record<string, number> = {}
  const stamp = (file: string) => {
    try {
      out[file] = statSync(`${root}/${file}`).mtimeMs
    } catch {}
  }
  const r = await nodeRunner.run(h, ['git', 'ls-files', '--modified', '--others', '--exclude-standard', '-z'], { cwd: root, timeoutMs: 20000 })
  if (r.exitCode === 0) {
    for (const file of r.stdout.split('\0')) if (file) stamp(file)
    return out
  }
  let seen = 0
  const walk = (dir: string) => {
    let ents
    try {
      ents = readdirSync(`${root}/${dir}`, { withFileTypes: true })
    } catch {
      return
    }
    for (const ent of ents) {
      if (seen >= MAX_SCAN) return
      const rel = dir ? `${dir}/${ent.name}` : ent.name
      if (ent.isDirectory()) {
        if (!ent.name.startsWith('.') && ent.name !== 'node_modules') walk(rel)
      } else if (ent.isFile()) {
        seen++
        stamp(rel)
      }
    }
  }
  walk('')
  return out
}

/** Claude Code hears FileChanged as it happens; Codex looks at every hook: a file whose time moved since the last
 *  look changed. The first look only remembers. */
async function lookForChanges(h: Hook, lint: Lint<Hook>, saved: Saved) {
  const roots = await lint.watchPaths()
  if (!roots.length) return void (saved.files = undefined)
  const now = await changedFiles(h, roots[0])
  const before = saved.files
  saved.files = now
  if (!before) return
  for (const [file, t] of Object.entries(now)) if (before[file] !== t) await lint.fileChanged({ file, change: file in before ? 'change' : 'add' })
}

// ---------------------------------------------------------------- calls with no PostToolUse

/** Codex runs PostToolUse only for a call that succeeded: a failed patch, a refusal further on, a call the
 *  person declined leaves its before half waiting. Claude Code gives back what such a call took at once; here it
 *  is given back as soon as its actor is two responses further (one response's margin, since a call's
 *  PostToolUse may come after the response's token_usage_record). `only` limits it to one actor's calls. */
function reclaim(lint: Lint<Hook>, saved: Saved, hook: Hook, all: boolean, only?: (p: PendingCall) => boolean) {
  const steps = hook.saved?.steps ?? {}
  for (const [key, ps] of Object.entries(saved.pending)) {
    const gone = ps.filter(p => (!only || only(p)) && (all || (steps[p.e.agent ?? 'main'] ?? 0) - p.at.step >= 2))
    if (!gone.length) continue
    for (const p of gone) lint.toolAbandoned(p)
    const left = ps.filter(p => !gone.includes(p))
    if (left.length) saved.pending[key] = left
    else delete saved.pending[key]
  }
}
const mainLoop = (p: PendingCall) => !p.e.agent

// ---------------------------------------------------------------- the events

/** What a compaction carried, said to the conversation after it: the engine's list, without its line asking the
 *  summary to keep it (an item may span lines). */
const carried = (carry: string) => `壓縮前還沒做完的要求（baransu lint），照做：\n${carry.slice(carry.indexOf('\n- ') + 1)}`

async function systemNotes(lint: Lint<Hook>): Promise<string> {
  return (await lint.systemNotes()).map(n => n.text).join('\n\n')
}

async function handle(i: Input, lint: Lint<Hook>, saved: Saved, hook: Hook, cwd: string, turn: string): Promise<object> {
  switch (i.hook_event_name) {
    case 'SessionStart': {
      const parts: string[] = []
      if (i.source === 'clear') lint.cleared()
      if (i.source !== 'compact') await lint.sessionStarted()
      // Claude Code's prompt.compose: in the system prompt from the start, and again after a compaction.
      saved.notes = await systemNotes(lint)
      if (saved.notes) parts.push(saved.notes)
      if (i.source === 'compact') {
        if (saved.carry) parts.push(carried(saved.carry))
        saved.carry = undefined
        // The compaction happened, and what it carried is told now: its after half.
        if (saved.compact) {
          const p = saved.compact
          saved.compact = undefined
          await lint.compactAfter(p, saved.summary ?? '')
        }
      }
      return context('SessionStart', parts)
    }
    case 'UserPromptSubmit': {
      // A subagent's task message is not the person's: Claude Code's prompt.submit is only what the person typed.
      if (i.agent_id) return {}
      const prompt = String(i.prompt ?? '')
      const parts: string[] = []
      const said: string[] = []
      if (prompt.trim()) {
        // What the person typed: Codex writes a mentioned skill as a link, `[$baransu:lint](C:\…\SKILL.md)`; a link
        // keeps only its text, so a path's letters are not read as the person's language.
        const typed = prompt.replace(/\[([^\]\n]*)\]\([^)\n]*\)/g, ' $1 ').replace(/(?<![\w$])\$[A-Za-z][\w:-]*/g, ' ')
        await lint.promptSubmit({ typed, opensTurnNow: true }, async n => void said.push(...n), () => false)
      }
      // prompt.compose is built after the prompt went in (its language guess counts) and read again each time:
      // a check added mid-session counts from the next prompt. Said only when it changed.
      const notes = await systemNotes(lint)
      if (notes && notes !== saved.notes) parts.push(notes)
      saved.notes = notes
      parts.push(...said)
      for (const e of mentioned(prompt)) {
        const preface = await skillStart(lint, saved, turn, e)
        if (preface) parts.push(preface)
      }
      return context('UserPromptSubmit', parts)
    }
    case 'PreToolUse': {
      const goes: PendingCall[] = []
      const denied: string[] = []
      try {
        for (const e of callsOf(i, cwd)) {
          const r = await lint.toolBefore(e)
          if (r.kind === 'deny') denied.push(r.reason)
          else goes.push(r.pending)
        }
      } catch (err) {
        // The first call took what was owed; a later one failing must not strand it.
        for (const p of goes) lint.toolAbandoned(p)
        throw err
      }
      if (denied.length) {
        // The parts that passed carry their notes on the refusal, as the engine's own refusal does.
        const carried = goes.flatMap(p => lint.toolRefused(p))
        return { hookSpecificOutput: { hookEventName: 'PreToolUse', permissionDecision: 'deny', permissionDecisionReason: [...denied, ...carried].join('\n\n') } }
      }
      if (goes.length) saved.pending[String(i.tool_use_id ?? '')] = goes
      return {}
    }
    case 'PostToolUse': {
      const key = String(i.tool_use_id ?? '')
      const ps = saved.pending[key] ?? []
      delete saved.pending[key]
      const o = outcomeOf(i)
      const notes: string[] = []
      for (const p of ps) notes.push(...(await lint.toolAfter(p, o)))
      // The model loaded a skill by reading its SKILL.md: its start, as Claude Code's skill.prompt.
      const command = typeof i.tool_input?.command === 'string' ? i.tool_input.command : ''
      const skill = i.tool_name === 'Bash' && !i.agent_id && !o.isError ? readsSkill(command) : undefined
      if (skill) {
        const preface = await skillStart(lint, saved, turn, skill)
        if (preface) notes.push(preface)
      }
      return context('PostToolUse', notes)
    }
    case 'Stop': {
      // Every call of the main loop's turn is over by now: a before half still waiting got no PostToolUse. A
      // subagent may still be running its own.
      reclaim(lint, saved, hook, true, mainLoop)
      // A compaction with no PostCompact: told already (SessionStart) → it happened; else it did not.
      if (saved.compact) {
        if (saved.carry) lint.compactAbandoned(saved.compact)
        else await lint.compactAfter(saved.compact, saved.summary ?? '')
        saved.compact = saved.carry = undefined
      }
      const v = await lint.stopping({ text: String(i.last_assistant_message ?? '') })
      if (v.kind === 'hold') return { decision: 'block', reason: v.reason }
      await lint.turnCompleted({ answered: true })
      return {}
    }
    case 'Interrupt': {
      // The person stopped the turn (Codex runs Interrupt, not Stop): Claude Code's turn.complete with no answer —
      // a /review it ran does not count; calls still waiting get no PostToolUse.
      reclaim(lint, saved, hook, true, mainLoop)
      await lint.turnCompleted({ answered: false })
      return {}
    }
    case 'SubagentStart':
      await lint.agentStarted({ agent: String(i.agent_id ?? ''), agentType: String(i.agent_type ?? '') })
      return {}
    case 'SubagentStop':
      await lint.agentStopped({ agent: String(i.agent_id ?? ''), agentType: String(i.agent_type ?? ''), text: String(i.last_assistant_message ?? '') })
      return {}
    case 'PreCompact': {
      // The main conversation's compaction only, as Claude Code (a subagent's own carries agent_id).
      if (i.agent_id) return {}
      if (saved.compact) lint.compactAbandoned(saved.compact)
      saved.compact = await lint.compactBefore({ instructions: '' })
      saved.carry = saved.compact.carry || undefined
      saved.summary = undefined
      return {}
    }
    case 'PostCompact': {
      // What it carries is still to be told (SessionStart compact comes later): that start finishes it.
      if (i.agent_id || !saved.compact || saved.carry) return {}
      const p = saved.compact
      saved.compact = undefined
      await lint.compactAfter(p, saved.summary ?? '')
      return {}
    }
    default:
      return {}
  }
}

let answered = false
/** Codex reads exactly one JSON object from stdout (codex-rs/hooks output_parser): answer once. */
function answer(v: object) {
  if (answered) return
  answered = true
  process.stdout.write(JSON.stringify(v))
}

async function main() {
  let input: Input
  try {
    input = JSON.parse(readFileSync(0, 'utf8'))
  } catch {
    return answer({})
  }
  const cwd = slash(String(input.cwd ?? process.cwd()))
  const hook: Hook = { cwd, pluginRoot: slash(process.env.PLUGIN_ROOT ?? '') }
  const ports = codexPorts()
  // No .claude/lint/ here: nothing to check, no lock, no state.
  if (!(await ports.config.load(hook).catch(() => null))) return answer({})
  const data = slash(process.env.PLUGIN_DATA || `${homedir()}/.codex/plugins/data/baransu`)
  const file = new SessionFile(`${data}/lint`, String(input.session_id ?? 'none'))
  if (input.hook_event_name === 'SessionStart' && input.source === 'startup') pruneOld(`${data}/lint`)
  if (!(await file.lock(input.hook_event_name === 'Interrupt' ? INTERRUPT_LOCK_WAIT_MS : LOCK_WAIT_MS))) return answer({})
  try {
    const saved = file.read()
    if (saved.lint) hook.saved = saved.lint
    let reply: object = {}
    try {
      const lint = await createEngine(ports).ready(hook)
      const turn = String(input.turn_id ?? saved.turn ?? '')
      // Without a readable transcript, a new turn_id is the only sign of a new turn.
      if (!(await followTranscript(input, lint, saved)) && input.turn_id && input.turn_id !== saved.turn) lint.turnStarted({})
      if (input.turn_id) saved.turn = input.turn_id
      // What happened between hooks reaches the model with this event, as on Claude Code with its next step.
      reclaim(lint, saved, hook, false)
      await lookForChanges(hook, lint, saved)
      await lint.wake()
      reply = await handle(input, lint, saved, hook, cwd, turn)
    } catch (err) {
      // The act goes through; BARANSU_LINT_DEBUG shows why the mod failed (Codex keeps a hook's stderr).
      if (process.env.BARANSU_LINT_DEBUG) process.stderr.write(String((err as Error)?.stack ?? err))
      reply = {}
    }
    // A waiter took the lock away (this process looked dead): answer as a dead hook does and leave the state
    // to the new holder (the model's WriteGuard; it hands nothing over twice and overwrites nothing).
    if (!file.owns()) return answer({})
    // Codex has its answer before the state is written: a kill in between re-sends, never loses (reading D2).
    answer(reply)
    if (hook.saved) saved.lint = hook.saved
    try {
      if (file.owns()) file.write(saved)
    } catch {}
  } finally {
    file.unlock()
  }
}

main().catch(() => answer({}))
