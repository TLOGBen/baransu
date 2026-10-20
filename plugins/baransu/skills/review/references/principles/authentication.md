# Authentication

The identity the system acts on — who is logged in, which service is calling, which peer it is talking to — was established by a check that cannot be skipped or forged, and stays valid only as long as the evidence behind it does.

**Why:** Every later decision trusts the identity it is handed. An identity taken from an unverified token, a guessable value, or an unchecked peer turns every authorization check downstream into a check on the attacker's chosen name.

**Pattern:**
1. **Establish identity on every path.** Each entry point that acts for a principal — routes, jobs, sockets, webhooks, internal endpoints exposed beyond the process — runs the authentication the project's model requires; a path that reaches the same handler without it is the finding. Risk: 認證繞過.
2. **Verify sessions and tokens fully.** Signature, algorithm, issuer, audience, expiry, and revocation are checked, not only decoded; a session identifier is rotated at login and bound to its principal, so a fixed or replayed one does not carry another user's session. Risk: 偽冒身分.
3. **Make secret values unguessable.** Session ids, reset and invite tokens, API keys, and identifiers used as capabilities come from a cryptographic source; a UUIDv4 is unguessable by precedent, a counter, timestamp, or non-cryptographic random value is not.
4. **Verify the other side and store credentials one way.** Certificate and host checks are not skipped for a peer whose identity matters; passwords are stored with a dedicated slow hash, never reversible encryption or a fast digest.

**The test:** For each principal the change acts for, which line established that identity, and could an attacker reach the same code with an identity they chose?

**You skipped this when** a finding about authorization accepted the caller's identity without asking where it came from.

Distinct from `access-control.md`, which takes an established identity and judges what it may do; a revoked token still accepted is here, a revoked permission still honoured is there. Where a credential is exposed is `disclosure.md`.
