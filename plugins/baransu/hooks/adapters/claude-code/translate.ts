// Host events → engine events, engine verdicts → host results. Pure functions of their arguments: no `$`,
// no await, no state. This file is where "the engine never heard the model speak" gets tested on its own
// (constraint 7): feed it the exact host shapes, assert the engine event that comes out.

import type { Args, TurnStepChunk } from 'claude-code'
import type {
  Actor, DoneSkillEvent, Outcome, PromptEvent, ReplyEvent, SpokenEvent, ToolCallEvent, ToolVerdict, TurnEndEvent, TurnStartEvent,
} from '../../engine'

const EDIT_TOOLS = new Set(['Edit', 'Write', 'MultiEdit', 'NotebookEdit'])
const SHELL_TOOLS = new Set(['Bash', 'PowerShell'])
const DONE_SKILLS: Record<string, DoneSkillEvent['skill']> = { ship: 'ship', 'baransu:ship': 'ship', review: 'review', 'baransu:review': 'review', lint: 'lint', 'baransu:lint': 'lint' }

export const actorOf = (e: { agentId?: string }): Actor => (e.agentId ? { agent: e.agentId } : {})

/** Whether lint looks at this tool at all (an edit tool or a shell). The hook asks this first and hands every
 *  other tool on before it awaits anything — as today, a Read or Grep touches no `$`. */
export const isLintTool = (e: Args<'tool.call'>): boolean => EDIT_TOOLS.has(e.tool) || SHELL_TOOLS.has(e.tool)

/** null for every tool lint does not look at (Read, Grep, MCP tools …): the hook hands those on untouched.
 *  `cwd` is `$.session.cwd()` read in the hook, normalized here (forward slashes, no trailing slash); '' when
 *  it could not be read, which the engine turns into the project root (ToolCallEvent.cwd). */
export function toolEvent(e: Args<'tool.call'>, cwd: string): ToolCallEvent | null {
  const a = e as any
  const base = { id: a.tool_use_id, ...actorOf(a), cwd: String(cwd).replace(/\\/g, '/').replace(/\/$/, '') }
  if (EDIT_TOOLS.has(a.tool)) return { ...base, kind: 'edit', file: String(a.file_path ?? a.notebook_path ?? '') }
  if (SHELL_TOOLS.has(a.tool)) return { ...base, kind: 'shell', shell: a.tool === 'PowerShell' ? 'ps' : 'sh', command: String(a.command ?? ''), background: !!a.run_in_background }
  return null
}

/** How the host's own handling ended, read off its result. A `deny` from below: not ran. */
export function outcomeOf(r: any): Outcome {
  return { ran: !!r && !r.deny, isError: r?.isError === true, isReadOnly: r?.isReadOnly === true }
}

/** The verdict as the hook's return: a refusal, or the host's result with the notes appended to its context. */
export function toolResult<R extends { context?: readonly string[] }>(v: ToolVerdict<R>): R | { deny: string } {
  if (v.kind === 'deny') return { deny: v.reason }
  return v.notes.length ? { ...v.result, context: [...(v.result.context ?? []), ...v.notes] } : v.result
}

/** null for a meta prompt or empty text. `typed` drops tags and a leading /command; a slash command reaches
 *  the model now only when typed into a running turn (`e.turnId`). */
export function promptEvent(e: Args<'prompt.submit'>): PromptEvent | null {
  const a = e as any
  if (a.isMeta || !String(a.text ?? '').trim()) return null
  const typed = String(a.text)
    .replace(/<([a-z][\w-]*)\b[^>]*>[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[a-z][\w-]*\b[^>]*\/>/gi, ' ')
    .replace(/^\s*\/\S+/, ' ')
  return { typed, opensTurnNow: !a.command || !!a.turnId }
}
export const withContext = (e: Args<'prompt.submit'>, notes: readonly string[]): Args<'prompt.submit'> =>
  (notes.length ? { ...e, context: [...((e as any).context ?? []), ...notes] } : e)
export const droppedPrompt = (r: any): boolean => !!r && 'drop' in r && !!r.drop

/**
 * A piece of a model response the person sees: a text chunk, or a thinking chunk that carries text. On
 * Claude Opus 5.5 the words between tool calls stream as thinking blocks and are shown; hidden reasoning
 * streams as thinking with empty text (HUNT-2026-001). null for empty thinking and every other kind. The
 * subagent is carried, not filtered: whether a subagent's words count is the engine's rule.
 */
export function streamedText(e: Pick<Args<'turn.step'>, 'turnId' | 'index'> & { agentId?: string }, chunk: TurnStepChunk | unknown): SpokenEvent | null {
  const c = chunk as any
  if (c?.kind !== 'text' && !(c?.kind === 'thinking' && c.text)) return null
  return { ...actorOf(e), text: String(c.text ?? '') }
}

/** An assistant row's text blocks, joined. null for user, attachment and system rows. */
export function appendedReply(e: Args<'session.append'>): ReplyEvent | null {
  const a = e as any
  if (a.message?.type !== 'assistant' || !Array.isArray(a.message.content)) return null
  const text = (a.message.content as any[]).filter(b => b.type === 'text').map(b => String(b.text)).join('\n')
  return { ...actorOf(a), text }
}

export const turnStartEvent = (e: Args<'turn.start'>): TurnStartEvent => ({ ...actorOf(e as any), text: (e as any).text })
export const turnEndEvent = (e: Args<'turn.complete'>): TurnEndEvent => ({ ...actorOf(e as any), answered: (e as any).reason === 'answer' })
export const skillEvent = (e: Args<'skill.prompt'>): DoneSkillEvent | null => {
  const name = (e as any).skill
  if (typeof name !== 'string' || !name) return null
  return { skill: Object.hasOwn(DONE_SKILLS, name) ? DONE_SKILLS[name] : 'other', name }
}

/** Pass each chunk on unchanged, calling `see` on the way, and return the generator's own return value. */
export async function* tap<T, R>(source: AsyncIterable<T> & AsyncIterator<T, R>, see: (chunk: T) => void): AsyncGenerator<T, R> {
  // manual iteration as lintTurnStep does today, so the return value is kept
  const it = source[Symbol.asyncIterator]()
  for (;;) {
    const { value, done } = await it.next()
    if (done) return value as R
    see(value as T)
    yield value as T
  }
}

export { EDIT_TOOLS, SHELL_TOOLS }
