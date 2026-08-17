# Reference metrics — measured from the original

**Status: NOT YET MEASURED. This file is the gate on the 03:00–05:00 tuning block.**

Budget 45 minutes, once. Do it before day one, not during.

Without these numbers, the two-hour tuning block silently becomes "adjust until it feels
okay" — which is the failure the whole plan exists to prevent, and it will not announce
itself. You will finish the block feeling fine about it.

---

## Protocol

1. Find a longplay of the **PS1 or PC** version. Record which — the console version runs
   at a lower framerate than the PC release, and every frame count below depends on it.
2. Step frame by frame: `,` and `.` in a paused YouTube player.
3. **Measure in character-heights and character-widths, never pixels.** `tuning.json` is
   authored in tiles, so these port directly. A character is roughly 2 tiles tall — pin
   that ratio once, early, and use it consistently.

## Source

| | |
|---|---|
| Version measured | <!-- PS1 / PC --> |
| Video URL | |
| Playback framerate | <!-- fps --> |
| Assumed character height | <!-- in tiles, e.g. 2.0 --> |
| Date measured | |

---

## Measurements

| Metric | Unit | Value | → maps to |
|---|---|---|---|
| Jump input → apex | frames @ fps | | `jump.timeToApexMs` |
| Total airtime, standing jump | frames | | sanity-check on apex + fall |
| Jump height | character-heights | | `jump.heightTiles` |
| Tapped vs held jump height | character-heights | | `jump.releaseCutMultiplier` |
| Max gap cleared, running | character-widths | | exit condition (±10%) |
| Run speed | char-widths / sec | | `run.maxSpeedTilesPerSec` |
| Acceleration to full run | frames | | `run.timeToMaxSpeedMs` |
| Swing arc, grab → release | frames | | `swing` tuning |
| Distance gained per swing | character-widths | | swing-gap unit for level grammar |
| Fall : rise speed | ratio | | `jump.fallGravityMultiplier` |

---

## Conversion notes

- `frames ÷ fps × 1000` → ms for any `*Ms` key
- `character-heights × (character height in tiles)` → tiles for any `*Tiles` key
- Fall:rise ratio maps directly onto `fallGravityMultiplier` — the plan's starting guess
  is `2.0`, so a measured ratio far from that is the single most valuable number here

## The design target to hold onto

A runner abandoned a tool-assisted speedrun of the original because most of it is "hold
right" — there wasn't enough room for stunts. **The game is momentum-forward and
forgiving, not precision-demanding.** If your level starts requiring pixel-perfect input,
you've drifted from the reference, regardless of what these numbers say.

---

## After tuning — fill this in too

This side-by-side is one of the two most compelling case-study artifacts. Capture it while
the numbers are fresh.

| Metric | Reference | My final value | Δ | Why it differs |
|---|---|---|---|---|
| Jump height | | | | |
| Time to apex | | | | |
| Fall multiplier | | | | |
| Run speed | | | | |
| Max gap cleared | | | | |
| Distance per swing | | | | |
