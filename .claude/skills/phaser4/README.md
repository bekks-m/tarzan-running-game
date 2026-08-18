# Vendored Phaser 4 reference — read this before using anything in here

**Source:** `github.com/Yakoub-ai/phaser4-gamedev`, shallow-cloned to quarantine and audited 2026-08-17.
**Vendored:** 5 of 21 skills. Markdown only.
**Stripped before entry:** all hooks (`hooks.json` had a `SessionStart` shell hook), all `.sh` scripts, all `.mjs` scripts, `.claude-plugin/`, `.codex-plugin/`, `.github/`. Audited clean — no Unicode tag characters in 78 files, no exfiltration endpoints, no `.env` reads. The hook scripts were benign on inspection and were removed anyway: this directory holds prompt material, never executable material.

## Why only 5 of 21

The 16 skipped skills teach architecture, and this project's architecture is already decided and stricter. Several of them demonstrate frame-delta movement (`tilePositionX += speed * (delta / 1000)`), which load-bearing decision 2 forbids outright. Vendoring them would have put the agent's most available examples in direct conflict with the determinism test.

Skipped: `phaser-init`, `phaser-coder`, `phaser-architect`, `phaser-physics`, `phaser-matter`, `phaser-playtest`, `phaser-build`, `phaser-analyze`, `phaser-saveload`, `phaser-scene`, `phaser-animation`, `phaser-audio`, `phaser-ui`, `phaser-gdd`, `phaser-asset-advisor`, `phaser-debugger`.

## These are API references, not patterns to copy

**This corpus predates Phaser 4 stable.** It documents RC6→RC7 churn from the pre-release period; Phaser shipped **4.2.1** stable well after it was written. Some drift notes describe behavior that has since resolved.

> **When this reference disagrees with `node_modules/phaser/types`, the types win. Every time. No exceptions.**

## Four places where CLAUDE.md overrides what the examples show

The examples below are correct *as Phaser API usage* and wrong *for this project*. Read the API, ignore the architecture.

| The examples show | This project requires | Rule |
|---|---|---|
| `this.add.text(...)` for HUD and score — 8 occurrences across `phaser-gameobj` and `phaser-mobile` | **DOM elements over the canvas.** Never draw interface text to the canvas. | Decision 6 |
| `cursors.left.isDown` read directly in `update()` — `phaser-input/SKILL.md:25-27`, `virtual-joystick.md:279-285` | **All input through the single `InputState` object**, latched per frame, consumed per step. | Decision 3 |
| `update(time, delta)` driving movement | **Movement lives in the pure integrator**, stepped at fixed `dt`. Phaser never drives gameplay timing. | Decisions 1, 2 |
| `npm install phaser@...` | **Never run npm install.** Propose the dependency instead. (The `@beta` pins were also stale and have been corrected to `^4.2.1` in place.) | Hard rules |

## What each vendored skill is actually good for

| Skill | Use it for | Ignore |
|---|---|---|
| `phaser-migrate` | The v3→v4 API delta. The highest-value part of this corpus — v4 is new and the removals are non-obvious. | `rc6-to-rc7-changes.md` is pre-stable churn; verify anything it claims against the types |
| `phaser-tilemap` | Tiled export settings and the tilemap API. Lowest architectural opinion of the set. | — |
| `phaser-input` | Gamepad and pointer API surface; `virtual-joystick.md` is directly relevant to touch controls | Its `update()` examples — route everything through `InputState` |
| `phaser-mobile` | Scale Manager, safe areas, iOS Safari quirks. Directly relevant to fixed 16:9 letterboxing. | Its `add.text` HUD examples |
| `phaser-gameobj` | Flat game-object API reference | Its text examples |

## One good idea worth stealing, not installing

The stripped `check-v3-api.sh` was a `PreToolUse` hook that grepped writes for removed v3 APIs and warned. That's a genuinely good idea. If it proves needed, write it yourself against `node_modules/phaser/types` rather than reinstating a third-party script — the plan's §1.5 step 6 rule.
