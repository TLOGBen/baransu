// Globs as the check format writes them: no "/" matches the file name anywhere, with "/" the root-relative path;
// `*` within a segment, `**` across segments, `**/` any number of folders.

export function globRe(g: string): RegExp {
  let r = ''
  for (let i = 0; i < g.length; i++) {
    const c = g[i]
    if (c === '*') {
      if (g[i + 1] === '*') {
        i++
        if (g[i + 1] === '/') {
          i++
          r += '(?:.*/)?'
        } else r += '.*'
      } else r += '[^/]*'
    } else if (c === '?') r += '[^/]'
    else r += c.replace(/[.+^${}()|[\]\\]/g, '\\$&')
  }
  return new RegExp('^' + r + '$')
}
