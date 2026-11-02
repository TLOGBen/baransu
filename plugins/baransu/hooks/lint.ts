import type { Register } from 'claude-code'
import type { LintCard, LintFinding, LintState } from '../types'

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
  redo?: string
}
// `redo` (重新) is the fourth answer: the words already reached the user, so the fix is to say it again the right way.
type Finding = LintFinding

const LINT = '.claude/lint'
const EDIT_TOOLS = new Set(['Edit', 'Write', 'MultiEdit', 'NotebookEdit'])
const SHELL_TOOLS = new Set(['Bash', 'PowerShell'])
const GIT_WRITE = /\bgit\b[^|;&\n]*\b(commit|push)\b/
const DONE_SKILLS = new Set(['ship', 'review', 'baransu:ship', 'baransu:review'])
const CORRECTION = /又犯|又錯|又忘|又來了|不是這樣|(?<!對)不對(?!勁)|錯了|說過了?|講過|跟你說|別再|不要再|為什麼又|\bagain\b|\bwrong\b|told you|\bstop doing\b|don'?t do that/i

// ---- session memory: kept in $.state, so a reload of the mod (module variables start over) loses none of it ----
// The model of this state and the rules it keeps: .claude/hypothesis/lint-mod-state/.
const freshState = (): LintState => ({ editSeq: 0, reviewedAt: -1, commands: [], spoke: true, previewed: [], steps: {}, slips: [], tools: 0, textAfterTools: '', cards: {} })
let S: LintState = freshState()
let loading: Promise<void> | undefined
const STATE_REF = { plugin: 'baransu', key: 'lint' } as const
function restore($: any): Promise<void> {
  return (loading ??= (async () => {
    try {
      const r = await $.state.get(STATE_REF)
      if (r?.value) S = { ...freshState(), ...r.value }
    } catch {}
  })())
}
function persist($: any) {
  try {
    Promise.resolve($.state.set(STATE_REF, JSON.parse(JSON.stringify(S)))).catch(() => {})
  } catch {}
}

// Share of Han characters among letters, code left out.
function hanShare(text: string): { han: number; letters: number } {
  // Code, links and identifiers (session.start, lint.ts, camelCase, snake_case, a/path) are not prose.
  const prose = text.replace(/```[\s\S]*?```/g, ' ').replace(/`[^`\n]*`/g, ' ').replace(/https?:\/\/\S+/g, ' ')
    .replace(/[A-Za-z0-9_$-]*[._/\\][A-Za-z0-9_$./\\-]+|\b[a-z]+[A-Z][A-Za-z0-9]*\b/g, ' ')
  return { han: (prose.match(/\p{Script=Han}/gu) ?? []).length, letters: (prose.match(/\p{L}/gu) ?? []).length }
}
const wantsChinese = () => !!S.userLanguage && /中文|zh/i.test(S.userLanguage)
const slipHead = (text: string) => `${text.split('\n')[0].slice(0, 40)}…`
// The fix for a reply in the wrong language: restate it in the user's language the way /huh does.
// A check's own `redo` replaces the default instruction.
function restateNote(c: Check, text: string): string {
  const how = c.redo ?? `先照 /baransu:huh 的方式，用使用者的語言（${S.userLanguage}）把這段重新說一次——白話、不加術語，說的是同一件事；之後寫給使用者看的文字一律用這個語言。`
  return `baransu lint（${c.id}，重新）：剛才給使用者的那段寫成英文了。${how}那段原文：\n"""\n${text}\n"""`
}

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
        redo: typeof t.redo === 'string' ? t.redo : undefined,
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
  const after = S.commands.filter(x => x.seq === S.editSeq && !GIT_WRITE.test(x.cmd))
  const lines = after.slice(-15).map(x => `  ${x.ok ? '✓' : '✗'} ${x.cmd.slice(0, 120)}`)
  const reviewed = S.editSeq === 0 ? '這個 session 沒有改檔' : S.reviewedAt >= S.editSeq ? '有' : '沒有'
  const text = [
    `最後一次改檔之後跑過的指令：${lines.length ? '\n' + lines.join('\n') : '（沒有）'}`,
    ...(needReview ? [`最後一次改檔之後有沒有跑 /review：${reviewed}`] : []),
  ].join('\n')
  const missing = S.editSeq > 0 && (lines.length === 0 || (needReview && S.reviewedAt < S.editSeq))
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
// The commands of a command line: split on && || ; | and newlines outside quotes only,
// so a script passed in quotes (node -e "...", python -c '...') stays one command.
function segments(command: string): string[] {
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
// Words of one shell segment, quotes removed.
function words(segment: string): string[] {
  // A subshell's parentheses, `(cd x && rm y)`, are not part of the words.
  const plain = segment.replace(/^\s*\(+/, '').replace(/\)+\s*$/, '')
  return (plain.match(/"[^"]*"|'[^']*'|\S+/g) ?? []).map(w => w.replace(/^["']|["']$/g, ''))
}
async function describePath($: any, root: string, p: string): Promise<string> {
  const shown = relTo(root, p)
  if (/[~$%]/.test(p)) return `${shown}（含 ~ 或變數，mod 無法展開：改寫成實際路徑再刪）`
  if (/[*?[]/.test(p)) return `${shown}（萬用字元：先 ls 看實際範圍）`
  try {
    if (!(await $.fs.exists(p))) return `${shown}（不存在）`
    const s = await $.fs.stat(p)
    if (s.kind === 'dir') {
      const n = (await $.fs.list(p)).length
      return `${shown}/（資料夾，第一層 ${n} 項）`
    }
    return `${shown}（檔案）`
  } catch {
    return `${shown}（讀不到）`
  }
}
// The words of a segment without a leading wrapper (sudo, env VAR=x, command, nohup, time, doas).
function bare(w: string[]): string[] {
  let i = 0
  while (i < w.length && (/^(sudo|doas|command|nohup|time|env|npx|bunx|pnpx)$/i.test(w[i]) || /^[A-Za-z_][A-Za-z0-9_]*=/.test(w[i]))) i++
  return w.slice(i)
}
// A shell command that writes files counts as an edit: sed -i, tee, a redirect to a file, Set-Content, git apply, patch.
function writesFiles(command: string): boolean {
  const unquoted = command.replace(/"[^"]*"|'[^']*'/g, '""')
  return /\bsed\s+(-[a-zA-Z]*i|--in-place)|\btee\b|\b(Set-Content|Add-Content|Out-File)\b|\bgit\s+apply\b|\bpatch\s/i.test(unquoted) ||
    /(^|[^0-9&>])>>?\s*(?!&|\/dev\/null|\$null\b|nul\b)[^\s|;&]/i.test(unquoted)
}
async function destructivePreview($: any, root: string, command: string, cwd: string): Promise<string[]> {
  const out: string[] = []
  const lines = async (argv: string[], max = 15) =>
    String((await run($, argv, cwd, 30000)).stdout).trim().split(/\r?\n/).filter(Boolean).slice(0, max)
  // Relative paths start from where the shell is; a `cd` earlier in the same command moves it.
  let base = cwd.replace(/\\/g, '/').replace(/\/$/, '')
  const at = (p: string) => (/^([A-Za-z]:)?[\\/]/.test(p) || !base ? p : `${base}/${p}`)
  for (const seg of segments(command)) {
    const w = bare(words(seg.trim()))
    if (!w.length) continue
    const cmd = w[0].toLowerCase()
    const args = w.slice(1).filter(a => !a.startsWith('-'))
    const script = ['bash', 'sh', 'zsh', 'pwsh', 'powershell'].includes(cmd) ? w[w.findIndex(x => /^-(c|command)$/i.test(x)) + 1] : cmd === 'cmd' ? w[w.findIndex(x => /^\/c$/i.test(x)) + 1] : undefined
    if (script && w.some(x => /^(-c|-command|\/c)$/i.test(x))) {
      // A script handed to another shell: preview what it would run.
      out.push(...(await destructivePreview($, root, script, base)))
    } else if (cmd === 'find' && (w.includes('-delete') || w.some((x, i) => /^-(exec|execdir|ok)$/.test(x) && /^(rm|rmdir|del|remove-item|unlink|shred)$/i.test(w[i + 1] ?? '')))) {
      // List what it would delete: the same search with its action replaced by -print.
      const action = w.findIndex(x => /^-(delete|exec|execdir|ok)$/.test(x))
      const r = await run($, ['find', ...w.slice(1, action), '-print'], base, 30000)
      const hit = r.exitCode === 0 ? String(r.stdout).trim().split(/\r?\n/).filter(Boolean) : []
      out.push(...(hit.length ? [`find 會刪 ${hit.length} 項：`, ...hit.slice(0, 15).map(h => `  ${relTo(root, at(h).replace(/\/\.\//g, '/'))}`)] : ['find 會刪除符合條件的檔案，但列不出清單：先把刪除動作換成 -print 跑一次']))
    } else if (cmd === 'xargs' && /^(rm|rmdir|del|remove-item)$/i.test(w.find((x, i) => i > 0 && !x.startsWith('-')) ?? '')) {
      out.push(`xargs ${w.slice(1).join(' ')}：要刪什麼由前一個指令的輸出決定，無法事先列出；先單獨跑前一段看清單`)
    } else if ((cmd === 'cd' || cmd === 'set-location') && args[0]) {
      base = at(args[0]).replace(/\\/g, '/').replace(/\/$/, '')
    } else if (['rm', 'rmdir', 'rd', 'del', 'remove-item', 'ri', 'erase', 'rimraf'].includes(cmd)) {
      for (const a of args.filter(x => !/^\/[a-z]$/i.test(x))) out.push(`刪除 ${await describePath($, root, at(a))}`)
    } else if (['mv', 'move-item', 'move'].includes(cmd) && args.length >= 2) {
      const dest = args[args.length - 1]
      for (const a of args.slice(0, -1)) out.push(`搬移 ${await describePath($, root, at(a))} → ${await describePath($, root, at(dest))}`)
    } else if (cmd === 'git') {
      const sub = w[1]
      const rest = w.slice(2)
      if (sub === 'rm' && !rest.includes('--cached')) {
        for (const a of rest.filter(x => !x.startsWith('-'))) out.push(`git rm 刪除 ${await describePath($, root, at(a))}`)
      } else if (sub === 'clean') {
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
  const mark = { error: '✖', warn: '⚠', redo: '↻', note: '·' } as const
  return [head, ...findings.map(f => `${mark[f.severity]} ${f.id}：${f.text}`)].join('\n')
}
// ---- drawing: a card for each held or refused call, and a band above the prompt ----
// A card: an optional bold title (what happened), a meta line (which lint moment, the counts),
// the findings, and an optional footer (what to do next). `replace` draws it in place of the error text.
// The cards are kept in $.state (S.cards), so a reload of the mod still draws them.
type Drawn = LintCard
function keepCard(id: string, d: Drawn) {
  S.cards[id] = d
  const ids = Object.keys(S.cards)
  for (const old of ids.slice(0, Math.max(0, ids.length - 100))) delete S.cards[old]
}

// Colors from the design canvas "Lint 卡片樣式": tint, border, strong text, meta text, body text, icon.
const PALETTE = {
  error: { bg: '#FDF3F3', border: '#F2CFCF', strong: '#8E1B1B', meta: '#A35A5A', body: '#3B2020', icon: '#D63B3B', chip: '#F0C6C6' },
  hold: { bg: '#FDF7EA', border: '#EFD9A6', strong: '#7A4A06', meta: '#9C6E2A', body: '#3A2A0E', icon: '#E39A1C', chip: '#F0DDB0' },
  warn: { bg: '#FFFBF2', border: '#F3E3BD', strong: '#7A4A06', meta: '#9C6E2A', body: '#3A2A0E', icon: '#C98A16', chip: '#F0DDB0' },
  redo: { bg: '#EFF5FD', border: '#C8DAF2', strong: '#1C4E8E', meta: '#4E70A3', body: '#1D2A3C', icon: '#2F6FD0', chip: '#C8DAF2' },
} as const
const SHIELD = 'M14 3.5 L22.5 6.8 V13 C22.5 18.4 18.9 22.3 14 24.5 C9.1 22.3 5.5 18.4 5.5 13 V6.8 Z'
function iconSvg(kind: Drawn['kind']): string {
  const c = PALETTE[kind].icon
  const svg = (body: string) => `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28" overflow="visible">${body}</svg>`
  if (kind === 'error')
    return svg(`<circle cx="14" cy="14" r="10" fill="none" stroke="${c}" stroke-width="1.6"><animate attributeName="r" values="9;14;14" keyTimes="0;0.7;1" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0;0" keyTimes="0;0.7;1" dur="1.6s" repeatCount="indefinite"/></circle><path d="${SHIELD}" fill="${c}"/><rect x="12.8" y="8.6" width="2.4" height="7" rx="1.2" fill="#fff"/><circle cx="14" cy="18.8" r="1.5" fill="#fff"/>`)
  if (kind === 'hold')
    return svg(`<path d="${SHIELD}" fill="${c}"/><g><animate attributeName="opacity" values="1;0.45;1" dur="1.8s" repeatCount="indefinite"/><rect x="10.6" y="9.4" width="2.4" height="8.4" rx="1" fill="#fff"/><rect x="15" y="9.4" width="2.4" height="8.4" rx="1" fill="#fff"/></g>`)
  if (kind === 'redo')
    return svg(`<g><animateTransform attributeName="transform" type="rotate" from="0 14 14" to="360 14 14" dur="6s" repeatCount="indefinite"/><path d="M21.5 11.5 A8 8 0 1 0 22 16.5" fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round"/><path d="M22.8 6.8 L22.2 12.2 L16.9 11.2" fill="none" stroke="${c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g>`)
  return svg(`<path d="M14 4.5 L24 22 H4 Z" fill="none" stroke="${c}" stroke-width="1.8" stroke-linejoin="round"/><rect x="13.1" y="11" width="1.8" height="6" rx="0.9" fill="${c}"/><circle cx="14" cy="19.4" r="1.1" fill="${c}"/>`)
}
function card($: any, e: any, d: Drawn): any {
  const els = $.ui.resolve(e) as any
  const { Box, Text } = els
  const terminal = e.surface === 'terminal'
  const p = PALETTE[d.kind]
  // The terminal keeps theme colors so the card reads in any terminal palette.
  const strong = terminal ? (d.kind === 'error' ? 'error' : d.kind === 'redo' ? 'suggestion' : 'warning') : p.strong
  const meta = terminal ? 'subtle' : p.meta
  const body = terminal ? 'text' : p.body
  const icon = !terminal && els.Svg
    ? h(els.Svg, { source: iconSvg(d.kind), alt: d.title ?? d.meta, width: 28, height: 28, isInteractive: true })
    : h(Text, { color: strong, bold: true }, { hold: '⏸', error: '✖', warn: '⚠', redo: '↻' }[d.kind])
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
  const warns = shown.filter(f => f.severity === 'warn').length
  const redos = shown.filter(f => f.severity === 'redo').length
  const counts = [errors ? `${errors} error` : '', warns ? `${warns} warn` : '', redos ? `${redos} 重新` : ''].filter(Boolean).join('、')
  return { kind: errors ? 'error' : warns ? 'warn' : 'redo', meta: `lint · ${moment} · ${counts}`, lines: shown }
}

async function notify($: any, text: string) {
  try {
    await $.session.append({ message: { type: 'system', content: [{ type: 'text', text }] } })
  } catch {}
}

// The model's text as it streams, in order: it arrives before a tool call of the same message does,
// while the message's row is kept only later. So "spoke this turn" and the text after the last step
// are read here, not from session.append. Each main-loop response is one step.
// A plugin hooks turn.step once: main.ts registers it and chains this with the status line's.
export async function* lintTurnStep($: any, e: any, next: any): any {
  await restore($)
  const who = e.agentId ?? 'main'
  S.steps[who] = (S.steps[who] ?? 0) + 1
  persist($)
  const it = next(e)[Symbol.asyncIterator]()
  for (;;) {
    const { value, done } = await it.next()
    if (done) return value
    if (!e.agentId && value?.kind === 'text') {
      const t = String(value.text ?? '')
      S.textAfterTools += t
      if (t.trim() && !S.spoke) {
        S.spoke = true
        persist($)
      }
    }
    yield value
  }
}

export const register: Register = on => {
  // Session start: worktrees left behind, and the repo's git facts for the model.
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await restore($)
    const root = await projectRoot($)
    if (!(await hasLint($, root))) return result
    const { checks } = await loadChecks($, root!)
    const wt = checks.find(c => c.builtin === 'worktree-cleanup')
    if (wt) {
      const f = await worktreeCleanup($, root!, wt)
      if (f.length) await notify($, `lint · session 開始 · 沒清掉的 worktree\n${f.map(x => `⚠ ${x.text}`).join('\n')}`)
    }
    if (checks.some(c => c.builtin === 'git-facts')) S.gitFacts = (await gitFacts($, root!)).text
    const lang = checks.find(c => c.builtin === 'user-language')
    if (lang?.language) S.userLanguage = lang.language
    persist($)
    return result
  })

  // The model reads the repo's git facts and the user's language in the system prompt.
  on('prompt.compose', async ($, e, next) => {
    const result = await next(e)
    await restore($)
    const add: { id: string; text: string; scope: 'session' }[] = []
    if (S.gitFacts) add.push({ id: 'baransu:lint-git', text: `這個 repo 的 git 習慣（baransu lint）。commit、push、開分支前照這些：\n${S.gitFacts}`, scope: 'session' })
    if (S.userLanguage) add.push({ id: 'baransu:lint-language', text: `使用者的慣用語言：${S.userLanguage}。寫給使用者看的文字一律用這個語言。`, scope: 'session' })
    return add.length ? { ...result, sections: [...result.sections, ...add] } : result
  })

  // What the user types — a slash command's arguments included: their language, the redos owed, a correction.
  on('prompt.submit', async ($, e, next) => {
    if (e.isMeta || !e.text.trim()) return next(e)
    await restore($)
    // Plain text, or a message typed into a running turn, reaches the model: it takes what is owed.
    // A slash command may open no model turn (/cost, /model): it carries a copy, and what it carried
    // is taken only when its turn starts (turn.start), so a command that opens none leaves it owed.
    const takes = !e.command || !!e.turnId
    // Take what is owed at once, before any await, and save that at once: nothing else can deliver it too,
    // and a reload in between cannot hand it out a second time.
    const slips = takes ? S.slips.splice(0) : [...S.slips]
    const owedReport = S.pendingReport
    if (takes) {
      S.pendingReport = undefined
      S.offered = undefined
    } else S.offered = { slips, report: owedReport }
    persist($)
    let returned = false
    const putBack = () => {
      if (returned) return
      returned = true
      if (takes) {
        S.slips.unshift(...slips)
        if (owedReport && !S.pendingReport) S.pendingReport = owedReport
      } else S.offered = undefined
      persist($)
    }
    try {
    const root = await projectRoot($)
    if (!(await hasLint($, root))) {
      putBack()
      return next(e)
    }
    const { checks } = await loadChecks($, root!)
    const typed = e.text
      .replace(/<([a-z][\w-]*)\b[^>]*>[\s\S]*?<\/\1>/gi, ' ')
      .replace(/<[a-z][\w-]*\b[^>]*\/>/gi, ' ')
      .replace(/^\s*\/\S+/, ' ')
    const lang = checks.find(c => c.builtin === 'user-language')
    if (lang && !lang.language) {
      const han = (typed.match(/\p{Script=Han}/gu) ?? []).length
      const letters = (typed.match(/\p{L}/gu) ?? []).length
      if (letters) S.userLanguage = han / letters > 0.2 ? '中文（照使用者用的字，繁體或簡體）' : 'English'
    }
    const notes: string[] = []
    if (lang) notes.push(...slips.map(t => restateNote(lang, t)))
    if (owedReport) {
      const rc = checks.find(c => c.id === owedReport)
      const how = rc?.redo ?? `先照 ${$.plugin.root}/skills/what-now/SKILL.md 的寫法（那個 skill 只有使用者能叫，讀它照做）重新交代：第一句說有什麼等使用者決定或沒有；做了什麼、做到哪、哪些沒驗證；每個等他決定的事附上建議、依據和風險。`
      notes.push(`baransu lint（${owedReport}，重新）：上一輪做了事，結束前卻沒交代現況。回應這則訊息之前，${how}`)
    }
    const fix = checks.find(c => c.builtin === 'correction-to-lint')
    if (fix && CORRECTION.test(typed)) {
      await notify($, `lint · ${fix.id}：這像是在糾正，修完後會評估能不能寫成 lint`)
      notes.push(`baransu lint（${fix.id}）：使用者在糾正你。先照他說的修好，再判斷這個錯能不能寫成檢查：能，就交給 /baransu:lint 新增（附上這次錯在哪、怎麼修、出錯的 commit）；不能，用一句話說明為什麼。${fix.message}`)
    }
    persist($)
    const r: any = await (notes.length ? next({ ...e, context: [...(e.context ?? []), ...notes] }) : next(e))
    // The prompt did not enter (a hook or a settings hook below refused it): what it took is still owed.
    if (r && 'drop' in r && r.drop) putBack()
    return r
    } catch (err) {
      // Whatever failed after the take, what was taken goes back to be delivered next time.
      putBack()
      throw err
    }
  }).catch(($, e, next) => next(e))

  // At the end of a turn: a reply in the wrong language, or work done with no account of where it stands,
  // is shown to the person now; the model is told to redo it at the start of the next turn.
  on('turn.complete', async ($, e: any, next) => {
    const result = await next(e)
    if (e.agentId) return result
    await restore($)
    // A /review counts only once the turn that ran it ends with an answer, not when it was stopped.
    if (S.reviewPending !== undefined) {
      if (e.reason === 'answer') S.reviewedAt = S.reviewPending
      S.reviewPending = undefined
    }
    if (S.slips.length) await notify($, `lint · user-language：剛才那段寫成英文了（「${slipHead(S.slips[S.slips.length - 1])}」）→ 重新：下一步用你的語言再說一次`)
    const root = await projectRoot($)
    if (await hasLint($, root)) {
      const { checks } = await loadChecks($, root!)
      const c = checks.find(x => x.builtin === 'report-before-stop')
      // A report counts its whole text, tables and code included; a Han character counts as two letters.
      const letters = (S.textAfterTools.match(/\p{L}/gu) ?? []).length
      const han = (S.textAfterTools.match(/\p{Script=Han}/gu) ?? []).length
      const reported = letters - han + 2 * han >= 60
      if (reported) S.pendingReport = undefined
      else if (c && S.tools > 0) {
        S.pendingReport = c.id
        await notify($, `lint · ${c.id}：這一輪做了事，結束前卻沒交代現況 → 重新：下一步照 what-now 交代`)
      }
    }
    persist($)
    return result
  })

  // A new main-loop turn: nothing said, nothing done; delete approvals from the last turn end (they last one turn).
  on('turn.start', async ($, e, next) => {
    if (!e.agentId) {
      await restore($)
      S.spoke = false
      S.tools = 0
      S.textAfterTools = ''
      S.previewed = []
      // A slash command's message carried a copy of what was owed; it opened this turn, so that is delivered.
      if (S.offered && e.text) {
        for (const t of S.offered.slips) {
          const i = S.slips.indexOf(t)
          if (i >= 0) S.slips.splice(i, 1)
        }
        if (S.offered.report && S.pendingReport === S.offered.report) S.pendingReport = undefined
        S.offered = undefined
      }
      persist($)
    }
    return next(e)
  })
  // /clear goes on under a new session with no session.start: what was owed belongs to the old one.
  on('session.end', async ($, e: any, next) => {
    if (e.reason === 'clear') {
      await restore($)
      S = { ...freshState(), userLanguage: S.userLanguage, gitFacts: S.gitFacts }
      persist($)
    }
    return next(e)
  })
  // turn.step is registered once for the plugin in main.ts, which calls lintTurnStep.
  on('session.append', async ($, e, next) => {
    if (!e.agentId && e.message.type === 'assistant') {
      await restore($)
      const text = (e.message.content as any[]).filter(b => b.type === 'text').map(b => String(b.text)).join('\n')
      if (text.trim()) S.spoke = true
      // The user writes Chinese and this block is English prose: owe a restate of this block.
      const { han, letters } = hanShare(text)
      if (wantsChinese() && letters >= 40 && han / letters < 0.1) S.slips.push(text.trim().slice(0, 800))
      persist($)
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  on('tool.call', async ($, e: any, next) => {
    const tool: string = e.tool
    const isEdit = EDIT_TOOLS.has(tool)
    const isBash = SHELL_TOOLS.has(tool)
    if (!isEdit && !isBash) return next(e)
    await restore($)
    const main = !e.agentId
    // Take what is owed at once, before any await, and save that: two calls in flight never both deliver it,
    // and a reload while the tool runs cannot hand it out again.
    const slips = main ? S.slips.splice(0) : []
    const owedReport = main ? S.pendingReport : undefined
    if (main) S.pendingReport = undefined
    const seqAtStart = S.editSeq
    const stepAtStart = S.steps[e.agentId ?? 'main'] ?? 0
    persist($)
    let returned = false
    const putBack = () => {
      if (returned) return
      returned = true
      S.slips.unshift(...slips)
      if (owedReport && !S.pendingReport) S.pendingReport = owedReport
      persist($)
    }
    const shell = tool === 'PowerShell' ? 'ps' : 'sh'
    try {
    const root = await projectRoot($)
    if (!(await hasLint($, root))) {
      putBack()
      // Nothing is checked without .claude/lint/, but edits still count for a /lint set up later this session.
      const r: any = await next(e)
      if (r && !r.deny && !r.isError && (isEdit || (isBash && writesFiles(String(e.command ?? ''))))) {
        S.editSeq++
        persist($)
      }
      return r
    }
    const { checks } = await loadChecks($, root!)
    // Where this call's shell is: the session's own directory, read inside the hook (a subagent's own).
    // A foreground `cd` moves it; a subshell or a backgrounded command does not.
    let cwdNow = root!
    try {
      cwdNow = String(await $.session.cwd()).replace(/\\/g, '/').replace(/\/$/, '') || root!
    } catch {}
    const command: string = isBash ? String(e.command ?? '') : ''
    const context: string[] = []
    // Everything lint says about this call is drawn as one card under it.
    const inline: Finding[] = []
    // A refused call still hands the model what it is owed: the notes ride on the refusal.
    const refuse = (d: Drawn, deny: string) => {
      keepCard(e.tool_use_id, { ...d, replace: true })
      persist($)
      return { deny: [deny, ...context].join('\n\n') }
    }

    // Blocks written in the wrong language since the last call: redo each in the user's language.
    const lang = checks.find(x => x.builtin === 'user-language')
    if (lang)
      for (const t of slips) {
        inline.push({ id: lang.id, severity: 'redo', text: `剛才那段寫成英文了（「${slipHead(t)}」）→ 重新：用你的語言再說一次` })
        context.push(restateNote(lang, t))
      }

    // A report owed from the last turn that the user's next message did not carry (it was typed while that turn ran).
    if (owedReport) {
      const rc = checks.find(c => c.id === owedReport)
      const how = rc?.redo ?? `先照 ${$.plugin.root}/skills/what-now/SKILL.md 的寫法（那個 skill 只有使用者能叫，讀它照做）重新交代上一輪的現況：有什麼等使用者決定、做了什麼、做到哪、哪些沒驗證。`
      inline.push({ id: owedReport, severity: 'redo', text: '上一輪做了事卻沒交代現況 → 重新：照 what-now 交代' })
      context.push(`baransu lint（${owedReport}，重新）：上一輪做了事，結束前卻沒交代現況。${how}`)
    }

    // Explain before acting: the first edit or command of a turn should follow words to the user.
    if (main && !S.spoke) {
      const c = checks.find(x => x.builtin === 'explain-before-edit')
      S.spoke = true
      if (c) {
        const what = `這一輪還沒跟使用者說明，就先${isEdit ? '改檔' : '跑指令'}了`
        const how = c.redo ?? `照 ${$.plugin.root}/skills/show-me/SKILL.md 的寫法（那個 skill 只有使用者能叫，讀它照做），用最小的一張圖或幾行文字跟使用者說明這一步要做什麼、會動到什麼、為什麼，再繼續`
        if (c.severity === 'error') return refuse({ kind: 'error', title: '沒有執行', meta: `lint · ${c.id}`, lines: [{ id: c.id, severity: 'error', text: what }], footer: '先說明要做什麼，再下一次' }, `baransu lint（${c.id}）：${what}。${how}。`)
        inline.push({ id: c.id, severity: 'redo', text: `${what} → 重新：先說明要做什麼` })
        context.push(`baransu lint（${c.id}，重新）：${what}。${how}。`)
      }
    }

    // Before any shell command: checks that read the command line itself.
    if (isBash) {
      const findings = commandFindings(checks, command)
      if (findings.some(f => f.severity === 'error')) {
        return refuse({ ...summarize('指令前', findings)!, title: '沒有執行', footer: '照上面改寫這個指令再跑' }, `${render('bash', '', findings)}\n照上面改寫這個指令再跑。`)
      }
      if (findings.length) {
        inline.push(...findings)
        context.push(render('bash', '', findings))
      }

      // Before a command that deletes, moves or discards: show what it will touch, once per actor, directory and turn.
      // The same command passes only in a later response than the one held, after the model has read the list.
      const preview = checks.find(c => c.builtin === 'destructive-preview')
      const key = `${e.agentId ?? 'main'}|${shell}|${cwdNow}|${command}`
      const seen = S.previewed.find(p => p.key === key)
      if (preview && !(seen && seen.step < stepAtStart)) {
        const touched = await destructivePreview($, root!, command, cwdNow)
        if (touched.length) {
          if (!seen) S.previewed.push({ key, step: stepAtStart })
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
    const ran = result && !result.deny
    // A call refused further down, or a run that failed, carries no notes: what was taken goes back.
    if (!ran || result.isError) putBack()
    // Work done this turn, and the text after it starts over; a read-only call (git status, ls) does neither.
    if (main && ran && !result.isReadOnly) {
      S.tools++
      S.textAfterTools = ''
    }
    if (isBash && ran) {
      // A shell command that writes files is an edit, not a check run after one. A background command
      // has only started, so it is not a run; a command counts against the edit count it started at.
      if (writesFiles(command)) S.editSeq++
      else if (!e.run_in_background) S.commands.push({ cmd: command, ok: result.isError !== true, seq: seqAtStart })
    }

    // After a successful edit.
    const file = isEdit ? relTo(root!, String(e.file_path ?? e.notebook_path ?? '')) : ''
    const insideRepo = file !== '' && !/^([A-Za-z]:)?\//.test(file)
    if (isEdit && ran && !result.isError) S.editSeq++
    if (isEdit && insideRepo && ran && !result.isError) {
      if (file.startsWith(`${LINT}/`)) checksCache = undefined
      const findings = (await runMoment($, root!, 'edit', { file })).filter(f => f.severity !== 'note')
      if (findings.length) {
        inline.push(...findings)
        context.push(`${render('edit', file, findings)}\n修好 error；warn 判斷要不要改。`)
      }
    }

    persist($)
    if (inline.length && ran) {
      const d = summarize(isEdit ? `改檔後 · ${file}` : GIT_WRITE.test(command) ? 'commit 前' : '指令前', inline)
      keepCard(e.tool_use_id, d ?? { kind: 'warn', meta: 'lint', lines: inline })
      persist($)
    }
    if (context.length && ran && !result.isError) return { ...result, context: [...(result.context ?? []), ...context] }
    return result
    } catch (err) {
      // Whatever failed after the take, what was taken goes back to be delivered next time.
      putBack()
      throw err
    }
  }).catch(($, e, next) => next(e))

  // Lint's card under the call it is about: in place of the error text for a held or refused call,
  // below the tool's own result otherwise.
  on('ui.render', { component: 'ToolResult' }, async ($, e: any, next) => {
    await restore($)
    const d = S.cards[e.props?.tool_use_id]
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
    await restore($)
    if (isReview) {
      // Counted when the review's turn ends with an answer (turn.complete), not when it starts.
      S.reviewPending = S.editSeq
      persist($)
    }
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
