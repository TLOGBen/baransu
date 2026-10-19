# rationale — the page that ships beside the sketch

One page at `.claude/draft/<slug>.md`, in Traditional Chinese, with these sections in this order. Each states content, not boilerplate.

- **問題** — what the change is for, and what about the existing system makes its shape non-obvious; the constraints grounding found (callers that cannot break, types to interoperate with, invariants crossing the boundary).
- **用法** — the call sites, written first; the shape below is derived from them and agrees with them.
- **形狀** — data structures first, then how data flows through the signatures; the decisions that carry the weight; which invariants live in types and where validation sits; what the interface hides and why it is no larger; what the shape deliberately does not do. Each decision cites the principle move behind it (`structure.md #5`).
- **選擇** — the candidates by location, the screen of each, which became the base and why, what was grafted from which, what was rejected and why; or that they converged.
- **後置條件** — each trap another candidate found that this shape also faces, as a condition the implementation must meet.
- **接受的取捨** — one line each, 「我們接受 X，換到 Y」, including anything a later reader might mistake for an oversight.
- **待決問題與風險** — phrased as questions for the user.
- **第一步** — the first body to fill, in one sentence.
