// TypeScript and JavaScript: one syntax for imports, so one adapter.

import type { Language, SourceFact, TreeView } from '../../engine/ports'
import { escapeRe, joinPath, stemOf } from './paths'

const EXTS = ['ts', 'tsx', 'mts', 'cts', 'js', 'jsx', 'mjs', 'cjs']
const SPEC = /(?:\bfrom\s*|^\s*import\s*|\brequire\(\s*|\bimport\(\s*)['"]([^'"]+)['"]/g
const EXPORT = /^\s*export\s+(?:default\s+)?(?:async\s+)?(?:function\*?|class|const|let|interface|type|enum)\s+([A-Za-z_$][\w$]*)/

export const typescript: Language = {
  id: 'typescript',
  exts: EXTS,
  // import … from '…' · import '…' · export … from '…' · require('…') · import('…') · export function|class|const X
  lines: String.raw`(\bfrom\s*['"]|^\s*import\s*['"]|\brequire\(\s*['"]|\bimport\(\s*['"]|^\s*export\s+(default\s+)?(async\s+)?(function|class|const|let|interface|type|enum)\s)`,
  /** import/require specifiers; `export <kind> X` → export X. */
  read(_path: string, line: string): readonly SourceFact[] {
    const out: SourceFact[] = []
    for (const m of line.matchAll(SPEC)) out.push({ kind: 'import', spec: m[1] })
    const e = EXPORT.exec(line)
    if (e) out.push({ kind: 'export', name: e[1] })
    return out
  },
  /**
   * Relative only ('./x', '../x'): try as written, then with each ext, then <spec>/index.<ext>; a '.js'
   * specifier also tries '.ts'/'.tsx' (TS ESM writes .js for a .ts file). Bare specifiers ('react',
   * '@scope/x') → []: a package is not the project. tsconfig `paths` aliases ('@/x') → [] (design: traps).
   */
  resolve(spec: string, from: string, tree: TreeView): readonly string[] {
    if (!spec.startsWith('.')) return []
    const base = joinPath(from, spec)
    const tries = [base, ...EXTS.map(e => `${base}.${e}`), ...EXTS.map(e => `${base}/index.${e}`)]
    const js = /\.(m|c)?jsx?$/.exec(base)
    if (js) {
      const bare = base.slice(0, -js[0].length)
      tries.push(...['ts', 'tsx', 'mts', 'cts'].map(e => `${bare}.${e}`))
    }
    const hit = tries.find(t => tree.files.has(t))
    return hit ? [hit] : []
  },
  /** from|require|import( with a quoted specifier ending in the file's stem (or `<dir>` for an index file). */
  importerPattern(path: string): string | null {
    const stem = stemOf(path)
    const name = stem === 'index' ? (path.split('/').slice(-2, -1)[0] ?? '') : stem
    if (!name) return null
    return String.raw`(\bfrom\s*|^\s*import\s*|\brequire\(\s*|\bimport\(\s*)['"][^'"]*\b` + escapeRe(name) + String.raw`(\.[a-z]+)?(/index(\.[a-z]+)?)?['"]`
  },
}
