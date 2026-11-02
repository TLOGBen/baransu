import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'
import type { StatuslineState } from '../types'

// The status line under the prompt: model and effort, context with a compaction reminder, cache hit rate,
// and the 5-hour and 7-day windows as two-layer lines (thick: budget left; thin: time left until it refills).
// Only the window most at risk is coloured. Design: https://claude.ai/artifact/EkcP9pAz6y89uYhuFSkUUD.

const STATE = atom({ plugin: 'baransu', key: 'statusline' } as const, { tick: 0 } as StatuslineState)

const WINDOW_MS: Record<string, number> = { five_hour: 5 * 3600e3, seven_day: 7 * 86400e3 }
const LABEL: Record<string, string> = { five_hour: '5 小時', seven_day: '7 天' }
type Win = { kind: string; label: string; left: number; time: number; reset: string; risk: 0 | 1 | 2 }
type Line = { model: string; effort?: string; ctx?: number; cache?: number; wins: Win[]; working: boolean }

const pad = (n: number) => String(n).padStart(2, '0')
function resetText(kind: string, iso: string | undefined, now: number): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(+d)) return ''
  const hm = `${pad(d.getHours())}:${pad(d.getMinutes())}`
  if (kind === 'five_hour' || +d - now < 86400e3) return hm
  return `${d.getMonth() + 1}/${pad(d.getDate())} 週${'日一二三四五六'[d.getDay()]}`
}
// Budget below 10% is red; budget running behind the clock by more than five points is amber.
const riskOf = (left: number, time: number): 0 | 1 | 2 => (left < 10 ? 2 : left < time - 5 ? 1 : 0)

async function reading($: any, working: boolean): Promise<Line> {
  const s = await read($, STATE)
  let model = ''
  try { model = String(await $.session.model()) } catch {}
  let usage: any
  try { usage = await $.session.usage() } catch {}
  const now = Date.now()
  const wins: Win[] = []
  for (const r of usage?.rateLimits ?? []) {
    const span = WINDOW_MS[r.kind]
    if (!span) continue
    const left = Math.max(0, Math.round(100 - Number(r.percentUsed ?? 0)))
    const until = r.resetsAt ? +new Date(r.resetsAt) - now : span
    const time = Math.max(0, Math.min(100, Math.round((until / span) * 100)))
    wins.push({ kind: r.kind, label: LABEL[r.kind], left, time, reset: resetText(r.kind, r.resetsAt, now), risk: riskOf(left, time) })
  }
  wins.sort((a, b) => (a.kind === 'five_hour' ? -1 : b.kind === 'five_hour' ? 1 : 0))
  return { model, effort: s.effort, ctx: usage?.context?.percent, cache: s.cache, wins, working }
}

// The window that gets the colour: the one most at risk, and only when it is at risk.
function focusOf(wins: Win[]): Win | undefined {
  return wins.reduce<Win | undefined>((a, w) => (w.risk > (a?.risk ?? 0) ? w : a), undefined)
}
const ctxNote = (ctx?: number) => (ctx === undefined ? '' : ctx >= 90 ? ' 即將自動壓縮' : ctx >= 75 ? ' 可以先 /compact' : '')

function terminalTail(l: Line): string {
  const parts = [`${l.model}${l.effort ? ` ${l.effort}` : ''}`]
  if (l.ctx !== undefined) parts.push(`context ${l.ctx}%${ctxNote(l.ctx)}`)
  if (l.cache !== undefined) parts.push(`cache ${l.cache}%`)
  for (const w of l.wins) parts.push(`${w.label} 剩 ${w.left}%${w.reset ? `（${w.reset} 補回）` : ''}`)
  return parts.join('   ')
}

const esc = (s: string) => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]!)
// What the last drawing showed, so a changed value slides from there. Only the motion uses it; after a
// reload of the mod the next drawing simply starts without a slide.
const lastLeft = new Map<string, number>()

function svgLine(l: Line): { source: string; width: number } {
  const focus = focusOf(l.wins)
  const col = (r: number) => (r === 2 ? 'var(--red)' : 'var(--amber)')
  const x0 = 0
  let x = x0
  const out: string[] = []
  const text = (t: string, cls = 't', extra = '') => {
    out.push(`<text x="${x}" y="16" class="${cls}"${extra}>${esc(t)}</text>`)
    // A rough width: CJK about one em, everything else about 0.58 em at 12 px.
    x += [...t].reduce((n, c) => n + (/[　-鿿＀-￯]/.test(c) ? 12 : 7), 0)
  }
  const keyframes: string[] = []
  // Model and effort, with the spinner while a turn runs.
  out.push(`<g transform="translate(${x + 7} 12)"><circle r="5" fill="none" style="stroke:var(--track)" stroke-width="2"/><path class="${l.working ? 'spin' : ''}" d="M0 -5 A5 5 0 0 1 5 0" fill="none" style="stroke:var(--muted)" stroke-width="2" stroke-linecap="round"/></g>`)
  x += 20
  text(l.model || 'Claude', 'b')
  x += 6
  if (l.effort) {
    const levels = ['low', 'medium', 'high', 'xhigh', 'max']
    const n = levels.indexOf(l.effort) + 1
    for (let i = 0; i < 5; i++) out.push(`<rect x="${x + i * 6}" y="${18 - (6 + i * 2)}" width="4" height="${6 + i * 2}" rx="1" style="fill:var(${i < n ? '--text' : '--track'})"/>`)
    x += 34
    text(l.effort, 'm')
  }
  x += 24
  // Context and its compaction reminder.
  if (l.ctx !== undefined) {
    const c = l.ctx >= 90 ? 'var(--red)' : l.ctx >= 75 ? 'var(--amber)' : 'var(--grey)'
    text('context', 'm')
    x += 6
    out.push(`<rect x="${x}" y="10" width="72" height="4" rx="2" style="fill:var(--track)"/><rect x="${x}" y="10" width="${(72 * l.ctx) / 100}" height="4" rx="2" style="fill:${c}"/>`)
    x += 80
    text(`${l.ctx}%${ctxNote(l.ctx)}`, l.ctx >= 75 ? 'b' : 't', l.ctx >= 75 ? ` style="fill:${c}"` : '')
    x += 24
  }
  if (l.cache !== undefined) {
    text('cache', 'm')
    x += 6
    text(`${l.cache}%`, 'b', ' style="fill:var(--blue)"')
    x += 24
  }
  // The two-layer lines.
  l.wins.forEach((w, i) => {
    const hot = focus === w
    const c = hot ? col(w.risk) : 'var(--grey)'
    text(`${w.label} 剩 ${w.left}%`, hot ? 'b' : 't', hot ? ` style="fill:${c}"` : '')
    x += 8
    const from = lastLeft.get(w.kind)
    const to = (120 * w.left) / 100
    const slide = from !== undefined && Math.abs(from - to) > 0.5
    if (slide) keyframes.push(`@keyframes s${i}{from{width:${from}px}to{width:${to}px}}`)
    lastLeft.set(w.kind, to)
    out.push(`<rect x="${x}" y="7" width="120" height="5" rx="2.5" style="fill:var(--track)"/>`)
    out.push(`<rect x="${x}" y="7" width="${to}" height="5" rx="2.5" style="fill:${c}${slide ? `;animation:s${i} .7s cubic-bezier(.2,.8,.2,1) both` : ''}"/>`)
    if (hot) out.push(`<circle class="cap" cx="${x + to}" cy="9.5" r="3.5" style="fill:${c}"/>`)
    out.push(`<rect x="${x}" y="15" width="120" height="2" rx="1" style="fill:var(--line)"/><rect x="${x}" y="15" width="${(120 * w.time) / 100}" height="2" rx="1" style="fill:var(--grey)"/>`)
    x += 128
    if (w.reset) text(`${w.reset} 補回`, 'm')
    x += 24
  })
  const width = Math.ceil(x)
  const style = `
:root{--text:#1F2421;--muted:#646B67;--track:#DCDFDB;--line:#E6E8E5;--grey:#9AA19D;--amber:#B87507;--red:#C2362F;--blue:#2F6FD0}
@media (prefers-color-scheme: dark){:root{--text:#E8ECE9;--muted:#A3ABA6;--track:#3A423E;--line:#2C3330;--grey:#7D8681;--amber:#E0A54A;--red:#EE6A5F;--blue:#7FA8EA}}
text{font:12px "Noto Sans TC","Microsoft JhengHei","PingFang TC",system-ui,sans-serif;font-variant-numeric:tabular-nums}
.t{fill:var(--text)}.m{fill:var(--muted)}.b{fill:var(--text);font-weight:700}
@keyframes cap{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.9);opacity:.35}}
@keyframes spin{to{transform:rotate(360deg)}}
.cap{transform-box:fill-box;transform-origin:center;animation:cap 1.3s ease-in-out infinite}
.spin{transform-origin:0 0;animation:spin 1.4s linear infinite}
${keyframes.join('\n')}
@media (prefers-reduced-motion: reduce){*{animation:none!important}}`
  return {
    width,
    source: `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="24" viewBox="0 0 ${width} 24"><style>${style}</style>${out.join('')}</svg>`,
  }
}

// What only a main-loop response carries: its effort, and how much of its input came from the cache.
// A plugin hooks turn.step once: main.ts registers it and chains this after the lint gate's.
export async function* statuslineTurnStep($: any, e: any, next: any): any {
  const it = next(e)[Symbol.asyncIterator]()
  for (;;) {
    const { value, done } = await it.next()
    if (done) {
      if (!e.agentId) {
        const u = value?.usage
        const total = u ? u.input_tokens + u.cache_read_input_tokens + u.cache_creation_input_tokens : 0
        const effort = typeof e.effort === 'string' ? e.effort : undefined
        try {
          await update($, STATE, (s: StatuslineState) => ({
            ...s,
            effort: effort ?? s.effort,
            cache: total > 0 ? Math.round((100 * u.cache_read_input_tokens) / total) : s.cache,
            tick: s.tick + 1,
          }))
        } catch {}
      }
      return value
    }
    yield value
  }
}

export const register: Register = on => {
  // The session's usage moved (a turn ended, a window moved a point): redraw.
  on('session.measure', async ($, e, next) => {
    try { await update($, STATE, (s: StatuslineState) => ({ ...s, tick: s.tick + 1 })) } catch {}
    return next(e)
  })

  on('ui.render', { component: 'PromptHint' }, async ($, e: any, next) => {
    const line = await reading($, !!e.props?.isWorking)
    if (!line.model && !line.wins.length && line.ctx === undefined) return next(e)
    if (e.surface === 'terminal') return next({ ...e, props: { ...e.props, tail: terminalTail(line) } })
    const els = $.ui.resolve(e) as any
    if (!els.Svg) return next(e)
    const { source, width } = svgLine(line)
    const hint = await next(e)
    return h(els.Box, { flexDirection: 'column', gap: 'xs' },
      h(els.Svg, { source, alt: terminalTail(line), width, height: 24, isInteractive: true }),
      hint) as any
  }).catch(($, e, next) => next(e))
}
