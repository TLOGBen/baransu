# Stable verification entrypoint — run everything an agent or human needs
# before declaring work done. Individual suites stay runnable on their own.

.PHONY: test mirror mirror-check ship-check
test:
	python3 scripts/verify-skills.py
	python3 -m pytest tests/scripts/ -q
	@set -e; for f in $$(find tests -name '*.sh' -not -path '*/fixtures/*' | sort); do \
		echo "== $$f"; bash "$$f"; \
	done
	@echo "== all suites green"

# Regenerate the codex mirror in place (output root is codex/, never
# codex/plugins/baransu — the script nests the plugin path itself).
mirror:
	python3 plugins/baransu/skills/codex-skill-transfer/scripts/transfer.py plugins/baransu codex

# Drift gate: regen into a temp dir and diff against the committed mirror.
# Deliberately NOT part of `make test` — mid-development skill edits would stay
# red until regen. There is no CI and no cron in this repo: the only gate is
# human, and `make ship-check` below is the one entrypoint that runs it.
mirror-check:
	@TMP=$$(mktemp -d); trap 'rm -rf "$$TMP"' EXIT; \
	python3 plugins/baransu/skills/codex-skill-transfer/scripts/transfer.py plugins/baransu "$$TMP/codex" >/dev/null 2>&1; \
	if diff -r "$$TMP/codex" codex >/dev/null 2>&1; then \
		echo "== mirror in sync"; \
	else \
		echo "== MIRROR DRIFT — run 'make mirror' and commit:"; \
		diff -rq "$$TMP/codex" codex | head -20; exit 1; \
	fi

# Pre-ship gate: the full suite plus the mirror-drift check, in that order.
# `make test` deliberately stops short of mirror-check (see above), so this is
# the target to run before committing a release — never merge mirror-check into
# `test`, or mid-development edits go red before regen.
ship-check: test mirror-check
	@echo "== ship-check green (test + mirror-check)"
