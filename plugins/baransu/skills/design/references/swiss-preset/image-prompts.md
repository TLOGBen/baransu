---
preset: swiss
purpose: External AI image-gen prompt templates for the Swiss International Style preset. Three product-category fallbacks (product photo / logo / UI) with a standardized negative tail for /design lint grep-gate.
accent: "#002FA7"
flavor: neutral paper canvas, IKB ultramarine single accent, neo-grotesque sans-serif, ample whitespace
---

# swiss-preset / image-prompts.md

> **Scope**: prompt templates only; no API calls. Audience: users feeding Codex CLI image-gen, ChatGPT Images 2.0, or compatible tools when sourcing imagery for a Swiss-preset DESIGN.md or `/book` artifact.
>
> Every prompt ends with the literal negative tail string, byte-for-byte, so the `/design` grep-gate (`task-checklist-governance` TASK-cg-04) can validate without ambiguity:
> `no title, no footer, no page chrome, no logo, no border`

---

## 1. 產品圖（Product photo）— editorial Swiss-modernist still life

**Prompt template**

```
Editorial product photograph in Swiss International Style. Subject placed precisely on a neutral off-white paper canvas (#f5f5f1), composition follows a strict baseline grid; ample negative space on at least two sides. Single saturated accent of International Klein Blue (#002FA7) — may appear as a coloured plinth, a thin geometric element, or a single object — everything else stays in neutral grey, near-black (#0a0a0a), and paper white. Hard north-light, crisp edges, no atmospheric haze. Studio-flat, documentary precision, 1960s Helvetica catalogue mood. No screen elements, no UI chrome.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Use when a Swiss preset DESIGN.md needs a hero or section photo with rationalist confidence.
- IKB must remain the *only* saturated hue — any second accent breaks the Swiss invariant.
- Grid alignment is implicit in the prompt: ask for "baseline grid" composition so the result drops cleanly into a 12-column layout.

---

## 2. Logo / mark — minimalist single-colour geometric mark

**Prompt template**

```
Minimalist vector logo mark, single colour International Klein Blue (#002FA7) on neutral paper background (#f5f5f1). Pure geometric construction — circle, square, slab, or a single rule — high-contrast bold silhouette, perfect optical balance, no wordmark, no tagline. Flat, no gradient, no bevel, no shadow, no texture. Constructed as if drawn with a compass and a ruling pen; legible at 16px favicon scale and at A0 poster scale. Reference: Müller-Brockmann, Hofmann, Vivarelli.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Placeholder mark for Swiss preset DESIGN.md previews and `/book` slug avatars.
- The "no logo" element of the negative tail targets host-platform branding chrome; the prompt itself requests a *mark*, so the gate match remains literal text only.
- Pure geometry: any organic curve or hand-drawn gesture pushes the mark out of the Swiss canon.

---

## 3. UI / mockup — long-form Swiss-grid mockup

**Prompt template**

```
Long-form web mockup screenshot in Swiss International Style. Twelve-column baseline grid visible as a faint guide, neutral paper background (#f5f5f1), neo-grotesque sans-serif (Helvetica / Akzidenz feel) at near-black ink (#0a0a0a), generous whitespace, IKB (#002FA7) accent on H1, one rule, and one inline link only. Hero block aligned to columns 1–8, body copy in columns 1–8, a small caption in columns 9–12, one rule divider, one data block with right-aligned figures. Render flat as a printed proof on a desk: no browser shell, no address bar, no scrollbar, no operating-system frame.
no title, no footer, no page chrome, no logo, no border
```

**Description (3 lines)**

- Use when illustrating a Swiss DESIGN.md long-form output for stakeholder review decks.
- "no browser shell / address bar / scrollbar" qualifiers reinforce the literal negative tail without altering its byte-exact form.
- The faint twelve-column guide is a tell — it signals "designed against a grid", which is the Swiss preset's primary identity.
