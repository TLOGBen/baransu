import type { Register } from 'claude-code'

// baransu lint mod: reads the project's .claude/lint/ and runs each check at its
// moment — after an edit, before a git commit or push, before /ship or /review,
// at session start. Findings go to the person as a notice row and to the model
// with the tool result or the skill's text. No .claude/lint/, no effect.

type Severity = 'error' | 'warn' | 'off'
type Check = {
  id: string
  on: string[]
  severity: Severity
  files: string[]
  ignores: string[]
  forbid?: string
  run?: string[]
  builtin?: string
  message: string
  changed?: string
  language?: string
}
type Finding = { id: string; severity: 'error' | 'warn' | 'note'; text: string }

const LINT = '.claude/lint'
const EDIT_TOOLS = new Set(['Edit', 'Write', 'MultiEdit', 'NotebookEdit'])
const SHELL_TOOLS = new Set(['Bash', 'PowerShell'])
const GIT_WRITE = /\bgit\b[^|;&\n]*\b(commit|push)\b/
const DONE_SKILLS = new Set(['ship', 'review', 'baransu:ship', 'baransu:review'])

// ---- session memory (module scope: a reload starts it over) ----
let editSeq = 0
let reviewedAt = -1
const commands: { cmd: string; ok: boolean; seq: number }[] = []
let spokeThisTurn = true
let userLanguage: string | undefined
let gitFactsText: string | undefined
const previewed = new Set<string>()

// ---- small TOML subset: key = "s" | 's' | ["a", 'b'], # comments ----
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

// ---- globs: no "/" matches the file name anywhere; with "/" the repo path ----
function globRe(g: string): RegExp {
  let r = ''
  for (let i = 0; i < g.length; i++) {
    const c = g[i]
    if (c === '*') {
      if (g[i + 1] === '*') {
        i++
        if (g[i + 1] === '/') { i++; r += '(?:.*/)?' } else r += '.*'
      } else r += '[^/]*'
    } else if (c === '?') r += '[^/]'
    else r += c.replace(/[.+^${}()|[\]\\]/g, '\\$&')
  }
  return new RegExp('^' + r + '$')
}
function matches(rel: string, globs: string[]): boolean {
  const base = rel.slice(rel.lastIndexOf('/') + 1)
  return globs.some(g => globRe(g).test(g.includes('/') ? rel : base))
}
function inScope(rel: string, c: Check): boolean {
  return (c.files.length === 0 || matches(rel, c.files)) && !matches(rel, c.ignores)
}
function pathspecs(c: Check): string[] {
  const glob = (g: string) => (g.includes('/') ? g : `**/${g}`)
  const inc = c.files.length ? c.files.map(g => `:(glob)${glob(g)}`) : ['.']
  return [...inc, ...c.ignores.map(g => `:(exclude,glob)${glob(g)}`)]
}

// ---- project ----
async function projectRoot($: any): Promise<string | undefined> {
  try {
    const r = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
    if (r.exitCode === 0) return r.stdout.trim().replace(/\\/g, '/')
  } catch {}
  return undefined
}
function relTo(root: string, file: string): string {
  const f = file.replace(/\\/g, '/')
  return f.toLowerCase().startsWith(root.toLowerCase() + '/') ? f.slice(root.length + 1) : f
}
async function loadChecks($: any, root: string): Promise<{ checks: Check[]; problems: Finding[] }> {
  const checks: Check[] = []
  const problems: Finding[] = []
  const dir = `${root}/${LINT}/checks`
  if (!(await $.fs.exists(dir))) return { checks, problems }
  for (const entry of await $.fs.list(dir)) {
    if (entry.kind !== 'file' || !entry.name.endsWith('.toml')) continue
    const id = entry.name.slice(0, -5)
    try {
      const t = parseToml(await $.fs.read(`${dir}/${entry.name}`))
      const list = (v: unknown) => (Array.isArray(v) ? v : typeof v === 'string' ? [v] : [])
      const sev = t.severity === 'error' || t.severity === 'off' ? t.severity : 'warn'
      checks.push({
        id,
        on: list(t.on),
        severity: sev,
        files: list(t.files),
        ignores: list(t.ignores),
        forbid: typeof t.forbid === 'string' ? t.forbid : undefined,
        run: Array.isArray(t.run) ? t.run : undefined,
        builtin: typeof t.builtin === 'string' ? t.builtin : undefined,
        message: typeof t.message === 'string' ? t.message : '',
        changed: typeof t.changed === 'string' ? t.changed : undefined,
        language: typeof t.language === 'string' ? t.language : undefined,
      })
    } catch (err) {
      problems.push({ id, severity: 'warn', text: `設定讀不懂：checks/${entry.name}：${(err as Error).message}` })
    }
  }
  return { checks: checks.filter(c => c.severity !== 'off'), problems }
}
async function hasLint($: any, root: string | undefined): Promise<boolean> {
  return !!root && (await $.fs.exists(`${root}/${LINT}`))
}

// ---- running checks ----
async function run($: any, argv: string[], cwd: string, timeoutMs = 120000) {
  try {
    return await $.process.run(argv, { cwd, timeoutMs })
  } catch (err) {
    return { exitCode: -1, stdout: '', stderr: `無法執行：${(err as Error).message}` }
  }
}
function tail(s: string, n = 8): string {
  return s.trim().split(/\r?\n/).slice(-n).join('\n')
}
async function forbidCheck($: any, root: string, c: Check, file?: string): Promise<Finding[]> {
  const specs = file ? [file] : pathspecs(c)
  const r = await run($, ['git', 'grep', '-nIP', '--untracked', '-e', c.forbid!, '--', ...specs], root)
  if (r.exitCode === 1) return []
  if (r.exitCode !== 0) return [{ id: c.id, severity: 'warn', text: `沒有執行成功：${tail(r.stderr, 3)}` }]
  const hits = r.stdout.trim().split(/\r?\n/).slice(0, 10)
  return hits.map((h: string) => {
    const [path, line] = h.split(':')
    return { id: c.id, severity: c.severity as 'error' | 'warn', text: `${path}:${line} ${c.message}` }
  })
}
async function runCheck($: any, root: string, c: Check, file?: string): Promise<Finding[]> {
  const argv = c.run!.map(a => (file ? a.split('{file}').join(file) : a))
  const r = await run($, argv, root)
  if (r.exitCode === 0) return []
  if (r.exitCode === -1) return [{ id: c.id, severity: 'warn', text: `${r.stderr}（沒有檢查到）` }]
  return [{ id: c.id, severity: c.severity as 'error' | 'warn', text: `${c.message}\n${tail(r.stdout + '\n' + r.stderr)}` }]
}
async function astGrep($: any, root: string, file?: string): Promise<Finding[]> {
  const cfg = `${LINT}/sgconfig.yml`
  if (!(await $.fs.exists(`${root}/${cfg}`))) return []
  const r = await run($, ['ast-grep', 'scan', '-c', cfg, '--json=compact', ...(file ? [file] : [])], root)
  if (r.exitCode === -1) return [{ id: 'ast-grep', severity: 'warn', text: `${r.stderr}（rules/ 沒有檢查到）` }]
  let items: any[]
  try {
    items = JSON.parse(r.stdout || '[]')
  } catch {
    return [{ id: 'ast-grep', severity: 'warn', text: `輸出讀不懂：${tail(r.stderr || r.stdout, 3)}` }]
  }
  return items.slice(0, 20).map(m => ({
    id: m.ruleId,
    severity: m.severity === 'error' ? 'error' : 'warn',
    text: `${String(m.file).replace(/\\/g, '/')}:${(m.range?.start?.line ?? 0) + 1} ${m.message}`,
  }))
}
async function changedFiles($: any, root: string): Promise<string[]> {
  const r = await run($, ['git', 'status', '--porcelain', '--untracked-files=all'], root)
  return r.stdout
    .split(/\r?\n/)
    .filter(Boolean)
    .map((l: string) => l.slice(3).replace(/^"|"$/g, '').split(' -> ').pop()!)
}

// ---- built-ins ----
async function gitFacts($: any, root: string): Promise<{ text: string; authors: string[]; commits: number; coAuthor: number; prMerges: number; defaultBranch: string }> {
  const out = async (argv: string[]): Promise<string> => String((await run($, argv, root, 30000)).stdout).trim()
  const remote = await out(['git', 'remote', 'get-url', 'origin'])
  let visibility = '未知'
  if (/github\.com/i.test(remote)) {
    const v = await out(['gh', 'repo', 'view', '--json', 'visibility', '-q', '.visibility'])
    if (v) visibility = v === 'PUBLIC' ? '公開' : v === 'PRIVATE' ? '私人' : v
  }
  const name = await out(['git', 'config', 'user.name'])
  const email = await out(['git', 'config', 'user.email'])
  const authorLines = (await out(['git', 'log', '-30', '--format=%an <%ae>'])).split(/\r?\n/).filter(Boolean)
  const counts = new Map<string, number>()
  for (const a of authorLines) counts.set(a, (counts.get(a) ?? 0) + 1)
  const authors = [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([a, n]) => `${a}（${n}）`)
  const subjects = (await out(['git', 'log', '-8', '--format=%s'])).split(/\r?\n/).filter(Boolean)
  const bodies = await out(['git', 'log', '-30', '--format=%B%x00'])
  const coAuthor = bodies.split('\0').filter(b => /Co-Authored-By:/i.test(b)).length
  const merges = (await out(['git', 'log', '-50', '--merges', '--format=%s'])).split(/\r?\n/).filter(Boolean)
  const prMerges = merges.filter(s => /Merge pull request|See merge request|Merge branch '.+' into/.test(s)).length
  const head = await out(['git', 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD'])
  const defaultBranch = head.replace(/^origin\//, '') || 'main'
  const branch = await out(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
  const text = [
    `遠端：${remote || '（沒有 origin）'}（${visibility}）`,
    `目前身分：${name} <${email}>；近期作者：${authors.slice(0, 3).join('、') || '（沒有歷史）'}`,
    `近期 commit 標題：\n${subjects.map(s => `  - ${s}`).join('\n')}`,
    `近 30 個 commit 有 Co-Authored-By 的：${coAuthor} 個`,
    `目前分支：${branch}；主分支：${defaultBranch}；近 50 個 merge 裡來自 PR/MR 的：${prMerges} 個（${prMerges >= 3 ? '習慣開 PR/MR' : '習慣直接 push'}）`,
  ].join('\n')
  return { text, authors: [...counts.keys()], commits: authorLines.length, coAuthor, prMerges, defaultBranch }
}
async function gitFactsAtCommit($: any, root: string, c: Check, command: string): Promise<Finding[]> {
  const f = await gitFacts($, root)
  const out: Finding[] = []
  const email = (await run($, ['git', 'config', 'user.email'], root)).stdout.trim().toLowerCase()
  const sev = c.severity as 'error' | 'warn'
  if (f.commits >= 5 && email && !f.authors.some(a => a.toLowerCase().includes(`<${email}>`)))
    out.push({ id: c.id, severity: sev, text: `目前的 git 身分 <${email}> 不在這個 repo 的近期作者裡。${c.message}\n${f.text}` })
  if (/\bcommit\b/.test(command) && /Co-Authored-By:/i.test(command) && f.coAuthor === 0 && f.commits >= 5)
    out.push({ id: c.id, severity: sev, text: `這個 repo 近 30 個 commit 都沒有 Co-Authored-By，這次卻加了。${c.message}` })
  const branch = (await run($, ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], root)).stdout.trim()
  if (/\bpush\b/.test(command) && f.prMerges >= 3 && branch === f.defaultBranch)
    out.push({ id: c.id, severity: sev, text: `這個 repo 習慣透過 PR/MR 合併，這次卻直接 push 到 ${f.defaultBranch}。${c.message}` })
  return out
}
async function secretFiles($: any, root: string, c: Check): Promise<Finding[]> {
  const staged = (await run($, ['git', 'diff', '--cached', '--name-only'], root)).stdout.split(/\r?\n/).filter(Boolean)
  const bad = staged.filter((p: string) =>
    /(^|\/)(\.env(\..*)?|[^/]*\.pem|[^/]*\.key|id_rsa[^/]*|[^/]*\.p12|credentials[^/]*\.json)$/i.test(p),
  )
  return bad.map((p: string) => ({ id: c.id, severity: c.severity as 'error' | 'warn', text: `${p}：${c.message}` }))
}
function sessionRecord(c: Check): Finding[] {
  const after = commands.filter(x => x.seq === editSeq)
  const lines = after.slice(-15).map(x => `  ${x.ok ? '✓' : '✗'} ${x.cmd.slice(0, 120)}`)
  const reviewed = editSeq === 0 ? '這個 session 沒有改檔' : reviewedAt >= editSeq ? '有' : '沒有'
  const text = [
    `最後一次改檔之後跑過的指令：${lines.length ? '\n' + lines.join('\n') : '（沒有）'}`,
    `最後一次改檔之後有沒有跑 /review：${reviewed}`,
  ].join('\n')
  const missing = editSeq > 0 && (lines.length === 0 || reviewedAt < editSeq)
  return [{ id: c.id, severity: missing ? (c.severity as 'error' | 'warn') : 'note', text: missing ? `${text}\n${c.message}` : text }]
}
async function worktreeCleanup($: any, root: string, c: Check): Promise<Finding[]> {
  const list = (await run($, ['git', 'worktree', 'list', '--porcelain'], root)).stdout
  const merged = new Set(
    (await run($, ['git', 'branch', '--merged', 'HEAD', '--format=%(refname:short)'], root)).stdout
      .split(/\r?\n/)
      .map((s: string) => s.trim())
      .filter(Boolean),
  )
  const out: Finding[] = []
  let path = ''
  for (const line of list.split(/\r?\n/)) {
    if (line.startsWith('worktree ')) path = line.slice(9)
    if (line.startsWith('branch ')) {
      const b = line.slice(7).replace('refs/heads/', '')
      if (path.replace(/\\/g, '/') !== root && merged.has(b))
        out.push({ id: c.id, severity: c.severity as 'error' | 'warn', text: `${path}（${b}）：${c.message}` })
    }
  }
  return out
}

// ---- shell commands ----
// A `(?i)` prefix (PCRE style) becomes the JS `i` flag.
function commandRe(src: string): RegExp {
  return src.startsWith('(?i)') ? new RegExp(src.slice(4), 'im') : new RegExp(src, 'm')
}
function commandFindings(checks: Check[], command: string): Finding[] {
  const out: Finding[] = []
  for (const c of checks) {
    if (!c.on.includes('bash') || !c.forbid) continue
    try {
      if (commandRe(c.forbid).test(command)) out.push({ id: c.id, severity: c.severity as 'error' | 'warn', text: c.message })
    } catch (err) {
      out.push({ id: c.id, severity: 'warn', text: `regex 讀不懂：${(err as Error).message}` })
    }
  }
  return out
}
// Words of one shell segment, quotes removed.
function words(segment: string): string[] {
  return (segment.match(/"[^"]*"|'[^']*'|\S+/g) ?? []).map(w => w.replace(/^["']|["']$/g, ''))
}
async function describePath($: any, p: string): Promise<string> {
  if (/[*?[]/.test(p)) return `${p}（萬用字元：先 ls 看實際範圍）`
  try {
    if (!(await $.fs.exists(p))) return `${p}（不存在）`
    const s = await $.fs.stat(p)
    if (s.kind === 'dir') {
      const n = (await $.fs.list(p)).length
      return `${p}/（資料夾，第一層 ${n} 項）`
    }
    return `${p}（檔案）`
  } catch {
    return `${p}（讀不到）`
  }
}
async function destructivePreview($: any, root: string, command: string): Promise<string[]> {
  const out: string[] = []
  const lines = async (argv: string[], max = 15) =>
    String((await run($, argv, root, 30000)).stdout).trim().split(/\r?\n/).filter(Boolean).slice(0, max)
  for (const seg of command.split(/&&|\|\||;|\||\r?\n/)) {
    const w = words(seg.trim())
    if (!w.length) continue
    const cmd = w[0].toLowerCase()
    const args = w.slice(1).filter(a => !a.startsWith('-'))
    if (['rm', 'rmdir', 'del', 'remove-item', 'ri', 'erase'].includes(cmd)) {
      for (const a of args) out.push(`刪除 ${await describePath($, a)}`)
    } else if (['mv', 'move-item', 'move'].includes(cmd) && args.length >= 2) {
      const dest = args[args.length - 1]
      for (const a of args.slice(0, -1)) out.push(`搬移 ${await describePath($, a)} → ${await describePath($, dest)}`)
    } else if (cmd === 'git') {
      const sub = w[1]
      const rest = w.slice(2)
      if (sub === 'clean') {
        const flags = ['-n', ...(rest.some(a => /^-[a-z]*d/.test(a)) ? ['-d'] : []), ...(rest.some(a => /^-[a-z]*x/i.test(a)) ? ['-x'] : [])]
        const hit = await lines(['git', 'clean', ...flags])
        out.push(...(hit.length ? hit.map(h => `git clean 會刪：${h.replace(/^Would remove /, '')}`) : ['git clean：沒有要刪的檔案']))
      } else if (sub === 'reset' && rest.includes('--hard')) {
        const hit = await lines(['git', 'status', '--short'])
        out.push(...(hit.length ? hit.map(h => `reset --hard 會丟掉：${h}`) : ['reset --hard：工作樹沒有未 commit 的改動']))
      } else if ((sub === 'checkout' && rest.includes('--')) || sub === 'restore') {
        const paths = rest.slice(rest.indexOf('--') + 1).filter(a => !a.startsWith('-'))
        const hit = await lines(['git', 'diff', '--stat', '--', ...paths])
        out.push(...(hit.length ? hit.map(h => `會丟掉的改動：${h.trim()}`) : ['這些檔案沒有未 commit 的改動']))
      } else if (sub === 'branch' && (rest.includes('-D') || rest.includes('-d') || rest.includes('--delete'))) {
        const merged = new Set(await lines(['git', 'branch', '--merged', 'HEAD', '--format=%(refname:short)'], 500))
        for (const b of rest.filter(a => !a.startsWith('-'))) {
          const log = await lines(['git', 'log', '--oneline', '-3', b], 3)
          out.push(`刪除分支 ${b}（${merged.has(b) ? '已合併進 HEAD' : '沒有合併進 HEAD'}）：${log.join('；') || '找不到這個分支'}`)
        }
      } else if (sub === 'worktree' && w[2] === 'remove') {
        for (const p of w.slice(3).filter(a => !a.startsWith('-'))) {
          const dirty = await lines(['git', '-C', p, 'status', '--short'])
          out.push(`移除 worktree ${p}：${dirty.length ? `還有 ${dirty.length} 個沒 commit 的改動（${dirty.slice(0, 5).join('、')}）` : '乾淨'}`)
        }
      } else if (sub === 'stash' && (w[2] === 'drop' || w[2] === 'clear')) {
        const list = await lines(['git', 'stash', 'list'])
        out.push(`stash ${w[2]}：${list.length ? list.join('；') : '沒有 stash'}`)
      }
    }
  }
  return out
}

// ---- one moment ----
async function runMoment($: any, root: string, moment: 'edit' | 'commit' | 'done', opts: { file?: string; command?: string } = {}): Promise<Finding[]> {
  const { checks, problems } = await loadChecks($, root)
  const out: Finding[] = [...problems]
  const changed = moment === 'edit' ? [] : await changedFiles($, root)
  for (const c of checks) {
    if (c.builtin) {
      if (moment === 'commit' && c.builtin === 'git-facts') out.push(...(await gitFactsAtCommit($, root, c, opts.command ?? '')))
      if (moment === 'commit' && c.builtin === 'secret-files') out.push(...(await secretFiles($, root, c)))
      if (moment === 'done' && c.builtin === 'session-record') out.push(...sessionRecord(c))
      continue
    }
    if (!c.on.includes(moment)) continue
    if (moment === 'edit') {
      if (!opts.file || !inScope(opts.file, c)) continue
      if (c.forbid) out.push(...(await forbidCheck($, root, c, opts.file)))
      else if (c.run) out.push(...(await runCheck($, root, c, opts.file)))
      continue
    }
    const touched = c.files.length > 0 && changed.some(p => inScope(p, c))
    if (c.changed && touched) out.push({ id: c.id, severity: 'note', text: c.changed })
    if (c.forbid) out.push(...(await forbidCheck($, root, c)))
    else if (c.run && !c.run.some(a => a.includes('{file}')) && (c.files.length === 0 || touched)) out.push(...(await runCheck($, root, c)))
  }
  out.push(...(await astGrep($, root, moment === 'edit' ? opts.file : undefined)))
  return out
}

const MOMENT = { edit: '改檔後', commit: 'commit 前', done: '收尾前', bash: '指令前' } as const
function render(moment: keyof typeof MOMENT, where: string, findings: Finding[]): string {
  const errors = findings.filter(f => f.severity === 'error').length
  const warns = findings.filter(f => f.severity === 'warn').length
  const head = `lint · ${MOMENT[moment]}${where ? ' · ' + where : ''}：${errors} error、${warns} warn`
  const mark = { error: '✖', warn: '⚠', note: '·' } as const
  return [head, ...findings.map(f => `${mark[f.severity]} ${f.id}：${f.text}`)].join('\n')
}
async function notify($: any, text: string) {
  try {
    await $.session.append({ message: { type: 'system', content: [{ type: 'text', text }] } })
  } catch {}
}

export const register: Register = on => {
  // Session start: worktrees left behind, and the repo's git facts for the model.
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    const root = await projectRoot($)
    if (!(await hasLint($, root))) return result
    const { checks } = await loadChecks($, root!)
    const wt = checks.find(c => c.builtin === 'worktree-cleanup')
    if (wt) {
      const f = await worktreeCleanup($, root!, wt)
      if (f.length) await notify($, `lint · session 開始 · 沒清掉的 worktree\n${f.map(x => `⚠ ${x.text}`).join('\n')}`)
    }
    if (checks.some(c => c.builtin === 'git-facts')) gitFactsText = (await gitFacts($, root!)).text
    const lang = checks.find(c => c.builtin === 'user-language')
    if (lang?.language) userLanguage = lang.language
    return result
  })

  // The model reads the repo's git facts and the user's language in the system prompt.
  on('prompt.compose', async ($, e, next) => {
    const result = await next(e)
    const add: { id: string; text: string; scope: 'session' }[] = []
    if (gitFactsText) add.push({ id: 'baransu:lint-git', text: `這個 repo 的 git 習慣（baransu lint）。commit、push、開分支前照這些：\n${gitFactsText}`, scope: 'session' })
    if (userLanguage) add.push({ id: 'baransu:lint-language', text: `使用者的慣用語言：${userLanguage}。寫給使用者看的文字一律用這個語言。`, scope: 'session' })
    return add.length ? { ...result, sections: [...result.sections, ...add] } : result
  })

  // The user's language, from what they type, unless a check pins it.
  on('prompt.submit', async ($, e, next) => {
    if (!e.isMeta && !e.command && e.text.trim()) {
      const root = await projectRoot($)
      if (await hasLint($, root)) {
        const { checks } = await loadChecks($, root!)
        const lang = checks.find(c => c.builtin === 'user-language')
        if (lang && !lang.language) {
          const han = (e.text.match(/\p{Script=Han}/gu) ?? []).length
          const letters = (e.text.match(/\p{L}/gu) ?? []).length
          userLanguage = letters && han / letters > 0.2 ? '中文（照使用者用的字，繁體或簡體）' : 'English'
        }
      }
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  // A new turn on the main loop has not spoken to the user yet.
  on('turn.start', ($, e, next) => {
    if (!e.agentId) spokeThisTurn = false
    return next(e)
  })
  on('session.append', ($, e, next) => {
    if (!e.agentId && e.message.type === 'assistant' && (e.message.content as any[]).some(b => b.type === 'text' && String(b.text).trim()))
      spokeThisTurn = true
    return next(e)
  }).catch(($, e, next) => next(e))

  on('tool.call', async ($, e: any, next) => {
    const tool: string = e.tool
    const isEdit = EDIT_TOOLS.has(tool)
    const isBash = SHELL_TOOLS.has(tool)
    if (!isEdit && !isBash) return next(e)
    const root = await projectRoot($)
    if (!(await hasLint($, root))) return next(e)
    const command: string = isBash ? String(e.command ?? '') : ''
    const context: string[] = []

    // Explain before acting: the first edit or command of a turn should follow words to the user.
    if (!e.agentId && !spokeThisTurn) {
      const { checks } = await loadChecks($, root!)
      const c = checks.find(x => x.builtin === 'explain-before-edit')
      spokeThisTurn = true
      if (c) {
        await notify($, `lint · ${c.id}：這一輪還沒跟使用者說明，就先${isEdit ? '改檔' : '跑指令'}了`)
        if (c.severity === 'error') return { deny: c.message }
        context.push(`baransu lint（${c.id}）：${c.message}`)
      }
    }

    // Before any shell command: checks that read the command line itself.
    if (isBash) {
      const { checks } = await loadChecks($, root!)
      const findings = commandFindings(checks, command)
      if (findings.length) await notify($, render('bash', '', findings))
      if (findings.some(f => f.severity === 'error')) return { deny: `${render('bash', '', findings)}\n照上面改寫這個指令再跑。` }
      if (findings.length) context.push(render('bash', '', findings))

      // Before a command that deletes, moves or discards: show the model what it will touch, once.
      const preview = checks.find(c => c.builtin === 'destructive-preview')
      if (preview && !previewed.has(command)) {
        const touched = await destructivePreview($, root!, command)
        if (touched.length) {
          previewed.add(command)
          const text = `lint · ${preview.id}：這個指令會動到\n${touched.map(t => `  ${t}`).join('\n')}`
          await notify($, text)
          if (preview.severity === 'error') return { deny: `${text}\n${preview.message}` }
          context.push(text)
        }
      }
    }

    // Before a git commit or push.
    if (isBash && GIT_WRITE.test(command)) {
      const findings = await runMoment($, root!, 'commit', { command })
      if (findings.length) await notify($, render('commit', '', findings))
      if (findings.some(f => f.severity === 'error')) return { deny: `${render('commit', '', findings)}\n修好 error 再 commit / push。` }
      if (findings.length) context.push(render('commit', '', findings))
    }

    const result: any = await next(e)
    if (isBash && result && !result.deny) commands.push({ cmd: command, ok: result.isError !== true, seq: editSeq })

    // After a successful edit.
    if (isEdit && result && !result.deny && !result.isError) {
      editSeq++
      const file = relTo(root!, String(e.file_path ?? e.notebook_path ?? ''))
      const findings = (await runMoment($, root!, 'edit', { file })).filter(f => f.severity !== 'note')
      if (findings.length) {
        const text = render('edit', file, findings)
        await notify($, text)
        context.push(`${text}\n修好 error；warn 判斷要不要改。`)
      }
    }
    if (context.length && result && !result.deny && !result.isError) return { ...result, context: [...(result.context ?? []), ...context] }
    return result
  }).catch(($, e, next) => next(e))

  // Before /ship or /review: the full set, written as this version's lint record.
  on('skill.prompt', async ($, e, next) => {
    const result = await next(e)
    if (!DONE_SKILLS.has(e.skill)) return result
    const isReview = e.skill.endsWith('review')
    if (isReview) reviewedAt = editSeq
    const root = await projectRoot($)
    if (!(await hasLint($, root))) return result
    const findings = await runMoment($, root!, 'done')
    const text = render('done', isReview ? '/review' : '/ship', findings)
    await notify($, text)
    const errors = findings.some(f => f.severity === 'error')
    const tailLine = isReview
      ? '這是 review 開始前、作者這一端跑的 lint 紀錄，照 review 的判定規則讀。'
      : errors
        ? '有 error：停下，不要 commit；把上面的 error 回報給使用者。'
        : '沒有 error，可以繼續；warn 要在收尾報告裡提到。'
    return { ...result, text: `## Lint 紀錄（baransu lint mod，這個版本）\n\n${text}\n\n${tailLine}\n\n${result.text}` }
  })
}
