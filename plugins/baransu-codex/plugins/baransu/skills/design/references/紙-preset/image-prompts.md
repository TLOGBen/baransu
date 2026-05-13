---
preset: 紙 (Kami)
purpose: External AI image-gen prompt templates for the Kami warm-paper preset. Three product-category fallbacks (product photo / logo / UI) with a standardized negative tail for /design lint grep-gate.
accent: "#1B365D"
flavor: warm parchment background, deep ink-blue accent, serif typography hints
---

# 紙-preset / image-prompts.md

> **Scope**: prompt templates only; no API calls. Audience: users feeding Codex CLI image-gen, ChatGPT Images 2.0, or compatible tools when sourcing imagery for a Kami-preset DESIGN.md or `/book` artifact.
>
> Every prompt ends with the literal negative tail string, byte-for-byte, so the `/design` grep-gate (`task-checklist-governance` TASK-cg-04) can validate without ambiguity:
> `no title, no footer, no page chrome, no logo, no border`

---

## 1. 產品圖（Product photo）— editorial paper-stock photography

**Prompt template**

```
Editorial product photograph in warm parchment-paper aesthetic. Subject centered on an ivory cotton-paper backdrop (#faf9f5) with subtle linen-fibre texture; soft diffused window light from the upper-left, gentle deckle-edge shadow at base. Restrained palette: warm whites, oat, deep ink-blue accent (#1B365D) as the single saturated note. Shot 50mm equivalent, shallow depth-of-field, true-to-life colour, fine grain. No screen elements, no UI chrome, no overlay text. Mood: contemplative, archival, hand-bound book monograph.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Use when the DESIGN.md needs a hero or section product photo with editorial gravitas.
- Paper texture and ink-blue accent are non-negotiable — they carry Kami brand recognition without a wordmark.
- Avoid glossy reflections, neon, or hi-tech surfaces; Kami imagery skews towards craft, archive, and stillness.

---

## 2. Logo / mark — minimalist single-colour mark

**Prompt template**

```
Minimalist vector logo mark, single colour deep ink-blue (#1B365D) on warm ivory background (#faf9f5). Bold simple silhouette, balanced negative space, no wordmark, no tagline. Geometric or hand-drawn ink-brush feel acceptable; one continuous gesture preferred. Flat, no gradient, no bevel, no shadow. Suitable for letterpress at 8mm and for favicon at 32px without loss of identity. Subject: a single emblem that reads as a stamp seal or chōji-style mon.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Used for placeholder marks in Kami preset DESIGN.md previews and `/book` slug avatars.
- "no logo" in the negative tail refers to incidental brand chrome (page-level watermarks, host UI badges) — the prompt explicitly asks for a *mark*, so this is intentional and the grep-gate treats it as literal text only.
- One-colour, one-gesture: any second hue or stroke variation breaks Kami's monastic typographic feel.

---

## 3. UI / mockup — long-form paper-feel mockup

**Prompt template**

```
Long-form web mockup screenshot in Kami warm-paper aesthetic. Single column reading layout, parchment background (#faf9f5), serif headings in near-black ink (#141413), generous line-height, deep ink-blue (#1B365D) accent on a few inline links only. Includes a hero block, three body paragraphs with a pulled blockquote, a small two-row data table, and a subtle drop-cap initial. Render as if photographed flat on a desk: no browser chrome, no address bar, no scrollbar, no operating-system shell. Pixel-sharp typography, deckle-edge crop at the bottom suggesting more content below.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Use when illustrating a Kami DESIGN.md long-form output for stakeholder review decks.
- The "no browser chrome / no address bar / no scrollbar" inline qualifiers reinforce the literal negative tail — the gate text remains exact.
- Deckle-edge crop signals "page continues" without needing a footer; this is the Kami substitute for a `…more` UI element.
