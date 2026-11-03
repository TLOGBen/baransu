import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'
import type { StatuslineState } from '../types'

// The status line: model and effort, context with a compaction reminder, cache hit rate, and the 5-hour
// and 7-day windows as two-layer lines (thick: budget left; thin: time left until it refills). Only the
// window most at risk is coloured. Design: https://claude.ai/artifact/EkcP9pAz6y89uYhuFSkUUD.
// The desktop draws one row above the prompt: text in the app's own Text, only the bars and the spinner
// as small SVG. The terminal adds the whole line to the end of the hint line under the prompt.

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

// `claude-opus-5-5` as people say it, `Opus 5.5`; anything else as given.
function modelName(id: string): string {
  const m = /^claude-([a-z]+)-(\d+)(?:-(\d{1,2}))?(?:\b|$)/.exec(id)
  return m ? `${m[1][0].toUpperCase()}${m[1].slice(1)} ${m[2]}${m[3] ? `.${m[3]}` : ''}` : id
}

function terminalTail(l: Line): string {
  const parts = [`${modelName(l.model)}${l.effort ? ` ${l.effort}` : ''}`]
  if (l.ctx !== undefined) parts.push(`context ${l.ctx}%${ctxNote(l.ctx)}`)
  if (l.cache !== undefined) parts.push(`cache ${l.cache}%`)
  for (const w of l.wins) parts.push(`${w.label} 剩 ${w.left}%${w.reset ? `（${w.reset} 補回）` : ''}`)
  return parts.join('   ')
}

// The app draws an SVG as an image that knows nothing of its theme, so these read on light and dark alike.
const C = { amber: '#c0841a', red: '#d64545', grey: '#8a8f98' }
const svg = (w: number, h: number, body: string) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`
const MOTION = '<style>@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>'

const SPINNER = svg(14, 14, `${MOTION}<style>@keyframes spin{to{transform:rotate(360deg)}}.s{transform-origin:7px 7px;animation:spin 1.4s linear infinite}</style><circle cx="7" cy="7" r="5" fill="none" stroke="${C.grey}" stroke-opacity=".3" stroke-width="2"/><path class="s" d="M7 2 A5 5 0 0 1 12 7" fill="none" stroke="${C.grey}" stroke-width="2" stroke-linecap="round"/>`)

function ctxBar(ctx: number, colour: string): string {
  return svg(56, 6, `<rect width="56" height="6" rx="3" fill="${C.grey}" fill-opacity=".28"/><rect width="${Math.max(6, (56 * ctx) / 100)}" height="6" rx="3" fill="${colour}"/>`)
}

// What the last drawing showed, so a changed value slides from there. Only the motion uses it; after a
// reload of the mod the next drawing simply starts without a slide.
const lastLeft = new Map<string, number>()
const W = 96
function windowBar(w: Win, colour: string, hot: boolean): string {
  const to = (W * w.left) / 100
  const from = lastLeft.get(w.kind)
  lastLeft.set(w.kind, to)
  const slide = from !== undefined && Math.abs(from - to) > 0.5
  const css = [
    MOTION,
    slide ? `<style>@keyframes s{from{width:${from}px}to{width:${to}px}}.f{animation:s .7s cubic-bezier(.2,.8,.2,1) both}</style>` : '',
    hot ? '<style>@keyframes p{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.9);opacity:.35}}.cap{transform-box:fill-box;transform-origin:center;animation:p 1.3s ease-in-out infinite}</style>' : '',
  ].join('')
  return svg(W + 8, 14,
    `${css}<g transform="translate(4 0)">` +
    `<rect y="3" width="${W}" height="5" rx="2.5" fill="${C.grey}" fill-opacity=".28"/>` +
    `<rect class="f" y="3" width="${to}" height="5" rx="2.5" fill="${colour}"/>` +
    (hot ? `<circle class="cap" cx="${to}" cy="5.5" r="3.5" fill="${colour}"/>` : '') +
    `<rect y="11" width="${W}" height="2" rx="1" fill="${C.grey}" fill-opacity=".2"/>` +
    `<rect y="11" width="${(W * w.time) / 100}" height="2" rx="1" fill="${C.grey}"/></g>`)
}

// One row, never wrapped: a spinner while a turn runs, context, and the two windows. The app already
// shows the model and the effort under the prompt, so the row leaves them out, and the cache rate with
// them. Only the 5-hour window names its refill time; the 7-day one's thin line already says how far off
// it is. Where it is narrow it drops the bars, then that refill time.
function desktopRow(els: any, l: Line, columns: number): any {
  const { Box, Text: T, Svg } = els
  const Text = (props: any, s: string) => h(T, { size: 'footnote', ...props }, s)
  const focus = focusOf(l.wins)
  const bars = columns >= 100
  const resets = columns >= 70
  const item = (key: string, ...kids: any[]) => h(Box, { key, flexDirection: 'row', columnGap: 1, alignItems: 'center', flexShrink: 0 }, ...kids)
  const parts: any[] = []
  if (l.working) parts.push(item('spin', h(Svg, { source: SPINNER, alt: '執行中', width: 14, height: 14, isInteractive: true })))
  if (l.ctx !== undefined) {
    const colour = l.ctx >= 90 ? C.red : l.ctx >= 75 ? C.amber : C.grey
    parts.push(item('ctx',
      Text({ dimColor: true }, 'context'),
      bars ? h(Svg, { source: ctxBar(l.ctx, colour), alt: `context ${l.ctx}%`, width: 56, height: 6 }) : null,
      l.ctx >= 75
        ? Text({ color: colour, weight: 'semibold', tabular: true }, `${l.ctx}%${ctxNote(l.ctx)}`)
        : Text({ tabular: true }, `${l.ctx}%`)))
  }
  for (const w of l.wins) {
    const hot = focus === w
    const colour = hot ? (w.risk === 2 ? C.red : C.amber) : C.grey
    parts.push(item(w.kind,
      hot ? Text({ color: colour, weight: 'semibold', tabular: true }, `${w.label} 剩 ${w.left}%`) : Text({ tabular: true }, `${w.label} 剩 ${w.left}%`),
      bars ? h(Svg, { source: windowBar(w, colour, hot), alt: `${w.label} 剩 ${w.left}%，時間剩 ${w.time}%`, width: W + 8, height: 14, isInteractive: true }) : null,
      w.reset && resets && w.kind === 'five_hour' ? Text({ dimColor: true, tabular: true }, w.reset) : null))
  }
  return h(Box, { flexDirection: 'row', flexWrap: 'nowrap', columnGap: 2, alignItems: 'center' }, ...parts)
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

// A window's time layer, and the colour judged against it, move with the clock while nothing else
// redraws the row (no turn, no usage change): redraw each minute.
// Started by the first drawing; a reload starts the module, and so this, over.
let ticking = false
function tickEachMinute($: any) {
  if (ticking) return
  ticking = true
  try { $.clock.every(60e3, () => $.ui.invalidate('ui.render')) } catch { ticking = false }
}

export const register: Register = on => {
  // The session's usage moved (a turn ended, a window moved a point): redraw.
  on('session.measure', async ($, e, next) => {
    try { await update($, STATE, (s: StatuslineState) => ({ ...s, tick: s.tick + 1 })) } catch {}
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e: any, next) => {
    if (e.surface === 'terminal' || e.props?.hasSurvey) return next(e)
    const els = $.ui.resolve(e) as any
    if (!els.Svg) return next(e)
    tickEachMinute($)
    const line = await reading($, !!e.props?.isWorking)
    if (!line.model && !line.wins.length && line.ctx === undefined) return next(e)
    return h(els.Box, { flexDirection: 'column', rowGap: 1 }, desktopRow(els, line, e.props?.bodyColumns ?? 120), await next(e)) as any
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'PromptHint' }, async ($, e: any, next) => {
    if (e.surface !== 'terminal') return next(e)
    tickEachMinute($)
    const line = await reading($, !!e.props?.isWorking)
    if (!line.model && !line.wins.length && line.ctx === undefined) return next(e)
    return next({ ...e, props: { ...e.props, tail: terminalTail(line) } })
  }).catch(($, e, next) => next(e))
}
