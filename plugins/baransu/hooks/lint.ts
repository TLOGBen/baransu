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
const CORRECTION = /又犯|又錯|又忘|又來了|不是這樣|(?<!對)不對(?!勁)|錯了|說過了?|講過|跟你說|別再|不要再|為什麼又|\bagain\b|\bwrong\b|told you|\bstop doing\b|don'?t do that/i

// ---- session memory (module scope: a reload starts it over) ----
let editSeq = 0
let reviewedAt = -1
const commands: { cmd: string; ok: boolean; seq: number }[] = []
let spokeThisTurn = true
let userLanguage: string | undefined
let gitFactsText: string | undefined
const previewed = new Set<string>()
let languageSlip: string | undefined

// Share of Han characters among letters, code left out.
function hanShare(text: string): { han: number; letters: number } {
  const prose = text.replace(/```[\s\S]*?```/g, ' ').replace(/`[^`\n]*`/g, ' ').replace(/https?:\/\/\S+/g, ' ')
  return { han: (prose.match(/\p{Script=Han}/gu) ?? []).length, letters: (prose.match(/\p{L}/gu) ?? []).length }
}
const wantsChinese = () => !!userLanguage && /中文|zh/i.test(userLanguage)

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
// The repo root is asked once per working directory; the checks are reread at most every few seconds,
// or at once after an edit inside .claude/lint/.
const rootCache = new Map<string, string | undefined>()
let checksCache: { root: string; at: number; value: { checks: Check[]; problems: Finding[] } } | undefined
async function projectRoot($: any): Promise<string | undefined> {
  let cwd = ''
  try { cwd = await $.session.cwd() } catch {}
  if (rootCache.has(cwd)) return rootCache.get(cwd)
  let root: string | undefined
  try {
    const r = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
    if (r.exitCode === 0) root = r.stdout.trim().replace(/\\/g, '/')
  } catch {}
  rootCache.set(cwd, root)
  return root
}
function relTo(root: string, file: string): string {
  const f = file.replace(/\\/g, '/')
  return f.toLowerCase().startsWith(root.toLowerCase() + '/') ? f.slice(root.length + 1) : f
}
async function loadChecks($: any, root: string): Promise<{ checks: Check[]; problems: Finding[] }> {
  if (checksCache && checksCache.root === root && Date.now() - checksCache.at < 5000) return checksCache.value
  const value = await readChecks($, root)
  checksCache = { root, at: Date.now(), value }
  return value
}
async function readChecks($: any, root: string): Promise<{ checks: Check[]; problems: Finding[] }> {
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
async function gitFacts($: any, root: string): Promise<{ text: string; authors: string[]; commits: number; coAuthor: number; prHabit: boolean; defaultBranch: string }> {
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
  // The habit is what the main line does lately: of its last 20 first-parent commits, how many are PR or MR merges.
  // A local `Merge branch 'x' into main` is not a PR.
  const line = (await out(['git', 'log', '-20', '--first-parent', '--format=%s'])).split(/\r?\n/).filter(Boolean)
  const prMerges = line.filter(s => /^Merge pull request #\d+|See merge request /.test(s)).length
  const prHabit = line.length > 0 && prMerges * 2 > line.length
  const head = await out(['git', 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD'])
  const defaultBranch = head.replace(/^origin\//, '') || 'main'
  const branch = await out(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
  const text = [
    `遠端：${remote || '（沒有 origin）'}（${visibility}）`,
    `目前身分：${name} <${email}>；近期作者：${authors.slice(0, 3).join('、') || '（沒有歷史）'}`,
    `近期 commit 標題：\n${subjects.map(s => `  - ${s}`).join('\n')}`,
    `近 30 個 commit 有 Co-Authored-By 的：${coAuthor} 個`,
    `目前分支：${branch}；主分支：${defaultBranch}；主線最近 ${line.length} 個 commit 裡來自 PR/MR 合併的：${prMerges} 個（${prHabit ? '習慣開 PR/MR' : '習慣直接 push'}）`,
  ].join('\n')
  return { text, authors: [...counts.keys()], commits: authorLines.length, coAuthor, prHabit, defaultBranch }
}
async function gitFactsAtCommit($: any, root: string, c: Check, command: string): Promise<Finding[]> {
  const f = await gitFacts($, root)
  const out: Finding[] = []
  const sev = c.severity as 'error' | 'warn'
  const known = (email: string) => f.authors.some(a => a.toLowerCase().includes(`<${email}>`))
  if (/\bcommit\b/.test(command)) {
    // `git -c user.email=X commit` commits as X whatever the config says.
    const override = /-c\s+["']?user\.email=["']?([^"'\s]+)/.exec(command)?.[1]
    const email = (override ?? String((await run($, ['git', 'config', 'user.email'], root)).stdout)).trim().toLowerCase()
    if (f.commits >= 5 && email && !known(email))
      out.push({ id: c.id, severity: sev, text: `目前的 git 身分 <${email}> 不在這個 repo 的近期作者裡。${c.message}\n${f.text}` })
  } else if (/\bpush\b/.test(command)) {
    // A push makes no commit: what matters is who wrote the commits it sends.
    const sent = String((await run($, ['git', 'log', '@{u}..HEAD', '--format=%ae'], root)).stdout).split(/\r?\n/).map(s => s.trim().toLowerCase()).filter(Boolean)
    const strangers = [...new Set(sent.filter(e => !known(e)))]
    if (f.commits >= 5 && strangers.length)
      out.push({ id: c.id, severity: sev, text: `要推上去的 commit 裡有不屬於這個 repo 近期作者的身分：${strangers.join('、')}。${c.message}` })
  }
  if (/\bcommit\b/.test(command) && /Co-Authored-By:/i.test(command) && f.coAuthor === 0 && f.commits >= 5)
    out.push({ id: c.id, severity: sev, text: `這個 repo 近 30 個 commit 都沒有 Co-Authored-By，這次卻加了。${c.message}` })
  const branch = (await run($, ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], root)).stdout.trim()
  if (/\bpush\b/.test(command) && f.prHabit && branch === f.defaultBranch)
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
// At commit: was anything built or tested since the last edit? At done, also: was it reviewed?
function sessionRecord(c: Check, needReview: boolean): Finding[] {
  const after = commands.filter(x => x.seq === editSeq && !GIT_WRITE.test(x.cmd))
  const lines = after.slice(-15).map(x => `  ${x.ok ? '✓' : '✗'} ${x.cmd.slice(0, 120)}`)
  const reviewed = editSeq === 0 ? '這個 session 沒有改檔' : reviewedAt >= editSeq ? '有' : '沒有'
  const text = [
    `最後一次改檔之後跑過的指令：${lines.length ? '\n' + lines.join('\n') : '（沒有）'}`,
    ...(needReview ? [`最後一次改檔之後有沒有跑 /review：${reviewed}`] : []),
  ].join('\n')
  const missing = editSeq > 0 && (lines.length === 0 || (needReview && reviewedAt < editSeq))
  return [{ id: c.id, severity: missing ? (c.severity as 'error' | 'warn') : 'note', text: missing ? `${text}\n${c.message}` : text }]
}
// Before a commit or push: has the remote moved on since this branch last caught up?
async function upToDate($: any, root: string, c: Check): Promise<Finding[]> {
  const fetched = await run($, ['git', 'fetch', '--quiet'], root, 20000)
  if (fetched.exitCode !== 0) return [{ id: c.id, severity: 'warn', text: `git fetch 沒成功，無法確認是不是最新版：${tail(fetched.stderr, 2)}` }]
  const behind = await run($, ['git', 'rev-list', '--count', 'HEAD..@{u}'], root, 10000)
  if (behind.exitCode !== 0) return []
  const n = Number(String(behind.stdout).trim())
  return n > 0 ? [{ id: c.id, severity: c.severity as 'error' | 'warn', text: `遠端有 ${n} 個本機還沒有的 commit。${c.message}` }] : []
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
  // A `cd` earlier in the same command moves where later relative paths point.
  let base = ''
  const at = (p: string) => (/^([A-Za-z]:)?[\\/]/.test(p) || !base ? p : `${base}/${p}`)
  for (const seg of command.split(/&&|\|\||;|\||\r?\n/)) {
    const w = words(seg.trim())
    if (!w.length) continue
    const cmd = w[0].toLowerCase()
    const args = w.slice(1).filter(a => !a.startsWith('-'))
    if ((cmd === 'cd' || cmd === 'set-location') && args[0]) {
      base = at(args[0]).replace(/\\/g, '/').replace(/\/$/, '')
    } else if (['rm', 'rmdir', 'del', 'remove-item', 'ri', 'erase'].includes(cmd)) {
      for (const a of args) out.push(`刪除 ${await describePath($, at(a))}`)
    } else if (['mv', 'move-item', 'move'].includes(cmd) && args.length >= 2) {
      const dest = args[args.length - 1]
      for (const a of args.slice(0, -1)) out.push(`搬移 ${await describePath($, at(a))} → ${await describePath($, at(dest))}`)
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
      if (moment === 'commit' && c.builtin === 'built-before-commit') out.push(...sessionRecord(c, false).filter(f => f.severity !== 'note'))
      if (moment === 'commit' && c.builtin === 'up-to-date') out.push(...(await upToDate($, root, c)))
      if (moment === 'done' && c.builtin === 'session-record') out.push(...sessionRecord(c, true))
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
// ---- drawing: a card for each held or refused call, and a band above the prompt ----
// A card: an optional bold title (what happened), a meta line (which lint moment, the counts),
// the findings, and an optional footer (what to do next). `replace` draws it in place of the error text.
type Drawn = { kind: 'hold' | 'error' | 'warn'; title?: string; meta: string; lines: Finding[]; footer?: string; replace?: boolean }
const drawn = new Map<string, Drawn>()

// Colors from the design canvas "Lint 卡片樣式": tint, border, strong text, meta text, body text, icon.
const PALETTE = {
  error: { bg: '#FDF3F3', border: '#F2CFCF', strong: '#8E1B1B', meta: '#A35A5A', body: '#3B2020', icon: '#D63B3B', chip: '#F0C6C6' },
  hold: { bg: '#FDF7EA', border: '#EFD9A6', strong: '#7A4A06', meta: '#9C6E2A', body: '#3A2A0E', icon: '#E39A1C', chip: '#F0DDB0' },
  warn: { bg: '#FFFBF2', border: '#F3E3BD', strong: '#7A4A06', meta: '#9C6E2A', body: '#3A2A0E', icon: '#C98A16', chip: '#F0DDB0' },
} as const
const SHIELD = 'M14 3.5 L22.5 6.8 V13 C22.5 18.4 18.9 22.3 14 24.5 C9.1 22.3 5.5 18.4 5.5 13 V6.8 Z'
function iconSvg(kind: Drawn['kind']): string {
  const c = PALETTE[kind].icon
  const svg = (body: string) => `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28" overflow="visible">${body}</svg>`
  if (kind === 'error')
    return svg(`<circle cx="14" cy="14" r="10" fill="none" stroke="${c}" stroke-width="1.6"><animate attributeName="r" values="9;14;14" keyTimes="0;0.7;1" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0;0" keyTimes="0;0.7;1" dur="1.6s" repeatCount="indefinite"/></circle><path d="${SHIELD}" fill="${c}"/><rect x="12.8" y="8.6" width="2.4" height="7" rx="1.2" fill="#fff"/><circle cx="14" cy="18.8" r="1.5" fill="#fff"/>`)
  if (kind === 'hold')
    return svg(`<path d="${SHIELD}" fill="${c}"/><g><animate attributeName="opacity" values="1;0.45;1" dur="1.8s" repeatCount="indefinite"/><rect x="10.6" y="9.4" width="2.4" height="8.4" rx="1" fill="#fff"/><rect x="15" y="9.4" width="2.4" height="8.4" rx="1" fill="#fff"/></g>`)
  return svg(`<path d="M14 4.5 L24 22 H4 Z" fill="none" stroke="${c}" stroke-width="1.8" stroke-linejoin="round"/><rect x="13.1" y="11" width="1.8" height="6" rx="0.9" fill="${c}"/><circle cx="14" cy="19.4" r="1.1" fill="${c}"/>`)
}
function card($: any, e: any, d: Drawn): any {
  const els = $.ui.resolve(e) as any
  const { Box, Text } = els
  const terminal = e.surface === 'terminal'
  const p = PALETTE[d.kind]
  // The terminal keeps theme colors so the card reads in any terminal palette.
  const strong = terminal ? (d.kind === 'error' ? 'error' : 'warning') : p.strong
  const meta = terminal ? 'subtle' : p.meta
  const body = terminal ? 'text' : p.body
  const icon = !terminal && els.Svg
    ? h(els.Svg, { source: iconSvg(d.kind), alt: d.title ?? d.meta, width: 28, height: 28, isInteractive: true })
    : h(Text, { color: strong, bold: true }, d.kind === 'hold' ? '⏸' : d.kind === 'error' ? '✖' : '⚠')
  const line = (l: Finding) => l.id
    ? h(Box, { flexDirection: 'row', gap: 'sm' },
        h(Text, { mono: true, size: 'footnote', color: strong, backgroundColor: terminal ? undefined : '#FFFFFF' }, terminal ? `[${l.id}]` : ` ${l.id} `),
        h(Text, { color: body }, l.text.split('\n')[0]))
    : h(Text, { color: body }, `· ${l.text}`)
  return h(Box, { flexDirection: 'row', gap: 'md', borderStyle: 'round', borderColor: terminal ? strong : p.border, backgroundColor: terminal ? undefined : p.bg, padding: 'md' },
    icon,
    h(Box, { flexDirection: 'column', gap: 'sm', flexShrink: 1 },
      d.title
        ? h(Box, { flexDirection: 'row', gap: 'md', flexWrap: 'wrap' },
            h(Text, { bold: true, color: strong }, d.title),
            h(Text, { size: 'footnote', color: meta }, d.meta))
        : h(Text, { size: 'footnote', color: meta }, d.meta),
      ...d.lines.slice(0, 6).map(line),
      ...(d.footer ? [h(Text, { size: 'footnote', color: meta }, d.footer)] : [])))
}
function summarize(moment: string, findings: Finding[]): Drawn | null {
  const shown = findings.filter(f => f.severity !== 'note')
  if (!shown.length) return null
  const errors = shown.filter(f => f.severity === 'error').length
  const warns = shown.length - errors
  const counts = [errors ? `${errors} error` : '', warns ? `${warns} warn` : ''].filter(Boolean).join('、')
  return { kind: errors ? 'error' : 'warn', meta: `lint · ${moment} · ${counts}`, lines: shown }
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

  // What the user types: their language, and whether they are correcting the model.
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
        const fix = checks.find(c => c.builtin === 'correction-to-lint')
        // Only the words the user typed: drop tagged blocks the host or an artifact attached.
        const typed = e.text.replace(/<([a-z][\w-]*)\b[^>]*>[\s\S]*?<\/\1>/gi, ' ').replace(/<[a-z][\w-]*\b[^>]*\/>/gi, ' ')
        if (fix && CORRECTION.test(typed)) {
          await notify($, `lint · ${fix.id}：這像是在糾正，修完後會評估能不能寫成 lint`)
          return next({ ...e, context: [...(e.context ?? []), `baransu lint（${fix.id}）：使用者在糾正你。先照他說的修好，再判斷這個錯能不能寫成檢查：能，就交給 /baransu:lint 新增（附上這次錯在哪、怎麼修、出錯的 commit）；不能，用一句話說明為什麼。${fix.message}`] })
        }
      }
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  // A reply that ended the turn in the wrong language is shown to the person now; the model hears it on its next call.
  on('turn.complete', async ($, e: any, next) => {
    const result = await next(e)
    if (!e.agentId && languageSlip !== undefined) await notify($, `lint · user-language：剛才那段寫成英文了（「${languageSlip}…」）`)
    return result
  })

  // A new turn on the main loop has not spoken to the user yet.
  on('turn.start', ($, e, next) => {
    if (!e.agentId) spokeThisTurn = false
    return next(e)
  })
  on('session.append', ($, e, next) => {
    if (!e.agentId && e.message.type === 'assistant') {
      const text = (e.message.content as any[]).filter(b => b.type === 'text').map(b => String(b.text)).join('\n')
      if (text.trim()) spokeThisTurn = true
      // The user writes Chinese and this block is English prose: flag it on the next tool call.
      const { han, letters } = hanShare(text)
      if (wantsChinese() && letters >= 40 && han / letters < 0.1) languageSlip = text.trim().split('\n')[0].slice(0, 60)
    }
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
    // Everything lint says about this call is drawn as one card under it.
    const inline: Finding[] = []
    const refuse = (d: Drawn, deny: string) => {
      drawn.set(e.tool_use_id, { ...d, replace: true })
      return { deny }
    }

    // A block written in the wrong language since the last call.
    if (languageSlip !== undefined) {
      const { checks } = await loadChecks($, root!)
      const c = checks.find(x => x.builtin === 'user-language')
      if (c && !e.agentId) {
        inline.push({ id: c.id, severity: 'warn', text: `剛才那段寫成英文了（「${languageSlip}…」）` })
        context.push(`baransu lint（${c.id}）：剛才給使用者的那段寫成英文了（「${languageSlip}…」）。使用者用 ${userLanguage}；接下來寫給使用者看的文字一律用這個語言。`)
      }
      languageSlip = undefined
    }

    // Explain before acting: the first edit or command of a turn should follow words to the user.
    if (!e.agentId && !spokeThisTurn) {
      const { checks } = await loadChecks($, root!)
      const c = checks.find(x => x.builtin === 'explain-before-edit')
      spokeThisTurn = true
      if (c) {
        const f: Finding = { id: c.id, severity: c.severity === 'error' ? 'error' : 'warn', text: `這一輪還沒跟使用者說明，就先${isEdit ? '改檔' : '跑指令'}了` }
        if (c.severity === 'error') return refuse({ kind: 'error', title: '沒有執行', meta: `lint · ${c.id}`, lines: [f], footer: c.message }, c.message)
        inline.push(f)
        context.push(`baransu lint（${c.id}）：${c.message}`)
      }
    }

    // Before any shell command: checks that read the command line itself.
    if (isBash) {
      const { checks } = await loadChecks($, root!)
      const findings = commandFindings(checks, command)
      if (findings.some(f => f.severity === 'error')) {
        return refuse({ ...summarize('指令前', findings)!, title: '沒有執行', footer: '照上面改寫這個指令再跑' }, `${render('bash', '', findings)}\n照上面改寫這個指令再跑。`)
      }
      if (findings.length) {
        inline.push(...findings)
        context.push(render('bash', '', findings))
      }

      // Before a command that deletes, moves or discards: show the model what it will touch, once.
      const preview = checks.find(c => c.builtin === 'destructive-preview')
      if (preview && !previewed.has(command)) {
        const touched = await destructivePreview($, root!, command)
        if (touched.length) {
          previewed.add(command)
          const text = `lint · ${preview.id}：這個指令會動到\n${touched.map(t => `  ${t}`).join('\n')}`
          const lines = touched.map(t => ({ id: '', severity: 'note' as const, text: t }))
          if (preview.severity === 'error') return refuse({ kind: 'hold', title: '先確認會動到的東西', meta: 'lint · 刪除前預覽', lines, footer: '確認沒錯，再下一次同樣的指令就會執行' }, `${text}\n${preview.message}`)
          inline.push(...lines)
          context.push(text)
        }
      }
    }

    // Before a git commit or push.
    if (isBash && GIT_WRITE.test(command)) {
      const findings = await runMoment($, root!, 'commit', { command })
      if (findings.some(f => f.severity === 'error')) {
        return refuse({ ...summarize('commit 前', findings)!, title: /\bpush\b/.test(command) ? '沒有 push' : '沒有 commit', footer: '修好 error 再 commit／push' }, `${render('commit', '', findings)}\n修好 error 再 commit / push。`)
      }
      const shown = findings.filter(f => f.severity !== 'note')
      if (shown.length) {
        inline.push(...shown)
        context.push(render('commit', '', findings))
      }
    }

    const result: any = await next(e)
    if (isBash && result && !result.deny) commands.push({ cmd: command, ok: result.isError !== true, seq: editSeq })

    // After a successful edit.
    const file = isEdit ? relTo(root!, String(e.file_path ?? e.notebook_path ?? '')) : ''
    const insideRepo = file !== '' && !/^([A-Za-z]:)?\//.test(file)
    if (isEdit && insideRepo && result && !result.deny && !result.isError) {
      editSeq++
      if (file.startsWith(`${LINT}/`)) checksCache = undefined
      const findings = (await runMoment($, root!, 'edit', { file })).filter(f => f.severity !== 'note')
      if (findings.length) {
        inline.push(...findings)
        context.push(`${render('edit', file, findings)}\n修好 error；warn 判斷要不要改。`)
      }
    }

    if (inline.length && result && !result.deny) {
      const d = summarize(isEdit ? `改檔後 · ${file}` : GIT_WRITE.test(command) ? 'commit 前' : '指令前', inline)
      drawn.set(e.tool_use_id, d ?? { kind: 'warn', meta: 'lint', lines: inline })
    }
    if (context.length && result && !result.deny && !result.isError) return { ...result, context: [...(result.context ?? []), ...context] }
    return result
  }).catch(($, e, next) => next(e))

  // Lint's card under the call it is about: in place of the error text for a held or refused call,
  // below the tool's own result otherwise.
  on('ui.render', { component: 'ToolResult' }, async ($, e: any, next) => {
    const d = drawn.get(e.props?.tool_use_id)
    if (!d) return next(e)
    if (d.replace) return card($, e, d)
    const { Box } = $.ui.resolve(e) as any
    return h(Box, { flexDirection: 'column', gap: 1 }, await next(e), card($, e, d)) as any
  })

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
