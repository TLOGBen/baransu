// The TOML subset check files are written in: key = "s" | 's' | ["a", 'b'], # comments.
// Moved unchanged from 8.39's lint.ts parseToml (git show 58de798a:plugins/baransu/hooks/lint.ts); only its output type is named now.

import type { RawCheck, RuleConverter } from '../../engine'

export const toml: RuleConverter = {
  name: 'toml',
  extension: '.toml',
  parse(source: string): RawCheck {
    return parseToml(source)
  },
}

function parseToml(src: string): Record<string, string | string[]> {
  const out: Record<string, string | string[]> = {}
  let i = 0
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
    if (q !== '"' && q !== "'") throw new Error(`expected a string near "${src.slice(i, i + 12)}"`)
    i++
    let s = ''
    while (i < src.length && src[i] !== q) {
      if (q === '"' && src[i] === '\\') {
        const n = src[i + 1]
        s += n === 'n' ? '\n' : n === 't' ? '\t' : n
        i += 2
      } else s += src[i++]
    }
    if (src[i] !== q) throw new Error('unterminated string')
    i++
    return s
  }
  const value = (): string | string[] => {
    skip()
    if (src[i] === '[') {
      i++
      const arr: string[] = []
      for (;;) {
        skip()
        if (src[i] === ']') { i++; return arr }
        if (i >= src.length) throw new Error('unterminated array')
        arr.push(str())
      }
    }
    if (src[i] === '"' || src[i] === "'") return str()
    const m = /^[^\s#]+/.exec(src.slice(i))
    if (!m) throw new Error('missing value')
    i += m[0].length
    return m[0]
  }
  for (;;) {
    skip()
    if (i >= src.length) break
    const m = /^[A-Za-z0-9_-]+/.exec(src.slice(i))
    if (!m) throw new Error(`unexpected "${src.slice(i, i + 12)}"`)
    i += m[0].length
    skip()
    if (src[i] !== '=') throw new Error(`expected = after ${m[0]}`)
    i++
    out[m[0]] = value()
  }
  return out
}
