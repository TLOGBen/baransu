# Stable verification entrypoint — run everything an agent or human needs
# before declaring work done. Individual suites stay runnable on their own.

.PHONY: test parity-check ship-check
test:
	python3 scripts/verify-skills.py
	python3 -m pytest tests/scripts/ -q
	@set -e; for f in $$(find tests -name '*.sh' -not -path '*/fixtures/*' | sort); do \
		echo "== $$f"; bash "$$f"; \
	done
	@echo "== all suites green"

# Codex parity gate. The Codex copy under codex/plugins/baransu/ is maintained
# by hand (see AGENTS.md); this checks that every skill file has a counterpart
# on the other side (Codex-only agents/openai.yaml allowed) and that the two
# manifest versions match. It never runs transfer.py. Deliberately NOT part of
# `make test` — mid-development edits may lag on one side. There is no CI and
# no cron in this repo: `make ship-check` below is the one entrypoint that runs it.
parity-check:
	python3 scripts/verify-codex-parity.py

# Pre-ship gate: the full suite plus the Codex parity check, in that order.
# Never merge parity-check into `test`; bundling is ship-check's job.
ship-check: test parity-check
	@echo "== ship-check green (test + parity-check)"
