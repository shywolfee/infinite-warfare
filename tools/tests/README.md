# Regression checks

For release 0.5.9.3, run `python tools/tests/release_0593_regression.py`.
It validates version/build metadata, all explicit supply offers, device
capabilities, module compatibility and the corrected item categories.
The client suite exercises source/blank lines, UTF-8 character review and
cross-line word review. The commerce suite exercises chip-stack deposits,
module installation, storage loss, cart validation and receipt replay.

Run `C:/nvgt/nvgt.exe companion_bowling_regression_runner.nvgt` from
`iwserver` for production companion movement and rolling-bomb physics.
It uses isolated flat, ramp and ledge maps and checks bounded pilot input,
unchanged body position, collision, range, momentum, landing and reversal.

`python tools/audit_sounds.py --duplicates` resolves runtime sound defaults,
world-effect variants, fixture cues and companion folders as well as weapon
lifecycles and maps. Exact duplicates are reported for review, not deleted:
legacy aliases and foley for physically equivalent objects are intentional.

`python tools/tests/content_audio_regression.py` decodes all repaired audio,
checks peak headroom, loop seams, quiet flight cues, distinct grenade
detonations, content bindings and source provenance. Reproduce personal-use
imports with `python tools/repair_content_audio.py` while the documented
external-drive libraries are available. Existing audio is preserved; targeted
`--refresh --only filename` accepts only unchanged files owned by its manifest.

After rebuilding `sounds.dat` with `C:/nvgt/nvgt.exe pack_creator.nvgt /s`,
run `C:/nvgt/nvgt.exe tools/tests/content_audio_pack_regression.nvgt` to check
every repaired recording inside the encrypted archive with NVGT's decoder.
Sound assets and the pack remain ignored local outputs, not Git source files;
deploy the rebuilt pack with the client and updated content/server files.

Run these from source using the same NVGT installation used to build the game:

```powershell
& C:/nvgt/nvgt.exe tools/tests/wallet_regression.nvgt
& C:/nvgt/nvgt.exe tools/tests/client_regression_runner.nvgt
& C:/nvgt/nvgt.exe tools/tests/acoustic_regression_runner.nvgt
& C:/nvgt/nvgt.exe tools/tests/dynamic_objects_regression.nvgt
python tools/tests/world_editor_regression.py
python tools/tests/weapon_data_regression.py
python tools/tests/mechanics_wiring_regression.py
python tools/tests/markdown_regression.py
python tools/tests/server_vehicles_regression.py
python tools/tests/updater_regression.py
python tools/tests/repo_status_regression.py
python tools/compile_check/compile_check.py --nvgt /path/to/nvgt
cd iwserver; & C:/nvgt/nvgt.exe world_editor_regression_runner.nvgt; cd ..
cd iwserver; & C:/nvgt/nvgt.exe commerce_regression_runner.nvgt; cd ..
python tools/build_maps.py
python tools/validate_maps.py
```

Reports and synthetic wallet records go in uniquely named `IW-*-regression-*`
directories under the current user's Local AppData Temp directory. No real
accounts, settings or game connections are used. The large inventory fixture
takes time to construct; the report distinguishes setup from browsing timings.

The commerce suite uses production banking, physical-payment, medicine,
dumpster, terminal and app-installation services with isolated financial
records. It checks exact change, replay rejection, fees, account debt,
repayment, failed bank writes, interrupted-transfer recovery, OS compatibility
and terminal-loss cleanup.

The 0.5.9.2 client checks exercise Markdown headings, links, lists and tables,
document-to-form navigation, disabled-control navigation, Markdown release
grouping, and spectator inventory restoration. Server checks cover distinct
simultaneous arena instances, travel, practice respawns, map cleanup, and
restoration of health, armour durability and suppressor state.

The updater suite uses the current Python interpreter, permits its isolated
PowerShell test process to execute scripts, and compares text independently
of Windows checkout line endings. Binary files still require exact matches.

The acoustic test loads Freya's Ascent geometry directly from the source tree
and compares narrowed wall traces with the pre-optimization reference. It also
checks conservative bounds after rotating and translating a dynamic object.
The client test compiles the actual game functions with a separate test entry
point; normal client builds do not include that entry point or test code.

The world-object test uses production parsing, damage, client geometry and
late-join handlers with isolated network/audio sinks. It checks the real maps'
component parity and verifies their sound names inside the existing sound pack.
The Python validator floods walkable foot positions in ordered map geometry,
including headroom and furniture, and checks all spawns, POIs, doors and services.

The world editor has two checks. The client test runs every builder with its
default settings on a blank map, with spawn points on every floor of the
building, at the top of the stairs and on the bridge, and writes it to
`IW-editor-test` in Local AppData Temp; `world_editor_regression.py` then runs
the server's own line validator over it (`map_line_check.nvgt`) and the raster
validator, so a builder that writes a line the server would refuse, or builds
a floor nobody can reach, fails. The server test
(`iwserver/world_editor_regression_runner.nvgt`, run from `iwserver`) drives the
real request handler: creating, travelling to and editing a map, undo and
redo, properties and lobby listing, content files and reloading, and refusing
requests without permission. It removes what it made and writes its report to
`iwserver/administration/world_editor_regression.txt`.

`weapon_data_regression.py` reads every weapon definition and checks that each
magazine, belt or launch tube is used by one calibre only, that each calibre
has one bullet diameter, and that rocket launchers fire rockets over a
sensible range. It needs no sound pack or NVGT installation.

`mechanics_wiring_regression.py` statically checks mechanics that once looked
correct but never ran: the collectable-item loop being serviced, corpses being
filled from the dying client, the ring equipment branch being reachable,
server-held WireNet charges, and anti-cheat removals disconnecting the peer.
Since 0.5.7 it also checks that alternate ammunition, weapon maintenance and
the physics server stay gone, that every weapon's `vehicle_use` is handled by
the server, that only a vehicle's driver can move it, that every vehicle file
describes its drivetrain, that arena maps are unlisted and have a spectator
gallery, and that every player removal also releases arena membership.

The server test also starts an arena with a single combatant and checks that
it runs as practice, that a practice death respawns the player, and that the
host leaving closes the arena.

`updater_regression.py` runs the GitHub updater (`updater/iw-update.ps1`)
against a local stand-in for GitHub that serves this working tree. It updates
a 0.5.4 source install and a release folder and checks that every file then
matches, that retired files are deleted, that the server's own files are left
alone, that a second update downloads only what changed (CRLF line endings
do not count), and that a failed download changes nothing. It needs PowerShell
(`pwsh`, or set `IW_PWSH`); without it only its static checks run. It also
checks that `updater/retired_files.txt` is current, which needs full history.

`repo_status_regression.py` runs the Repository status data layer
(`includes/repo_status.nvgt`) under NVGT against recorded GitHub replies in
`fixtures/github`, served locally, and checks every view: counts, links,
drill-downs, the commit comparison of a git checkout, the releases newer than
yours, time and Markdown handling, caching, and the rate-limit message. It
also signs in against the stand-in (a token, and GitHub's device flow),
checks the token is stored encrypted and only sent to GitHub's API, and runs
every account action: star, watch, fork, new issue, comment, close, reopen,
merge and marking notifications read. Set
`NVGT` to the executable; it skips without one.

`iwserver/grenade_regression_runner.nvgt` runs the production grenade code
from the server directory without a live network connection. It checks
pinning and throwing during the old cooldown, variable fuse preservation,
duplicate requests, late throws, damage from in-hand expiry, moving holders,
map changes, connection reuse, and invalid or spectator pin requests.
The client suite also checks grenade acknowledgements and pending state.
The live-fuse workflow adds `grenade_pin`, `grenade_release`,
`grenade_armed` and `grenade_finished` packets. Deploy the rebuilt client
and server together; it does not change item definitions or saved data.

`tools/compile_check/compile_check.py` compiles the client and the server on
Linux with the NVGT 0.90.0-dev build from nvgt.dev, in a temporary copy with
stubs for the APIs and Windows plugins that build lacks
(`nvgt_dev_stubs.nvgt`). It catches missing functions and type errors without
Windows. With an NVGT matching the one the game is built with, add
`--no-stubs`.
