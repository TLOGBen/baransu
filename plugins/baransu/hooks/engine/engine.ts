// The engine: one memory of the cross-event state per module load, and the inbound port over it.
// Reads like today's register(), minus every host detail: each hook body became one method here.

import { builtinOf, namesSkill, relTo } from './check'
import { commandFindings, commitLook, gitFacts, runMoment, worktreeCleanup } from './moments'
import type { Engine, Lint, Ports } from './ports'
import { commitDirs, destructivePreview, isGitWrite, writesFiles } from './shell'
import { CORRECTION, hanShare, render, restateNote, slipHead, summarize } from './text'
import type {
  Actor, Card, Check, Config, DoneSkillEvent, Finding, LintState, Outcome, PromptEvent, ReplyEvent, SkillPreface, SpokenEvent,
  SystemNote, ToolCallEvent, ToolVerdict, TurnEndEvent, TurnStartEvent,
} from './types'

/** Build the engine once, at module scope. A reload of the module builds a new one, which loads from storage. */
export function createEngine<H>(ports: Ports<H>): Engine<H> {
  const memory = new Memory<H>(ports)
  return {
    async ready(h) {
      await memory.loaded(h)
      return bind(h, ports, memory)
    },
  }
}

export const freshState = (): LintState => ({
  editSeq: 0, reviewedAt: -1, commands: [], spoke: true, previewed: [], steps: {}, slips: [], tools: 0, textAfterTools: '', cards: {},
})

const find = (config: Config, name: string): Check | undefined => config.checks.find(c => builtinOf(c) === name)

// ================================================================ memory

/**
 * The working copy of LintState. The only writer of the state: every method of every dispatch mutates this
 * one object and saves it through the StateStore port. JS runs one dispatch at a time between awaits, so a
 * synchronous stretch — a take plus its save — is atomic against every other dispatch.
 */
class Memory<H> {
  s: LintState = freshState()
  #loading: Promise<void> | undefined
  readonly #ports: Ports<H>
  constructor(ports: Ports<H>) {
    this.#ports = ports
  }

  /** Load once per engine; every caller, concurrent ones included, waits on the same promise. A failed load
   *  leaves fresh state (as today). */
  loaded(h: H): Promise<void> {
    return (this.#loading ??= this.#ports.state.load(h).then(v => { if (v) this.s = { ...freshState(), ...v } }, () => {}))
  }

  save(h: H): void {
    this.#ports.state.save(h, this.s)
  }

  /**
   * Take what a call or prompt delivers: the restates owed and the owed report. Synchronous, and saves before
   * returning, so (1) a second call in flight finds them gone and (2) a reload while the tool runs cannot hand
   * them out again from storage.
   *
   * mode 'prompt' — removes them and clears `offered` (prompt.submit that reaches the model now; as 8.39 did).
   * mode 'call'   — removes them and leaves `offered` as it is (tool.call on main: today it never touches
   *                 `offered`, which only turnStarted with text settles — a continuation turn has no text).
   * mode 'offer'  — leaves them owed and records a copy in `offered` (a slash command that may open no turn);
   *                 turnStarted settles the copy.
   * mode 'none'   — a subagent's call: takes nothing.
   *
   * The returned giveBack runs once (a `returned` flag, as today): it puts back everything it took, unconditionally —
   *   prompt, call → slips.unshift(...taken); pendingReport ??= taken report
   *   offer        → offered = undefined
   * then saves. A second call does nothing (the flag); no de-duplication by value, as today.
   */
  take(h: H, mode: 'prompt' | 'call' | 'offer' | 'none'): Taken {
    const s = this.s
    let slips: string[] = []
    let report: string | undefined
    if (mode === 'prompt' || mode === 'call') {
      slips = s.slips.splice(0)
      report = s.pendingReport
      s.pendingReport = undefined
      if (mode === 'prompt') s.offered = undefined
    } else if (mode === 'offer') {
      slips = [...s.slips]
      report = s.pendingReport
      s.offered = { slips, report }
    }
    this.save(h)
    let returned = false
    return {
      slips,
      report,
      giveBack: () => {
        if (returned) return
        returned = true
        // `this.s`, not `s`: a /clear in between replaced the state, and what is given back goes to the current one (as today).
        if (mode === 'prompt' || mode === 'call') {
          this.s.slips.unshift(...slips)
          if (report && !this.s.pendingReport) this.s.pendingReport = report
        } else if (mode === 'offer') this.s.offered = undefined
        this.save(h)
      },
    }
  }
}

type Taken = {
  readonly slips: readonly string[]
  readonly report?: string
  giveBack(): void
}

/** Keep a card under its call id; past 500 cards the oldest go. Every save copies the whole state, and that copy
 *  grows with the cards (measured 2026-11-03: about 6 ms at 500, 130 ms at 10,000), so the state must not grow
 *  without bound. */
function keepCard(s: LintState, id: string, d: Card) {
  s.cards[id] = d
  const ids = Object.keys(s.cards)
  for (const old of ids.slice(0, Math.max(0, ids.length - 500))) delete s.cards[old]
}

// ================================================================ inbound port

function bind<H>(h: H, ports: Ports<H>, memory: Memory<H>): Lint<H> {
  const S = () => memory.s
  const save = () => memory.save(h)

  return {
    async sessionStarted() {
      const config = await ports.config.load(h)
      if (!config) return
      const look = { runner: ports.runner, h, config }
      // Worktrees and git facts are a repo's; a plain-folder root (config.git false) has neither.
      const wt = config.git ? find(config, 'worktree-cleanup') : undefined
      if (wt) {
        const f = await worktreeCleanup(look, wt)
        if (f.length) await ports.notify.notice(h, `lint · session 開始 · 沒清掉的 worktree\n${f.map(x => `⚠ ${x.text}`).join('\n')}`)
      }
      if (config.git && find(config, 'git-facts')) S().gitFacts = (await gitFacts(look)).text
      const lang = find(config, 'user-language')
      if (lang?.language) S().userLanguage = lang.language
      save()
    },

    systemNotes(): SystemNote[] {
      const add: SystemNote[] = []
      const s = S()
      if (s.gitFacts) add.push({ id: 'baransu:lint-git', text: `這個 repo 的 git 習慣（baransu lint）。commit、push、開分支前照這些：\n${s.gitFacts}` })
      if (s.userLanguage) add.push({ id: 'baransu:lint-language', text: `使用者的慣用語言：${s.userLanguage}。寫給使用者看的文字一律用這個語言。` })
      return add
    },

    promptSubmit<R>(e: PromptEvent, proceed: (notes: readonly string[]) => Promise<R>, dropped: (r: R) => boolean): Promise<R> {
      // Not async: the take below runs before anything is awaited.
      const taken = memory.take(h, e.opensTurnNow ? 'prompt' : 'offer')
      return submitAfterTake(h, ports, memory, taken, e, proceed, dropped)
    },

    turnStarted(e: TurnStartEvent) {
      if (e.agent) return
      const s = S()
      s.spoke = false
      s.tools = 0
      s.textAfterTools = ''
      s.previewed = []
      // A slash command's message carried a copy of what was owed; it opened this turn, so that is delivered.
      if (s.offered && e.text) {
        for (const t of s.offered.slips) {
          const i = s.slips.indexOf(t)
          if (i >= 0) s.slips.splice(i, 1)
        }
        if (s.offered.report && s.pendingReport === s.offered.report) s.pendingReport = undefined
        s.offered = undefined
      }
      save()
    },

    async turnCompleted(e: TurnEndEvent) {
      if (e.agent) return
      // A /review counts only once the turn that ran it ends with an answer, not when it was stopped.
      if (S().reviewPending !== undefined) {
        if (e.answered) S().reviewedAt = S().reviewPending!
        S().reviewPending = undefined
      }
      if (S().slips.length) await ports.notify.notice(h, `lint · user-language：剛才那段寫成英文了（「${slipHead(S().slips[S().slips.length - 1])}」）→ 重新：下一步用你的語言再說一次`)
      const config = await ports.config.load(h)
      // Only a turn that ended with an answer owes a report: one the person interrupted (or that failed) left
      // the model no moment to give it (user 2026-11-03), and a report owed from before stays owed.
      if (config && e.answered) {
        const c = find(config, 'report-before-stop')
        // A report counts its whole text, tables and code included; a Han character counts as two letters.
        const text = S().textAfterTools
        const letters = (text.match(/\p{L}/gu) ?? []).length
        const han = (text.match(/\p{Script=Han}/gu) ?? []).length
        const reported = letters - han + 2 * han >= 60
        if (reported) S().pendingReport = undefined
        else if (c && S().tools > 0) {
          S().pendingReport = c.id
          await ports.notify.notice(h, `lint · ${c.id}：這一輪做了事，結束前卻沒交代現況 → 重新：下一步照 what-now 交代`)
        }
      }
      save()
    },

    cleared() {
      memory.s = { ...freshState(), userLanguage: S().userLanguage, gitFacts: S().gitFacts }
      save()
    },

    stepBegan(actor: Actor) {
      const who = actor.agent ?? 'main'
      S().steps[who] = (S().steps[who] ?? 0) + 1
      save()
    },

    textStreamed(e: SpokenEvent) {
      if (e.agent) return
      S().textAfterTools += e.text
      if (e.text.trim() && !S().spoke) {
        S().spoke = true
        save()
      }
    },

    replyAppended(e: ReplyEvent) {
      if (e.agent) return
      if (e.text.trim()) S().spoke = true
      // The user writes Chinese and this block is English prose: owe a restate of this block.
      const { han, letters } = hanShare(e.text)
      const lang = S().userLanguage
      const wantsChinese = !!lang && /中文|zh/i.test(lang)
      if (wantsChinese && letters >= 40 && han / letters < 0.1) S().slips.push(e.text.trim().slice(0, 800))
      save()
    },

    toolCall<R>(e: ToolCallEvent, proceed: () => Promise<R>, outcome: (r: R) => Outcome): Promise<ToolVerdict<R>> {
      // Not async: the take and the two readings that must belong to the moment the call arrived happen here.
      const main = !e.agent
      const taken = memory.take(h, main ? 'call' : 'none')
      const at = { editSeq: S().editSeq, step: S().steps[e.agent ?? 'main'] ?? 0 }
      return callAfterTake(h, ports, memory, taken, at, e, proceed, outcome)
    },

    async skillPrompt(e: DoneSkillEvent): Promise<SkillPreface> {
      const isReview = e.skill === 'review'
      if (isReview) {
        // Counted when the review's turn ends with an answer (turnCompleted), not when it starts.
        S().reviewPending = S().editSeq
        save()
      }
      const config = await ports.config.load(h)
      if (!config) return null
      const look = { runner: ports.runner, h, config }
      if (e.skill === 'other') {
        // Any other skill: only the checks whose `on` names it; none → the skill is left as it is.
        if (!config.checks.some(c => namesSkill(c, e.name))) return null
        const found = await runMoment(look, S(), 'skill', { skill: e.name })
        const said = render('skill', `/${e.name}`, found)
        await ports.notify.notice(h, said)
        const tail = found.some(f => f.severity === 'error')
          ? `這是 /${e.name} 開始前跑的檢查。有 error：先把 error 交代給使用者，修好或問過他，再做這個 skill 的事。`
          : `這是 /${e.name} 開始前跑的檢查；warn 在做完時一起交代。`
        return { text: `## Lint 紀錄（baransu lint mod，這個版本）\n\n${said}\n\n${tail}` }
      }
      const manual = e.skill === 'lint'
      const findings = await runMoment(look, S(), manual ? 'manual' : 'done', { skill: e.name })
      const text = manual ? render('manual', '/lint', findings) : render('done', isReview ? '/review' : '/ship', findings)
      await ports.notify.notice(h, text)
      const errors = findings.some(f => f.severity === 'error')
      const tailLine = manual
        ? '這是叫 /lint 時先跑的全部檢查。先把結果用一兩句話交代給使用者（沒有發現也說），再做使用者這次要求的事。'
        : isReview
          ? '這是 review 開始前、作者這一端跑的 lint 紀錄，照 review 的判定規則讀。'
          : errors
            ? '有 error：停下，不要 commit；把上面的 error 回報給使用者。'
            : '沒有 error，可以繼續；warn 要在收尾報告裡提到。'
      return { text: `## Lint 紀錄（baransu lint mod，這個版本）\n\n${text}\n\n${tailLine}` }
    },

    cardFor(callId: string): Card | undefined {
      return S().cards[callId]
    },
  }
}

// ================================================================ the async halves

async function submitAfterTake<H, R>(
  h: H, ports: Ports<H>, memory: Memory<H>, taken: Taken, e: PromptEvent,
  proceed: (notes: readonly string[]) => Promise<R>, dropped: (r: R) => boolean,
): Promise<R> {
  const S = () => memory.s
  try {
    const config = await ports.config.load(h)
    if (!config) {
      taken.giveBack()
      return proceed([])
    }
    const lang = find(config, 'user-language')
    if (lang && !lang.language) {
      const han = (e.typed.match(/\p{Script=Han}/gu) ?? []).length
      const letters = (e.typed.match(/\p{L}/gu) ?? []).length
      if (letters) S().userLanguage = han / letters > 0.2 ? '中文（照使用者用的字，繁體或簡體）' : 'English'
    }
    const notes: string[] = []
    if (lang) notes.push(...taken.slips.map(t => restateNote(lang, S().userLanguage, t)))
    if (taken.report) {
      const rc = config.checks.find(c => c.id === taken.report)
      const how = rc?.redo ?? `先照 ${ports.whatNowSkill(h)} 的寫法（那個 skill 只有使用者能叫，讀它照做）重新交代：第一句說有什麼等使用者決定或沒有；做了什麼、做到哪、哪些沒驗證；每個等他決定的事附上建議、依據和風險。`
      notes.push(`baransu lint（${taken.report}，重新）：上一輪做了事，結束前卻沒交代現況。回應這則訊息之前，${how}`)
    }
    const fix = find(config, 'correction-to-lint')
    if (fix && CORRECTION.test(e.typed)) {
      await ports.notify.notice(h, `lint · ${fix.id}：這像是在糾正，修完後會評估能不能寫成 lint`)
      notes.push(`baransu lint（${fix.id}）：使用者在糾正你。先照他說的修好，再判斷這個錯能不能寫成檢查：能，就交給 /baransu:lint 新增（附上這次錯在哪、怎麼修、出錯的 commit）；不能，用一句話說明為什麼。${fix.message}`)
    }
    memory.save(h)
    const r = await proceed(notes)
    // The prompt did not enter (a hook or a settings hook below refused it): what it took is still owed.
    if (dropped(r)) taken.giveBack()
    return r
  } catch (err) {
    // Whatever failed after the take, what was taken goes back to be delivered next time.
    taken.giveBack()
    throw err
  }
}

/**
 * Gate, run, after-moment. Order and early returns as today's tool.call:
 *   no config        → giveBack; r = proceed(); count an edit (edit tool, or shell that writes files) if it ran clean
 *   restates owed    → card lines (redo) + notes
 *   owed report      → card line (redo) + note
 *   main && !spoke   → spoke = true; explain-before-edit: error → deny (card, replace) | warn → redo line + note
 *   shell            → command checks (error → deny) ; destructive-preview (see below)
 *   shell git write  → runMoment('commit') (error → deny)
 *   r = await proceed(); o = outcome(r)
 *   !o.ran || o.isError → giveBack                ← notes were not delivered
 *   main && o.ran && !o.isReadOnly → tools++, textAfterTools = ''
 *   shell && o.ran → writesFiles ? editSeq++ : (!background && commands.push({ cmd, ok: !o.isError, seq: at.editSeq }))
 *   edit && o.ran && !o.isError → editSeq++; ports.config.edited(h, file); in repo → runMoment('edit', file)
 *   card kept under e.id when lines (keepCard: the oldest cards are dropped past 500 — state must
 *     not grow without bound); notes returned only when o.ran && !o.isError
 *
 * destructive-preview — key = `${agent ?? 'main'}|${shell}|${cwd}|${command}`; seen = previewed[key]
 *   passes only when seen && seen.step < at.step (a later response of the same actor, this turn).
 *   Else touched = await destructivePreview(...); if touched: record {key, step: at.step} unless seen;
 *   error → deny with kind 'hold'. Two copies in one response share at.step, so both are held (R11).
 *
 * A deny: keep the card (replace: true; same 500-card trim), save, return { kind: 'deny', reason: [deny, ...notes].join('\n\n') }.
 * The taken items ride on the refusal and are not given back — the model reads them in the refusal.
 *
 * Twice / halfway: the whole body sits in try/catch → giveBack, so a throw anywhere after the take re-owes
 * what was taken; giveBack is idempotent, so a throw after an explicit giveBack does not re-owe twice.
 */
async function callAfterTake<H, R>(
  h: H, ports: Ports<H>, memory: Memory<H>, taken: Taken, at: { editSeq: number; step: number },
  e: ToolCallEvent, proceed: () => Promise<R>, outcome: (r: R) => Outcome,
): Promise<ToolVerdict<R>> {
  const S = () => memory.s
  const save = () => memory.save(h)
  const main = !e.agent
  const isEdit = e.kind === 'edit'
  const isBash = e.kind === 'shell'
  const command = e.kind === 'shell' ? e.command : ''
  try {
    const config = await ports.config.load(h)
    if (!config) {
      taken.giveBack()
      // Nothing is checked without .claude/lint/, but edits still count for a /lint set up later this session.
      const r = await proceed()
      const o = outcome(r)
      if (o.ran && !o.isError && (isEdit || (isBash && writesFiles(command)))) {
        S().editSeq++
        save()
      }
      return { kind: 'ran', result: r, notes: [] }
    }
    const root = config.root
    const look = { runner: ports.runner, h, config }
    // Where this call's shell is: the session's own directory, read inside the hook (a subagent's own).
    const cwdNow = e.cwd || root
    const context: string[] = []
    // Everything lint says about this call is drawn as one card under it.
    const inline: Finding[] = []
    // A refused call still hands the model what it is owed: the notes ride on the refusal.
    const refuse = (d: Card, deny: string): ToolVerdict<R> => {
      keepCard(S(), e.id, { ...d, replace: true })
      save()
      return { kind: 'deny', reason: [deny, ...context].join('\n\n') }
    }

    // Blocks written in the wrong language since the last call: redo each in the user's language.
    const lang = find(config, 'user-language')
    if (lang)
      for (const t of taken.slips) {
        inline.push({ id: lang.id, severity: 'redo', text: `剛才那段寫成英文了（「${slipHead(t)}」）→ 重新：用你的語言再說一次` })
        context.push(restateNote(lang, S().userLanguage, t))
      }

    // A report owed from the last turn that the user's next message did not carry (it was typed while that turn ran).
    if (taken.report) {
      const rc = config.checks.find(c => c.id === taken.report)
      const how = rc?.redo ?? `先照 ${ports.whatNowSkill(h)} 的寫法（那個 skill 只有使用者能叫，讀它照做）重新交代上一輪的現況：有什麼等使用者決定、做了什麼、做到哪、哪些沒驗證。`
      inline.push({ id: taken.report, severity: 'redo', text: '上一輪做了事卻沒交代現況 → 重新：照 what-now 交代' })
      context.push(`baransu lint（${taken.report}，重新）：上一輪做了事，結束前卻沒交代現況。${how}`)
    }

    // Words before acting: the first file change of a turn — an edit, or a command that writes a file — should
    // follow a word on how it will be done. A read-only look is no act and leaves the turn's flag as it is.
    if (main && !S().spoke && (isEdit || (isBash && writesFiles(command)))) {
      const c = find(config, 'explain-before-edit')
      S().spoke = true
      if (c) {
        const what = '這一輪還沒說要怎麼動手，就先改檔了'
        const how = c.redo ?? '改檔前先用一兩句話說要怎麼動手：改哪些檔、怎麼改，然後直接繼續，不等他確認；只有真的不確定他要什麼時才停下來問'
        if (c.severity === 'error') return refuse({ kind: 'error', title: '沒有執行', meta: `lint · ${c.id}`, lines: [{ id: c.id, severity: 'error', text: what }], footer: '先說要怎麼動手，再下一次' }, `baransu lint（${c.id}）：${what}。${how}。`)
        inline.push({ id: c.id, severity: 'redo', text: `${what} → 重新：先說要怎麼動手` })
        context.push(`baransu lint（${c.id}，重新）：${what}。${how}。`)
      }
    }

    // Before any shell command: checks that read the command line itself.
    if (e.kind === 'shell') {
      const findings = commandFindings(config.checks, command)
      if (findings.some(f => f.severity === 'error')) {
        return refuse({ ...summarize('指令前', findings)!, title: '沒有執行', footer: '照上面改寫這個指令再跑' }, `${render('bash', '', findings)}\n照上面改寫這個指令再跑。`)
      }
      if (findings.length) {
        inline.push(...findings)
        context.push(render('bash', '', findings))
      }

      // Before a command that deletes, moves or discards: show what it will touch, once per actor, directory and turn.
      // The same command passes only in a later response than the one held, after the model has read the list.
      const preview = find(config, 'destructive-preview')
      const key = `${e.agent ?? 'main'}|${e.shell}|${cwdNow}|${command}`
      const seen = S().previewed.find(p => p.key === key)
      if (preview && !(seen && seen.step < at.step)) {
        const touched = await destructivePreview(ports.runner, h, root, command, cwdNow)
        if (touched.length) {
          if (!seen) S().previewed.push({ key, step: at.step })
          const text = `lint · ${preview.id}：這個指令會動到\n${touched.map(t => `  ${t}`).join('\n')}`
          const lines = touched.map(t => ({ id: '', severity: 'note' as const, text: t }))
          if (preview.severity === 'error') return refuse({ kind: 'hold', title: '先確認會動到的東西', meta: 'lint · 刪除前預覽', lines, footer: '確認沒錯，再下一次同樣的指令就會執行' }, `${text}\n${preview.message}`)
          inline.push(...lines)
          context.push(text)
        }
      }
    }

    // Before a git commit or push. An ordinary project: once, at the root, whenever isGitWrite reads one (8.39).
    // Otherwise commitDirs alone says which segments write with git — a mention in another command's quotes
    // (`rg "git push"`) is none — and each write is checked in the repo it commits in. A write whose directory
    // the text does not show, or with no repo to check, gets a warning that its checks did not run: never a
    // silent skip, never a scan of the whole workspace. Findings of a repo's own checks carry `[repo] ` when
    // the command writes to more than one; config problems and the session record are said once, untagged.
    const plainWrites = isBash && !config.git ? commitDirs(command, cwdNow) : []
    const gitWrite = isBash && (config.git ? isGitWrite(command) : plainWrites.length > 0)
    if (gitWrite) {
      let findings: Finding[]
      if (config.git) findings = await runMoment(look, S(), 'commit', { command })
      else {
        findings = []
        const dirs = plainWrites
        const ran = '這次 commit／push 會照常執行，但它的 lint 檢查沒有跑'
        const general = new Set([
          ...config.problems.map(p => p.id),
          ...config.checks.filter(c => builtinOf(c) === 'built-before-commit').map(c => c.id),
        ])
        for (const dir of dirs) {
          if (dir === null) {
            findings.push({ id: 'commit-repo', severity: 'warn', text: `看不出這次 commit／push 在哪個 repo（路徑用了 ~、變數、cd -、popd，或 git 包在別的指令裡）。${ran}；下次改寫成 cd <實際路徑> && git …` })
            continue
          }
          const { look: there, skip } = await commitLook(look, dir)
          if (skip) {
            const where = relTo(root, dir)
            findings.push({ id: 'commit-repo', severity: 'warn', text: skip === 'none' ? `${where} 不在任何 git repo 裡。${ran}` : `${where} 的 repo 不在這個 lint 的資料夾（${root}）底下。${ran}` })
            continue
          }
          const tag = dirs.length > 1 && there.repo?.rel ? `[${there.repo.rel}] ` : ''
          findings.push(...(await runMoment(there, S(), 'commit', { command })).map(f => (tag && f.id && !general.has(f.id) ? { ...f, text: tag + f.text } : f)))
        }
        const seen = new Set<string>()
        findings = findings.filter(f => !seen.has(`${f.id}|${f.text}`) && !!seen.add(`${f.id}|${f.text}`))
      }
      if (findings.some(f => f.severity === 'error')) {
        return refuse({ ...summarize('commit 前', findings)!, title: /\bpush\b/.test(command) ? '沒有 push' : '沒有 commit', footer: '修好 error 再 commit／push' }, `${render('commit', '', findings)}\n修好 error 再 commit / push。`)
      }
      const shown = findings.filter(f => f.severity !== 'note')
      if (shown.length) {
        inline.push(...shown)
        context.push(render('commit', '', findings))
      }
    }

    const result = await proceed()
    const o = outcome(result)
    // A call refused further down, or a run that failed, carries no notes: what was taken goes back.
    if (!o.ran || o.isError) taken.giveBack()
    // Work done this turn, and the text after it starts over; a read-only call (git status, ls) does neither.
    if (main && o.ran && !o.isReadOnly) {
      S().tools++
      S().textAfterTools = ''
    }
    if (e.kind === 'shell' && o.ran) {
      // A shell command that writes files is an edit, not a check run after one. A background command
      // has only started, so it is not a run; a command counts against the edit count it started at.
      if (writesFiles(command)) S().editSeq++
      else if (!e.background) S().commands.push({ cmd: command, ok: o.isError !== true, seq: at.editSeq })
    }

    // After a successful edit.
    const file = e.kind === 'edit' ? relTo(root, e.file) : ''
    const insideRepo = file !== '' && !/^([A-Za-z]:)?\//.test(file)
    if (isEdit && o.ran && !o.isError) S().editSeq++
    if (isEdit && insideRepo && o.ran && !o.isError) {
      // An edit to the lint config (wherever lint.json put it) drops the source's cache: this moment reads the
      // checks again. The config source alone knows which files are its own.
      const fresh = ports.config.edited(h, file) ? ((await ports.config.load(h)) ?? config) : config
      const findings = (await runMoment({ ...look, config: fresh }, S(), 'edit', { file })).filter(f => f.severity !== 'note')
      if (findings.length) {
        inline.push(...findings)
        context.push(`${render('edit', file, findings)}\n修好 error；warn 判斷要不要改。`)
      }
    }

    save()
    if (inline.length && o.ran) {
      const d = summarize(isEdit ? `改檔後 · ${file}` : gitWrite ? 'commit 前' : '指令前', inline)
      keepCard(S(), e.id, d ?? { kind: 'warn', meta: 'lint', lines: inline })
      save()
    }
    return { kind: 'ran', result, notes: context.length && o.ran && !o.isError ? context : [] }
  } catch (err) {
    // Whatever failed after the take, what was taken goes back to be delivered next time.
    taken.giveBack()
    throw err
  }
}

