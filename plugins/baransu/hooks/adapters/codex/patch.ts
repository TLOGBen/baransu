// apply_patch's text → what it does to each file. Codex hands the whole patch to PreToolUse as
// tool_input.command (PoC 0.169.1 Q11): `*** Add File:`, `*** Update File:` (with `*** Move to:`), `*** Delete File:`.

/**
 * One thing the patch does to a file:
 * - write: the file (a move's destination) and the text it writes — the added lines, as Claude Code's Edit hands
 *   its new strings.
 * - delete: a deleted file. Claude Code deletes only through a shell command, so the adapter hands it to the
 *   engine the same way (pre:bash reads its deletes and the delete preview).
 * - move: a moved file's source and destination; the source goes away as a shell `mv` would take it.
 */
export type PatchOp =
  | { readonly kind: 'write'; readonly file: string; readonly text: string }
  | { readonly kind: 'delete'; readonly file: string }
  | { readonly kind: 'move'; readonly from: string; readonly to: string }

export function patchOps(patch: string): PatchOp[] {
  const out: PatchOp[] = []
  let cur: { file: string; lines: string[]; deleted: boolean; from?: string } | null = null
  const flush = () => {
    if (!cur) return
    if (cur.deleted) out.push({ kind: 'delete', file: cur.file })
    else {
      if (cur.from) out.push({ kind: 'move', from: cur.from, to: cur.file })
      out.push({ kind: 'write', file: cur.file, text: cur.lines.join('\n') })
    }
    cur = null
  }
  for (const raw of patch.split(/\r?\n/)) {
    const m = /^\*\*\* (Add|Update|Delete) File: (.+)$/.exec(raw)
    if (m) {
      flush()
      cur = { file: m[2].trim(), lines: [], deleted: m[1] === 'Delete' }
      continue
    }
    const mv = /^\*\*\* Move to: (.+)$/.exec(raw)
    if (mv && cur) {
      cur.from = cur.file
      cur.file = mv[1].trim()
      continue
    }
    if (raw.startsWith('*** ')) continue
    if (cur && raw.startsWith('+')) cur.lines.push(raw.slice(1))
  }
  flush()
  return out
}
