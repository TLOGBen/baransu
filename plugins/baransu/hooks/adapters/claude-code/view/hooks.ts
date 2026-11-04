// Where each card is drawn: the one place that decides it. A card kept under a call hangs on that call's row
// (a tool call, the Agent or Workflow call that started a subagent — one card per subagent — the Skill call that
// loaded a skill) where the surface draws that row; a card with no call is a plain row (view/port.ts). Nothing
// is forced into view: a folded group stays folded (purpose over display, user 2026-11-04).

import { lintOf } from '../instance'
import { drawCard } from './card'

type On = Parameters<import('claude-code').Register>[0]

export function registerView(on: On) {
  // A card is drawn on the call's row (ToolUse), the one place every row passes: a standalone row and a row inside a
  // folded group alike (HUNT-2026-002: a folded group's rows draw their result inline, with no ToolResult). A held
  // call's card stands in place of its error text, so that text is emptied in the row and in a standalone result.
  on('ui.render', { component: 'ToolUse' }, async ($, e: any, next) => {
    const lint = await lintOf($)
    const id = e.props?.tool_use_id
    const d = lint.cardFor(id)
    // The check of the model's answer to a 重新, drawn on the next call's row (there is no row of its own).
    const answer = lint.cardFor(`${id}#answer`)
    const agents = id ? lint.agentCardsUnder(id) : []
    if ((!d && !answer && !agents.length) || e.props?.isRunning) return next(e)
    const row = await next(d?.replace ? { ...e, props: { ...e.props, output: '' } } : e)
    const { Box } = $.ui.resolve(e) as any
    return h(Box, { flexDirection: 'column', gap: 1 },
      ...(answer ? [drawCard($, e, answer)] : []), row, ...(d ? [drawCard($, e, d)] : []), ...agents.map(a => drawCard($, e, a))) as any
  })

  // A standalone held call: its card is on the row above, so its result draws nothing (an errored ToolResult draws
  // the error text whatever its output says, so the result is answered here rather than rewritten).
  on('ui.render', { component: 'ToolResult' }, async ($, e: any, next) => {
    const d = (await lintOf($)).cardFor(e.props?.tool_use_id)
    if (!d?.replace) return next(e)
    const { Box } = $.ui.resolve(e) as any
    return h(Box, null) as any
  })
}
