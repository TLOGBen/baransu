import type { Register } from 'claude-code'
import { lintTurnStep, register as lint } from './adapters/claude-code/hooks'

// The plugin's one hooks module (hooks.json → main.ts). A part hooks the events only it reads in its own
// register; turn.step, which the host accepts only as a literal async generator, is registered here around
// the part's handler. Unchanged from 8.39 except the import path.
export const register: Register = (on, options) => {
  lint(on, options)
  on('turn.step', async function* ($: any, e: any, next: any) {
    return yield* lintTurnStep($, e, next)
  } as any)
}
