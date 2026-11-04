// The one engine of this module load, built at module scope, so every dispatch shares its memory; a reload builds
// a new one, which reads `$.state` back. Its own file so the hooks and the view both reach it by import (the host
// lets `$` go only to a function declared at a file's top or imported from the module's own files).

import { createEngine, type Lint } from '../../engine'
import { LANGUAGES } from '../../util/languages'
import { hostConfig } from './config'
import { hostMachine } from './machine'
import { hostClock, hostOf, hostRunner, hostState, whatNowSkill, type Dollar, type Host } from './ports'
import { hostView } from './view/port'

export const engine = createEngine<Host>({
  config: hostConfig(), runner: hostRunner, state: hostState, view: hostView, clock: hostClock, whatNowSkill, machine: hostMachine, languages: LANGUAGES,
  languageSetting: h => h.language(),
})

/** The engine, ready, for this dispatch's `$`. */
export async function lintOf($: Dollar): Promise<Lint<Host>> {
  return engine.ready(hostOf($))
}
