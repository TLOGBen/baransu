// The lint mod's session state, kept in $.state so a reload of the mod does not lose it.
// quiet: drawn on the card for the person, never sent to the model (a scope's skip note, a cut list).
export type LintFinding = { id: string; severity: 'error' | 'check' | 'warn' | 'retry' | 'note'; text: string; quiet?: boolean }
// A card drawn under a tool call: what happened, which moment, the findings, what to do next.
// 'answer' (lint-scope sketch): the result of checking the model's answer to a 重新 — drawn for the person only.
export type LintCard = { kind: 'check' | 'error' | 'warn' | 'retry' | 'answer'; title?: string; meta: string; lines: LintFinding[]; footer?: string; replace?: boolean }
export type LintState = {
  editSeq: number
  reviewedAt: number
  // A /review that started at this edit count; it counts once its turn ends with an answer.
  reviewPending?: number
  commands: { cmd: string; ok: boolean; seq: number }[]
  spoke: boolean
  userLanguage?: string
  // Acts held once at a pre timing (`check` level, the delete preview): the key, and the model response (step)
  // that was held. The same key passes in a later response of the same actor. Cleared each turn.
  held: { key: string; step: number }[]
  // Model responses so far, per actor ('main' or a subagent's id).
  steps: Record<string, number>
  slips: string[]
  // What a slash command's message carried, removed from what is owed once that message opens a turn.
  offered?: { slips: string[] }
  tools: number
  textAfterTools: string
  gitFacts?: string
  cards: Record<string, LintCard>
  // 重新 requests delivered and not yet answered (lint-scope sketch; Answering in hooks/engine/scope/types.ts).
  // Taken in replyAppended, with the save, before its first await.
  answering?: { id: number; kinds: ('restate' | 'explain' | 'report' | 'retry')[]; step: number }[]
  // The next Answering id.
  answerSeq?: number
  // The check of an answer to a 重新, waiting for the next main-loop call's row to be drawn on.
  answerCard?: LintCard
  // Lines for the model that no event could carry when they were found (a stop or a subagent's end that
  // passed, a file changed outside Claude, a wait that ran out): taken by the next main-loop call or prompt,
  // given back if that does not go through. At most 20, oldest dropped.
  queued?: string[]
  // Files Claude itself wrote this turn (root-relative), so post:file sees only changes made outside Claude.
  // Recorded before the write goes on, removed if it fails; cleared each turn.
  touched?: string[]
  // Times this turn was held at pre:stop by an error (at most STOP_HOLDS). Cleared each turn.
  stopHolds?: number
  // around:agent snapshots, by subagent id: each path git status listed at its start, with its content hash.
  // At most MAX_SPANS; taken (removed) synchronously when the subagent ends.
  spans?: Record<string, { agentType: string; entries: Record<string, string> }>
  // The mod's own object store for around snapshots: a bare git in the system's temp folder (engine.ts storeOf),
  // made the first time a session needs it. Nothing about it is in the project.
  objects?: string
  // /lint ran this turn: the rules may change through its commands, so each main-loop command and the turn's end
  // read them again. Cleared when the turn ends.
  lintTurn?: boolean
  // after:<act>:<wait> deadlines, by check id and timing (`<id>|<key>`): when the wait runs out (ms since the epoch) and its timing.
  // Moved later by every such act; taken synchronously when it runs out. Re-armed when the mod loads.
  timers?: Record<string, { key: 'after:edit' | 'after:bash' | 'after:commit' | 'after:push'; due: number }>
}

declare module 'claude-code' {
  interface PluginState {
    baransu: { lint: LintState }
  }
}
