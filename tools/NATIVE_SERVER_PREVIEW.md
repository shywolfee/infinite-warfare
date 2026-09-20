# Native server movement-model integration

This remains an incomplete 0.5.1.1 migration, but running the native server no
longer requires a special launch command. Use a separate testing server until
the remaining migration gates are complete.

## Prepare and test

Build the pinned project-local runtime described in `native/README.md`. From the
game directory run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/tests/run_reactphysics.ps1
```

This generates physical map JSON under `runtime_build/maps` and runs the isolated
adapter tests plus the **actual server's** integration self-test. The server
self-test branches before normal startup: it does not open a listening socket,
load player accounts or run the item economy. Reports go into fresh temporary
directories; incomplete reports and hung processes fail the runner.

## Build and run the native server

From the game directory, with the usual server instance stopped:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build_physics_server.ps1
& ./iwserver/iwserver_physics.exe
```

The build command regenerates `iwserver/physics_maps`, validates their source
fingerprints and compiles `iwserver_physics.exe` with the pinned runtime. Launching that
executable normally enables native physics before the listening socket opens.
The separate `iwserver.exe` remains the regular non-ReactPhysics server, so the
two modes are unambiguous and neither executable silently changes identity.
`--no-native-models` exists only as a diagnostic escape hatch; `--native-models`
can still override the map directory for development tests.

Developers/admins can use `/physicsstatus` from chat, including the lobby, to see
whether native models are active and how many maps/actors they own.

## What is connected

- Real server maps create native worlds after source-hash verification and
  before the server opens its listening socket.
- Real on-foot player objects create native actors. Accepted coordinate changes
  become navigation targets; native force/solver updates produce the existing
  `model_x/y/z` and `model_vx/vy/vz` fields used by gameplay/combat.
- The legacy interpolation function skips native-owned models. Simulation runs
  once per world service, not once per packet in a drained burst.
- Equipment armour mass updates actor mass. Death, departure, map transfer and
  reused peer IDs remove/replace the correct native body.
- Native worlds are explicitly cleaned up on the normal quit/reboot paths.
- A live map edit disables the preview and notifies staff. Recompile maps and
  restart to re-enable it; stale startup geometry is rejected and rolled back.

## Remaining limitations

The client still sends the existing destination-coordinate protocol. This is
not native input prediction/reconciliation or authoritative position replication.
Player integer navigation coordinates remain unchanged. Existing combat queries
use the new model positions but are not all replaced by native anatomical casts.
Furniture, dynamic structures, vehicles and terrain/ramp handling are not fully
connected. Do not use this preview to validate complete map traversability.

Vehicles/plane occupants and swimmers retain their existing movement models.
Vertical coordinate changes and long relocations re-create the native actor for
compatibility; they are **not** the final native jump/teleport protocol. Native
contact audio and structural fracture replication also remain unfinished.

No release version is raised by enabling the preview.
