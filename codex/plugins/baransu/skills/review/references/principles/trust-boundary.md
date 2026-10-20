# Trust boundary

Data from outside the system is untrusted until it is parsed and checked at the boundary where it enters; inside, typed data is trusted only for what that check actually guaranteed. A trust-boundary problem is a concrete path by which untrusted data — a request, a file, a message, a model's output, or a value stored earlier — reaches a dangerous operation, shown from source to sink with the control that should have stopped it, and opened or relied on by this change.

**Why:** Scattered validation is noisy and gives false safety; a check one component performs is trusted by the next only as far as both agree on what it checked. The hole is usually where one side's guarantee is narrower than the other side's assumption.

**Pattern:**
1. **Read the project's own security model first.** Its frameworks, sanitizers, parsers, and established secure patterns. A change that deviates from them, or adds a new entry point beside them, is where to look.
2. **Compare what one side guarantees with what the next assumes.** An upstream check is relied on only for the property it actually established — truncation, normalization, encoding, type, length. Data read back from storage was written by every path that writes that store, not only the one that validated on the way in. Risk: 驗證落差.
3. **Trace source to sink, and name the control.** Show where the untrusted data enters, the dangerous operation it reaches, and the strongest control visible on the path between them; a finding that names no control has not shown why the path is open.
4. **Look for the known injection classes.** SQL, NoSQL, shell, templates, XML entities, `eval`, deserialization (pickle, YAML), path traversal, XSS outside a framework's escaping, and SSRF through a URL the user stores and the server fetches later — a webhook, a callback, an import — unless the scheme is pinned, the address is checked at connect time, and redirects are refused.
5. **Check quantities as the domain's type at entry.** A count, price, size, or index from the requester is checked for negative, zero, overflow, precision loss, and string-to-number coercion where it is parsed, not where it is spent.
6. **Follow stored data into its later use.** A value that was safe when stored becomes dangerous when a later step uses it as a path, a template, a regex, a URL, a query fragment, or a policy expression; the source is its original writer, the sink is that later use.
7. **Treat a model's output as an untrusted source when it can act.** Output that drives a tool call, a durable write, another principal's context, or a sink the requester cannot reach directly is untrusted input to that sink; output seen only by the requester who wrote the prompt is not.
8. **Trust what precedent trusts.** Environment variables and CLI flags; React and Angular output unless an unsafe escape hatch is used; client-side code, whose checks the server owns.

**The test:** Can you name the source, the sink, the control between them, and the property that control fails to guarantee — each with a citation?

**You skipped this when** a finding accepts "validated upstream" without saying what upstream validated, or follows input only as far as the first function that stores it.

Distinct from `authentication.md`, which judges whether an identity was established; `access-control.md`, which judges whether that identity may act — tenant scope belongs there, format guarantees here; and `disclosure.md`, which judges what leaves the system. How a security finding is stated and graded is `security-finding.md`.
