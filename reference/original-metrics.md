# Reference metrics — measured from the original

**Source:** `reference-video.mov` — 990.1 s of PC-version gameplay capture, 1504×994.
**Method:** AVFoundation exact-timestamp frame extraction (zero snapping tolerance),
skin-tone blob tracking in a camera-relative window. Measured 2026-08-17.

> **Protocol changed from the plan.** The capture is **variable frame rate**
> (nominal 34.835 fps). The plan's "count frames ÷ fps" method silently produces
> wrong numbers on VFR footage — 12 frames might be 340 ms or 290 ms, and nothing
> tells you which. All timings below are read from **exact timestamps in
> milliseconds** instead, which is also what `tuning.json` wants directly.

---

## Confidence legend

| | |
|---|---|
| **SOLID** | Read from exact timestamps. Trust it. |
| **SOFT** | Spatial measurement. Depends on the character-height denominator, which 3D perspective makes uncertain by roughly ±15%. |
| **NOT MEASURABLE** | Sample was corrupted by sloped terrain or camera motion. Do not guess from it. |

---

## Measured

| Metric | Value | Confidence | Feeds |
|---|---|---|---|
| **Time to apex** | **~200 ms** | **SOLID** | `jump.timeToApexMs` |
| Jump rise (screen) | ~78 px | SOLID | — |
| Character height (same scene) | ~85–95 px | SOFT | denominator |
| **Jump height** | **~0.85 character-heights** | **SOFT** | `jump.heightTiles` |
| Fall : rise ratio | — | **NOT MEASURABLE** | `jump.fallGravityMultiplier` |
| Run speed | not yet measured | — | `run.maxSpeedTilesPerSec` |
| Accel to full run | not yet measured | — | `run.timeToMaxSpeedMs` |
| Swing arc | not yet measured | — | `swing.*` |
| Distance per swing | not yet measured | — | level grammar |

### The sample

Jump at **t = 320.0 s**. Ground at 319.92–320.00 (feet y≈428), apex at
320.205–320.233 (feet y=350), descending through 320.9.

### Why fall:rise is marked NOT MEASURABLE

He takes off from a hillside and lands on **lower ground**, so the descent
continues past takeoff height and the airtime is asymmetric for reasons that have
nothing to do with gravity. Raw numbers give rise 71 px/201 ms vs fall 114 px/689 ms
— implying fall is *slower* than rise, i.e. `fallGravityMultiplier < 1`, which is
almost certainly an artifact of the slope plus possible vertical camera pan rather
than a real property of the game.

**Measure this from a flat-ground jump before trusting any number for it.**

---

## What this already tells you — and it contradicts the plan's defaults

| Value | Plan's guess | Measured | Direction |
|---|---|---|---|
| `jump.timeToApexMs` | 350 | **~200** | Much snappier |
| `jump.heightTiles` | 3.0 | **~1.7** (at 2 tiles/character) | Much lower |

Both point the same way: **the original's jump is quicker and smaller than the plan
assumed.** That is a coherent finding, not two unrelated errors — a short, fast hop
rather than a big floaty arc, which fits the "momentum-forward and forgiving"
design target.

**Suggested starting point for the tuning block** (replacing the plan's guesses):

```json
"jump": { "heightTiles": 1.8, "timeToApexMs": 210 }
```

Start there rather than at 3.0 / 350. Then tune by feel — these are targets, not
answers.

---

## Caveats worth holding onto

1. **One jump sample**, and possibly not a maximal one. A second flat-ground jump
   would confirm or move it.
2. **3D perspective.** Character on-screen size varies with depth, so the
   character-height denominator is the weakest link in every spatial number.
   Always take it from a grounded frame in the *same* scene.
3. **Scrolling camera.** Screen-space Y mixes character motion with camera motion.
   Only measure where the camera is vertically stable, or measure relative to a
   ground line visible in the same frame.
4. `t=70 s` is a **tree-surf section**, not a standing jump — not usable.
5. `t=769 s` does not show a vine swing at that instant.

## Best remaining sources in the capture

| Moment | t | Why it's good |
|---|---|---|
| Monkey-bar vine traverse | **210 s** | Cleanest in the whole capture — high contrast, dark background |
| Run on flat ledge | **81 s** | Camera fairly stable, good for run speed and acceleration |
| Running jump over gap | **66 s** | Log crossing; needs a flat-ground segment isolated |
| Cliff hang / climb | 454 s | Clean, but climb is out of scope for v1 |

---

## After tuning — fill this in

| Metric | Reference | My final value | Δ | Why it differs |
|---|---|---|---|---|
| Jump height | ~0.85 char-h | | | |
| Time to apex | ~200 ms | | | |
| Fall multiplier | unmeasured | | | |
| Run speed | | | | |
| Max gap cleared | | | | |
| Distance per swing | | | | |
