// The engine's public surface. Adapters and util import from here only; nothing in engine/ imports outward, except types from the plugin's own contract (types/index.d.ts), erased at run time.

export { createEngine } from './engine'
export { readCheck } from './check'
export { resolveSets } from './sets'
export { configFromFiles, CONFIG, DEFAULTS, type LintSettings } from './folder'
export type { Engine, Lint, Ports, ConfigSource, Runner, RunResult, PathProbe, StateStore, Notify, RuleConverter, Clock } from './ports'
export type * from './types'
