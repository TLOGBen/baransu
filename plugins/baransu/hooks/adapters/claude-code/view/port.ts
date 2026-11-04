// The engine's View port on Claude Code. The engine has already kept the card (on its call, or in the band);
// this asks the host to draw again, and writes a card with no call as a plain row too. The band above the prompt
// is drawn on the terminal and desktop only, and a survey holding it hides it (the hook yields), so the row is what
// a phone, an editor, or a band under a survey still shows (user 2026-11-04: both, rather than a card unseen).

import { cardText, type View } from '../../../engine'
import type { Host } from '../ports'

export const hostView: View<Host> = {
  async show(h, card, at) {
    try {
      h.invalidate()
    } catch {}
    if (at) return
    try {
      await h.append(cardText(card))
    } catch {}
  },
}
