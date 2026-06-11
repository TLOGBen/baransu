# Stable verification entrypoint — run everything an agent or human needs
# before declaring work done. Individual suites stay runnable on their own.

.PHONY: test
test:
	python3 scripts/verify-skills.py
	python3 -m pytest tests/scripts/ -q
	@set -e; for f in $$(find tests -name '*.sh' -not -path '*/fixtures/*' | sort); do \
		echo "== $$f"; bash "$$f"; \
	done
	@echo "== all suites green"
