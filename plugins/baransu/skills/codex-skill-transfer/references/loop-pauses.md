# loop-pauses — /codex-skill-transfer PAUSE classification

PAUSE classification for non-interactive drivers; semantics in `../../_shared/loop-contract.md` §2.

/codex-skill-transfer issues no AskUserQuestion call of its own. Its
interaction points are the mode choice, design choices a port surfaces but
cannot make on the author's behalf, sources that cannot be reached, and edits
to a hand-maintained copy.

| Interaction point | Class | Non-interactive default |
|---|---|---|
| Mode not stated | Input | Run Audit mode (read-only) and write the report — never edit either copy without an explicit request |
| Source matches no known shape (skill, plugin, skills batch, marketplace) | Input | Report `no progress: source matches no known shape` and end the run — never force a shape |
| Design choice the author owns (where bundled agents live, manifest format, omitting a Claude-only component, marketplace layout, a `context: fork` skill's Codex path) | Input | Record it under 待查 with the options and their sources, continue — never auto-pick |
| An official page or the Codex source cannot be fetched | Input | Mark every rule that depended on it 待查 with the URL that failed, continue with the rest — never fill the gap from memory |
| Port edits to an existing hand-maintained Codex copy | **Authorization** | Edit only when the run's instructions explicitly request edits to that copy; otherwise stay in Audit mode and report the proposed fixes |
