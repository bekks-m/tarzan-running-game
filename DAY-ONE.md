# Day One Runbook

**Goal:** Level 1 of the real game — architecture done properly, movement tuned against measured reference targets, vine swinging, collectibles, an enemy, profiles and saves, accessibility options, deployed and playable on your phone.

**This is not a prototype.** Nobody rewrites working code, so the six load-bearing decisions in PROJECT-PLAN §5 get made properly today. Everything else is genuine deferral.

**Not today:** Spine, Blender, chase level, boss, difficulty tiers, telemetry, cloud saves, dual preview harness, save migrations.

**Total:** ~11½ hours including breaks, plus ~3 hours of prep beforehand.

> Revision 3 — remote phone session added as prep and used from the tuning block onward, save layer moved forward out of hour nine, Playwright smoke test added (CLAUDE.md was already demanding it), deny-list widened, CLAUDE.md rewritten against the corrected architecture, split points marked.
>
> Revision 2 — tuning extended to 2 hours, tests added, reference measurement added, abstractions moved to day one, accessibility added, case study capture added, App Store removed.

---

# PART 1 — BEFORE THE DAY

## 1.1 Measure the original (45 min) — do this first

You cannot tune toward "feels right" without knowing what right is. No published frame data exists, so produce your own.

1. Find a longplay of the PS1 or PC version. Record which — the console version runs at a lower framerate.
2. Step frame by frame (`,` and `.` in a paused YouTube player).
3. **Measure in character-heights and character-widths, never pixels.** `tuning.json` is authored in tiles, so these port directly.

Fill in `reference/original-metrics.md`:

| Metric | Unit | Value |
|---|---|---|
| Jump input → apex | frames @ fps | |
| Total airtime, standing jump | frames | |
| Jump height | character-heights | |
| Tapped vs held jump height | character-heights | |
| Max gap cleared, running | character-widths | |
| Run speed | char-widths / sec | |
| Acceleration to full run | frames | |
| Swing arc, grab → release | frames | |
| Distance gained per swing | character-widths | |
| Fall : rise speed | ratio | |

**Design target to hold onto:** a runner abandoned a tool-assisted speedrun of the original because most of it is "hold right" — not enough room for stunts. The game is momentum-forward and forgiving, not precision-demanding. If your level starts demanding pixel-perfect input, you've drifted.

## 1.2 Accounts and installs

- Node.js LTS; Claude Code updated (`claude update`)
- GitHub repo created and cloned; Vercel linked
- An AI asset account (Ludo is broadest — sprites, animation, tiles, music, SFX)
- **Claude app installed on the phone and signed in to the same account**
- Phone charged, same wifi as the laptop

## 1.3 Environment hygiene

A documented incident: a *legitimate* skill loaded a project's `.env` on first run and pulled every secret in it. Assume anything you install can read that file.

```bash
# Asset-tool keys live in your shell, never the repo.
echo 'export LUDO_API_KEY="..."' >> ~/.zshrc

touch .env.example
printf ".env\n.env.local\n" >> .gitignore
```

You have no backend today, so no secret needs to enter the repo at all.

## 1.4 Install official plugins only

```
/plugin install security-guidance@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install claude-code-setup@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
```

Plus Vercel and GitHub partner MCPs. Note even official means curated, not audited to zero risk — Anthropic states it cannot verify plugins work as intended.

## 1.5 Vendor the Phaser knowledge — do not install it

**Step 1 — clone into quarantine, outside your project**

```bash
mkdir -p ~/quarantine && cd ~/quarantine
git clone --depth 1 https://github.com/Yakoub-ai/phaser4-gamedev
```

**Never open Claude Code in this directory.** Plain editor and terminal only. Current Claude Code versions do prompt for workspace trust on first open of an unfamiliar directory — but that dialog is skipped in non-interactive mode, has been the subject of at least one disclosed bypass, and is not something to lean on when the alternative is "don't open it." Verify the specifics against Anthropic's own advisories rather than trusting a CVE number copied into a planning doc.

**Step 2 — delete the executable surface**

```bash
cd phaser4-gamedev
rm -rf .claude hooks scripts .github 2>/dev/null
find . -name "settings.json" -o -name "*.sh" -o -name "postinstall*"
```

Anything that command returns, read before continuing.

**Step 3 — scan for invisible Unicode instructions**

Unicode Tag characters (U+E0000–U+E007F) render as nothing but are read as instructions by the model. Demonstrated technique, not theoretical.

```bash
python3 - << 'EOF'
import pathlib
hits = []
for p in pathlib.Path('.').rglob('*'):
    if p.is_file() and p.suffix in {'.md','.json','.txt','.yaml','.yml'}:
        t = p.read_text(errors='ignore')
        n = sum(1 for c in t if 0xE0000 <= ord(c) <= 0xE007F)
        if n: hits.append((str(p), n))
print("SUSPICIOUS:" if hits else "Clean — no tag characters found.")
for h in hits: print(" ", h)
EOF
```

Anything flagged: discard the whole repo. Don't clean it.

**Step 4 — grep for exfiltration patterns**

```bash
grep -rniE 'curl|wget|\.env|base64|eval\(|child_process|exec\(|https?://[^ )]*' \
  --include='*.md' --include='*.json' --include='*.js' --include='*.ts' . | less
```

Doc URLs are fine. Endpoints, `.env` reads, encoding or execution — stop.

**Step 5 — read what survives, then copy it in**

```bash
cd /path/to/your/project
mkdir -p .claude/skills/phaser4
cp ~/quarantine/phaser4-gamedev/skills/<reviewed>/SKILL.md .claude/skills/phaser4/
git add .claude/skills && git commit -m "chore: vendor reviewed phaser 4 skills"
```

These are prompt material. If a line tells the agent to do something you wouldn't ask for, delete the line. Committed means diffable forever after.

**Step 5b — grade it for accuracy, not just safety.** *(New in revision 3.)* The likelier failure here isn't malice, it's a confidently wrong description of a young API. Spot-check three claims in the skill against `node_modules/phaser/types`. If any is wrong, keep the skill for its patterns and add a line to CLAUDE.md telling the agent the shipped types win every disagreement.

**Step 6 — same treatment for the QA pattern.** Don't install `game-creator`. Write its one good idea yourself: build-check, headless run, Playwright screenshot after each change.

## 1.6 Lock down settings

`.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(rm -fr:*)",
      "Bash(curl:*)",
      "Bash(npm install:*)",
      "Bash(npm i:*)",
      "Bash(npm add:*)",
      "Bash(pnpm add:*)",
      "Bash(pnpm install:*)",
      "Bash(yarn add:*)",
      "Bash(bun add:*)",
      "Bash(npx:*)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(**/.env)",
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)",
      "Read(~/.config/gh/**)"
    ]
  }
}
```

Revision 2 denied `npm install` alone. An agent adding a package will reach for `npm i` or `npx` with no intent to evade you and go straight past it — the list above closes the ordinary spellings.

**Write these through `/permissions` rather than by hand.** The UI emits the syntax your installed version actually parses, and a deny rule that silently fails to match is worse than no deny rule, because you'll trust it.

**Calibrate what this buys you.** These are speed bumps against accident, not a sandbox against a determined prompt injection. What actually carries the weight: never run this project in `bypassPermissions` mode, no secrets in the repo (you have no backend, so there are none), read the diff before you commit.

## 1.7 Set up the remote session (20 min) — see REMOTE-SESSION.md

Do the full dry run tonight, not tomorrow. You need this working before the tuning block, and "the phone can't see the session" is not a problem you want to debug at hour three with a tuned jump arc in your head.

```bash
cd /path/to/your/project
caffeinate -is claude --remote-control tarzan-dayone
```

Then open the Claude app on your phone, find the session, send it something trivial like "list the files in this repo," and confirm you get the answer on the phone. That's the whole test. Details, failure modes and the working loop are in **REMOTE-SESSION.md**.

## 1.8 Write CLAUDE.md

```markdown
# Project rules

## Stack
Phaser 4 + TypeScript + Vite. Read PROJECT-PLAN.md and specs.md before large changes.
When any vendored skill disagrees with node_modules/phaser/types, the types win.

## Load-bearing architecture — never bypass
1. The movement integrator is a pure function: step(state, input, tuning, dt) -> state.
   It must not import Phaser. Collision goes through the CollisionWorld interface.
2. Physics runs on a fixed timestep that this project owns. Never tie game logic to
   frame delta. Never let Phaser's auto-step drive gameplay.
3. All input goes through a single InputState object, latched once per render frame
   and consumed per physics step. Edge events fire exactly once. Movement never reads
   a key, a touch, or a gamepad directly.
4. Every feel-affecting number lives in tuning.json, and its key name carries its unit
   (Tiles, TilesPerSec, Ms, Degrees, PerSecond, Multiplier). Never inline a magic number.
   Never author a raw pixel value.
5. All persistence goes through the SaveStore interface.
6. All UI — menus, HUD, pause, options, profile picker, tuning overlay — is DOM over
   the canvas. Never draw interface text to the canvas.

## Animation
All animation goes through the AnimationController interface. Never call sprite
animation APIs from gameplay code.

## Hard rules
- `import Phaser from 'phaser'` does NOT work in Phaser 4. Use named imports.
- One system per file. Past 250 lines, split it.
- No network calls. No analytics, no CDN fonts, no remote assets.
- Never read or write .env. Never run npm install — propose the dependency instead.

## Verification
After any gameplay change: run `npm test`, then `npm run e2e:smoke`, and report both
results before saying done. Screenshots verify rendering, not correctness — logic
changes need a unit test. Never report done on a red test.
```

**Stop. Sleep.**

---

# PART 2 — THE DAY

Green-build rule: never leave a broken state uncommitted for more than 20 minutes. Roll back rather than debugging forward.

Case-study rule: every time you commit a milestone, drop a screenshot and two sentences into `/case-study`. It takes 60 seconds and it's unrecoverable later.

**Split points, if you're not doing this in one day:** after 05:00 and after 08:00. Both leave a committed, playable state. Never split inside the tuning block.

---

## 00:00–00:20 — Kickoff

Start asset generation first so it renders while you code. One locked reference image is your best defense against frame-to-frame inconsistency.

> Generate a character reference sheet for a 2D platformer protagonist: [description]. Side view, neutral standing pose, high-resolution, transparent background, flat stylized shading, no outline. Then a matching jungle tileset: ground, platform edges, hanging vines, and three parallax canopy layers at decreasing detail and increasing haze.

Verify setup: `claude --version`, `ls .claude/skills/phaser4/`, `cat .claude/settings.json`, and `/plugin` showing official-only.

Start the session with Remote Control on, so the phone is available all day without a restart:

```bash
caffeinate -is claude --remote-control tarzan-dayone
```

---

## 00:20–01:10 — Scaffold and abstractions

Plan mode on:

> Read PROJECT-PLAN.md, specs.md and CLAUDE.md. We are building Level 1 of the real game today — production code, not a prototype. Out of scope: Spine, Blender, chase level, boss, difficulty tiers, telemetry, cloud saves, dual preview harness, save migrations.
>
> Scaffold Phaser 4 + TypeScript + Vite with these six load-bearing pieces in place from the start:
> 1. A movement integrator as a pure function `step(state, input, tuning, dt)` with **no Phaser import**, and a `CollisionWorld` interface with a Phaser tilemap implementation plus a plain-fixture implementation for tests
> 2. A fixed timestep loop that this project owns and that drives Phaser, not the reverse. Clamp to maxSubSteps and discard the remainder; reset the accumulator on visibilitychange
> 3. tuning.json in design-intent units with unit suffixes on every key, constants derived at load, plus tuning.meta.json with min/max/step
> 4. A single InputState object, latched once per render frame and consumed per physics step, with edge events consumed exactly once
> 5. A SaveStore interface **and today's implementation** — IndexedDB with a synchronous localStorage mirror, promoted only after a verified read-back
> 6. A DOM UI layer over the canvas, with pointer events routed so the overlay doesn't eat gameplay taps
>
> Show me the plan before writing code.

Note item 5 says *and today's implementation*. Revision 2 built only the interface here and left the storage work for hour nine, which put a load-bearing decision in the tiredest block of the day. It's an hour of work either way; do it now.

**Commit:** `chore: scaffold with load-bearing abstractions`

---

## 01:10–01:50 — The tests

Before any gameplay. These are the safety net that replaces code review.

> Set up Vitest and write exactly three tests:
>
> 1. **Physics determinism.** Hold `world.fixedTimestepHz` at 60 for every run. Feed one recorded input timeline through the accumulator three ways: 33.33ms frames, 6.94ms frames, and a jittered sequence containing one 200ms hitch. Make total elapsed time an exact multiple of the timestep. Assert **exact equality** — not a tolerance — of final position, final velocity and total step count across all three. This runs headless against the CollisionWorld fixture, with no Phaser and no browser.
> 2. **Save round-trip.** Write, read, verify. Then confirm a truncated blob and a schema-violating blob both fail safely without throwing into game code. Then corrupt the IndexedDB blob and confirm boot falls back to the localStorage mirror and surfaces that it did.
> 3. **Derived math and unit lint.** gravityRise = 2h/t², jumpVelocity = 2h/t, runAccel, and dampingPerStep = dampingPerSecond ** (1/hz) all produce known values from known inputs. Then walk every numeric leaf in tuning.json and fail on any key that doesn't end in a known unit suffix or appear in the dimensionless allowlist.
>
> Then add one Playwright smoke test: boot the game, wait for the canvas, assert zero console errors, screenshot at 1280×720 and 390×844. Wire `npm test` and `npm run e2e:smoke`.

**Verify:** deliberately break the timestep (multiply by frame delta) and confirm test 1 fails. A test that can't fail isn't a test. Then put it back.

> Test 1 is the one that earns its keep, and revision 2 had it wrong — it described varying the *physics* rate, which legitimately changes the answer, so it would have failed honestly, been "fixed" with a tolerance, and the tolerance is exactly where a real frame-coupling bug would then live.

> Blank Playwright screenshots mean headless WebGL, not a broken renderer. Run headed or use `--use-gl=swiftshader`.

**Commit:** `test: determinism, save round-trip, derived math + unit lint`

---

## 01:50–03:00 — Movement and the tuning harness

Colored rectangle. No art.

> Implement player movement inside the pure integrator, reading exclusively from tuning.json, in this order:
> 1. Run acceleration and deceleration, with air multipliers and a turnaround multiplier
> 2. Jump using derived gravity
> 3. Asymmetric gravity — fall gravity is rise gravity × fallGravityMultiplier
> 4. Variable height — releasing mid-rise cuts upward velocity by releaseCutMultiplier
> 5. Coyote time and jump buffering, both measured in steps, not wall-clock
> 6. Apex modifier — reduced gravity and increased air control near zero vertical velocity
> 7. Corner correction — nudge around a platform corner rather than stopping dead
>
> All input via InputState. All animation state changes via AnimationController.
> Then build the debug overlay in DOM, generated from tuning.meta.json: a live range input per value, plus readouts for velocity, grounded state, airtime, and state name. It must be usable with a thumb on a phone — 44px targets, no hover affordances — and it must include the snapshot button.

Then:

> Create a training room: flat ground, ledges at 1, 2 and 3 tiles, and gaps from 2 to 7 tiles with tile markers. All tuning happens here, never in a designed level.

**Verify:** sliders change behavior with no reload; `npm test` still green; the overlay is legible on the phone.

**Case study:** screenshot the capsule and the overlay now. This is the artifact you can never recreate.

**Commit:** `feat: movement + tuning harness + training room`

---

## 03:00–05:00 — Tune the jump against your reference

**Two hours, and it's yours alone.** The agent cannot feel a jump arc. This is the highest-value block of the day.

Open `reference/original-metrics.md` beside the game. Get the game on the phone now:

```bash
npm run dev -- --host
```

Both frames are live and both get every update. **Tune with the phone in your hand** — it's the input scheme you can't simulate, and the Claude session is in the same hand if you need something changed. Desktop stays open beside you for the diff.

1. **Height and time to apex** — set directly from your measured frames ÷ fps. Start at the reference, not at a guess.
2. **Fall multiplier** — most of the difference between floaty and good. Compare against your measured fall:rise ratio.
3. **Release cut** — tap vs hold should match your two measured heights and feel like one continuous control.
4. **Coyote and buffer** — press deliberately early and late. Punishing either way means the window is too small. Remember the target: forgiving, not precise.
5. **Apex modifier** — long jumps should feel steerable, not committed.
6. **Corner correction** — clip a corner on purpose; you should slide past.
7. **Run speed and acceleration** — against measured char-widths/sec.

**Snapshot whenever something feels right, before you touch the next slider.** The button is on the overlay for exactly this and you will otherwise lose a good value to the slider after it.

**Exit condition:** your max running gap clears within ~10% of the measured reference, and you can run the gap row three times without a death that feels unfair — **on the phone**, not just on the keyboard.

```bash
mkdir -p tuning.snapshots
cp tuning.json tuning.snapshots/jump-v1.json
cp tuning.json case-study/tuning-after-reference-match.json
```

**Case study:** photo of the phone in your hand with the overlay open. It's the single frame that shows this was a process.

**Commit:** `tune: jump feel matched to reference metrics`

---

## 05:00–05:30 — Break

Leave the desk. Judgment degrades from the inside without announcing itself.

The session is still running with Remote Control on. If something occurs to you on the walk, send it from your phone and let it be waiting when you sit down. Don't approve edits you can't read properly on a 6-inch screen — queue the thought, not the change.

*(Split point. Everything before this is committed and playable.)*

---

## 05:30–06:45 — Vine swinging

> Implement vine swinging as a hand-rolled pendulum inside the pure integrator, not as a physics constraint.
> - Angular acceleration = -(gravityRise / ropeLength) × sin(θ)
> - Damping is authored PER SECOND as `swing.dampingPerSecond` and converted per step as `dampingPerSecond ** (1 / fixedTimestepHz)`. The committed value is 0.74, which equals 0.995 per step at 60Hz. Do not author a per-step value and do not carry 0.995 over into the per-second key.
> - On grab: incoming velocity converts to angular velocity × grabMomentumTransfer. Never snap to rest.
> - Pumping: holding the direction of travel adds angular acceleration, capped at maxAngularVelocity. Respect the hold-to-toggle accessibility setting.
> - On release: tangential velocity (ω × ropeLength) × releaseBoostMultiplier plus releaseUpwardBiasTilesPerSec on Y.
> - Grab assist: grabRadiusTiles within a forward cone, multiplied by grabRadiusTouchMultiplier when the active input is touch. Auto-snap to nearest valid vine, grabCooldownMs after release.

Add a vine corridor to the training room. Tune against your measured swing arc and distance-per-swing.

**Verify by feel:** a grab never kills momentum; a well-timed release travels noticeably further than a jump. If chaining feels like work, raise grab assist before touching physics — and if it's only hard on the phone, raise `grabRadiusTouchMultiplier`, not the base radius.

**If the swing feels weightless and won't settle:** check `dampingPerSecond`. 0.995 in that key is a near-frictionless pendulum and it does not present as a unit bug.

**Checkpoint:** past 07:15, drop pumping, keep momentum transfer, move on.

**Commit:** `feat: vine swinging` + `tune: swing feel v1`

---

## 06:45–08:00 — Level 1

> Derive a level grammar from current tuning.json: max jumpable gap, max ledge height, and a swing-gap unit from an average chained release. Print those numbers, then build Level 1 in Tiled loaded from JSON using only distances within them.
>
> Structure: a safe opening teaching run and jump; a gap sequence escalating to 80% of max; a vine section requiring two chained swings; a mixed challenge; an exit.

Play it three times. Anything that killed you unfairly is usually a gap at 100% of theoretical max — which is never actually fair.

**Commit:** `feat: level 1`

*(Split point. You have a playable level.)*

---

## 08:00–08:45 — Content systems

> Add: collectible coins with a pickup tween; three hidden letters off the main path, **distinguished by shape as well as colour**; one patrolling enemy defeated by a thrown projectile; a visibly-activating mid-level checkpoint; death and respawn to last checkpoint; a level-complete state showing coins and letters.

**Verify:** die deliberately after the checkpoint; confirm you return to it.

**Commit:** `feat: collectibles, enemy, checkpoint, win state`

---

## 08:45–09:20 — Profiles

Shorter than revision 2's block, because the storage layer was built in the scaffold. This is UI and wiring only.

> Build the profile select screen per specs.md section 3, as DOM over the canvas:
> - Profiles index (max 5): id, name, avatarId, lastPlayedAt, summary block; levelsTotal and lettersTotal derived from the level manifest, not stored
> - Create, delete with confirmation, "play as guest" in one tap
> - A corrupt blob renders a warning badge with Repair/Delete and never crashes the picker
> - Save on checkpoint, level complete, visibilitychange and pagehide
> - Names sanitized before the DOM, never transmitted
> - Real buttons, real focus order, keyboard and gamepad navigable, 44px targets on mobile

**Verify:** two profiles, different progress, hard refresh, both intact. Then corrupt a blob in devtools and confirm the picker survives and offers repair. `npm test` green.

**Commit:** `feat: profile select`

---

## 09:20–09:50 — Accessibility and options menu

Built now, not retrofitted. Mostly cheap because the UI is already DOM.

> Add an options menu with: remappable controls for keyboard and gamepad; a hold-to-toggle setting for sustained inputs including swing pumping; a reduced-motion toggle disabling parallax and screen shake, defaulting from prefers-reduced-motion; adjustable HUD text size driven by a CSS variable; an "extended input windows" toggle that increases coyote time and jump buffering; and pause available from anywhere including mid-swing. Store these as device settings, separate from per-profile progress.

**Verify:** tab through the whole menu with the keyboard only. If focus disappears anywhere, it isn't done.

**Commit:** `feat: accessibility options`

---

## 09:50–10:45 — Art, audio, mobile

> Replace placeholder art with the assets in /assets, wired through AnimationController — gameplay code must not change. States: idle, run, jump, fall, swing, throw. Three parallax layers at depth-proportional scroll rates. Keep the physics body separate from the sprite; the sprite may have a visual offset, the collision box must not change.

Add music and 6–8 SFX. **Do not retune movement to match art** — adjust the sprite offset instead. You tuned that with a clear head ten hours ago.

> Add touch controls: virtual stick bottom-left, jump and action bottom-right, 44px minimum targets, all routed through InputState. Scale Manager on FIT at fixed 16:9, gameplay-critical elements inside a safe zone clear of thumbs.

**Test on your actual phone**, driving the session from the phone as you go — the whole point is that the fix gets described while your thumb still remembers the problem, instead of reconstructed at the laptop two minutes later. If the vine grab isn't achievable with a real thumb, raise `grabRadiusTouchMultiplier` — never change swing physics.

**Case study:** before/after screenshots of the art swap.

**Commit:** `feat: art, audio, touch controls`

---

## 10:45–11:15 — Harden and ship

> Add a strict Content-Security-Policy and X-Frame-Options DENY **via vercel.json headers, production only** — a production CSP in dev kills the tuning WebSocket. Add a PWA manifest with icons and landscape orientation. Confirm zero outbound network requests in the production build. Run npm audit and report high or critical findings. Confirm the lockfile is committed.

Then `/security-review`, deploy to Vercel, and run the full loop on your phone against the **deployed URL**, not the dev server: create a profile, play start to finish, collect a letter, die once, finish, reload, confirm persistence.

---

## 11:15–11:30 — Land it

- README with screenshot and play URL
- `git tag v1.0-level-1 && git push --tags`
- Assemble today's case-study material: capsule screenshot, tuning overlay, phone-in-hand photo, reference metrics beside your final values, art before/after
- Write down the three things that felt worst — that's your day-two list
- Stop the Remote Control session. Don't leave it running unattended overnight.

---

# PART 3 — WHEN THINGS GO WRONG

## Cut ladder

Cut from the top:

1. The enemy and projectile
2. The three hidden letters
3. Music (keep SFX — they matter far more for feel)
4. Accessibility menu → ship reduced-motion and extended-input-windows only
5. Multiple profiles → single autosave
6. Parallax → one flat background
7. Touch controls → desktop only, mobile day two

**Never cut:** the three tests, the two-hour tuning block, the six load-bearing abstractions, or the deploy. Those either can't be added later or get silently skipped forever.

> Note that cutting #7 costs you the phone tuning loop, which is most of why the remote session is set up. Cut #6 twice before you cut #7.

## Time checkpoints

| By | You should have |
|---|---|
| 01:50 | Tests green, abstractions in place, save layer real |
| 03:00 | Movement working, sliders live on the phone |
| 05:00 | Jump matching reference metrics |
| 06:45 | Swinging that chains |
| 08:00 | A playable level start to finish |
| 09:20 | Saves surviving a reload |
| 10:45 | Something on your phone |

Behind at a checkpoint → **cut, don't compress.** Compressing produces a worse version of everything; cutting produces a smaller version of something good.

## Rules for the day

- **Commit after every working state.** You will want to roll back, probably twice.
- **Never refactor today.** Messy code that runs beats clean code that doesn't at hour nine — with the six load-bearing decisions as the standing exception. Those are not refactors, they're the reason today produces something you can build on.
- **`npm test` before every commit.** Screenshots verify rendering; tests verify correctness.
- **Plan mode before any large change**, and plan mode reads badly on a phone — start big changes at the laptop.
- **Stuck 15 minutes → revert and re-approach.** Describing the problem differently from a clean state is usually faster than debugging agent output forward.
