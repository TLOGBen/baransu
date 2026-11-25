# Feature map

Baseline: the recipe's Launch done (the throwaway `lintpilot` plugin installed, the scratch project made from
`fixtures/codex-lint/checks.toml`). Driving convention: one `codex exec` session per journey; the model is asked to
repeat the rule codes it received. Proof rule: a journey is proved by the file state or the hook state read back,
not by the model saying it complied.

| Feature | File |
|---|---|
| Lint on Codex: gates around acts, the turn's end, the session's context, skills, subagents, compaction, files changed outside | [codex-lint.md](codex-lint.md) |
