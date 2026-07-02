---
name: some-other-name
description: Deliberately valid description on a stub whose frontmatter name does not match its directory name.
---

# name-mismatch

Stub whose only defect is the one the name==directory check targets.

## Outcome Contract

- **Outcome**: prove the name==directory check produces a violation on bad input
- **Done when**: verify-skills exits 1 naming this stub and the name==directory check
- **Evidence**: tests/scripts/test_verify_skills.py asserts the violation message
- **Output**: one violation line in the verifier output
- **Automation**: none — data-only negative fixture
