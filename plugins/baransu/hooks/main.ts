import type { Register } from 'claude-code'
import { lintTurnStep, register as lint } from './lint'
import { register as statusline, statuslineTurnStep } from './statusline'

// The plugin's one hooks module: the lint gate and the status line.
// A plugin hooks each event once, so the one event both parts read, turn.step, is registered here:
// the lint gate's step runs first and its `next` is the status line's.
export const register: Register = (on, options) => {
  lint(on, options)
  statusline(on, options)
  on('turn.step', async function* ($: any, e: any, next: any) {
    return yield* lintTurnStep($, e, (x: any) => statuslineTurnStep($, x, next))
  } as any)
}
