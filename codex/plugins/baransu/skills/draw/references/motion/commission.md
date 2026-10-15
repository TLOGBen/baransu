# Commissioned films — from a sample to a paid delivery

Technique reference for client work, read alongside the phases: § 1 and § 7 in Phase 1 (scope, finding and pricing), § 3 and § 4 while building (Phases 4–5), § 5 and § 6 in Phase 5 (review and package).

When the film is for a client, or a sample meant to win one, the craft rules stay the same and three things are added: a scope that can be delivered, review evidence the buyer can trust, and a package someone else can re-render. This file carries the delivery side; the selling side at the end is for when the user asks for help finding or answering a brief. The renderer stays Route A (`pipeline.md`) unless the brief names a framework.

## 1. Choose the job before the effects — scope and samples

Start from a deliverable a buyer can use, not from a technique. A short SaaS product demo is a good first job because its goal is specific: show one useful interaction clearly enough that a viewer understands the product.

- **A sample is labelled as one.** Without permission to use a real product, make an independent concept with original interface graphics and a small, readable `Concept demo` label throughout. No third-party logos, no testimonials, no performance claims; labels such as Ads, Social and Website, never invented results (the `UNACCEPTABLE` line of `docs/brief.md`, `1-design.md` § 1).
- **With permission, use the approved material**: the client's logo, fonts, screenshots, copy and real product flows, listed in `assets/manifest.json` before drawing.
- **Starting scope:** one 15-second film, a widescreen master, a vertical adaptation (re-laid out, not cropped) and the editable source.

## 2. Story, references, keys — handled by the phases

Client work runs the same five phases. What the producer insists on:

- **Story in frame ranges, every frame covered** (`2-draft.md` § 3 has the worked 15 s / 450-frame example): `docs/brief.md`, `docs/style_guide.md` and `docs/storyboard.md` list the exact copy, assets, frame ranges, transitions and sound cues. Read the storyboard back: you should be able to say what the viewer learns before any animation exists. Read it back yourself and log it in `docs/review_log.md`, then go on to the keys (`3-keys.md`) without waiting (`README.md`: no gate waits on the user).
- **References** are read for principles, never copied as assets; without one, a restrained typographic direction with a licensed font and the single accent (`1-design.md` § 2).

## 3. Build so revisions stay cheap

### Separate content from motion

Copy, colours and asset paths live in one object at the top of the film file; the animation reads them. A copy change is then one edit, not a hunt.

### Motion follows the frame number

Everything derives from `t` (`seek(t)`), no wall-clock timers, no unseeded randomness, fonts loaded explicitly (`pipeline.md` § The render contract).

### Rough preview first

An animatic of all scenes at low resolution (`render.mjs animatic`) and the project's checks before any polish; check the interaction and reading time before spending effort on shadows.

### The gather spring

For cards gathering into an overview, start at stiffness 180, damping 22 (unit mass; Remotion's `spring()` with mass 1, stiffness 180, damping 22 is the same) and tune from there. If the cards still bounce when the viewer should be reading, raise the damping.

### Preserve position across a state change

The moment separate cards become the overview is where the illusion breaks: a jump in position or a sudden font change is visible. The incoming state starts where the outgoing one left (`transitions.md`: the match cut and accent carry rows).

### Keep the headline still while it is read

Keep the headline still while it is read, and do not animate every element at once: one read at a time (`2-draft.md` § 4).

### Check the handoffs

Pause at each scene boundary (3 s and 7 s in the example): the cursor touches the intended control, and the cards land where the next scene expects them.

### Longer films

Longer films expand the same brief into scenes with checkpoints (`chapters.md`). Save progress so another session can continue (`docs/review_log.md`).

## 4. Sound

A few well-placed sounds are enough for a sample: a click at the selection, a soft movement cue, a restrained tone when the overview settles. Use original synthesized effects (`sfx.mjs`) or assets licensed for publication. With supplied music, listen to the detected beats before aligning the whole film to them (`beat-grid.md`). Cues sit at the actual interaction frames, with short fades and headroom; keep a silent version for comparison. Check the peaks for clipping; when the mix cannot be heard, finish the film and say in the completion report that the mix still needs a human listen (the run does not stop for it).

## 5. Review the actual export

`review.md` § Review the export, held to the letter: a contact sheet every second and around every scene boundary, the probe (duration, dimensions, frame rate, audio stream), phone-size text, cursor continuity, scene coverage, the final three-second hold, muted and with sound, the loop seam on its own; fix the three most important defects and repeat until the export passes (no pass cap), timestamped findings for every pass, and **never mark a check that could not run as passed** — return the files and the remaining issues.

## 6. Package the deliverable

- Both formats as H.264 MP4 (`render.mjs full --all`); open each and confirm dimensions, duration and audio.
- The source without secrets or dependency folders, with the lockfile (if any), permitted assets, licence notes, and the exact install and render commands in `README.md`.
- When a framework renders the film (Route B), check its licence for the commercial setup; Remotion, for one, has company licensing terms.
- For repeat work, the folder itself is the template: the next film for the same brand copies it and replaces `docs/brief.md` and `assets/` (`1-design.md` § 1).
- **Disclosure, in four separate claims.** The README and the caption say what the person supplied (brief, assets, components, a song), what an existing skill or template contributed, which external services actually rendered or generated anything, and what the model drew. "One prompt", "pure code", "no external assets" and "no human edits" are four independent statements; none implies another, and a tool that was not used is never named. Beside the render line, keep the three counts apart that public cost comparisons conflate — human prompts, internal review passes, time to the accepted master — and give the whole-task cost with revisions, services and assets, not the price of one call.
- **A portfolio piece**: upload it where a prospect can view it without logging in, label it as self-initiated, and write a caption that names the problem, your contribution and the delivered formats, so a buyer understands your role without asking.

### Route B with Remotion (when the brief names it)

The published setup: `npx create-video --yes --blank --no-tailwind <name>`, `npm install`, `npx remotion skills add` (installs Remotion's own agent skills), `npx remotion studio` (the template's preview script) for the preview; compositions are registered with fixed size, fps and duration (e.g. `SaaSDemo`, 1920×1080, 30 fps, 450 frames; `SaaSDemoVertical`, 1080×1920); motion derives from `useCurrentFrame()` and `useVideoConfig()`; `spring()` for physical moves; `npx remotion render` (or the Studio's Render button) for the MP4. The rules in §§ 3–6 apply unchanged; this skill does not bundle Remotion (`pipeline.md` § Routes and engines).

## 7. Finding and answering a brief (on request)

Only when the user asks for help selling the work. Nothing is sent, submitted or posted on the user's behalf; every draft comes back for the user to send.

### Search by outcome, not by tool

Buyers write "SaaS product video", "UI animation", "Remotion developer", "product launch video"; a search for a model name misses most of them. Start with the last 14 days, widen to 30 and 90 only when needed, and open each original posting.

### Qualify with evidence

Record each lead's URL, posting date, public buyer name, deliverables, stated budget and currency, source-file requirements and visible status. Score the fit on similarity to the sample, required tools, source compatibility, workload and deadline. Keep closed or inaccessible postings apart. Never invent a budget, an open status or a sale. Postings close: reopen the source before applying.

### Read the brief as the one who must deliver it

Separate what you can meet, what is missing, and what your sample does not demonstrate. Before treating a stated budget as acceptable, clarify how many videos it covers, the formats, the revision rounds and whether editable source is expected.

### Scope a bounded first assignment

One approved interaction, one 15-second film, the agreed aspect ratios, a storyboard review, one revision round, the source if wanted, and a definition of what counts as a new request.

### Price it transparently

Base = hours × hourly rate + direct costs; quote = base ÷ (1 − platform fee). Example: 5 h × $40 + $20 = $220; with a 10 % fee, $220 ÷ 0.90 = $244.44 before tax. Replace every assumption with real numbers and the fee shown for that contract. If one project's budget covers several films, a single-film calculation cannot justify it: propose a smaller paid pilot or pass.

### Write `offer.md` and an intake checklist

Write `offer.md` and an intake checklist: exact deliverables, durations, aspect ratios, required assets, revision boundaries, source format, acceptance checks, and when the delivery clock starts. Proposed terms are labelled as proposed; no price or deadline is invented when an input is missing.

### The proposal

The proposal opens by showing the brief was read, offers the sample, proposes a first step, and asks one useful question. Example core: "Your brief calls for short videos built around real product workflows. I'd start with one interaction and turn it into a fifteen-second demo using your supplied access and brand assets. My self-initiated sample shows the interface animation and pacing I can bring to that format. Before production, I'd share a storyboard with the exact screens and copy for approval. Could you confirm how many videos the project covers and whether you need editable source files?" Use only experience the user supplied; on a milestone platform, production starts after the milestone is funded.

### Other routes from the same sample

Other routes from the same sample: a fixed package on a project catalogue (respect each marketplace's AI-assistance rules and buyers who require a different process), founder prospecting from a public launch, an inbound breakdown with a commissioning link, white-label work for agencies, referral partners and expert directories; paid acquisition only after an offer converts. Expansions once there is demand: launch bundles, ad-hook variations, localisations, product updates, monthly retainers; reusable motion kits and templates; stock (check the library's AI-content rules); data-driven batches or a client-owned generator (these need engineering and ongoing support); workshops on the workflow itself.

### Keep a delivery log

Estimated versus actual hours, and the reason for each revision, so future quotes improve and packages that run over their scope show up.

### A dated market snapshot

A dated market snapshot (2026-10-02, from one public article; postings close and prices move): a SaaS promo video at $500, two UI animations at $400 total, a website demo video at $200, a podcast logo animation at $100, fintech promo videos at $60–80 each, a B2B SaaS demo at about $2,000, a website explainer at $100, website animations at $100 total, a SaaS video ad at $30–250, looping LED visuals at about $42–62; a 15–30 s Remotion product-video brief listed $300 fixed. One creator with a recognisable house style reported selling pieces at $129 for under an hour of work each.
