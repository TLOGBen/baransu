import type { Register } from 'claude-code'
import { lintTurnStep, register as lint } from './lint'

// The plugin's one hooks module. A part hooks the events only it reads in its own register; turn.step,
// which the engine accepts only as a literal async generator, is registered here around the part's handler.
export const register: Register = (on, options) => {
  lint(on, options)
  on('turn.step', async function* ($: any, e: any, next: any) {
    return yield* lintTurnStep($, e, next)
  } as any)
}
