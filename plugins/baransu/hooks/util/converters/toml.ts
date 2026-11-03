// The TOML subset check files and collections are written in:
//   key = "s" | 's' | ["a", 'b']      # comments
//   [check.<id>]  [check.<id>.options]  — tables, nested by their dotted header
//   [[extends]]                          — an array of tables, in written order
// Anything outside it that could be quietly misread — an inline table, a dotted key, a table or key written
// twice — is an error naming its line, never a guess.

import type { RawCheck, RawTable, RuleConverter } from '../../engine'

export const toml: RuleConverter = {
  name: 'toml',
  parse(source: string): RawCheck {
    return parseToml(source)
  },
}

type Mutable = { [key: string]: unknown }

function parseToml(src: string): RawTable {
  const root: Mutable = {}
  let table: Mutable = root
  const defined = new Set<string>()
  let i = 0
  const lineAt = (at: number) => src.slice(0, at).split('\n').length
  const fail = (msg: string, at = i): never => {
    throw new Error(`line ${lineAt(at)}: ${msg}`)
  }
  const skip = () => {
    while (i < src.length) {
      const c = src[i]
      if (c === ' ' || c === '\t' || c === '\r' || c === '\n' || c === ',') i++
      else if (c === '#') while (i < src.length && src[i] !== '\n') i++
      else break
    }
  }
  const str = (): string => {
    const q = src[i]
    if (q !== '"' && q !== "'") fail(`expected a string near "${src.slice(i, i + 12)}"`)
    const start = i
    i++
    let s = ''
    while (i < src.length && src[i] !== q) {
      if (q === '"' && src[i] === '\\') {
        const n = src[i + 1]
        s += n === 'n' ? '\n' : n === 't' ? '\t' : n
        i += 2
      } else s += src[i++]
    }
    if (src[i] !== q) fail('unterminated string', start)
    i++
    return s
  }
  const value = (): string | string[] => {
    skip()
    if (src[i] === '{') fail('an inline table is not read: write it as its own [table]')
    if (src[i] === '[') {
      const start = i
      i++
      const arr: string[] = []
      for (;;) {
        skip()
        if (src[i] === ']') {
          i++
          return arr
        }
        if (i >= src.length) fail('unterminated array', start)
        arr.push(str())
      }
    }
    if (src[i] === '"' || src[i] === "'") return str()
    const m = /^[^\s#]+/.exec(src.slice(i))
    if (!m) fail('missing value')
    i += m![0].length
    return m![0]
  }
  /** The table a dotted header names, created on the way; `[[x]]` appends a new table to the list x. */
  const open = (path: string[], array: boolean, at: number): Mutable => {
    let t = root
    for (let k = 0; k < path.length; k++) {
      const key = path[k]
      const last = k === path.length - 1
      if (last && array) {
        const list = (t[key] ??= []) as unknown
        if (!Array.isArray(list)) fail(`${path.join('.')} is not a list of tables`, at)
        const fresh: Mutable = {}
        ;(list as Mutable[]).push(fresh)
        return fresh
      }
      let next = t[key]
      if (Array.isArray(next)) next = next[next.length - 1]
      if (next === undefined) next = t[key] = {}
      if (typeof next !== 'object' || next === null) fail(`${path.slice(0, k + 1).join('.')} is a value, not a table`, at)
      t = next as Mutable
    }
    const name = path.join('.')
    if (defined.has(name)) fail(`[${name}] defined twice`, at)
    defined.add(name)
    return t
  }

  for (;;) {
    skip()
    if (i >= src.length) break
    if (src[i] === '[') {
      const at = i
      const array = src[i + 1] === '['
      const end = src.indexOf(array ? ']]' : ']', i)
      const nl = src.indexOf('\n', i)
      if (end < 0 || (nl >= 0 && nl < end)) fail('unterminated table header', at)
      const header = src.slice(i + (array ? 2 : 1), end).trim()
      if (!/^[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*$/.test(header)) fail(`table name "${header}" is not read`, at)
      i = end + (array ? 2 : 1)
      table = open(header.split('.'), array, at)
      continue
    }
    const keyAt = i
    const m = /^[A-Za-z0-9_-]+/.exec(src.slice(i))
    if (!m) fail(`unexpected "${src.slice(i, i + 12)}"`)
    i += m![0].length
    if (src[i] === '.') fail(`dotted key "${m![0]}.…" is not read: write [${m![0]}] as a table`, keyAt)
    skip()
    if (src[i] !== '=') fail(`expected = after ${m![0]}`)
    i++
    const key = m![0]
    if (Object.prototype.hasOwnProperty.call(table, key)) fail(`${key} written twice`, keyAt)
    table[key] = value()
  }
  return root as RawTable
}
