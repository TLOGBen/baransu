// review F1 and F2 (2026-11-04): a card names how many findings it left out and shows a tool's last lines; the
// agents of one Workflow call each keep their own card under it.
import { expect, test } from 'claude-code/testing'
import { mountLint } from './fixtures/layout'

const ROOT = 'C:/repo'
const FILES: Record<string, string> = {
  [`${ROOT}/.claude/lint/checks/agent-todo.toml`]: `on = ["post:agent"]\nseverity = "warn"\nforbid = 'TODO'\nmessage = "the subagent left a TODO"\n`,
  [`${ROOT}/.claude/lint/checks/json-parses.toml`]: `on = ["manual"]\nseverity = "error"\next = ["json"]\nrun = ["jq", "empty", "{file}"]\nmessage = "fix the JSON"\n`,
  [`${ROOT}/.claude/lint/checks/no-todo.toml`]: `on = ["manual"]\nseverity = "error"\nforbid = 'TODO'\nmessage = "use an issue link"\n`,
}
let STATE: any
let SPAWNED = 0
const TEN = Array.from({ length: 10 }, (_, i) => `src/f${i}.ts\u00001\u0000// TODO`).join('\n') + '\n'

function kit(on: any) {
  STATE = undefined
  mountLint(on, { root: () => ROOT, files: () => FILES })
  on('process.run', (_: any, e: any) => {
    const a = e.argv.join(' ')
    const ok = (stdout: string, exitCode = 0, stderr = '') => ({ value: { exitCode, stdout, stderr } })
    if (a === 'git rev-parse --show-toplevel') return ok(ROOT + '\n')
    if (a.startsWith('git grep -lIz')) return ok('bad.json\u0000')
    if (a.startsWith('git grep')) return a.includes('TODO') ? ok(TEN) : ok('', 1)
    if (a.startsWith('jq empty')) return ok('', 5, 'jq: error (at bad.json:3): Invalid numeric literal at line 4, column 21')
    return ok('')
  })
  on('classic.SubagentStop', () => ({}))
  SPAWNED = 0
  on('agent.spawn', () => ({ model: 'm', agentId: `w${++SPAWNED}` }))
  on('skill.prompt', (_: any, e: any) => ({ text: e.text }))
  on('ui.render', ($$: any, e: any) => h($$.ui.resolve(e).Text, null, 'engine row') as any)
  on('state.set', (_: any, e: any, next: any) => {
    if (e.plugin === 'baransu' && e.key === 'lint') STATE = e.value
    return next(e)
  })
}

test('F2: two agents of one Workflow call each keep their card under it, both drawn on its row', async ($, on) => {
  kit(on)
  await ($ as any).agent.spawn({ tool_use_id: 'tu-wf', prompt: 'a', description: 'a', subagentType: 'Explore', parentModel: 'm' })
  await ($ as any).agent.spawn({ tool_use_id: 'tu-wf', prompt: 'b', description: 'b', subagentType: 'Explore', parentModel: 'm' })
  await ($ as any).classic.SubagentStop({ stop_hook_active: false, agent_id: 'w1', agent_transcript_path: '', agent_type: 'Explore', last_assistant_message: 'TODO one' })
  await ($ as any).classic.SubagentStop({ stop_hook_active: false, agent_id: 'w2', agent_transcript_path: '', agent_type: 'Explore', last_assistant_message: 'TODO two' })
  const kept = Object.keys(STATE.cards).filter(k => k.startsWith('tu-wf#agent:')).sort()
  const ui = await ($.ui as any).mount({ plugin: 'baransu', surface: 'desktop', component: 'ToolUse', props: { tool_use_id: 'tu-wf', tool: 'Workflow', input: {}, isRunning: false, isErrored: false, isInterrupted: false, output: 'ok' } })
  const drawn = (await ui.findAll({ type: 'Text', text: /^lint · subagent 結束後/ })).length
  await ui.unmount()
  expect(`${kept.join(',')}|${drawn}`).toBe('tu-wf#agent:w1,tu-wf#agent:w2|2')
})

test('F1: a card past its rows says how many it left out, and a tool’s last lines show under its finding', async ($, on) => {
  kit(on)
  await $.skill.prompt({ skill: 'baransu:lint', text: 'LINT' } as any)
  const ui = await ($.ui as any).mount({ plugin: 'baransu', surface: 'desktop', component: 'AbovePrompt', props: { hasSurvey: false, isWorking: false, maxRows: 80 } })
  const has = async (t: RegExp) => Boolean(await ui.find({ type: 'Text', text: t }))
  const got = [await has(/^還有 3 條沒列出$/), await has(/line 4, column 21/)]
  await ui.unmount()
  expect(got).toEqual([true, true])
})
