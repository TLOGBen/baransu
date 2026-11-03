// The Claude Code adapter's hooks. Each hook: translate the host event, call the engine, translate back.
// No rule lives here. The one engine of this module load is built below, at module scope, so every
// dispatch shares its memory; a reload builds a new one, which reads `$.state` back.
//
// Constraint 3, in one place each: no `.claude/lint/` → the engine's ConfigSource answers null and the engine
// hands the call on (it still counts edits, as today); every gating hook carries `.catch(… next(e))`.
//
// The engine's `H` is `hostOf($)`, built in each hook from that hook's `$` (ports.ts says why it is not `$`).

import type { Register } from 'claude-code'
import { createEngine } from '../../engine'
import { drawCard } from './card'
import { hostConfig } from './config'
import { hostNotify, hostOf, hostRunner, hostState, whatNowSkill, type Dollar, type Host } from './ports'
import {
  actorOf, appendedReply, droppedPrompt, isLintTool, outcomeOf, promptEvent, skillEvent, streamedText, tap, toolEvent,
  toolResult, turnEndEvent, turnStartEvent, withContext,
} from './translate'

const engine = createEngine<Host>({ config: hostConfig(), runner: hostRunner, state: hostState, notify: hostNotify, whatNowSkill })

/** `$.session.cwd()`, the actor's own shell directory, read inside the hook. '' when it cannot be read. */
async function cwdOf($: Dollar): Promise<string> {
  try { return String(await $.session.cwd()) } catch { return '' }
}

/** turn.step's body. main.ts owns the literal generator and delegates here (constraint 2). */
export async function* lintTurnStep($: any, e: any, next: any): any {
  const lint = await engine.ready(hostOf($))
  lint.stepBegan(actorOf(e))
  return yield* tap(next(e), chunk => {
    const said = streamedText(e, chunk)
    if (said) lint.textStreamed(said)
  })
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await (await engine.ready(hostOf($))).sessionStarted()
    return result
  })

  on('prompt.compose', async ($, e, next) => {
    const result = await next(e)
    const add = (await engine.ready(hostOf($))).systemNotes().map(n => ({ ...n, scope: 'session' as const }))
    return add.length ? { ...result, sections: [...result.sections, ...add] } : result
  })

  on('prompt.submit', async ($, e, next) => {
    const ev = promptEvent(e)
    if (!ev) return next(e)
    const lint = await engine.ready(hostOf($))
    return lint.promptSubmit(ev, notes => next(withContext(e, notes)), droppedPrompt)
  }).catch(($, e, next) => next(e))

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    await (await engine.ready(hostOf($))).turnCompleted(turnEndEvent(e))
    return result
  })

  on('turn.start', async ($, e, next) => {
    ;(await engine.ready(hostOf($))).turnStarted(turnStartEvent(e))
    return next(e)
  })

  on('session.end', async ($, e: any, next) => {
    if (e.reason === 'clear') (await engine.ready(hostOf($))).cleared()
    return next(e)
  })

  on('session.append', async ($, e, next) => {
    const reply = appendedReply(e)
    if (reply) (await engine.ready(hostOf($))).replyAppended(reply)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('tool.call', async ($, e: any, next) => {
    if (!isLintTool(e)) return next(e)
    const ev = toolEvent(e, await cwdOf($))
    if (!ev) return next(e)
    const lint = await engine.ready(hostOf($))
    return toolResult(await lint.toolCall(ev, () => next(e), outcomeOf)) as any
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'ToolResult' }, async ($, e: any, next) => {
    const d = (await engine.ready(hostOf($))).cardFor(e.props?.tool_use_id)
    if (!d) return next(e)
    if (d.replace) return drawCard($, e, d)
    const { Box } = $.ui.resolve(e) as any
    return h(Box, { flexDirection: 'column', gap: 1 }, await next(e), drawCard($, e, d)) as any
  })

  on('skill.prompt', async ($, e, next) => {
    const result = await next(e)
    const ev = skillEvent(e)
    if (!ev) return result
    const preface = await (await engine.ready(hostOf($))).skillPrompt(ev)
    return preface ? { ...result, text: `${preface.text}\n\n${result.text}` } : result
  })
}
