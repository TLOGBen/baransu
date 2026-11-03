// Running checks at a moment. Every outside look goes through the Runner port; the state is read, never
// written, here (only engine.ts writes). Bodies came from 8.39's lint.ts (git show 58de798a:plugins/baransu/hooks/lint.ts) with `$` replaced by (runner, h).

import { relTo } from './check'
import type { Language, Machine, Runner } from './ports'
import { admitted, keysOf, runsAt, subjectOf, targets, touches } from './scope/evaluate'
import { openLens, type Lens } from './scope/lens'
import { toRegExp } from './scope/parse'
import { relationsFor } from './scope/relations'
import type { Occurrence, Targets } from './scope/types'
import { MAX_TARGETS } from './scope/types'
import { isGitWrite, pushRefs } from './shell'
import type { Check, Config, Finding, LintState } from './types'

/**
 * What a moment looks at. `config.root` is always the lint root: the base every setting and glob is written
 * against, and where file checks (forbid, run, ast-grep) run. `repo` is set only for a commit when the lint
 * root is not a repo's top (commitLook): the repo it commits in — `top`, absolute; `rel`, its path from the
 * lint root ('' when the lint root lies inside it); `inner`, the lint root's path inside it in that case.
 * Then the git built-ins and "what the change touches" are asked of that repo, and forbid and ast-grep report
 * only its files.
 */
export type Look<H> = {
  readonly runner: Runner<H>
  readonly h: H
  readonly config: Config
  readonly repo?: { readonly top: string; readonly rel: string; readonly inner?: string }
  /** For a check's `when` guards (scope/lens.ts FACTS). */
  readonly machine: Machine<H>
  /** For `scope = "related"` (scope/relations.ts). */
  readonly languages: readonly Language[]
}
/** A check's level as a finding: info is a quiet note (card only); the others keep their name. Whether a
 *  `check` holds or reads as warn depends on the moment, which the engine decides, not this. */
export function level(c: Check): Pick<Finding, 'severity' | 'quiet'> {
  return c.severity === 'info' ? { severity: 'note', quiet: true } : { severity: c.severity }
}

function run<H>(look: Look<H>, argv: readonly string[], timeoutMs = 120000, env?: Readonly<Record<string, string>>) {
  return look.runner.run(look.h, argv, { cwd: look.config.root, timeoutMs, ...(env ? { env } : {}) })
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

const BATCH = 200 // paths per git command (Windows command-line length)

/** A forbid over the check's targets: git pathspecs for a whole-tree scope, an explicit list otherwise. */
async function forbidCheck<H>(look: Look<H>, c: Check, pattern: string, t: Targets): Promise<Finding[]> {
  if (t.kind === 'none') return []
  const batches = t.kind === 'tree' ? [t.specs] : chunk(t.paths, BATCH)
  const hits: { path: string; line: string }[] = []
  for (const specs of batches) {
    // -z: the name as it is (not quoted for 中文 letters) and NUL after the name and the line number.
    const r = await run(look, ['git', 'grep', '-nIPz', ...searchScope(look), '-e', pattern, '--', ...specs])
    if (r.exitCode === 1) continue
    if (r.exitCode !== 0) return [{ id: c.id, severity: 'warn', text: `沒有執行成功：${tail(r.stderr, 3)}` }]
    for (const hit of String(r.stdout).trim().split(/\r?\n/).filter(Boolean)) {
      const [path, line] = hit.includes('\0') ? hit.split('\0') : hit.split(':')
      hits.push({ path, line })
    }
  }
  return hits
    .filter(h => inRepo(look, h.path))
    .slice(0, 10)
    .map(h => ({ id: c.id, ...level(c), text: `${h.path}:${h.line} ${c.message}` }))
}
async function runCheck<H>(look: Look<H>, c: Check, argv0: readonly string[], file?: string, env?: Readonly<Record<string, string>>): Promise<Finding[]> {
  const argv = argv0.map(a => (file ? a.split('{file}').join(file) : a))
  const r = await run(look, argv, 120000, env)
  if (r.exitCode === 0) return []
  if (r.exitCode === -1) return [{ id: c.id, severity: 'warn', text: `${r.stderr}（沒有檢查到）` }]
  return [{ id: c.id, ...level(c), text: `${c.message}\n${tail(r.stdout + '\n' + r.stderr)}` }]
}
/** A `run` holding {file}, once per file the scope selects. A whole-tree scope is listed first (the files a
 *  forbid would search). MAX_TARGETS (scope/types.ts) is the only cap. A list the scope already cut is noted
 *  by runMoment; only a cut this listing makes is noted here, so a cut is said once. */
async function runPerFile<H>(look: Look<H>, c: Check, argv: readonly string[], t: Targets, env?: Readonly<Record<string, string>>): Promise<Finding[]> {
  if (t.kind === 'none') return []
  let files: readonly string[]
  let dropped = 0
  if (t.kind === 'paths') {
    files = t.paths
  } else {
    // -z: names as they are, NUL-separated (without it git quotes a name with non-ASCII letters, 中文.json).
    const listed = await run(look, ['git', 'grep', '-lIz', ...searchScope(look), '-e', '', '--', ...t.specs])
    if (listed.exitCode !== 0 && listed.exitCode !== 1) return [{ id: c.id, severity: 'warn', text: `沒有執行成功：${tail(listed.stderr, 3)}` }]
    const all = String(listed.stdout).split(/\0|\r?\n/).filter(Boolean)
    files = all.slice(0, MAX_TARGETS)
    dropped = Math.max(0, all.length - MAX_TARGETS)
  }
  const out: Finding[] = []
  for (const f of files) out.push(...(await runCheck(look, c, argv, f, env)))
  if (dropped) out.push({ id: c.id, severity: 'note', quiet: true, text: `範圍內還有 ${dropped} 個檔沒有檢查（上限 ${MAX_TARGETS}）` })
  return out
}
function chunk<T>(xs: readonly T[], n: number): T[][] {
  const out: T[][] = []
  for (let i = 0; i < xs.length; i += n) out.push(xs.slice(i, i + n))
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

/** The lens for one occurrence: the look's machine and languages behind it. */
export function lensFor<H>(look: Look<H>, at: Occurrence): Lens {
  return openLens(look, at, { machine: look.machine, relations: relationsFor<H>(look.languages) })
}

/** Whether an occurrence's checks read text (subjectOf) rather than files. Pure. */
export const readsText = (at: Occurrence): boolean => subjectOf({ base: { kind: 'all' }, where: { folders: [], files: [], trees: [], exts: [] }, ignores: [], actions: [], when: [] }, at) !== undefined

/** What a commit-time or a gate moment is: before a commit or push, or before /ship or /review. A gate checks
 *  what this change touched; every other file timing checks its targets whether or not they changed. */
const isGate = (at: Occurrence): boolean =>
  at.key === 'pre:commit' || at.key === 'pre:push' || (at.key === 'pre:skill' && /(^|:)(ship|review)$/.test(at.skill))

/**
 * One occurrence's findings: text checks (subjectFindings) for a timing that reads text, else the file checks,
 * config problems first, ast-grep last. `env` reaches every `run` (LINT_CHANGED, LINT_BEFORE on around).
 * Which checks: runsAt (scope/evaluate.ts) — `on`, the skill named, the actions; then the `when` guards
 * (admitted), a guard that fails saying so only on the person's card.
 * Which files: targets() — the whole tree as pathspecs, this change, or this change and its relatives, narrowed
 * by folder / file / ext and ignores; an act that names its files (an edit, post:file) checks those.
 * An act's own files (post:edit, post:file): forbid on them; `run` once, with {file} per path.
 * A gate (pre:commit / pre:push / pre:skill:ship / pre:skill:review): built-ins git-facts / secret-files /
 *         built-before-commit / up-to-date, session-record; then forbid over the targets; a `run` without {file}
 *         once (a `diff` / `related` scope only when the change touches it); a `run` with {file} per target path,
 *         only for a `diff` or `related` scope; `changed` notes.
 * manual, pre:skill, after:*: every check on files over its targets, a `run` whether or not the change touched them.
 * A check with no action and a message (not a `changed` note) says its message when it is due and its scope
 * selects something — never at manual.
 */
export async function runMoment<H>(look: Look<H>, ledger: Readonly<LintState>, at: Occurrence, env?: Readonly<Record<string, string>>): Promise<Finding[]> {
  if (readsText(at)) return subjectFindings(look, at, env)
  const out: Finding[] = [...look.config.problems]
  const lens = lensFor(look, at)
  const keys = keysOf(at)
  const command = 'command' in at ? at.command : ''
  const atCommit = keys.includes('pre:commit') || keys.includes('pre:push')
  const atDone = at.key === 'pre:skill' && isGate(at)
  const ownFiles = at.key === 'post:edit' || at.key === 'post:file'
  // A plain folder has no change of its own outside a commit, so its diff / related checks wait for one; said
  // once at /lint (lint-scope postcondition 6) so a quiet result does not read as a broken one.
  if (at.key === 'manual' && !look.config.git && !look.repo) {
    const waiting = look.config.checks.filter(c => c.action.kind !== 'builtin' && c.scope.base.kind !== 'all' && runsAt(c, at))
    if (waiting.length)
      out.push({ id: 'scope', severity: 'note', text: `這是一般資料夾，沒有「本次修改」：${waiting.map(c => c.id).join('、')} 的範圍是 diff／related，要等子 repo commit 時才跑` })
  }
  for (const c of look.config.checks) {
    const a = c.action
    if (a.kind === 'builtin') {
      // session-record also runs when a wait its `on` names runs out.
      const waited = at.key.startsWith('after:') && a.name === 'session-record' && c.on.some(t => t.key === at.key)
      if (!atCommit && !atDone && !waited) continue
      // The commit-time git built-ins read the repo; a plain folder has none to read.
      const gitOnly = a.name === 'git-facts' || a.name === 'secret-files' || a.name === 'up-to-date'
      if (gitOnly && !look.config.git && !look.repo) continue
      if (atCommit && a.name === 'git-facts') out.push(...(await gitFactsAtCommit(look, c, command)))
      if (keys.includes('pre:commit') && a.name === 'secret-files') out.push(...(await secretFiles(look, c)))
      if (atCommit && a.name === 'built-before-commit') out.push(...sessionRecord(ledger, c, false).filter(f => f.severity !== 'note'))
      if (atCommit && a.name === 'up-to-date') out.push(...(await upToDate(look, c)))
      if ((atDone || waited) && a.name === 'session-record') out.push(...sessionRecord(ledger, c, atDone).filter(f => atDone || f.severity !== 'note'))
      continue
    }
    if (!runsAt(c, at)) continue
    const gate = await admitted(c.scope, lens)
    if (gate.kind === 'skip') {
      if (gate.say) out.push({ id: c.id, severity: 'note', quiet: true, text: gate.say })
      continue
    }
    const perFile = a.kind === 'run' && a.argv.some(x => x.includes('{file}'))
    const narrowed = c.scope.base.kind !== 'all'
    const t = await targets(c.scope, lens)
    if (t.kind === 'paths' && t.dropped)
      out.push({ id: c.id, severity: 'note', quiet: true, text: `範圍內還有 ${t.dropped} 個檔沒有檢查（上限 ${MAX_TARGETS}）` })
    if (a.kind === 'none') {
      if (!c.changed && c.message && at.key !== 'manual' && t.kind !== 'none') out.push({ id: c.id, ...level(c), text: c.message })
      if (!c.changed || !isGate(at)) continue
    }
    if (ownFiles) {
      if (t.kind === 'none') continue
      if (a.kind === 'forbid') out.push(...(await forbidCheck(look, c, a.pattern, t)))
      else if (a.kind === 'run' && perFile) out.push(...(await runPerFile(look, c, a.argv, t, env)))
      else if (a.kind === 'run') out.push(...(await runCheck(look, c, a.argv, undefined, env)))
      continue
    }
    if (isGate(at)) {
      const touched = c.changed || narrowed ? await touches(c.scope, lens) : false
      if (c.changed && touched) out.push({ id: c.id, severity: 'note', text: c.changed })
      if (a.kind === 'forbid') out.push(...(await forbidCheck(look, c, a.pattern, t)))
      else if (a.kind === 'run' && perFile) {
        if (narrowed) out.push(...(await runPerFile(look, c, a.argv, t, env)))
      } else if (a.kind === 'run' && (!narrowed || t.kind !== 'none')) out.push(...(await runCheck(look, c, a.argv, undefined, env)))
      continue
    }
    // manual, pre:skill, after:*
    if (a.kind === 'forbid') out.push(...(await forbidCheck(look, c, a.pattern, t)))
    else if (a.kind === 'run' && perFile) out.push(...(await runPerFile(look, c, a.argv, t, env)))
    else if (a.kind === 'run') out.push(...(await runCheck(look, c, a.argv, undefined, env)))
  }
  // ast-grep rules belong to no check, so they run at the project's own moments: after an edit, at a gate, at
  // /lint — not before another skill, not when a wait runs out, not for a file changed outside Claude.
  if (at.key === 'post:edit') out.push(...(await astGrep(look, at.file)))
  else if (atCommit || atDone || at.key === 'manual') out.push(...(await astGrep(look, look.repo?.rel || undefined)))
  return out
}

/**
 * Checks on text — a command line, its output, what an edit writes or added, a stop's last words, a subagent's,
 * a compaction's, the answer to a 重新, the paths a delete removes. `forbid` is read as a JS regex against each
 * line of the subject (a `(?i)` prefix → flag i); a `run` runs once with the subject in LINT_TEXT (and `env`);
 * a check with no action says its message when its subject is not empty. Due checks only (runsAt); `when`
 * guards through the lens. An empty subject (a delete that reaches nothing in scope, an edit outside the
 * check's files) is silent.
 */
export async function subjectFindings<H>(look: Look<H>, at: Occurrence, env?: Readonly<Record<string, string>>): Promise<Finding[]> {
  const lens = lensFor(look, at)
  const out: Finding[] = []
  for (const c of look.config.checks) {
    if (c.action.kind === 'builtin' || !runsAt(c, at)) continue
    const subject = subjectOf(c.scope, at)
    if (!subject || !subject.lines.some(l => l !== '')) continue
    const gate = await admitted(c.scope, lens)
    if (gate.kind === 'skip') {
      if (gate.say) out.push({ id: c.id, severity: 'note', quiet: true, text: gate.say })
      continue
    }
    if (c.action.kind === 'none') {
      if (c.message) out.push({ id: c.id, ...level(c), text: c.message })
      continue
    }
    if (c.action.kind === 'run') {
      out.push(...(await runCheck(look, c, c.action.argv, undefined, { ...env, LINT_TEXT: subject.lines.join('\n') })))
      continue
    }
    let re: RegExp
    try {
      const raw = toRegExp(c.action.pattern)
      re = new RegExp(raw.source, raw.flags + 'm')
    } catch (err) {
      out.push({ id: c.id, severity: 'warn', text: `regex 讀不懂：${(err as Error).message}` })
      continue
    }
    const hit = subject.lines.find(l => re.test(l))
    if (hit === undefined) continue
    const where = c.scope.actions.length || at.key.startsWith('around:') ? `${hit.slice(0, 200)}：` : ''
    out.push({ id: c.id, ...level(c), text: `${where}${c.message}` })
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
  const known = (email: string) => f.authors.some(a => a.toLowerCase().includes(`<${email}>`))
  const refs = /\bpush\b/.test(command) ? pushRefs(command) : null
  if (/\bcommit\b/.test(command)) {
    // `git -c user.email=X commit` commits as X whatever the config says.
    const override = /-c\s+["']?user\.email=["']?([^"'\s]+)/.exec(command)?.[1]
    const email = (override ?? String((await runGit(look, ['git', 'config', 'user.email'])).stdout)).trim().toLowerCase()
    if (f.commits >= 5 && email && !known(email))
      out.push({ id: c.id, ...level(c), text: `目前的 git 身分 <${email}> 不在這個 repo 的近期作者裡。${c.message}\n${f.text}` })
  } else if (/\bpush\b/.test(command)) {
    // A push makes no commit: what matters is who wrote the commits it sends. A refspec (`tmp:dev`) sends what
    // the source has and the remote's destination lacks; without one, the branch's own upstream decides.
    const ranges = refs ? refs.map(r => [`${r.remote}/${r.dst}..${r.src}`]) : [['@{u}..HEAD']]
    const sent: string[] = []
    for (const [range] of ranges)
      sent.push(...String((await runGit(look, ['git', 'log', range, '--format=%ae'])).stdout).split(/\r?\n/).map(s => s.trim().toLowerCase()).filter(Boolean))
    const strangers = [...new Set(sent.filter(e => !known(e)))]
    if (f.commits >= 5 && strangers.length)
      out.push({ id: c.id, ...level(c), text: `要推上去的 commit 裡有不屬於這個 repo 近期作者的身分：${strangers.join('、')}。${c.message}` })
  }
  if (/\bcommit\b/.test(command) && /Co-Authored-By:/i.test(command) && f.coAuthor === 0 && f.commits >= 5)
    out.push({ id: c.id, ...level(c), text: `這個 repo 近 30 個 commit 都沒有 Co-Authored-By，這次卻加了。${c.message}` })
  // The branch a push lands on: each refspec's destination, else the current branch.
  const targets = refs ? refs.map(r => r.dst) : [(await runGit(look, ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])).stdout.trim()]
  if (/\bpush\b/.test(command) && f.prHabit && targets.includes(f.defaultBranch))
    out.push({ id: c.id, ...level(c), text: `這個 repo 習慣透過 PR/MR 合併，這次卻直接 push 到 ${f.defaultBranch}。${c.message}` })
  return out
}

async function secretFiles<H>(look: Look<H>, c: Check): Promise<Finding[]> {
  const staged = (await runGit(look, ['git', 'diff', '--cached', '--name-only'])).stdout.split(/\r?\n/).filter(Boolean)
  // A committed example (.env.example, app.env.sample, .env.template) shows the shape of a secret, not one.
  const bad = staged.filter((p: string) =>
    /(^|\/)(\.env(\..*)?|[^/]*\.pem|[^/]*\.key|id_rsa[^/]*|[^/]*\.p12|credentials[^/]*\.json)$/i.test(p) &&
    !/\.(example|sample|template)$/i.test(p),
  )
  return bad.map((p: string) => ({ id: c.id, ...level(c), text: `${p}：${c.message}` }))
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
  return [missing ? { id: c.id, ...level(c), text: `${text}\n${c.message}` } : { id: c.id, severity: 'note', text }]
}

// Before a commit or push: has the remote moved on since this branch last caught up?
async function upToDate<H>(look: Look<H>, c: Check): Promise<Finding[]> {
  const fetched = await runGit(look, ['git', 'fetch', '--quiet'], 20000)
  if (fetched.exitCode !== 0) return [{ id: c.id, severity: 'warn', text: `git fetch 沒成功，無法確認是不是最新版：${tail(fetched.stderr, 2)}` }]
  const behind = await runGit(look, ['git', 'rev-list', '--count', 'HEAD..@{u}'], 10000)
  if (behind.exitCode !== 0) return []
  const n = Number(String(behind.stdout).trim())
  return n > 0 ? [{ id: c.id, ...level(c), text: `遠端有 ${n} 個本機還沒有的 commit。${c.message}` }] : []
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
        out.push({ id: c.id, ...level(c), text: `${path}（${b}）：${c.message}` })
    }
  }
  return out
}

