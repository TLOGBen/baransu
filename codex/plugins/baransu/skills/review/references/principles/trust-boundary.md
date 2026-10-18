# Trust boundary

Data from outside the system is untrusted until it is parsed and checked at the boundary where it enters; inside, typed data is trusted. A security problem is a concrete path by which untrusted input, a stolen credential, or a crafted command reaches something it should not, shown from source to sink, and opened or relied on by this change.

**Why:** Scattered validation is noisy and gives false safety, and theoretical warnings bury the one real hole. A finding a security engineer would not raise with confidence in a PR review costs the reader more than it saves.

**Pattern:**
1. **Read the project's own security model first.** Its frameworks, sanitizers, auth middleware, and established secure patterns. A change that deviates from them, or adds a new attack surface beside them, is where to look; a layer that does not re-validate what an upstream boundary already checked is not a finding.
2. **Trace source to sink.** Show where untrusted data enters — a request, a file of unknown origin, an external API, a message — and the dangerous operation it reaches.
3. **Look for the known classes.** Injection into SQL, NoSQL, shell, templates, XML entities, `eval`, or deserialization (pickle, YAML); path traversal; authentication or authorization bypass, privilege escalation, session or token flaws; hardcoded secrets, weak cryptography or randomness, skipped certificate checks; secrets or personal data in logs, errors, or responses; XSS outside a framework's escaping.
4. **Report only a concrete, exploitable path.** "An attacker might..." without an exposed surface in the present code is not a finding. Exposure only on a local network can still be severe.
5. **Leave these out unless a concrete path makes them real.** Denial of service and resource exhaustion; rate limits; secrets on disk that are otherwise secured; missing hardening; theoretical races or timing attacks; outdated dependencies; memory safety in memory-safe languages; test-only files; log spoofing; SSRF that controls only the path; user content in AI prompts; regex injection or regex DoS; documentation files; missing audit logs.
6. **Trust what precedent trusts.** Environment variables and CLI flags; UUIDs as unguessable; React and Angular output unless an unsafe escape hatch is used; client-side code, whose checks the server owns; logging URLs or non-sensitive data.
7. **Verify a suspected secret before flagging it.** An example file, a marked test credential, a key meant to be public, or a checksum hash is not a leak.
8. **Fit the threat model and the fix to it.** A purely local tool has no network threat model; never push a heavy countermeasure down a low-risk path.
9. **Ground the weakness.** Name the CWE, the OWASP entry, or the concrete exploit; a "best practice" with none behind it is not a problem.

**The test:** Can you write the exploit as a sentence — who sends what, through which line, to reach which operation — with every step cited?

**You skipped this when** a security finding has no source, no sink, or no attacker who could actually send the input.
