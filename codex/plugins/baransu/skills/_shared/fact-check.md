# fact-check — counting-noun discipline for quantitative claims

> **Scope**: the canonical source for the counting-noun discipline shared by baransu
> skills that re-verify a target's quantitative claims. `/think` inlines this same rule
> set as of its v4 Stage D claim-cite-first (the four-noun taxonomy + literal-number
> rule); `/review`'s dispatcher fact-table step references this file. The two are kept
> in sync by hand — **do not edit `/think` when changing this file**. The fifth category
> (framework fingerprint) lives here only.

## Purpose

A quantitative claim is only as trustworthy as the command that produced it. A count
labelled with the wrong noun — files where the claim needs classes, call sites where it
needs test cases — reads as verified yet proves nothing. This file fixes one canonical
command TEMPLATE per countable noun so a re-run is reproducible and a mislabel is
mechanically visible. A count may be labelled ONLY with the noun whose template produced
it. All templates are `REPO_ROOT`-scoped and exclude the ecosystem's generated /
build-output dirs — `bin/` and `obj/` in .NET, and the equivalent elsewhere
(`node_modules/`, `dist/`, `target/`, `__pycache__/`).

## The five categories

Each entry: the noun the count may back · the canonical command template · the failure
it prevents.

1. **檔案數 files** — a file listing.
   `find . -path '*/bin/*' -prune -o -path '*/obj/*' -prune -o -name '*.cs' -print | wc -l`
   Backs only 「檔案數」, never 「類別／實作數」: the directory also holds base / factory /
   bean files that declare no concrete class, so a file count over-states classes.

2. **類別數 classes** — declaration sites, never a directory file listing.
   `grep -rlE 'class \w+<Suffix>' --include='*.cs' --exclude-dir=bin --exclude-dir=obj . | wc -l`

3. **呼叫點 call sites** — dot-prefixed invocations.
   `grep -rnE '\.<Method>\(' --include='*.cs' --exclude-dir=bin --exclude-dir=obj .`
   The leading dot is MANDATORY, not decoration: bare `<Method>(` also matches the
   declaration, the interface signature, and comment lines, so it may never back 「呼叫點」.

4. **測試案例數 test cases** — a test-attribute count, never a call-site or file count.
   `grep -rhoE '\[(Test|TestMethod|Fact)\]' --include='*.cs' --exclude-dir=bin --exclude-dir=obj . | wc -l`

5. **框架指紋 framework fingerprint** — per test project, the triple of attribute counts.
   Run once per `*.csproj` test-project directory:
   `grep -rhoE '\[(TestMethod|Test|Fact)\]' --include='*.cs' <proj-dir> | sort | uniq -c`
   The max of the three identifies the framework — `[TestMethod]`→MSTest, `[Test]`→NUnit,
   `[Fact]`→xUnit. A framework-identity claim ("this project uses xUnit") may cite ONLY
   this row: a pasted fragment whose attributes read `[Test]` cannot back a claim of xUnit.

Non-.NET ecosystems substitute the language's file glob and test attributes / decorators
into the same templates (`*.py` + `def test_` / `@pytest.mark`; `*.ts` + `it(` / `test(`);
the noun-to-template binding and the leading-dot rule are unchanged.

## Executor

When a shell is available, fill each row by running
`plugins/baransu/skills/review/scripts/fact-count.sh <category> <root> …` — the
script IS the template (the leading dot, the excludes, and the per-project
fingerprint are all hardcoded); the prose templates above stay the spec and the
fallback when no shell exists.

**Template-authority rule (structural).** A row's `command run` MUST be the
category's canonical template — the script subcommand, or the verbatim prose
template above. Re-running the TARGET's own command proves reproducibility only,
never earns `✔`; a row whose command deviates from its category's template is
itself marked `✘ (template-deviation)`, because a reproducible number under the
wrong pattern is exactly how a dotless `25` passed as 呼叫點.

## Existence claims

An 「X 存在」 claim maps to the category of the artifact's noun: a file's existence cites
the files template (its output listing the path), a class the classes template, a test
suite the test-cases or fingerprint template. Existence = the category's command returning
> 0 with the artifact visible in the pasted fragment; absence may be asserted only when
the repo-root-scoped template genuinely returns 0.

## Literal-number anchoring

The number written in prose MUST be the literal number in the pasted output fragment of
the SAME fact-table entry. A `(verified: …)` tag is earned only by carrying the exact
command AND a quoted fragment of its output. A tag whose quote holds no number, or a
number different from the prose (a figure that drifted 34→32), or a fragment whose noun /
attributes do not match the claimed one, downgrades to `(inferred: 未實查)`.

## Fact-table entry shape

One row per load-bearing quantitative / existence claim:

| # | claim quoted from target | category | command run | pasted output fragment | verdict ✔/✘ |
|---|--------------------------|----------|-------------|------------------------|-------------|

`category` is one of the five above. `verdict` is `✔` only when the pasted fragment's
literal number AND noun both match the claim; otherwise `✘`.

## Fail-closed rule

When the environment cannot execute commands (headless / no shell), every quantitative
claim is marked **unverifiable-by-harness** — never assumed true. A row that cannot be
filled with real pasted output carries no `✔`, and the consuming skill's Unverified-claims
hard stop fires. Fail closed: an unrunnable check blocks, it never passes.
