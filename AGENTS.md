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

## Other house rules

- Record every player-visible change in `changes.txt` under the current
  version heading, in plain prose, as you make it.
- Do not commit runtime server state (`iwserver/admins.txt`,
  `iwserver/motd.svr`, `iwserver/accounts/`, logs) or build output other
  than the tracked client executable.
- Compile both `Infinite Warfare.nvgt` and `iwserver/iwserver.nvgt` with
  `C:/nvgt/nvgt.exe -c` and run the suites in `tools/tests/` before
  committing.
