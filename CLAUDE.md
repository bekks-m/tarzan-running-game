# Project rules

## Stack

Phaser 4 + TypeScript + Vite. Read `PROJECT-PLAN.md` and `specs.md` before large changes.

When any vendored skill disagrees with `node_modules/phaser/types`, the types win.
Before using anything in `.claude/skills/phaser4/`, read that directory's `README.md` —
it is API reference from the Phaser 4 pre-release period, and it demonstrates several
patterns this project forbids.

## Load-bearing architecture — never bypass

1. **The movement integrator is a pure function:** `step(state, input, tuning, dt) -> state`.
   It must not import Phaser. Collision goes through the `CollisionWorld` interface.
2. **Physics runs on a fixed timestep that this project owns.** Never tie game logic to
   frame delta. Never let Phaser's auto-step drive gameplay. Clamp to `maxSubSteps` and
   discard the remainder; reset the accumulator on `visibilitychange`.
3. **All input goes through a single `InputState` object**, latched once per render frame
   and consumed per physics step. Edge events fire exactly once. Movement never reads a
   key, a touch, or a gamepad directly.
4. **Every feel-affecting number lives in `tuning.json`**, and its key name carries its
   unit (`Tiles`, `TilesPerSec`, `Ms`, `Degrees`, `PerSecond`, `Multiplier`, `Scale`, `Hz`).
   Never inline a magic number. Never author a raw pixel value.
5. **All persistence goes through the `SaveStore` interface.** A blob is promoted to the
   localStorage mirror only after a verified read-back, never on write alone.
6. **All UI is DOM over the canvas** — menus, HUD, pause, options, profile picker, tuning
   overlay. Never draw interface text to the canvas.

## Animation

All animation goes through the `AnimationController` interface. Never call sprite
animation APIs from gameplay code.

## Hard rules

- `import Phaser from 'phaser'` does NOT work in Phaser 4. Use named imports.
- One system per file. Past 250 lines, split it.
- No network calls. No analytics, no CDN fonts, no remote assets.
- Never read or write `.env`. Never run `npm install` — propose the dependency instead.
- The production CSP is production-only, shipped from `vercel.json`. A production CSP in
  dev kills the tuning WebSocket.

## Verification

After any gameplay change: run `npm test`, then `npm run e2e:smoke`, and report both
results before saying done. Screenshots verify rendering, not correctness — logic changes
need a unit test. **Never report done on a red test.**

## Known gotchas

- Blank Playwright screenshots mean headless WebGL, not a broken renderer. Run headed or
  use `--use-gl=swiftshader`.
- Swing feeling weightless and refusing to settle: check `swing.dampingPerSecond`. The
  value is `0.74` (= `0.995` per step at 60Hz). `0.995` in that key is a near-frictionless
  pendulum and does not present as a unit bug.
- The Spine runtime package is `@esotericsoftware/spine-phaser-v4`. The unscoped
  `spine-phaser` on npm is a stale third-party fork — do not use it.
