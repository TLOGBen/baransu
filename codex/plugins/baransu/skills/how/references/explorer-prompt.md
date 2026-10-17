# Explorer prompt

Fill in the placeholders and send the text below as the agent's prompt.

---

Other explorers are tracing other slices of the same subsystem in parallel. Do not try to cover everything: stay on your slice and go deep. Do not write or change any file in the repo; a read-only command is fine.

## Question

> {QUESTION}

## Your slice

{SLICE}

## Entry points already read by the main session

{ENTRY_POINTS}

## Report in this shape

- **Components**: the key types, services, classes, and abstractions on your slice — name, file path, one sentence on what each does.
- **Flow**: the execution path step by step — which function runs, in which file, what it does, what it calls next, and the data passed between steps.
- **Files read**: every file you opened, so the main session can cite them.
- **Boundaries**: where your slice connects to the rest of the codebase — its inputs and outputs.
- **Non-obvious things**: anything surprising or easy to get wrong; things that look like they work one way and work another.
- **Open questions**: what you could not trace or understand. Say so plainly.
