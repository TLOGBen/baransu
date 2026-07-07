#!/usr/bin/env bash
# fact-count.sh — /baransu:review Stage 1.6 fact-table executor.
#
# The counting-noun templates from
# plugins/baransu/skills/_shared/fact-check.md, made executable. This script
# IS the template: each subcommand hardcodes ONE category's canonical command
# so a fact-table row is filled by RUNNING THE TEMPLATE — never by re-running
# the target's own command. A reproducible number produced under the wrong
# pattern (a dotless `grep 'Save('` that counts declarations and comment
# mentions as call sites) is exactly the failure the noun->template binding
# prevents; the leading dot on `callsites` is hardcoded so callers cannot omit
# it.
#
# Usage: bash fact-count.sh <subcommand> <root> [args]
#   files       <root> <glob>          file listing            (檔案數)
#   classes     <root> <suffix>        declaration sites       (類別數)
#   callsites   <root> <method>        dot-prefixed calls      (呼叫點)
#   testcases   <root> [--glob <g>]    test-attribute count    (測試案例數)
#   fingerprint <root> [--glob <g>]    per-project framework   (框架指紋)
#
# Every result block prints three labeled lines:
#   COMMAND: <the exact command executed>
#   OUTPUT:  <raw output, truncated to 20 lines + a TRUNCATED marker>
#   COUNT:   <the number>
# fingerprint adds PROJECT / FRAMEWORK framing and emits one block per project.
#
# Build-output / generated dirs are excluded everywhere: bin obj node_modules
# dist target __pycache__. No deps beyond grep / find / sort / uniq / wc and
# bash builtins. Exit codes: 0 = ran; 2 = usage error.

set -u

OUTPUT_LIMIT=20

# grep --exclude-dir set, shared by every grep-based category.
GREP_EXCL=(--exclude-dir=bin --exclude-dir=obj --exclude-dir=node_modules \
           --exclude-dir=dist --exclude-dir=target --exclude-dir=__pycache__)

# Display strings for the COMMAND line (kept in sync with the code below).
PRUNE_STR="-path '*/bin/*' -prune -o -path '*/obj/*' -prune -o -path '*/node_modules/*' -prune -o -path '*/dist/*' -prune -o -path '*/target/*' -prune -o -path '*/__pycache__/*' -prune -o"
EXCL_STR="--exclude-dir=bin --exclude-dir=obj --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=target --exclude-dir=__pycache__"

usage() {
  cat >&2 <<'EOF'
usage: bash fact-count.sh <subcommand> <root> [args]
  files       <root> <glob>
  classes     <root> <suffix>
  callsites   <root> <method>
  testcases   <root> [--glob <glob>]
  fingerprint <root> [--glob <glob>]
EOF
  exit 2
}

# find with every build-output dir pruned. find_pruned <root> <name-glob>
find_pruned() {
  find "$1" \
    -path '*/bin/*' -prune -o \
    -path '*/obj/*' -prune -o \
    -path '*/node_modules/*' -prune -o \
    -path '*/dist/*' -prune -o \
    -path '*/target/*' -prune -o \
    -path '*/__pycache__/*' -prune -o \
    -type f -name "$2" -print 2>/dev/null
}

# count_lines <string> -> number of lines (0 for empty).
count_lines() {
  if [ -z "$1" ]; then echo 0; return; fi
  printf '%s\n' "$1" | grep -c '^'
}

# print_truncated <string> — up to OUTPUT_LIMIT lines then a TRUNCATED marker.
print_truncated() {
  local total line i=0
  total=$(count_lines "$1")
  if [ "$total" -eq 0 ]; then
    printf '(no output)\n'
    return
  fi
  printf '%s\n' "$1" | while IFS= read -r line; do
    i=$((i + 1))
    if [ "$i" -le "$OUTPUT_LIMIT" ]; then printf '%s\n' "$line"; fi
  done
  if [ "$total" -gt "$OUTPUT_LIMIT" ]; then
    printf '... TRUNCATED (%d of %d lines shown)\n' "$OUTPUT_LIMIT" "$total"
  fi
}

# emit <command-string> <raw-output> <count>
emit() {
  printf 'COMMAND: %s\n' "$1"
  printf 'OUTPUT:\n'
  print_truncated "$2"
  printf 'COUNT: %s\n' "$3"
}

# count_token <raw> <ERE full-line pattern> — exact-line matches (`[Test]`
# never matches `[TestMethod]`, so the triple is cleanly separable).
count_token() {
  if [ -z "$1" ]; then echo 0; return; fi
  printf '%s\n' "$1" | grep -xcE "$2"
}

# parse_glob_opt <args…> — sets PARSED_GLOB (default *.cs). --glob <g> only.
parse_glob_opt() {
  # The attribute regex and csproj discovery are .NET-bound; a non-*.cs glob
  # would silently return 0 (false 'no tests'), so refuse it instead.
  PARSED_GLOB='*.cs'
  if [ "$#" -eq 0 ]; then return; fi
  if [ "$#" -eq 2 ] && [ "$1" = "--glob" ]; then
    case "$2" in *.cs) PARSED_GLOB="$2"; return ;; 
      *) printf "fact-count.sh: testcases/fingerprint support only .cs globs (attribute regex is .NET-bound); got %s\n" "$2" >&2; exit 2 ;; esac
  fi
  usage
}

cmd_files() {
  [ "$#" -eq 2 ] || usage
  local root="$1" glob="$2" out
  out=$(find_pruned "$root" "$glob")
  emit "find '$root' $PRUNE_STR -type f -name '$glob' -print" "$out" "$(count_lines "$out")"
}

cmd_classes() {
  [ "$#" -eq 2 ] || usage
  local root="$1" suffix="$2" out
  out=$(grep -rlE "class \w+$suffix" --include='*.cs' "${GREP_EXCL[@]}" "$root" 2>/dev/null)
  emit "grep -rlE 'class \\w+$suffix' --include='*.cs' $EXCL_STR '$root'" "$out" "$(count_lines "$out")"
}

cmd_callsites() {
  [ "$#" -eq 2 ] || usage
  local root="$1" method="$2" out
  # Leading dot hardcoded — a caller cannot ask for a dotless (declaration +
  # comment) pattern; that is precisely the mislabel this category prevents.
  out=$(grep -rnE "\.$method\(" --include='*.cs' "${GREP_EXCL[@]}" "$root" 2>/dev/null)
  emit "grep -rnE '\\.$method\\(' --include='*.cs' $EXCL_STR '$root'" "$out" "$(count_lines "$out")"
}

cmd_testcases() {
  [ "$#" -ge 1 ] || usage
  local root="$1"; shift
  parse_glob_opt "$@"
  local glob="$PARSED_GLOB" out
  out=$(grep -rhoE '\[(Test|TestMethod|Fact)\]' --include="$glob" "${GREP_EXCL[@]}" "$root" 2>/dev/null)
  emit "grep -rhoE '\\[(Test|TestMethod|Fact)\\]' --include='$glob' $EXCL_STR '$root'" "$out" "$(count_lines "$out")"
}

# fingerprint_project <proj-dir> <glob> — one block: triple + inferred framework.
fingerprint_project() {
  local proj="$1" glob="$2" raw uniq_out tm t fa fw fwcount
  raw=$(grep -rhoE '\[(TestMethod|Test|Fact)\]' --include="$glob" "${GREP_EXCL[@]}" "$proj" 2>/dev/null)
  if [ -n "$raw" ]; then uniq_out=$(printf '%s\n' "$raw" | sort | uniq -c); else uniq_out=""; fi
  tm=$(count_token "$raw" '\[TestMethod\]')
  t=$(count_token "$raw" '\[Test\]')
  fa=$(count_token "$raw" '\[Fact\]')
  # Framework = max wins; tie order TestMethod > Test > Fact.
  fw="unknown"; fwcount=0
  if [ "$tm" -ge "$t" ] && [ "$tm" -ge "$fa" ] && [ "$tm" -gt 0 ]; then fw="MSTest"; fwcount=$tm
  elif [ "$t" -ge "$fa" ] && [ "$t" -gt 0 ]; then fw="NUnit"; fwcount=$t
  elif [ "$fa" -gt 0 ]; then fw="xUnit"; fwcount=$fa
  fi
  printf 'PROJECT: %s\n' "$proj"
  printf 'COMMAND: grep -rhoE '\''\\[(TestMethod|Test|Fact)\\]'\'' --include='\''%s'\'' %s '\''%s'\'' | sort | uniq -c\n' "$glob" "$EXCL_STR" "$proj"
  printf 'OUTPUT:\n'
  print_truncated "$uniq_out"
  printf 'COUNT: TestMethod=%s Test=%s Fact=%s\n' "$tm" "$t" "$fa"
  printf 'FRAMEWORK: %s (max=%s)\n' "$fw" "$fwcount"
}

cmd_fingerprint() {
  [ "$#" -ge 1 ] || usage
  local root="$1"; shift
  parse_glob_opt "$@"
  local glob="$PARSED_GLOB" csproj dir base dbase seen="" found=0
  while IFS= read -r csproj; do
    [ -n "$csproj" ] || continue
    dir="${csproj%/*}"; base="${csproj##*/}"; dbase="${dir##*/}"
    # Test-project convention: csproj name or its dir name reads test/spec.
    printf '%s %s\n' "$base" "$dbase" | grep -qiE 'test|spec' || continue
    case " $seen " in *" $dir "*) continue ;; esac
    seen="$seen $dir"; found=$((found + 1))
    [ "$found" -gt 1 ] && printf '\n'
    fingerprint_project "$dir" "$glob"
  done <<EOF
$(find_pruned "$root" '*.csproj')
EOF
  if [ "$found" -eq 0 ]; then
    printf 'PROJECT: (none)\n'
    printf 'COMMAND: find %s ... -name '\''*.csproj'\'' (test-convention filtered)\n' "$root"
    printf 'OUTPUT:\n(no test-convention *.csproj under %s)\n' "$root"
    printf 'COUNT: 0\n'
  fi
}

[ "$#" -ge 1 ] || usage
sub="$1"; shift
case "$sub" in
  files)       cmd_files "$@" ;;
  classes)     cmd_classes "$@" ;;
  callsites)   cmd_callsites "$@" ;;
  testcases)   cmd_testcases "$@" ;;
  fingerprint) cmd_fingerprint "$@" ;;
  *)           usage ;;
esac
