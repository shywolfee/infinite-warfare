# 0.5.1.1 migration ledger

This is a release gate checklist, not a claim that adding a wrapper migrates
the game. The current shipping version remains 0.5.1.0 until every gate passes.

- [ ] Verify and pin native runtime capabilities, callback safety and teardown.
- [ ] Shared ownership-safe worlds, IDs, shapes, joints and fixed stepping.
- [ ] Compile map geometry with ordered cuts, physical surfaces and metre scale.
- [ ] Structural assemblies, breakable supports and replicated debris.
- [ ] Authoritative characters, precise taps, posture, stairs and moving supports.
- [ ] Vehicles, interiors, seats, hinges, suspension and aircraft forces.
- [ ] Every projectile, melee, blast, weapon/attachment and physical item path.
- [ ] Corpses/ragdolls, loose props, equipment and persistent gameplay adapters.
- [ ] Sequenced inputs, prediction, reconciliation and versioned snapshots.
- [ ] Physics-backed interaction, camera, footsteps, audio and occlusion.
- [ ] Remove all competing legacy motion/collision authority.
- [ ] Regression, 32-player load, networking and multiplayer listening tests.
- [ ] Version 0.5.1.1/build 84, verified local Windows client/server packages.

Decisions: one coordinate is one metre; a brief unobstructed tap travels one
coordinate; terrain/bedrock remain fixed but buildings and bridges can collapse.
Android and GitHub publication are not part of this first release.

Runtime capability tests run in isolated processes and write a checkpoint before
each native call so an access violation can be located without a script exception.
No test connects to the live server or writes account/settings data.

## Verified development checkpoints

- Project-local NVGT source patch and build: 18 native checks pass, including
  contact snapshots, forces, four joint factories, callback errors and teardown.
- Shared owner: 17 checks pass for IDs, stepping/debt, lifetime, copied contacts
  and closest-body raycasts. No raw native handles are returned to consumers.
- Ordered static map compilation: four Python tests pass, with 9,370 parity
  points across the four authored maps. 24 native map-loading checks pass.
- Run `powershell -NoProfile -ExecutionPolicy Bypass -File
  tools/tests/run_reactphysics.ps1` from the project directory. This builds test
  map artifacts and requires fresh reports for all three native test suites.
- Run `python -m unittest discover -s tools/tests -p test_physics_map_compiler.py -v`
  for source geometry parity tests.

These checkpoints do not complete the larger checklist above. In particular,
the shared layer is not included by the shipping client/server yet, fluid
volumes do not simulate fluid, and static map bodies do not implement collapse.
Next: finish compound shapes/constraints, structural ownership and ramps,
then integrate authoritative actors and vehicles before changing the backend.

## Continued actor and structure work

- Compound box/sphere/upright-capsule bodies now own and dispose of all their
  parts. Contacts/raycasts carry part labels, and movement hulls can be excluded
  from anatomical hit queries. Generic native capsule destruction was repaired.
- Native actor adapter: 17 checks pass for anatomical hits, one-coordinate
  continuous movement, stopping, gravity-driven jumps, wall contact, mass and
  teardown, bounded-force weight penalties and a rider on a moving native
  platform. Stair traversal, postures, equipment-specific tuning, articulated
  poses/ragdolls and actual client/server input integration are not complete.
- Breakable native-joint adapter: 10 checks pass for gravity-supported decks,
  damage/overload failure, falling debris and connection cleanup. Actual map
  structural ownership and fracture replication remain to be implemented.
- Scheduler: 7 checks pass, including an isolated 32-actor/600-tick simulation
  with no event overflow. This is not the required networked multiplayer load
  test. Example run: 478 ms total, mean 0.797 ms, maximum 3 ms per tick.
- Matched Windows stubs built. Existing client/server compatibility compilation
  passes; actor regression also ran successfully as a compiled executable.
  The compiler supplies `IW_REACTPHYSICS_RUNTIME` for built-in HTTP compatibility.
- Dimensional audit finding: existing furniture/map geometry was authored with
  values such as an eight-coordinate bench and six-coordinate room heights.
  With metres selected, these must be deliberately resized/re-authored as part
  of the physical map migration; no silent feet/metres conversion has occurred.

The default game backend is still the existing implementation. The adapters
are not a completed gameplay port, and version.txt remains 0.5.1.0.

## Live server integration

The actual server now includes a guarded native adapter. Running
`tools/build_physics_server.ps1` emits the distinct `iwserver_physics.exe`,
which automatically loads its bundled fingerprinted maps; `iwserver.exe`
remains the regular server. The old `--native-models <compiled-map-directory>`
switch remains only as a developer override.
On-foot native actors drive the existing gameplay model position/velocity
fields; the old interpolation skips those actors. Spawn/lifecycle, armour mass,
map transfers, death, disconnection and peer-ID reuse are connected to real
server player objects. This mode is deliberately opt-in during migration.

Seventeen integration checks pass through an early self-test entry in the
actual server, before listening/account startup. The common runner now runs
110 native checks total plus map compilation. Both the installed-runtime server
and pinned-runtime server still compile, as does the installed-runtime client.

Compiled maps include source SHA-256 fingerprints. Startup validates all maps
before binding a listening socket; failures roll back native worlds. Runtime
map edits disable the preview and notify staff. `/physicsstatus` is available
to authenticated developers/admins in game or lobby. Quit/reboot paths explicitly
close the native ownership hierarchy.

See [NATIVE_SERVER_PREVIEW.md](NATIVE_SERVER_PREVIEW.md) for the one-command build, safeguards
and limitations. This is not yet a new client input protocol: vertical changes
and long moves are compatibility relocations, and vehicles/swimmers retain their
old controllers. Furniture, ramps, native hit queries for all combat, prediction,
reconciliation, snapshots and contact/fracture audio remain unfinished.
