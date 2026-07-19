# Task Map

**spec_dir**: `.claude/analyze/2026-05-26-tui-menu-funnel-switch-src/`
**execute_dir**: `.claude/execute/2026-05-26-tui-menu-funnel-switch-src/execute/`

## DAG / Frontier

| Frontier | Groups (parallel) | Predecessor |
|---|---|---|
| L0 | shared, catalog | — |
| L1 | library | shared |
| L2 | handlers-core | library, catalog |
| L3 | tui | shared, handlers-core |

Max width = 2 → **Class L** → gitworktree per group at L0; subsequent levels have width 1 (single worktree per level).

File-conflict pre-scan (L0): shared touches `Cargo.toml` + `src/presentation/handlers/tui/{mod,widgets}.rs`; catalog touches `src/catalog/facade.rs` + `src/catalog/service/scraper.rs`. **No overlap** — safe to parallelize.

## Task → TaskCreate # → Worktree mapping

| Task ID | TaskCreate # | Worktree branch |
|---|---|---|
| TASK-shared-01 | 13 | `execute/2026-05-26-tui-menu-funnel-switch-src/shared` |
| TASK-shared-02 | 14 | `execute/2026-05-26-tui-menu-funnel-switch-src/shared` |
| TASK-shared-03 | 15 | `execute/2026-05-26-tui-menu-funnel-switch-src/shared` |
| TASK-catalog-01 | 16 | `execute/2026-05-26-tui-menu-funnel-switch-src/catalog` |
| TASK-library-01 | 17 | `execute/2026-05-26-tui-menu-funnel-switch-src/library` |
| TASK-library-02 | 18 | `execute/2026-05-26-tui-menu-funnel-switch-src/library` |
| TASK-hc-01 | 19 | `execute/2026-05-26-tui-menu-funnel-switch-src/handlers-core` |
| TASK-hc-02 | 20 | `execute/2026-05-26-tui-menu-funnel-switch-src/handlers-core` |
| TASK-hc-03 | 21 | `execute/2026-05-26-tui-menu-funnel-switch-src/handlers-core` |
| TASK-tui-01 | 22 | `execute/2026-05-26-tui-menu-funnel-switch-src/tui` |
| TASK-tui-02 | 23 | `execute/2026-05-26-tui-menu-funnel-switch-src/tui` |
| TASK-tui-03 | 24 | `execute/2026-05-26-tui-menu-funnel-switch-src/tui` |
| TASK-tui-04 | 25 | `execute/2026-05-26-tui-menu-funnel-switch-src/tui` |
| TASK-tui-05 | 26 | `execute/2026-05-26-tui-menu-funnel-switch-src/tui` |
| TASK-tui-06 | 27 | `execute/2026-05-26-tui-menu-funnel-switch-src/tui` |
| TASK-tui-07 | 28 | `execute/2026-05-26-tui-menu-funnel-switch-src/tui` |

## Checklist file mapping

- shared → impl-checklist-shared.md
- catalog → impl-checklist-catalog.md
- library → impl-checklist-library.md
- handlers-core → impl-checklist-handlers-core.md
- tui → impl-checklist-tui.md

## Build / test commands (for impl-agent / merge-agent)

- Build: `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo build --bin novel-looker`
- Tests: `LIBCLANG_PATH=/usr/lib/llvm-18/lib cargo test`
- Layer invariant grep: `grep -nE "use crate::catalog::facade|use crate::library::facade" src/library src/catalog`（零命中為通過）
