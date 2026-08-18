# Jungle Platformer — Project Plan

A 2.5D side-scrolling platformer cloning the mechanics of the 1999 Disney's Tarzan action game, skinned entirely with original design. **Web-first, desktop and mobile, portfolio-targeted.**

> Revision 4 — level 2 pinned to tree surfing after manual research (`reference/manual-notes.md`); collectible counts aligned to the source. Day one deliberately unchanged.
>
> Revision 3 — second critical pass. Changes: physics core made engine-agnostic and headless-testable, UI moved to DOM as a load-bearing decision, all tuning values converted to tile-relative units, swing damping unit contradiction resolved, determinism test corrected (it was testing the wrong thing), input sampling contract added, Playwright reconciled with CLAUDE.md, permission deny-list widened, remote phone session added as a first-class working mode.
>
> Revision 2 — revised against a critical review. Changes: App Store cut, scope reduced to three levels, testing strategy added, day one is now production code rather than a prototype, reference library added, accessibility added, case study capture added.

---

## 1. Locked decisions

| Question | Answer |
|---|---|
| Purpose | Portfolio piece — publicly linkable |
| **Distribution** | **Web only. A URL a reviewer opens in one click.** |
| Scope | **3 levels: one platforming, one tree-surf runner, one boss** |
| Failure model | Lives → checkpoint. Game over → start of level |
| Difficulty | Multiple tiers, hint character on lower tiers |
| Progression | Linear |
| Art | Original design, high-res, AI for concept + placeholder only |
| Audio | Generative AI with creative direction |
| Orientation | Landscape only |
| Camera | Fixed 16:9, letterboxed |
| Target device | Current iPhone via browser |
| Saves | Local now, cloud later |
| PWA | Yes |
| Telemetry | Yes — privacy-first, post-v1 |
| Accessibility | **Menu options, built in from day one** |
| **UI layer** | **DOM overlay, not canvas-drawn. See §5.** |
| **Working mode** | **Laptop session, driven from the phone via Remote Control. See REMOTE-SESSION.md.** |
| Code review | Mostly trusting agent output → **tests are the safety net, not review** |

**Why three levels, one of each type:** three *different* mechanics demonstrate more range than three platforming levels, and reviewers rarely play past level two anyway. The runner is now a third of the content rather than a bonus — scope it as a real system, not a set piece.

**Level 2 is tree surfing specifically, not a generic chase.** *(Revision 4.)* The original already shipped a three-lane runner — land on a twisting branch, auto-forward motion, duck under overhangs, jump low vines, swing wide laterally, collect throughout, with the parasol as an offensive verb against baboons ahead. That is a complete runner grammar, in the source, already balanced by people who shipped it. Building "a chase level" from scratch invents a design problem that the reference already solved. See `reference/manual-notes.md`.

**Why the runner is level 2 and not level 1**, despite the repo name: day one's job is proving the six load-bearing decisions, and it should carry the least novel risk possible. Platforming exercises the fixed timestep, the pure integrator, the collision interface and the tuning harness against a mechanic whose feel targets are already measured. The runner needs a second control scheme and its own obstacle-spacing grammar — real work, but work that benefits from an architecture already proven rather than one being invented alongside it.

**Why not the App Store:** it adds an annual fee, review risk on wrapped web content, Capacitor complexity, age ratings and the entire COPPA compliance surface — in exchange for nothing a portfolio reviewer wants. A link is strictly better. Revisit only if the game outgrows being a portfolio piece.

**IP posture:** mechanics cloned, every asset original. No Disney character names, likenesses, music, or level layouts.

---

## 2. Stack

- **Phaser 4 + TypeScript + Vite** — MIT, actively developed, one codebase for desktop and mobile.
  - Gotcha: `import Phaser from 'phaser'` does not work in v4.
  - **Phaser renders and resolves collisions. It does not own the timestep and it does not own player movement.** See §5.
- **Tiled** for levels → JSON the agent can edit directly.
- **Spine** (`@esotericsoftware/spine-phaser-v4`, needs Phaser 4.2.1+) for character animation, arriving in Phase 4 — but behind an interface that exists from day one.
- **Blender** for environment props only. No character rigging.
- **Vitest** for logic, **Playwright** for visual and gameplay verification.
- No Capacitor. No native wrapper.

> **Verified 2026-08-17.** Phaser latest is **4.2.1** — the version floor above is exactly satisfied, so Phaser 4 is shipping, not a bet. Vitest 4.1.10, Playwright 1.62.1.
>
> **The Spine package name in revision 2 was wrong.** Bare `spine-phaser-v4` 404s on npm. The correct package is the scoped `@esotericsoftware/spine-phaser-v4` (4.3.13). This is worse than a typo, because the unscoped `spine-phaser` *does* resolve — as a stale 2024 fork under an unrelated maintainer. A failed install is exactly the kind of thing that gets "helpfully" recovered into the wrong package.
>
> **Open question before Phase 3, not during it:** Spine runtimes are licensed alongside the Spine editor, which is paid. The art pipeline in §4 makes Spine load-bearing for every character. The `AnimationController` interface protects the *code* from that decision; it does not protect the budget. Check the current terms and cost, and confirm the licence covers a publicly-linkable portfolio piece, before Phase 3 starts. If it doesn't fit, the interface means falling back to sprite sheets costs one file — but that's a decision worth making with the numbers in front of you.

**Trust the shipped types over any vendored knowledge pack.** Phaser 4 is new enough that third-party skill files describing its API are as likely to be *wrong* as malicious, and a confidently wrong API description sends the agent in circles for an hour. `node_modules/phaser/types` is the authority; CLAUDE.md says so explicitly.

---

## 3. Reference library — build this before tuning

The plan previously rested on "make it feel right" with no definition of right. No published frame data exists for the original, so measure it yourself.

**Status: partially measured.** See `reference/original-metrics.md` for results and confidence levels.

### Protocol — revised, and it is not frame counting

Revision 3 said "step frame by frame, count frames ÷ fps." **That method is invalid on the capture we have.** `reference-video.mov` is a variable-frame-rate screen recording (nominal 34.835 fps), so frames are not evenly spaced in time: twelve frames might span 340 ms or 290 ms, and nothing on screen tells you which. Counting would have produced confident, wrong numbers.

Use exact-timestamp extraction instead:

1. Pull frames at precise times via AVFoundation with zero snapping tolerance (`AVAssetImageGenerator`, `requestedTimeTolerance{Before,After} = .zero`). Verified accurate to within ~20 ms of request.
2. Read timings directly in **milliseconds** — which is what `tuning.json` wants anyway, so the frame-count conversion and its error disappear entirely.
3. Measure spatial values in **character-heights**, taking the character-height denominator from a *grounded frame in the same scene*.

### Three traps specific to this source

- **3D perspective.** On-screen character size changes with depth, so a height measured in one scene does not transfer to another. This is the weakest link in every spatial number.
- **Scrolling camera.** Screen-space Y mixes character motion with camera motion. Only measure where the camera is vertically stable, or measure against a ground line visible in the same frame.
- **Sloped terrain.** A jump that lands lower than it took off has asymmetric airtime for reasons unrelated to gravity. `fallGravityMultiplier` needs a *flat-ground* jump; anything else is an artifact.

### One design target worth naming

A speedrunner who attempted a tool-assisted run abandoned it because most of the game is "hold right" — there wasn't enough room for stunts. **The original is momentum-forward and forgiving, not precision-demanding.** Target that deliberately. If your level starts requiring pixel-perfect inputs, you've drifted from the reference.

---

## 4. Art pipeline

**Hybrid:**

- **Characters → Spine skeletal animation.** Draw once as separated parts, animate bones. Tiny files, high-res costs nothing, and the work is design work rather than 150 frames of animation labor. Trade-off: limited squash-and-stretch.
- **Environments → pre-rendered 3D in Blender.** Ortho render to sprites, composite as parallax layers. ~10–15 hours of learning because no rigging or animation is involved.
- **AI** for concept exploration, turnarounds, model sheets, mood boards, static props. **Not** for animation frames — image models can't hold character consistency frame to frame.
- **Tuning uses a colored capsule.** No art.

**Critical:** all animation goes through an `AnimationController` interface from day one, with a sprite-sheet implementation behind it. Swapping in Spine at Phase 4 then touches one file instead of the player, the physics coupling, and every state transition.

---

## 5. Architecture

Schemas in `specs.md`. Summary:

- **`tuning.json`** — feel values in design-intent units (tiles, ms), physics derived at load. `tuning.meta.json` drives an auto-generated slider overlay.
- **Dev push over Vite's WebSocket** — hot-apply without reload, slider writeback, origin-tagged to prevent echo loops. Every connected frame updates, including your phone.
- **Saves** — profile index plus one atomic blob per profile, schema-versioned. IndexedDB primary, **with a synchronous localStorage mirror of the last-known-good save**, because unload handlers must be synchronous and IndexedDB cannot serve them.
- **Fixed timestep physics.** Non-negotiable.

### Load-bearing on day one

Day one produces **Level 1 of the real game**, not a prototype. Nobody rewrites working code, so these must be right immediately even in simplified form.

**1. The movement integrator is a pure function with no Phaser import.** *(New in revision 3.)*

```ts
step(state: PlayerState, input: InputFrame, tuning: DerivedTuning, dt: number): PlayerState
```

Collision goes through a `CollisionWorld` interface — a Phaser tilemap implementation in the game, a hand-built fixture implementation in tests. This is the difference between a determinism test that runs in 4ms in Node and one that needs a browser, a canvas and a real level. It is also what stops "just read `scene.time.delta` here, it's easier" from ever being tempting.

Revision 2 said "fixed timestep, non-negotiable" without saying where the timestep lives. It lives here. Phaser's physics step is driven by this loop, not the other way round: disable Arcade's auto-update and call `world.step(dt)` yourself, or don't use Arcade for the player at all.

**2. A single `InputState` object — latched per frame, consumed per step.** *(Sampling contract new in revision 3.)*

Keyboard, touch and Gamepad all write into it. Nothing else reads raw input.

- Browser events write into a pending buffer as they arrive.
- Once per **render frame**, latch the buffer into the current `InputState`.
- Each **physics step** consumes that same latched value.
- **Edge events (jump pressed, throw pressed) are consumed exactly once** — flagged by the first step that sees them, cleared after.

Without this, a 144Hz display samples input 2.4× more often than a 30Hz one, the input timeline diverges between the two, and the determinism test in §6 fails for reasons that have nothing to do with frame-coupling. It also means jump buffering is a step-count window, not a wall-clock window.

**3. All feel values behind `tuning.json` indirection.** Every numeric key carries its unit in its name (`heightTiles`, `timeToApexMs`, `maxSpeedTilesPerSec`). The suffix *is* the contract, and test 3 enforces it.

**4. Fixed timestep loop**, with an explicit spiral-of-death rule: accumulate frame delta, run at most `world.maxSubSteps` steps, **discard the remainder rather than catching up**, and log the drop in dev. Reset the accumulator to zero on `visibilitychange` — returning from a backgrounded tab hands you a multi-second delta and will otherwise teleport the player through a wall.

**5. Save layer behind a `SaveStore` interface** so cloud can slot in later. "Last-known-good" is defined: a blob is only promoted to the localStorage mirror after it has been written, read back, and passed checksum plus schema validation. A write is not a guarantee.

**6. UI lives in the DOM, over the canvas. Game lives in the canvas.** *(New in revision 3.)*

Menus, HUD, profile picker, options, pause and the tuning overlay are DOM elements in a sibling layer, not canvas-drawn text.

- Screen readers see nothing drawn to a canvas. "Accessibility built in from day one" is not true if the menus are pixels.
- "Adjustable HUD text size" is a CSS variable in DOM and a reflow engine in canvas.
- Focus management for keyboard and gamepad navigation is free in DOM and hand-rolled in canvas.
- The tuning overlay has to be usable **with a thumb on a phone**. Canvas sliders on touch are miserable; `<input type="range">` is not.
- Localization later becomes possible instead of a rewrite.

Cost: pointer events need routing so the overlay doesn't eat gameplay taps, and Playwright screenshots need the overlay hidden. Both are ten-line problems on day one and structural ones at Phase 7. `specs.md` already assumed this — "sanitize profile names before the DOM" — it was just never stated as a decision.

Everything else — Spine, migrations, the dual preview harness, telemetry — is genuine deferral.

### Corrected: swing damping

`damping` must be expressed **per second** and converted per step:

```
dampingPerStep = dampingPerSecond ** (1 / fixedTimestepHz)
```

Revision 2 identified this and then left `"damping": 0.995` sitting in the schema — which is the exact bug it was warning about. **0.995 per step at 60Hz is 0.74 per second.** Rename the key without changing the value and the vine loses 0.5% of its energy per second instead of per step: a pendulum that swings essentially forever, failing as "the swing feels weightless" rather than as a unit error you'd go looking for.

The key is now `swing.dampingPerSecond`, the value is `0.74`, and the name carries the unit so it cannot silently happen again.

---

## 6. Testing strategy

You're mostly trusting agent output, so tests are the safety net — not review, and not screenshots. Playwright verifies that pixels rendered; it cannot catch a frame-coupled timestep or a non-atomic save.

**Three tests exist from day one, before the first level:**

**1. Physics determinism — vary the *frame* rate, hold the *physics* rate constant.** *(Corrected in revision 3.)*

Revision 2 said "stepped at 30Hz and at 144Hz produces identical final position," which describes changing `fixedTimestepHz` — and a different integration granularity legitimately produces a different result. That test fails honestly, gets "fixed" with a tolerance, and the tolerance is then exactly where a real frame-coupling bug hides. Correct form:

- Hold `world.fixedTimestepHz` at 60 for every run.
- Feed one recorded input timeline through the accumulator three ways: 33.33ms frames, 6.94ms frames, and a jittered sequence including one 200ms hitch.
- Make total elapsed time an exact multiple of the timestep, or compare only at a step boundary with the accumulator drained.
- Assert **exact equality** of final position, velocity and step count. Not approximate. Identical fixed steps in identical order produce identical floats; if they don't, something read a frame delta.

Runs headless in Node against the `CollisionWorld` fixture, in milliseconds, because of load-bearing decision 1.

**2. Save round-trip** — write, read, verify; then a truncated blob and a schema-violating blob both fail safely without crashing the picker. Plus: corrupt the IndexedDB blob and confirm boot falls back to the localStorage mirror and says so out loud.

**3. Derived math + unit lint** — `gravityRise = 2h/t²` and friends produce known values from known inputs. Then walk every numeric leaf in `tuning.json` and assert its key ends in a known unit suffix (`Tiles`, `TilesPerSec`, `Ms`, `Degrees`, `PerSecond`, `Multiplier`, `Scale`, `Hz`) or sits in an explicit dimensionless allowlist. Three lines, and it's the only thing that stops raw pixel values drifting back in — which is precisely what happened between revisions of `specs.md`.

**Plus one Playwright smoke test on day one.** *(New in revision 3.)* CLAUDE.md's verification step tells the agent to run "the Playwright check" and revision 2 never created one. An instruction pointing at a tool that doesn't exist trains the agent to report success it didn't earn. The smoke test boots the game, waits for the canvas, asserts zero console errors, and screenshots 1280×720 and 390×844.

> If the screenshots come back blank, that's headless WebGL, not your renderer. Run headed, or launch Chromium with `--use-gl=swiftshader`.

**Added as systems arrive:** progression reducers as pure functions (`collectLetter(save, level, letter)` → new save) are fully unit-testable with no browser and should be. Playwright covers rendering and end-to-end gameplay on top, not instead.

---

## 7. Accessibility

Menu options, built in from day one rather than retrofitted — and made *possible* by the DOM UI decision in §5, which is why that decision is load-bearing rather than cosmetic:

- Remappable controls (keyboard and gamepad)
- **Hold-to-toggle for any sustained input** — swing pumping requires holding a direction, which is exactly the input a player with limited hand strength can't sustain
- Reduced motion — disables parallax and screen shake
- Collectibles distinguished by **shape as well as colour**
- Adjustable text size for HUD and menus
- Optional extended input windows (coyote/buffer) as a difficulty-adjacent accessibility setting
- Pause available from anywhere, including mid-swing

For a design portfolio, the absence of these is visible to a reviewer. Their presence is a talking point.

---

## 8. Privacy and security

With the App Store cut, this collapses to almost nothing.

**Privacy:** collect nothing. No persistent identifiers, no third-party analytics SDK, no transmitted names, no birthdate or location. Post-v1 telemetry is self-hosted, aggregate-only, session-scoped with a discarded random id. Publish a short retention policy. Nothing personal means no compliance program.

**Save integrity:** checksum for corruption detection, schema validation before any loaded save reaches game code. **Not anti-cheat** — a single-player save is the player's own data, so no obfuscation and no anti-tamper.

**Dependency hygiene — the larger real surface.** Your Vite and Phaser tree is hundreds of packages with postinstall hooks, a far more probable attack vector than a hand-inspected skill file:

- Commit the lockfile; `npm ci` only, never `npm install` in CI
- No new dependency without justification, and read what it pulls in
- `npm audit` in CI, review anything high or critical
- Prefer the framework's built-in over a package

**Agent tooling:** official plugins only. Community skills are **vendored, never installed** — inspected, stripped of hooks, copied into `.claude/skills/` and committed. Deny rules in `.claude/settings.json`. Never open Claude Code in a repo you didn't write.

**On deny rules — calibrate the expectation.** *(Revision 3.)* Revision 2's list denied `Bash(npm install *)` and stopped there. An agent that wants to add a package will type `npm i`, `npm add`, `pnpm add` or `npx` with no intent to evade you at all, and sail straight past it. The widened list is in DAY-ONE.md §1.6.

These are **speed bumps against accident, not a sandbox against a determined prompt injection.** The controls that actually carry weight: never run a session in `bypassPermissions` mode, keep secrets out of the repo entirely (you already do — there's no backend), and read the diff before you commit. Seatbelt, not vault.

**Web hardening:** strict CSP, HTTPS, `X-Frame-Options`, no secrets in the client bundle, sanitize profile names before the DOM. **Production only** — the dev tuning socket is a WebSocket and a production-strength CSP applied in dev will kill it, taking your phone tuning loop with it. Ship the headers from `vercel.json`, not a meta tag in `index.html`.

---

## 9. Case study capture — ongoing, not retrospective

Half of what makes this a portfolio piece rather than a game. It is unrecoverable after the fact, so capture as you go into `/case-study`:

| Capture | When |
|---|---|
| Screenshot of the capsule prototype | Before any art exists |
| Screenshot of the tuning slider overlay | Once built |
| **Photo of the phone in your hand, overlay open, game running** | Tuning session — the one artifact that reads as a practice rather than a hobby |
| `tuning.json` snapshots at each feel milestone | Each tuning session |
| A short note per significant decision — what, why, what was rejected | As decided |
| Before/after of the art swap | Phase 4 |
| Reference measurements next to your final values | After tuning |
| A 30-second capture of movement feel | Each milestone |

The tuning overlay screenshot and the reference-vs-final comparison are the two most compelling artifacts. They show process, which is what a design reviewer is actually assessing.

---

## 10. Phases

| Phase | Deliverable |
|---|---|
| 0 | Reference library measured |
| 1 | **Day one** — architecture, movement, swing, Level 1, saves, deployed |
| 2 | Tuning session 2 against reference targets |
| 3 | Art direction: Spine character, Blender environments, audio |
| 4 | **Tree-surf runner** — auto-forward, three-lane duck/jump/dodge, parasol verb |
| 5 | Boss fight |
| 6 | Difficulty tiers + hint character |
| 7 | Accessibility polish, full menu |
| 8 | Privacy-first telemetry, then difficulty tuning from real data |
| 9 | PWA, performance pass, case study assembled |

---

## 11. Timeline

Three levels rather than six roughly halves the remaining work.

**Day one is an 11½-hour day.** Revision 2's table read "Playable Level 1 — Day one" at every pace including 5 hrs/week, which can't be true at both ends. Corrected:

| Pace | Playable Level 1 | All three levels + polish |
|---|---|---|
| 5 hrs/week | ~2½ weeks — day one split across 3 sittings | 7–9 months |
| 10 hrs/week | ~1 week — 2 sittings | 4–5 months |
| 20 hrs/week | One long day, as written | 2–3 months |

If you split it, split at the 05:00 break and at 08:00 — both are green-build boundaries with a committed, playable state on either side. Do **not** split inside the tuning block; feel memory doesn't survive a night.

---

## 12. Risk register

| Risk | Mitigation |
|---|---|
| Movement never feels right | Reference library gives targets; training room isolates tuning; you tune by hand |
| Agent breaks working systems | Three unit tests from day one + Playwright smoke + constant commits |
| Day-one shortcuts calcify | Six load-bearing decisions made properly on day one |
| **Frame-coupling ships silently** | Determinism test asserts exact equality — possible only because the integrator is Phaser-free |
| Runner level is underestimated | Now a third of content, its own phase, and its grammar is taken from the source rather than invented |
| Art becomes the bottleneck | Spine caps animation cost; interface makes the swap cheap |
| Save loss on iOS Safari | PWA install exemption + export/import + localStorage mirror |
| **Phone testing loop is slow enough that you skip it** | Remote Control session — see REMOTE-SESSION.md |
| Case study never gets written | Captured continuously, not at the end |

---

## 13. Deferred

Portrait orientation, cloud sync and accounts, leaderboards, localization, level editor, additional characters, native app distribution. None enters conversation before Phase 5.
