# CLAUDE.md — health-checker fixture project

Static fixture for tests/scripts/test_health_checkers.py. It pins the current
behavior of the health skill checker scripts; keep it small and deterministic.

The reference to @ROADMAP.md below is intentionally broken: ROADMAP.md does
not exist, so check_doc_refs.py must report it as MISSING and exit non-zero.

## Project map

- `docs/` — project documentation; see docs/guide.md for the broken-link case
- `Makefile` — lint and build entrypoints only

## Verification

Run `make lint` and `make build` before handing off changes.

The fenced example below must be skipped by the doc-reference scan:

```text
Broken example inside a fence: docs/absent-in-fence.md is never reported.
```

## Non-goals

- This project never ships; it exists only as a test fixture.
- Keep this file free of drift markers so counts stay at zero.
