---
name: one-workflow-at-a-time
description: "User wants concurrent Workflow count kept low — run experiments/workflows sequentially, not stacked"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7e0693c7-4aae-4eb1-a9a3-bdc2ced69a42
---

During multi-experiment ultracode sessions (2026-07-10, execute/read/learn A/B tests), the user interrupted a second concurrent Workflow launch with 「workflow 的數量注意一下」.

**Why:** Each workflow fans out many condition agents (heavy model usage + local cargo builds); stacking workflows multiplies concurrent load and makes progress hard to track.

**How to apply:** Keep at most one big Workflow running at a time. Queue subsequent experiment rounds and launch them only after the previous workflow completes. Consolidate related tracks into one workflow rather than launching parallel ones.

Follow-up in the same session: 「agent 不要太多」 — also keep the agent count per workflow lean: fewer redundant condition runs, ~2 judges not 3+, one consolidated auditor instead of 4 parallel lenses, minimal adversarial-verify fan-out.
