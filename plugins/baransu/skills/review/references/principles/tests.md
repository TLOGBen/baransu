# Tests

A test is a claim about what the code does for its users, made at the interface they use. It proves a behaviour only when breaking that behaviour would make it fail and changing only the internals would not.

**Why:** A test that passes either way proves nothing and gives false confidence; a test pinned to internals breaks on every refactor and still catches no bug. Tests written to have tests are the first kind.

**Pattern:**
1. **Imagine breaking the behaviour.** A wrong value, a skipped effect, an effect done twice. If the test would still pass, it is a phenomenon, not evidence. Usual causes: an assertion looser than the contract, an expected value computed the way the code computes it, a restated constant that never runs the code that reads it, an assertion on data the test built itself.
2. **Imagine changing only the internals.** If the test would fail while every observable result stays the same — it mocks an internal collaborator, tests a private method, counts calls, or verifies through a side channel instead of the interface — it is pinned to the implementation.
3. **Take the expected value from an independent source:** a known literal, a worked example, the requirement — never a run of the code under test.
4. **Let the contract decide, not the assertion's shape.** What a mocked external service receives is behaviour; a call to an internal helper is not. The error type callers branch on is the contract; an exact message no caller reads is not.
5. **Mock only at system boundaries** — external services, time, randomness, sometimes the database or file system. A mock of the claimed layer does not cover it; a layer with no tests is read, not exempted.
6. **Prove the path, not only the unit.** A behaviour that crosses several units needs evidence across them; an integration boundary needs its full path covered.
7. **Ask risky logic for one test that fails when it breaks.** A branch, a parser, money, security, a data write, a bug fix — one good test, not coverage.
8. **Ask "unchanged behaviour" for a recorded comparison** on inputs development did not use, stating the n it rests on (rule of three, `../../../_shared/modeling.md`); it holds on identical bytes or inside a declared tolerance, each mask listed with its why.

**The test:** For each test a claim rests on, read its assertion against the requirement: would it go red if the behaviour broke, and stay green if only the internals moved?

**You skipped this when** a test was counted as evidence because it exists or passes, without reading what its assertion checks.
