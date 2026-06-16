# /baransu:design — Error Codes

| Error | Trigger | Action |
|-------|------|--------|
| lint: DESIGN.md not found | no DESIGN.md at project root | Report + suggest `/design gen`; stop |
| preset: no name given | `/design preset` with no second token | List available presets; exit ≠ 0 |
| preset: unknown name | name not in enum | List available presets; exit ≠ 0 |
| preset: references/ empty | install missing files | Report「目前無可用 preset」 |
| preset: `references/<name>-preset/` any file missing | plugin damaged | Report which path is missing; abort |
| preset: v1.2 residue + no `--force` | tokens.css first line fails regex or partial v1.2 artifact | stderr warning + exit ≠ 0 |
| preset: copy write failure (permission/disk full/EPERM/ENOSPC) | IO error | Report path; abort; preserve staging |
| preset: atomic mv failed | partial state risk | Report; project root stays in prior state |
| gen: --slug missing | gen mode with no `--slug` | reject |
| gen: --slug pattern fail | does not match `/^[a-z][a-z0-9-]{1,15}$/` | reject |
| gen: --slug reserved word collision | slug ∈ {kami, google-design, swiss} | reject |
| lint: any check (A/B/C/D/E/F) fail | see Lint Mode section | list the specific violation + exit 1; if Check A fails, terminate without running B-F |
| git rev-parse fails (non-repo) | not a git project | Use cwd as project root |
| Stage 0 inject: file already has v1.3 block | idempotency | skip silently |
| Stage 0 inject: file has v1.2 block | upgrade required | replace stale block with v1.3 canonical block |
| gen / preset: DESIGN.html already exists | overwrite | Overwrite without prompting |
