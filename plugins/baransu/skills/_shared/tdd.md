# Test-Driven Development — TDD reference (authoritative for baransu)

> **Scope**: Every trigger point that writes, modifies, or reviews tests under the
> baransu framework (`/execute`'s `impl-agent`, `/execute`'s `review-agent`, and the
> small tasks implemented directly by the main session after `/think`／`/hunt`
> reroute) treats this document as the **single source of knowledge for "how to design a Test"**.
> This file is translated/localized from mattpocock/skills' TDD skill, with baransu's
> existing RED / GREEN / TDAID vocabulary as inline gloss.
>
> **Source attribution**: Translated from [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd)
> commit `b843cb5ea74b1fe5e58a0fc23cddef9e66076fb8` (2026-04-30), original by Matt Pocock.
>
> **License**: Original is MIT License (Copyright © 2026 Matt Pocock). This file is a
> derivative work, retaining the MIT license; original attribution preserved.
>
> **Trigger points**: before `impl-agent.md` General Principle §1, before `review-agent.md`
> General Principle §3, and the small-task reroute sentences of `/think`／`/hunt`
> (pointing at this file's §7 direct-implementation discipline). All point to this file via passive reference sentences.

---

## 1. Core Principles (four main pillars)

Each principle gives the original key point first, then the baransu context mapping.

### 1.1 Test verifies behavior, not implementation (test-verifies-behavior)

**Principle**: A good test verifies what the system does through the public interface,
not how the system does it. Code can be entirely replaced; the test should not change.
If refactoring internal structure (without changing behavior) makes the test fail, then
the test verifies implementation, not behavior.

**baransu context mapping**:
- In the direct-implementation RED→GREEN cycle (§7), the red-light test written in task 1
  must describe "behavior" rather than "implementation". A test named
  `test_user_can_checkout_with_valid_cart` is behavior; one named
  `test_processOrder_calls_validateInventory` is implementation.
- In `/execute`'s TDAID cycle, the tests written by `impl-agent` are checked in
  `review-agent` Phase 3's test_quality observation dimension for whether they survive a
  hypothetical refactor.
- BAD example: `expect(mockPayment.process).toHaveBeenCalledWith(cart.total)` — verifies an internal
  call; breaks the moment you refactor the payment flow.
- GOOD example: `const result = await checkout(cart, payment); expect(result.status).toBe("confirmed")` —
  verifies an observable outcome; refactoring the internal payment service does not affect this test.

### 1.2 Vertical slicing — one test per round (no horizontal slicing)

**Principle**: It is strictly forbidden to write a pile of tests first and then a pile of
impl (horizontal slicing). What that produces is "imagined tests" that verify shape, not
behavior. **The right answer is a tracer bullet: one test → one impl → the next round is
decided by what the previous round taught you**.

**baransu context mapping**:
- The four tasks of §7.2 (red-light test → confirm red → green-light impl → confirm green)
  are themselves one vertical slice.
- `/execute`'s TDAID cycle is **per-task**; if one task has multiple acceptance criteria
  (AC), `/analyze`'s design layer should have already split the cardinality. `impl-agent`
  does not re-split; it writes per design.md. review-agent catches the process advisory
  "does the diff add ≥ 2 test functions at once without a corresponding split cycle" in Phase 3.
- BAD example: one task contains "add endpoints A, B, C", and impl-agent writes 3 tests in one
  go and runs red, then writes 3 impls and runs green — with no tracer bullet learning anything in between.
- GOOD example: one task maps to one AC in design.md, and impl-agent writes one test, runs red,
  writes impl, runs green; the next AC is handled by the next TDAID round.

### 1.3 Mock only at system boundaries (mock-at-boundaries)

**Principle**: Mock only at system boundaries — external APIs (payment, email), time,
randomness, the file system (sometimes). **Do not mock a class / internal collaborator /
module you own.**

**baransu context mapping**:
- In Phase 3's test_quality observation dimension, review-agent greps the test body for:
  `jest.mock(...)` against a project-internal path, `unittest.mock.patch(...)` against a
  project-internal path, or `expect(internal.method).toHaveBeenCalled`-type assertions.
  A hit yields the advisory "mocking an internal collaborator; consider verifying the
  result through the public interface instead".
- BAD example: `jest.mock('./userRepository')` — mocks an internal module you own.
- GOOD example: `jest.mock('stripe')` — mocks an external SDK; `jest.useFakeTimers()` — mocks a
  system boundary (time).

### 1.4 Refactor only when GREEN

**Principle**: No refactoring of structure while red. Get the test green first, then consider refactoring.

**baransu context mapping**:
- The §7.2 task 3 (write green-light impl) rule "write the minimal implementation sufficient
  to make the red-light test pass, adding nothing the test did not require" directly
  enforces this principle.
- `/execute` `impl-agent.md` General Principle §4 already mandates: "Refactor runs at most once;
  do not refactor proactively unless `refactor_mode: true` is received". Refactor is triggered
  by a second dispatch carrying `refactor_mode: true` after review-agent's Phase 3 assessment.
- BAD example: in the RED phase, modifying the test and the existing impl structure at the same
  time, confusing the source of failure.
- GOOD example: in the RED phase, modify only the test file; in the GREEN phase, write only the
  impl sufficient to pass; refactor is started only after `review-agent` assesses the quality tier.

---

## 2. Interface design: the precondition for testability

A good interface makes testing natural; a bad interface makes testing painful. Three interface design principles:

### 2.1 Accept dependencies, don't create them

```
GOOD: function processOrder(order, paymentGateway) { ... }
BAD:  function processOrder(order) { const gateway = new StripeGateway(); ... }
```

Dependency injection makes mocking the system boundary natural; internal construction forces tests to rely on monkey-patching.

### 2.2 Return results, don't produce side effects

```
GOOD: function calculateDiscount(cart): Discount { ... }
BAD:  function applyDiscount(cart): void { cart.total -= discount; }
```

Return values are assertable; side effects require an extra observation point to be designed.

### 2.3 Small surface area

The fewer methods and the fewer parameters, the simpler the tests.

---

## 3. Deep modules — a small interface wrapping deep logic

From *A Philosophy of Software Design* (Ousterhout).

```
Deep module    = Small interface + Deep implementation   ← preferred
Shallow module = Large interface + Thin implementation   ← avoid
```

When designing, ask yourself:
- Can the number of methods be reduced?
- Can the parameters be simplified?
- Can more complexity be hidden inside the implementation?

A deep module's test focus concentrates on public interface behavior; a shallow module is
the opposite — each thin method must be tested individually, and the test surface area explodes.

---

## 4. SDK-style API — the side benefit for mockability

At the system boundary (external API integration), prefer an SDK-style interface and avoid a generic fetcher:

```
GOOD: const api = {
        getUser: (id) => fetch(`/users/${id}`),
        getOrders: (userId) => fetch(`/users/${userId}/orders`),
        createOrder: (data) => fetch('/orders', {...}),
      };
BAD:  const api = {
        fetch: (endpoint, options) => fetch(endpoint, options),
      };
```

Benefits of SDK-style:
- Each mock returns a single shape — no conditional logic needed.
- The test setup reveals which endpoints the test touches.
- It can be type-safe per-endpoint.

---

## 5. Refactor candidates — only after green

Look at the list below only after GREEN is confirmed:

- **Duplication** → extract a function / class
- **Long methods** → split into private helpers (tests still hit the public interface)
- **Shallow modules** → merge or deepen
- **Feature envy** → move the logic to where the data lives
- **Primitive obsession** → introduce a value object
- **Problems in existing code exposed by new code** → record them, decide whether to handle this round

Run the tests once after each refactor to ensure they are still green.

---

## 6. Anti-pattern quick reference (Anti-patterns)

| Signal | Why it's bad |
|---|---|
| Test name reads "X calls Y" | Describes HOW not WHAT; breaks on refactor. |
| Test mocks its own module / class | Couples to implementation details; does not verify behavior. |
| Multiple tests then multiple impls in one round | Horizontal slicing; produces imagined tests. |
| Test passes only because the spy count matches | Verifies an internal call; not the observable outcome. |
| Test verifies the result directly via `db.query(...)` | Bypasses the interface; queries the DB instead of writing a retrieve API. |
| Refactoring the existing impl during the RED phase | Confuses the source of failure; violates "refactor only when GREEN". |

Cross-skill behavioral anti-patterns (including the red/green discipline items) are in `../../rules/anti-patterns.md`; this table collects only test-design-layer anti-patterns.

---

## 7. The red/green gate for direct implementation (document discipline)

When a small task bypasses the `/execute` pipeline and is implemented directly by the main
session (for example, a `/think`-approved plan or the single change point after `/hunt`
diagnosis converges), the red/green gate operates as **document discipline (discipline-suggested)**:
no orchestrator gatekeeps for you; the implementer builds their own red/green task list per
this section, goes red first then green, and writes the implementation only after the red is
confirmed. If the approved plan already has an upstream work journal (`.claude/think/*.html`),
out-of-spec decisions made during implementation are appended to that journal's "執行日誌"
section per the `output-journal.md` contract.

### 7.1 Classify first: TDD or cosmetic

cosmetic = the change has no semantic impact on runtime behavior, limited to four kinds:

- comment edits (comment modifications)
- dead import removal (removing dead imports)
- identifier rename with no behavior change (identifier rename with no behavior change)
- pure formatting (pure formatting adjustments)

When unsure, always take the TDD path. Once made, the classification is final; do not
re-classify mid-execution. The cosmetic path implements directly and writes no tests; the
TDD path proceeds to §7.2.

### 7.2 Build your own red/green task list (four tasks)

Build the complete task list before executing, so the completion criteria are visible from
the start. The four tasks are themselves one vertical slice (§1.2):

1. Write the red-light test — written only for the new behavior (§1.1); do not write tests for existing behavior
2. Confirm red — run the test, expect failure
3. Write the green-light impl — write the minimal implementation sufficient to make the red-light test pass, adding nothing the test did not require (§1.4)
4. Confirm green — run the tests, all pass with no regression

The order is fixed: do not enter implementation before red is confirmed; do not modify the test during the green phase (the test is the spec).

### 7.3 Gate decisions

**Confirm red**:

| Result | Action |
|---|---|
| Test fails | Red confirmed; proceed to the green-light impl. |
| Test passes | Stop. The test verifies existing behavior, not new behavior; rewrite the test and re-confirm red. |
| compile error | The test itself has a syntax error; fix the test and restart from task 1, not counted toward the green retry count. |

**Confirm green**:

| Result | Action |
|---|---|
| All pass, no regression | Green confirmed; done. |
| Test fails (1st time) | Modify the implementation and re-run directly. |
| Test fails (2nd time) | Stop. If the direction is in doubt, return to `/think` to refocus, then retry. |
| compile error | Fix and re-run; not counted toward the retry count. |

In `/execute`'s TDAID pipeline, the authoritative counting rules for compile error and `failure_count` are in `plugins/baransu/skills/execute/SKILL.md`; this file only references them, it does not duplicate the rule text.

### 7.4 Per-cycle self-check list

At the end of each RED→GREEN round, ask yourself:

```
[ ] Test 描述 behavior、不描述 implementation
[ ] Test 只用 public interface
[ ] Test 在內部 refactor 後仍會 pass
[ ] Code 是 minimal、夠通過此 test 而已
[ ] 沒添加未被任何 test 要求的功能
```

---

## 8. baransu-specific trigger-point record

This file is referenced by the following trigger points:

| Trigger point | Reference location | Reference sentence |
|---|---|---|
| `/execute` impl-agent | `plugins/baransu/agents/impl-agent.md` General Principle §1, before the Red gate | "Before writing tests, read `plugins/baransu/skills/_shared/tdd.md`." |
| `/execute` review-agent | `plugins/baransu/agents/review-agent.md` before General Principle §3 | "Before reviewing, read `plugins/baransu/skills/_shared/tdd.md` and check test quality per its principles." |
| `/think` small-task reroute | `plugins/baransu/skills/think/SKILL.md` Stage G downstream split | Small tasks reroute to this file's §7: the main session builds its own red/green task list per document discipline and implements directly. |
| `/hunt` fix reroute | `plugins/baransu/skills/hunt/SKILL.md` fix-suggestion split | Single change-point fixes reroute to this file's §7 direct-implementation discipline. |

In Phase 3, besides checking test quality per this file's principles, review-agent must report the four green_proof fields (see
`plugins/baransu/agents/review-agent.md` General Principle §3 and the 5-tier required matrix).

---

## 9. Original-section cross-reference table

When cross-referencing externally, cite this file's section + the mattpocock original section:

| This file's section | mattpocock original |
|---|---|
| §1.1 test-verifies-behavior | SKILL.md "Philosophy" section, all of tests.md |
| §1.2 vertical slicing | SKILL.md "Anti-Pattern: Horizontal Slices" |
| §1.3 mock-at-boundaries | mocking.md |
| §1.4 refactor only when GREEN | SKILL.md "Refactor" section |
| §2 Interface design | interface-design.md |
| §3 Deep modules | deep-modules.md |
| §5 Refactor candidates | refactoring.md |
