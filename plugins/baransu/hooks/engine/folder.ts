// The lint folder's files → its settings and the checks in force. Pure: the config source scans `.claude/lint/`
// once and hands every file it found here as text; this decides what they mean. The one place the layout is
// read, so which file says what, and which wins, is written once.
//
//   .claude/lint/
//     config.toml        [settings] (converter, sgconfig) · [[extends]] the sets in force · [check.<id>] patches
//     sets/baransu/*     the preset's sets, as /lint sync wrote them (replaced whole by the next sync)
//     sets/local/*       the project's own sets (sync never touches them)
//     rules/ scripts/ sgconfig.yml

import { readCheck } from './check'
import type { RuleConverter } from './ports'
import { resolveSets } from './sets'
import type { Check, Finding, RawTable } from './types'

/** The one config file, relative to the lint folder. Always TOML: it names the converter the sets are read with. */
export const CONFIG = 'config.toml'

export type LintSettings = {
  /** The converter that reads the sets (`toml` today). */
  readonly converter: string
  /** ast-grep's config, relative to the lint folder. Its own `ruleDirs` says where the rules are. */
  readonly sgconfig: string
}
export const DEFAULTS: LintSettings = { converter: 'toml', sgconfig: 'sgconfig.yml' }

/** The shape before 8.44: one file per check, a JSON settings file, `lint.toml`. Read as a problem pointing to
 *  /lint sync, never as rules (sole user; sync moves them). */
const OLD = (p: string) => p === 'lint.json' || p === 'lint.toml' || p.startsWith('checks/')

/**
 * `files`: every file of the scan, keyed by its path relative to the lint folder (`config.toml`,
 * `sets/baransu/git.toml`, `sets/local/repo.toml`), forward slashes. `converters`: by name; `toml` reads
 * config.toml whatever the sets use.
 *
 *   config.toml absent → no checks; when files of the old layout are there, one problem naming /lint sync.
 *   [settings]          → converter and sgconfig over DEFAULTS; a value that is not a string, an unknown
 *                         converter, or an sgconfig outside the lint folder is a problem and keeps the default.
 *   [[extends]] / [check.<id>] → resolveSets over the sets the scan found (a set it did not find is a problem),
 *                         each result through readCheck.
 * Problems read 「設定讀不懂：<where>：<text>」. Never throws.
 */
export function configFromFiles(
  files: ReadonlyMap<string, string>,
  converters: (name: string) => RuleConverter | undefined,
): { settings: LintSettings; checks: Check[]; problems: Finding[] } {
  const checks: Check[] = []
  const problems: Finding[] = []
  const bad = (id: string, where: string, text: string) => problems.push({ id, severity: 'warn', text: `設定讀不懂：${where}：${text}` })
  let settings = DEFAULTS

  const old = [...files.keys()].filter(OLD)
  const text = files.get(CONFIG)
  const listed = `${old.slice(0, 3).join('、')}${old.length > 3 ? ' …' : ''}`
  // Without config.toml the old files are all there is: a problem. Beside a config.toml they are what a sync
  // left to delete once its result is checked: a note, so "no 設定讀不懂 is left" can be reached.
  if (old.length && text === undefined)
    bad('config.toml', '.claude/lint', `還是舊的版面（${listed}）：跑 /lint sync 搬進 config.toml 與 sets/，這些檔裡的規則沒有生效`)
  else if (old.length)
    problems.push({ id: 'config.toml', severity: 'note', text: `舊版面的檔還在（${listed}），沒有生效：確認 config.toml 讀出的規則沒錯後，跑 migrate-layout.py --remove 刪掉` })

  const toml = converters('toml')
  if (text === undefined || !toml) return { settings, checks, problems }
  let doc: RawTable
  try {
    doc = toml.parse(text)
  } catch (err) {
    bad('config.toml', CONFIG, (err as Error).message)
    return { settings, checks, problems }
  }

  const given = doc.settings && typeof doc.settings === 'object' && !Array.isArray(doc.settings) ? (doc.settings as RawTable) : {}
  const field = (name: keyof LintSettings): string => {
    const v = given[name]
    if (v === undefined) return DEFAULTS[name]
    if (typeof v !== 'string') {
      bad('config.toml', CONFIG, `[settings] ${name} 要是字串，改用預設的 ${DEFAULTS[name]}`)
      return DEFAULTS[name]
    }
    return v
  }
  let converterName = field('converter')
  let converter = converters(converterName)
  if (!converter) {
    bad('config.toml', CONFIG, `沒有叫 ${converterName} 的轉換器，改用 toml`)
    converterName = 'toml'
    converter = toml
  }
  // Relative to .claude/lint; may reach the project's own (`../../sgconfig.yml`): the config source checks it
  // stays inside the project, which only it knows.
  let sgconfig = field('sgconfig').replace(/\\/g, '/').replace(/^\.\//, '')
  if (/^([A-Za-z]:)?\//.test(sgconfig)) {
    bad('config.toml', CONFIG, `[settings] sgconfig 要寫成相對 .claude/lint 的路徑（${sgconfig}），改用預設的 ${DEFAULTS.sgconfig}`)
    sgconfig = DEFAULTS.sgconfig
  }
  settings = { converter: converterName, sgconfig }

  const sets = new Map<string, RawTable>()
  for (const e of Array.isArray(doc.extends) ? (doc.extends as RawTable[]) : []) {
    const p = typeof e.set === 'string' ? e.set.replace(/\\/g, '/').replace(/^\.\//, '') : ''
    const t = files.get(p)
    if (!p || sets.has(p) || t === undefined) continue
    try {
      sets.set(p, converter.parse(t))
    } catch (err) {
      bad('config.toml', p, (err as Error).message)
    }
  }
  const r = resolveSets(doc, sets)
  for (const p of r.problems) bad('config.toml', CONFIG, p)
  for (const c of r.checks) {
    const read = readCheck(c.id, c.raw)
    if (read.kind === 'check') checks.push(read.check)
    else if (read.kind === 'problems')
      for (const p of read.problems) bad(c.id, `${c.id}（${c.origin.forbid ?? c.origin.run ?? c.origin.builtin ?? c.origin.severity ?? CONFIG}）`, `${p}（這條檢查沒有生效）`)
  }
  return { settings, checks, problems }
}
