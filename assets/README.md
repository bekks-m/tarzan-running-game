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
