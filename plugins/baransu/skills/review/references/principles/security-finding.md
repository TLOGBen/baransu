# Security finding

A security finding states a concrete crossing: a lower-trust actor, what it sends or does, the control that should have stopped it, the boundary it crosses, a different principal or resource it affects, and the result — each cited, claimed no stronger than the evidence reaches, and fixed where the last trusted decision is made.

**Why:** A security finding is read with alarm, so an inflated or theoretical one costs the reader more than a missed style point, and a true one stated loosely gets argued away. The six parts are what make it checkable.

**Pattern:**
1. **State the six parts, each cited.** The actor and its starting capability; the input or action; the control that should reject, bind, isolate, limit, or revoke it; the boundary; the affected principal or resource; the result. A part that cannot be cited makes the finding uncertain, naming that part.
2. **Require a different party.** Authority the actor already holds, or harm only to itself, crosses no boundary; a user deleting their own data, or a model doing what its own requester asked with the requester's own rights, is not a finding.
3. **Claim no more than the ceiling in `index.md` allows.** A crash is not code execution, a same-principal action is not privilege gain, an unbounded string is not injection.
4. **Show a concrete, exploitable path.** "An attacker might..." without an exposed surface in the present code is not a finding. Exposure only on a local network can still be severe.
5. **Leave these out unless a concrete path makes them real.** Denial of service and resource exhaustion; rate limits; secrets on disk that are otherwise secured; missing hardening; theoretical races or timing attacks; outdated dependencies; memory safety in memory-safe languages; test-only files; log spoofing; SSRF that controls only the path; regex injection or regex DoS; documentation files; missing audit logs.
6. **Ground the weakness.** Name the CWE, the OWASP entry, or the concrete exploit; a "best practice" with none behind it is not a problem.
7. **Fit the threat model.** A purely local tool has no network threat model; judge a path by who can actually reach it.
8. **Place the fix at the last trusted decision point.** The bedrock names the invariant and the narrowest change that enforces it where the system last decides with trusted information, with a regression case; never push a heavy countermeasure down a low-risk path.
9. **Read severity from the result against the security anchors in `index.md`.** The anchors measure what a lower-trust actor gains over another party, not whether normal use still works.

**The test:** Can you write the finding as one sentence — who, sending what, past which control, across which boundary, does what to whom — with every part cited, and does its severity match its anchor?

**You skipped this when** a security finding has no control, no affected party other than the actor, or a severity read from the usability scale.

Distinct from `trust-boundary.md`, `authentication.md`, `access-control.md`, and `disclosure.md`, which say where to look; this one says how what was found is stated, bounded, and fixed.
