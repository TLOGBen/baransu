---
name: oversize-listing
description: Deliberately oversize listing stub: description and when_to_use each stay under their own caps but sum to 1600 characters. pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-pad-p
when_to_use: listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,listing-budget,
---

# oversize-listing

Stub whose only defect is the one the listing-budget check targets.

## Outcome Contract

- **Outcome**: prove the listing-budget check produces a violation on bad input
- **Done when**: verify-skills exits 1 naming this stub and the listing-budget check
- **Evidence**: tests/scripts/test_verify_skills.py asserts the violation message
- **Output**: one violation line in the verifier output
- **Automation**: none — data-only negative fixture
