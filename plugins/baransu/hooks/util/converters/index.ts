// Converters by name. A new format is one file beside toml.ts and one line here; nothing else changes.

import type { RuleConverter } from '../../engine'
import { toml } from './toml'

const BY_NAME: Readonly<Record<string, RuleConverter>> = { [toml.name]: toml }

/** undefined for a name no converter has; the config source turns that into a problem finding. */
export function converterNamed(name: string): RuleConverter | undefined {
  return Object.hasOwn(BY_NAME, name) ? BY_NAME[name] : undefined
}
