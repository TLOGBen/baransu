// The engine's View port on Claude Code. A card with a call is already kept under it: this asks the host to draw
// that row again. A card with no call is said as a plain row, where any surface shows it; nothing is kept to stay
// on screen (purpose over display, user 2026-11-04).

import { cardText, type View } from '../../../engine'
import type { Host } from '../ports'

export const hostView: View<Host> = {
  async show(h, card, at) {
    if (at) {
      try {
        h.invalidate()
      } catch {}
      return
    }
    try {
      await h.append(cardText(card))
    } catch {}
  },
}
