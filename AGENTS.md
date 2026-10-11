# Notes for AI agents working on this repository

These rules apply to every automated agent (Claude, Codex, Copilot or anything
else) that edits, commits to or pushes to this repository.

## You may not touch the repository without explaining what you did

Any agent that changes this repository must describe every change in a
properly formatted, modern commit message. If you are not going to write
one, do not commit, push, amend, rebase, tag or otherwise alter the
repository's history. Leaving the working tree changed for the owner to
review is fine; recording changes nobody can understand is not.

A commit message must have:

1. **A summary line** in the imperative mood, no more than 72 characters,
   with no trailing full stop, using a Conventional Commits type and an
   optional scope:

   ```
   feat(awareness): turn nearby players into a motion tracker
   fix(nv_form): let Left and Right change tabs again
   ```

   Types: `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `build`,
   `chore`, `audio`, `maps`. Use `!` after the type for a change that breaks
   the client/server protocol or saved data (`feat(server)!: ...`).

2. **A blank line**, then **a body** wrapped at 72 columns that says what
   changed and why, in plain language a player or maintainer can follow.
   Group related changes under short headings or bullet points. Name any
   protocol, save-format or sound-pack changes explicitly, and say what the
   owner has to do (rebuild `sounds.dat`, update the server, and so on).

3. **Trailers** at the end where they apply, such as `Co-Authored-By:` for
   the agent and `BREAKING CHANGE:` for incompatible changes.

One commit per coherent change is preferred over one enormous commit; when a
single commit has to cover a large batch, its body must still list every
area it touches.

## Content imported from another game: read the source, never reconstruct it

The 0.6.0 Redspot import is the example to learn from, because it looked
finished and was not. Its weapons were right and almost everything else was
invented: 317 of the recordings under those weapons were another weapon's, so
80 Redspot guns holstered with a pistol's slide and dry-fired like one; 38 of
the source's items were never shipped at all; the item behaviour was rewritten
by hand with invented numbers (`random(300, 900)` where the source documents
300 to 2000) instead of ported; the deployed robot pointed its sounds at a
folder the game never reads, so it was silent; and `changes.txt` described the
whole thing as imported. Nobody could see any of that by playing it once, which
is exactly why it survived review.

These rules exist so it cannot happen again:

- **The source is the authority, verbatim.** Read its data files
  (`server/weapons.json`, `server/includes/items_db.nvgt`) and its code for the
  behaviour. Copy its numbers. Do not re-derive them, round them, rescale them
  for balance, or replace them with something that feels equivalent. If the
  source says 300 to 2000, the port says 300 to 2000.
- **Absence is data.** Port exactly the recordings the source names for an
  event, and where it names none, be silent. Never fill a gap with another
  weapon's, creature's or object's recording. A missing cue is not a hole to
  patch; it is the source telling you that event never happened. Substituting
  one is what made every imported weapon sound wrong.
- **Adapt placement, not content.** This engine names some things differently
  (a companion's recordings are `executioners_rage/<name>/<event>.wav`, not
  `<name>/<event>.ogg`). Re-encode or refile the source's recording; never
  invent a new one and never leave it where nothing will read it.
- **Record provenance for every asset you import** (see
  `sounds/REDSPOT_AUDIO_SOURCES.json`) and **write a mechanical audit** that
  compares what is shipped against the source it came from
  (`tools/audit_redspot_import.py`). "I checked it over" is not a check. If you
  cannot quote how many divergences remain, you do not know what you did.
- **Never widen a test or a contract to cover an invention.** This game's sound
  contract asks every weapon for a holster, an empty click and an unload; the
  import satisfied it by copying other weapons' recordings. The right answer was
  to fix the contract, as `tools/audit_sounds.py` now does: an imported profile
  is judged by the recordings the source actually has. When a check wants
  something the source does not have, the check is wrong.
- **Do not call it "imported" unless it was.** Say plainly what came from the
  source and what was written here; a changelog that overstates the port is how
  this went unnoticed for a release.
- **Surface collisions, never absorb them.** Two of the registry's entries
  (`machete`, `crossbow`) carry names this game already used. Silently keeping
  one side leaves the other entry missing with no record of the decision. List
  it, decide it, and write the decision down.
- **Ship complete slices, not shelves of stubs.** An item that can be bought
  while its behaviour is unported misleads players. Port a coherent group
  completely -- item, behaviour, recordings, shop entry, changelog -- and list
  what is still missing. The 38 unshipped Redspot items are still owed.

## Other house rules

- Record every player-visible change in `changes.txt` under the current
  version heading, in plain prose, as you make it.
- Do not commit runtime server state (`iwserver/admins.txt`,
  `iwserver/motd.svr`, `iwserver/accounts/`, logs) or build output other
  than the tracked client executable.
- Compile both `Infinite Warfare.nvgt` and `iwserver/iwserver.nvgt` with
  `C:/nvgt/nvgt.exe -c` and run the suites in `tools/tests/` before
  committing.
