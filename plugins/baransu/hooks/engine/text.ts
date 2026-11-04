// What the engine says, in the person's words: the notes, card titles and footers, restate and report
// instructions — 8.39 lint.ts's strings, unchanged. Strings tied to one check sit with that check (moments.ts,
// shell.ts's preview lines); the adapter keeps only the words of its own failures (config.ts 「設定讀不懂：…」,
// ports.ts 「無法執行：…」), the same words as today. All pure.

import type { Card, Check, Finding, PathRow } from './types'

export const MOMENT = { edit: '改檔', commit: 'commit 前', done: '收尾前', bash: '指令', manual: '手動', skill: 'skill 前', reply: '回應後', stop: '結束這一輪前', agent: 'subagent 結束後', compact: '壓縮', file: 'Claude 之外改檔後', after: '時間到' } as const

/** `lint · <moment> · <where>：N error、M warn` and one line per finding. */
export function render(moment: keyof typeof MOMENT, where: string, all: readonly Finding[]): string {
  // A quiet finding is for the person's card only (lint-scope postcondition 14).
  const findings = all.filter(f => !f.quiet)
  const errors = findings.filter(f => f.severity === 'error').length
  const warns = findings.filter(f => f.severity === 'warn').length
  const head = `lint · ${MOMENT[moment]}${where ? ' · ' + where : ''}：${errors} error、${warns} warn`
  const mark = { error: '✖', check: '⏸', warn: '⚠', retry: '↻', note: '·' } as const
  return [head, ...findings.map(f => `${mark[f.severity]} ${f.id}：${f.text}`)].join('\n')
}

/** The card for a set of findings, notes left out except quiet ones (they exist for the card); null when
 *  nothing is left to show. A card of quiet notes alone is the 只給你看 card (`note`). `edited`: the act already
 *  changed the file, so an error there is the 已改 card. */
export function summarize(moment: string, findings: readonly Finding[], o: { edited?: boolean } = {}): Card | null {
  const shown = findings.filter(f => f.severity !== 'note' || f.quiet)
  if (!shown.length) return null
  const errors = shown.filter(f => f.severity === 'error').length
  const warns = shown.filter(f => f.severity === 'warn').length
  const redos = shown.filter(f => f.severity === 'retry').length
  const counts = [errors ? `${errors} error` : '', warns ? `${warns} warn` : '', redos ? `${redos} 重新` : ''].filter(Boolean).join('、')
  const meta = `lint · ${moment}${counts ? ` · ${counts}` : ''}`
  if (errors && o.edited) return { kind: 'edited', title: '改好了，但這個檔有 error', meta, lines: shown, footer: '下一步先修這裡' }
  return { kind: errors ? 'error' : warns ? 'warn' : redos ? 'retry' : 'note', meta, lines: shown }
}

/** A card as the plain row a surface without the band shows: its head, one line per finding, its footer. */
export function cardText(d: Card): string {
  const mark = { error: '✖', check: '⏸', warn: '⚠', retry: '↻', note: '·' } as const
  return [
    d.title ? `${d.meta}：${d.title}` : d.meta,
    ...d.lines.map(f => `${mark[f.severity]} ${f.id ? `${f.id}：` : ''}${f.text}`),
    ...(d.paths ?? []).map(r => `  ${r.verb} ${r.path}${r.to ? ` → ${r.to}` : ''}${r.meta ? `（${r.meta}）` : ''}`),
    ...(d.footer ? [`→ ${d.footer}`] : []),
  ].join('\n')
}

/** The card for a set of findings, the same as summarize, or a card of its notes when summarize leaves nothing. */
export function cardOf(moment: string, findings: readonly Finding[], o: { kind?: Card['kind']; title?: string; footer?: string } = {}): Card {
  const d = summarize(moment, findings) ?? { kind: 'note' as const, meta: `lint · ${moment}`, lines: [...findings] }
  return { ...d, ...(o.kind ? { kind: o.kind } : {}), ...(o.title ? { title: o.title } : {}), ...(o.footer ? { footer: o.footer } : {}) }
}

/** The card of every check run before a skill or at /lint, as the design canvas draws it: /ship told to stop, the
 *  record before /review, or what the run found. `head` is render()'s first line (`lint · 收尾前 · /ship：…`). */
export function skillCard(head: string, findings: readonly Finding[], stop: boolean, review: boolean): Card {
  const meta = head.replace('：', ' · ')
  const lines = [...findings]
  if (stop) return { kind: 'stop', title: '停下，不要 commit', meta, lines, footer: '把 error 回報給使用者，修好再收尾' }
  if (review) return { kind: 'record', title: 'Lint 紀錄', meta, lines, footer: '照 review 自己的判定規則讀' }
  const loud = findings.filter(f => !f.quiet)
  const errors = loud.filter(f => f.severity === 'error').length
  const warns = loud.filter(f => f.severity === 'warn').length
  if (errors) return { kind: 'scanError', title: `跑完，發現 ${errors} 個 error${warns ? `、${warns} 個 warn` : ''}`, meta, lines }
  if (warns) return { kind: 'scanWarn', title: `跑完，發現 ${warns} 個 warn`, meta, lines }
  return { kind: 'scan', title: '跑完，沒有發現', meta, lines }
}

/** The delete preview's rows as the design canvas "Lint 卡片設計" groups them: one header per action and
 *  destination, in the order first met, counting folders and files; under a destination, a folder every row
 *  shares moves up into the header (`from`), so each row shows only what differs. A row splits into its folder
 *  part, drawn quiet, and its name, drawn strong. */
export type PathGroup = { verb: string; count: string; from?: string; to?: string; rows: { kind: PathRow['kind']; dir: string; name: string; meta?: string; warn?: boolean }[] }
export function pathGroups(rows: readonly PathRow[]): PathGroup[] {
  const groups: { verb: string; to?: string; rows: PathRow[] }[] = []
  for (const r of rows) {
    const g = groups.find(x => x.verb === r.verb && x.to === r.to)
    if (g) g.rows.push(r)
    else groups.push({ verb: r.verb, ...(r.to !== undefined ? { to: r.to } : {}), rows: [r] })
  }
  const split = (p: string) => {
    const m = /^(.*\/)?([^/]+\/?)$/.exec(p)
    return { dir: m?.[1] ?? '', name: m?.[2] ?? p }
  }
  return groups.map(g => {
    const parts = g.rows.map(r => ({ r, ...split(r.path) }))
    const shared = g.to !== undefined && parts.every(x => x.dir && x.dir === parts[0].dir) ? parts[0].dir : ''
    const folders = g.rows.filter(r => r.kind === 'folder').length
    const files = g.rows.filter(r => r.kind === 'file' || r.kind === 'missing').length
    const other = g.rows.length - folders - files
    const count = [folders ? `${folders} 個資料夾` : '', files ? `${files} 個檔案` : '', other ? `${other} 項` : ''].filter(Boolean).join('、')
    return {
      verb: g.verb, count, ...(shared ? { from: shared } : {}), ...(g.to !== undefined ? { to: g.to } : {}),
      rows: parts.map(({ r, dir, name }) => ({ kind: r.kind, dir: shared ? '' : dir, name, ...(r.meta ? { meta: r.meta } : {}), ...(r.warn ? { warn: true } : {}) })),
    }
  })
}

/** Han characters and letters, code / links / identifiers left out. */
export function hanShare(text: string): { han: number; letters: number } {
  // Code, links and identifiers (session.start, lint.ts, camelCase, snake_case, a/path) are not prose.
  const prose = text.replace(/```[\s\S]*?```/g, ' ').replace(/`[^`\n]*`/g, ' ').replace(/https?:\/\/\S+/g, ' ')
    .replace(/[A-Za-z0-9_$-]*[._/\\][A-Za-z0-9_$./\\-]+|\b[a-z]+[A-Z][A-Za-z0-9]*\b/g, ' ')
  return { han: (prose.match(/\p{Script=Han}/gu) ?? []).length, letters: (prose.match(/\p{L}/gu) ?? []).length }
}

/** The note asking the model to restate an English block in the user's language (check.redo replaces the default). */
export function restateNote(c: Check, userLanguage: string | undefined, text: string): string {
  const how = c.redo ?? `先照 /baransu:huh 的方式，用使用者的語言（${userLanguage}）把這段重新說一次——白話、不加術語，說的是同一件事；之後寫給使用者看的文字一律用這個語言。`
  return `baransu lint（${c.id}，重新）：剛才給使用者的那段寫成英文了。${how}那段原文：\n"""\n${text}\n"""`
}

export function slipHead(text: string): string {
  return `${text.split('\n')[0].slice(0, 40)}…`
}

/** Does what the person typed read as a correction (又犯、不是這樣、again、wrong …). 說過／講過 followed by 話 is
 *  talk about speech (查說過話的 bug), not "I told you already". */
export const CORRECTION = /又犯|又錯|又忘|又來了|不是這樣|(?<!對)不對(?!勁)|錯了|說過(?!話)|講過(?!話)|跟你說|別再|不要再|為什麼又|\bagain\b|\bwrong\b|told you|\bstop doing\b|don'?t do that/i
