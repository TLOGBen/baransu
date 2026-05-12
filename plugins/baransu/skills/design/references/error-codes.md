# /baransu:design — Error Codes

| Error | 觸發 | Action |
|-------|------|--------|
| lint: DESIGN.md not found | project root 無 DESIGN.md | Report + suggest `/design gen`; stop |
| preset: no name given | `/design preset` 無第二 token | List available presets; exit ≠ 0 |
| preset: unknown name | name 不在 enum | List available presets; exit ≠ 0 |
| preset: references/ empty | 安裝缺檔 | Report「目前無可用 preset」 |
| preset: `references/<name>-preset/` 任一檔缺失 | plugin damaged | Report 缺哪個 path; abort |
| preset: v1.2 殘留 + 無 `--force` | tokens.css 第一行不符 regex 或 partial v1.2 artifact | stderr warning + exit ≠ 0 |
| preset: copy write failure (permission/disk full/EPERM/ENOSPC) | IO error | Report path; abort；保留 staging |
| preset: atomic mv 失敗 | partial state risk | Report；project root 維持前狀態 |
| gen: --slug missing | gen 模式無 `--slug` | reject |
| gen: --slug pattern fail | 不合 `/^[a-z][a-z0-9-]{1,15}$/` | reject |
| gen: --slug reserved word collision | slug ∈ {kami, google-design, swiss} | reject |
| lint: 任一 check (A/B/C/D/E/F) fail | 詳見 Lint Mode 段 | 列具體 violation + exit 1；Check A fail 即終止不跑 B-F |
| git rev-parse fails (non-repo) | 非 git project | Use cwd as project root |
| Stage 0 inject: file already has v1.3 block | idempotency | skip silently |
| Stage 0 inject: file has v1.2 block | 升級需求 | replace stale block with v1.3 canonical block |
| gen / preset: DESIGN.html already exists | overwrite | Overwrite without prompting |
