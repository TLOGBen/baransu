// The Machine port on Claude Code. `$` exposes no platform, and `$.env.get` reads only names spelled in this
// module's source, so a check's `env:<NAME>` cannot be read through it: the engine's runnerMachine asks the
// machine itself through `$.process.run` (hostRunner), once per module load.

import { runnerMachine } from '../../engine/scope/machine'
import type { Host } from './ports'
import { hostRunner } from './ports'

export const hostMachine = runnerMachine<Host>(hostRunner)
