import type { Language, SourceFact, TreeView } from '../../engine/ports'
import { escapeRe, stemOf } from './paths'

const IMPORT = /^\s*import\s+(static\s+)?([\w.]+?)(\.\*)?\s*;/
const PACKAGE = /^\s*package\s+([\w.]+)\s*;/
const TYPE = /^\s*public\s+(?:(?:final|abstract|sealed)\s+)*(?:class|interface|enum|record)\s+(\w+)/

export const java: Language = {
  id: 'java',
  exts: ['java'],
  // import a.b.C; · import static a.b.C.m; · import a.b.*; · package a.b; · public class|interface|enum|record N
  lines: String.raw`^\s*(import\s+(static\s+)?[\w.]+(\.\*)?\s*;|package\s+[\w.]+\s*;|public\s+(final\s+|abstract\s+|sealed\s+)*(class|interface|enum|record)\s+\w)`,
  /** `import a.b.C;` → a.b.C; `import a.b.*;` → a.b.*; `import static a.b.C.m;` → a.b.C; package → declare. */
  read(_path: string, line: string): readonly SourceFact[] {
    const i = IMPORT.exec(line)
    if (i) {
      if (i[3]) return [{ kind: 'import', spec: `${i[2]}.*` }]
      const spec = i[1] ? i[2].slice(0, Math.max(0, i[2].lastIndexOf('.'))) : i[2]
      return spec ? [{ kind: 'import', spec }] : []
    }
    const p = PACKAGE.exec(line)
    if (p) return [{ kind: 'declare', name: p[1] }]
    const t = TYPE.exec(line)
    return t ? [{ kind: 'export', name: t[1] }] : []
  },
  /**
   * `a.b.C` → the file declaring package a.b named C.java; `a.b.*` → every file declaring a.b; a nested
   * `a.b.C.D` walks up to a.b.C. Same-package references need no import and are not edges (design: traps).
   */
  resolve(spec: string, from: string, tree: TreeView): readonly string[] {
    if (spec.endsWith('.*')) return (tree.declared.get(spec.slice(0, -2)) ?? []).filter(f => f !== from)
    const segs = spec.split('.')
    for (let k = segs.length - 1; k >= 1; k--) {
      const pkg = segs.slice(0, k).join('.')
      const hit = (tree.declared.get(pkg) ?? []).filter(f => f !== from && stemOf(f) === segs[k])
      if (hit.length) return hit
    }
    return []
  },
  /** `import <package>.<Class>;` or `import <package>.*;`, from ownFacts' package and the file's stem. */
  importerPattern(path: string, ownFacts: readonly SourceFact[]): string | null {
    const pkg = ownFacts.find(f => f.kind === 'declare')
    if (!pkg || pkg.kind !== 'declare') return null
    return String.raw`^\s*import\s+(static\s+)?` + escapeRe(pkg.name) + String.raw`\.(` + escapeRe(stemOf(path)) + String.raw`\b|\*)`
  },
}
