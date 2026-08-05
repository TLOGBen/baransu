#!/usr/bin/env bash
# Machine anchors for the contract→seal→ship lifecycle (TASK-lifecycle-05).
#
# Every literal below is copied byte-for-byte from the spec's Verbatim
# Constants block or from the owning SKILL.md / agent file. All matching is
# grep -F (fixed string) so a single changed character fails the run.
#
# Assertions:
#   A1  sealed-marker line appears >= 1x in EACH of contract/seal/ship SKILL.md
#       (three files, byte-identical literal)
#   A2  seal/SKILL.md carries the dispatcher clauses: seal-log enum, head -3
#       detection form, re-verification cap (total dispatches <= 3), branch 2/3
#       no-marker clause, five-field payload, Exactly-one-pass replacement
#       (old sentence gone), fingerprint definition, write-after-fingerprint
#       ordering
#   A3  ship/SKILL.md carries the three-condition early-stop message, the INV-1
#       two-sources line, and the INV-8 staged-deletion note
#   A4  the five user-facing message formats from the Surface Inventory each
#       live in their owning SKILL.md
#   A5  agents/seal-agent.md verify-only boundary: tool set, never-applies-a-fix
#       line, git revert prohibition, structured status enum — and NO sentence
#       granting fix authority

set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILLS="$ROOT/plugins/baransu/skills"
CONTRACT_MD="$SKILLS/contract/SKILL.md"
SEAL_MD="$SKILLS/seal/SKILL.md"
SHIP_MD="$SKILLS/ship/SKILL.md"
SEAL_AGENT="$ROOT/plugins/baransu/agents/seal-agent.md"

PASS=0
FAIL=0
FAILED_TESTS=()

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() {
  FAIL=$((FAIL + 1))
  FAILED_TESTS+=("$1")
  echo "  FAIL: $1"
  if [ -n "${2:-}" ]; then echo "        $2"; fi
}

# assert_lit <name> <file> <literal>   — literal present on one line (grep -F)
assert_lit() {
  local name="$1" file="$2" lit="$3"
  if [ ! -f "$file" ]; then
    fail "$name: file missing: $file"
    return
  fi
  if grep -qF -- "$lit" "$file"; then
    pass "$name"
  else
    fail "$name" "not found in ${file#$ROOT/}: [$lit]"
  fi
}

# assert_lit_joined <name> <file> <literal>
# For literals the source file soft-wraps at a CJK boundary: newlines are
# deleted (no space inserted), then matched byte-exact.
assert_lit_joined() {
  local name="$1" file="$2" lit="$3"
  if [ ! -f "$file" ]; then
    fail "$name: file missing: $file"
    return
  fi
  if tr -d '\n' < "$file" | grep -qF -- "$lit"; then
    pass "$name"
  else
    fail "$name" "not found (newline-joined) in ${file#$ROOT/}: [$lit]"
  fi
}

# assert_absent_lit <name> <file> <literal>
assert_absent_lit() {
  local name="$1" file="$2" lit="$3"
  if [ ! -f "$file" ]; then
    fail "$name: file missing: $file"
    return
  fi
  if grep -qF -- "$lit" "$file"; then
    fail "$name" "literal must NOT appear in ${file#$ROOT/}: [$lit]"
  else
    pass "$name"
  fi
}

# assert_absent_re <name> <file> <ERE>  — case-insensitive negative match
assert_absent_re() {
  local name="$1" file="$2" re="$3"
  if [ ! -f "$file" ]; then
    fail "$name: file missing: $file"
    return
  fi
  local hit
  # dispatcher-scoped sentences legitimately mention fixes — exclude them from the negative sweep
  hit=$(grep -niE -- "$re" "$file" | grep -viF 'dispatcher' | head -3 || true)
  if [ -n "$hit" ]; then
    fail "$name" "forbidden phrasing matched: $hit"
  else
    pass "$name"
  fi
}

# ---------------------------------------------------------------------------
# Verbatim constants (spec: design.md ## Verbatim Constants)
# ---------------------------------------------------------------------------
SEALED_MARKER='> STATUS: sealed（{ISO 日期}）— {五點結果一行摘要}'

# Detection form — carries both quote flavours and $f, so it is fed through a
# quoted heredoc to stay byte-exact.
DETECT_FORM=$(cat <<'VERBATIM_EOF'
head -3 "$f" | grep -qF '> STATUS: sealed'
VERBATIM_EOF
)

SEAL_LOG_ENUM='pass|fixed|unresolved'

# ---------------------------------------------------------------------------
# A1: sealed marker literal, byte-identical across the three SKILL.md files
# ---------------------------------------------------------------------------
echo "A1: sealed-marker literal present in contract/seal/ship SKILL.md..."
for pair in "contract:$CONTRACT_MD" "seal:$SEAL_MD" "ship:$SHIP_MD"; do
  label="${pair%%:*}"
  file="${pair#*:}"
  if [ ! -f "$file" ]; then
    fail "A1[$label]: file missing: $file"
    continue
  fi
  COUNT=$(grep -cF -- "$SEALED_MARKER" "$file" || true)
  if [ "${COUNT:-0}" -ge 1 ]; then
    pass "A1[$label]: sealed-marker literal count = $COUNT (>= 1)"
  else
    fail "A1[$label]: sealed-marker literal count = ${COUNT:-0} (expected >= 1)" \
         "Expected byte-exact: [$SEALED_MARKER]"
  fi
done

# ---------------------------------------------------------------------------
# A2: seal/SKILL.md dispatcher clauses
# ---------------------------------------------------------------------------
echo "A2: seal/SKILL.md dispatcher clauses..."
assert_lit "A2a: seal-log result enum literal 'pass|fixed|unresolved'" \
           "$SEAL_MD" "$SEAL_LOG_ENUM"
assert_lit "A2b: head -3 sealed-marker detection form" \
           "$SEAL_MD" "$DETECT_FORM"
assert_lit "A2c: re-verification cap heading (cap 2)" \
           "$SEAL_MD" '**Re-verification cap: 2**'
assert_lit "A2d: total-dispatch ceiling clause (total dispatches <= 3)" \
           "$SEAL_MD" '2 re-verification dispatches (total dispatches ≤3).'
assert_lit "A2e: branch 2/3 write no sealed marker" \
           "$SEAL_MD" 'Branches 2 and 3 never write a marker.'
assert_lit "A2f: dispatch payload is exactly five fields" \
           "$SEAL_MD" 'Every dispatch of seal-agent carries exactly these five fields'
assert_lit "A2g: payload field 5 = scratch path" \
           "$SEAL_MD" '5. **Scratch path** —'
assert_absent_lit "A2h: old Exactly-one-pass sentence removed" \
           "$SEAL_MD" 'Exactly one pass (no seal-of-a-seal, no iterative rounds)'
assert_lit "A2i: Exactly-one-pass replacement (latest clean dispatch)" \
           "$SEAL_MD" 'The marker stamps only the latest clean dispatch'
assert_lit "A2j: fingerprint definition (tracked diff + untracked list)" \
           "$SEAL_MD" '**Fingerprint definition**: the tracked diff (`git diff`) plus the'
assert_lit "A2k: marker write ordered after fingerprint comparison" \
           "$SEAL_MD" '**Ordering**: the sealed marker write is ordered strictly AFTER the'

# ---------------------------------------------------------------------------
# A3: ship/SKILL.md detection, INV-1, INV-8
# ---------------------------------------------------------------------------
echo "A3: ship/SKILL.md three-condition early stop + invariants..."
assert_lit "A3a: three-condition early-stop message" \
           "$SHIP_MD" '「沒有可歸檔的工作檔案，git 也乾淨，root 無 sealed 合約，結束。」'
assert_lit "A3b: early stop requires all three inputs empty" \
           "$SHIP_MD" 'Stop only when **all three** are empty'
assert_lit "A3c: INV-1 names exactly two archive sources" \
           "$SHIP_MD" 'Exactly two sources feed the archive: (1) the Step 1 `ARCHIVE_DIRS` allowlist, swept dir by dir; (2) sealed root `CONTRACT*.md` files'
assert_lit "A3d: ship reuses the head -3 detection form" \
           "$SHIP_MD" "$DETECT_FORM"
assert_lit "A3e: INV-8 note — sealed-contract deletion enters the staged diff" \
           "$SHIP_MD" 'shows up as a **deletion of the old root path**'
assert_lit "A3f: INV-8 note — that deletion must not dominate the commit subject" \
           "$SHIP_MD" 'it is session cleanup, so it must never dominate the commit subject'

# ---------------------------------------------------------------------------
# A4: the five Surface Inventory user-facing message formats
# ---------------------------------------------------------------------------
echo "A4: Surface Inventory message formats in their owning SKILL.md..."
assert_lit_joined "A4a: seal 封緘完成 message format" "$SEAL_MD" \
  '「封緘完成：{N} 條條文核對、{M} 個表面掃描、{K} 處修正（各附釘死測試）、突變 {X}/{Y} 被測試攔截。」'
assert_lit "A4b: seal 複驗超限 message format" "$SEAL_MD" \
  '「複驗上限已達（2 次）：{N} 項未清 findings 如下，未蓋章（seal-log: unresolved）。」'
assert_lit "A4c: ship Step 1 早停 message format" "$SHIP_MD" \
  '「沒有可歸檔的工作檔案，git 也乾淨，root 無 sealed 合約，結束。」'
assert_lit "A4d: ship Step 2 歸檔輸出 message format (含 sealed 計數 {S})" "$SHIP_MD" \
  '「已歸檔：{N} 個項目 → .claude/archived/（read/learn/book 產物保留；含 sealed 合約 {S} 份）」'
assert_lit "A4e: contract 覆蓋前歸檔 message format" "$CONTRACT_MD" \
  '「偵測到已封緘合約，已先歸檔至 .claude/archived/{filename}-{unix_timestamp}，續寫新合約。」'

# ---------------------------------------------------------------------------
# A5: seal-agent.md verify-only boundary
# ---------------------------------------------------------------------------
echo "A5: agents/seal-agent.md verify-only boundary..."
assert_lit "A5a: frontmatter tool set (no permissionMode, verify-only set)" \
           "$SEAL_AGENT" 'tools: Read, Grep, Glob, Bash, Write, Edit'
assert_lit "A5b: agent never applies a fix" \
           "$SEAL_AGENT" 'This agent NEVER applies a fix'
assert_lit "A5c: git checkout/restore/stash forbidden as revert mechanism" \
           "$SEAL_AGENT" '`git checkout` / `git restore` / `git stash` are FORBIDDEN as revert mechanisms'
assert_lit "A5d: structured report status enum" \
           "$SEAL_AGENT" 'status: [clean | findings | revert-failure | malformed-payload]'
assert_absent_re "A5e: no sentence granting fix authority" \
           "$SEAL_AGENT" 'direct-fix rights|((the|this) agent|you)[^.]*(may|can|(is|are) (allowed|authorized) to)[^.]*(fix|repair|correct)|授權[^。]*修復'

# ---------------------------------------------------------------------------
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
  printf 'Failed: %s\n' "${FAILED_TESTS[@]}"
  exit 1
fi
exit 0
