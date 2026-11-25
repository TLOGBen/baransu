// The judge of rules E1–E7 (lint-cards README, confirmed 2026-11-04, W1–W3 count as breaks): every timing's
// result is one card the person can see. It runs the real mod in the test kit; each test is one situation, and a
// failing test is a broken rule (its name says which). model/check.py runs it and compares with the expected list.
//
// Observable state only: what the mod keeps ($.state baransu/lint: cards, band), what a surface draws (ui.mount of
// ToolUse / AbovePrompt), and the system rows it writes. No rule code is shared with the mod.
import { expect, test } from 'claude-code/testing'
import { mountLint } from './fixtures/layout'

const ROOT = 'C:/repo'
const FILES: Record<string, string> = {
  [`${ROOT}/.claude/lint/checks/stop-todo.toml`]: `on = ["pre:stop"]\nseverity = "error"\nforbid = 'TODO'\nmessage = "no TODO at the end"\n`,
  [`${ROOT}/.claude/lint/checks/agent-todo.toml`]: `on = ["post:agent"]\nseverity = "warn"\nforbid = 'TODO'\nmessage = "the subagent left a TODO"\n`,
  [`${ROOT}/.claude/lint/checks/file-note.toml`]: `on = ["post:file"]\nseverity = "warn"\nforbid = 'XYZ_NEVER'\nmessage = "x"\nfile = ["*.md"]\n`,
  [`${ROOT}/.claude/lint/checks/compact-note.toml`]: `on = ["pre:compact"]\nseverity = "warn"\nforbid = 'skip the tests'\nmessage = "the compaction must not drop the tests"\n`,
  [`${ROOT}/.claude/lint/checks/correction-to-lint.toml`]: `severity = "warn"\nbuiltin = "correction-to-lint"\nmessage = "never twice"\n`,
}
let STATE: any
// A hook below the plugins that refuses the next message (it never enters), as another plugin may.
let DROP = false

type Kit = { notices: string[] }
function kit(on: any, $: any, surfaces: string[], grep?: (argv: string[]) => string | undefined): Kit {
  const k: Kit = { notices: [] }
  STATE = undefined
  mountLint(on, { root: () => ROOT, files: () => FILES })
  on('process.run', (_: any, e: any) => {
    const hit = grep?.(e.argv)
    if (hit !== undefined) return { value: { exitCode: 0, stdout: hit, stderr: '' } }
    return { value: { exitCode: e.argv[0] === 'git' && e.argv[1] === 'grep' ? 1 : 0, stdout: e.argv.join(' ') === 'git rev-parse --show-toplevel' ? ROOT + '\n' : '', stderr: '' } }
  })
  // What the engine draws beneath the plugins, for a hook that hands a row on.
  on('ui.render', ($$: any, e: any) => h($$.ui.resolve(e).Text, null, 'engine row') as any)
  on('session.surfaces', () => ({ value: surfaces }))
  on('classic.Stop', () => ({}))
  on('classic.SubagentStop', () => ({}))
  on('classic.FileChanged', () => ({}))
  DROP = false
  on('prompt.submit', (_: any, e: any) => (DROP ? { drop: 'not now' } : { text: e.text }))
  on('skill.prompt', (_: any, e: any) => ({ text: e.text }))
  on('session.append', (_: any, e: any, next: any) => {
    if (e.message.type === 'system') k.notices.push(e.message.content[0].text)
    return next(e)
  })
  on('state.set', (_: any, e: any, next: any) => {
    if (e.plugin === 'baransu' && e.key === 'lint') STATE = e.value
    return next(e)
  })
  return k
}
const stopHeld = ($: any) => $.classic.Stop({ stop_hook_active: false, last_assistant_message: 'done, TODO later' })
async function bandTitles($: any, props: Record<string, unknown> = {}): Promise<number> {
  const ui = await $.ui.mount({ plugin: 'baransu', surface: 'desktop', component: 'AbovePrompt', props: { hasSurvey: false, isWorking: false, maxRows: 80, ...props } })
  const n = (await ui.findAll({ type: 'Text', text: /^lint · / })).length
  await ui.unmount()
  return n
}
async function rowHasCard($: any, id: string): Promise<boolean> {
  const ui = await $.ui.mount({ plugin: 'baransu', surface: 'desktop', component: 'ToolUse', props: { tool_use_id: id, tool: 'Agent', input: {}, isRunning: false, isErrored: false, isInterrupted: false, output: 'ok' } })
  const has = Boolean(await ui.find({ type: 'Text', text: /^lint · / }))
  await ui.unmount()
  return has
}

// ---------------------------------------------------------------- E1: every timing makes a card

test('E1 stop held → a card', async ($, on) => {
  kit(on, $, ['desktop'])
  await stopHeld($)
  expect(STATE.band?.length).toBe(1)
})

test('E1 a file changed outside Claude → a card', async ($, on) => {
  FILES[`${ROOT}/.claude/lint/checks/file-note.toml`] = `on = ["post:file"]\nseverity = "warn"\nforbid = 'TODO'\nmessage = "a TODO came in from outside"\nfile = ["*.md"]\n`
  kit(on, $, ['desktop'], argv => (argv[0] === 'git' && argv[1] === 'grep' ? 'notes.md\u00003\u0000TODO\n' : undefined))
  await ($ as any).classic.FileChanged({ file_path: `${ROOT}/notes.md`, event: 'change' })
  expect(STATE?.band?.length ?? 0).toBe(1)
})

test('E1 before a compaction → a card', async ($, on) => {
  kit(on, $, ['desktop'])
  on('session.compact', () => ({ messages: [{ role: 'assistant', text: 'summary', toolUses: [] }] }))
  await ($.session as any).compact({ trigger: 'manual', instructions: 'summarise, skip the tests', messages: [{ role: 'user', text: 'hi', toolUses: [] }] })
  expect(STATE?.band?.length ?? 0).toBe(1)
})

test('E1 a message read as a correction → a card', async ($, on) => {
  kit(on, $, ['desktop'])
  await $.prompt.submit({ text: '又犯同樣的錯了' } as any)
  expect(STATE?.band?.length ?? 0).toBe(1)
})

test('E1 /lint typed by the person → a card, nothing found', async ($, on) => {
  kit(on, $, ['desktop'])
  await $.skill.prompt({ skill: 'baransu:lint', text: 'LINT' } as any)
  expect(`${STATE?.band?.length}|${STATE?.band?.[0]?.kind}`).toBe('1|scan')
})

// ---------------------------------------------------------------- E2 / E3: cards under Agent and Skill calls

test('E2 a background subagent that ends after its Agent call returned: its card shows on that row', async ($, on) => {
  kit(on, $, ['desktop'])
  on('agent.spawn', () => ({ model: 'm', agentId: 'a1' }))
  on('tool.call', () => ({ result: {} }))
  await ($ as any).agent.spawn({ tool_use_id: 'tu-agent', prompt: 'look', description: 'look', subagentType: 'Explore', parentModel: 'm' })
  await $.tool.call({ tool: 'Agent', tool_use_id: 'tu-agent', prompt: 'look', run_in_background: true } as any)
  await ($ as any).classic.SubagentStop({ stop_hook_active: false, agent_id: 'a1', agent_transcript_path: '', agent_type: 'Explore', last_assistant_message: 'TODO check b.ts' })
  expect(await rowHasCard($, 'tu-agent')).toBe(true)
})

test('E3 two Skill calls at once: each skill card hangs under its own call', async ($, on) => {
  kit(on, $, ['desktop'])
  // Both calls start before either skill loads (parallel tool calls in one response).
  let release!: () => void
  const both = new Promise<void>(r => (release = r))
  let started = 0
  on('tool.call', async (_: any, e: any) => {
    if (e.tool === 'Skill') {
      if (++started === 2) release()
      await both
      await ($ as any).skill.prompt({ skill: e.skill, text: 'BODY' })
    }
    return { result: {} }
  })
  await Promise.all([
    $.tool.call({ tool: 'Skill', skill: 'baransu:lint', tool_use_id: 'tu-1' } as any),
    $.tool.call({ tool: 'Skill', skill: 'baransu:review', tool_use_id: 'tu-2' } as any),
  ])
  expect(`${STATE.cards['tu-1']?.kind}|${STATE.cards['tu-2']?.kind}`).toBe('scan|record')
})

// ---------------------------------------------------------------- E4 / E5 / E6: the band

test('E4 (W1) five cards kept in the band: all five are drawn', async ($, on) => {
  kit(on, $, ['desktop'])
  for (let i = 0; i < 5; i++) await $.skill.prompt({ skill: 'baransu:lint', text: 'LINT' } as any)
  expect(`${STATE.band.length}|${await bandTitles($)}`).toBe('5|5')
})

test('E4 six cards before the next message: none is lost', async ($, on) => {
  kit(on, $, ['desktop'])
  for (let i = 0; i < 6; i++) await $.skill.prompt({ skill: 'baransu:lint', text: 'LINT' } as any)
  expect(STATE.band.length).toBe(6)
})

test('E5 the next message the person sends clears the band; a message not typed by the person does not', async ($, on) => {
  kit(on, $, ['desktop'])
  await stopHeld($)
  await $.prompt.submit({ text: 'reminder', isMeta: true } as any)
  const kept = STATE.band.length
  await $.prompt.submit({ text: '好' } as any)
  expect(`${kept}|${STATE.band.length}`).toBe('1|0')
})

// From the second derivation (2026-11-04): two paths the judge above did not cover.
test('E4 a message that never enters (a hook below drops it) leaves the band as it was', async ($, on) => {
  kit(on, $, ['desktop'])
  await stopHeld($)
  DROP = true
  await $.prompt.submit({ text: '好' } as any)
  expect(STATE.band?.length ?? 0).toBe(1)
})

test('E5 a message of only an image clears the band too', async ($, on) => {
  kit(on, $, ['desktop'])
  await stopHeld($)
  await $.prompt.submit({ text: '', images: [{ mediaType: 'image/png', data: 'AA==' }] } as any)
  expect(STATE.band?.length ?? 0).toBe(0)
})

test('E6 a skill loaded through a Skill call is under the call and not in the band', async ($, on) => {
  kit(on, $, ['desktop'])
  on('tool.call', async (_: any, e: any) => {
    if (e.tool === 'Skill') await ($ as any).skill.prompt({ skill: 'baransu:lint', text: 'LINT' })
    return { result: {} }
  })
  await $.tool.call({ tool: 'Skill', skill: 'baransu:lint', tool_use_id: 'tu-s' } as any)
  expect(`${Boolean(STATE.cards['tu-s'])}|${(STATE.band ?? []).length}`).toBe('true|0')
})

// ---------------------------------------------------------------- E7: where the band cannot be seen

test('E7 no surface draws the band: the card is written as a row', async ($, on) => {
  const k = kit(on, $, [])
  await stopHeld($)
  expect(k.notices.some(n => n.includes('還不能結束'))).toBe(true)
})

test('E7 (W2) the band is held by a survey: the card is still seen', async ($, on) => {
  const k = kit(on, $, ['desktop'])
  await stopHeld($)
  expect((await bandTitles($, { hasSurvey: true })) > 0 || k.notices.some(n => n.includes('還不能結束'))).toBe(true)
})

test('E7 (W3) a terminal and a phone: the phone sees the card too', async ($, on) => {
  const k = kit(on, $, ['terminal', 'mobile'])
  await stopHeld($)
  expect(k.notices.some(n => n.includes('還不能結束'))).toBe(true)
})

// ---------------------------------------------------------------- the answer to a 重新 with no next call

test('E1 a checked answer with no later call in its turn is seen before the person sends the next message', async ($, on) => {
  FILES[`${ROOT}/.claude/lint/checks/user-language.toml`] = `severity = "retry"\nbuiltin = "user-language"\nmessage = "x"\n`
  FILES[`${ROOT}/.claude/lint/checks/answer-zh.toml`] = `on = ["post:retry"]\nseverity = "warn"\nforbid = '[A-Za-z]{4,}( [A-Za-z]{2,}){4,}'\nmessage = "still English"\n`
  kit(on, $, ['desktop'])
  on('turn.start', (_: any, e: any) => ({ turnId: e.turnId }))
  on('tool.call', () => ({ result: {} }))
  on('turn.complete', () => ({ text: '' }))
  on('turn.step', async function* (_: any, e: any) {
    yield { kind: 'stop', stopReason: 'end_turn', usage: null, ref: 0 }
    return { turnId: e.turnId, index: e.index, answer: '', toolUses: [] }
  } as any)
  const step = async (index: number) => { for await (const _ of ($ as any).turn.step({ turnId: 't1', index, model: 'm', messageCount: 1 })) void _ }
  const row = (t: string) => ($ as any).session.append({ message: { type: 'assistant', content: [{ type: 'text', text: t }] } })
  await $.prompt.submit({ text: '幫我改一下這個檢查然後跑測試' } as any)
  await ($ as any).turn.start({ turnId: 't1' })
  await step(0)
  await row('The test kit allows one process.run mock per test; fold the extra answers into the shared mock instead.')
  await step(1)
  await $.tool.call({ tool: 'Bash', command: 'ls', tool_use_id: 'k1' } as any)
  await step(2)
  await row('我改用中文重講：測試只允許一個替身，其他回答要併進同一個替身裡。')
  await ($ as any).turn.complete({ turnId: 't1', answer: '', durationMs: 1, isAborted: false, reason: 'answer' })
  // The answer was checked; no call follows in this turn. Is its card anywhere the person can see now?
  const seen = Boolean(STATE.answerCard === undefined && (STATE.band ?? []).some((c: any) => c.meta.includes('回應後')))
    || Object.keys(STATE.cards).some(id => id.endsWith('#answer'))
  expect(seen).toBe(true)
  delete FILES[`${ROOT}/.claude/lint/checks/user-language.toml`]
  delete FILES[`${ROOT}/.claude/lint/checks/answer-zh.toml`]
})
