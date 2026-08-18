# Mechanic inventory — from the original manual

Source: N64 retail manual (Activision / Disney Interactive, © 2000), 30-page scan in
`reference/Manual.pdf` (study only, gitignored).

These are **functional notes**, not a transcription. Mechanics, not prose or art.
Nothing here is a measurement — the manual states no numbers. The frame-count gate in
`original-metrics.md` is still open and still needs the video.

---

## Move set (the full verb list the original shipped with)

| Verb | Original binding | Notes |
|---|---|---|
| Run / move | Control Stick or D-Pad | analog on stick |
| Jump | A | |
| Duck | Control Stick down | doubles as the coconut dodge |
| Swing | hold stick L/R on a vine | stick up = climb up, down = descend |
| Vine release | A while swinging | chains vine → vine; framed as the wide-pit crossing tool |
| Climb | A + stick up, against a cliff/tree/vine | |
| Tree surf | contextual, on a twisting branch | see below |
| Ground pound | Z | opens boxes, shakes trees, reveals floor secrets |
| Power jump | A off a springboard | springy plants, branches, loose boards, animal backs |
| Throw (overhand) | B | for distant targets |
| Throw (underhand) | C-Down | for close targets |
| Fruit cycle | L / R | |

Weapons are level-scoped, not a persistent loadout: knife (C-Up slash, C-Right thrust),
spear (Sabor fight only — C-Down high, B low), Jane's parasol (tree-surf only, B to pop).

Fruit tiers: yellow (unlimited, baseline) → purple (2× impact) → red (splits, multi-hit)
→ blue (clears everything nearby).

---

## Tree Surfing is the runner — this is the find

Manual p14 describes it as: land on a twisting branch, auto-forward motion, **duck** under
overhanging branches, **A to leap** low-clinging vines, **stick L/R to swing wide** of
branches, collecting tokens throughout. Birds and monkeys stream past.

That is a three-lane endless-runner grammar — duck / jump / lateral dodge / collect —
already present in the source material. If this project is going to be a running game and
still be honest about being a Tarzan clone, tree surfing is the mode to build from. It
is the one part of the original that was already a runner.

Corollary for level grammar: the parasol exists **only** in tree surf, and its job is
knocking baboons off the branch ahead. So the original's runner mode already had an
offensive verb layered on top of dodge/jump. Worth deciding early whether ours does.

---

## Hazard grammar

- **Contact damage** from ordinary jungle animals — not all hazards are "enemies," some
  just cost health on touch. Cheap density filler.
- **Birds drop coconuts** — a telegraphed overhead threat answered by *either* jump
  (to spot it coming) or duck (to shelter). Two valid answers to one hazard.
- **Exotic plants** — orange-pink plant activates on a thrown fruit, banana tree on a
  ground pound. Both spit out pickups. These are interactables, not threats.
- Named antagonists: Sabor (leopard, spear duel), Clayton, Clayton's thugs, baboon horde,
  rampaging rhinos, stampeding elephants.

## Economy

- **Tokens** — 100 collected before finishing a level = 1 extra life.
- **T-A-R-Z-A-N letters** — 6 per level, all six unlocks a story screen.
- **Sketches** — 4 pieces per level, completing one before level end unlocks a bonus level.
- **Terk tokens** — jump-and-grab, triggers a hint. First two levels only (tutorial device).
- **Bananas** — health refill. Health is a continuous energy bar, not discrete hearts.
- Lives counter is displayed in a leaf, lower-right.

Three parallel collectible tracks (life economy / completion / bonus unlock) over the same
level. Cheap replay value; worth stealing the structure even at one level.

---

## Level list (13)

Welcome to the Jungle · Going Ape · The Elephant Hair Dare · Stampede · Coming of Age ·
Sabor Attacks · The Baboon Chase · Trashing the Camp · Campsite Commotion ·
Journey to the Treehouse · Rockin' the Boat · Tarzan to the Rescue · Conflict with Clayton

Chase levels (Stampede, The Baboon Chase) and Tree Surfing are the forward-momentum ones.
"Going Ape" is where the original taught vines. Level select is linear-unlock with a
completion percentage.

---

## Gaps and caveats

- **Manual pages 22–23 are missing from this scan** — "Completing Levels" and
  "Bonus Levels" per the table of contents. So the level-exit conditions and the bonus
  level rules are *not* documented here. If exit conditions matter, that scan is incomplete.
- The manual carries **no timing, distance, or speed figures** of any kind. It cannot
  close `original-metrics.md`. Nothing in this file is a substitute for the frame-by-frame
  measurement block.
- Bindings above are **N64 layout**. The PC and PS1 releases differ, and the metrics
  protocol deliberately targets PS1/PC because framerate differs per port — so treat this
  manual as authoritative for *what verbs exist*, never for *how they feel*.
