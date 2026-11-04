// Drawing a Card with the host's UI elements, as the design canvas "Lint 卡片設計" (2026-11-03) draws every card,
// on a call's row or above the prompt alike; it takes the engine's Card value and writes no sentence of its own
// beyond the path list's connectives (從, →).

import { pathGroups, type PathGroup } from '../../../engine/text'
import type { Card, Finding } from '../../../engine'
import type { Dollar } from '../ports'

// Colors from the design canvas: tint, border, strong text, meta text, body text, icon, chip.
const PALETTE = {
  error: { bg: '#FDF3F3', border: '#F2CFCF', strong: '#8E1B1B', meta: '#9A4C4C', body: '#3B2020', icon: '#D63B3B', chip: '#F3D3D3' },
  edited: { bg: '#FDF3F3', border: '#F2CFCF', strong: '#8E1B1B', meta: '#9A4C4C', body: '#3B2020', icon: '#D63B3B', chip: '#F3D3D3' },
  check: { bg: '#FDF7EA', border: '#EFD9A6', strong: '#6E4205', meta: '#8A5F1F', body: '#3A2A0E', icon: '#E39A1C', chip: '#F3E2BA' },
  warn: { bg: '#FCFBF8', border: '#E8E3D6', strong: '#5C4210', meta: '#756749', body: '#2F2A20', icon: '#C98A16', chip: '#F1EAD8' },
  retry: { bg: '#EFF5FD', border: '#C8DAF2', strong: '#1C4E8E', meta: '#41628F', body: '#1D2A3C', icon: '#2F6FD0', chip: '#D2E2F6' },
  note: { bg: '#F4F5F7', border: '#DADDE3', strong: '#353C49', meta: '#5E6573', body: '#2A2F38', icon: '#7A8494', chip: '#E3E6EB' },
  stop: { bg: '#FBEAEA', border: '#E7B1B1', strong: '#7A1414', meta: '#934545', body: '#361A1A', icon: '#C42B2B', chip: '#F0C4C4' },
  record: { bg: '#F5F6F8', border: '#DCDFE6', strong: '#30364A', meta: '#5B6175', body: '#262A36', icon: '#5B63C9', chip: '#E4E6EE' },
  // Every check run: nothing found, warns found, an error found (the model's answer to a 重新 too).
  scan: { bg: '#EEF8F6', border: '#C6E6E0', strong: '#11554B', meta: '#356F66', body: '#17332F', icon: '#1F9A88', chip: '#D2ECE7' },
  scanWarn: { bg: '#FDF7EA', border: '#EFD9A6', strong: '#6E4205', meta: '#8A5F1F', body: '#3A2A0E', icon: '#D88E12', chip: '#F3E2BA' },
  scanError: { bg: '#FDF3F3', border: '#F2CFCF', strong: '#8E1B1B', meta: '#9A4C4C', body: '#3B2020', icon: '#D63B3B', chip: '#F3D3D3' },
} as const
const MAGNIFIER = (c: string) => `<circle cx="12.5" cy="12.5" r="7" fill="none" stroke="${c}" stroke-width="1.9"/><path d="M17.8 17.8 L23.5 23.5" stroke="${c}" stroke-width="2.2" stroke-linecap="round"/>`
const SHIELD = 'M14 3.5 L22.5 6.8 V13 C22.5 18.4 18.9 22.3 14 24.5 C9.1 22.3 5.5 18.4 5.5 13 V6.8 Z'
const svg = (size: number, body: string) => `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" overflow="visible">${body}</svg>`
function iconSvg(kind: Card['kind']): string {
  const c = PALETTE[kind].icon
  const s = (body: string) => svg(28, body)
  if (kind === 'error')
    // The shield's own outline expands and fades, not a generic ring.
    return s(`<g transform="translate(14 14)"><path d="M0 -10.5 L8.5 -7.2 V-1 C8.5 4.4 4.9 8.3 0 10.5 C-4.9 8.3 -8.5 4.4 -8.5 -1 V-7.2 Z" fill="none" stroke="${c}" stroke-width="1.4" vector-effect="non-scaling-stroke"><animate attributeName="opacity" values="0.7;0;0" keyTimes="0;0.7;1" dur="1.6s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="scale" values="1;1.45;1.45" keyTimes="0;0.7;1" dur="1.6s" repeatCount="indefinite"/></path></g><path d="${SHIELD}" fill="${c}"/><rect x="12.8" y="8.6" width="2.4" height="7" rx="1.2" fill="#fff"/><circle cx="14" cy="18.8" r="1.5" fill="#fff"/>`)
  if (kind === 'edited')
    // A page with a mark on its corner: the file is already changed.
    return s(`<rect x="5" y="4" width="15" height="20" rx="2.5" fill="none" stroke="${c}" stroke-width="1.8"/><path d="M8.5 9.5 H16.5 M8.5 13 H14" stroke="${c}" stroke-width="1.6" stroke-linecap="round"/><circle cx="20" cy="19" r="5.5" fill="${c}"><animate attributeName="r" values="5.5;6.6;5.5;6.6;5.5;5.5" keyTimes="0;0.06;0.12;0.18;0.24;1" dur="3.5s" begin="0.6s" repeatCount="indefinite"/></circle><rect x="19.2" y="15.6" width="1.6" height="4" rx="0.8" fill="#fff"/><circle cx="20" cy="21.6" r="0.95" fill="#fff"/>`)
  if (kind === 'check')
    return s(`<path d="${SHIELD}" fill="${c}"/><g><animate attributeName="opacity" values="1;0.45;1" dur="1.8s" repeatCount="indefinite"/><rect x="10.6" y="9.4" width="2.4" height="8.4" rx="1" fill="#fff"/><rect x="15" y="9.4" width="2.4" height="8.4" rx="1" fill="#fff"/></g>`)
  if (kind === 'retry')
    return s(`<g><animateTransform attributeName="transform" type="rotate" values="0 14 14;360 14 14;360 14 14" keyTimes="0;0.3;1" dur="4s" begin="0.5s" repeatCount="indefinite"/><path d="M20.93 10 A8 8 0 1 0 20.93 18" fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round"/><path d="M21.07 5.57 L21.52 11.26 L17.21 10.17" fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g>`)
  if (kind === 'note')
    return s(`<circle cx="14" cy="14" r="9.5" fill="none" stroke="${c}" stroke-width="1.8"><animate attributeName="opacity" values="0.45;1;0.45" dur="3.6s" begin="0.4s" repeatCount="indefinite"/></circle><circle cx="14" cy="9.6" r="1.25" fill="${c}"/><rect x="13.1" y="12.4" width="1.8" height="7" rx="0.9" fill="${c}"/>`)
  if (kind === 'scan')
    // A magnifier whose tick draws in: everything was read and checked.
    return s(`${MAGNIFIER(c)}<path d="M8.5 12.5 L11.3 15.2 L16.5 9.8" fill="none" stroke="${c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="12" stroke-dashoffset="12"><animate attributeName="stroke-dashoffset" values="12;12;0;0;12" keyTimes="0;0.4;0.52;0.9;1" dur="5s" begin="0.3s" repeatCount="indefinite"/></path>`)
  if (kind === 'scanWarn' || kind === 'scanError')
    // The magnifier finds something: a mark appears inside the lens.
    return s(`${MAGNIFIER(c)}<g><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.4;0.5;0.9;1" dur="5s" begin="0.3s" repeatCount="indefinite"/><rect x="11.6" y="8.4" width="1.8" height="5.2" rx="0.9" fill="${c}"/><circle cx="12.5" cy="16" r="1.1" fill="${c}"/></g>`)
  if (kind === 'stop')
    // An octagon whose outline expands and fades: the turn or the skill is held here.
    return s(`<g transform="translate(14 14)"><path d="M-3.4 -8.5 H3.4 L8.5 -3.4 V3.4 L3.4 8.5 H-3.4 L-8.5 3.4 V-3.4 Z" fill="none" stroke="${c}" stroke-width="1.4" vector-effect="non-scaling-stroke"><animate attributeName="opacity" values="0.7;0;0" keyTimes="0;0.7;1" dur="1.4s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="scale" values="1;1.55;1.55" keyTimes="0;0.7;1" dur="1.4s" repeatCount="indefinite"/></path></g><path d="M10.6 5.5 H17.4 L22.5 10.6 V17.4 L17.4 22.5 H10.6 L5.5 17.4 V10.6 Z" fill="${c}"/><rect x="9.5" y="12.8" width="9" height="2.4" rx="1.2" fill="#fff"/>`)
  if (kind === 'record')
    // A clipboard whose lines write themselves: a record, not a verdict.
    return s(`<rect x="6" y="5" width="16" height="20" rx="2.5" fill="none" stroke="${c}" stroke-width="1.8"/><rect x="10.5" y="3" width="7" height="4" rx="1.4" fill="${c}"/><path d="M9.5 12 H18.5" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-dasharray="9" stroke-dashoffset="9"><animate attributeName="stroke-dashoffset" values="9;0;0;9" keyTimes="0;0.1;0.85;1" dur="4.5s" begin="0.5s" repeatCount="indefinite"/></path><path d="M9.5 16 H18.5" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-dasharray="9" stroke-dashoffset="9"><animate attributeName="stroke-dashoffset" values="9;9;0;0;9" keyTimes="0;0.07;0.17;0.85;1" dur="4.5s" begin="0.5s" repeatCount="indefinite"/></path><path d="M9.5 20 H15" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-dasharray="6" stroke-dashoffset="6"><animate attributeName="stroke-dashoffset" values="6;6;0;0;6" keyTimes="0;0.14;0.24;0.85;1" dur="4.5s" begin="0.5s" repeatCount="indefinite"/></path>`)
  return s(`<g><animateTransform attributeName="transform" type="rotate" values="0 14 22;-6 14 22;6 14 22;0 14 22;0 14 22" keyTimes="0;0.08;0.16;0.24;1" dur="4s" begin="0.5s" repeatCount="indefinite"/><path d="M14 4.5 L24 22 H4 Z" fill="none" stroke="${c}" stroke-width="1.8" stroke-linejoin="round"/><rect x="13.1" y="11" width="1.8" height="6" rx="0.9" fill="${c}"/><circle cx="14" cy="19.4" r="1.1" fill="${c}"/></g>`)
}
// The path list's row icons: a filled folder, an outlined page, a dashed page for one that is not there.
function rowSvg(kind: PathGroup['rows'][number]['kind'], icon: string, meta: string): string {
  const page = 'M4.5 2 H10.5 L14 5.5 V15 C14 15.6 13.6 16 13 16 H4.5 C3.9 16 3.5 15.6 3.5 15 V3 C3.5 2.4 3.9 2 4.5 2 Z'
  if (kind === 'folder') return svg(18, `<path d="M2 5 C2 4.2 2.6 3.6 3.4 3.6 H7 L8.6 5.3 H14.6 C15.4 5.3 16 5.9 16 6.7 V13.6 C16 14.4 15.4 15 14.6 15 H3.4 C2.6 15 2 14.4 2 13.6 Z" fill="${icon}" opacity="0.85"/>`)
  if (kind === 'file') return svg(18, `<path d="${page}" fill="none" stroke="${icon}" stroke-width="1.4"/><path d="M10.5 2 V5.5 H14" fill="none" stroke="${icon}" stroke-width="1.4" stroke-linejoin="round"/>`)
  return svg(18, `<path d="${page}" fill="none" stroke="${meta}" stroke-width="1.3" stroke-dasharray="2.2 2"/>`)
}

/** Findings drawn on one card, and the last lines of a tool's output under each. */
const MAX_LINES = 8
const TAIL_LINES = 3

const TERMINAL_COLOR: Record<Card['kind'], string> = { error: 'error', edited: 'error', check: 'warning', warn: 'warning', retry: 'suggestion', note: 'subtle', stop: 'error', record: 'subtle', scan: 'success', scanWarn: 'warning', scanError: 'error' }
const TERMINAL_ICON: Record<Card['kind'], string> = { error: '✖', edited: '✖', check: '⏸', warn: '⚠', retry: '↻', note: 'ⓘ', stop: '⛔', record: '▤', scan: '✓', scanWarn: '⚠', scanError: '✖' }
const TERMINAL_ROW: Record<PathGroup['rows'][number]['kind'], string> = { folder: '▸', file: '·', missing: '∅', unknown: '?' }

/** The card element for a `ui.render` of ToolResult: terminal keeps theme colors, desktop the palette + SVG icon. */
export function drawCard($: Dollar, e: any, d: Card): any {
  const els = $.ui.resolve(e) as any
  const { Box, Text } = els
  const terminal = e.surface === 'terminal'
  const p = PALETTE[d.kind]
  // The terminal keeps theme colors so the card reads in any terminal palette.
  const strong = terminal ? TERMINAL_COLOR[d.kind] : p.strong
  const meta = terminal ? 'subtle' : p.meta
  const body = terminal ? 'text' : p.body
  const pic = (source: string, size: number, alt: string, fallback: string, color: string) => !terminal && els.Svg
    ? h(els.Svg, { source, alt, width: size, height: size, isInteractive: true })
    : h(Text, { color, bold: true }, fallback)
  const chip = (text: string, mono = true) =>
    h(Text, { mono, size: 'footnote', bold: !mono, color: strong, backgroundColor: terminal ? undefined : p.chip }, terminal ? `[${text}]` : ` ${text} `)
  // A finding's first line is its sentence; what follows is a tool's output (jq's line and column), of which the
  // last lines are shown, as format.md promises for a `run` check.
  const line = (l: Finding) => {
    if (!l.id) return h(Text, { color: body }, l.text)
    const [head, ...rest] = l.text.split('\n')
    const tail = rest.filter(x => x.trim()).slice(-TAIL_LINES)
    return h(Box, { flexDirection: 'column', gap: 'xs' },
      h(Box, { flexDirection: 'row', gap: 'sm' }, chip(l.id), h(Text, { color: body }, head)),
      ...tail.map(x => h(Text, { mono: true, size: 'footnote', color: meta }, x)))
  }
  const more = d.lines.length - MAX_LINES
  // The delete preview: a header per action (what, how many, from where, to where), then one row per path,
  // the folder part quiet and the name strong; a meta that warns (missing, would overwrite) stands out.
  const groups = d.paths?.length ? pathGroups(d.paths) : []
  const list = groups.length
    ? [h(Box, { flexDirection: 'column', gap: 'xs', borderStyle: terminal ? undefined : 'round', borderColor: terminal ? undefined : p.border, backgroundColor: terminal ? undefined : '#FFFFFF', padding: terminal ? undefined : 'sm' },
        ...groups.flatMap(g => [
          h(Box, { flexDirection: 'row', gap: 'sm', flexWrap: 'wrap' },
            chip(g.verb, false),
            h(Text, { color: body }, g.count),
            ...(g.from ? [h(Text, { size: 'footnote', color: meta }, '從'), h(Text, { mono: true, size: 'footnote', color: meta }, g.from)] : []),
            ...(g.to !== undefined ? [h(Text, { color: meta }, '→'), h(Text, { mono: true, size: 'footnote', bold: true, color: strong }, g.to)] : [])),
          ...g.rows.map(r => h(Box, { flexDirection: 'row', gap: 'sm', paddingLeft: terminal ? 2 : 'md' },
            pic(rowSvg(r.kind, p.icon, p.meta), 18, r.kind, TERMINAL_ROW[r.kind], meta),
            ...(r.dir ? [h(Text, { mono: true, size: 'footnote', color: meta }, r.dir)] : []),
            h(Text, { mono: true, size: 'footnote', bold: true, color: strong }, r.name),
            ...(r.meta ? [h(Text, { size: 'footnote', bold: !!r.warn, color: r.warn ? strong : meta }, r.meta)] : []))),
        ]))]
    : []
  return h(Box, { flexDirection: 'row', gap: 'md', borderStyle: 'round', borderColor: terminal ? strong : p.border, backgroundColor: terminal ? undefined : p.bg, padding: 'md' },
    pic(iconSvg(d.kind), 28, d.title ?? d.meta, TERMINAL_ICON[d.kind], strong),
    h(Box, { flexDirection: 'column', gap: 'sm', flexShrink: 1 },
      d.title
        ? h(Box, { flexDirection: 'row', gap: 'md', flexWrap: 'wrap' },
            h(Text, { bold: true, color: strong }, d.title),
            h(Text, { size: 'footnote', color: meta }, d.meta))
        : h(Text, { size: 'footnote', color: meta }, d.meta),
      ...d.lines.slice(0, MAX_LINES).map(line),
      ...(more > 0 ? [h(Text, { size: 'footnote', color: meta }, `還有 ${more} 條沒列出`)] : []),
      ...list,
      ...(d.footer ? [h(Text, { size: 'footnote', color: meta }, d.footer)] : [])))
}
