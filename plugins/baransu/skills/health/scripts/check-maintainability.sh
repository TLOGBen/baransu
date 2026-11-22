#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# check_maintainability.py runs the doc-reference check itself, with its own interpreter
# (a DOC_REF_CHECKER already in the environment is still honoured).
exec python3 "$SCRIPT_DIR/check_maintainability.py" "$@"
