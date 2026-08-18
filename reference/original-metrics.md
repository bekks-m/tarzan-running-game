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

Source: **`jumps.mov`** — 8.1 s, three deliberate jumps on a **flat log with a static
world**. This is the good sample; the earlier `reference-video.mov` numbers are
superseded (see correction below).

Method: exact-timestamp extraction, skin-tone blob tracking, **and per-frame camera
compensation** — the camera pans vertically up to 254 px during a jump, so raw screen-Y
is meaningless. World-Y is recovered by cross-correlating static background rows against
a reference frame and subtracting the camera offset.

| Jump | Rise | Fall | Airtime | Peak height | fall/rise |
|---|---|---|---|---|---|
| **Small** (tapped) | **128 ms** | 128 ms | 256 ms | **1.18 char-heights** | 1.00 |
| **Medium** | **333 ms** | 384 ms | 717 ms | **3.31 char-heights** | 1.15 |
| **Large** (held) | **333 ms** | 589 ms | 922 ms | **3.91 char-heights** | 1.77 |

Character height 74 px (63 px skin-masked + ~18% for the dark hair the mask excludes),
median over 198 grounded frames. Ground plane flat at world-Y 500.

---

## CORRECTION — the earlier 200 ms figure was wrong

An earlier pass on `reference-video.mov` reported **time to apex ~200 ms** and concluded
the plan's 350 ms guess was far too slow. **Discard that.** That sample was taken on
sloped terrain with an uncompensated panning camera — both errors push the apex earlier.

The flat-ground, camera-corrected measurement is **333 ms**, which means the plan's
original guess of 350 ms was very nearly right. The reference-video jump-height figure
(~0.85 char-heights) is superseded for the same reason.

Lesson worth keeping: on this source, *any* measurement without camera compensation is
untrustworthy, and it fails in a direction that looks plausible rather than obviously broken.

---

## What this changes in tuning.json

| Value | Plan's guess | Measured | Verdict |
|---|---|---|---|
| `jump.timeToApexMs` | 350 | **333** | Guess was good — keep ~335 |
| `jump.heightTiles` | 3.0 | **~7.8** (at 2 tiles/character) | **Guess was far too low** |
| `jump.releaseCutMultiplier` | 0.4 | **~0.55** | Slightly too aggressive |
| `jump.fallGravityMultiplier` | 2.0 | **~1.0, see caveat** | **Guess likely too high** |

Height ratio tapped:held = 1.18 : 3.91 = **0.30**. Height scales with v², so the velocity
cut is sqrt(0.30) ≈ **0.55**.

### Caveat on fallGravityMultiplier — still not fully settled

The small jump is textbook symmetric: rise 128 ms, fall 128 ms, ratio 1.00, implying
**fall gravity == rise gravity**. But medium and large show fall *longer* than rise
(1.15, 1.77), implying fall is *slower*.

Constant gravity cannot produce both. Either the bigger jumps land below takeoff height,
or the landing-recovery animation extends the detected airborne segment, or the game
genuinely floats the descent on longer jumps.

**Do not set `fallGravityMultiplier` to 2.0 on the plan's say-so.** Start at **1.0** —
which the cleanest sample directly supports — and raise it by feel only if the fall reads
as floaty. This is the value the plan calls "most of the difference between floaty and
good," so it deserves the tuning block's attention rather than an inherited guess.

### Suggested starting point

```json
"jump": {
  "heightTiles": 7.5,
  "timeToApexMs": 335,
  "releaseCutMultiplier": 0.55,
  "fallGravityMultiplier": 1.0
}
```

Two of those four move a long way from the plan's defaults. Start here, then tune by feel.

## Still unmeasured

| Metric | Best source |
|---|---|
| Run speed, acceleration | `reference-video.mov` t=81 s |
| Swing arc, distance per swing | `reference-video.mov` t=210 s (monkey-bar traverse) |
| Max gap cleared running | needs a flat-ground gap sequence |

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
