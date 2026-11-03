// Running checks at a moment. Every outside look goes through the Runner port; the state is read, never
// written, here (only engine.ts writes). Bodies came from 8.39's lint.ts (git show 58de798a:plugins/baransu/hooks/lint.ts) with `$` replaced by (runner, h).

import { inScope, pathspecs, relTo } from './check'
import type { Runner } from './ports'
import { isGitWrite } from './shell'
import type { Check, Config, Finding, LintState } from './types'

/**
 * What a moment looks at. `config.root` is always the lint root: the base every setting and glob is written
 * against, and where file checks (forbid, run, ast-grep) run. `repo` is set only for a commit when the lint
 * root is not a repo's top (commitLook): the repo it commits in — `top`, absolute; `rel`, its path from the
 * lint root ('' when the lint root lies inside it); `inner`, the lint root's path inside it in that case.
 * Then the git built-ins and "what the change touches" are asked of that repo, and forbid and ast-grep report
 * only its files.
 */
type Look<H> = {
  readonly runner: Runner<H>
  readonly h: H
  readonly config: Config
  readonly repo?: { readonly top: string; readonly rel: string; readonly inner?: string }
}
type Sev = 'error' | 'warn'

function run<H>(look: Look<H>, argv: readonly string[], timeoutMs = 120000) {
  return look.runner.run(look.h, argv, { cwd: look.config.root, timeoutMs })
}
/** A git command about the repo itself (identity, staged files, upstream, status): in the commit's repo when
 *  there is one, else at the lint root. */
function runGit<H>(look: Look<H>, argv: readonly string[], timeoutMs = 120000) {
  return look.runner.run(look.h, argv, { cwd: look.repo?.top ?? look.config.root, timeoutMs })
}
/** In a commit's repo, keep only findings on that repo's files (a root-relative path under `rel/`; every
 *  path when the lint root lies inside the repo). Case-insensitive: Windows paths. */
function inRepo<H>(look: Look<H>, path: string): boolean {
  return !look.repo || !look.repo.rel || path.toLowerCase().startsWith(`${look.repo.rel.toLowerCase()}/`)
}
/** Which files a search covers: a repo's tracked and untracked files; in a plain folder (not a repo) the
 *  folder's files, each repo's own .gitignore applied (`--no-index --exclude-standard`), so a dependency
 *  folder a repo ignores is not searched. */
function searchScope<H>(look: Look<H>): string[] {
  return look.config.git ? ['--untracked'] : ['--no-index', '--exclude-standard']
}

/**
 * The look a commit-time moment uses. In an ordinary project (the lint root is a repo's top) the look as it
 * is — 8.39's behaviour. Otherwise the commit's repo (`dir` is where the command commits, from commitDirs):
 * - a repo inside the lint root (a workspace's sub-repo, `cd src/app && git commit`): `repo` with `rel` its
 *   path from the lint root; the git built-ins read it and file checks keep only its files;
 * - the lint root inside a repo (`.claude/lint` in a repo's subfolder): `repo` with `rel` '' and `inner` the
 *   lint root's path in it; the git built-ins read the repo, the change is what falls under the lint root;
 * - no repo at `dir`: `skip: 'none'`; a repo apart from the lint root: `skip: 'outside'` — the caller warns.
 * Settings, globs and sgconfig always stay on the lint root.
 */
export async function commitLook<H>(look: Look<H>, dir: string): Promise<{ look: Look<H>; skip?: 'none' | 'outside' }> {
  if (look.config.git) return { look }
  const r = await look.runner.run(look.h, ['git', 'rev-parse', '--show-toplevel'], { cwd: dir, timeoutMs: 10000 })
  const top = r.exitCode === 0 ? String(r.stdout).trim().replace(/\\/g, '/') : ''
  if (!top) return { look, skip: 'none' }
  const root = look.config.root
  const rel = relTo(root, top)
  if (rel !== top) return { look: { ...look, repo: { top, rel } } }
  const inner = relTo(top, root)
  if (inner !== root) return { look: { ...look, repo: { top, rel: '', inner } } }
  return { look, skip: 'outside' }
}

function tail(s: string, n = 8): string {
  return s.trim().split(/\r?\n/).slice(-n).join('\n')
}

async function forbidCheck<H>(look: Look<H>, c: Check, pattern: string, file?: string): Promise<Finding[]> {
  const specs = file ? [file] : pathspecs(c)
  // -z: the name as it is (not quoted for 中文 letters) and NUL after the name and the line number.
  const r = await run(look, ['git', 'grep', '-nIPz', ...searchScope(look), '-e', pattern, '--', ...specs])
  if (r.exitCode === 1) return []
  if (r.exitCode !== 0) return [{ id: c.id, severity: 'warn', text: `沒有執行成功：${tail(r.stderr, 3)}` }]
  const parsed = r.stdout.trim().split(/\r?\n/).map((hit: string) => {
    const [path, line] = hit.includes('\0') ? hit.split('\0') : hit.split(':')
    return { path, line }
  })
  return parsed
    .filter(h => inRepo(look, h.path))
    .slice(0, 10)
    .map(h => ({ id: c.id, severity: c.severity, text: `${h.path}:${h.line} ${c.message}` }))
}
async function runCheck<H>(look: Look<H>, c: Check, argv0: readonly string[], file?: string): Promise<Finding[]> {
  const argv = argv0.map(a => (file ? a.split('{file}').join(file) : a))
  const r = await run(look, argv)
  if (r.exitCode === 0) return []
  if (r.exitCode === -1) return [{ id: c.id, severity: 'warn', text: `${r.stderr}（沒有檢查到）` }]
  return [{ id: c.id, severity: c.severity, text: `${c.message}\n${tail(r.stdout + '\n' + r.stderr)}` }]
}
/** At manual: a `run` holding {file}, once per text file in its scope over the whole tree (the same files a
 *  forbid would search), at most MAX_FILES; past that, one note says how many were left out. */
const MAX_FILES = 200
async function runPerFile<H>(look: Look<H>, c: Check, argv: readonly string[]): Promise<Finding[]> {
  // -z: names as they are, NUL-separated (without it git quotes a name with non-ASCII letters, 中文.json).
  const listed = await run(look, ['git', 'grep', '-lIz', ...searchScope(look), '-e', '', '--', ...pathspecs(c)])
  if (listed.exitCode !== 0 && listed.exitCode !== 1) return [{ id: c.id, severity: 'warn', text: `沒有執行成功：${tail(listed.stderr, 3)}` }]
  const files = String(listed.stdout).split(/\0|\r?\n/).filter(Boolean)
  const out: Finding[] = []
  for (const f of files.slice(0, MAX_FILES)) out.push(...(await runCheck(look, c, argv, f)))
  if (files.length > MAX_FILES) out.push({ id: c.id, severity: 'note', text: `範圍內有 ${files.length} 個檔，只檢查了前 ${MAX_FILES} 個` })
  return out
}

async function astGrep<H>(look: Look<H>, file?: string): Promise<Finding[]> {
  const cfg = look.config.sgconfig
  if (!cfg) return []
  if ((await look.runner.probe(look.h, `${look.config.root}/${cfg}`)).kind === 'missing') return []
  const r = await run(look, ['ast-grep', 'scan', '-c', cfg, '--json=compact', ...(file ? [file] : [])])
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
async function changedFiles<H>(look: Look<H>): Promise<string[]> {
  // A plain folder has no change set of its own: outside a commit nothing counts as touched, so `changed`
  // notes stay quiet and a `run` check with `files` waits for /lint's manual run. In a commit's repo, that
  // repo's changes, made relative to the lint root so the checks' globs read them.
  if (!look.config.git && !look.repo) return []
  const r = await runGit(look, ['git', 'status', '--porcelain', '--untracked-files=all'])
  return r.stdout
    .split(/\r?\n/)
    .filter(Boolean)
    .map((l: string) => l.slice(3).replace(/^"|"$/g, '').split(' -> ').pop()!)
    .flatMap((p: string) => {
      const repo = look.repo
      if (!repo) return [p]
      if (repo.rel) return [`${repo.rel}/${p}`]
      // The lint root inside the repo: only what falls under it, made relative to it.
      const inner = `${repo.inner ?? ''}/`
      return p.toLowerCase().startsWith(inner.toLowerCase()) ? [p.slice(inner.length)] : []
    })
}

/**
 * One moment's findings, config problems first, ast-grep last (as today).
 * edit:   checks with `edit` in `on` and the file in scope — forbid via `git grep` on the file, or `run` with {file}.
 * commit: built-ins git-facts / secret-files / built-before-commit / up-to-date, then forbid / run / changed.
 * done:   built-in session-record, then forbid / run / changed.
 * manual: what /lint runs when the person calls it — every check on files, over the whole tree: a forbid or
 *         run whose `on` names manual, edit, commit or done (a check `on = ["manual"]` runs here and nowhere
 *         else). A run runs whether or not the change touched its files; a run holding {file} runs once per file in its
 *         scope (runPerFile). Not here: built-ins (they belong to their moment), bash-only checks (they read a
 *         command line, not files).
 * A `run` holding {file} runs only at edit and manual; at commit/done a `run` with `files` runs only when the change touches them.
 */
export async function runMoment<H>(
  look: Look<H>, ledger: Readonly<LintState>, moment: 'edit' | 'commit' | 'done' | 'manual', opts: { file?: string; command?: string } = {},
): Promise<Finding[]> {
  const out: Finding[] = [...look.config.problems]
  const changed = moment === 'edit' ? [] : await changedFiles(look)
  for (const c of look.config.checks) {
    const a = c.action
    if (moment === 'manual') {
      if (a.kind === 'builtin' || !c.on.some(m => m !== 'bash')) continue
      if (a.kind === 'forbid') out.push(...(await forbidCheck(look, c, a.pattern)))
      else if (a.kind === 'run' && !a.argv.some(x => x.includes('{file}'))) out.push(...(await runCheck(look, c, a.argv)))
      else if (a.kind === 'run') out.push(...(await runPerFile(look, c, a.argv)))
      continue
    }
    if (a.kind === 'builtin') {
      // The commit-time git built-ins read the repo; a plain folder has none to read.
      const gitOnly = a.name === 'git-facts' || a.name === 'secret-files' || a.name === 'up-to-date'
      if (gitOnly && !look.config.git && !look.repo) continue
      if (moment === 'commit' && a.name === 'git-facts') out.push(...(await gitFactsAtCommit(look, c, opts.command ?? '')))
      if (moment === 'commit' && a.name === 'secret-files') out.push(...(await secretFiles(look, c)))
      if (moment === 'commit' && a.name === 'built-before-commit') out.push(...sessionRecord(ledger, c, false).filter(f => f.severity !== 'note'))
      if (moment === 'commit' && a.name === 'up-to-date') out.push(...(await upToDate(look, c)))
      if (moment === 'done' && a.name === 'session-record') out.push(...sessionRecord(ledger, c, true))
      continue
    }
    if (!c.on.includes(moment)) continue
    if (moment === 'edit') {
      if (!opts.file || !inScope(opts.file, c)) continue
      if (a.kind === 'forbid') out.push(...(await forbidCheck(look, c, a.pattern, opts.file)))
      else if (a.kind === 'run') out.push(...(await runCheck(look, c, a.argv, opts.file)))
      continue
    }
    const touched = c.files.length > 0 && changed.some(p => inScope(p, c))
    if (c.changed && touched) out.push({ id: c.id, severity: 'note', text: c.changed })
    if (a.kind === 'forbid') out.push(...(await forbidCheck(look, c, a.pattern)))
    else if (a.kind === 'run' && !a.argv.some(x => x.includes('{file}')) && (c.files.length === 0 || touched)) out.push(...(await runCheck(look, c, a.argv)))
  }
  out.push(...(await astGrep(look, moment === 'edit' ? opts.file : look.repo?.rel || undefined)))
  return out
}

/** `bash` checks: their `forbid` read as a JS regex against the command line (a `(?i)` prefix → flag i). Pure. */
export function commandFindings(checks: readonly Check[], command: string): Finding[] {
  const out: Finding[] = []
  for (const c of checks) {
    if (!c.on.includes('bash') || c.action.kind !== 'forbid') continue
    const src = c.action.pattern
    try {
      const re = src.startsWith('(?i)') ? new RegExp(src.slice(4), 'im') : new RegExp(src, 'm')
      if (re.test(command)) out.push({ id: c.id, severity: c.severity, text: c.message })
    } catch (err) {
      out.push({ id: c.id, severity: 'warn', text: `regex 讀不懂：${(err as Error).message}` })
    }
  }
  return out
}

/** The repo's git facts: text for the model plus what commit-time checks compare against. */
export async function gitFacts<H>(look: Look<H>): Promise<{ text: string; authors: string[]; commits: number; coAuthor: number; prHabit: boolean; defaultBranch: string }> {
  const out = async (argv: string[]): Promise<string> => String((await runGit(look, argv, 30000)).stdout).trim()
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

async function gitFactsAtCommit<H>(look: Look<H>, c: Check, command: string): Promise<Finding[]> {
  const f = await gitFacts(look)
  const out: Finding[] = []
  const sev: Sev = c.severity
  const known = (email: string) => f.authors.some(a => a.toLowerCase().includes(`<${email}>`))
  if (/\bcommit\b/.test(command)) {
    // `git -c user.email=X commit` commits as X whatever the config says.
    const override = /-c\s+["']?user\.email=["']?([^"'\s]+)/.exec(command)?.[1]
    const email = (override ?? String((await runGit(look, ['git', 'config', 'user.email'])).stdout)).trim().toLowerCase()
    if (f.commits >= 5 && email && !known(email))
      out.push({ id: c.id, severity: sev, text: `目前的 git 身分 <${email}> 不在這個 repo 的近期作者裡。${c.message}\n${f.text}` })
  } else if (/\bpush\b/.test(command)) {
    // A push makes no commit: what matters is who wrote the commits it sends.
    const sent = String((await runGit(look, ['git', 'log', '@{u}..HEAD', '--format=%ae'])).stdout).split(/\r?\n/).map(s => s.trim().toLowerCase()).filter(Boolean)
    const strangers = [...new Set(sent.filter(e => !known(e)))]
    if (f.commits >= 5 && strangers.length)
      out.push({ id: c.id, severity: sev, text: `要推上去的 commit 裡有不屬於這個 repo 近期作者的身分：${strangers.join('、')}。${c.message}` })
  }
  if (/\bcommit\b/.test(command) && /Co-Authored-By:/i.test(command) && f.coAuthor === 0 && f.commits >= 5)
    out.push({ id: c.id, severity: sev, text: `這個 repo 近 30 個 commit 都沒有 Co-Authored-By，這次卻加了。${c.message}` })
  const branch = (await runGit(look, ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])).stdout.trim()
  if (/\bpush\b/.test(command) && f.prHabit && branch === f.defaultBranch)
    out.push({ id: c.id, severity: sev, text: `這個 repo 習慣透過 PR/MR 合併，這次卻直接 push 到 ${f.defaultBranch}。${c.message}` })
  return out
}

async function secretFiles<H>(look: Look<H>, c: Check): Promise<Finding[]> {
  const staged = (await runGit(look, ['git', 'diff', '--cached', '--name-only'])).stdout.split(/\r?\n/).filter(Boolean)
  const bad = staged.filter((p: string) =>
    /(^|\/)(\.env(\..*)?|[^/]*\.pem|[^/]*\.key|id_rsa[^/]*|[^/]*\.p12|credentials[^/]*\.json)$/i.test(p),
  )
  return bad.map((p: string) => ({ id: c.id, severity: c.severity, text: `${p}：${c.message}` }))
}

/** At commit (needReview false) or done (true): commands run since the last edit, and whether a /review counted. Pure. */
export function sessionRecord(ledger: Readonly<LintState>, c: Check, needReview: boolean): Finding[] {
  const S = ledger
  const after = S.commands.filter(x => x.seq === S.editSeq && !isGitWrite(x.cmd))
  const lines = after.slice(-15).map(x => `  ${x.ok ? '✓' : '✗'} ${x.cmd.slice(0, 120)}`)
  const reviewed = S.editSeq === 0 ? '這個 session 沒有改檔' : S.reviewedAt >= S.editSeq ? '有' : '沒有'
  const text = [
    `最後一次改檔之後跑過的指令：${lines.length ? '\n' + lines.join('\n') : '（沒有）'}`,
    ...(needReview ? [`最後一次改檔之後有沒有跑 /review：${reviewed}`] : []),
  ].join('\n')
  const missing = S.editSeq > 0 && (lines.length === 0 || (needReview && S.reviewedAt < S.editSeq))
  return [{ id: c.id, severity: missing ? c.severity : 'note', text: missing ? `${text}\n${c.message}` : text }]
}

// Before a commit or push: has the remote moved on since this branch last caught up?
async function upToDate<H>(look: Look<H>, c: Check): Promise<Finding[]> {
  const fetched = await runGit(look, ['git', 'fetch', '--quiet'], 20000)
  if (fetched.exitCode !== 0) return [{ id: c.id, severity: 'warn', text: `git fetch 沒成功，無法確認是不是最新版：${tail(fetched.stderr, 2)}` }]
  const behind = await runGit(look, ['git', 'rev-list', '--count', 'HEAD..@{u}'], 10000)
  if (behind.exitCode !== 0) return []
  const n = Number(String(behind.stdout).trim())
  return n > 0 ? [{ id: c.id, severity: c.severity, text: `遠端有 ${n} 個本機還沒有的 commit。${c.message}` }] : []
}

/** Merged worktrees left behind, for the session-start notice. */
export async function worktreeCleanup<H>(look: Look<H>, c: Check): Promise<Finding[]> {
  const root = look.config.root
  const list = (await run(look, ['git', 'worktree', 'list', '--porcelain'])).stdout
  const merged = new Set(
    (await run(look, ['git', 'branch', '--merged', 'HEAD', '--format=%(refname:short)'])).stdout
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
        out.push({ id: c.id, severity: c.severity, text: `${path}（${b}）：${c.message}` })
    }
  }
  return out
}

