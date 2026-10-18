---
name: ui
description: "Designs or restyles the web UI in the user's repo with deliberate palette, type, layout and motion, writing the UI files directly; can learn a style from a reference site or image, and builds explanatory pages that embed $baransu:draw figures. Trigger On '$baransu:ui', '美化', '調 UI', '看起來太 AI', '照這個網站的風格', 'make it look designed'. Not For: a single diagram, video or interactive figure ($baransu:draw)."
compatibility: Designed for Claude Code; ported to Codex.
metadata:
  version: 0.1.0-codex
---

# ui — the design lead for the UI in your repo

All user-facing output is Traditional Chinese (繁體中文); code, identifiers and CSS stay as written.

## Outcome Contract

- **Outcome**: The UI the user asked for exists in their files — built new or reshaped — with a visual direction chosen for this brief rather than a default; when a reference was given, its design language is captured in `.codex/design/reference-<slug>.md` and applied.
- **Done when**: The design plan (main story, idea, palette, type roles, layout concept with its 6 : 3 : 1 ranking, principles) was shown in the conversation before any file changed; the files are written or edited; the closing message lists every changed file with one line each.
- **Evidence**: The plan in the transcript, the changed-file list, and a screenshot when the environment can take one (taken only as § Browser checks allows).
- **Output**: UI source files in the user's project; optionally `.codex/design/reference-<slug>.md`; Traditional Chinese status messages.
- **Automation**: ultracode=neutral, loop=not-drivable（when driven non-interactively — /loop, cron, Workflow — read `../_shared/loop-contract.md` first and apply its PAUSE semantics）
- **Telemetry**: on invocation, append one selection record per `../_shared/selection-telemetry.md`.

Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the client. You can come up with one concrete subject, the design's audience, and the design's primary job, as a proposal. If there's any information in your memory about the client's preferences or context about what they're building, use that as a hint. The subject's industry, subject matter, materials, and vernacular are where distinctive visual choices come from — a design for a toy for girls aged 8–11 will be very aesthetically different from a dashboard for financial analysts. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is the first thing viewers will see. Open with the most characteristic thing in the subject's world, in the form that is most appropriate: a headline, an image, an animation, a live demo, an interactive moment, or other treatments. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the default treatment, so only use it if that's truly the best option.

Typography carries the personality of the page. You don't need a different typeface for display or headline text and body content: use one family or two, and if two, make them clearly distinct.

Choose your typefaces deliberately, not the default families you would reach for on any other project, and set a clear type scale following the default guidance of The Elements of Typographic Style with intentional weights, widths, and spacing. When type is used as a headline or visual element, use the type treatment itself as an active part of the design, not a neutral delivery vehicle for the content.

Default to line lengths of less than 80 characters. Serif typefaces can have slightly longer line lengths; give serif body text slightly more line-height than a sans-serif.

Avoid these default typographic treatments; they are the commonest tells of a generated page:
- Accenting just a single word or phrase in a headline, like putting one word in italic/bold or a different color.
- Using all caps for labels.
- Adding unnecessary typographic labels above content.

Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode useful information about the content rather than decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence — like a stepped process or a timeline. Before adding numbered markers, check the content really is a sequence.

Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment — one page-load sequence or one reveal — lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance.

## Process: plan, review against the brief, build, critique

For calibration, AI-generated design right now clusters around some traits:
1. a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta or warm-clay accent (often near #D97757 — Anthropic's own Claude-interaction accent, so on a user's brief it reads as a tell);
2. a near-black background with a single bright acid-green or vermilion accent;
3. a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns;
4. the SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow (rgba(0,0,0,.1)) under each, and gradient washes as decoration;
5. template chrome that appears whatever the subject: a tracked-out ALL-CAPS eyebrow label above every heading; meta strings joined with middle dots ('A · B · C'); labels built as 'WORD — fragment' with a spaced em dash; tinted near-black (#0B0B0B, #111) standing in for black; a monospace face for small data labels; a '→' appended to link and button text.

All traits are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly — the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, don't spend that freedom on one of these defaults. As with a hired human designer, there's often a careful balance between doing what you're good at and taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the client's design brief: create a compact token system with color, type, layout, and principles.
- Color: describe the core base palette as 4–6 named hex values.
- Type: the typefaces and their roles.
- Layout: a layout concept, using one-sentence prose descriptions and ASCII wireframes to ideate and compare. Include alignment guidance; should the content be left aligned, center aligned, justified?
- Principles: the high-level guidance for what makes this page unique.

Then review that plan against the brief before building: if any part of it reads like the generic default you would produce for any similar page (work through a similar prompt to see if you arrive somewhere similar) rather than a choice made for this specific brief — revise that part, say what you changed and why. Only after you've confirmed the relative uniqueness of your design plan should you start to write the code, following the revised plan.

When writing the code, be careful of structuring your CSS selector specificities. It's easy to generate CSS classes that cancel each other out (especially with a type-based selector like .section and an element-based selector like .cta). This can happen often with padding/margin between sections.

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected, visually accessible, harmonious color palettes. Critique your own work as you build, taking screenshots to review if your environment supports it — a picture is worth 1000 tokens. Consider Chanel's advice: before leaving the house, take a look in the mirror and remove one accessory. Human creatives have memory and always try to do something new, so if you have a space to quickly jot down notes about what you've tried, it can help you in future passes.

## The idea, the argument, and looking at the result

This section sharpens three steps above for any new build; where it and the sections above differ, this one wins. When refining an existing UI (§ Refining an existing UI), skip the inventory, the idea and the argument: that work keeps the page's sections and facts, and adds none.

**Name the main story first.** Before anything else, write the page's main story in one sentence: who arrives, what they came to find out, and what they know and do when they leave — "a commuter with a flat tyre finds the price, sees the shop is open today, and books on LINE". If it cannot be said in one sentence, no layout will rescue the page. Everything below serves this sentence: the idea is the form it takes, the argument is its order, and the hierarchy decides how loudly each part speaks. Every design choice and visual effect — a colour, a typeface, a motif, a motion, an ornament, the idea itself — earns its place only by serving this story; one that does not is cut, however good it looks on its own.

**The idea comes before the palette.** Before choosing any colour, write an inventory of 8–12 things that belong to this subject and to no competitor: its name and what the name means, its place (street, neighbourhood, light, weather, the lettering on its signs), the numbers in the brief, the one constraint it lives with, its materials and colours, its rituals and hours, the printed things of its world (a ticket, a label, a timetable, a manual). Then turn one item into the page's idea, in this sentence:

> On this page, [something only this subject has] becomes [the device that carries it].

Competitor test: put the nearest real competitor into the sentence; if it still holds, the idea belongs to the category — find another. "Clean and modern" is not an idea; a loaf of bread is every bakery. Distinctive pages are built from an inventory item, not from a better composition of a category idea. The idea carries the answer to the visitor's first question; it never replaces it. The first screen answers, in large type, what the brief says a visitor came to find out — the prices and hours, what the tool does and how to get it, when and where — and the idea is the form that answer takes: the prices set inside the motif, not pushed below it. The main story and the idea are the first two entries of the design plan, ahead of color. When you review the plan against the brief, run the competitor test on the idea and on each part of the plan instead of working through a similar prompt: a part that would serve the nearest competitor just as well is a default — revise it, and say what you changed and why.

**The argument comes before the layout.** Before the plan, list the page as claims with their proof, one line per section, in the order a visitor needs them. The claims decide which sections exist and in what order; delete any section that has no claim. This keeps the page off the stock sequence of hero, logos, three features, testimonial, pricing, call to action.

**Rank everything 6 : 3 : 1.** Do not make everything the protagonist, and the page sorts itself into an order. Every screen, and the page as a whole, reads at three levels: about 60 % a quiet stage (the ground, large calm masses, whitespace or a colour field, few changes), about 30 % supporting material that organises the space and leads the eye (the content, its structure, the secondary colour), and about 10 % one focus that the main story needs — found because it differs from its surroundings in one way (scale, the accent, isolation, value), not every way. The same split runs through colour (dominant, secondary, accent on two things at most), type (one size dominates, the rest stay small), density (quiet areas give the dense one something to read against) and the page itself (the sections that carry the main story are loud; the rest step back rather than each competing for attention). Taking the most space and drawing the most attention are different jobs: the stage may fill the screen while a small focus carries the meaning. The numbers are an empirical starting point, not a ratio to measure; the point is to pull the three apart. Write it into the plan: for the page and for each screen in the layout sketch, name the stage, the middle and the focus. The full treatment, with the colour, light and detail cases, is `$baransu:draw`'s `<draw>/references/motion/composition.md`.

**Fill what restraint empties.** Removing ornament is only half the job. A page that has lost its labels, rules and cards and gained nothing in their place reads as thin, and a richer page with a few tells beats an empty page without them. Fill the space ornament leaves with one of four things only: scale (make the main thing larger), the full content, a real picture of the subject's world, or a field of flat colour. Leave a screen empty on purpose at most once per page. Full content means every section the brief asks for delivers its information completely and at a readable size — the whole menu with prices, each room with its details, the price with what it includes. Where the brief leaves gaps, sample details (dish names, room names, project titles) are expected so the design is seen at full density; list them in the closing message for the user to confirm. On the `$baransu:draw` hand-off path (§ Pages built around $baransu:draw components), sample details come only from the facts in `docs/ui_brief.md`. Proof is never invented: no customers, testimonials, reviews, press, logos or business figures the brief does not give.

**Looking is required.** The screenshot critique in § Restraint is not optional here. Critique from screenshots, never from the code — you wrote the code, so you will read your intentions into it. Take them with `node "<draw>/scripts/motion/verify-page.mjs" <file>.html --out <dir>` (§ Browser checks), open `light-page.png` and `phone-page.png`, and run each of these checks on its own, marking it pass or fail.

Checks: one-second focus · squint · cover the name · left edges · neighbouring sections · fullness · phone

- One-second focus: glance at the first screen; there is exactly one answer to "what did I see", it is not "a website", and the brief's first question is answered there at desktop and phone width.
- Squint: at thumbnail size every screen reads 6 : 3 : 1 — a quiet stage, a leading middle, one focus that can be found — not many similar medium masses; the focus of the first screen is the main story's.
- Cover the name: with the name hidden, the first screen could not belong to a competitor, and the idea still reaches the last sections.
- Left edges: text blocks share two or three left edges, reused on purpose.
- Neighbouring sections: name each section's layout in one word; no word repeats back to back.
- Fullness: every screen is a composed poster carrying content, and at most one is a deliberate rest.
- Phone: the phone page is a composition of its own and its first screen is still one clear thing; a wide figure, table or code block is restacked, wrapped or redrawn for the phone, never left to scroll sideways inside its block, because a screenshot and most visitors read that as cut off.

Fix at most the three most important failures, take the screenshots again and re-run the checks; stop after two rounds and name in the closing message any check that still fails. On an existing UI, answer a fullness failure with scale or colour only, never with new content. When no browser tool in § Browser checks is available, skip this and say so in the closing message.

## Browser checks

Every screenshot, computed-style read or page check this skill runs goes through one of two kinds of tool, and no other:

- The user's real Chrome, when a tool that drives it is connected (Claude in Chrome). It runs on the user's own profile.
- `$baransu:draw`'s seeded scripts, run with the draw skill's directory `<draw>` = `../draw` beside this skill: `node "<draw>/scripts/motion/verify-page.mjs" <file>.html --out <dir>` (light and dark screenshots, a phone-width page, console errors, sideways scroll), `node "<draw>/scripts/motion/perf-check.mjs" <file>.html` (frame cost of embedded figures), and `node "<draw>/scripts/motion/grab.mjs" <url> --out <dir>` (a reference site's screenshots plus the fonts and colours it computes). Each starts Chromium through `scripts/motion/browser.mjs` `launchChromium()`.

Never start a fresh Playwright browser (`chromium.launch()`, a new `launchPersistentContext`), agent-browser, a Playwright MCP or any other browser tool: on Windows, Chromium on a fresh profile probes the account with a blank-password logon each time it opens a tab, and a handful of those lock the user's Windows account; the draw scripts seed the profile so the probe never runs. When neither kind of tool is available, skip the screenshot and say so in the closing message.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand and use. They are design content, not decoration. Bring the same intentionality and minimalism to copywriting that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's perspective. Name things by what users will understand in simple language, not by how the system is built. A user manages notifications, not webhook config. Describe what something is or does in plain terms rather than selling it. Being specific and legible to new users is always better than being clever.

Use active voice as default. A CTA says exactly what happens when it is used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the tone conversational: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each written element do exactly one job.

## Learning a design language from a reference

When the brief points at a reference — a URL, a screenshot, a poster, an art movement, "make it feel like this site" — the job is to read the reference for its decisions, not to copy its parts. Look at five things, in this order, and write down what you find in plain words before touching any code:

- Type: which roles exist (display, body, label, data), how many families, the scale steps and their ratio, weight and width choices, line length and line height. A reference often carries its whole personality in one typographic decision.
- Color: the relationships more than the hex values — how many hues, which one carries emphasis and how much surface it is allowed to cover, whether contrast comes from value or from hue, how background and surfaces differ.
- Spacing and rhythm: the base unit, how vertical rhythm is kept, where density changes and why.
- Layout: alignment (left, centered, justified), the grid or the deliberate lack of one, how sections are separated (whitespace, rules, color fields), where the eye lands first.
- Motion: what moves, what triggers it, how fast, and whether it answers an action or only decorates.

How to look depends on what the environment gives you. When a tool driving the user's real Chrome is available, open the page, read computed styles (font-family, font-size, line-height, colors, spacing) from the real DOM and take a screenshot — measured values beat guesses. Otherwise `$baransu:draw`'s `grab.mjs` (§ Browser checks) captures the page and the fonts and colours it computes. When neither can reach the page, read the screenshot or image the user gave you and describe what you see. When there is neither, ask the user for one screenshot rather than designing from a memory of the site. None of these tools is a precondition; the reading is.

Write the result as a short prose note at `.codex/design/reference-<slug>.md`, first line naming the source, so a later session can reuse it without re-reading the reference. `$baransu:draw` reads that note as a brand source when it skins a diagram or a component, so capture it once here and let drawing work reuse it; when a finished diagram must sit inside the user's site, `$baransu:draw` exports the SVG and this skill places it. Then design from the note the way you would from any brief: plan, review against the brief, build, critique.

Extract properties, never assets. 只抽性質，不抽素材、文案、logo. Type choices, palettes, proportions, spacing systems and motion patterns are ideas; the reference's images, illustrations, icons, copy, logos and brand marks belong to their owner and do not enter the user's project.

## Pages built around $baransu:draw components

`$baransu:draw` makes single pieces only: a diagram (`<slug>.html` + `.svg`/`.png`), a map (`<slug>.map.html`), a film (`out/<slug>.mp4` from `<slug>.film.html`, poster `out/<slug>.poster.png`), or an interactive component (`<name>.html`, named for its figure — a mechanism figure, a draggable or animated figure). A page that explains something with figures, a tutorial, or several figures meant to be read together is a page, and this skill designs it: the layout, the reading column, the prose, the section rhythm, and how each figure is introduced and captioned.

The user usually asks `$baransu:draw` ("draw X", "show me and draw it"), not this skill. When such a request needs a whole page, `$baransu:draw` builds and checks every component first, then loads this skill in the same turn and hands over the component paths and a summary of the request. The hand-off contract:

- **Input**: `<project>/.codex/draw/<slug>/docs/ui_brief.md` (who reads the page, what they must understand, the order of the ideas, each component's path, point and caption, the facts the page text may use, the page file name) and the component paths `$baransu:draw` lists.
- **Output**: one page, `<project>/.codex/draw/<slug>/<page-name>.html`, in the same folder as the components. Use the name the brief gives; if it gives none or it equals a component's file name, pick a name for the page's subject that no component uses. Never `index.html`, and never overwrite a component file.
- **Components keep their own look** (step 4 below).
- **No question to the user on this path.** The user is not waiting to approve a plan here: where § Ground your designs says to confirm the subject with the client, state it in the plan and continue; where anything is unclear, decide from `docs/ui_brief.md` and say what you decided in the closing message.

1. Read the hand-off: `docs/ui_brief.md` first — what the page must explain, to whom, and the component list (path, what each one shows, its size and theme behaviour). Open each component file to see its markup, its script, its theme tokens and how it sizes itself.
2. Design the page with the plan-review-build-critique process above; ground it in the subject the way any brief is grounded. State the plan in the conversation, then build — do not wait for a reply.
3. Embed each component, choosing per component: an `<iframe>` (the default; it keeps the component's styles and scripts isolated — size it to the component's aspect and pass the page's theme through when the component reads one), or the component's markup and script lifted into the page when the page needs one shared document (scope its CSS under a wrapper so neither side restyles the other, and keep one copy of any shared script). Films go in as `<video>` with the poster `$baransu:draw` rendered.
4. Keep each component's own look. Its palette, line weight, motion and internal layout were decided by `$baransu:draw` for that piece; the page sets the frame around it — spacing, captions, surrounding type, the page palette — and never restyles the inside. When the page palette and a component clash, adjust the page, or say in the closing message which component should be redrawn and why.
5. Check the page as a whole: phone width with no sideways scroll, both colour schemes, every embedded component loading and responding, reduced motion respected. Run `node "<draw>/scripts/motion/verify-page.mjs" <page-name>.html --out shots` and `node "<draw>/scripts/motion/perf-check.mjs" <page-name>.html` from the output folder (§ Browser checks) and fix the page until both pass.
6. Close as below, listing the page file and the embedded component paths; the closing message also says which components the page uses, how each is embedded, and the two check results.

The user may also call this skill directly on a page that already holds `$baransu:draw` components, to adjust the page around them. The same rule applies: change the page, not the components; anything inside a component goes back to `$baransu:draw`.

## Refining an existing UI

When the user points at UI that already exists and wants it better — tuned, polished, "less generic", closer to a reference — resist the urge to start restyling. Read the existing files first, the way you would read a reference: type, color, spacing, layout, motion, and what the current design seems to be trying to do. Then compare — against the reference note if there is one, against the principles above if there is not — and lay the differences out in the conversation as a short list: what the current UI does, what the target does, and which of those gaps are worth closing for this brief. Only then edit, and edit in place: the page keeps its markup, its content and its numbers; what changes is the CSS, and only the copy a listed difference calls for. Rewording changes how existing content is said, never what it says: add no fact the page does not already hold — no date, period, count, name or source the file cannot vouch for. That list is the plan for this kind of work; an edit that does not trace back to a listed difference is drift. If you notice you are rewriting the file from scratch, stop — that is the redesign the user declined — and go back to the list. Keep what already works.

## Closing the work

End with a short Traditional Chinese message that lists every file you changed, one line each saying what changed in it, followed by any sample details for the user to confirm and any check that still fails. Say only what you actually did: if you could not take a screenshot, do not write that you checked it visually; do not report scores, percentages or ratings of any kind — the reader judges the result by looking at it.
