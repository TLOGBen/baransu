// The languages the imports relation knows. Adding one: a file beside these, a line here. Nothing else.

import type { Language } from '../../engine/ports'
import { csharp } from './csharp'
import { java } from './java'
import { python } from './python'
import { rust } from './rust'
import { typescript } from './typescript'

/** Two languages must not share an extension (relations.ts languageOf picks by extension). */
export const LANGUAGES: readonly Language[] = [typescript, python, csharp, java, rust]
