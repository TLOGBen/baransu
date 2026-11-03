import type { Language, SourceFact, TreeView } from '../../engine/ports'
import { dirOf, escapeRe, stemOf } from './paths'

const IMPORT = /^\s*import\s+(.+)$/
const FROM = /^\s*from\s+([\w.]+)\s+import\s+\(?([^)#]*)\)?/
const DEF = /^(?:async\s+)?(?:def|class)\s+(\w+)/

export const python: Language = {
  id: 'python',
  exts: ['py', 'pyi'],
  // import a.b · from a.b import c · from . import c · def/class at column 0 (exports)
  lines: String.raw`^(\s*(from\s+[\w.]+\s+import\b|import\s+[\w.])|(async\s+)?(def|class)\s+\w)`,
  /** `from x import (` with no `)` on the line continues until `)`. */
  continues(line: string): string | null {
    return /^\s*from\s+[\w.]+\s+import\s*\(/.test(line) && !line.includes(')') ? ')' : null
  },
  /** `import a.b, c` → a.b, c; `from .x import y` → .x and .x.y (y may be a submodule), also when the names are
   *  joined from a parenthesised list over several lines; top-level def/class → export. */
  read(_path: string, line: string): readonly SourceFact[] {
    const flat = line.replace(/\s*\n\s*/g, ' ')
    const f = FROM.exec(flat)
    if (f) {
      const mod = f[1]
      const names = f[2].split(',').map(s => s.trim().split(/\s+as\s+/)[0].trim()).filter(n => n && n !== '*')
      const sub = (n: string) => (mod.endsWith('.') ? `${mod}${n}` : `${mod}.${n}`)
      return [{ kind: 'import', spec: mod }, ...names.map(n => ({ kind: 'import' as const, spec: sub(n) }))]
    }
    const i = IMPORT.exec(flat)
    if (i) return i[1].split(',').map(s => s.trim().split(/\s+as\s+/)[0].trim()).filter(Boolean).map(spec => ({ kind: 'import' as const, spec }))
    const d = DEF.exec(line)
    return d ? [{ kind: 'export', name: d[1] }] : []
  },
  /**
   * Dotted → path: a/b.py or a/b/__init__.py, looked up from each source root — the repo root and every
   * folder holding a top-level package that some file's absolute import names (covers `src/` layouts).
   * Leading dots: relative to the importing file's package. Not found → [] (std lib, site-packages).
   */
  resolve(spec: string, from: string, tree: TreeView): readonly string[] {
    const dots = /^\.*/.exec(spec)![0].length
    const parts = spec.slice(dots).split('.').filter(Boolean)
    const at = (base: string) => {
      const p = [base, ...parts].filter(Boolean).join('/')
      const tries = parts.length ? [`${p}.py`, `${p}.pyi`, `${p}/__init__.py`] : [`${p}/__init__.py`]
      return tries.find(t => tree.files.has(t))
    }
    if (dots) {
      let base = dirOf(from)
      for (let k = 1; k < dots; k++) base = dirOf(base)
      const hit = at(base)
      return hit ? [hit] : []
    }
    if (!parts.length) return []
    for (const root of sourceRoots(parts[0], tree)) {
      const hit = at(root)
      if (hit) return [hit]
    }
    return []
  },
  /** `import … <module>` / `from … <module> import` / `from <pkg> import <stem>`, the module from the path. */
  importerPattern(path: string): string | null {
    const stem = stemOf(path)
    const name = stem === '__init__' ? (path.split('/').slice(-2, -1)[0] ?? '') : stem
    if (!name) return null
    const n = escapeRe(name)
    return String.raw`^\s*(from\s+[\w.]*\b` + n + String.raw`\b[\w.]*\s+import\b|import\s+[\w., ]*\b` + n + String.raw`\b|from\s+[\w.]+\s+import\s+.*\b` + n + String.raw`\b)`
  },
}

/** The folders a top-level package or module named `first` sits in: '' first, then each other folder. */
function sourceRoots(first: string, tree: TreeView): string[] {
  const roots = new Set<string>([''])
  for (const f of tree.files) {
    const i = f.indexOf(`/${first}/`)
    if (i >= 0) roots.add(f.slice(0, i))
    else if (f.endsWith(`/${first}.py`)) roots.add(f.slice(0, -(first.length + 4)))
  }
  return [...roots]
}
