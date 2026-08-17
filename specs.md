# Specs: Tuning, Dev Push Contract, Profile Select

Three specs, written to be dropped into `/docs` and referenced from `CLAUDE.md`.

> Revision 3 — every raw-pixel value converted to tile-relative, `damping` renamed and revalued, unit-suffix naming rule made a hard contract, touch grab-assist multiplier added, late-join handshake added to the dev push contract, `levelsTotal` corrected to 3, "last-known-good" given a definition.

---

## 1. `tuning.json`

### Principles

- **Design intent, not derived physics.** Author "3 tiles high, 350ms to apex" — never a gravity constant. The engine derives the rest at load.
- **The key name carries the unit.** `heightTiles`, `timeToApexMs`, `maxSpeedTilesPerSec`. This is a contract, not a style preference — test 3 walks the document and fails on any numeric leaf whose key doesn't end in a known suffix or appear in the dimensionless allowlist.
- **Two files.** `tuning.json` is pure data (clean diffs, small payload). `tuning.meta.json` holds slider ranges, units, and apply-mode. The debug overlay is *generated* from the meta file, so adding a value adds a slider for free.
- **Nothing hardcoded.** If a number affects feel, it lives here.

### Unit suffixes

| Suffix | Conversion at load |
|---|---|
| `Tiles` | × `world.tileSize` → px |
| `TilesPerSec` | × `world.tileSize` → px/sec |
| `Ms` | ÷ 1000 → sec |
| `Degrees` | × π/180 → rad |
| `PerSecond` | exponentiated to per-step — see damping |
| `Hz` | used as-is |
| `Multiplier`, `Scale` | dimensionless, used as-is |

Dimensionless allowlist (no suffix required): `tileSize`, `maxSubSteps`, `schemaVersion`, `autoSnapToNearest`, `pumpAngularAccel`, `maxAngularVelocity`.

> `pumpAngularAccel` and `maxAngularVelocity` are genuinely angular — rad/s² and rad/s — and are dimensionless with respect to tile size. They're allowlisted rather than suffixed because renaming them to `RadPerSecSq` reads worse than the exemption.

### `tuning.json`

```json
{
  "schemaVersion": 2,
  "world": {
    "tileSize": 32,
    "fixedTimestepHz": 60,
    "maxSubSteps": 5
  },
  "run": {
    "maxSpeedTilesPerSec": 8.0,
    "timeToMaxSpeedMs": 120,
    "timeToStopMs": 80,
    "turnaroundMultiplier": 2.0,
    "airAccelMultiplier": 0.7,
    "airDragMultiplier": 0.4
  },
  "jump": {
    "heightTiles": 3.0,
    "timeToApexMs": 350,
    "fallGravityMultiplier": 2.0,
    "releaseCutMultiplier": 0.4,
    "coyoteMs": 100,
    "bufferMs": 120,
    "apexVelocityThresholdTilesPerSec": 2.0,
    "apexGravityMultiplier": 0.5,
    "apexAirControlMultiplier": 1.3,
    "cornerCorrectionTiles": 0.2,
    "maxFallSpeedTilesPerSec": 28.0
  },
  "swing": {
    "defaultRopeLengthTiles": 5.0,
    "gravityScale": 1.0,
    "dampingPerSecond": 0.74,
    "pumpAngularAccel": 3.2,
    "maxAngularVelocity": 4.0,
    "grabRadiusTiles": 1.5,
    "grabRadiusTouchMultiplier": 1.5,
    "grabConeDegrees": 60,
    "grabMomentumTransfer": 0.85,
    "grabCooldownMs": 150,
    "releaseBoostMultiplier": 1.2,
    "releaseUpwardBiasTilesPerSec": 3.75,
    "autoSnapToNearest": true
  },
  "combat": {
    "fruitSpeedTilesPerSec": 16.0,
    "fruitArcGravityScale": 0.6,
    "throwCooldownMs": 300,
    "hitstopMs": 60
  },
  "camera": {
    "lookaheadTiles": 3.0,
    "lookaheadSmoothMs": 240,
    "followSmoothMs": 140,
    "deadzoneWidthTiles": 2.0,
    "deadzoneHeightTiles": 3.0
  }
}
```

**What changed from schemaVersion 1 and why.** Revision 2 opened with "design intent, never pixels" and then authored nine values in raw pixels — `apexVelocityThreshold`, `maxFallSpeed`, `cornerCorrectionPx`, `grabRadiusPx`, `releaseUpwardBias`, `fruitSpeed`, `lookaheadPx`, `deadzoneWidthPx`, `deadzoneHeightPx`. Each one would have silently broken the moment `tileSize` changed, which is a thing you will do when the art arrives at a different resolution than the placeholder capsule. The suffix rule and the lint in test 3 exist so this can't quietly return.

**`grabRadiusTouchMultiplier` is new and it is load-bearing for the phone.** The plan says "if the vine grab isn't achievable with a real thumb, raise grab assist — never change swing physics." Without a touch-specific multiplier, doing that also loosens grab on desktop, and you end up tuning one input scheme by degrading the other. Multiply `grabRadiusTiles` by this when the active input source is touch.

### Derivations (document these in code comments)

Let `h = jump.heightTiles × world.tileSize`, `t = jump.timeToApexMs / 1000`.

```
gravityRise     = 2h / t²
jumpVelocity    = 2h / t
gravityFall     = gravityRise × fallGravityMultiplier
runAccel        = maxSpeed / (timeToMaxSpeedMs / 1000)
runDecel        = maxSpeed / (timeToStopMs / 1000)
swingAngAccel   = -(gravityRise / ropeLength) × sin(θ)
dampingPerStep  = dampingPerSecond ** (1 / fixedTimestepHz)
releaseVel      = (ω × ropeLength) × releaseBoostMultiplier + upwardBias
```

**On damping specifically.** `0.74` per second is `0.995` per step at 60Hz — verify with `0.74 ** (1/60) ≈ 0.99499`. Author the per-second value and derive the per-step one, because the alternative is that moving `fixedTimestepHz` from 60 to 120 halves the energy loss per second and changes the swing feel with no diff to explain it. Revision 2 named this hazard and then shipped `"damping": 0.995` anyway; if you rename that key to `dampingPerSecond` without also changing the number to `0.74`, the vine becomes effectively frictionless and reads as "weightless," not as a unit bug.

### `tuning.meta.json`

Keyed by dot-path. Drives the overlay and validates incoming writes.

```json
{
  "jump.heightTiles": {
    "label": "Jump height",
    "unit": "tiles",
    "min": 0.5, "max": 8, "step": 0.1,
    "applyMode": "live",
    "note": "Design in tiles so level grammar stays derivable."
  },
  "jump.timeToApexMs": {
    "label": "Time to apex",
    "unit": "ms",
    "min": 100, "max": 900, "step": 5,
    "applyMode": "live"
  },
  "jump.fallGravityMultiplier": {
    "label": "Fall gravity",
    "unit": "×rise",
    "min": 1.0, "max": 4.0, "step": 0.05,
    "applyMode": "live",
    "note": "Most of the difference between floaty and good."
  },
  "swing.dampingPerSecond": {
    "label": "Swing damping",
    "unit": "per second",
    "min": 0.10, "max": 1.00, "step": 0.01,
    "applyMode": "live",
    "note": "PER SECOND. Converted per-step at load. 0.74/sec = 0.995/step at 60Hz."
  },
  "swing.grabRadiusTiles": {
    "label": "Grab assist radius",
    "unit": "tiles",
    "min": 0.5, "max": 4.0, "step": 0.1,
    "applyMode": "live"
  },
  "swing.grabRadiusTouchMultiplier": {
    "label": "Grab assist — touch bonus",
    "unit": "×",
    "min": 1.0, "max": 3.0, "step": 0.1,
    "applyMode": "live",
    "note": "Raise this on the phone, not the base radius."
  },
  "world.fixedTimestepHz": {
    "label": "Physics rate",
    "unit": "hz",
    "min": 30, "max": 120, "step": 10,
    "applyMode": "reload"
  }
}
```

`applyMode`:

| Value | Meaning |
|---|---|
| `live` | Patch running objects immediately. Default. Most feel values. |
| `respawn` | Needs the player re-instantiated; harness respawns at last position. |
| `reload` | Full page reload (timestep, renderer config). |

Any path missing from meta defaults to `live` with no slider — it still hot-applies, it just isn't exposed in the overlay.

---

## 2. Dev push contract

### Transport

Don't stand up a separate WebSocket server. Use Vite's existing dev socket via a small plugin — `server.ws.send()` outbound, `server.ws.on()` inbound, `import.meta.hot.on()` on the client. Free reconnection, no port juggling, and the whole thing tree-shakes out of production behind `import.meta.env.DEV`.

**This is why the production CSP is production-only.** A `connect-src 'self'` policy applied in dev kills the tuning socket, and the failure looks like "sliders stopped working on the phone."

### Message envelope

Every message carries:

```json
{ "seq": 42, "origin": "server" | "client:<sessionId>", "ts": 1723900000000 }
```

`origin` is what prevents the echo loop: when a slider drag writes to disk, the resulting file-watch event bounces back and would stomp the value mid-drag. Clients ignore any `tuning:update` whose `origin` matches their own session id.

### Server → client

**`tuning:hello`** — sent immediately on connect. *(New in revision 3.)* Carries the full current document. Without it, a phone that joins after you've already been dragging sliders on the laptop starts from whatever was in the bundle and shows different values than the desktop frame — and you spend ten minutes convinced the socket is broken. Late joiners are the normal case here, not the edge case, because you pick the phone up mid-session.

**`tuning:update`** — file changed on disk (Claude Code edit, git checkout, or an echoed client write).

```json
{
  "seq": 42,
  "origin": "server",
  "ts": 1723900000000,
  "tuning": { "...full document..." },
  "changedPaths": ["jump.heightTiles", "jump.timeToApexMs"],
  "applyMode": "live"
}
```

Send the full document, not a patch — it's a few KB, and partial application is a class of bug you don't need. `changedPaths` is for logging and for deciding the strongest `applyMode` among the changes.

**`tuning:error`** — malformed JSON on disk.

```json
{ "seq": 43, "origin": "server", "error": "Unexpected token } at line 14", "path": "tuning.json" }
```

Client shows a non-blocking banner and **keeps the last good values running**. Never reset to defaults on a parse error — you'll lose an hour of tuning to a stray comma.

**`tuning:reverted`** — file returned to last-known-good after an error.

### Client → server

**`tuning:write`** — slider moved or overlay "save" pressed.

```json
{
  "seq": 88,
  "origin": "client:a3f9",
  "changes": [ { "path": "jump.heightTiles", "value": 3.4 } ]
}
```

Server behavior:
1. Validate each path exists in `tuning.meta.json` and the value is within `min`/`max`. Reject out-of-range with `tuning:error` rather than writing garbage to disk.
2. Coalesce writes on a 100ms trailing debounce — a slider drag emits ~60/sec and you don't want 60 file writes or 60 git-visible changes.
3. Write the whole document with stable key order and 2-space indent, so diffs stay readable.
4. Echo `tuning:update` with the client's `origin` so *other* connected frames (desktop + phone) update while the dragging one doesn't fight itself.

**`tuning:reset`** — `{ "scope": "all" | "<section>" }`. Restores from `tuning.defaults.json`, which is committed and never written to.

**`tuning:snapshot`** — `{ "label": "swing-feels-good" }`. Copies current values to `tuning.snapshots/<label>.json`. Cheap insurance; you will want to A/B two feels and you will lose one of them otherwise. **Put this button somewhere your thumb can reach** — the snapshot you actually need is the one taken on the phone one second before you wrecked a good value.

### Client apply

- `live` → walk `changedPaths`, patch the tuning singleton, recompute derived values, notify subscribed systems. Never re-instantiate the player.
- `respawn` → capture position and state, rebuild player, restore.
- `reload` → `location.reload()`, with session state restored from sessionStorage per the harness spec.

### Multi-frame

Both preview frames (desktop and phone) hold their own connection with distinct session ids. Every frame receives every update. That's the point: one edit, both viewports change at once.

**The phone is the primary tuning surface, not a verification afterthought.** It's the device with the input scheme you can't simulate, and the tuning overlay is DOM (see PROJECT-PLAN §5) specifically so a range input is draggable with a thumb. During the tuning block the loop is: play on the phone, drag on the phone, `tuning.json` on the laptop changes, both frames update. See REMOTE-SESSION.md for driving the Claude session from the same hand.

---

## 3. Profile select

### Screen states

```
boot
 └─ read profiles:index
     ├─ index empty            → FIRST_RUN
     ├─ index has entries      → PICKER
     └─ storage unavailable    → GUEST_ONLY
```

| State | Contents |
|---|---|
| `FIRST_RUN` | Title, one primary "Create profile", secondary "Play as guest" |
| `PICKER` | Profile cards + "New profile" tile (hidden at cap) + "Play as guest" link |
| `CREATE` | Name field (12 char max), avatar picker, Create / Cancel |
| `MANAGE` | Long-press or edit toggle → Rename / Delete per card |
| `CONFIRM_DELETE` | Names the profile and its completion %, requires explicit confirm |
| `GUEST_ONLY` | Banner explaining progress won't be saved, single "Play" action |

Cap profiles at 5. Guest is always reachable in one tap — nobody should hit a form before they can play.

**This screen is DOM.** Real `<button>`s, real focus order, real `<input>` for the name field so iOS gives you a keyboard without you building one. Canvas-drawn text here would put the first screen a reviewer sees outside the reach of a screen reader.

### Card data

Read entirely from `profiles:index`, never by loading full saves. The picker must render instantly.

```json
{
  "profiles": [
    {
      "id": "p_01H8X...",
      "name": "Bekks",
      "avatarId": "leaf-03",
      "createdAt": 1723900000000,
      "lastPlayedAt": 1723986400000,
      "summary": {
        "levelsCompleted": 1,
        "levelsTotal": 3,
        "lettersFound": 2,
        "lettersTotal": 9,
        "coins": 4820
      }
    }
  ],
  "lastUsedProfileId": "p_01H8X...",
  "schemaVersion": 1
}
```

> `levelsTotal` was 6 in revision 2, against a scope locked at 3. Doc drift like this is how a wrong constant ends up hardcoded in a progress bar. Both totals are now derived from the level manifest at boot rather than stored — the index caches them for render speed, the manifest is the truth.

Card shows: avatar, name, a progress bar from `levelsCompleted / levelsTotal`, letter count, and relative last-played ("2 days ago"). Sort by `lastPlayedAt` descending; pre-focus `lastUsedProfileId` so gamepad and keyboard land on the likely choice.

### Last-known-good — definition

*(New in revision 3. Revision 2 used the phrase four times without defining it.)*

A blob is promoted to the synchronous localStorage mirror only after it has been **written to IndexedDB, read back, and passed both checksum and schema validation.** Not on write. A successful `put()` is not evidence the bytes survived, and mirroring an unverified blob means both copies can be corrupt in the same way.

On boot: if the IndexedDB blob fails validation, fall back to the mirror, load it, and **tell the player** — "restored from backup, you may have lost the last few minutes" — rather than silently rolling their progress back.

### Layout

- **Desktop** — horizontal row of cards, keyboard and gamepad navigable, Enter/A to select, no hover-only affordances.
- **Mobile** — vertical stack, full-width cards, minimum 44px touch targets, no tiny inline edit icons. Rename and delete live behind an explicit "Edit" toggle rather than swipe gestures, which conflict with browser back-swipe on iOS.

### Error and edge cases

| Case | Behavior |
|---|---|
| Corrupted profile blob | Card renders with a warning badge; selecting it offers "Repair" (reset to last valid migration) or "Delete". Never crash the picker. |
| Index present, blob missing | Same as corrupted. Index is the source of truth for *what exists*, blob for *what's in it*. |
| Quota exceeded on create | Inline message on the create form, offer export-and-delete of an existing profile. |
| Storage entirely unavailable | Drop to `GUEST_ONLY` with an honest banner. Don't pretend to save. |
| Duplicate name | Allowed. `id` is the key; two kids named Sam is a real scenario. |

### Actions to expose here

Export and import belong on the profile card, not buried in settings — given browser storage can be evicted, this is the only durable backup a player has. Export writes `<name>-save.json`; import creates a *new* profile rather than overwriting, so a mis-tap can't destroy progress.

### Dev fixtures

Under `import.meta.env.DEV`, a `?profile=` URL param loads a seeded fixture from `fixtures/profiles/` — `fresh`, `mid-game`, `all-unlocked`, `corrupt` — into a separate `dev:` storage namespace. This is how the preview harness jumps straight to any game state, and how the corrupted-save path gets tested without hand-mangling a real blob.

**Keep the fixture URLs short enough to type on a phone.** `?profile=corrupt` is the whole point; you will want to reproduce a picker bug on iOS Safari without a laptop in reach.
