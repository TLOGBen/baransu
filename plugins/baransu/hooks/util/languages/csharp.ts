import type { Language, SourceFact, TreeView } from '../../engine/ports'
import { escapeRe, stemOf } from './paths'

const USING = /^\s*(?:global\s+)?using\s+(?:static\s+)?(?:\w+\s*=\s*)?([\w.]+)\s*;/
const NAMESPACE = /^\s*namespace\s+([\w.]+)/
const TYPE = /^\s*(?:public|internal)\s+(?:(?:sealed|static|abstract|partial)\s+)*(?:class|record|interface|enum|struct)\s+(\w+)/

export const csharp: Language = {
  id: 'csharp',
  exts: ['cs'],
  // using X.Y; · using static X.Y; · global using X; · namespace X.Y · public class|record|interface|enum|struct N
  lines: String.raw`^\s*((global\s+)?using\s+(static\s+)?[\w.=\s]+;|namespace\s+[\w.]+|(public|internal)\s+(sealed\s+|static\s+|abstract\s+|partial\s+)*(class|record|interface|enum|struct)\s+\w)`,
  /** using → import; namespace → declare; public type → export. `using A = B.C;` → import B.C. */
  read(_path: string, line: string): readonly SourceFact[] {
    const u = USING.exec(line)
    if (u) return [{ kind: 'import', spec: u[1] }]
    const n = NAMESPACE.exec(line)
    if (n) return [{ kind: 'declare', name: n[1] }]
    const t = TYPE.exec(line)
    return t ? [{ kind: 'export', name: t[1] }] : []
  },
  /**
   * C# imports a namespace, not a file: `using N;` → every file declaring N (tree.declared). Coarse by
   * nature — one using of a big namespace relates many files; the cap in targets() and hop ordering keep it
   * bounded. A file also implicitly depends on files of its own namespace: not an edge (it would relate the
   * whole namespace to every change; design: traps). `using static N.T` / `using A = N.T` name a type:
   * the files of N whose name is T.
   */
  resolve(spec: string, from: string, tree: TreeView): readonly string[] {
    const files = tree.declared.get(spec)
    if (files) return files.filter(f => f !== from)
    const dot = spec.lastIndexOf('.')
    if (dot < 0) return []
    const type = spec.slice(dot + 1)
    return (tree.declared.get(spec.slice(0, dot)) ?? []).filter(f => f !== from && stemOf(f) === type)
  },
  /** `using <its namespace>;` from ownFacts' declare; no namespace → null. */
  importerPattern(_path: string, ownFacts: readonly SourceFact[]): string | null {
    const ns = ownFacts.find(f => f.kind === 'declare')
    if (!ns || ns.kind !== 'declare') return null
    return String.raw`^\s*(global\s+)?using\s+(static\s+)?(\w+\s*=\s*)?` + escapeRe(ns.name) + String.raw`(\.\w+)?\s*;`
  },
}
