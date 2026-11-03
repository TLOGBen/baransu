// Reading a shell command line: its segments, whether it writes files, what a delete would touch.
// Pure except destructivePreview, which looks through the Runner port. Bodies came from 8.39's lint.ts (git show 58de798a:plugins/baransu/hooks/lint.ts).

import { relTo } from './check'
import type { Runner } from './ports'

const GIT_WRITE = /\bgit\b[^|;&\n]*\b(commit|push)\b/

/** Split on && || ; | and newlines outside quotes, so `node -e "…"` stays one command. Pure. */
export function segments(command: string): string[] {
  const out: string[] = []
  let cur = ''
  let quote = ''
  for (let i = 0; i < command.length; i++) {
    const ch = command[i]
    if (quote) {
      if (ch === quote) quote = ''
      cur += ch
    } else if (ch === '"' || ch === "'") {
      quote = ch
      cur += ch
    } else if (ch === ';' || ch === '\n' || ch === '|' || (ch === '&' && command[i + 1] === '&')) {
      if (ch === '&' || (ch === '|' && command[i + 1] === '|')) i++
      out.push(cur)
      cur = ''
    } else cur += ch
  }
  out.push(cur)
  return out
}

/** A shell command that writes files counts as an edit: sed -i, tee, a redirect, Set-Content, git apply, patch. Pure. */
export function writesFiles(command: string): boolean {
  const unquoted = command.replace(/"[^"]*"|'[^']*'/g, '""')
  return /\bsed\s+(-[a-zA-Z]*i|--in-place)|\btee\b|\b(Set-Content|Add-Content|Out-File)\b|\bgit\s+apply\b|\bpatch\s/i.test(unquoted) ||
    /(^|[^0-9&>])>>?\s*(?!&|\/dev\/null|\$null\b|nul\b)[^\s|;&]/i.test(unquoted)
}

/**
 * True when a segment of the command runs `git [-C dir] [-c k=v] commit|push` (through sudo/env wrappers, a
 * shell keyword, `bash -c` / `pwsh -c`). Words that only mention git — a heredoc's text, a quoted argument
 * (`rg "git push"`), a comment — are not one (found 2026-11-03: a script's prose held both words). Pure.
 */
export function isGitWrite(command: string): boolean {
  return gitWrites(command).length > 0
}

/** Which git writes a command runs — `commit`, `push`, or both — read the same way as isGitWrite: a word in
 *  a message (`git commit -m "push later"`) or a branch name (`git push origin commit-fix`) is neither. Pure. */
export function gitWrites(command: string): ('commit' | 'push')[] {
  if (!GIT_WRITE.test(command)) return []
  const out = new Set<'commit' | 'push'>()
  for (const seg of segments(command)) {
    let w = bare(words(seg.trim()))
    while (w.length && /^(do|then|else|elif|\{|!|\(+)$/.test(w[0])) w = bare(w.slice(1))
    if (!w.length) continue
    const cmd = w[0].replace(/^\(+/, '').toLowerCase()
    const flag = w.findIndex(x => /^(-c|-command|\/c)$/i.test(x))
    if (['bash', 'sh', 'zsh', 'pwsh', 'powershell', 'cmd'].includes(cmd) && flag > 0 && w[flag + 1]) {
      for (const x of gitWrites(w[flag + 1])) out.add(x)
      continue
    }
    if (cmd !== 'git') continue
    let i = 1
    while (i < w.length && (w[i] === '-C' || w[i] === '-c' || w[i] === '--git-dir' || w[i] === '--work-tree')) i += 2
    while (i < w.length && w[i].startsWith('-')) i++
    if (w[i] === 'commit' || w[i] === 'push') out.add(w[i] as 'commit' | 'push')
  }
  return (['commit', 'push'] as const).filter(x => out.has(x))
}

/**
 * Where a `git push` sends what, read from its refspecs: `git push origin tmp:dev` sends tmp to dev, `git push
 * origin feature` sends feature to feature, `+HEAD:refs/heads/main` sends HEAD to main; a delete (`:old`) sends
 * nothing. null when the command names no refspec (`git push`, `git push origin`): the branch's upstream decides,
 * as git does. Flags are skipped. Pure.
 */
export function pushRefs(command: string): { remote: string; src: string; dst: string }[] | null {
  const m = /\bgit(?:\s+-C\s+\S+)?\s+push\b([^\n|;&]*)/.exec(command)
  if (!m) return null
  const args = m[1].trim().split(/\s+/).filter(t => t && !t.startsWith('-')).map(t => t.replace(/^["']|["']$/g, ''))
  if (args.length < 2) return null
  const [remote, ...specs] = args
  const out: { remote: string; src: string; dst: string }[] = []
  for (const spec of specs) {
    const s = spec.replace(/^\+/, '')
    const [src, dst = src] = s.includes(':') ? s.split(':', 2) : [s, s]
    if (!src) continue
    out.push({ remote, src, dst: dst.replace(/^refs\/heads\//, '') })
  }
  return out
}

/**
 * The directory each `git commit` / `git push` in this command runs in, one entry per git write, in order:
 * `cwd`, moved by each `cd` / `pushd` / `Set-Location` / `Push-Location [-Path|-LiteralPath]` before it (a
 * `cd` inside `( … )` stays inside), then by that segment's `git -C <dir>`. Relative paths resolve against the
 * directory so far; Git Bash's `/c/…` reads as `C:/…`. An entry is null when the directory cannot be read
 * from the text (`~`, a variable, `cd -`, a bare `cd`, after `popd` / `Pop-Location`), or when the write runs
 * inside another shell (`bash -c "… git commit"`, `pwsh -c`, `cmd /c`): the caller says so instead of guessing.
 * This is the one judge of "does this command write with git" in a plain-folder workspace: a segment led by
 * `git` / `git.exe` (after shell keywords `do`, `then`, `else`, `{`, `!` and env assignments) is a write; a
 * mention inside another command's quotes (`rg "git push"`, `echo "… git commit"`) is not, and yields nothing.
 * Forward slashes, no trailing slash. Pure. A workspace's commit happens in one of its repos (`cd src/app &&
 * git commit`); its checks run in that repo.
 */
export function commitDirs(command: string, cwd: string): (string | null)[] {
  let dir: string | null = cwd.replace(/\\/g, '/').replace(/\/+$/, '')
  const resolve = (from: string | null, to: string): string | null => {
    let t = to.replace(/\\/g, '/')
    if (from === null || t === '-' || /[~$%]/.test(t)) return null
    t = t.replace(/^\/([A-Za-z])(\/|$)/, (_, d, s) => `${d.toUpperCase()}:${s || '/'}`)
    const out: string[] = []
    for (const p of (/^([A-Za-z]:)?\//.test(t) ? t : `${from}/${t}`).split('/')) {
      if (p === '..') { if (out.length > 1) out.pop() } else if (p !== '.' && (p !== '' || out.length === 0)) out.push(p)
    }
    return out.join('/').replace(/\/+$/, '') || '/'
  }
  const target = (w: string[]): string | undefined => {
    for (let i = 1; i < w.length; i++) {
      if (/^-(Path|LiteralPath)$/i.test(w[i])) return w[i + 1]
      if (!w[i].startsWith('-') || w[i] === '-') return w[i]
    }
    return undefined
  }
  const dirs: (string | null)[] = []
  let outside: string | null = dir
  let depth = 0
  for (const seg of segments(command)) {
    const opens = (seg.match(/^\s*\(+/)?.[0].match(/\(/g) ?? []).length
    const closes = (seg.match(/\)+\s*$/)?.[0].match(/\)/g) ?? []).length
    if (opens && depth === 0) outside = dir
    depth += opens
    // Shell keywords before the command itself (`for …; do cd x`, `if …; then git commit`, `{ git push; }`).
    let w = bare(words(seg))
    while (w.length && /^(do|then|else|elif|\{|!)$/.test(w[0])) w = bare(w.slice(1))
    if (/^(cd|pushd|Set-Location|Push-Location|sl|chdir)$/i.test(w[0] ?? '')) {
      // A bare `cd` goes home, which the text does not show: unknown, like ~.
      const to = target(w)
      dir = to === undefined ? null : resolve(dir, to)
    } else if (/^(popd|Pop-Location)$/i.test(w[0] ?? '')) dir = null
    if (/^git(\.exe)?$/i.test(w[0] ?? '')) {
      // The subcommand is the first word after git's own options (-C <dir>, -c <k=v>, --flags):
      // `git log --grep commit` is not a write.
      let here: string | null = dir
      let i = 1
      for (; i < w.length && w[i].startsWith('-'); i++) {
        if (w[i] === '-C') here = resolve(here, w[++i] ?? '')
        else if (w[i] === '-c') i++
      }
      if (w[i] === 'commit' || w[i] === 'push') dirs.push(here)
    } else if (/^(bash|sh|zsh|pwsh|powershell|cmd)(\.exe)?$/i.test(w[0] ?? '') && /^(-c|-Command|\/c)$/i.test(w[1] ?? '') && GIT_WRITE.test(w.slice(2).join(' '))) {
      // A git write inside another shell: its directory is that shell's business; say so.
      dirs.push(null)
    }
    depth = Math.max(0, depth - closes)
    if (closes && depth === 0) dir = outside
  }
  return dirs
}

// Words of one shell segment, quotes removed.
function words(segment: string): string[] {
  // A subshell's parentheses, `(cd x && rm y)`, are not part of the words.
  const plain = segment.replace(/^\s*\(+/, '').replace(/\)+\s*$/, '')
  return (plain.match(/"[^"]*"|'[^']*'|\S+/g) ?? []).map(w => w.replace(/^["']|["']$/g, ''))
}

// The words of a segment without a leading wrapper (sudo, env VAR=x, command, nohup, time, doas).
function bare(w: string[]): string[] {
  let i = 0
  while (i < w.length && (/^(sudo|doas|command|nohup|time|env|npx|bunx|pnpx)$/i.test(w[i]) || /^[A-Za-z_][A-Za-z0-9_]*=/.test(w[i]))) i++
  return w.slice(i)
}

async function describePath<H>(runner: Runner<H>, h: H, root: string, p: string): Promise<string> {
  const shown = relTo(root, p)
  if (/[~$%]/.test(p)) return `${shown}（含 ~ 或變數，mod 無法展開：改寫成實際路徑再刪）`
  if (/[*?[]/.test(p)) return `${shown}（萬用字元：先 ls 看實際範圍）`
  const at = await runner.probe(h, p)
  if (at.kind === 'missing') return `${shown}（不存在）`
  if (at.kind === 'dir') return `${shown}/（資料夾，第一層 ${at.entries} 項）`
  if (at.kind === 'file') return `${shown}（檔案）`
  return `${shown}（讀不到）`
}

/**
 * lint-scope sketch: the root-relative paths a command deletes or moves away, for `actions = ["delete"]`
 * (Occurrence bash.deletes). Pure: the same reading as destructivePreview — cd inside the command, wrappers,
 * `( … )`, `bash -c` — for rm / rmdir / rd / del / Remove-Item / rimraf / mv's sources / git rm (not --cached).
 * What only a run can tell (find -delete, git clean, reset --hard, xargs rm) is not listed (format.md says so).
 * A path with ~ or a variable is kept as written. Paths outside the root are dropped. null: nothing destructive.
 */
export function deletedPaths(command: string, cwd: string, root: string): string[] | null {
  const found = deletedAbsolute(command, cwd.replace(/\\/g, '/').replace(/\/$/, ''))
  if (!found.length) return null
  const r = root.replace(/\\/g, '/').replace(/\/$/, '')
  const out: string[] = []
  for (const p of found) {
    const f = p.replace(/\\/g, '/').replace(/\/+$/, '')
    if (/[~$%]/.test(f)) out.push(f)
    else if (f.toLowerCase() === r.toLowerCase()) out.push('')
    else {
      const rel = relTo(r, f)
      if (rel !== f) out.push(rel)
    }
  }
  return out.length ? out : null
}

/** The worktrees a command removes (`git worktree remove <path>`), as written, for `actions =
 *  ["worktree-remove"]`. Pure; sees through `bash -c` like deletedPaths. null: none. */
export function removedWorktrees(command: string): string[] | null {
  const out: string[] = []
  for (const seg of segments(command)) {
    const w = bare(words(seg.trim()))
    if (!w.length) continue
    const cmd = w[0].toLowerCase()
    const flag = w.findIndex(x => /^(-c|-command|\/c)$/i.test(x))
    if (['bash', 'sh', 'zsh', 'pwsh', 'powershell', 'cmd'].includes(cmd) && flag > 0 && w[flag + 1]) out.push(...(removedWorktrees(w[flag + 1]) ?? []))
    else if (cmd === 'git' && w[1] === 'worktree' && w[2] === 'remove') out.push(...w.slice(3).filter(a => !a.startsWith('-')))
  }
  return out.length ? out : null
}

function deletedAbsolute(command: string, cwd: string): string[] {
  const out: string[] = []
  let base = cwd
  const at = (p: string) => (/^([A-Za-z]:)?[\\/]/.test(p) || /^[~$%]/.test(p) || !base ? p : `${base}/${p}`.replace(/\/\.\//g, '/').replace(/\/\.$/, ''))
  for (const seg of segments(command)) {
    const w = bare(words(seg.trim()))
    if (!w.length) continue
    const cmd = w[0].toLowerCase()
    const args = w.slice(1).filter(a => !a.startsWith('-'))
    const flag = w.findIndex(x => /^(-c|-command|\/c)$/i.test(x))
    if (['bash', 'sh', 'zsh', 'pwsh', 'powershell', 'cmd'].includes(cmd) && flag > 0 && w[flag + 1]) out.push(...deletedAbsolute(w[flag + 1], base))
    else if ((cmd === 'cd' || cmd === 'set-location') && args[0]) base = at(args[0]).replace(/\\/g, '/').replace(/\/$/, '')
    else if (['rm', 'rmdir', 'rd', 'del', 'remove-item', 'ri', 'erase', 'rimraf'].includes(cmd)) out.push(...args.filter(x => !/^\/[a-z]$/i.test(x)).map(at))
    else if (['mv', 'move-item', 'move'].includes(cmd) && args.length >= 2) out.push(...args.slice(0, -1).map(at))
    else if (cmd === 'git' && w[1] === 'rm' && !w.includes('--cached')) out.push(...w.slice(2).filter(x => !x.startsWith('-')).map(at))
  }
  return out
}

/**
 * The lines 「刪除 …」「搬移 … → …」「git clean 會刪：…」… a command would touch, read from `cwd` (the actor's
 * real directory), following a `cd` inside the same command, seeing through sudo/env/npx, `( … )` and
 * `bash -c` / `pwsh -c` / `cmd /c` (recursively). Empty: nothing destructive.
 * Paths are probed with runner.probe; `find`, `git clean -n`, `git status` … run with runner.run.
 * Runs twice: same answer for the same tree. Stops halfway: no effect, it only reads.
 */
export async function destructivePreview<H>(runner: Runner<H>, h: H, root: string, command: string, cwd: string): Promise<string[]> {
  const out: string[] = []
  const lines = async (argv: string[], max = 15) =>
    String((await runner.run(h, argv, { cwd, timeoutMs: 30000 })).stdout).trim().split(/\r?\n/).filter(Boolean).slice(0, max)
  // Relative paths start from where the shell is; a `cd` earlier in the same command moves it.
  let base = cwd.replace(/\\/g, '/').replace(/\/$/, '')
  const at = (p: string) => (/^([A-Za-z]:)?[\\/]/.test(p) || !base ? p : `${base}/${p}`)
  const describe = (p: string) => describePath(runner, h, root, p)
  for (const seg of segments(command)) {
    const w = bare(words(seg.trim()))
    if (!w.length) continue
    const cmd = w[0].toLowerCase()
    const args = w.slice(1).filter(a => !a.startsWith('-'))
    const script = ['bash', 'sh', 'zsh', 'pwsh', 'powershell'].includes(cmd) ? w[w.findIndex(x => /^-(c|command)$/i.test(x)) + 1] : cmd === 'cmd' ? w[w.findIndex(x => /^\/c$/i.test(x)) + 1] : undefined
    if (script && w.some(x => /^(-c|-command|\/c)$/i.test(x))) {
      // A script handed to another shell: preview what it would run.
      out.push(...(await destructivePreview(runner, h, root, script, base)))
    } else if (cmd === 'find' && (w.includes('-delete') || w.some((x, i) => /^-(exec|execdir|ok)$/.test(x) && /^(rm|rmdir|del|remove-item|unlink|shred)$/i.test(w[i + 1] ?? '')))) {
      // List what it would delete: the same search with its action replaced by -print.
      const action = w.findIndex(x => /^-(delete|exec|execdir|ok)$/.test(x))
      const r = await runner.run(h, ['find', ...w.slice(1, action), '-print'], { cwd: base, timeoutMs: 30000 })
      const hit = r.exitCode === 0 ? String(r.stdout).trim().split(/\r?\n/).filter(Boolean) : []
      out.push(...(hit.length ? [`find 會刪 ${hit.length} 項：`, ...hit.slice(0, 15).map(x => `  ${relTo(root, at(x).replace(/\/\.\//g, '/'))}`)] : ['find 會刪除符合條件的檔案，但列不出清單：先把刪除動作換成 -print 跑一次']))
    } else if (cmd === 'xargs' && /^(rm|rmdir|del|remove-item)$/i.test(w.find((x, i) => i > 0 && !x.startsWith('-')) ?? '')) {
      out.push(`xargs ${w.slice(1).join(' ')}：要刪什麼由前一個指令的輸出決定，無法事先列出；先單獨跑前一段看清單`)
    } else if ((cmd === 'cd' || cmd === 'set-location') && args[0]) {
      base = at(args[0]).replace(/\\/g, '/').replace(/\/$/, '')
    } else if (['rm', 'rmdir', 'rd', 'del', 'remove-item', 'ri', 'erase', 'rimraf'].includes(cmd)) {
      for (const a of args.filter(x => !/^\/[a-z]$/i.test(x))) out.push(`刪除 ${await describe(at(a))}`)
    } else if (['mv', 'move-item', 'move'].includes(cmd) && args.length >= 2) {
      const dest = args[args.length - 1]
      for (const a of args.slice(0, -1)) out.push(`搬移 ${await describe(at(a))} → ${await describe(at(dest))}`)
    } else if (cmd === 'git') {
      const sub = w[1]
      const rest = w.slice(2)
      if (sub === 'rm' && !rest.includes('--cached')) {
        for (const a of rest.filter(x => !x.startsWith('-'))) out.push(`git rm 刪除 ${await describe(at(a))}`)
      } else if (sub === 'clean') {
        const flags = ['-n', ...(rest.some(a => /^-[a-z]*d/.test(a)) ? ['-d'] : []), ...(rest.some(a => /^-[a-z]*x/i.test(a)) ? ['-x'] : [])]
        const hit = await lines(['git', 'clean', ...flags])
        out.push(...(hit.length ? hit.map(x => `git clean 會刪：${x.replace(/^Would remove /, '')}`) : ['git clean：沒有要刪的檔案']))
      } else if (sub === 'reset' && rest.includes('--hard')) {
        const hit = await lines(['git', 'status', '--short'])
        out.push(...(hit.length ? hit.map(x => `reset --hard 會丟掉：${x}`) : ['reset --hard：工作樹沒有未 commit 的改動']))
      } else if ((sub === 'checkout' && rest.includes('--')) || sub === 'restore') {
        const paths = rest.slice(rest.indexOf('--') + 1).filter(a => !a.startsWith('-'))
        const hit = await lines(['git', 'diff', '--stat', '--', ...paths])
        out.push(...(hit.length ? hit.map(x => `會丟掉的改動：${x.trim()}`) : ['這些檔案沒有未 commit 的改動']))
      } else if (sub === 'branch' && (rest.includes('-D') || rest.includes('-d') || rest.includes('--delete'))) {
        const merged = new Set(await lines(['git', 'branch', '--merged', 'HEAD', '--format=%(refname:short)'], 500))
        for (const b of rest.filter(a => !a.startsWith('-'))) {
          const log = await lines(['git', 'log', '--oneline', '-3', b], 3)
          out.push(`刪除分支 ${b}（${merged.has(b) ? '已合併進 HEAD' : '沒有合併進 HEAD'}）：${log.join('；') || '找不到這個分支'}`)
        }
      } else if (sub === 'worktree' && w[2] === 'remove') {
        for (const p of w.slice(3).filter(a => !a.startsWith('-'))) {
          const dirty = await lines(['git', '-C', p, 'status', '--short'])
          const branch = (await lines(['git', '-C', p, 'rev-parse', '--abbrev-ref', 'HEAD'], 1))[0] ?? ''
          const unpushed = branch && branch !== 'HEAD' ? await lines(['git', '-C', p, 'log', '--oneline', `${branch}`, '--not', '--remotes'], 50) : []
          const pushed = !branch || branch === 'HEAD' ? '沒有分支' : unpushed.length ? `分支 ${branch} 有 ${unpushed.length} 個 commit 不在遠端` : `分支 ${branch} 都在遠端`
          out.push(`移除 worktree ${p}：${dirty.length ? `還有 ${dirty.length} 個沒 commit 的改動（${dirty.slice(0, 5).join('、')}）` : '乾淨'}；${pushed}`)
        }
      } else if (sub === 'stash' && (w[2] === 'drop' || w[2] === 'clear')) {
        const list = await lines(['git', 'stash', 'list'])
        out.push(`stash ${w[2]}：${list.length ? list.join('；') : '沒有 stash'}`)
      }
    }
  }
  return out
}
