#!/usr/bin/env bash
# Structural test for TASK-agents-01: investigator-agent.md
# (perspective-class, read-only, no git ops).
#
# Asserts (7 checks total):
#   1) plugins/baransu/agents/investigator-agent.md exists
#   2) YAML frontmatter contains: name: investigator-agent,
#      non-empty description:, tools: listing only read-only tools
#      (Read, Grep, Glob, Bash). Edit/Write must NOT appear in tools.
#   3) Body has the four perspective sections — Perspective / Mission /
#      Principles / Lane-keeping (English or 視角 / 目標 / 通用原則 /
#      禁忌 in Traditional Chinese).
#   4) Forbidden-operations list mentions ≥ 5 of:
#      不寫檔/不 stage/不 commit/不 push/不 branch/不 worktree/
#      不 subprocess (or English equivalents).
#   5) Allowed-operations mentions ≥ 4 of:
#      Read / grep|find|glob / git log / git show / git blame /
#      bash 純查詢 (or English equivalents).
#   6) Output schema mentions root_cause_guess, citations, confidence
#      (3 grep hits, one per term).
#   7) Self-check note: grep finds `git status --porcelain`.
#
# Exit 0 on full pass; non-zero (and prints reason) on any failure.

set -u

WORKTREE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
AGENT_FILE="$WORKTREE_ROOT/plugins/baransu/agents/investigator-agent.md"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

# (1) file exists
[ -f "$AGENT_FILE" ] || fail "agent file not found at $AGENT_FILE"

# (2) frontmatter checks
# Extract frontmatter (between first two `---` lines)
FRONTMATTER="$(awk 'NR==1 && /^---$/ {flag=1; next} flag && /^---$/ {exit} flag {print}' "$AGENT_FILE")"
[ -n "$FRONTMATTER" ] || fail "frontmatter not found or empty"

echo "$FRONTMATTER" | grep -qE '^name:[[:space:]]*investigator-agent[[:space:]]*$' \
  || fail "frontmatter missing 'name: investigator-agent'"

DESC_LINE="$(echo "$FRONTMATTER" | grep -E '^description:' || true)"
[ -n "$DESC_LINE" ] || fail "frontmatter missing 'description:'"
DESC_VALUE="$(echo "$DESC_LINE" | sed -E 's/^description:[[:space:]]*//')"
[ -n "$DESC_VALUE" ] || fail "frontmatter 'description:' is empty"

TOOLS_LINE="$(echo "$FRONTMATTER" | grep -E '^tools:' || true)"
[ -n "$TOOLS_LINE" ] || fail "frontmatter missing 'tools:'"
# Disallow Edit / Write in tools list
echo "$TOOLS_LINE" | grep -qiE '\b(Edit|Write|MultiEdit|NotebookEdit)\b' \
  && fail "frontmatter 'tools:' must not list write tools (Edit/Write/etc.); got: $TOOLS_LINE"
# Require all four read-only tools
for tool in Read Grep Glob Bash; do
  echo "$TOOLS_LINE" | grep -qE "\\b${tool}\\b" \
    || fail "frontmatter 'tools:' missing required read-only tool '$tool'"
done

# (3) four perspective sections present (English or Traditional Chinese)
have_section() {
  # $1: english heading, $2: chinese heading
  grep -qE "^##[[:space:]]+(${1}|${2})[[:space:]]*$" "$AGENT_FILE"
}
have_section "Perspective" "視角"  || fail "missing section: ## Perspective / ## 視角"
have_section "Mission"     "目標"  || fail "missing section: ## Mission / ## 目標"
have_section "Principles"  "通用原則" || fail "missing section: ## Principles / ## 通用原則"
# Lane-keeping accepts the english label or the chinese 禁忌 / Forbidden
grep -qE '^##[[:space:]]+(Lane-keeping|Forbidden|禁忌)[[:space:]]*$' "$AGENT_FILE" \
  || fail "missing section: ## Lane-keeping / ## Forbidden / ## 禁忌"

# (4) forbidden-operations: ≥ 5 distinct hits
FORBIDDEN_TERMS=(
  '不寫.*檔'
  '不[[:space:]]*stage'
  '不[[:space:]]*commit'
  '不[[:space:]]*push'
  '不[[:space:]]*branch'
  '不[[:space:]]*worktree'
  '不[[:space:]]*subprocess'
  '[Nn]o[[:space:]]+writes?'
  '[Nn]o[[:space:]]+staging'
  '[Nn]o[[:space:]]+commits?'
  '[Nn]o[[:space:]]+push'
  '[Nn]o[[:space:]]+branch'
  '[Nn]o[[:space:]]+worktree'
  '[Nn]o[[:space:]]+subprocess'
)
forbidden_hits=0
for pat in "${FORBIDDEN_TERMS[@]}"; do
  if grep -qE "$pat" "$AGENT_FILE"; then
    forbidden_hits=$((forbidden_hits + 1))
  fi
done
[ "$forbidden_hits" -ge 5 ] \
  || fail "expected ≥ 5 forbidden-operations terms, got $forbidden_hits"

# (5) allowed-operations: ≥ 4 distinct hits
ALLOWED_TERMS=(
  '\bRead\b'
  '\bgrep\b'
  '\bfind\b'
  '\bglob\b'
  'git[[:space:]]+log'
  'git[[:space:]]+show'
  'git[[:space:]]+blame'
  'bash[[:space:]]*純查詢'
  'read-only[[:space:]]+bash'
)
allowed_hits=0
for pat in "${ALLOWED_TERMS[@]}"; do
  if grep -qiE "$pat" "$AGENT_FILE"; then
    allowed_hits=$((allowed_hits + 1))
  fi
done
[ "$allowed_hits" -ge 4 ] \
  || fail "expected ≥ 4 allowed-operations terms, got $allowed_hits"

# (6) output schema mentions root_cause_guess, citations, confidence
for term in root_cause_guess citations confidence; do
  grep -qE "\\b${term}\\b" "$AGENT_FILE" \
    || fail "output schema missing term: $term"
done

# (7) self-check note
grep -qF 'git status --porcelain' "$AGENT_FILE" \
  || fail "missing self-check: 'git status --porcelain'"

echo "PASS: investigator-agent.md structural checks (7/7)"
exit 0
