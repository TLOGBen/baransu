# fact-check — counting-noun discipline for quantitative claims

> **Scope**: the canonical statement of the counting-noun discipline shared by baransu
> skills that re-verify a target's quantitative claims. `/think` inlines the same rule
> set in its Stage D claim-cite-first (the counting-noun taxonomy + literal-number rule);
> `/review`'s dispatcher references this file at Stage 1.6. The two are kept in sync by
> hand — **do not edit `/think` when changing this file**. What follows is a set of
> ecosystem-agnostic *principles*, not a runnable script: every command shown is a
> clearly-marked illustration of one stack, never required machinery.

## Purpose

A quantitative claim is only as trustworthy as the command that produced it. A count
labelled with the wrong noun — files where the claim needs classes, call sites where it
needs test cases — reads as verified yet proves nothing. The discipline: fix ONE command
per counted noun so a re-run is reproducible and a mislabel is mechanically visible, and
label a count ONLY with the noun that command actually enumerated. A reproducible number
produced under the wrong pattern is not evidence — it is exactly how a call-site count
masquerades as a test-case count.

Two rules bracket every count:

- **Scope from the repository root**, excluding this ecosystem's generated / build-output
  and vendored-dependency directories — whatever they are for the stack (e.g. `bin/` `obj/`
  in .NET, `node_modules/` `dist/` in Node, `target/` in Rust/Java, `__pycache__/` `.venv/`
  in Python). A search rooted in a subdirectory licenses no claim about the whole repo.
- **Anchor the prose number to the literal output.** The number written in prose MUST be
  the literal number in the pasted fragment of the same command.

## The counting nouns

Each noun binds to a distinct kind of command. The binding — not the exact syntax — is
what carries the discipline; the syntax shown is one illustration and must be re-derived
for the stack under check.

1. **檔案數 files** — a file listing.
   Backs only 「檔案數」, never 「類別／實作數」: a directory of source files also holds
   base / abstract / factory / interface files that declare no concrete type, so a file
   count over-states classes. (e.g. in a C-family layout, `find … -name '<src-ext>' | wc -l`.)

2. **類別數 classes / types** — declaration sites, never a directory file listing.
   Count a type by matching its declaration in the language's own syntax; the file count
   and the declaration count are different numbers. (e.g. `grep -rlE 'class \w+<Suffix>'`
   in a `class`-keyword language; a `struct` / `type … struct` / `impl` form elsewhere.)

3. **呼叫點 call sites** — invocations only.
   The pattern MUST match the invocation form so it EXCLUDES the declaration, the
   interface / signature, and comment lines — a pattern that also matches the declaration
   can never back 「呼叫點」. The exact syntax is language-specific, not a fixed leading dot.
   (e.g. in a dot-notation language the leading dot in `\.<Method>\(` drops the declaration
   that a bare `<Method>(` would still match; free-function `func()`, UFCS, pipeline `|>`,
   or Lisp `(method …)` languages each need their own form.)

4. **測試案例數 test cases** — a per-case marker count, never a call-site or file count.
   Count by this framework's own per-case marker — an attribute, a decorator, or a naming
   convention — each of which identifies exactly one case. (e.g. `[Test]` / `[Fact]`
   attributes in .NET, `def test_` / `@pytest.mark` in Python, `it(` / `test(` in JS,
   `func TestXxx` in Go, `#[test]` in Rust.)

## Framework-identity claims

A claim that "this project uses framework X" must be backed by the actual in-repo
fingerprint — the marker that framework, and only that framework, leaves in the source —
not assumed from a filename or from memory. A pasted fragment whose markers belong to
framework A cannot back a claim about framework B.

## Existence and absence claims

An 「X 存在」 claim maps to the noun of the artifact: a file's existence cites a file
listing that prints its path, a class the declaration search, a test suite the test-case
marker count. **Existence** = the command returning > 0 with the artifact visible in the
pasted fragment. **Absence** may be asserted ONLY when a repo-root-scoped command genuinely
returns 0 across every candidate location — never from a subdirectory search, never from
not having looked. When several directories could hold the artifact, the absence command
must span all of them; a zero from one subtree does not license 「不存在」 for the repo.

## Coverage claims

A coverage claim (「X 已被測試」 / 「安全網充足」 / 「有測試保護，可安全重構」) is not discharged by
a test that merely names or references the unit under change. Confirm the test drives the
**real** implementation and asserts on its **actual** behavior. A reference to that unit
sitting inside a mock / stub / spy / fake construct — the test doubling it out (e.g.
`vi.mock` / `jest.mock` in JS, `Mock<>` / a substitute in .NET, `patch` in Python,
`Mockito.mock` in Java) — is **anti-coverage**: it proves the test deliberately replaces
that code with a stand-in and exercises none of it. When counting a layer's coverage,
exclude every reference that sits inside a mocking construct; a symbol grep that counts
mock declarations as call sites inflates coverage with the exact opposite of coverage. A
spec named for the layer it targets but which mocks that very layer covers it **zero** —
the coverage lives at whatever layer actually runs unmocked and is asserted on.

## Don't swap one unverified figure for another

Revising a claim under challenge does not discharge it. If a premise is refuted or unproven,
replacing it with a second unverified premise ("actually it's N, not M") re-opens the same
obligation: the replacement number needs its own command plus quoted fragment before
anything downstream leans on it. A drifted or swapped figure that was never re-run is
`(inferred: 未實查)`, not a correction.

## Literal-number anchoring

A `(verified: …)` tag is earned only by carrying the exact command AND a quoted fragment
of its output. A tag whose quote holds no number, or a number different from the prose (a
figure that drifted 34→32), or a fragment whose noun / markers do not match the claimed
one, downgrades to `(inferred: 未實查)`. A bare tool name — `(verified: find)`,
`(verified: grep)` — never qualifies.

## Never re-run the target's own command

Re-verification means an INDEPENDENT command that counts the claimed noun from the repo
root. Re-running the command the target itself used proves reproducibility, not
noun-correctness — the exact way a dotless pattern passes a declaration off as a call site.
A tag the target already carries is a claim about the repo, not in-session evidence, and
does not discharge the row.

## Fact-table entry shape

One row per load-bearing quantitative / existence claim:

| # | claim quoted from target | noun | command run | pasted output fragment | verdict ✔/✘ |
|---|--------------------------|------|-------------|------------------------|-------------|

`noun` is one of the counting nouns above. `verdict` is `✔` only when the pasted fragment's
literal number AND its noun both match the claim; otherwise `✘` (including a number
reproduced under a pattern that counts a different noun — a mislabel).

## Fail-closed rule

When the environment cannot execute commands (headless / no shell), every quantitative
claim is marked **unverifiable-by-harness** — never assumed true. A row that cannot be
filled with real pasted output carries no `✔`, and the consuming skill's Unverified-claims
hard stop fires. Fail closed: an unrunnable check blocks, it never passes.
