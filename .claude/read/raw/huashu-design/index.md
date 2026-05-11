Title: GitHub - alchaincyf/huashu-design: Huashu Design · HTML-native design skill for Claude Code · Claude Code 里 HTML 原生的设计 skill · 高保真原型 / 幻灯片 / 动画 + 20 设计哲学 + 5 维评审 + MP4 导出 · Agent-agnostic

URL Source: https://github.com/alchaincyf/huashu-design

Markdown Content:
**🌐 English** · [中文](https://github.com/alchaincyf/huashu-design/blob/master/README.zh.md)

> _"Type. Hit enter. A finished design lands in your lap."_ _「打字。回车。一份能交付的设计。」_

[![Image 1: License](https://camo.githubusercontent.com/bf44b54f34b30f3eff1193911b084ca418ad25795ab1ce75826e4e84f6aac594/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d506572736f6e616c2532305573652532304f6e6c792d6f72616e67652e737667)](https://github.com/alchaincyf/huashu-design/blob/master/LICENSE)[![Image 2: Agent-Agnostic](https://camo.githubusercontent.com/62863600d0f7ed303901c0093a2a8458ae3692f3d31c6207fd4da7513348c2d4/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4167656e742d41676e6f737469632d626c756576696f6c6574)](https://skills.sh/)[![Image 3: Skills](https://camo.githubusercontent.com/57d990bf3ba568d760f0184e195515f4e4584cafeeaa79884c2b280dd5e3f97c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f736b696c6c732e73682d436f6d70617469626c652d677265656e)](https://skills.sh/)

**Say one sentence to your agent — Claude Code, Cursor, Codex, OpenClaw, Hermes all work.**

3 to 30 minutes — you ship a **product launch animation**, a clickable App prototype, an editable PPT deck, a print-grade infographic.

Not "decent for AI" quality — it looks like a real design team made it. Give the skill your brand assets (logo, colors, UI screenshots) and it reads your brand's voice; give it nothing and the built-in 20 design vocabularies still keep you out of AI slop territory.

**Every animation in this README was made by huashu-design itself.** No Figma, no After Effects — just a sentence + skill run. Next product launch needs a promo video? You can make it too.

```
npx skills add alchaincyf/huashu-design
```

[See it work](https://github.com/alchaincyf/huashu-design#demo-gallery) · [Install](https://github.com/alchaincyf/huashu-design#install) · [What it does](https://github.com/alchaincyf/huashu-design#what-it-does) · [How it works](https://github.com/alchaincyf/huashu-design#core-mechanics) · [vs. Claude Design](https://github.com/alchaincyf/huashu-design#vs-claude-design)

> 📖 **Note for English readers**: this skill is built by a Chinese-speaking developer. The skill's agent prompts (`SKILL.md`, `references/*.md`) are in Chinese but the agent is bilingual — works fine with English tasks. The demos below are the English parallel versions; the Chinese ones are in the default-named files (see the [Chinese README](https://github.com/alchaincyf/huashu-design/blob/master/README.zh.md)).
> 
> 
> 📖 **致中文读者**：这个 skill 由花叔（@AlchainHust）开发。一句话能让 agent 在 3–30 分钟内交付**产品发布动画 / 可点击 App 原型 / 可编辑 PPT / 印刷级信息图**。完整中文介绍见 [README.zh.md](https://github.com/alchaincyf/huashu-design/blob/master/README.zh.md)。

* * *

▲ 10-second hero animation showing what huashu-design does ([download MP4](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/hero-animation-v10-en.mp4) if autoplay doesn't work)

* * *

## Install

[](https://github.com/alchaincyf/huashu-design#install)

npx skills add alchaincyf/huashu-design

Then just talk to Claude Code:

```
"Make a keynote for AI psychology. Give me 3 style directions to pick from."
"Build an iOS prototype for a Pomodoro app — 4 screens, actually clickable."
"Turn this logic into a 60-second animation. Export MP4 and GIF."
"Run a 5-dimension expert review on this design."
```

No buttons, no panels, no Figma plugin. Agent-agnostic — drops into Claude Code, Cursor, Trae, Hermes, OpenClaw, or any markdown-skill-capable agent.

* * *

## Star History

[](https://github.com/alchaincyf/huashu-design#star-history)
[![Image 4: huashu-design Star History](https://camo.githubusercontent.com/606bb35e4902548268892c03101b3d8186b0b2d5a28df87820f5deb0ff9c7353/68747470733a2f2f6170692e737461722d686973746f72792e636f6d2f7376673f7265706f733d616c636861696e6379662f6875617368752d64657369676e26747970653d44617465)](https://star-history.com/#alchaincyf/huashu-design&Date)

* * *

## What it does

[](https://github.com/alchaincyf/huashu-design#what-it-does)
| Capability | Deliverable | Typical time |
| --- | --- | --- |
| Interactive prototype (App / Web) | Single-file HTML · real iPhone bezel · clickable · Playwright-verified | 10–15 min |
| Slide decks | HTML deck (browser presentation) + editable PPTX (text frames preserved) | 15–25 min |
| Motion design | MP4 (25fps / 60fps interpolation) + GIF (palette-optimized) + BGM | 8–12 min |
| Design variations | 3+ side-by-side · Tweaks live params · cross-dimension exploration | 10 min |
| Infographic / data viz | Print-quality typography · exports to PDF/PNG/SVG | 10 min |
| Design direction advisor | 5 schools × 20 philosophies · 3 directions recommended · Demos generated in parallel | 5 min |
| 5-dimension expert critique | Radar chart + Keep/Fix/Quick Wins · actionable punch list | 3 min |

* * *

## Demo Gallery

[](https://github.com/alchaincyf/huashu-design#demo-gallery)
> English parallel versions of the demos. Chinese versions live at the default filenames (see the Chinese README).

### Design Direction Advisor

[](https://github.com/alchaincyf/huashu-design#design-direction-advisor)
The fallback for vague briefs: pick 3 differentiated directions from 5 schools × 20 philosophies, generate all 3 demos in parallel, let the user choose.

[![Image 5: w3-fallback-advisor-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w3-fallback-advisor-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w3-fallback-advisor-en.gif)

### iOS App Prototype

[](https://github.com/alchaincyf/huashu-design#ios-app-prototype)
Pixel-accurate iPhone 15 Pro body (Dynamic Island / status bar / Home Indicator) · state-driven multi-screen navigation · real images pulled from Wikimedia/Met/Unsplash · Playwright click tests before delivery.

[![Image 6: c1-ios-prototype-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c1-ios-prototype-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c1-ios-prototype-en.gif)

### Motion Design Engine

[](https://github.com/alchaincyf/huashu-design#motion-design-engine)
Stage + Sprite time-slice model · `useTime` / `useSprite` / `interpolate` / `Easing` — four APIs cover every animation need · one command exports MP4 / GIF / 60fps-interpolated / BGM-scored finals.

[![Image 7: c3-motion-design-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c3-motion-design-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c3-motion-design-en.gif)

### HTML Slides → Editable PPTX

[](https://github.com/alchaincyf/huashu-design#html-slides--editable-pptx)
HTML decks for browser presentation · `html2pptx.js` reads DOM computed styles and translates each element into real PowerPoint objects · exports are **actual text frames**, not image-bed fakes.

[![Image 8: c2-slides-pptx-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c2-slides-pptx-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c2-slides-pptx-en.gif)

### Tweaks · Live Variation Switching

[](https://github.com/alchaincyf/huashu-design#tweaks--live-variation-switching)
Colors / typography / information density parameterized · side panel toggle · pure-frontend + `localStorage` persistence · survives reload.

[![Image 9: c4-tweaks-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c4-tweaks-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c4-tweaks-en.gif)

### Infographic / Data Viz

[](https://github.com/alchaincyf/huashu-design#infographic--data-viz)
Magazine-grade typography · precise CSS Grid columns · `text-wrap: pretty` typographic details · driven by real data · exports to vector PDF / 300dpi PNG / SVG.

[![Image 10: c5-infographic-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c5-infographic-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c5-infographic-en.gif)

### 5-Dimension Expert Critique

[](https://github.com/alchaincyf/huashu-design#5-dimension-expert-critique)
Philosophical coherence · visual hierarchy · execution craft · functionality · innovation — each scored 0–10 · radar-chart visualization · outputs Keep / Fix / Quick Wins punch list.

[![Image 11: c6-expert-review-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c6-expert-review-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/c6-expert-review-en.gif)

### Junior Designer Workflow

[](https://github.com/alchaincyf/huashu-design#junior-designer-workflow)
No heroic one-shot attempts: start with assumptions + placeholders + reasoning, show it to the user early, then iterate. Fixing a misunderstanding early is 100× cheaper than fixing it late.

[![Image 12: w2-junior-designer-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w2-junior-designer-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w2-junior-designer-en.gif)

### Core Asset Protocol · 5-step hard process

[](https://github.com/alchaincyf/huashu-design#core-asset-protocol--5-step-hard-process)
Mandatory whenever the task involves a specific brand: ask → search → download (three fallback paths) → verify + extract → write `brand-spec.md` covering **logo, product shots, UI screenshots, colors, fonts** — all required assets, not just colors.

[![Image 13: w1-brand-protocol-en.gif](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w1-brand-protocol-en.gif)](https://github.com/alchaincyf/huashu-design/releases/download/v2.0/w1-brand-protocol-en.gif)

* * *

## Core Mechanics

[](https://github.com/alchaincyf/huashu-design#core-mechanics)
### Core Asset Protocol

[](https://github.com/alchaincyf/huashu-design#core-asset-protocol)
The hardest rule in the skill. When the task touches a specific brand (Stripe, Linear, Anthropic, DJI, your own company, etc.), five steps are enforced:

| Step | Action | Purpose |
| --- | --- | --- |
| 1 · Ask | Checklist of 6 asset types: logo / product shots / UI screenshots / color palette / fonts / brand guidelines | Respect existing resources |
| 2 · Search official channels | `<brand>.com/brand` · `<brand>.com/press` · `brand.<brand>.com` · product pages · launch films | Find authoritative assets |
| 3 · Download by asset type | Logo (SVG → inline-SVG in HTML → social avatar) · Product shots (hero → press kit → launch video frames → AI-generated from reference) · UI (App Store screenshots → official video frames) | Three fallback paths per asset type |
| 4 · Verify + extract | Check logo fidelity · product image resolution · UI freshness · grep color hex from real assets | **Never guess from memory** |
| 5 · Freeze to spec | Write `brand-spec.md` with logo paths, product image paths, UI screenshot paths, CSS variables for colors/fonts | Un-frozen knowledge evaporates |

**Ranking of asset importance** (from the skill's internal rubric):

1.   Logo — mandatory for any brand
2.   Product renders — mandatory for physical products
3.   UI screenshots — mandatory for digital products
4.   Color values — auxiliary
5.   Fonts — auxiliary

A/B-tested (v1 vs v2, 6 agents each): **v2 reduced stability variance by 5×**. Stability of stability — that's the real moat.

### Design Direction Advisor (Fallback)

[](https://github.com/alchaincyf/huashu-design#design-direction-advisor-fallback)
Triggered when the brief is too vague to execute:

*   Don't run on generic intuition — enter Fallback mode
*   Recommend 3 differentiated directions from 5 schools × 20 philosophies, each **from a different school**
*   Each comes with flagship works, gestalt keywords, representative designer
*   Generate 3 visual demos in parallel, let the user choose
*   Once chosen, continue into the Junior Designer main flow

### Junior Designer Workflow

[](https://github.com/alchaincyf/huashu-design#junior-designer-workflow-1)
The default working mode across every task:

*   Send the full question set in one batch, wait for all answers before moving
*   Write assumptions + placeholders + reasoning comments directly into the HTML
*   Show it to the user early (even if just gray blocks)
*   Fill in real content → variations → Tweaks — show at each of these three steps
*   Manually eyeball the browser with Playwright before delivery

### Fact Verification First (Principle #0)

[](https://github.com/alchaincyf/huashu-design#fact-verification-first-principle-0)
The highest-priority rule, added after a real failure mode: when the task mentions a specific product / technology / event (e.g., "DJI Pocket 4", "Nano Banana Pro", "Gemini 3 Pro"), the first action **must** be a `WebSearch` to confirm existence, release status, current version, and specs. No claims from training-corpus memory. Cost of a search: ~10 seconds. Cost of a wrong assumption: 1–2 hours of rework.

### Anti AI-slop Rules

[](https://github.com/alchaincyf/huashu-design#anti-ai-slop-rules)
Avoid the visual common denominator of AI output (purple gradients / emoji icons / rounded-corner + left border accent / SVG humans / Inter-as-display / **CSS silhouettes standing in for real product shots**). Use `text-wrap: pretty` + CSS Grid + carefully chosen serif display faces + oklch colors.

* * *

## vs. Claude Design

[](https://github.com/alchaincyf/huashu-design#vs-claude-design)
I'll be upfront: the Core Asset Protocol's philosophy was lifted from system prompts Anthropic wrote for Claude Design. That prompt hammers home a single idea — **great hi-fi design doesn't start from a blank page, it grows from existing design context**. That one principle is the difference between a 65-point design and a 90-point design.

Positioning differences:

|  | Claude Design | huashu-design |
| --- | --- | --- |
| Form | Web product (used in browser) | Skill (used in Claude Code) |
| Quota | Subscription quota | API usage · parallel agents unblocked |
| Output | Canvas + Figma export | HTML / MP4 / GIF / editable PPTX / PDF |
| Interaction | GUI (click, drag, edit) | Conversation (tell agent, wait) |
| Complex animation | Limited | Stage + Sprite timeline · 60fps export |
| Agent compatibility | Claude.ai only | Claude Code / Cursor / Trae / Hermes / OpenClaw |

Claude Design is a **better graphics tool**. Huashu-design makes **the graphics-tool layer disappear**. Two paths, different audiences.

* * *

## Limitations

[](https://github.com/alchaincyf/huashu-design#limitations)
*   **No layer-editable PPTX-to-Figma round-trip.** The output is HTML — screenshottable, recordable, image-exportable, but not draggable into Keynote for text-position tweaks.
*   **Framer-Motion-tier complex animations are out of scope.** 3D, physics simulation, particle systems exceed the skill's boundaries.
*   **Brand-from-zero design quality drops to 60–65 points.** Drawing hi-fi from nothing was always a last resort.

This is an 80-point skill, not a 100-point product. For people unwilling to open a graphical UI, an 80-point skill beats a 100-point product.

* * *

## Repository Structure

[](https://github.com/alchaincyf/huashu-design#repository-structure)

```
huashu-design/
├── SKILL.md                 # Main doc (read by agent, Chinese)
├── README.md                # English README (default, this file)
├── README.zh.md             # Chinese README
├── assets/                  # Starter Components
│   ├── animations.jsx       # Stage + Sprite + Easing + interpolate
│   ├── ios_frame.jsx        # iPhone 15 Pro bezel
│   ├── android_frame.jsx
│   ├── macos_window.jsx
│   ├── browser_window.jsx
│   ├── deck_stage.js        # HTML deck engine
│   ├── deck_index.html      # Multi-file deck assembler
│   ├── design_canvas.jsx    # Side-by-side variation display
│   ├── showcases/           # 24 prebuilt samples (8 scenes × 3 styles)
│   └── bgm-*.mp3            # 6 scene-specific background tracks
├── references/              # Drill-down docs by task (Chinese)
│   ├── animation-pitfalls.md
│   ├── design-styles.md     # 20 design philosophies in detail
│   ├── slide-decks.md
│   ├── editable-pptx.md
│   ├── critique-guide.md
│   ├── video-export.md
│   └── ...
├── scripts/                 # Export toolchain
│   ├── render-video.js      # HTML → MP4
│   ├── convert-formats.sh   # MP4 → 60fps + GIF
│   ├── add-music.sh         # MP4 + BGM
│   ├── export_deck_pdf.mjs
│   ├── export_deck_pptx.mjs
│   ├── html2pptx.js
│   └── verify.py
└── demos/                   # Capability demos referenced by this README
```

* * *

## Origin Story

[](https://github.com/alchaincyf/huashu-design#origin-story)
The day Anthropic launched Claude Design I played with it until 4 a.m. A few days later I realized I hadn't opened it once since — not because it's bad (it's the most polished product in the category) but because I'd rather have an agent work in my terminal than open any graphical UI.

So I had an agent deconstruct Claude Design itself (including the system prompts circulating in the community, the brand asset protocol, the component mechanics), distill it into a structured spec, then write it as a skill installed in my own Claude Code.

Thanks to Anthropic for writing the Claude Design prompts so clearly. This kind of derivative work inspired by other products is the new form of open-source culture in the AI era.

* * *

## License · Usage Rights

[](https://github.com/alchaincyf/huashu-design#license--usage-rights)
**Personal use is free and unrestricted** — studying, research, creating things for yourself, writing articles, side projects, personal social media. Use it freely, no need to ask.

**Enterprise / commercial use is restricted** — any company, team, or for-profit organization integrating this skill into a product, external service, or client deliverable **must obtain authorization from Huasheng first**. Including but not limited to:

*   Using the skill as part of internal company tooling
*   Using skill outputs as the primary creative method for external deliverables
*   Building a commercial product on top of the skill
*   Using it in paid client projects

**Indicative pricing**: USD 1,800 / year (Annual) or USD 3,500 one-time (Perpetual). Custom enterprise terms available. See [LICENSE](https://github.com/alchaincyf/huashu-design/blob/master/LICENSE) for full terms.

**Commercial licensing contact**: email **[alchaincyf@gmail.com](mailto:alchaincyf@gmail.com)** (preferred) or DM on any social platform below.

* * *

## Connect · Huasheng (Huashu)

[](https://github.com/alchaincyf/huashu-design#connect--huasheng-huashu)
Huasheng is an AI-native coder, independent developer, and AI content creator. Notable work: Cat Fill Light (App Store Top 1 in Paid category), _A Book on DeepSeek_, Nüwa.skill (GitHub 12k+ stars). Combined 300k+ followers across platforms.

| Platform | Handle | Link |
| --- | --- | --- |
| X / Twitter | @AlchainHust | [https://x.com/AlchainHust](https://x.com/AlchainHust) |
| WeChat Official Account | 花叔 | Search "花叔" in WeChat |
| Bilibili | 花叔 | [https://space.bilibili.com/14097567](https://space.bilibili.com/14097567) |
| YouTube | 花叔 | [https://www.youtube.com/@Alchain](https://www.youtube.com/@Alchain) |
| Xiaohongshu | 花叔 | [https://www.xiaohongshu.com/user/profile/5abc6f17e8ac2b109179dfdf](https://www.xiaohongshu.com/user/profile/5abc6f17e8ac2b109179dfdf) |
| Official Site | huasheng.ai | [https://www.huasheng.ai/](https://www.huasheng.ai/) |
| Developer Hub | bookai.top | [https://bookai.top](https://bookai.top/) |

For commercial licensing, collaborations, or sponsored content, DM on any of the above.
