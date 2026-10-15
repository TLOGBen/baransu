# Stable verification entrypoint. This plugin ships no unit tests (see
# CLAUDE.md § Verification): `make test` runs only the structural verifier,
# which is the mechanism anchor the principles bind to, not a unit test.

.PHONY: test parity-check ship-check
test:
	python3 scripts/verify-skills.py

# Codex parity gate. The Codex copy under codex/plugins/baransu/ is maintained
# by hand (see AGENTS.md); this checks that every skill file has a counterpart
# on the other side (Codex-only agents/openai.yaml allowed) and that the two
# manifest versions match. It never runs transfer.py. Deliberately NOT part of
# `make test` — mid-development edits may lag on one side. There is no CI and
# no cron in this repo: `make ship-check` below is the one entrypoint that runs it.
parity-check:
	python3 scripts/verify-codex-parity.py

# Pre-ship gate: the structural verifier plus the Codex parity check, in that order.
# Never merge parity-check into `test`; bundling is ship-check's job.
ship-check: test parity-check
	@echo "== ship-check green (test + parity-check)"
