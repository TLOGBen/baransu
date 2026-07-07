#!/usr/bin/env bash
# Fixture-tree tests for plugins/baransu/skills/review/scripts/fact-count.sh
# (review Stage 1.6 fact-table executor — the canonical counting-noun
# templates made executable, so rows are filled by the template, never by
# re-running the target's own command).
#
# Coverage:
#   T1: bad usage (unknown subcommand / missing args) -> exit 2
#   T2: files    -> COUNT 5, bin/ .cs excluded, COMMAND+OUTPUT present
#   T3: classes  -> COUNT 2 (suffix matches only; base class + bin excluded)
#   T4: callsites-> COUNT 3 (3 dot-prefixed; bare decl + comment + bin excluded)
#   T5: testcases-> COUNT 2 ([Test]x2; bin [Test] excluded)
#   T6: fingerprint -> NUnit, TestMethod=0 Test=2 Fact=0, PROJECT emitted
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$ROOT/plugins/baransu/skills/review/scripts/fact-count.sh"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
TMP="$(realpath "$TMP")"

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

has() { printf '%s\n' "$1" | grep -q "$2"; } # has <text> <ere-anchored-pattern>

# ---------------------------------------------------------------------------
# Fixture: a fake .NET-ish tree with a build-output bin/ that must be excluded
# from every category, plus a test project a fingerprint must discover.
# ---------------------------------------------------------------------------
FIX="$TMP/proj"
mkdir -p "$FIX/src" "$FIX/bin" "$FIX/MyApp.Tests"

cat >"$FIX/src/UserService.cs" <<'EOF'
namespace App;
public class UserService : IService {
    public void Run() { }
}
EOF

cat >"$FIX/src/OrderService.cs" <<'EOF'
namespace App;
public class OrderService {
    public void Run() { }
}
EOF

cat >"$FIX/src/BaseController.cs" <<'EOF'
namespace App;
public abstract class BaseController {
}
EOF

cat >"$FIX/src/Calls.cs" <<'EOF'
namespace App;
public class Caller {
    public void Save() { }          // bare declaration — no leading dot
    public void Run(Repo r) {
        r.Save();
        this.Save();
        _repo.Save();
        // remember to Save() later -- comment mention, no leading dot
    }
}
EOF

# bin/ content: matches every pattern, so if the excludes fail, every COUNT
# below shifts by one. It is the single cross-category exclusion probe.
cat >"$FIX/bin/Generated.cs" <<'EOF'
namespace App;
public class GhostService {
    [Test] public void Ghost() { _x.Save(); }
}
EOF

cat >"$FIX/MyApp.Tests/MyApp.Tests.csproj" <<'EOF'
<Project Sdk="Microsoft.NET.Sdk"></Project>
EOF

cat >"$FIX/MyApp.Tests/SampleTests.cs" <<'EOF'
namespace App.Tests;
public class SampleTests {
    [Test] public void A() { }
    [Test] public void B() { }
}
EOF

# ---------------------------------------------------------------------------
# T1: bad usage -> exit 2
# ---------------------------------------------------------------------------
echo "T1: bad usage exits 2..."
bash "$SCRIPT" bogus >/dev/null 2>&1;            rc_sub=$?
bash "$SCRIPT" >/dev/null 2>&1;                  rc_none=$?
bash "$SCRIPT" files "$FIX" >/dev/null 2>&1;     rc_arg=$?
if [ "$rc_sub" -eq 2 ] && [ "$rc_none" -eq 2 ] && [ "$rc_arg" -eq 2 ]; then
  pass "T1: unknown subcommand, no args, and missing glob all exit 2"
else
  fail "T1: expected exit 2 on bad usage" "sub=$rc_sub none=$rc_none arg=$rc_arg"
fi

# ---------------------------------------------------------------------------
# T2: files -> COUNT 5, bin excluded, labeled lines present
# ---------------------------------------------------------------------------
echo "T2: files counts *.cs and excludes bin/..."
out=$(bash "$SCRIPT" files "$FIX" '*.cs')
if has "$out" '^COUNT: 5$' && has "$out" '^COMMAND: ' && has "$out" '^OUTPUT:$' \
  && ! has "$out" 'bin/Generated.cs'; then
  pass "T2: COUNT 5, COMMAND+OUTPUT present, bin excluded"
else
  fail "T2: files count/labels wrong" "$out"
fi

# ---------------------------------------------------------------------------
# T3: classes -> COUNT 2 (suffix declaration sites only)
# ---------------------------------------------------------------------------
echo "T3: classes counts suffix declaration sites only..."
out=$(bash "$SCRIPT" classes "$FIX" Service)
if has "$out" '^COUNT: 2$' && has "$out" '^COMMAND: grep -rlE ' ; then
  pass "T3: COUNT 2 (UserService+OrderService; base class + bin excluded)"
else
  fail "T3: classes count wrong" "$out"
fi

# ---------------------------------------------------------------------------
# T4: callsites -> COUNT 3 (dot-prefixed only)
# ---------------------------------------------------------------------------
echo "T4: callsites counts dot-prefixed invocations only..."
out=$(bash "$SCRIPT" callsites "$FIX" Save)
if has "$out" '^COUNT: 3$' && has "$out" '^COMMAND: grep -rnE ' && has "$out" '^OUTPUT:$'; then
  pass "T4: COUNT 3 (bare decl, comment, and bin call all excluded)"
else
  fail "T4: callsites count wrong" "$out"
fi

# ---------------------------------------------------------------------------
# T5: testcases -> COUNT 2
# ---------------------------------------------------------------------------
echo "T5: testcases counts test attributes and excludes bin/..."
out=$(bash "$SCRIPT" testcases "$FIX")
if has "$out" '^COUNT: 2$' && has "$out" '^COMMAND: grep -rhoE '; then
  pass "T5: COUNT 2 ([Test]x2; bin [Test] excluded)"
else
  fail "T5: testcases count wrong" "$out"
fi

# ---------------------------------------------------------------------------
# T6: fingerprint -> NUnit block for the discovered test project
# ---------------------------------------------------------------------------
echo "T6: fingerprint discovers the test project and infers NUnit..."
out=$(bash "$SCRIPT" fingerprint "$FIX")
if has "$out" '^PROJECT: .*MyApp.Tests$' \
  && has "$out" '^COUNT: TestMethod=0 Test=2 Fact=0$' \
  && has "$out" '^FRAMEWORK: NUnit ' \
  && has "$out" '^COMMAND: ' && has "$out" '^OUTPUT:$'; then
  pass "T6: NUnit fingerprint block with the correct triple"
else
  fail "T6: fingerprint block wrong" "$out"
fi

# ---------------------------------------------------------------------------

# T7: non-.cs glob on testcases must be refused (exit 2), not silently 0
echo "T7: non-.cs glob on testcases is refused..."
if bash "$SCRIPT" testcases "$FIX" --glob '*.py' >/dev/null 2>&1; then
  fail "T7: non-.cs glob was accepted (silent false-zero risk)"
else
  echo "  PASS: T7: non-.cs glob refused with usage error"
fi

# summary
# ---------------------------------------------------------------------------
echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "${#FAILED_TESTS[@]}" -gt 0 ]; then
  echo "Failed tests:"
  for t in "${FAILED_TESTS[@]}"; do echo "  - $t"; done
  exit 1
fi
exit 0
