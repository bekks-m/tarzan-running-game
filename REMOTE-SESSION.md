# Remote Session — driving the build from your phone

**What you want:** one Claude session, running on the laptop in this repo, that you can talk to from your phone while you're holding the phone and playing the game on it.

**What does that:** Remote Control. `claude --remote-control <name>` starts an ordinary interactive session on the laptop with remote access turned on, and the Claude app on your phone drives *that same session* — same conversation, same working directory, same dev server, same git state. It isn't a copy or a handoff. It's the session you left open, reachable from your pocket.

Verified against Claude Code **2.1.150** (your installed version):

```
--remote-control [name]                          Start an interactive session with Remote Control enabled (optionally named)
--remote-control-session-name-prefix <prefix>    Prefix for auto-generated Remote Control session names (default: hostname)
```

---

## Setup

Do this tonight, in the 1.7 prep block. Not on the day.

**1. Phone.** Install the Claude app, sign in as `rebekahjoym@gmail.com` — the same account the laptop CLI is authenticated with. Mismatched accounts is the most likely reason a session doesn't appear.

**2. Laptop.** In the project directory:

```bash
cd /path/to/tarzan-running-game
caffeinate -is claude --remote-control tarzan-dayone
```

Name it. The default prefix is your hostname, and by hour six you may have more than one session running — a named session is the one you can find on a phone screen without squinting.

**3. Phone.** Open the app, find `tarzan-dayone` in the Claude Code sessions list, and send something trivial:

> list the files in this repo

If the answer comes back on the phone, you're done. **That's the entire dry run** — do it once, tonight, so the day doesn't start with an unfamiliar failure.

**4. Stop it** when you're finished: `Ctrl-C` at the laptop. Don't leave it running unattended overnight.

> The CLI flags above are confirmed on your version. The exact phone-side navigation is whatever the current app build shows — check it during the dry run rather than trusting a screenshot in a planning doc written today.

---

## Why this matters for *this* project specifically

It isn't a convenience. It closes the one loop the plan otherwise leaves broken.

**The 10:00 mobile block.** Revision 2's instruction is "test on your actual phone." What that actually means without remote control: you play, you feel that the vine grab is a fraction too tight for a thumb, you put the phone down, you cross the room, and you type a reconstruction of a feeling you had ninety seconds ago. The signal degrades in transit. Feel notes have a shelf life measured in seconds.

With the session on the phone, you describe it while your thumb still remembers it, and you're still looking at the thing you're describing.

**The 03:00 tuning block — the bigger win.** Three things are on the phone at once:

| On the phone | Because |
|---|---|
| The game, via `npm run dev -- --host` | It's the input scheme you can't simulate at a keyboard |
| The tuning overlay | It's DOM, so `<input type="range">` is thumb-draggable (PROJECT-PLAN §5, decision 6) |
| The Claude session | So "the apex feels mushy, try 0.45 on the release cut" happens without standing up |

A slider drag on the phone sends `tuning:write` over the dev socket, the laptop writes `tuning.json`, and both frames update. The file on disk is the source of truth the whole time, so everything you do with your thumb is still a reviewable diff and a `git` history.

This is the loop the two-hour tuning block was always describing. It just wasn't reachable before.

**Away from the desk.** The 05:00 break, the walk, the bus. Something occurs to you about the gap sequence — send it, let it be waiting when you sit down.

**Bug capture.** Screenshot on the phone, send it into the session, keep playing.

---

## Rules

**Don't approve what you can't read.** A phone screen is a bad diff viewer, and remote control gives you real approval power over real file writes. Use it for direction, verification, screenshots and small edits. Start anything that needs plan mode at the laptop.

**Never pair it with `bypassPermissions`.** The combination is a session that edits your filesystem on instructions from a device you might be holding one-handed on a walk. The whole security posture in PROJECT-PLAN §8 assumes you're reading the diffs.

**The laptop has to stay awake and online.** `caffeinate -is` prevents idle sleep for as long as the command runs — but closing the lid still sleeps the machine on battery. Lid open, or plugged in with an external display attached.

**Same account, and that's the boundary.** This reaches your machine and your repo. Sign out of the app on any device you don't control.

**Stop the session when the day ends.** It's an open door on your laptop; there's no reason to leave it open overnight.

---

## The other remote option, and when it's the right one

**Claude Code on the web** (claude.ai/code) runs a session in Anthropic's cloud against your GitHub repo. It works with the laptop closed and asleep. It cannot see your local dev server, your phone's LAN, `tuning.json` on your disk, or anything you haven't pushed.

So they're complements, not alternatives:

| | Remote Control | Claude Code on web |
|---|---|---|
| Laptop must be awake | Yes | No |
| Sees your running dev server | Yes | No |
| Can tune by feel with your thumb | Yes | No |
| Works from a train | Only if the laptop's awake at home | Yes |
| Good for | The tuning block, phone testing, the whole of day one | Phase 4 boss AI on a train; a level layout you can review as a diff |

For day one it's Remote Control, and it isn't close — every valuable thing about the phone loop depends on the dev server and the file on your disk.

---

## If it doesn't work

| Symptom | First thing to check |
|---|---|
| Session doesn't appear on the phone | Same account on both? The laptop CLI is signed in as whoever `claude auth` says, not necessarily who you last used in a browser |
| Appears, then goes stale | Laptop slept. `caffeinate -is`, lid open |
| Phone can reach Claude but not the game | That's two separate things — the game needs `npm run dev -- --host` and the same wifi. Remote control does not tunnel your dev server |
| Sliders don't move the game on the phone | Dev socket. Check you haven't applied the production CSP in dev (specs.md §2) |
| Both frames show different values | Late-join. That's what `tuning:hello` is for (specs.md §2) — if it's not implemented yet, reload the phone frame |

---

## Where this lands in the plan

- **DAY-ONE.md §1.7** — the 20-minute dry run, tonight
- **DAY-ONE.md 00:00** — start the day's session with the flag on, once
- **DAY-ONE.md 03:00** — the tuning loop, phone in hand
- **DAY-ONE.md 09:50** — mobile testing with the fix described in the moment
- **DAY-ONE.md 11:15** — stop the session
- **PROJECT-PLAN.md §12** — the risk this retires: *phone testing loop is slow enough that you skip it*
