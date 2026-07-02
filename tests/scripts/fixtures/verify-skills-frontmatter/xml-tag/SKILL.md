---
name: xml-tag
description: Deliberately carries an XML tag <tool_use> in its description to trip the XML-tag check.
---

# xml-tag

Stub whose only defect is the one the XML-tag check targets.

## Outcome Contract

- **Outcome**: prove the XML-tag check produces a violation on bad input
- **Done when**: verify-skills exits 1 naming this stub and the XML-tag check
- **Evidence**: tests/scripts/test_verify_skills.py asserts the violation message
- **Output**: one violation line in the verifier output
- **Automation**: none — data-only negative fixture
