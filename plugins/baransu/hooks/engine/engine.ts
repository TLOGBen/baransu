// The engine: one memory of the cross-event state per module load, and the inbound port over it.
// Every entry point reads the same way: find (the checks at a timing) → settle (timing.ts: what each level
// does there) → send (the host's way for that timing: refuse, hold the stop, a line, a 重新, the card, the
// queue). Nothing here names a host event; adapters/claude-code translates.

import { addedLines, aroundEnv, diffHead, diffTree, headBefore, MAX_SPANS, snapEdit, snapHead, snapTree, treeBefore, wantsAround, type HeadSnap, type Store, type TreeSnap } from './around'
import { builtinOf, namesSkill, relTo } from './check'
import { commitLook, gitFacts, runMoment, worktreeCleanup, type Look } from './moments'
import type { Engine, Lint, Ports } from './ports'
import { runsAt } from './scope/evaluate'
import type { Occurrence, RedoKind } from './scope/types'
import { commitDirs, deletedPaths, destructivePreview, gitWrites, isGitWrite, pushRefs, removedWorktrees, writesFiles, type PreviewLine } from './shell'
import { cardOf, CORRECTION, hanShare, render, restateNote, skillCard, slipHead, summarize } from './text'
import { settle, STOP_HOLDS, type AfterKey, type Settled, type TimingKey } from './timing'
import type {
  Actor, Card, Check, Config, DoneSkillEvent, Finding, LintState, Outcome, PromptEvent, ReplyEvent, SkillPreface, SpokenEvent,
  StopVerdict, SystemNote, ToolCallEvent, ToolVerdict, TurnEndEvent, TurnStartEvent,
} from './types'

/** Build the engine once, at module scope. A reload of the module builds a new one, which loads from storage. */
export function createEngine<H>(ports: Ports<H>): Engine<H> {
  const memory = new Memory<H>(ports)
  let armed = false
  return {
    async ready(h) {
      await memory.loaded(h)
      // A reload cancelled the old module's waits: arm every stored deadline again, once per engine.
      if (!armed) {
        armed = true
        await rearm(h, ports, memory)
      }
      return bind(h, ports, memory)
    },
  }
}

export const freshState = (): LintState => ({
  editSeq: 0, reviewedAt: -1, commands: [], spoke: true, held: [], steps: {}, slips: [], tools: 0, textAfterTools: '', cards: {},
})

const find = (config: Config, name: string): Check | undefined => config.checks.find(c => builtinOf(c) === name)

/** At most this many lines wait in LintState.queued; the oldest go (every save copies the whole state). */
export const MAX_QUEUED = 20

/** The default instruction of report-before-stop's 重新. */
const reportHow = (skill: string) =>
  `先照 ${skill} 的寫法（那個 skill 只有使用者能叫，讀它照做）交代現況：第一句說有什麼等使用者決定或沒有；做了什麼、做到哪、哪些沒驗證；每個等他決定的事附上建議、依據和風險。`

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
   *  leaves fresh state. A stored value from before 8.43 (previewed, pendingReport) loads with `held` fresh. */
  loaded(h: H): Promise<void> {
    return (this.#loading ??= this.#ports.state.load(h).then(v => { if (v) this.s = { ...freshState(), ...v, held: Array.isArray(v.held) ? v.held : [] } }, () => {}))
  }

  save(h: H): void {
    this.#ports.state.save(h, this.s)
  }

  /**
   * Take what a call or prompt delivers: the restates owed and the queued lines. Synchronous, and saves before
   * returning, so (1) a second call in flight finds them gone and (2) a reload while the tool runs cannot hand
   * them out again from storage.
   *
   * mode 'prompt' — removes them and clears `offered` (prompt.submit that reaches the model now).
   * mode 'call'   — removes them and leaves `offered` as it is (tool.call on main).
   * mode 'offer'  — leaves them owed and records a copy of the restates in `offered` (a slash command that may
   *                 open no turn); turnStarted settles the copy. Queued lines stay queued.
   * mode 'none'   — a subagent's call: takes nothing.
   *
   * The returned giveBack runs once: it puts back everything it took (restates first, then the queued lines
   * ahead of any queued since), or clears `offered`; then saves.
   */
  take(h: H, mode: 'prompt' | 'call' | 'offer' | 'none'): Taken {
    const s = this.s
    let slips: string[] = []
    let queued: string[] = []
    if (mode === 'prompt' || mode === 'call') {
      slips = s.slips.splice(0)
      queued = (s.queued ?? []).splice(0)
      if (mode === 'prompt') s.offered = undefined
    } else if (mode === 'offer') {
      slips = [...s.slips]
      s.offered = { slips }
    }
    this.save(h)
    let returned = false
    return {
      slips,
      queued,
      giveBack: () => {
        if (returned) return
        returned = true
        // `this.s`, not `s`: a /clear in between replaced the state, and what is given back goes to the current one.
        if (mode === 'prompt' || mode === 'call') {
          this.s.slips.unshift(...slips)
          this.s.queued = [...queued, ...(this.s.queued ?? [])].slice(-MAX_QUEUED)
        } else if (mode === 'offer') this.s.offered = undefined
        this.save(h)
      },
    }
  }
}

type Taken = {
  readonly slips: readonly string[]
  readonly queued: readonly string[]
  giveBack(): void
}

/** Put lines for the model in the queue (a stop or a subagent's end that passed, a file changed outside, a
 *  wait run out). Synchronous, saves. */
function enqueue<H>(memory: Memory<H>, h: H, lines: readonly string[]) {
  if (!lines.length) return
  memory.s.queued = [...(memory.s.queued ?? []), ...lines].slice(-MAX_QUEUED)
  memory.save(h)
}

/**
 * A 重新 reached the model: record it as owed an answer (LintState.answering; hypothesis lint-mod-state
 * R14–R17). `step` is steps.main now: the model answers in a later response. Synchronous, saves.
 */
function deliver<H>(memory: Memory<H>, h: H, kinds: readonly RedoKind[]) {
  if (!kinds.length) return
  const s = memory.s
  const id = (s.answerSeq ?? 0) + 1
  s.answerSeq = id
  s.answering = [...(s.answering ?? []), { id, kinds: [...new Set(kinds)], step: s.steps.main ?? 0 }]
  memory.save(h)
}

/** Take the answer card waiting for a row to be drawn on (the next main-loop call), synchronously. */
function takeAnswerCard(s: LintState): Card | undefined {
  const d = s.answerCard
  s.answerCard = undefined
  return d
}

/** Keep a card under its call id; past 500 cards the oldest go. Every save copies the whole state, and that copy
 *  grows with the cards (measured 2026-11-03: about 6 ms at 500, 130 ms at 10,000), so the state must not grow
 *  without bound. */
function keepCard(s: LintState, id: string, d: Card) {
  s.cards[id] = d
  const ids = Object.keys(s.cards)
  for (const old of ids.slice(0, Math.max(0, ids.length - 500))) delete s.cards[old]
}

/** Every timing's card for the person: kept under its call when it has one, so a redraw finds it; a moment with
 *  no call is said as a plain row and kept nowhere (purpose over display, 2026-11-04). */
async function post<H>(h: H, ports: Ports<H>, memory: Memory<H>, card: Card, at?: string) {
  if (at) {
    keepCard(memory.s, at, card)
    memory.save(h)
  }
  try {
    await ports.view.show(h, card, at)
  } catch {}
}

/** The person's language: the user-language check's own `language`, else the host's language setting (Claude
 *  Code's `language`); with neither, what a guess from the person's messages left stands (submitAfterTake). */
async function settleLanguage<H>(h: H, ports: Ports<H>, memory: Memory<H>, lang: Check | undefined) {
  const s = memory.s
  if (lang?.language) {
    s.userLanguage = lang.language
    s.languageFrom = 'check'
    return
  }
  let setting: string | undefined
  try {
    setting = await ports.languageSetting(h)
  } catch {}
  if (setting) {
    s.userLanguage = setting
    s.languageFrom = 'setting'
  } else if (s.languageFrom === 'setting' || s.languageFrom === 'check') {
    // The setting or the check's language was removed: guess again from the next message.
    s.userLanguage = undefined
    s.languageFrom = undefined
  }
}

/** A short stable hash (FNV-1a), for the held key of an edit: the same file with other text is another act. */
function hash(text: string): string {
  let x = 0x811c9dc5
  for (let i = 0; i < text.length; i++) x = Math.imul(x ^ text.charCodeAt(i), 0x01000193)
  return (x >>> 0).toString(16)
}

/** The line the model reads for a settled set: the 重新 ones as requests, the rest as one rendered block. */
function told(label: Parameters<typeof render>[0], where: string, s: Settled, tail = ''): { lines: string[]; redo: boolean } {
  const lines: string[] = []
  for (const f of s.redo) lines.push(`baransu lint（${f.id}，重新）：${f.text}。照這個要求重做這一步，回應時說明改了什麼。`)
  const plain = [...s.fix, ...s.line]
  if (plain.length) lines.push(`${render(label, where, plain)}${s.fix.length && tail ? `\n${tail}` : ''}`)
  return { lines, redo: s.redo.length > 0 }
}

// ================================================================ inbound port

/** What a moment looks at, from the ports and the config. */
export const lookOf = <H>(ports: Ports<H>, h: H, config: Config): Look<H> =>
  ({ runner: ports.runner, h, config, machine: ports.machine, languages: ports.languages })

function bind<H>(h: H, ports: Ports<H>, memory: Memory<H>): Lint<H> {
  const S = () => memory.s
  const save = () => memory.save(h)

  return {
    async sessionStarted() {
      const config = await ports.config.load(h)
      if (!config) return
      const look = lookOf(ports, h, config)
      // Worktrees and git facts are a repo's; a plain-folder root (config.git false) has neither.
      const wt = config.git ? find(config, 'worktree-cleanup') : undefined
      if (wt) {
        const f = await worktreeCleanup(look, wt)
        if (f.length) await post(h, ports, memory, cardOf('session 開始 · 沒清掉的 worktree', f))
      }
      if (config.git && find(config, 'git-facts')) S().gitFacts = (await gitFacts(look)).text
      await settleLanguage(h, ports, memory, find(config, 'user-language'))
      save()
      // The around store keeps every snapshot it was given: what is older than two days no act still reads.
      const store = await storePath(h, ports)
      if ((await ports.runner.probe(h, store)).kind === 'dir')
        await ports.runner.run(h, ['git', `--git-dir=${store}`, 'gc', '--quiet', '--prune=2.days.ago'], { cwd: config.root, timeoutMs: 60000 })
    },

    async systemNotes(): Promise<SystemNote[]> {
      const add: SystemNote[] = []
      const config = await ports.config.load(h)
      // The setting may have changed since the session started: read it again for each prompt.
      if (config) await settleLanguage(h, ports, memory, find(config, 'user-language'))
      const s = S()
      if (s.gitFacts) add.push({ id: 'baransu:lint-git', text: `這個 repo 的 git 習慣（baransu lint）。commit、push、開分支前照這些：\n${s.gitFacts}` })
      // Claude Code's own setting is already in its system prompt (its language section): not said twice.
      if (s.userLanguage && s.languageFrom !== 'setting') add.push({ id: 'baransu:lint-language', text: `使用者的慣用語言：${s.userLanguage}。寫給使用者看的文字一律用這個語言。` })
      // remind = true: the rule is known before the act, not only after a slip. Read from the config each time,
      // so a check added or turned off mid-session counts at the next prompt.
      const reminds = (config?.checks ?? []).filter(c => c.remind && c.message)
      if (reminds.length) add.push({ id: 'baransu:lint-remind', text: `這個 repo 的 lint 規則（baransu lint，事前提醒）：\n${reminds.map(c => `- ${c.id}：${c.message}`).join('\n')}` })
      return add
    },

    async watchPaths() {
      const config = await ports.config.load(h)
      return config && config.checks.some(c => c.on.some(t => t.key === 'post:file')) ? [config.root] : []
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
      s.held = []
      s.stopHolds = 0
      s.touched = []
      // A slash command's message carried a copy of what was owed; it opened this turn, so that is delivered.
      if (s.offered && e.text) {
        for (const t of s.offered.slips) {
          const i = s.slips.indexOf(t)
          if (i >= 0) s.slips.splice(i, 1)
        }
        const kinds: RedoKind[] = s.offered.slips.length ? ['restate'] : []
        s.offered = undefined
        deliver(memory, h, kinds)
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
      // Before any await: a 重新 the model read (a later response began) and did not answer is dropped; one
      // delivered with a queued message it has not read yet waits for the next turn.
      const main = S().steps.main ?? 0
      if (S().answering?.length) S().answering = S().answering!.filter(a => a.step >= main)
      const unseen = takeAnswerCard(S())
      if (S().lintTurn) {
        S().lintTurn = false
        ports.config.reload()
      }
      save()
      if (unseen) await post(h, ports, memory, unseen)
      if (S().slips.length) {
        const lang = 'user-language'
        await post(h, ports, memory, { kind: 'retry', meta: `lint · ${lang}`, lines: [{ id: lang, severity: 'retry', text: `剛才那段寫成英文了（「${slipHead(S().slips[S().slips.length - 1])}」）→ 重新：下一步用你的語言再說一次` }] })
      }
    },

    cleared() {
      memory.s = { ...freshState(), userLanguage: S().userLanguage, languageFrom: S().languageFrom, gitFacts: S().gitFacts, timers: S().timers, objects: S().objects }
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

    async replyAppended(e: ReplyEvent) {
      if (e.agent) return
      if (e.text.trim()) S().spoke = true
      // The user writes Chinese and this block is English prose: owe a restate of this block.
      const { han, letters } = hanShare(e.text)
      const lang = S().userLanguage
      const wantsChinese = !!lang && /中文|zh/i.test(lang)
      if (wantsChinese && letters >= 40 && han / letters < 0.1) S().slips.push(e.text.trim().slice(0, 800))
      // The first row with words the person sees, in a later response than the one a 重新 reached the model
      // in, answers it: taken here, with the save, before the first await (R14–R17).
      const now = S().steps.main ?? 0
      const answered = e.visible.trim() ? (S().answering ?? []).filter(a => a.step < now) : []
      if (answered.length) S().answering = S().answering!.filter(a => a.step >= now)
      save()
      if (!answered.length) return
      const config = await ports.config.load(h)
      if (!config) return
      const redo = [...new Set(answered.flatMap(a => a.kinds))]
      const at: Occurrence = { key: 'post:retry', redo, text: e.visible }
      // One check per row, every kind it answers together.
      const due = config.checks.filter(c => c.action.kind !== 'builtin' && runsAt(c, at))
      if (!due.length) return
      const findings = (await runMoment(lookOf(ports, h, config), S(), at)).filter(f => f.severity !== 'note' || f.quiet)
      // An answer that passed needs nothing from anyone: no card.
      if (!findings.length) return
      const errors = findings.filter(f => f.severity === 'error').length
      const warns = findings.filter(f => f.severity === 'warn').length
      S().answerCard = {
        kind: errors ? 'scanError' : warns ? 'scanWarn' : 'scan',
        title: errors || warns ? '回答還有問題' : '回答檢查過了',
        meta: `lint · 回應後 · ${due.length} 條檢查${errors ? ` · ${errors} error` : ''}${warns ? ` · ${warns} warn` : ''}`,
        lines: findings,
      }
      save()
    },

    toolCall<R>(e: ToolCallEvent, proceed: () => Promise<R>, outcome: (r: R) => Outcome): Promise<ToolVerdict<R>> {
      // Not async: the take and the two readings that must belong to the moment the call arrived happen here.
      const main = !e.agent
      const taken = memory.take(h, main ? 'call' : 'none')
      const at = { editSeq: S().editSeq, step: S().steps[e.agent ?? 'main'] ?? 0 }
      // The check of the last answer to a 重新 is drawn on this call's row; what post:retry tells the model
      // (timing.ts: an error as a fix, its warn on the card only) reaches it as lines.
      const answer = main ? takeAnswerCard(S()) : undefined
      if (answer) {
        keepCard(S(), `${e.id}#answer`, answer)
        save()
      }
      const toldAnswer = answer ? settle('post:retry', answer.lines.filter(l => l.severity !== 'note')) : undefined
      const answerNote = toldAnswer
        ? [...toldAnswer.fix, ...toldAnswer.line].map(l => `baransu lint（${l.id}）：剛才的回答 ${l.text}`).join('\n')
        : ''
      return callAfterTake(h, ports, memory, taken, at, e, proceed, outcome, answerNote || undefined)
    },

    async skillPrompt(e: DoneSkillEvent): Promise<SkillPreface> {
      // `/lint help` explains, `/lint show` lists the checks from their files: neither runs one.
      // /lint is where the rules change: what was read is forgotten, and this call reads the folder again.
      if (e.skill === 'lint') {
        ports.config.reload()
        // The rules change after this moment, through the commands /lint runs (copying sets, the migration
        // scripts): each main-loop command while it runs, and the end of its turn, read the folder again.
        S().lintTurn = true
        save()
      }
      if (e.skill === 'lint' && /^(help|show)\b/i.test(e.args)) return null
      const isReview = e.skill === 'review'
      if (isReview) {
        // Counted when the review's turn ends with an answer (turnCompleted), not when it starts.
        S().reviewPending = S().editSeq
        save()
      }
      const config = await ports.config.load(h)
      if (!config) return null
      const look = lookOf(ports, h, config)
      const manual = e.skill === 'lint'
      // Any skill but /lint, /ship and /review: only the checks naming it; none → the skill is left as it is.
      if (e.skill === 'other' && !config.checks.some(c => namesSkill(c, e.name))) return null
      const at: Occurrence = manual ? { key: 'manual' } : { key: 'pre:skill', skill: e.name }
      const findings = await runMoment(look, S(), at)
      const label = manual ? 'manual' : e.skill === 'other' ? 'skill' : 'done'
      const where = manual ? '/lint' : `/${e.name}`
      const text = render(label, where, findings)
      // A skill cannot be refused: a hold is an instruction in its text to stop first (timing.ts pre:skill).
      const held = settle(manual ? 'manual' : 'pre:skill', findings).gate === 'hold'
      // /lint was asked for its result, found or not; before another skill a clean run needs no card (the skill's
      // text still carries the record).
      // Loaded by a Skill call: under that call. Typed by the person: under their message, matched by the skill's
      // name (a user row has no id, so the latest card of that name is drawn under each row naming it).
      const under = S().skillCalls?.[e.name] ?? `typed:${e.name.split(':').pop()}`
      if (manual || findings.length) await post(h, ports, memory, skillCard(text.split('\n')[0], findings, e.skill === 'ship' && held, isReview), under)
      const tailLine = manual
        ? '這是叫 /lint 時先跑的全部檢查。先把結果用一兩句話交代給使用者（沒有發現也說），再做使用者這次要求的事。'
        : isReview
          ? '這是 review 開始前、作者這一端跑的 lint 紀錄，照 review 的判定規則讀。'
          : e.skill === 'ship'
            ? held
              ? '有 error：停下，不要 commit；把上面的 error 回報給使用者。'
              : '沒有 error，可以繼續；warn 要在收尾報告裡提到。'
            : held
              ? `這是 /${e.name} 開始前跑的檢查。有 error：先把 error 交代給使用者，修好或問過他，再做這個 skill 的事。`
              : `這是 /${e.name} 開始前跑的檢查；warn 在做完時一起交代。`
      return { text: `## Lint 紀錄（baransu lint mod，這個版本）\n\n${text}\n\n${tailLine}` }
    },

    skillCalling(name: string, callId: string | undefined) {
      const calls = { ...(S().skillCalls ?? {}) }
      if (callId) calls[name] = callId
      else delete calls[name]
      S().skillCalls = calls
      save()
    },

    cardFor(callId: string): Card | undefined {
      return S().cards[callId]
    },

    agentCardsUnder(callId: string): readonly Card[] {
      const prefix = `${callId}#agent:`
      return Object.entries(S().cards).filter(([k]) => k.startsWith(prefix)).map(([, d]) => d)
    },

    async stopping(e): Promise<StopVerdict> {
      const config = await ports.config.load(h)
      if (!config) return { kind: 'stop' }
      const look = lookOf(ports, h, config)
      // What the person saw last: Opus 5.5 says its words in thinking, which last_assistant_message leaves out.
      const said = e.text.length >= S().textAfterTools.length ? e.text : S().textAfterTools
      const findings = await runMoment(look, S(), { key: 'pre:stop', text: said })
      // report-before-stop: work was done this turn and nothing was reported after the last tool.
      const rc = find(config, 'report-before-stop')
      if (rc && S().tools > 0) {
        const letters = (said.match(/\p{L}/gu) ?? []).length
        const han = (said.match(/\p{Script=Han}/gu) ?? []).length
        if (letters - han + 2 * han < 60) findings.push({ id: rc.id, severity: rc.severity === 'info' ? 'note' : rc.severity, ...(rc.severity === 'info' ? { quiet: true } : {}), text: `這一輪做了事，結束前卻沒交代現況。${rc.redo ?? reportHow(ports.whatNowSkill(h))}` })
      }
      if (!findings.length) return { kind: 'stop' }
      const s = settle('pre:stop', findings)
      const shown = render('stop', '', findings)
      // A check or retry holds once a turn, each by its own record (held, `stop|<id>`), not the host's
      // stop_hook_active: an error's hold must not use up the report's one ask (hypothesis lint-mod-state R4, found
      // 2026-11-03). Once held, it is shown on the card only — not asked again with another hold, not queued for the
      // next message (R5, found the same day: a report asked again at every error hold).
      const once = (f: Finding) => f.severity === 'check' || f.severity === 'retry'
      const heldBefore = (f: Finding) => S().held.some(p => p.key === `stop|${f.id}`)
      const fresh = findings.filter(f => once(f) && !heldBefore(f))
      const t0 = settle('pre:stop', findings.filter(f => !once(f) || !heldBefore(f)))
      // error holds up to STOP_HOLDS times a turn; check and retry hold once.
      const holds = S().stopHolds ?? 0
      const hold = (s.gate === 'hold' && holds < STOP_HOLDS) || fresh.length > 0
      if (hold) {
        if (s.gate === 'hold') S().stopHolds = holds + 1
        for (const f of fresh) S().held.push({ key: `stop|${f.id}`, step: S().steps.main ?? 0 })
        const t = told('stop', '', t0)
        save()
        if (t.redo) deliver(memory, h, t0.redo.some(f => f.id === rc?.id) ? ['report'] : ['retry'])
        await post(h, ports, memory, cardOf('結束這一輪前', findings, { kind: 'stop', title: '還不能結束，已請 Claude 接著做' }))
        return { kind: 'hold', reason: [...t.lines, ...(s.gate === 'hold' ? ['修好上面的 error 再結束這一輪。'] : [])].join('\n\n') || shown }
      }
      // It ends: what is left for the model waits for its next step.
      const gaveUp = s.gate === 'hold' ? `這一輪已經擋了 ${STOP_HOLDS} 次還沒過，放行；請你看一下` : undefined
      enqueue(memory, h, told('stop', '', { ...t0, line: [...t0.line, ...t0.fix, ...t0.redo], fix: [], redo: [] }).lines)
      // What was shown when the turn was held is not said again as it ends.
      const left = findings.filter(f => !(once(f) && heldBefore(f)))
      if (left.length || gaveUp) await post(h, ports, memory, cardOf('結束這一輪前', left, gaveUp ? { kind: 'warn', footer: gaveUp } : {}))
      return { kind: 'stop' }
    },

    async agentStarted(e) {
      // The Agent call that started it, so its card hangs under that call's row.
      if (e.callId) {
        const calls = { ...(S().agentCalls ?? {}), [e.agent]: e.callId }
        const ids = Object.keys(calls)
        for (const old of ids.slice(0, Math.max(0, ids.length - MAX_SPANS))) delete calls[old]
        S().agentCalls = calls
        save()
      }
      const config = await ports.config.load(h)
      if (!config || !wantsAround(config.checks, 'agent')) return
      const snap = await snapTree(lookOf(ports, h, config), await storeOf(h, ports, memory, config.root))
      const spans = { ...(S().spans ?? {}), [e.agent]: { agentType: e.agentType, entries: { ...snap.entries } } }
      const ids = Object.keys(spans)
      for (const old of ids.slice(0, Math.max(0, ids.length - MAX_SPANS))) delete spans[old]
      S().spans = spans
      save()
    },

    async agentStopped(e) {
      // The compaction runs as a subagent of no type: not an agent the person dispatched.
      if (!e.agentType) return
      // Take the snapshot synchronously, before any await, so a second end of the same agent finds it gone.
      const span = S().spans?.[e.agent]
      if (span) {
        const spans = { ...S().spans }
        delete spans[e.agent]
        S().spans = spans
        save()
      }
      const callId = S().agentCalls?.[e.agent]
      if (callId) {
        const calls = { ...S().agentCalls }
        delete calls[e.agent]
        S().agentCalls = calls
        save()
      }
      const config = await ports.config.load(h)
      if (!config) return
      const look = lookOf(ports, h, config)
      const findings = await runMoment(look, S(), { key: 'post:agent', agentType: e.agentType, text: e.text })
      if (span) {
        const snap: TreeSnap = { kind: 'tree', entries: span.entries }
        const store = await storeOf(h, ports, memory, config.root)
        const d = await diffTree(look, snap, store)
        const env = await aroundEnv(look, d.changed, treeBefore(look, snap), runWanted(config, 'around:agent'), store)
        findings.push(...(await runMoment(look, S(), { key: 'around:agent', agentType: e.agentType, changed: d.changed }, env)))
      }
      if (!findings.length) return
      const s = settle('post:agent', findings)
      enqueue(memory, h, told('agent', e.agentType, s).lines.map(l => `（subagent ${e.agentType} 結束後）${l}`))
      // Several agents of one Workflow share its call: each keeps its own card under it.
      await post(h, ports, memory, cardOf(`subagent 結束後 · ${e.agentType}`, findings, { kind: 'record' }), callId ? `${callId}#agent:${e.agent}` : undefined)
    },

    compacting<R>(e: { instructions: string }, proceed: (instructions: string) => Promise<R>, skipped: (r: R) => boolean, summary: (r: R) => string): Promise<R> {
      // Not async: what is owed is taken before any await, and written into the instructions so the summary
      // keeps it; a skipped compaction gives it back.
      const taken = memory.take(h, 'call')
      return compactAfterTake(h, ports, memory, taken, e.instructions, proceed, skipped, summary)
    },

    async fileChanged(e) {
      const config = await ports.config.load(h)
      if (!config || e.change === 'unlink') return
      const file = relTo(config.root, e.file)
      // Outside the root and git's own files are no change of the person's.
      if (/^([A-Za-z]:)?\//.test(file) || file.startsWith('.git/')) return
      // Claude's own write this turn is not a change made outside Claude.
      if ((S().touched ?? []).some(t => t.toLowerCase() === file.toLowerCase())) return
      const findings = await runMoment(lookOf(ports, h, config), S(), { key: 'post:file', files: [file] })
      const shown = findings.filter(f => f.id !== '' && !config.problems.includes(f))
      if (!shown.length) return
      const s = settle('post:file', shown)
      enqueue(memory, h, told('file', file, s).lines.map(l => `（${file} 在 Claude 之外被改了）${l}`))
      await post(h, ports, memory, cardOf(`Claude 之外改檔後 · ${file}`, shown))
    },
  }
}

/**
 * The mod's own object store for around snapshots: one bare git in the system's temp folder,
 * `baransu-lint.git`, shared by every session on the machine (its objects are named by their content, so two
 * sessions writing at once write the same thing), made the first time one is needed and named in
 * LintState.objects so a reload finds it again. Nothing goes into the project. Its old objects are pruned at
 * session start (sessionStarted). undefined when git cannot make one: around then has the changed paths only.
 */
async function storeOf<H>(h: H, ports: Ports<H>, memory: Memory<H>, root: string): Promise<Store | undefined> {
  const had = memory.s.objects
  if (had && (await ports.runner.probe(h, had)).kind === 'dir') return { dir: had }
  const dir = await storePath(h, ports)
  const there = (await ports.runner.probe(h, dir)).kind === 'dir'
  if (!there && (await ports.runner.run(h, ['git', 'init', '--bare', '--quiet', dir], { cwd: root, timeoutMs: 20000 })).exitCode !== 0) return undefined
  memory.s.objects = dir
  memory.save(h)
  return { dir }
}

/** Where the store is: `baransu-lint.git` in the system's temp folder (TEMP, TMP, TMPDIR, else /tmp). */
async function storePath<H>(h: H, ports: Ports<H>): Promise<string> {
  const tmp = (await ports.machine.env(h, 'TEMP')) ?? (await ports.machine.env(h, 'TMP')) ?? (await ports.machine.env(h, 'TMPDIR')) ?? '/tmp'
  return `${tmp.replace(/\\/g, '/').replace(/\/+$/, '')}/baransu-lint.git`
}

/** Whether a `run` check is due at an around timing (only then is LINT_BEFORE worked out). */
const runWanted = (config: Config, key: TimingKey) => config.checks.some(c => c.action.kind === 'run' && c.on.some(t => t.key === key))

// ================================================================ waits (after:<act>:<n>)

/**
 * An act just ran: every check waiting on it moves its deadline to now + its wait, and a wait is armed. An
 * older wait that wakes before the new deadline finds it moved and does nothing (one timer per act, none
 * cancelled: a reload re-arms from the stored deadlines alone).
 */
async function bump<H>(h: H, ports: Ports<H>, memory: Memory<H>, config: Config, acts: readonly ('edit' | 'bash' | 'commit' | 'push')[]) {
  const waits = config.checks.flatMap(c => c.on.filter(t => acts.some(a => t.key === `after:${a}`)).map(t => ({ c, t: t as { key: AfterKey; ms: number } })))
  if (!waits.length) return
  const now = await ports.clock.now(h)
  const timers = { ...(memory.s.timers ?? {}) }
  for (const { c, t } of waits) {
    // One deadline per check and timing: a check on after:edit:10m and after:bash:5m keeps two.
    timers[`${c.id}|${t.key}`] = { key: t.key, due: now + t.ms }
    ports.clock.after(h, t.ms, () => void wake(h, ports, memory).catch(() => {}))
  }
  memory.s.timers = timers
  memory.save(h)
}

/** Arm a wait for every stored deadline (a reload cancelled the old ones). */
async function rearm<H>(h: H, ports: Ports<H>, memory: Memory<H>) {
  const timers = Object.values(memory.s.timers ?? {})
  if (!timers.length) return
  const now = await ports.clock.now(h)
  for (const t of timers) ports.clock.after(h, Math.max(1000, t.due - now), () => void wake(h, ports, memory).catch(() => {}))
}

/**
 * A wait woke: take every deadline that has run out (synchronously, so two wakes never both run one), run
 * those checks, queue what the model should hear and show the card. The model is not woken: the lines reach
 * it with its next step.
 */
async function wake<H>(h: H, ports: Ports<H>, memory: Memory<H>) {
  const now = await ports.clock.now(h)
  const timers = { ...(memory.s.timers ?? {}) }
  const due = Object.entries(timers).filter(([, t]) => t.due <= now + 500)
  if (!due.length) return
  for (const [id] of due) delete timers[id]
  memory.s.timers = timers
  memory.save(h)
  const config = await ports.config.load(h)
  if (!config) return
  const ran = new Set(due.map(([k]) => k))
  for (const key of [...new Set(due.map(([, t]) => t.key))]) {
    const only: Config = { ...config, problems: [], checks: config.checks.filter(c => ran.has(`${c.id}|${key}`)) }
    const findings = await runMoment(lookOf(ports, h, only), memory.s, { key })
    if (!findings.length) continue
    enqueue(memory, h, told('after', key, settle(key, findings)).lines)
    await post(h, ports, memory, cardOf(`時間到 · ${key}`, findings))
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
    if (lang) await settleLanguage(h, ports, memory, lang)
    if (lang && S().languageFrom !== 'check' && S().languageFrom !== 'setting') {
      const han = (e.typed.match(/\p{Script=Han}/gu) ?? []).length
      const letters = (e.typed.match(/\p{L}/gu) ?? []).length
      if (letters) {
        S().userLanguage = han / letters > 0.2 ? '中文（照使用者用的字，繁體或簡體）' : 'English'
        S().languageFrom = 'guess'
      }
    }
    const notes: string[] = [...taken.queued]
    if (lang && lang.severity !== 'info') notes.push(...taken.slips.map(t => restateNote(lang, S().userLanguage, t)))
    const fix = find(config, 'correction-to-lint')
    if (fix && CORRECTION.test(e.typed)) {
      await post(h, ports, memory, cardOf('你的訊息', [{ id: fix.id, severity: 'note', quiet: true, text: '這像是在糾正，修完後會評估能不能寫成 lint' }]))
      if (fix.severity !== 'info') notes.push(`baransu lint（${fix.id}）：使用者在糾正你。先照他說的修好，再判斷這個錯能不能寫成檢查：能，就交給 /baransu:lint 新增（附上這次錯在哪、怎麼修、出錯的 commit）；不能，用一句話說明為什麼。${fix.message}`)
    }
    memory.save(h)
    const r = await proceed(notes)
    // The prompt did not enter (a hook or a settings hook below refused it): what it took is still owed.
    if (dropped(r)) taken.giveBack()
    // It entered with what it carried (a slash command's copy is delivered when its turn starts).
    else if (e.opensTurnNow && lang && lang.severity !== 'info' && taken.slips.length) deliver(memory, h, ['restate'])
    return r
  } catch (err) {
    // Whatever failed after the take, what was taken goes back to be delivered next time.
    taken.giveBack()
    throw err
  }
}

async function compactAfterTake<H, R>(
  h: H, ports: Ports<H>, memory: Memory<H>, taken: Taken, instructions: string,
  proceed: (instructions: string) => Promise<R>, skipped: (r: R) => boolean, summary: (r: R) => string,
): Promise<R> {
  let config: Config | null = null
  let carry = ''
  try {
    config = await ports.config.load(h)
    if (config) {
      const look = lookOf(ports, h, config)
      const pre = await runMoment(look, memory.s, { key: 'pre:compact', text: instructions })
      const lang = find(config, 'user-language')
      const owed = [
        ...taken.queued,
        ...(lang ? taken.slips.map(t => restateNote(lang, memory.s.userLanguage, t)) : []),
        ...told('compact', '', settle('pre:compact', pre)).lines,
      ]
      if (pre.length) await post(h, ports, memory, cardOf('壓縮 · 壓縮前', pre))
      if (owed.length) carry = `\n\n摘要裡要保留下面這些還沒做完的要求（baransu lint），壓縮後照做：\n${owed.map(o => `- ${o}`).join('\n')}`
    }
  } catch {
    // The compaction must go on whatever the checks did.
  }
  if (!carry) taken.giveBack()
  let r: R
  try {
    r = await proceed(instructions + carry)
  } catch (err) {
    taken.giveBack()
    throw err
  }
  if (skipped(r)) {
    taken.giveBack()
    return r
  }
  // The restates rode into the summary: delivered, so the model's answer to them is checked (R14).
  if (carry && taken.slips.length) deliver(memory, h, ['restate'])
  // post:compact: never throws past this point (the compaction already happened).
  try {
    if (config) {
      const postFindings = await runMoment(lookOf(ports, h, config), memory.s, { key: 'post:compact', text: summary(r) })
      if (postFindings.length) {
        enqueue(memory, h, told('compact', '壓縮後', settle('post:compact', postFindings)).lines)
        await post(h, ports, memory, cardOf('壓縮 · 壓縮後', postFindings))
      }
    }
  } catch {}
  return r
}

/**
 * Before, run, after. The pre half may refuse; once `proceed` has run nothing throws out of here (the hook's
 * `.catch` would hand the call on a second time and the notes and card of the first would be lost): the post
 * half catches its own failure and says so on the card.
 *
 *   no config        → giveBack; r = proceed(); count an edit (edit tool, or shell that writes files) if it ran clean
 *   restates owed    → card lines (retry) + notes; queued lines → notes
 *   first file change of a turn, nothing said yet → explain-before-edit at its level (pre:edit / pre:bash)
 *   pre:edit         → checks on the text it writes
 *   pre:bash         → checks on the command and on what it deletes / which worktrees it removes; the delete preview
 *   pre:commit/push  → the git checks (per sub-repo in a plain folder)
 *   settle every pre finding: hold → refuse; hold-once → refuse unless this actor held the same act in an
 *     earlier response this turn (held, keyed by actor | cwd | command, or file # text hash); else tell
 *   around snapshots (only when a check reads around:<act>); touched (only when a check reads post:file)
 *   r = await proceed(); o = outcome(r)
 *   !o.ran || o.isError → giveBack; touched removed
 *   counts: tools, textAfterTools, commands, editSeq; after:* deadlines moved
 *   post:edit / post:bash / post:commit|push and around:* → settle (fix, redo, line, card)
 */
async function callAfterTake<H, R>(
  h: H, ports: Ports<H>, memory: Memory<H>, taken: Taken, at: { editSeq: number; step: number },
  e: ToolCallEvent, proceed: () => Promise<R>, outcome: (r: R) => Outcome, answerNote?: string,
): Promise<ToolVerdict<R>> {
  const S = () => memory.s
  const save = () => memory.save(h)
  const main = !e.agent
  const isEdit = e.kind === 'edit'
  const isBash = e.kind === 'shell'
  const command = e.kind === 'shell' ? e.command : ''
  let config: Config | null
  // ---------------------------------------------------------------- before
  const context: string[] = answerNote ? [answerNote, ...taken.queued] : [...taken.queued]
  const inline: Finding[] = []
  const redo: RedoKind[] = []
  let gitWrite = false
  let file = ''
  let editSnap: Awaited<ReturnType<typeof snapEdit>> | undefined
  let treeSnap: TreeSnap | undefined
  let headSnap: HeadSnap | undefined
  let store: Store | undefined
  let touchedFile: string | undefined
  let previewCard: (c: Card) => Card = c => c
  try {
    config = await ports.config.load(h)
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
    const look = lookOf(ports, h, config)
    // Where this call's shell is: the session's own directory, read inside the hook (a subagent's own).
    const cwdNow = e.cwd || root
    file = e.kind === 'edit' ? relTo(root, e.file) : ''
    const insideRepo = file !== '' && !/^([A-Za-z]:)?\//.test(file)
    // A refused call still hands the model what it is owed: the notes ride on the refusal.
    const refuse = (d: Card, deny: string): ToolVerdict<R> => {
      keepCard(S(), e.id, { ...d, replace: true })
      save()
      deliver(memory, h, redo)
      return { kind: 'deny', reason: [deny, ...context].join('\n\n') }
    }

    // Blocks written in the wrong language since the last call: redo each in the user's language.
    const lang = find(config, 'user-language')
    // At info the slip is the person's card only; at any other level the model restates it.
    const asks = !!lang && lang.severity !== 'info'
    if (asks && taken.slips.length) redo.push('restate')
    if (lang)
      for (const t of taken.slips) {
        inline.push(asks
          ? { id: lang.id, severity: 'retry', text: `剛才那段寫成英文了（「${slipHead(t)}」）→ 重新：用你的語言再說一次` }
          : { id: lang.id, severity: 'note', quiet: true, text: `剛才那段寫成英文了（「${slipHead(t)}」）` })
        if (asks) context.push(restateNote(lang, S().userLanguage, t))
      }

    const pre: Finding[] = []
    // Words before acting: the first file change of a turn — an edit, or a command that writes a file — should
    // follow a word on how it will be done. A read-only look is no act and leaves the turn's flag as it is.
    let explain: Check | undefined
    if (main && !S().spoke && (isEdit || (isBash && writesFiles(command)))) {
      explain = find(config, 'explain-before-edit')
      S().spoke = true
      if (explain) {
        const how = explain.redo ?? '改檔前先用一兩句話說要怎麼動手：改哪些檔、怎麼改，然後直接繼續，不等他確認；只有真的不確定他要什麼時才停下來問'
        pre.push({ id: explain.id, severity: explain.severity === 'info' ? 'note' : explain.severity, ...(explain.severity === 'info' ? { quiet: true } : {}), text: `這一輪還沒說要怎麼動手，就先改檔了。${how}` })
      }
    }

    // Before an edit: checks on what it writes.
    if (e.kind === 'edit' && insideRepo) pre.push(...(await runMoment(look, S(), { key: 'pre:edit', file, text: e.text })))

    // Before any shell command: checks that read the command line, its deletes and the worktrees it removes.
    let preview: PreviewLine[] = []
    if (e.kind === 'shell') {
      pre.push(...(await runMoment(look, S(), { key: 'pre:bash', command, deletes: deletedPaths(command, cwdNow, root), worktrees: removedWorktrees(command) })))
      // The delete preview: what a command that deletes, moves or discards will touch.
      const dp = find(config, 'destructive-preview')
      if (dp) {
        preview = await destructivePreview(ports.runner, h, root, command, cwdNow)
        if (preview.length) pre.push({ id: dp.id, severity: dp.severity === 'info' ? 'note' : dp.severity, ...(dp.severity === 'info' ? { quiet: true } : {}), text: `這個指令會動到\n${preview.map(t => `  ${t.text}`).join('\n')}${dp.message ? `\n${dp.message}` : ''}` })
      }
    }

    // Before a git commit or push. An ordinary project: once, at the root, whenever isGitWrite reads one —
    // unless a write lands outside the root (`git -C <other repo> commit`, `cd <other> && git commit`): then, as in
    // a plain folder, commitDirs says where each write runs and each is checked in the repo it commits in; a write
    // whose repo cannot be told gets a warning that its checks did not run.
    const dirs = isBash ? commitDirs(command, cwdNow) : []
    const rootDir = root.replace(/\\/g, '/').replace(/\/+$/, '').toLowerCase()
    const outsideRoot = (d: string) => !`${d.toLowerCase()}/`.startsWith(`${rootDir}/`)
    const plainWrites = !config.git ? dirs : dirs.some(d => d !== null && outsideRoot(d)) ? dirs.map(d => d ?? root) : []
    gitWrite = isBash && (config.git ? isGitWrite(command) : plainWrites.length > 0)
    const writes = gitWrites(command)
    const pushes = writes.includes('push')
    const commits = writes.includes('commit')
    const gitAt = (): Occurrence => ({ key: commits || !pushes ? 'pre:commit' : 'pre:push', command, push: pushes ? { refs: pushRefs(command) } : null })
    if (gitWrite) {
      let findings: Finding[]
      if (config.git && !plainWrites.length) findings = await runMoment(look, S(), gitAt())
      else {
        findings = []
        const ran = '這次 commit／push 會照常執行，但它的 lint 檢查沒有跑'
        const general = new Set([
          ...config.problems.map(p => p.id),
          ...config.checks.filter(c => builtinOf(c) === 'built-before-commit').map(c => c.id),
        ])
        for (const dir of plainWrites) {
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
          const tag = plainWrites.length > 1 && there.repo?.rel ? `[${there.repo.rel}] ` : ''
          findings.push(...(await runMoment(there, S(), gitAt())).map(f => (tag && f.id && !general.has(f.id) ? { ...f, text: tag + f.text } : f)))
        }
        const seen = new Set<string>()
        findings = findings.filter(f => !seen.has(`${f.id}|${f.text}`) && !!seen.add(`${f.id}|${f.text}`))
      }
      pre.push(...findings)
    }

    // Settle everything before the act once: every pre row is the same row (timing.ts PRE).
    const key: TimingKey = isEdit ? 'pre:edit' : gitWrite ? 'pre:commit' : 'pre:bash'
    const s = settle(key, pre)
    const label = isEdit ? `改檔前 · ${file}` : gitWrite ? (pushes && !commits ? 'push 前' : 'commit 前') : '指令前'
    const footer = gitWrite ? '修好 error 再 commit／push' : isEdit ? '照上面改好要寫的內容再寫' : '照上面改寫這個指令再跑'
    // On the card the delete preview is its path list; a preview line that names no path stays a line.
    const previewId = find(config!, 'destructive-preview')?.id
    const rows = preview.flatMap(t => (t.row ? [t.row] : []))
    const withPreview = (lines: Finding[]) => (preview.length
      ? { lines: [...lines.filter(f => f.id !== previewId), ...preview.filter(t => !t.row).map(t => ({ id: '', severity: 'note' as const, text: t.text }))], ...(rows.length ? { paths: rows } : {}) }
      : { lines })
    // A card made after the act carries the preview as its path list too.
    previewCard = c => (c.lines.some(f => f.id === previewId) ? { ...c, ...withPreview(c.lines) } : c)
    if (s.gate === 'hold') {
      if (s.redo.some(f => f.id === explain?.id)) redo.push('explain')
      // An explain-before-edit at error holds every file change until the model has said how: the turn has
      // still said nothing.
      if (explain?.severity === 'error') S().spoke = false
      const card = summarize(label, pre) ?? { kind: 'error' as const, meta: `lint · ${label}`, lines: pre }
      return refuse({ ...card, ...withPreview(card.lines), title: gitWrite ? (pushes && !commits ? '沒有 push' : '沒有 commit') : '沒有執行', footer }, `${render(isEdit ? 'edit' : gitWrite ? 'commit' : 'bash', isEdit ? file : '', pre)}\n${footer}。`)
    }
    // What a hold-once showed when it held: once the act passes, neither the person nor the model hears it again.
    let shownOnce: Finding[] = []
    if (s.gate === 'hold-once') {
      // The same act by the same actor in a later response of this turn passes: it has read the list.
      const heldKey = `${e.agent ?? 'main'}|${isEdit ? `edit|${file}#${hash(e.kind === 'edit' ? e.text : '')}` : `${e.kind === 'shell' ? e.shell : ''}|${cwdNow}|${command}`}`
      const seen = S().held.find(p => p.key === heldKey)
      if (!(seen && seen.step < at.step)) {
        if (!seen) S().held.push({ key: heldKey, step: at.step })
        if (s.redo.some(f => f.id === explain?.id)) redo.push('explain')
        const once = pre.filter(f => f.severity === 'check' || f.id === previewId)
        const onlyPreview = preview.length > 0 && once.every(f => f.id === previewId)
        return refuse(
          { kind: 'check', title: onlyPreview ? '先確認會動到的東西' : '先確認一次', meta: onlyPreview ? 'lint · 刪除前預覽' : `lint · ${label}`, ...withPreview(pre), footer: `確認沒錯，再下一次同樣的${isEdit ? '動作' : '指令'}就會執行` },
          `${render(isEdit ? 'edit' : gitWrite ? 'commit' : 'bash', isEdit ? file : '', pre)}\n確認沒錯，下一次回應再送一次同樣的動作就會執行。`,
        )
      }
      shownOnce = pre.filter(f => f.severity === 'check' || f.id === previewId)
    }
    // It goes on: the model hears each finding as its level says there.
    for (const f of s.redo) {
      if (f.id === explain?.id) {
        redo.push('explain')
        inline.push({ ...f, severity: 'retry', text: '這一輪還沒說要怎麼動手，就先改檔了 → 重新：先說要怎麼動手' })
        context.push(`baransu lint（${f.id}，重新）：${f.text}。`)
      } else {
        redo.push('retry')
        inline.push(f)
        context.push(`baransu lint（${f.id}，重新）：${f.text}`)
      }
    }
    const plain = s.line.filter(f => !s.redo.includes(f) && !shownOnce.includes(f))
    inline.push(...plain, ...s.card.filter(f => f.quiet && !plain.includes(f) && !shownOnce.includes(f)))
    if (plain.length) context.push(render(isEdit ? 'edit' : gitWrite ? 'commit' : 'bash', isEdit ? file : '', plain))

    // Snapshots for around:<act>, and Claude's own write for post:file — both only when a check reads them.
    const aroundEdit = isEdit && insideRepo && wantsAround(config.checks, 'edit')
    const aroundBash = isBash && wantsAround(config.checks, 'bash')
    if (aroundEdit || aroundBash) store = await storeOf(h, ports, memory, root)
    if (aroundEdit) editSnap = await snapEdit(look, file, store)
    if (aroundBash) treeSnap = await snapTree(look, store)
    if (gitWrite && wantsAround(config.checks, 'commit')) headSnap = await snapHead(look)
    if (isEdit && insideRepo && config.checks.some(c => c.on.some(t => t.key === 'post:file'))) {
      touchedFile = file
      S().touched = [...(S().touched ?? []), file].slice(-500)
      save()
    }
  } catch (err) {
    // Whatever failed before the act, what was taken goes back to be delivered next time.
    taken.giveBack()
    throw err
  }

  // ---------------------------------------------------------------- the act
  let result: R
  try {
    result = await proceed()
  } catch (err) {
    taken.giveBack()
    if (touchedFile) S().touched = (S().touched ?? []).filter(t => t !== touchedFile)
    save()
    throw err
  }

  // ---------------------------------------------------------------- after (never throws)
  const o = outcome(result)
  const afterLines: string[] = []
  const afterFound = new Set<Finding>()
  let hadAfter = false
  try {
    // A call refused further down, or a run that failed, carries no notes: what was taken goes back.
    if (!o.ran || o.isError) {
      taken.giveBack()
      if (touchedFile) S().touched = (S().touched ?? []).filter(t => t !== touchedFile)
    } else deliver(memory, h, redo)
    // Work done this turn, and the text after it starts over; a read-only call (git status, ls) does neither.
    if (main && o.ran && !o.isReadOnly) {
      S().tools++
      S().textAfterTools = ''
    }
    // While /lint runs, a command may have rewritten the rules: the next load reads them again.
    if (isBash && main && o.ran && S().lintTurn) ports.config.reload()
    if (isBash && o.ran) {
      // A shell command that writes files is an edit, not a check run after one. A background command
      // has only started, so it is not a run; a command counts against the edit count it started at.
      if (writesFiles(command)) S().editSeq++
      else if (!(e.kind === 'shell' && e.background)) S().commands.push({ cmd: command, ok: o.isError !== true, seq: at.editSeq })
    }
    if (isEdit && o.ran && !o.isError) S().editSeq++
    save()

    const look = lookOf(ports, h, config)
    const insideRepo = file !== '' && !/^([A-Za-z]:)?\//.test(file)
    const post: Finding[] = []
    let postKey: TimingKey = 'post:bash'
    if (isEdit && insideRepo && o.ran && !o.isError) {
      postKey = 'post:edit'
      // An edit to a rule file under .claude/lint drops what the source kept: this moment reads the
      // checks again. The config source alone knows which files are its own.
      const fresh = ports.config.edited(h, file) ? ((await ports.config.load(h)) ?? config) : config
      const freshLook = { ...look, config: fresh }
      post.push(...(await runMoment(freshLook, S(), { key: 'post:edit', file })).filter(f => f.severity !== 'note' || f.quiet))
      if (editSnap?.kind === 'edit') {
        const after = await ports.runner.read(h, `${config.root}/${file}`)
        const added = addedLines(editSnap.text, after)
        const before = editSnap.hash
        const env = await aroundEnv(freshLook, [file], async () => before, runWanted(fresh, 'around:edit'), store)
        post.push(...(await runMoment(freshLook, S(), { key: 'around:edit', file, added }, env)))
      } else if (editSnap?.kind === 'too-big') post.push({ id: 'around', severity: 'note', quiet: true, text: `${file} 超過 1 MB，around:edit 沒有檢查` })
    }
    if (isBash && o.ran) {
      post.push(...(await runMoment(look, S(), { key: 'post:bash', command, output: o.output ?? '', failed: o.isError })))
      if (treeSnap) {
        const d = await diffTree(look, treeSnap, store)
        const env = await aroundEnv(look, d.changed, treeBefore(look, treeSnap), runWanted(config, 'around:bash'), store)
        post.push(...(await runMoment(look, S(), { key: 'around:bash', command, changed: d.changed }, env)))
      }
    }
    const gitPost: Finding[] = []
    if (gitWrite && o.ran && !o.isError) {
      const writes = gitWrites(command)
      const pushes = writes.includes('push')
      const commits = writes.includes('commit')
      const git = { command, push: pushes ? { refs: pushRefs(command) } : null }
      postKey = commits || !pushes ? 'post:commit' : 'post:push'
      const sideKey = (side: 'post' | 'around') => (commits || !pushes ? `${side}:commit` : `${side}:push`) as 'post:commit'
      if (config.checks.some(c => c.on.some(t => t.key === 'post:commit' || t.key === 'post:push'))) {
        const log = await ports.runner.run(h, ['git', 'log', '-1', '--format=%an <%ae>%n%B'], { cwd: config.root, timeoutMs: 10000 })
        gitPost.push(...(await runMoment(look, S(), { key: sideKey('post'), ...git, record: `${String(log.stdout).trim()}\n${o.output ?? ''}` })))
      }
      if (headSnap) {
        const d = await diffHead(look, headSnap)
        const env = await aroundEnv(look, d.changed, headBefore(look, headSnap), runWanted(config, 'around:commit'), undefined)
        if (commits) gitPost.push(...(await runMoment(look, S(), { key: 'around:commit', ...git, commits: d.commits, changed: d.changed }, env)))
      }
    }
    // What the checks after the act found reaches the model whenever the act ran — a failed command's output is
    // exactly what post:bash reads — even when what was taken before it goes back.
    for (const [k, found] of [[postKey, post], [gitPost.length ? (gitWrites(command).includes('commit') ? 'post:commit' : 'post:push') : postKey, gitPost]] as const) {
      if (!found.length) continue
      const s = settle(k, found)
      const t = told(isEdit ? 'edit' : k.endsWith('commit') || k.endsWith('push') ? 'commit' : 'bash', isEdit ? file : '', s, isEdit ? '修好 error；warn 判斷要不要改。' : '')
      for (const f of s.card.filter(f => f.severity !== 'note' || f.quiet)) {
        inline.push(f)
        afterFound.add(f)
      }
      afterLines.push(...t.lines)
      if (t.redo) deliver(memory, h, ['retry'])
      hadAfter = true
    }

    // The waits after an act start over (after:<act>:<n>).
    if (o.ran && !o.isError) {
      // A git write is a command too: after:bash moves with it, and after:commit / after:push.
      const acts = isEdit ? (['edit'] as const) : (['bash', ...(gitWrite ? gitWrites(command) : [])] as const)
      await bump(h, ports, memory, config, acts)
    }
  } catch {
    inline.push({ id: 'lint', severity: 'note', quiet: true, text: '動作之後的檢查沒有跑完' })
  }

  save()
  if (inline.length && o.ran) {
    const w = gitWrites(command)
    const act = isEdit ? '改檔' : gitWrite ? (w.includes('push') && !w.includes('commit') ? 'push ' : 'commit ') : '指令'
    const side = hadAfter ? (inline.length > afterCount() ? '前後' : '後') : '前'
    const d = summarize(`${act}${side}${isEdit ? ` · ${file}` : ''}`, inline, { edited: isEdit })
    keepCard(S(), e.id, previewCard(d ?? { kind: 'warn', meta: 'lint', lines: inline }))
    save()
  }
  const notes = [...(o.ran && !o.isError ? context : []), ...(o.ran ? afterLines : [])]
  return { kind: 'ran', result, notes }

  function afterCount() {
    return inline.filter(f => afterFound.has(f)).length
  }
}

