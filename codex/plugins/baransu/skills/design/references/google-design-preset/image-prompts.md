---
preset: google-design
purpose: External AI image-gen prompt templates for the Google Material You / M3 preset. Three product-category fallbacks (product photo / logo / UI) with a standardized negative tail for /design lint grep-gate.
accent: "#6750A4"
flavor: Material You dynamic colour, surface-tint elevation, rounded shape scale, Roboto / Google Sans feel
---

# google-design-preset / image-prompts.md

> **Scope**: prompt templates only; no API calls. Audience: users feeding Codex CLI image-gen, ChatGPT Images 2.0, or compatible tools when sourcing imagery for a Google Design / M3 preset DESIGN.md or `/book` artifact.
>
> Every prompt ends with the literal negative tail string, byte-for-byte, so the `/design` grep-gate (`task-checklist-governance` TASK-cg-04) can validate without ambiguity:
> `no title, no footer, no page chrome, no logo, no border`

---

## 1. 產品圖（Product photo）— Material You editorial photography

**Prompt template**

```
Editorial product photograph in Material You / Material 3 aesthetic. Subject rests on a soft surface-tinted background that subtly leans toward M3 primary (#6750A4) — think a pale lilac surface (#EADDFF) under cool diffused daylight. Rounded soft shadows beneath the subject (shape scale: large, ~28px equivalent radii echoed in props). Palette built from a dynamic-colour tonal range around the primary hue, with neutral surface and a single primary-container accent moment. Friendly, optimistic, approachable — Google product hero energy. No screen elements baked in, no UI chrome, no overlay text.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Use when a Google-Design preset DESIGN.md needs a product hero with M3 warmth.
- Surface-tint elevation: the background is not pure white — it leans subtly toward primary, which is the M3 elevation tell.
- Rounded props and soft shadows echo the shape scale; sharp 90° corners read as off-brand for this preset.

---

## 2. Logo / mark — minimalist single-colour M3 mark

**Prompt template**

```
Minimalist vector logo mark, single colour M3 primary (#6750A4) on M3 surface (#FEF7FF) background. Bold simple silhouette with rounded corners following the M3 shape scale (medium ~12px, large ~28px), balanced negative space, no wordmark, no tagline. Friendly geometric construction — softened squircle, rounded triangle, or pebble form. Flat, no gradient, no bevel; one optional soft surface-tint drop-shadow at 6% opacity is acceptable. Legible at 24dp Material icon scale and at app-store hero scale.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Placeholder mark for Google-Design preset DESIGN.md previews and `/book` slug avatars.
- The "no logo" element of the negative tail targets host-platform chrome; the prompt itself requests a *mark*, so the gate match stays literal text only.
- Rounded corners are mandatory — sharp-cornered geometry reads as Swiss or Kami, not M3.

---

## 3. UI / mockup — long-form Material You mockup

**Prompt template**

```
Long-form web mockup screenshot in Material You / Material 3 aesthetic. Single-column reading layout on M3 surface (#FEF7FF), body text in M3 on-surface (#1D1B20), headings with optional M3 primary (#6750A4) accent. Components follow M3 spec: a top app bar region (rendered as content, not host chrome), a filled card with 12px rounded corners and surface-tint elevation, an outlined card sibling, one filled button (primary container fill #EADDFF, on-primary-container text #21005D), a chip group, and a list row with leading icon. Roboto / Google Sans feel, generous 1.5 line-height. Render flat as a screenshot embedded in a document: no real browser chrome, no address bar, no OS shell.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Use when illustrating a Google-Design DESIGN.md long-form output for stakeholder review decks.
- "no real browser chrome / address bar / OS shell" qualifiers reinforce the literal negative tail without altering its byte-exact form.
- M3 specifies a top *app* bar (in-content); the gate's "no page chrome" refers to the *host* page shell — these are different layers and the prompt makes that explicit.
