# technical-writing — docs, technical articles, PR bodies, commit messages

Read this file, together with `writing-principles.md`, whenever the text is technical: a README, a doc page, an RFC or design note, a technical article or blog post, an answer that explains code, a PR description, or a commit message. `/wrap` reads the commit-message section when it writes its message. `writing-principles.md` still owns the anti-AI-voice catalog; this file adds the structure and sentence rules technical text needs on top of it.

The aim: a tired engineer understands it on the first read.

## Base rules

- Cut every word that does no work. Use the short, everyday word.
- Write the real symbol, file, flag or command name in code font, never a synonym or a description of it.
- Use the words a developer would say out loud. Invent no jargon; define a named pattern the first time it appears.
- Be specific: not 「schema 變動可能造成問題」 but 「欄位改名會讓 build 失敗」.
- When a rule below makes a sentence worse, fix the sentence another way or leave it alone.

## Pick the mode first

One document, one mode. When a piece needs two, split it and link the parts.

| Mode | Reader wants | Write |
|---|---|---|
| Tutorial | to learn by doing | Say what they will build. Every step gives a visible result, and say what they should see. Explanation gets one clause and a link. |
| How-to | to reach a goal | Steps only, assuming competence; forks allowed. Title it by the task. |
| Reference | to look a fact up | Describe only: dry, complete, sure. Mirror the structure of the thing described. |
| Explanation | to understand why | One bounded topic: context, design decisions, history, constraints, alternatives. The only mode where opinion belongs. |

A technical article is usually Explanation; one that walks the reader through doing something is a Tutorial or How-to and follows those rows.

## Sentences

- Address the reader directly (en "you", zh 「你」, or an imperative with no subject), present tense.
- Name who does what. Passive only when the actor is unknown or beside the point.
- Instructions are commands, one per sentence. The condition or warning comes before the step it guards; the common case comes first.
- One thought per sentence. Split an instruction past about 20 words (zh about 40 characters) and any other sentence past about 25 words (zh about 50 characters). Keep a long sentence that carries one thought.
- Never 「簡單」「只要」「輕鬆」, "simply", "easy", "quickly" in a procedure, and no "please".
- Do not announce what you are about to say. Do not start consecutive sentences the same way.
- Every 「它」「這」「此」, "it", "this", "they" points at one obvious noun; never at a whole clause.
- Call each thing by one name everywhere, and give each word one meaning.
- Link text says where the link goes.
- Headings state the point, in sentence case for en. One top-level heading per page, no skipped levels.
- Numbered lists for sequences, bullets for the rest. A complete sentence introduces a list; its items are parallel.
- Code, paths, flags and commands in code font; UI labels in bold.

English only, so text survives non-native readers and translation: keep "only" and "not" next to the word they change; break up long noun strings; keep "the", "a" and "that"; say which parts "and" or "or" joins; no semicolons, slashes, "(s)", Latin abbreviations or idioms; text in parentheses is a full grammatical unit.

## Claims in technical text

- Every count, list or tree the text states is true at the commit that lands it. When a command regenerates it, give the command.
- Write real paths, not placeholders, unless the reader must substitute one, and then say so.

## PR descriptions

Every section above except the mode table applies. A PR body is a briefing a reviewer reads in under a minute: why, what changed, what it risks, how it was verified. Do not paste run logs, SHA lists or metric tables into it; link them.

## Commit messages

The repo's own history decides the format and the language (`/wrap` INV-8); these rules govern the words inside that format.

- The subject names the outcome the commit ships, in the repo's form: what now works, what is fixed, what changed for a user. Never the mechanics ("update files", "apply changes", 「收尾」).
- The subject is one thought. When the repo's subjects carry a reason after a dash or a clause, give the concrete cause and its effect, as specific as the sentence rules above require.
- A body, when the change needs one, answers what the subject cannot: why, what was considered and rejected, what a reader of `git log` must know before touching this again. Wrap it as the repo's history does.
- Name files, symbols, flags and versions by their real names.
