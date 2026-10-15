# Builder prompt

Fill `{SKILL}`, `{BRIEF}`, `{OUT}` and `{DRAW}` and send as one subagent's whole task. The builder must not
see this kit, the other arm, or any other build.

---

Read the skill file at `{SKILL}` in full and follow it as your instructions for this task. It is a design
skill; treat it as if a user had invoked it with the brief below.

Where the skill refers to the draw skill's directory `<draw>`, use `{DRAW}`. For screenshots use only the
scripts the skill names under `<draw>/scripts/motion/`; never start any other browser or browser tool.

Brief:

{BRIEF}

Constraints for this run:
- Write exactly one self-contained HTML file at `{OUT}/page.html` (inline CSS and JS; web fonts from
  Google Fonts are allowed). Any other files you make go under `{OUT}/` too.
- There is no user to answer questions: where the skill says to confirm something with the client, state
  your decision and continue.
- Do not use photographs you do not have, and do not hotlink images from the web.
- Skip the skill's Telemetry line: this run writes no selection record.
- Finish with the closing message the skill asks for.
