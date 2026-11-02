// The lint mod's session state, kept in $.state so a reload of the mod does not lose it.
export type LintFinding = { id: string; severity: 'error' | 'warn' | 'redo' | 'note'; text: string }
// A card drawn under a tool call: what happened, which moment, the findings, what to do next.
export type LintCard = { kind: 'hold' | 'error' | 'warn' | 'redo'; title?: string; meta: string; lines: LintFinding[]; footer?: string; replace?: boolean }
export type LintState = {
  editSeq: number
  reviewedAt: number
  // A /review that started at this edit count; it counts once its turn ends with an answer.
  reviewPending?: number
  commands: { cmd: string; ok: boolean; seq: number }[]
  spoke: boolean
  userLanguage?: string
  // Delete previews shown: the key, and the model response (step) that was held.
  previewed: { key: string; step: number }[]
  // Model responses so far, per actor ('main' or a subagent's id).
  steps: Record<string, number>
  slips: string[]
  // What a slash command's message carried, removed from what is owed once that message opens a turn.
  offered?: { slips: string[]; report?: string }
  tools: number
  textAfterTools: string
  pendingReport?: string
  gitFacts?: string
  cards: Record<string, LintCard>
}

// The status line's own readings: what only a model response carries, and a counter that redraws the line.
export type StatuslineState = {
  // The effort the last main-loop response asked for (turn.step's effort).
  effort?: string
  // Cache-read tokens over all input tokens of the last main-loop response, 0 to 100.
  cache?: number
  // Bumped when the session's usage moved (session.measure), so the line redraws.
  tick: number
}

declare module 'claude-code' {
  interface PluginState {
    baransu: { lint: LintState; statusline: StatuslineState }
  }
}
