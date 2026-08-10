# Distillation candidate matrix

Use this as the single admission authority before a candidate becomes durable
or public guidance. It applies to lessons drawn from a conversation, incident,
external repository or release log, or private memory. It is not a privacy
gate for local read-only inspection or inspector dispatch.

## Five questions

| Question | Required decision evidence | Failed answer |
|---|---|---|
| Recurrence evidence | Show either (a) independent cases across fixes, releases, agents, or user reports, or (b) one reproducible failure plus a red-on-absence behavioral verifier. Repeated wording in one conversation is one case, not recurrence. | DEFER or REJECT if neither evidence route exists; it cannot PROMOTE. |
| Durable invariant | State a stable rule rather than a dated incident summary. | DEFER or REJECT. |
| Target layer | Select exactly one owner: `project`, `shared-skill`, `global-rule`, or `private-memory`. The owner is not a verifier. | REROUTE or REJECT. |
| Verifier | Name a separate executable check, artifact assertion, or runtime smoke. Demonstrate red-on-absence evidence through a mutation or pre-fix failure when the candidate behavior is absent; a text-presence grep alone is not sufficient. | DEFER or REJECT. |
| Project/private contamination | Necessary project-specific facts select `project` and REROUTE; private user or machine facts select `private-memory` and REROUTE. Strip only candidates destined for public/shared guidance of project/customer names, private paths, issue/build numbers, secrets, machine state, and unpublished release facts; if that public/shared candidate cannot be separated, REJECT it. | REROUTE for `project` or `private-memory`; REJECT inseparable public/shared contamination. |

The verifier is orthogonal to the owner layer. Exercise the stated behavior,
not merely its wording: when the behavior is absent, the verifier must fail
red. Text that says a rule exists, or a grep that finds that text, is never
behavioral proof.

## Disposition

- `PROMOTE` — all five questions pass and the selected owner is the authorized
  current target.
- `REROUTE` — the candidate is durable but its selected owner is another
  layer; name that owner and stop.
- `DEFER` — recurrence, invariant, or behavioral verifier is not yet ready;
  retain no durable/public change.
- `REJECT` — the candidate is unsound or project/private contamination cannot
  be separated from it.

`REROUTE`, `DEFER`, and `REJECT` are off-ramps: they never mutate another
owner layer. Record the outcome only in existing prose when a caller has such
a surface, using `候選處置：{PROMOTE|REROUTE|DEFER|REJECT} — {一行理由}`.
