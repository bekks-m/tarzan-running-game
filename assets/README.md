# assets/

**Everything the build loads lives here, and every file here is committed.**

That is not a style preference. Vercel builds from the git repo — if the game
imports a file that only exists on your laptop, the deploy succeeds and the game
renders nothing. Placeholder art is still *shipped* art.

| Folder | Contents |
|---|---|
| `sprites/` | Character sheets wired through `AnimationController` — idle, run, jump, fall, swing, throw |
| `tiles/` | Tileset PNG + the Tiled `.tsx`/JSON that references it |
| `parallax/` | Three canopy layers, back to front |
| `audio/` | Music + 6–8 SFX |

## Where placeholder art comes from

`art-placeholder/` is a **gitignored staging area** for raw vendor downloads.
Copy the specific files you actually use into `assets/`, and commit those.
Never point the build at `art-placeholder/`.

## Licensing

Placeholder art is Kenney (CC0, public domain) — safe to commit to a public repo
with no attribution obligation. Keep it that way: nothing enters `assets/` unless
its licence permits public redistribution.

Per PROJECT-PLAN §4, all placeholder art is replaced by original design before v1.
The `AnimationController` interface is what makes that swap cheap — gameplay code
must never reference an asset path directly.

---

## Placeholder set — Kenney New Platformer Pack 1.1 (CC0)

Staged and committed. 372 KB total. Atlases are Kenney XML format — load with
Phaser's `load.atlasXML(key, pngPath, xmlPath)`, not `load.spritesheet`.

| File | Frames |
|---|---|
| `sprites/spritesheet-characters-default.{png,xml}` | 45 |
| `sprites/spritesheet-enemies-default.{png,xml}` | — |
| `tiles/spritesheet-tiles-default.{png,xml}` | 314 |
| `parallax/background_{clouds,color_trees,fade_trees}.png` | 3 layers, back to front |
| `audio/*.ogg` | 10 SFX |

### AnimationController state mapping

The pack does not cover all six states. **Four map directly; two are deliberate
substitutes.** They are stand-ins for placeholder purposes only — do not let the
substitution leak into gameplay logic, and do not "fix" it by renaming states.

| State (PROJECT-PLAN §4) | Placeholder frame | |
|---|---|---|
| `idle` | `character_<c>_idle` | direct |
| `run` | `character_<c>_walk_a` / `_walk_b` | direct — 2-frame cycle |
| `jump` | `character_<c>_jump` | direct |
| `fall` | `character_<c>_jump` | **substitute** — pack has no distinct fall frame |
| `swing` | `character_<c>_climb_a` / `_climb_b` | **substitute** — closest hanging pose |
| `throw` | `character_<c>_hit` | **substitute** |

Colour variants: `beige`, `green`, `pink`, `purple`, `yellow`. Pick one and stay on it.

The point of the `AnimationController` interface is that these substitutions cost
nothing to undo. When original art arrives at Phase 3 with real `fall`, `swing` and
`throw` frames, one file changes and no gameplay code moves.

### Audio coverage

`sfx_jump`, `sfx_jump-high`, `sfx_coin`, `sfx_gem`, `sfx_hurt`, `sfx_throw`,
`sfx_bump`, `sfx_select`, `sfx_disappear`, `sfx_magic` — covers the plan's "6–8 SFX"
with `sfx_throw` already matching the fruit-throw verb. No music; music is #3 on the
cut ladder and SFX matter more for feel.

### Not used

`art-placeholder/` also holds 8 **3D** Kenney kits (FBX/OBJ/GLB) downloaded before it
was clear the project needs 2D sprites. They contain no 2D character animation frames
and are not used. The one exception worth remembering: `kenney_nature-kit/Side/` has
322 side-view prop pre-renders in the correct orientation for a side-scroller — useful
later for set dressing and parallax detail.
