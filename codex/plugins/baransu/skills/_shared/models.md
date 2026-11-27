# Models — which family and tier for which job

The one place a skill looks up which model to dispatch when it reaches outside the session's own model: a second reader on another family, a designer that must not share the first one's habits, a cheap sweep, a worker. A skill names the job (a row of §2); this file names the model.

## 1. Families and how to reach them

A *family* is a vendor: Claude (Anthropic) or GPT (OpenAI). "Another family" means another vendor. Each family is reached only through its own row below: a Claude model runs through the `claude` CLI.

| Family | Reached through | One-shot call |
|---|---|---|
| Claude | `claude` CLI (Claude Code), or the common suite's `delegate` | `claude -p "<brief>" --model <id> --effort <low\|medium\|high\|xhigh>`, with `--permission-mode plan` for a reader |
| GPT | the host's own agents (pin `model`) | — |

A family is available when its CLI answers on this machine (`claude --version`); an unavailable one is skipped, said in one line, never faked with the session's own model under another name.

Gemini is never dispatched. The user's Gemini plan is a consumer subscription used through `agy`, and Antigravity's terms (§6) forbid another vendor's agent driving it, even task by task. A Gemini row comes back only with an AI Studio or Vertex API key the user sets up for it.

## 2. Jobs

Ids as the live catalogs list them on 2026-11-27. Both families take effort separately from the id.

Both budgets have room to spare, and GPT's is the least used, so GPT takes the workers and sweeps. **First** names the pick when the job has no family constraint.

| Job | First | Claude | GPT |
|---|---|---|---|
| Prose a person reads — reports, explanations, the Attention section, a written candidate | Claude | `claude-opus-5-5` | `gpt-6.2-astra` |
| Independent reader — review, verifier, decision-log reader | GPT | `claude-opus-5-5` | `gpt-6.2-astra` |
| Long, hard reasoning or design — the thinking on a complex problem | Claude | `claude-opus-5-5`, or `claude-fable-5-2` | `gpt-6.2-astra` |
| Worker on a goal with acceptance — precise execution | GPT | `claude-sonnet-5-5` | `gpt-6.2-sol`; `gpt-6.2-astra` when the task is hard |
| Cheap read-only sweep or lookup | GPT | `claude-haiku-5-5` | `gpt-6-luna` |

When the job asks for another family than the one that wrote the work, take the other one.

GPT executes precisely but writes code that reads poorly and guards against cases that cannot happen. So a GPT worker's brief names the shape to follow — the existing code it should read like, or the `$baransu:draft` sketch — and says that a check beyond the acceptance is not wanted; its diff is read by Claude for shape and needless guards before it counts.

## 3. Keeping it true

- **The live catalog wins.** Before the first dispatch of a run, list it (the host's own model list, and `claude` for Claude ids); an id here that is no longer listed is replaced by the same row's newest listed model in that family, and the replacement is named in the report.
- **Name what ran.** Every report that a dispatched model produced or judged names the model id and effort that actually ran.
