import type { Language, SourceFact, TreeView } from '../../engine/ports'
import { dirOf, escapeRe, stemOf } from './paths'

const VIS = String.raw`(?:pub(?:\([\w:]+\))?\s+)?`
const MOD = new RegExp(String.raw`^\s*` + VIS + String.raw`mod\s+(\w+)\s*;`)
const USE = new RegExp(String.raw`^\s*` + VIS + String.raw`use\s+([\s\S]+?);`)
const ITEM = /^\s*pub(?:\([\w:]+\))?\s+(?:async\s+|unsafe\s+|const\s+)*(?:fn|struct|enum|trait|type|mod)\s+(\w+)/

export const rust: Language = {
  id: 'rust',
  exts: ['rs'],
  // use crate::a::b; · use super::x; · mod x; · pub fn|struct|enum|trait N
  lines: String.raw`^\s*(pub(\([\w:]+\))?\s+)?(use\s+[\w:{}, *]+|mod\s+\w+\s*;|fn\s+\w|struct\s+\w|enum\s+\w|trait\s+\w)`,
  /** A `use … {` with no matching `}` on the line continues until `;` (rustfmt splits long brace lists). */
  continues(line: string): string | null {
    if (!new RegExp(String.raw`^\s*` + VIS + String.raw`use\b`).test(line)) return null
    const open = (line.match(/\{/g) ?? []).length
    const close = (line.match(/\}/g) ?? []).length
    return open > close && !line.includes(';') ? ';' : null
  },
  /** `mod x;` → import of child module x; `use crate::a::{b, c}` → crate::a::b, crate::a::c, also
   *  when joined from several lines and with nested braces (`{b::{c, d}, e}`); `pub fn|struct|…` → export. */
  read(_path: string, line: string): readonly SourceFact[] {
    const m = MOD.exec(line)
    if (m) return [{ kind: 'import', spec: `mod:${m[1]}` }]
    const u = USE.exec(line)
    // `x as y` is dropped before whitespace goes, so `b as c` cannot run together into one name.
    if (u) return expandUse(u[1].replace(/\s+as\s+\w+/g, '').replace(/\s+/g, '')).map(spec => ({ kind: 'import' as const, spec }))
    const i = ITEM.exec(line)
    return i ? [{ kind: 'export', name: i[1] }] : []
  },
  /**
   * Module path → file: the crate root is the nearest folder holding lib.rs or main.rs above `from`;
   * crate::a::b tries a/b.rs, a/b/mod.rs, then a.rs (b an item, not a module); self:: and super:: from `from`'s
   * own module; `mod x;` → x.rs or x/mod.rs beside `from` (beside its folder for a non-mod.rs file:
   * foo.rs → foo/x.rs). External crates (`use serde::…`) → []. Workspace crates by name → [] (design: traps).
   */
  resolve(spec: string, from: string, tree: TreeView): readonly string[] {
    const file = (base: string) => [`${base}.rs`, `${base}/mod.rs`].find(t => tree.files.has(t))
    if (spec.startsWith('mod:')) {
      const hit = file(join(moduleDir(from), spec.slice(4)))
      return hit ? [hit] : []
    }
    const segs = spec.split('::').filter(s => s && s !== '*' && s !== 'self')
    const head = spec.split('::')[0]
    let base: string
    let rest: string[]
    if (head === 'crate') {
      const root = crateRoot(from, tree)
      if (root === undefined) return []
      base = root
      rest = segs.slice(1)
    } else if (head === 'self') {
      base = moduleDir(from)
      rest = segs
    } else if (head === 'super') {
      let dir = moduleDir(from)
      const parts = spec.split('::')
      let k = 0
      while (parts[k] === 'super') {
        dir = dirOf(dir)
        k++
      }
      base = dir
      rest = parts.slice(k).filter(s => s && s !== '*' && s !== 'self')
    } else return []
    // The longest prefix of the path that is a module file: crate::a::b::Item → a/b.rs.
    for (let k = rest.length; k >= 1; k--) {
      const hit = file(join(base, rest.slice(0, k).join('/')))
      if (hit) return [hit]
    }
    return []
  },
  /** `mod <stem>;` or a `use` path whose last module segment is the file's module name. */
  importerPattern(path: string): string | null {
    const stem = stemOf(path)
    if (stem === 'lib' || stem === 'main') return null
    const name = stem === 'mod' ? (path.split('/').slice(-2, -1)[0] ?? '') : stem
    if (!name) return null
    const n = escapeRe(name)
    return String.raw`^\s*(pub(\([\w:]+\))?\s+)?(mod\s+` + n + String.raw`\s*;|use\s+[\w:{}, *]*\b` + n + String.raw`\b)`
  },
}

const join = (a: string, b: string) => (a ? `${a}/${b}` : b)

/** The folder a file's child modules live in: its own folder for mod.rs / lib.rs / main.rs, else <dir>/<stem>. */
function moduleDir(from: string): string {
  const stem = stemOf(from)
  return stem === 'mod' || stem === 'lib' || stem === 'main' ? dirOf(from) : join(dirOf(from), stem)
}

/** The nearest folder above `from` holding lib.rs or main.rs. */
function crateRoot(from: string, tree: TreeView): string | undefined {
  let dir = dirOf(from)
  for (;;) {
    if (tree.files.has(join(dir, 'lib.rs')) || tree.files.has(join(dir, 'main.rs'))) return dir
    if (!dir) return undefined
    dir = dirOf(dir)
  }
}

/** `a::{b, c::{d, e}}` → a::b, a::c::d, a::c::e. Whitespace and `as` renames already removed. */
export function expandUse(t: string): string[] {
  const open = t.indexOf('{')
  if (open < 0) return [t]
  const prefix = t.slice(0, open)
  const inner = t.slice(open + 1, t.lastIndexOf('}'))
  const parts: string[] = []
  let depth = 0
  let cur = ''
  for (const ch of inner) {
    if (ch === '{') depth++
    if (ch === '}') depth--
    if (ch === ',' && depth === 0) {
      parts.push(cur)
      cur = ''
    } else cur += ch
  }
  if (cur) parts.push(cur)
  return parts.filter(Boolean).flatMap(p => expandUse(`${prefix}${p}`))
}
