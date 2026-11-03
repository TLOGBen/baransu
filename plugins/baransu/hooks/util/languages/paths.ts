// Path helpers the language adapters share. Root-relative, forward-slash paths only; pure.

/** The folder of a path ('' at the root). */
export const dirOf = (p: string): string => (p.includes('/') ? p.slice(0, p.lastIndexOf('/')) : '')

/** The file name without its last extension. */
export const stemOf = (p: string): string => {
  const base = p.slice(p.lastIndexOf('/') + 1)
  return base.includes('.') ? base.slice(0, base.lastIndexOf('.')) : base
}

/** `rel` (with ./ and ../) read from the folder of `from`, normalised. Leaving the root keeps '..' segments,
 *  which no tree entry matches. */
export function joinPath(from: string, rel: string): string {
  return normalise(`${dirOf(from)}/${rel}`)
}

/** Collapse '.', '..' and doubled slashes. */
export function normalise(p: string): string {
  const out: string[] = []
  for (const seg of p.split('/')) {
    if (seg === '' || seg === '.') continue
    if (seg === '..' && out.length && out[out.length - 1] !== '..') out.pop()
    else out.push(seg)
  }
  return out.join('/')
}

/** A literal for a PCRE / JS regex. */
export const escapeRe = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
