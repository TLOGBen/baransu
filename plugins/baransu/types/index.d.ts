// The lint mod's session state, kept in $.state so a reload of the mod does not lose it.
export type LintState = {
  editSeq: number
  reviewedAt: number
  commands: { cmd: string; ok: boolean; seq: number }[]
  spoke: boolean
  userLanguage?: string
  previewed: string[]
  slips: string[]
  tools: number
  textAfterTools: string
  pendingReport?: string
  cwd?: string
  psCwd?: string
}

declare module 'claude-code' {
  interface PluginState {
    baransu: { lint: LintState }
  }
}
