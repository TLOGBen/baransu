---
name: claude-helper
description: Deliberately valid stub whose name contains the reserved word so the reserved-word check fires.
---

# claude-helper

Stub whose only defect is the one the reserved-word check targets.

## Outcome Contract

- **Outcome**: prove the reserved-word check produces a violation on bad input
- **Done when**: verify-skills exits 1 naming this stub and the reserved-word check
- **Evidence**: tests/scripts/test_verify_skills.py asserts the violation message
- **Output**: one violation line in the verifier output
- **Automation**: none — data-only negative fixture
