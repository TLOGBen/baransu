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
import { LANGUAGES } from '../../util/languages'
import { hostMachine } from './machine'
import { hostClock, hostNotify, hostOf, hostRunner, hostState, whatNowSkill, type Dollar, type Host } from './ports'
import {
  actorOf, agentStopEvent, appendedReply, compactSummary, droppedPrompt, fileChangedEvent, isLintTool, outcomeOf, promptEvent,
  skillEvent, stopEvent, stopResult, streamedText, tap, toolEvent, toolResult, turnEndEvent, turnStartEvent, withContext,
} from './translate'

const engine = createEngine<Host>({
  config: hostConfig(), runner: hostRunner, state: hostState, notify: hostNotify, clock: hostClock, whatNowSkill, machine: hostMachine, languages: LANGUAGES,
})

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
    let add: { id: string; text: string; scope: 'session' }[] = []
    try {
      add = (await (await engine.ready(hostOf($))).systemNotes()).map(n => ({ ...n, scope: 'session' as const }))
    } catch {}
    return add.length ? { ...result, sections: [...result.sections, ...add] } : result
  })

  // watchPaths can only be answered at SessionStart (session start, and after a compaction), so post:file
  // watches the lint root from the next start after such a check is added.
  on('classic.SessionStart', async ($, e: any, next) => {
    const r: any = await next(e)
    let paths: readonly string[] = []
    try {
      paths = await (await engine.ready(hostOf($))).watchPaths()
    } catch {}
    return paths.length ? { ...r, watchPaths: [...(r?.watchPaths ?? []), ...paths] } : r
  })

  on('classic.Stop', async ($, e: any, next) => {
    const r: any = await next(e)
    const v = await (await engine.ready(hostOf($))).stopping(stopEvent(e))
    return stopResult(r, v)
  }).catch(($, e, next) => next(e))

  on('agent.spawn', async ($, e: any, next) => {
    const r: any = await next(e)
    if (r?.agentId) await (await engine.ready(hostOf($))).agentStarted({ agent: String(r.agentId), agentType: String(e.subagentType ?? '') })
    return r
  }).catch(($, e, next) => next(e))

  on('classic.SubagentStop', async ($, e: any, next) => {
    const r = await next(e)
    await (await engine.ready(hostOf($))).agentStopped(agentStopEvent(e))
    return r
  }).catch(($, e, next) => next(e))

  on('classic.FileChanged', async ($, e: any, next) => {
    const r = await next(e)
    const ev = fileChangedEvent(e)
    if (ev) await (await engine.ready(hostOf($))).fileChanged(ev)
    return r
  }).catch(($, e, next) => next(e))

  // The main conversation's compaction only (a subagent's own carries agentId), and not a precompute.
  on('session.compact', async ($, e: any, next) => {
    if (e.agentId || e.trigger === 'precompute') return next(e)
    const lint = await engine.ready(hostOf($))
    return lint.compacting(
      { instructions: String(e.instructions ?? '') },
      instructions => next(instructions ? { ...e, instructions } : e),
      (r: any) => !!r?.skip,
      compactSummary,
    ) as any
  }).catch(($, e, next) => next(e))

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
    // Awaited, so a failing redo check lands in this hook's .catch instead of going unhandled.
    if (reply) await (await engine.ready(hostOf($))).replyAppended(reply)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('tool.call', async ($, e: any, next) => {
    if (!isLintTool(e)) return next(e)
    const ev = toolEvent(e, await cwdOf($))
    if (!ev) return next(e)
    const lint = await engine.ready(hostOf($))
    return toolResult(await lint.toolCall(ev, () => next(e), outcomeOf)) as any
  }).catch(($, e, next) => next(e))

  // A card is drawn on the call's row (ToolUse), the one place every row passes: a standalone row and a row inside a
  // folded group alike (HUNT-2026-002: a folded group's rows draw their result inline, with no ToolResult). A held
  // call's card stands in place of its error text, so that text is emptied in the row and in a standalone result.
  on('ui.render', { component: 'ToolUse' }, async ($, e: any, next) => {
    const lint = await engine.ready(hostOf($))
    const d = lint.cardFor(e.props?.tool_use_id)
    // The check of the model's answer to a 重新, drawn on the next call's row (there is no row of its own).
    const answer = lint.cardFor(`${e.props?.tool_use_id}#answer`)
    if ((!d && !answer) || e.props?.isRunning) return next(e)
    const row = await next(d?.replace ? { ...e, props: { ...e.props, output: '' } } : e)
    const { Box } = $.ui.resolve(e) as any
    return h(Box, { flexDirection: 'column', gap: 1 }, ...(answer ? [drawCard($, e, answer)] : []), row, ...(d ? [drawCard($, e, d)] : [])) as any
  })

  // A standalone held call: its card is on the row above, so its result draws nothing (an errored ToolResult draws
  // the error text whatever its output says, so the result is answered here rather than rewritten).
  on('ui.render', { component: 'ToolResult' }, async ($, e: any, next) => {
    const d = (await engine.ready(hostOf($))).cardFor(e.props?.tool_use_id)
    if (!d?.replace) return next(e)
    const { Box } = $.ui.resolve(e) as any
    return h(Box, null) as any
  })

  // A folded group drawn as one line hides its rows, so one holding a call with a card unfolds (user 2026-11-03, Q1-b).
  on('ui.render', { component: 'ToolGroup' }, async ($, e: any, next) => {
    if (e.props?.isExpanded) return next(e)
    const lint = await engine.ready(hostOf($))
    const carded = (e.props?.calls ?? []).some((c: any) => c.tool_use_id && (lint.cardFor(c.tool_use_id) || lint.cardFor(`${c.tool_use_id}#answer`)))
    return next(carded ? { ...e, props: { ...e.props, isExpanded: true } } : e)
  })

  on('skill.prompt', async ($, e, next) => {
    const result = await next(e)
    const ev = skillEvent(e)
    if (!ev) return result
    const preface = await (await engine.ready(hostOf($))).skillPrompt(ev)
    return preface ? { ...result, text: `${preface.text}\n\n${result.text}` } : result
  })
}
