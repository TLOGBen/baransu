# Mechanism catalog — 52 ideas and the machines that explain them

Technique reference for Phases 1–2 of a mechanism figure (`mechanism.md`): pick or adapt a machine before inventing one.

Every mechanism figure in the published Anatomy collection, restated as concept → object → what moves and what that motion means. Use it two ways: when an idea is already here, start from its object; when it is not, read three or four nearby rows to see how a mapping is made, then invent your own with `mechanism.md` § Inventing your own.

Columns: **Layer** is how it is drawn (SVG: solids only; WebGL: SVG plus a shader for fire, water, plasma or light; 3D: parts that really turn; Early: the first figures, which taught the method). **Interaction** is what the reader does. **Prompt** is the one line that produced it; most say only the idea, not the object.

## Computing — algorithms and data structures

| # | Idea | Object | What moves, and what it means | Interaction | Prompt |
|---|---|---|---|---|---|
| 01 | Hash map collisions | Sorting desk (post office) | A coding machine prints each letter's bucket (hash of its name mod 8) and files it in that pigeonhole, on top of any letters already there: a full pigeonhole is a collision chain. | tap to file; hover a bucket | explain how a hash map handles collisions, interactive |
| 02 | Binary search | Lab balance with a case of 16 ordered brass weights | Each try weighs the sample against the middle weight still standing; the half that cannot hold the answer sinks into its seats. | drag along the weights | explain binary search, interactive |
| 05 | LRU cache | Low bookcase with bookends | Four books stand on top, most recently used at the left; a miss sends the right-hand book back to its slot below. | click a book; keys A–J | explain how an LRU cache evicts entries, interactive |
| 07 | Gradient descent | Contour model of a narrow valley, cut from stacked boards | Survey pins strung with thread mark each step down the slope; a knob sets the learning rate, so steps overshoot or crawl. | tap a start; turn the knob | explain how gradient descent finds a minimum, interactive |
| 08 | Bloom filter | Fruit machine | Three reels are the three hash functions and a row of 16 flags is the bit array; it pays out ("maybe") only when all three of a word's flags are already up. | pick a coin; pull or press | explain how a bloom filter works, interactive |
| 10 | Mark-and-sweep GC | Modular synth case (the heap) | Patch cables are pointers; marking lights every module reachable from the stack, and the sweep pulls the modules left dark. | tap to collect; cut a cable | explain mark-and-sweep garbage collection, interactive |
| 11 | B-tree index | Rotary card file | Ten trays on a wheel are the index's pages; the wheel brings one tray to the reading stop at a time, so a lookup costs one read per level. | move to pick; tap to find | explain how a B-tree index finds a row, interactive |
| 14 | Merge sort | Chime rack of eight tubular bells | An overhead traveller rehangs the bells run by run, always taking the lower of the two front bells, until they ring in order. | hover to step; click shuffles | explain merge sort, interactive |
| 15 | Temperature (LLM sampling) | Roulette wheel | 16 pockets are the likeliest next tokens, each as wide as its probability; a thermostat knob sets the temperature and moves the frets, widening the unlikely pockets as it heats. | drag to heat; tap to spin | explain how temperature changes how a language model picks the next token, interactive |
| 32 | Git branch and merge | Model railway on a baseboard | Each commit is a station with one stud per parent; committing lays track, and a merge joins the feature line back into main. | drag to commit; tap to merge | explain how git branches and merges, interactive |

## Computing — systems, networks and concurrency

| # | Idea | Object | What moves, and what it means | Interaction | Prompt |
|---|---|---|---|---|---|
| 03 | DNS resolution | Pneumatic tube dispatcher | The resolver sends a capsule up each server's tube (root, com, example.com), each tube as long as its round trip; every reply raises a flag in a cache rack until its TTL runs out. | tap to look up; ← → | explain how DNS resolves a domain name, interactive |
| 04 | Message queue | Marble run | Two hoppers produce marbles into one sloping lane (the queue) where they wait in order behind an escapement; three timer drums consume them one at a time. | drag to set rate; tap a drum | explain a message queue with producers and consumers, interactive |
| 06 | TCP three-way handshake | Mail ropeway between two stations | Canisters flying SYN, SYN with an ACK pennant, then ACK ride the rope across; each station's semaphore shows its connection state. | tap to connect; hut to drop | explain the TCP three-way handshake, interactive |
| 12 | Debounce vs throttle | Music-box recorder with a turning pin disc | Every click of the knob is a call; the throttle and debounce dashpots each set their own pins, so the disc shows when each function actually ran. | move across to turn the knob | explain debounce versus throttle, interactive |
| 13 | Mutex / race condition | Water tank filled by two pumps, with an interlock key | Without the key both controllers read the same level and overfill the tank; with it, only the one holding the key may read and run. | tap a pump; tap the key | explain how a mutex prevents a race condition, interactive |
| 27 | Token bucket rate limiter | Air bench: pump, tank, relief valve, press | A pump fills a tank at two tokens a second and a relief valve vents past eight; each press spends a token to punch a paper tape, and with none left an interlock holds the press shut. | hold to punch; hover the tape | explain a token bucket rate limiter, interactive |
| 29 | Public-key encryption | Two-key strongbox | Any of three public keys turns the lid lock to seal the box; only the one private key turns it back. | drag to turn; tap a key | explain public key encryption, interactive |

## Computing — the web platform and UI

| # | Idea | Object | What moves, and what it means | Interaction | Prompt |
|---|---|---|---|---|---|
| 09 | CSS flex-grow | Bench vise holding three spring-loaded blocks | Each block carries one spring per point of flex-grow, so every spring takes the same share of the free space as the jaw opens. | drag the jaw; tap a block | explain how flex-grow shares space in CSS flexbox, interactive |
| 28 | CSS easing curves | Easing bench: lead screw, graph board, follower | A lead screw drives a carriage across the board at a constant rate (time); a follower rides a steel band bent to the curve and lifts the element to the eased progress. | click to run; drag a handle | explain how easing curves work in CSS animations, interactive |
| 31 | CSS box model | Picture-frame jig | Content, padding, border and margin are its nested frames; dragging the width and switching box-sizing shows which frame gives way. | drag width; click box-sizing | explain the CSS box model, interactive |
| 26 | (an object, not an idea) | Old desk computer: deep CRT, coiled keyboard | Type on it and the keys go down; the typed line appears on the screen, drawn in the plane of the case front; switching off collapses the picture to a line and a dot. | type on it; click to switch | a physical old screen like Apple's first PC, with the Anthropic logo on the screen, and a keyboard with a cable |

## Physical machines (WebGL: fire, water, plasma, light)

| # | Idea | Object | What moves, and what it means | Interaction | Prompt |
|---|---|---|---|---|---|
| 16 | Jet afterburner | Turbojet on a thrust stand, afterburner cut open | Past military power, fuel sprays in behind the turbine, the flame catches on the V-gutters and the nozzle petals open; a load cell reads thrust from 52.9 to 79.3 kN. | click or ← → throttle | explain how a jet engine afterburner works, interactive |
| 17 | Glass reheating (glory hole) | Gas-fired drum furnace beside a steel marver | In the hole, 1,150 °C walls and the burner flame reheat the gather toward 990 °C; on the marver, the steel takes the heat back. | point to slide the pipe; ← → | explain how a glassblower reheats glass in a glory hole, interactive |
| 18 | Tokamak plasma confinement | Research tokamak cut open at the front | 32 D-shaped coils, six field rings and a solenoid around a ray-marched plasma; scrub a 37 s pulse from breakdown to flat-top at 3.5 MA and back onto the limiter. | drag to scrub; Space plays | explain how a tokamak holds a fusion plasma, interactive |
| 19 | CNC plasma cutting | Gantry torch over a 12 mm plate on water-pan slats | It pierces, then cuts a part with the arc dragging behind; sparks quench in the water and the kerf glows for only a few millimetres. | hover or drag the plate; Space runs; Q speed | explain how a CNC plasma cutter cuts steel, interactive |
| 20 | Forging | Coal forge with a hand-cranked blower beside a 100 lb power hammer | Cranking brings the bar to yellow forging heat; each blow of the 45 kg ram flattens it more; the quench tub takes it back to cold. | hold fire; hold hammer; tap tub | explain how a blacksmith heats steel in a coal forge and flattens it under a power hammer, interactive |
| 21 | Turbofan thrust | Rolls-Royce Trent 970 on a ground-run thrust frame, upper quarter cut away | Push the lever and the three spools wind up at their own speeds; the fan swallows 1.2 t of air a second, most leaves as cold bypass; the load cell reads 14 → 334 kN. | drag ↔ thrust; Space take-off | explain how a big airliner turbofan engine like the A380's makes thrust, interactive |
| 22 | Generator on the grid | 660 MW generating unit and step-up transformer | The generator turns at exactly 3,000 rpm, the transformer lifts 22 to 400 kV; open the disconnector before the breaker and an arc climbs between the blades until the breaker clears it. | Space steps; W wrong order | explain how a power station generator puts power on the grid and why a disconnector must never break current, interactive |
| 23 | Pump cavitation | API 610 refinery pump cut open at the shaft | It draws 255 °C gas oil from a suction drum; starve the suction head and vapour sheets grow on the vanes at the eye while the head on the curve drops. | drag ↔ valve; ↕ drum level; F strainer | explain how a refinery pump cavitates when its suction head runs short, interactive |
| 30 | Pouring steel | Lined ladle on trunnions, sand mould | A hand wheel tilts the ladle through a 40:1 worm gearbox; steel pours through a basin into a sand mould clamped on its bottom board. | drag or ← → to tilt; Space pours | explain how molten steel is poured into a sand mould, interactive |
| 33 | Reactor control | TRIGA research reactor in half section | The core sits at the bottom of a 6.4 m water tank; pull the rods and power climbs, scram and they drop. | drag rods ↕; P pulse; S scram; A auto | explain how a nuclear research reactor is controlled, interactive |
| — | Rocket engine (full-flow staged combustion) | SpaceX Raptor 2 in a test stand | Oxygen passes through an oxygen-rich preburner that spins the oxygen pump, methane through a fuel-rich one that spins the methane pump; the two hot gases meet at 300 bar. Hover takes it apart into 11 assemblies; I fires it. | hover or ← → to take apart; I ignite; Esc together | (a shipped example, not in the numbered collection) |

## Timekeeping and astronomy

| # | Idea | Object | What moves, and what it means | Interaction | Prompt |
|---|---|---|---|---|---|
| 24 | How a mechanical watch keeps time | Swiss automatic movement, 25.6 mm, in a holder on a bench mat | The balance swings at 4 Hz and the pallet fork lets the 15-tooth escape wheel through half a tooth eight times a second, so the seconds step in eighths; the fourth wheel turns once a minute, the centre wheel once an hour. Winding turns the ratchet, the click ticks, the power reserve climbs. | drag the crown ↑ to wind; S slows (1/20, 1/100); E lifts the bridges apart | explain how a mechanical watch keeps time, interactive |
| 25 | Why the Earth has seasons (3D) | Brass tellurion on a turntable | A lamp on the pillar is the Sun; five gears keep the globe's 23.4° axis pointing the same way all year, so the hemispheres take turns facing the lamp. At 50° N a day lasts 16 h 22 m in June and 8 h 04 m in December. | drag to turn; ← → date; Space pause | explain why the Earth has seasons, interactive, 3D |

## Rendering frosted glass (the early figures)

Drawn for a long article on rendering frosted panes in WebGL, before the method had a name. They show that even a graphics pipeline, the most abstract subject here, maps onto bench equipment.

| # | Idea | Object | What moves, and what it means | Interaction |
|---|---|---|---|---|
| 34 | One pane, taken apart | A die set on four guide pillars | The pane's layers stacked bottom up: the picture behind, the half-size frosted copy (with 100 px reach for bend and blur), the distance field engraved in 12 px rings, the 40 px glass whose 34 px bezel bends the picture by up to 71 px; the result copies into the pane's 2D canvas. | hover or tap a layer |
| 35 | One shared WebGL context | Plotter with one print head and 16 tiles | The head is the one WebGL2 context; each tile is a pane's own 2D canvas. The head renders, lowers and stamps (`copyTo`) each tile in turn. | hover a tile to send the head |
| 36 | A shared canvas that grows | Drafting board with rulers on ratchets | Born at 300 × 150; when a draw needs more room a ruler clicks out until it fits, and its ratchet never lets it back (up to `MAX_TEXTURE_SIZE`); `copyTo` lifts off exactly w × h. | hover to hold; click to step |
| 37 | One texture, many mip levels | Tray with pockets and three loupes | One upload fills the back slot; `generateMipmap` fills eleven pockets, each half the last; each loupe (a pane) reads the level its size needs. | hover a loupe; click for a new src |
| 38 | Image fit: cover, contain, fill | Picture frame with carriages on a steel square | The window is the element's box; cover cuts the overhang (37.5 % laid beside the frame), contain leaves hatched bands, fill stretches the print like canvas on a stretcher. | pick the fit |
| 39 | One stage's render targets | Chest of seven drawers | Each drawer is as tall as its bytes per texel (8 for half-float, 4 for 8-bit), filled in the order the passes write them; a card marks the four the glass pass binds. | hover or ↑ ↓ to open a drawer |
| 40 | Separable blur | Bench with a pin block and two combs | One pass reads 49 × 49 = 2,401 taps per pixel; the renderer's two combs read a row then a column, 49 + 49 = 98. The dial changes only the spacing: always 8 taps per sigma. | drag ← → to set the blur |
| 41 | A cache key that skips work | Pin-tumbler lock, cut open | Eight cuts on the key, one per shape setting; when every pin meets the shear line the plug turns and nothing is drawn; change one part and the lock jams, and all 34 draws run again. | hover a part of the key |
| 42 | Draw calls per kind of frame | Stacks of chips in four wells | One chip per draw in pass order: a full rebake stacks 38, a moving control 35, a still pane the glass alone, a control at rest none. | hover to pick a stack |
| 43 | One pixel's refraction lookup | Reading stand: clear pane on threaded posts over a frost plate | A probe sets one pixel and a wire drops to where it samples: straight down across the middle, further out across the bezel (4, 14, 29, 58 px at b 0.5–0.97), stopping 87 px past the rim. | move toward the rim |
| 44 | The glass edge's height profile | Profile gauge with forty spring pins against a slice of the pane | Pins stand level across the middle and give way over the 26 px bezel, slowly then fast; a caliper finds the rim 19 px below the middle. | hover a pin; click to set the gauge |
| 45 | Dispersion | Lens bench at true scale | A probed bezel pixel reads the plate three times along its normal: red and blue land 1.6, 3.3 and 7.4 px apart as the probe nears the rim. | hover or ← → to move the probe |
| 46 | Rim light by facing | Small photo studio: pill on a turntable, key and fill lamps | The rim is as bright as each edge faces the key (full) or fill (half); turn the table and the bright arc stays put, because the light is fixed on the screen. | point to turn the table |
| 47 | Frosted copy | Lightbox and a print | Frost is a half-resolution blurred copy of what is behind, made in two passes, then bent by the glass. | drag ← → to set the blur |
| 48 | Merging shapes | Spot plate with six channels of drops | Each pair of drops is one distance field; closer than `merge`, two drops run together into one piece of glass. A fan of feeler blades sets `merge`. | slide across to open the fan |
| 49 | Bevel offset vs index of refraction | Glass block clamped profile-on, with a comb | The comb shows how far out each bevel pixel reads as the ior changes. | slide along the bench to set the ior |
| 50 | Lit by facing | A clear rim between a key and a half-strength fill | Each rim point is lit by how squarely its normal faces the two fixed lights. | move round the rim |
| 51 | Press and pull | Test rig: glass button on a sprung carriage, finger probe on a rail, dial gauge | A press swells the button 8 % (≤ 6 px a side); pulling makes it lean toward the finger like a rubber band (`give · (1 − 1/(1 + 0.55·d/give))`, give 14 px); release springs it back past rest once. | press, then pull ← → |
| 52 | Three colour reads | Lines seen through a bevel | Red, green and blue are read at three distances along the same normal, so lines come apart into colour. | slide ← → to set the spread |

## The shipped examples (reference builds)

The source skill also ships complete builds to copy from: a dial indicator on a stand (the smallest, ~300 lines), the desk computer (~85 solids), an upright arcade cabinet with its side off (~240 solids: a coin rolls the chute at the speed a disc reaches on a 30° slope, trips a switch, and the CRT warms up), the Raptor engine (dense pipework, 11-assembly explode), a school ripple tank (two WebGL layers for lamp light, caustics and water, driven by a dispersion model), the glass-button test rig (the quality bar for drawing), the spot plate (morphing shapes, one control driving many parts) and a 3D turning dial with a robot hand. These are not bundled here; the rows above carry their mappings.
