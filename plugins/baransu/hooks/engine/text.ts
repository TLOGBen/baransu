// What the engine says, in the person's words: the notes, card titles and footers, restate and report
// instructions — 8.39 lint.ts's strings, unchanged. Strings tied to one check sit with that check (moments.ts,
// shell.ts's preview lines); the adapter keeps only the words of its own failures (config.ts 「設定讀不懂：…」,
// ports.ts 「無法執行：…」), the same words as today. All pure.

import type { Card, Check, Finding } from './types'

export const MOMENT = { edit: '改檔後', commit: 'commit 前', done: '收尾前', bash: '指令前', manual: '手動', skill: 'skill 前' } as const

/** `lint · <moment> · <where>：N error、M warn` and one line per finding. */
export function render(moment: keyof typeof MOMENT, where: string, findings: readonly Finding[]): string {
  const errors = findings.filter(f => f.severity === 'error').length
  const warns = findings.filter(f => f.severity === 'warn').length
  const head = `lint · ${MOMENT[moment]}${where ? ' · ' + where : ''}：${errors} error、${warns} warn`
  const mark = { error: '✖', warn: '⚠', redo: '↻', note: '·' } as const
  return [head, ...findings.map(f => `${mark[f.severity]} ${f.id}：${f.text}`)].join('\n')
}

/** The card for a set of findings, notes left out; null when nothing is left to show. */
export function summarize(moment: string, findings: readonly Finding[]): Card | null {
  const shown = findings.filter(f => f.severity !== 'note')
  if (!shown.length) return null
  const errors = shown.filter(f => f.severity === 'error').length
  const warns = shown.filter(f => f.severity === 'warn').length
  const redos = shown.filter(f => f.severity === 'redo').length
  const counts = [errors ? `${errors} error` : '', warns ? `${warns} warn` : '', redos ? `${redos} 重新` : ''].filter(Boolean).join('、')
  return { kind: errors ? 'error' : warns ? 'warn' : 'redo', meta: `lint · ${moment} · ${counts}`, lines: shown }
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
