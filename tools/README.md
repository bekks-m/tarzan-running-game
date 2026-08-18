# Measurement tooling

Extracts frames from a gameplay capture and measures movement from them. Used to
produce `reference/original-metrics.md`.

Requires: macOS (Swift + AVFoundation), Python 3 with `pillow` and `numpy`.
No installs beyond those — no ffmpeg, no scipy.

---

## The method, in five steps

### 1. Check the framerate first

```bash
swift tools/vidtool.swift info reference/jumps.mov
```

**If `nominal_fps` is not a clean 30 or 60, the capture is variable frame rate and
you must not count frames.** Both of our captures are VFR (34.8 and 39.1 nominal).
On VFR footage twelve frames might span 340 ms or 290 ms and nothing tells you
which. Work in timestamps, never frame counts.

### 2. Extract frames at exact times

```bash
# every frame for 315 frames starting at t=0.05
swift tools/vidtool.swift burst reference/jumps.mov /tmp/f 0.05 315

# specific moments only
swift tools/vidtool.swift grab reference/video.mov /tmp/f 81.0 210.0 320.4
```

Zero snapping tolerance — accurate to ~20 ms of the requested time.

### 3. Look before you measure

```bash
python3 tools/contact-sheet.py /tmp/f sheet.png 3 6     # every 3rd frame, 6 cols
```

Always do this. It costs nothing and it is how you find out the clip is a
tree-surf section rather than the standing jump you assumed.

### 4. Track, with camera compensation

```bash
python3 tools/track.py /tmp/f > trace.txt
```

Outputs `t, screen_feet, cam_dy, world_feet, blob_height, cx`.

**`world_feet` is the only column you should measure from.** The camera pans
vertically up to 254 px during a jump; `screen_feet` is camera motion and character
motion added together. The tool recovers the camera offset by cross-correlating
static background rows against the first frame.

Tune the crop if the tracker locks onto the wrong thing:

- `--y1` must exclude the HUD (warm-coloured health bar and lives counter)
- `--x0/--x1` should exclude collectibles, which are the same orange as skin
- `--bg0/--bg1` must be a strip the character never enters
- `--range` must exceed the real camera pan — **if reported `cam_dy` hits the
  range limit, it is clipping and every number downstream is wrong**

### 5. Read the trace

- **Ground** = the modal `world_feet` across frames where `cam_dy == 0`
- **Character height** = median `blob_height` on those same grounded frames,
  ×1.18 to add the dark hair the skin mask misses
- **Takeoff / apex / landing** = first, minimum, last of an airborne run
- Timings come from the `t` column directly. Heights go in character-heights,
  never pixels — perspective changes the pixel scale between scenes.

---

## Three traps this source has

1. **Vertical camera pan.** Step 4 handles it. Skipping it makes jumps read
   shorter *and* faster, which looks plausible and is wrong. This is what made an
   early pass report 200 ms instead of the true 333 ms.
2. **3D perspective.** On-screen character size changes with depth, so a height
   measured in one scene does not transfer to another. Always take the
   character-height denominator from a grounded frame in the *same* scene.
3. **Sloped terrain.** A jump landing lower than it took off has asymmetric
   airtime for reasons unrelated to gravity. `fallGravityMultiplier` needs flat
   ground; anything else is an artifact.

---

## Still unmeasured

| Metric | Source | Notes |
|---|---|---|
| Run speed, acceleration | `reference-video.mov` t≈81 s | Needs **horizontal** camera compensation — `track.py` only corrects Y today. Extend `camera_dy` to columns, then read `cx` displacement per second and divide by character *width*. |
| Swing arc, distance/swing | `reference-video.mov` t≈210 s | Different method: find the vine pivot, then measure the angle from pivot to character per frame. Cleanest footage in the capture — dark background, high contrast. |
| Max gap cleared | needs a flat-ground gap | Measure in character-widths, not pixels. |
