# recipe — how this repo's app is run for a proof

A recipe is written for the next run, not for a human: it is read cold, mid-task, by an agent that has never seen the app. It lives at `.codex/prove-it/recipe.md`, with the feature map beside it under `.codex/prove-it/features/`.

## Learn it from the repo

Answer from the codebase; ask the user only what you cannot observe.

- **Surface** — what a user actually touches: a web UI, a CLI or TUI, a desktop app, an API, a library. A repo can have several; pick the primary one and name the rest.
- **Run** — the command the repo itself documents for running it locally (package scripts, Makefile, README), with its ports, environment variables, seed data, and auth.
- **Drive** — existing harnesses first (end-to-end specs, PTY helpers, endpoints a request can reach, a debug port); only then a generic one: a browser for web and desktop shells, a terminal session for CLIs and TUIs, plain HTTP for services.
- **Observe** — what evidence there is to capture: screenshots, terminal transcripts, response bodies, logs, exit codes, stored state.
- **Isolate** — whether two instances can run side by side (ports, data directories, profiles). If not, the recipe says so and refuses to drive an instance it did not start.

If the checkout does not build or start, report that precisely before writing anything. When an asset unrelated to the claims blocks startup (a sample config, a static directory nothing serves), the recipe may create it, marked as verification scaffolding, and remove it in cleanup.

## The five parts

Each part uses this repo's real commands, paths, and handles; none is left as a placeholder.

- **Launch** — the command that brings the app to a usable state from an empty data directory, including migrations and seed data, and the sign that it is ready to use, not merely that a process answers. A health check can pass while init scripts are still running. Include teardown. A short-lived CLI has no server: launch means build or install once, then run each drive in its own isolated session.
- **Doctor** — one read-only check that this instance is worth driving: the process is up, it is this version's build, the port is ours, auth is valid.
- **Drive** — the harness recipe, using stable handles (accessible names, data attributes, prompt strings, routes) over coordinates and tab order.
- **Evidence** — what is captured for a proof and where it goes: the action and the resulting state, side effects alongside what is visible, and a read-back of anything stored.
- **Cleanup** — how to stop what a run started: by what it started, never by process name. Cleanup removes instances and scratch state, never evidence.

Any helper script the recipe ships is executable, and its invocation is written in the recipe.

## The feature map

`.codex/prove-it/features/README.md` holds the baseline preconditions, the driving conventions, the proof rules, and an index; one file per user-facing feature follows, starting with the three to five the repo shows most plainly (routes, commands, menus, docs). Each feature file, from the user's side, has four sections — `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, `Gotchas` — as `feature-map-example.md` shows. When the seed data lacks a precondition a journey needs, the journey reports a failure and the reason goes in `Gotchas`; the journey is never weakened to pass. A proof that drives one convenient entry point is incomplete when the map lists others.

## Prove the recipe before relying on it

Run it once end to end: launch, doctor, drive one mapped feature, capture evidence, clean up, then confirm the evidence is still at its named location. Fix what fails, and run cleanup after every failed attempt too. If you proved it in a stand-in for the real target (a container for a fresh machine, a local stack for a remote one), list each setup step the stand-in did that the target will not; those stay unproved until a run on the target covers them.
