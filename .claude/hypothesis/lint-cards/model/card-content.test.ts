// The judge of rules E8–E11 and reading R1 (lint-cards README, confirmed 2026-11-04): every card says only what
// is true at that moment, once. It sweeps every timing × level, the act sent once and — for an act that can be
// held once — sent again in a later response, on the real mod in the test kit. It reads only what the mod keeps
// ($.state baransu/lint: cards, band) and what the model is handed; no rule code is shared with the mod.
import { expect, test } from 'claude-code/testing'
import { mountLint } from './fixtures/layout'

const ROOT = 'C:/repo'
const FILES: Record<string, string> = {}
const CHECK = `${ROOT}/.claude/lint/checks/under-test.toml`
// The preset's own words for the delete preview (sets/baransu/runtime.toml).
const PREVIEW_MSG = '先看上面列出會動到的東西；確定沒錯，再下一次同樣的指令'
let STATE: any

type Act = 'edit' | 'bash' | 'delete' | 'commit' | 'push' | 'stop' | 'skill' | 'agent' | 'compact' | 'file' | 'manual' | 'retry'
type Sit = { timing: string; act: Act; level: string }
type Seen = { held: boolean; cards: any[]; told: string }
type Run = { first: Seen; second?: Seen }

// Levels each timing takes (format.md 時機); 'none' is a check that finds nothing.
const PRE = ['error', 'check', 'retry', 'warn', 'info', 'none']
const POST = ['error', 'retry', 'warn', 'info', 'none']
const TELL = ['warn', 'info', 'none']
const SITUATIONS: Sit[] = [
  ...PRE.map(level => ({ timing: 'pre:edit', act: 'edit' as Act, level })),
  ...PRE.map(level => ({ timing: 'pre:bash', act: 'bash' as Act, level })),
  // A delete always has paths to list: no 'none' for the preview.
  ...PRE.filter(l => l !== 'none').map(level => ({ timing: 'pre:bash', act: 'delete' as Act, level })),
  ...PRE.map(level => ({ timing: 'pre:commit', act: 'commit' as Act, level })),
  ...PRE.map(level => ({ timing: 'pre:push', act: 'push' as Act, level })),
  ...PRE.map(level => ({ timing: 'pre:stop', act: 'stop' as Act, level })),
  ...POST.map(level => ({ timing: 'post:edit', act: 'edit' as Act, level })),
  ...POST.map(level => ({ timing: 'post:bash', act: 'bash' as Act, level })),
  ...POST.map(level => ({ timing: 'post:commit', act: 'commit' as Act, level })),
  ...POST.map(level => ({ timing: 'post:push', act: 'push' as Act, level })),
  ...['error', 'warn', 'info', 'none'].map(level => ({ timing: 'pre:skill:ship', act: 'skill' as Act, level })),
  ...TELL.map(level => ({ timing: 'post:agent', act: 'agent' as Act, level })),
  ...TELL.map(level => ({ timing: 'pre:compact', act: 'compact' as Act, level })),
  ...['error', 'warn', 'info', 'none'].map(level => ({ timing: 'post:compact', act: 'compact' as Act, level })),
  ...['error', 'warn', 'info', 'none'].map(level => ({ timing: 'post:file', act: 'file' as Act, level })),
  ...['error', 'check', 'warn', 'info', 'none'].map(level => ({ timing: 'manual', act: 'manual' as Act, level })),
  ...['error', 'warn', 'info', 'none'].map(level => ({ timing: 'post:retry', act: 'retry' as Act, level })),
]

function checkText(s: Sit): string {
  if (s.act === 'delete') return `severity = "${s.level === 'none' ? 'warn' : s.level}"\nbuiltin = "destructive-preview"\nmessage = "${PREVIEW_MSG}"\n`
  const on = `on = ["${s.timing}"]\n`
  const sev = `severity = "${s.level === 'none' ? 'warn' : s.level}"\n`
  // Text the act carries: ZZZ. A check that finds nothing looks for what is never there.
  const pat = s.level === 'none' ? 'QQ_NEVER_QQ' : 'ZZZ'
  const scope = s.act === 'file' ? 'file = ["*.md"]\n' : ''
  return `${on}${sev}${scope}forbid = '${pat}'\nmessage = "MSG ${s.timing} ${s.level}"\n`
}

function kit(on: any, s: Sit) {
  STATE = undefined
  for (const k of Object.keys(FILES)) delete FILES[k]
  FILES[CHECK] = checkText(s)
  if (s.act === 'retry') FILES[`${ROOT}/.claude/lint/checks/asks-redo.toml`] = `on = ["pre:bash"]\nseverity = "retry"\nforbid = 'npm install -g'\nmessage = "install into the project"\n`
  mountLint(on, { root: () => ROOT, files: () => FILES })
  on('fs.stat', () => ({ value: { kind: 'dir' } }))
  on('process.run', (_: any, e: any) => {
    const a = e.argv.join(' ')
    const ok = (stdout: string, exitCode = 0) => ({ value: { exitCode, stdout, stderr: '' } })
    if (a === 'git rev-parse --show-toplevel') return ok(ROOT + '\n')
    if (e.argv[0] === 'git' && e.argv[1] === 'grep') return a.includes('ZZZ') ? ok(`${s.act === 'file' ? 'notes.md' : 'src/a.ts'}\u00003\u0000ZZZ\n`) : ok('', 1)
    if (a.startsWith('git status')) return ok(' M src/a.ts\n')
    if (a.startsWith('git diff') || a.includes('--name-only')) return ok('src/a.ts\n')
    if (a.startsWith('git log')) return ok('ZZZ\n')
    if (a === 'git config user.email') return ok('me@x.io\n')
    if (a === 'git config user.name') return ok('me\n')
    if (a.startsWith('git rev-parse --abbrev-ref')) return ok('feature\n')
    if (a.startsWith('git symbolic-ref')) return ok('origin/main\n')
    if (a.startsWith('git remote')) return ok('git@host:me/repo.git\n')
    return ok('')
  })
  on('fs.read', { path: `${ROOT}/src/a.ts` }, () => ({ value: 'ZZZ\n' }))
  on('classic.Stop', () => ({}))
  on('classic.SubagentStop', () => ({}))
  on('classic.FileChanged', () => ({}))
  on('session.surfaces', () => ({ value: ['desktop'] }))
  on('skill.prompt', (_: any, e: any) => ({ text: e.text }))
  on('prompt.submit', (_: any, e: any) => ({ text: e.text }))
  on('agent.spawn', () => ({ model: 'm', agentId: 'a1' }))
  on('session.compact', () => ({ messages: [{ role: 'assistant', text: 'summary ZZZ', toolUses: [] }] }))
  on('tool.call', () => ({ result: { stdout: 'out ZZZ', stderr: '' } }))
  on('turn.step', async function* (_: any, e: any) {
    if (STREAM) yield { kind: 'text', index: 0, text: STREAM }
    return { turnId: e.turnId, index: e.index, answer: STREAM, toolUses: [] }
  } as any)
  on('state.set', (_: any, e: any, next: any) => {
    if (e.plugin === 'baransu' && e.key === 'lint') STATE = e.value
    return next(e)
  })
}
let STREAM = ''
async function say($: any, text: string) {
  STREAM = text
  for await (const _ of ($.turn as any).step({ turnId: 't1', index: 0, model: 'm' })) void _
  STREAM = ''
}

const band = () => [...(STATE?.band ?? [])]
let N = 0
/** One occurrence of the act: was it held, which cards it left (under its call, or new in the band), what the model got. */
async function once($: any, s: Sit, second: boolean): Promise<Seen> {
  const before = band().length
  const id = `tu-${++N}`
  const call = async (input: any) => {
    const r: any = await $.tool.call({ tool_use_id: id, ...input })
    return { held: Boolean(r?.deny), told: [String(r?.deny ?? ''), ...(r?.context ?? [])].join('\n') }
  }
  let r: { held: boolean; told: string } = { held: false, told: '' }
  if (s.act === 'edit') r = await call({ tool: 'Write', file_path: `${ROOT}/src/a.ts`, content: 'ZZZ' })
  else if (s.act === 'bash') r = await call({ tool: 'Bash', command: 'echo ZZZ' })
  else if (s.act === 'delete') r = await call({ tool: 'Bash', command: 'rm -rf build' })
  else if (s.act === 'commit') r = await call({ tool: 'Bash', command: 'git commit -m ZZZ' })
  else if (s.act === 'push') r = await call({ tool: 'Bash', command: 'git push origin feature' })
  else if (s.act === 'stop') {
    const x: any = await $.classic.Stop({ stop_hook_active: second, last_assistant_message: 'done ZZZ' })
    r = { held: Boolean(x?.block), told: String(x?.block ?? '') }
  } else if (s.act === 'skill') {
    const x: any = await $.skill.prompt({ skill: 'baransu:ship', text: 'SHIP' })
    r = { held: /停下/.test(String(x?.text ?? '')), told: String(x?.text ?? '') }
  } else if (s.act === 'manual') {
    const x: any = await $.skill.prompt({ skill: 'baransu:lint', text: 'LINT' })
    r = { held: false, told: String(x?.text ?? '') }
  } else if (s.act === 'agent') {
    await $.agent.spawn({ tool_use_id: id, prompt: 'look', description: 'look', subagentType: 'Explore', parentModel: 'm' })
    await $.tool.call({ tool: 'Agent', tool_use_id: id, prompt: 'look' })
    await $.classic.SubagentStop({ stop_hook_active: false, agent_id: 'a1', agent_transcript_path: '', agent_type: 'Explore', last_assistant_message: 'found ZZZ' })
  } else if (s.act === 'compact') {
    const x: any = await $.session.compact({ trigger: 'manual', instructions: 'summarise ZZZ', messages: [{ role: 'user', text: 'hi', toolUses: [] }] })
    r = { held: false, told: JSON.stringify(x ?? '') }
  } else if (s.act === 'file') {
    await $.classic.FileChanged({ file_path: `${ROOT}/notes.md`, event: 'change' })
  } else if (s.act === 'retry') {
    // The 重新 is set up by another call, whose own card is not this act's.
    // Its answer is the first row with words in a later response; its card is drawn on the next call's row.
    await $.tool.call({ tool: 'Bash', tool_use_id: `${id}-setup`, command: 'npm install -g x' })
    const setup = band().length
    await say($, '')
    await $.session.append({ message: { type: 'assistant', content: [{ type: 'text', text: 'redone ZZZ' }] } })
    const x: any = await $.tool.call({ tool: 'Bash', tool_use_id: id, command: 'echo ok' })
    r = { held: false, told: (x?.context ?? []).join('\n') }
    const mine = Object.entries(STATE?.cards ?? {}).filter(([k]) => k === `${id}#answer`).map(([, c]) => c)
    return { held: false, cards: [...mine, ...band().slice(Math.max(before, setup))], told: r.told }
  }
  // Under its call: the call's own card, and any card hung on it (a subagent's, `<id>#…`).
  const own = Object.entries(STATE?.cards ?? {}).filter(([k]) => k === id || k.startsWith(`${id}#`)).map(([, c]) => c)
  return { held: r.held, cards: [...own, ...band().slice(before)], told: r.told }
}

const HOLD_ONCE = (s: Sit) => (s.level === 'check' || (s.act === 'stop' && s.level === 'retry')) && s.timing !== 'manual'
async function run($: any, s: Sit): Promise<Run> {
  await say($, '我先動手。')
  const first = await once($, s, false)
  if (!HOLD_ONCE(s) || !first.held) return { first }
  await say($, '')
  return { first, second: await once($, s, true) }
}

// ---------------------------------------------------------------- the rules, read off what was drawn

const text = (c: any) => [c.title, c.meta, ...(c.lines ?? []).map((l: any) => l.text), c.footer].filter(Boolean).join('\n')
const ids = (c: any) => new Set<string>((c.lines ?? []).map((l: any) => l.id).filter(Boolean))
const HELD_WORDS = /再下一次|沒有執行|沒有 commit|沒有 push|改寫這個指令再跑|改好要寫的內容再寫|修好 error 再|還不能結束/
const RAN_WORDS = /^(跑完|改好了)/

function judge(s: Sit, r: Run): string[] {
  const bad: string[] = []
  const look = (seen: Seen, when: string) => {
    for (const c of seen.cards) {
      if (!seen.held && HELD_WORDS.test(text(c))) bad.push(`E8 ${when}: ran, card says 「${text(c).match(HELD_WORDS)![0]}」`)
      if (seen.held && RAN_WORDS.test(c.title ?? '')) bad.push(`E8 ${when}: held, card titled 「${c.title}」`)
      if (/刪除 \S/.test(text(c)) && !(c.paths?.length)) bad.push(`E11 ${when}: the delete preview drawn as plain text`)
    }
  }
  look(r.first, 'first')
  if (r.second) look(r.second, 'second')
  // E1 (confirmed): before a skill and at /lint there is always a card, found or not.
  if (s.level === 'none' && s.act !== 'manual' && s.act !== 'skill' && r.first.cards.length) bad.push(`E10: no finding, yet a card 「${text(r.first.cards[0]).split('\n')[0]}」`)
  if (r.second) {
    // What the held card showed: its findings' ids and lines, and the paths of its delete preview.
    const heldIds = new Set(r.first.cards.flatMap(c => [...ids(c)]))
    const heldLines = new Set(r.first.cards.flatMap(c => (c.lines ?? []).map((l: any) => l.text)))
    const heldPaths = r.first.cards.flatMap(c => (c.paths ?? []).map((p: any) => String(p.path).replace(/\/$/, '')))
    for (const c of r.second.cards) {
      const again = [...ids(c)].filter(i => heldIds.has(i))
      const path = heldPaths.find(p => text(c).includes(p) || (c.paths ?? []).some((q: any) => String(q.path).startsWith(p)))
      if (again.length || path || (c.lines ?? []).some((l: any) => heldLines.has(l.text))) bad.push(`E9 second: the held finding drawn again (${again.join(',') || path || 'same line'})`)
    }
    if (!r.second.held) {
      for (const i of heldIds) if (r.second.told.includes(i)) bad.push(`R1 second: the model is told ${i} again`)
      for (const p of heldPaths) if (r.second.told.includes(`刪除 ${p}`)) bad.push(`R1 second: the model is told the preview of ${p} again`)
    }
  }
  return bad
}

for (const s of SITUATIONS) {
  test(`${s.timing} ${s.act} ${s.level}`, async ($, on) => {
    kit(on, s)
    const r = await run($, s)
    const shape = (x: Seen) => `${x.held ? 'held' : 'ran'} cards=${x.cards.length}${x.cards.map(c => ` [${c.kind}] ${text(c).replace(/\n/g, ' ⏎ ').slice(0, 160)}`).join('')}`
    console.log(`SIT ${s.timing} ${s.act} ${s.level} | 1st ${shape(r.first)}${r.second ? ` | 2nd ${shape(r.second)}` : ''}`)
    expect(judge(s, r)).toEqual([])
  })
}
