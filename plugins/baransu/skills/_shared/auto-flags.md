# auto-flags — every flag is also a decision the skill makes

A flag is a shortcut for the user, never the only way in. Each flag a baransu skill takes has a trigger written beside it in that skill: the observable situation in which the skill turns it on by itself.

- **The user's word wins, both ways.** A flag the user passes is on. A flag the user refuses（「不要 full」「不用存」「別用代理」）is off, whatever the trigger says.
- **Otherwise the trigger decides.** The skill reads the trigger against what it can observe — the request's words, the target, the repo, a failed fetch — and turns the flag on when it holds. A trigger it cannot observe leaves the flag off.
- **Say it once, when it turns on.** The moment the skill turns a flag on by itself, it says which and why, in one line: 「自動開啟 --full：改動會寫入資料」 — folded into the skill's own status line when it has one. A trigger seen before work starts is said in the first status line, where the user can still refuse it.
- **A setting has a default, not a trigger.** A flag that carries a value (a model, an effort) keeps the session's value unless its skill writes a trigger for changing it.
- **A guard outranks a trigger.** A flag that sends data off this machine, or changes something outside the session, turns on by itself only within the guard its skill names, and is said before it acts, not after; the guard is never relaxed by the trigger.
