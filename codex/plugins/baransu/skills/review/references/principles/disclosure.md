# Disclosure

What leaves the system, or sits where someone can read it, reveals only what its reader is meant to have: no stray fields, no secrets, and no difference an attacker can read as an answer to a question they could not ask directly.

**Why:** An allowed response can still leak. A serializer that sends the whole object, a log line with a token, or an error that says "no such user" rather than "wrong password" discloses through a door the access check already opened.

**Pattern:**
1. **Name who receives each output.** A response, an error, a log, an export file, a notification, a search result — and who can read it, including log readers, support tools, and third parties it is forwarded to.
2. **Keep secrets and personal data out of readable places.** Not in source or config committed to the repo, logs, errors, responses, or URLs; logging URLs or non-sensitive data is fine by precedent. Risk: 資料外洩.
3. **Send the fields the reader may have, not the object.** Whole-object serialization, an ORM model returned as-is, or a debug field left in a response over-fetches; for an export, the columns it writes are part of its output.
4. **Do not let search, filter, or sort answer for a hidden field.** A query over a field the requester cannot read reveals its values through which results match or the order they come back in.
5. **Make denials indistinguishable where existence is secret.** Different messages, status codes, response sizes, or a measurable timing difference between "does not exist" and "not allowed" let an attacker enumerate accounts or records.
6. **Verify a suspected secret before flagging it.** An example file, a marked test credential, a key meant to be public, or a checksum hash is not a leak.
7. **Protect confidential data in transit and at rest with adequate cryptography.** A plaintext channel for credentials or personal data, or a broken cipher or mode, is the finding; strength is judged against what the data is.

**The test:** For each output the change shapes, who reads it, and what can they learn from it — its fields, its presence, its order, its timing — that they are not meant to?

**You skipped this when** a review accepted "the user is authorized for this endpoint" as the answer to what the endpoint reveals.

Distinct from `access-control.md`, which decides whether the reader may reach the resource and which rows a route returns; `authentication.md`, which judges whether a credential is strong enough to stand for an identity, while where a credential is exposed is here.
