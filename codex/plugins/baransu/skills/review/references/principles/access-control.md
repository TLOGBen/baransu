# Access control

Every way to an action or a resource is gated by the check the business rule requires — the right check, equally strong on every route, decided at the moment of use, and failing closed when anything it depends on is missing.

**Why:** A check that exists is easy to see and easy to trust; a check that tests the wrong thing, guards one route of three, or opens when its config is absent looks the same in a diff. The breach is the route nobody compared.

**Pattern:**
1. **Name the actor, the owner, and the rule.** Who acts, whose resource it is, and where the rule that decides between them is written — a spec, a policy, a role table, the code that owns the invariant.
2. **Check that the check is the one the rule needs.** Ownership versus role; object level versus function level; the id actually fetched versus the id the request passed; the record's tenant versus the tenant the request names. Risk: 越權.
3. **Compare every route to the same effect.** API, UI, batch, admin, GraphQL, webhook, export, backup, and search that reach the same records or action carry checks of equal strength, not merely a check each; for an export or a backup, the rows it returns are part of that route.
4. **Fail closed.** When a config value is missing, a feature flag is off, a dependency is down, or a migration is half done, the gate denies; a default that allows is a decision the rule must state. Risk: 預設放行.
5. **Apply current rights to restored data.** Restore, rollback, undelete, and import run today's authorization and validation; old data carries no old rights, and an import cannot write where its user cannot.
6. **Decide at the time of use.** A permission checked once and cached, or checked before a long step, names the window that revocation and cache expiry leave open, and that window is judged against the rule.
7. **Keep authority from growing.** Delegation, token refresh, caching, a role change, or composing two capabilities never yields an operation the resulting principal should not have; name that operation.
8. **Do not count an instruction to a model as a control.** A guardrail prompt, a system instruction, or a classifier's judgment is not a gate; the gate is deterministic code outside the model — tool scope, credential scope, an approval step.
9. **Bind actions to the principal who asked for them.** Content from one party that causes a model or automation to act under another principal's valid authority, without that principal approving the exact action, is a failure even when every individual call is authorized. Risk: 動作綁定失效.

**The test:** For each action or resource the change touches, list every route to it and the check on each: is each the check the rule names, equally strong, made at use, and closed when its inputs are missing?

**You skipped this when** a finding says "the endpoint checks permissions" without saying which permission, or the review read one route to a resource and not the others.

Distinct from `authentication.md`, which establishes who the actor is; `disclosure.md`, which judges which fields and signals an allowed response carries — rows a route returns are here, fields within them there; and `trust-boundary.md`, which owns format guarantees while tenant scope is here.
