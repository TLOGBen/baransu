# replay — a proved journey kept so it reruns without a model

A replay is a feature's proved journeys driven by a script, with no agent and no person in it, run through `.claude/verify/run.py`. The contract — `check.toml`'s fields, the exit codes, admission, and the five rules of its §7 (data read back, a ready signal, a fresh data directory, stable names, no path with side effects outside the run) — is `../../_shared/regression.md`. This file adds the layout and what makes a replay stable.

## Layout

```
.claude/prove-it/replays/<feature>/
  check.toml        the checks, per the contract's §3
  <script>          the judge check.toml's cmd runs
  journeys/         one file per journey: its id, its promise, each step's input and the read-back it expects, the end state
```

A fixture the recipe already keeps stays where the recipe keeps it and is listed in `covers`, so a change to it marks the replay stale.

## The script's job

For each journey, in order:

1. **Build fresh** — a new temp project and data directory, fixed ids, the environment pointed into them.
2. **Feed the input** — each step's input to the program, and each side channel it reads, in the journey's order.
3. **Read back** — the decision, the codes and the marks the program returns, and the end state it stored.
4. **Normalize** — temp paths and shell or platform tokens to placeholders.
5. **Compare** — with what the journey expects; print one `red <journey> step <n>: expected …, got …` line per difference and go on to the next journey.
6. **Clean up** — remove the temp folder whatever happened.

Exit 0 when every journey matched, 1 when any read-back differed, 2 when the judge itself cannot stand: a tool missing, a malformed journey, an input field the program does not read, a changed command shape, the program crashing.

## Stable by construction

- **Drive the program the host would start, with the host's own input** — a hook's command with the event JSON on stdin, a CLI's command line, a service's request — never the host itself or an internal function. That is what takes the model out.
- **Isolate through what the code already reads.** Point its data, home and config environment variables into the journey's fresh folder, one per journey; fix session and request ids; drop debug variables from the inherited environment.
- **Write every side channel the program reads besides its input** — a transcript line that marks a new response, a file it polls. Without it the journey never reaches the state it promises.
- **Accept only the input fields the program reads.** Any other field is a stale judge, exit 2: a replay must not pass on a field the code ignores.
- **Check the registration that routes the event to the program.** A dropped registration is red — the program never ran; a changed command shape is a stale judge.
- **Compare decisions, codes and marks, never prose.** Free text carries paths and wording that change for reasons outside the promise.
- **Give every rule its negative twin** — refused beside allowed, trusted beside untrusted, held again in the same response beside released in the next. A one-sided journey passes on a program that does nothing.
- **Pin every condition a journey depends on** — trust, config, the project's own files — inside the journey; an unpinned one turns red for reasons outside the promise.
- **Read cheap state signals at the end** — counters, pending items, no lock left behind. They catch faults the decisions miss.
- **Time it cold and warm.** A cold start can take twice the warm run; set `timeout` for the cold one.
