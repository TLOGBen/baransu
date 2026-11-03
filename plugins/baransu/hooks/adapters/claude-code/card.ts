// Drawing a Card with the host's UI elements. Moved unchanged from 8.39's lint.ts (git show 58de798a:plugins/baransu/hooks/lint.ts) (PALETTE, SHIELD, iconSvg,
// card); it takes the engine's Card value and writes no sentence of its own.

import type { Card, Finding } from '../../engine'
import type { Dollar } from './ports'

// Colors from the design canvas "Lint 卡片樣式": tint, border, strong text, meta text, body text, icon.
const PALETTE = {
  error: { bg: '#FDF3F3', border: '#F2CFCF', strong: '#8E1B1B', meta: '#A35A5A', body: '#3B2020', icon: '#D63B3B', chip: '#F0C6C6' },
  hold: { bg: '#FDF7EA', border: '#EFD9A6', strong: '#7A4A06', meta: '#9C6E2A', body: '#3A2A0E', icon: '#E39A1C', chip: '#F0DDB0' },
  warn: { bg: '#FFFBF2', border: '#F3E3BD', strong: '#7A4A06', meta: '#9C6E2A', body: '#3A2A0E', icon: '#C98A16', chip: '#F0DDB0' },
  redo: { bg: '#EFF5FD', border: '#C8DAF2', strong: '#1C4E8E', meta: '#4E70A3', body: '#1D2A3C', icon: '#2F6FD0', chip: '#C8DAF2' },
} as const
const SHIELD = 'M14 3.5 L22.5 6.8 V13 C22.5 18.4 18.9 22.3 14 24.5 C9.1 22.3 5.5 18.4 5.5 13 V6.8 Z'
function iconSvg(kind: Card['kind']): string {
  const c = PALETTE[kind].icon
  const svg = (body: string) => `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28" overflow="visible">${body}</svg>`
  if (kind === 'error')
    return svg(`<circle cx="14" cy="14" r="10" fill="none" stroke="${c}" stroke-width="1.6"><animate attributeName="r" values="9;14;14" keyTimes="0;0.7;1" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0;0" keyTimes="0;0.7;1" dur="1.6s" repeatCount="indefinite"/></circle><path d="${SHIELD}" fill="${c}"/><rect x="12.8" y="8.6" width="2.4" height="7" rx="1.2" fill="#fff"/><circle cx="14" cy="18.8" r="1.5" fill="#fff"/>`)
  if (kind === 'hold')
    return svg(`<path d="${SHIELD}" fill="${c}"/><g><animate attributeName="opacity" values="1;0.45;1" dur="1.8s" repeatCount="indefinite"/><rect x="10.6" y="9.4" width="2.4" height="8.4" rx="1" fill="#fff"/><rect x="15" y="9.4" width="2.4" height="8.4" rx="1" fill="#fff"/></g>`)
  if (kind === 'redo')
    return svg(`<g><animateTransform attributeName="transform" type="rotate" from="0 14 14" to="360 14 14" dur="6s" repeatCount="indefinite"/><path d="M21.5 11.5 A8 8 0 1 0 22 16.5" fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round"/><path d="M22.8 6.8 L22.2 12.2 L16.9 11.2" fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g>`)
  return svg(`<path d="M14 4.5 L24 22 H4 Z" fill="none" stroke="${c}" stroke-width="1.8" stroke-linejoin="round"/><rect x="13.1" y="11" width="1.8" height="6" rx="0.9" fill="${c}"/><circle cx="14" cy="19.4" r="1.1" fill="${c}"/>`)
}

/** The card element for a `ui.render` of ToolResult: terminal keeps theme colors, desktop the palette + SVG icon. */
export function drawCard($: Dollar, e: any, d: Card): any {
  const els = $.ui.resolve(e) as any
  const { Box, Text } = els
  const terminal = e.surface === 'terminal'
  const p = PALETTE[d.kind]
  // The terminal keeps theme colors so the card reads in any terminal palette.
  const strong = terminal ? (d.kind === 'error' ? 'error' : d.kind === 'redo' ? 'suggestion' : 'warning') : p.strong
  const meta = terminal ? 'subtle' : p.meta
  const body = terminal ? 'text' : p.body
  const icon = !terminal && els.Svg
    ? h(els.Svg, { source: iconSvg(d.kind), alt: d.title ?? d.meta, width: 28, height: 28, isInteractive: true })
    : h(Text, { color: strong, bold: true }, { hold: '⏸', error: '✖', warn: '⚠', redo: '↻' }[d.kind])
  const line = (l: Finding) => l.id
    ? h(Box, { flexDirection: 'row', gap: 'sm' },
        h(Text, { mono: true, size: 'footnote', color: strong, backgroundColor: terminal ? undefined : '#FFFFFF' }, terminal ? `[${l.id}]` : ` ${l.id} `),
        h(Text, { color: body }, l.text.split('\n')[0]))
    : h(Text, { color: body }, `· ${l.text}`)
  return h(Box, { flexDirection: 'row', gap: 'md', borderStyle: 'round', borderColor: terminal ? strong : p.border, backgroundColor: terminal ? undefined : p.bg, padding: 'md' },
    icon,
    h(Box, { flexDirection: 'column', gap: 'sm', flexShrink: 1 },
      d.title
        ? h(Box, { flexDirection: 'row', gap: 'md', flexWrap: 'wrap' },
            h(Text, { bold: true, color: strong }, d.title),
            h(Text, { size: 'footnote', color: meta }, d.meta))
        : h(Text, { size: 'footnote', color: meta }, d.meta),
      ...d.lines.slice(0, 6).map(line),
      ...(d.footer ? [h(Text, { size: 'footnote', color: meta }, d.footer)] : [])))
}
