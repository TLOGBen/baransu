# output-journal — work-journal contract (single source)

> Shared contract for the HTML work journal produced by `/think` and `/review`
> and appended to by every downstream implementer. Skills cite this file; they
> do not restate it.

## Purpose

Terminal output is unreliable for long-running flows: scrollback truncates,
auto-compact drops context, and the user may not be watching when a decision
is made. Files on disk plus SendUserFile are the deliverable channel — the
journal is the durable, user-visible record of what was decided and what
happened during implementation.

## Trigger

- **Producers**: `/think` and `/review` each produce one journal per run,
  immediately after their primary deliverable is written.
- **Appenders**: any implementer working from that deliverable (`/execute`,
  direct implementation under `_shared/tdd.md` §7, or any later session)
  appends to the existing journal instead of creating a new one.

## Location

```
.claude/<skill>/<slug>.html
```

`<skill>` is the producing skill (`think` or `review`); `<slug>` matches the
primary deliverable's slug (e.g. `.claude/think/baransu-v2.1-philosophy-merge-plan.html`
beside the approved plan `.md`).

## Rendering basis

Render with the book golden template — `plugins/baransu/skills/book/references/golden-template.html`
— consuming the Kami tokens it carries. The journal is a standalone,
browser-ready HTML file; no external assets.

## Required sections

1. **Original skill output** — the full deliverable rendered in place, or a
   faithful summary plus a link to the source `.md`. Faithful means no
   reordering of conclusions and no dropped caveats.
2. **執行日誌** — newest-first entries appended over the journal's lifetime.
   Each entry records anything the user should know, in 繁體中文:
   - 規範外決策（off-spec decisions）
   - 被迫變更（forced changes）
   - 取捨（tradeoffs）
   - 其他使用者該知道的事
3. **處置表**（optional disposition table）— when the run tracked a list of
   candidate items, a table of 項目 / 處置（implemented / declined＋理由 /
   已存在）/ 出處.

Entry format for 執行日誌 (newest first):

```
2026-06-11 14:30 ｜ /execute
規範外決策：spec 未定義 slug 衝突行為，採「附加 -2 後綴」而非覆寫。
取捨：保留舊檔可追溯，代價是目錄多一份檔案。
```

## Append protocol

- Edit the journal **in place**; insert new 執行日誌 entries at the top of
  that section.
- **Never rewrite or delete existing history entries** — the journal is
  append-only below the entry being added. Corrections go in as new entries
  (e.g. 「更正 2026-06-11 14:30 條目：…」).
- The original-output section may be replaced only when the underlying
  deliverable itself was legitimately revised, and the revision must be noted
  as a 執行日誌 entry.

## Delivery

SendUserFile the journal:

1. immediately after creation (producer side), and
2. after the final update of a run (appender side).

Intermediate appends during a long run need not each trigger SendUserFile,
but the run must end with one so the user receives the final state.
