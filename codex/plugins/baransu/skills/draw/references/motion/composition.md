# Composition — the 6 : 3 : 1 rule

Technique reference for visual hierarchy in every frame: Phase 1 decides the look with it, Phase 2 writes the art direction and colour script with it (`2-draft.md` § 2), Phase 3 fills every key card's composition with it (`3-keys.md` § The key card), the review checks it (`review.md`). It applies to stills and diagrams too: the diagram system's one accent and target density are the same rule (`../diagram/style-guide.md`).

When generating scenes, images or assets there is a constant pull to add: buildings, neon, fog, reflections, rich texture, "a bit more cinematic". Every local area ends up beautiful and the whole has no focus; or the subject finally stands out and the style that was wanted has gone. The 6 : 3 : 1 rule is the fix, in one plain sentence: **do not make everything the protagonist, and the picture sorts itself into an order.**

## The rule

The 6 : 3 : 1 principle comes from spatial design, film set dressing, game art and visual-asset planning. It sets a gradient in geometric mass, material frequency and contrast, so the picture has a clear visual order and stays efficient to produce:

| Share | Layer | What it is |
|---|---|---|
| **60 %** | spatial foundation, low-frequency negative space | the big masses that establish the environment: walls, floor, sky, terrain, large shadow; quiet, few changes |
| **30 %** | narrative dressing, mid-frequency transition | the supporting structure and objects that give variation, organise the space and lead toward the focus |
| **10 %** | focal anchor, high contrast | the small, clear area the viewer must find: a figure, a door, a prop |

- **Taking up the most of the frame and drawing the most attention are two different things.** An empty station hall can fill the picture while a small figure in a lit doorway carries the story: the hall builds the environment, the figure holds the meaning. This is the entry point to the whole rule (and the same distinction as stage / life / focus, `2-draft.md` § Concepts).
- **The numbers are an empirical starting point, not a fixed ratio.** A real frame may sit nearer 7 : 2 : 1, or use another organisation for its purpose; the point is to pull the three apart. Game-art writing on the rule calls it an empirical proportion, not a measurement.
- **It is a choice, not a law.** A bustling street can let many neon signs build the atmosphere together; a confrontation can stage two equal subjects; a scene about chaos can use competition between elements on purpose. The goal and the style decide; 6 : 3 : 1 helps arrange the picture toward them.

## It governs more than colour

The familiar 60–30–10 colour rule (dominant, secondary, accent) is one case. The same relation organises:

| What you are handling | How to organise it |
|---|---|
| composition | big masses build the picture, lines connect the space, a small area forms the focus |
| lighting | a dominant light sets the mood, a secondary light keeps the shadows readable, a local light picks out what must be seen |
| colour | the dominant colour sets the tone, a secondary colour gives variation, an accent carries the emphasis |
| spatial layout | first the architecture and terrain, then the paths, last the traces of use |
| object form | first the overall shape, then the attached structures, last the small details |
| information density | keep quiet areas so the complex area has something to read against |

Do not stuff the whole table into one prompt or one key. Fix the one problem that most affects the picture now: a picture with no focus usually has lights of equal brightness everywhere; a fragmented picture usually has small texture spread into every corner. They need different changes.

## Colour: first decide what must survive

Pushing the surrounding signs of a neon street to grey-blue makes a warm doorway stand out — and kills the neon street. **Making the subject stand out does not automatically make the work better.** If coloured signs, wet pavement and crossing lights are the wanted style, removing them first leaves the target. The better version kept the neon colours and moved the change into **brightness**: the surrounding signs dimmed, the stronger local brightness kept for the doorway and the figure. Cyan, pink and orange signs remain, the wet ground still reflects colour; the doorway and the warm light on the ground now lead. The quieter version reads the figure more easily; the louder one keeps more street energy. What you want to express decides which.

So hierarchy can be built in another dimension while the vivid palette stays. Before hunting through swatches, write three things:

- **Dominant**: what tone covers most of the scene? Deep forest green, the purple-blue of a neon street, the off-white of an interior. It may be a family of close colours, and it need not be low-saturation: a large vivid purple can be the dominant; what matters is how the others relate to it.
- **Secondary**: what gives the necessary variation? Grey stones in a forest, wooden furniture indoors, a second group of lights in the street.
- **Accent**: what must be noticed? A door, a garment, a prop; it may echo in a few small places.

When several colour families compete, shrink the range of one, or keep the colour and change its brightness. Pick one change, then check whether the picture moved toward the goal.

## Lighting: write where it comes from and where it lands

Light sets the mood and decides what is easy to see. In the station: dusk through the skylights establishes the hall; reflections from walls and floor keep the benches in the dark readable; a small lamp at the door picks out the figure. With even lighting, the ceiling lamps, walls and hall all compete; with the hierarchy, the doorway behind the figure becomes the place to look, though the space is the same.

Write the relation, not the adjective:

```
Cold dusk enters the hall from high windows as the overall light. Faint reflections from walls and floor
keep the structure in the shadows. One warm lamp at the door lights the area around the figure, so the
figure's outline separates clearly from the background behind it.
```

Warm against cold is one tool; the same colour of light can also separate by brightness, position and reach. Do not add three lamps to fill three slots. After rendering, check the relations you wrote: is the light's direction right, are the shadows still readable, does the figure separate from the background — easier to act on than "is it cinematic".

## Detail: places to put it, and places to rest

A machine whose pipes, panels and small parts cover every surface, against an equally busy wall, reads as noise; the same machine with large intact casing surfaces and a calm wall lets the joints, ports and local details be read, and its overall shape reads better, not worse. The structure did not need the scattered fragments.

- **Build in order**: decide the whole (low, slender, heavy), then the attached structures (roof, balcony, entrance), last the small details (window frames, carving, wear). For a whole environment: walls, floor, openings and paths first; boxes, old posters and other traces of life after.
- **A few traces say more than a carpet of them.** A few footprints leading to the door say "someone just arrived"; it does not need litter everywhere.
- **Quiet areas may have real texture**, only less eye-catching change: a patch of fog, a shadow, an old wall. The focal area may also be simple: one clearly silhouetted figure is enough.
- Mechanism figures follow the same split: detail belongs to parts that do something, every region still rewards a 4× look, and the one lit part is the 10 % (`../mechanism/mechanism.md` § Drawing rules).

## In film: the set tells the characters' story

Translated from asset design to production design and cinematography, the three layers become three questions: **What is this world? Who lives here? What must we notice in this scene?** — space foundation → character life → plot focus. 60 / 30 / 10 is a reminder for weighting; the three describe *functions*, not areas allotted to architecture, furniture and props. (Production-design interviews do not call the ratio an industry standard; it is a lens for reading films and borrowing their methods.)

**Space foundation — make the world hold.** Walls, floor, ceiling, doors and windows, distant mountains and skylines tell us what world this is before anyone enters. Sometimes it recedes; sometimes it is the subject. The environment may carry strong colour and ornament; what matters is how it forms a whole.
- *The Grand Budapest Hotel* (2014), the lobby: a large red carpet, textured columns, railings, chandeliers and furniture — its order comes from the central axis, symmetry, repeated structures and colour in groups; the reception desk and the people sit inside those relations while the hall keeps its own loud style. Borrow "one system of structure and colour unifies the space"; the background does not have to be greyed out to build hierarchy.
- *Dune* (2021): walls and columns far taller than the figures, large shadows and close stone tones make the environment heavy; the complex relief on the right is organised into one block rather than cutting every wall into equally dense texture. The production design answers heat, wind and daylight as well as power and scale. In a prompt, turn "huge, oppressive" into visible relations: how much taller the wall is than the figure, where the entrance is, how light enters, which architectural shape leads.

**Character life — make the space look used.** Architecture gives a place; furniture, dressing and traces of use let us read who lives there. A chair that is always sat in, work materials piled on the floor, a worn table edge reveal a way of life; ask first how an object relates to the character, then decide how many.
- *Parasite* (2019): a low interior, old walls, and pizza boxes pressed against the family; they fold boxes on the floor, so the material of their living occupies their living space. The objects have concrete uses and explain the characters' situation. A room heaped with random clutter and a room holding the objects that explain its owner express different things: for someone living alone, consider how many things are used and how they are placed; for a makeshift office, how work materials invade the living area.

**Plot focus — what the shot leaves to the viewer in this scene.** Some objects become the focus only by entering the story: a letter, a ring, an actor's sudden stop. It need not be the brightest, most complex or largest thing.
- *Inception* (2010): the small spinning top at the front left edge of the table among papers, drinks, a fruit bowl and window light. Out of context the fruit bowl or the window may catch the eye; with the story, the viewer watches this small object's state. Visual emphasis and narrative importance both steer attention, and in a close-up the key object may fill the frame: do not keep it small to honour "10 %".
- *Schindler's List* (1993), the ghetto clearance: the crowd, clothes and street are not simple, and the girl's red coat has no fine detail; it stands out by the **scarcity** of colour in a black-and-white world. Leave one clear difference for the object the story needs; stacking high saturation, strong light and complex texture is not what makes a focus.

The three functions overlap: a box in a corner is dressing; picked up by an actor, it enters the scene's plot. Use them to assign tasks, not as three separate object lists. In production, art builds space and dressing, props support use, and camera, lighting and blocking decide how all of it is seen: **make the world credible, give life its reasons, then let this scene's focus be read.**

## Starting a scene

Write the purpose in plain words first ("an empty station at dusk, and one person still waiting"), then answer:

1. **What must the style keep?** Realistic texture, old architecture, a deserted mood — or, for a neon street, the coloured signs and wet reflections.
2. **What builds the big environment?** Here the hall, walls and floor, and large shadow; make them form a clear space first.
3. **Where must the viewer look?** The doorway and the figure; write the position, not "the subject stands out".
4. **What helps it stand out?** The lamp at the door, a lit surface behind the figure, benches angled toward the door. Two or three means are enough.
5. **What around it can compete less?** Small lamps, posters, fine texture, reflections: keep their function and style, lower their presence.

**The thumbnail test.** Shrink the result to a phone-sized thumbnail (`render.mjs phone`, or a 360 px still): can the person or object you want noticed still be found? Do the big light and dark masses and the space still read? If the focus is lost, check what competes with it; if the space does not read, go back to the big shapes and layout; if the style faded, check whether a defining feature was removed. **Change one main problem per round** and compare before and after; do not rewrite the whole prompt each time.

## The scene prompt structure

For a scene, a still, or the first frame of a generated shot. Fill the brackets; drop a line that cannot be written yet, but settle the scene, the style and the place to look first.

```
[Place, time, and what is happening in the frame].
In [the wanted style], keeping [the colours, materials or environmental features this style must have].

Most of the frame is [the big environment: architecture, terrain, walls and floor, sky or shadow], toned by [the dominant colour or family].
[Supporting structures or objects] in [the secondary colours] organise the space through [arrangement, direction or depth order] and lead toward [the main viewing area].
[A few furnishings and traces of use] suggest [the character's way of life, situation, or what happened here]; every object has a clear use.
[The figure, entrance, prop or other focus] sits at [a clear position], made to stand out by [local light-dark difference, the accent colour, a clear silhouette, or an isolated position].

Light enters from [a real or plausible source and direction], [its visible result in the environment].
Fill light keeps [the dark areas that must stay readable] structured; [a local light, if needed] lights [the area near the focus].
Detail sits mainly where [function or story must be expressed]; elsewhere keep larger intact shapes and gentler texture variation.

Keep [the characters, costumes, architecture, props and spatial relations that must not change].
Shot as [viewpoint and shot size], [aspect ratio, if the tool supports it].
```

A filled example (Chinese, as the user may write it):

```
暮色中的废弃车站，一名旅人站在右后方亮着灯的门口。
采用写实摄影风格，保留旧车站的建筑质感与冷清气氛。
大面积大厅、墙面和地面建立空旷环境，整体以冷灰和蓝灰定调。
深木色长椅与灰色立柱提供变化，地砖和长椅的走向引向右后方的门口。
门边一只磨旧的旅行箱与几道带水的鞋印，暗示旅人刚赶到，正在这里等候。
人物与门口形成主要观看区域，人物轮廓与身后的亮面清楚分开，暖色集中在门口及附近地面。
冷色暮光从高窗进入，形成方向一致的大块明暗。微弱反射保留阴影中的长椅和墙面结构。
门口的暖灯照亮人物附近，其他灯光不与它形成同样强的亮点。
墙地保留真实但温和的旧纹理，只在门口附近放少量使用痕迹，不把细碎物件均匀铺满大厅。
保持旅人的位置与车站空间关系。平视广角全景，横向 16:9。
```

In this skill's own films the same structure is the composition line of a key card and of `docs/style_guide.md`; in a directed prompt it fills LOOK and SHOTS (`prompts.md` § The directed prompt).

## In time: motion keeps the hierarchy, it does not split the seconds

- **Static first.** Get the still (the key, the first frame) right, then add one simple motion. When a first frame exists, it supplies the character, scene and style; the motion description covers only the action, the camera and environmental change: "Locked-off shot. The traveller at the door slowly raises their head and looks across the empty hall. The door light stays steady; the figure's outline stays clear; the background stays quiet, with no eye-catching flicker and nothing passing in front of the figure."
- **Check after it moves**: is the figure still clear, does background motion drown the action? (Ambient motion stays under 5 % of the hero's travel, `springs.md` § Hierarchy.)
- **The focus may move and grow.** A push-in makes the figure bigger; when the story turns to the room behind the door, the focus moves. Never cut a 10-second video into six seconds of environment, three of structure and one of subject, and never keep the figure small forever to honour 10 %. 6 : 3 : 1 is about each frame's order, not the timeline.

## The check, as a scorecard row

For every key and every contact sheet: **one 60 % that is quiet, one 30 % that leads, one 10 % that is found** — at thumbnail size, in the frame's own lighting, colour and detail, with the style's defining features still present. The critique card's composition row asks exactly this (`../critique-loop.md`).
