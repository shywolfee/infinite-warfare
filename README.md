# Infinite Warfare

Infinite Warfare is an audio-first online action game for Windows and Android.
It combines detailed server-authoritative combat, large three-dimensional maps,
touch access, live communications, accessible interfaces, and an optional
top-down visual presentation.

Current source release: **0.5.2, build 86**

> Infinite Warfare is an active alpha. Expect unfinished systems, balance
> changes, server maintenance, bugs, and possible data resets.

## What the game includes

### Combat and simulation

- Projectiles with flight time, gravity, drag, dispersion, penetration,
  retained energy, flybys, and ammunition-specific behavior.
- Facing-aware player models with distinct head, neck, torso, pelvis, arm,
  and leg hit regions.
- Firearms, energy weapons, bows, launchers, explosives, melee weapons, and
  heavy weapons with class-specific operation rather than one shared firing
  model.
- Manual actions, individual-round loading, ammunition selection, magazines,
  attachments, heat, fouling, maintenance, failures, recoil, and wall bracing
  where the weapon supports them.
- Armour by body location, durability, equipment weight, medication doses,
  toxicity, persistent credits, quickbars, and equipment abilities.

### World

- Four authored maps: Ghost Town, Shattersea, Freya's Ascent, and Coruscant.
- Elevation, ramps, roofs, water, destructible objects, fixtures, services,
  acoustic occlusion, points of interest, and multiple safe spawn locations.
- Physical vehicles with solid footprints, collision and player impact, roof
  riding, seats, doors, windows, fuel, damage, repairs, refitting, and
  customization.
- A live, permission-controlled world editor for building and changing maps
  without restarting the server. Maps can also be added as data files and are
  discovered dynamically.

### Interface and accessibility

- NV_form audio interfaces, categorized menus, dynamic database help, key
  practice, configurable keymap profiles, and optional interface sounds.
- Android gesture navigation, rebindable gestures, contextual gesture help,
  gesture practice, explore by touch, and QWERTY or analogue touch keyboards.
- An optional modern top-down visual interface with rendered terrain and
  objects, player and projectile markers, HUD, POI minimap, graphical forms,
  and a visual keyboard.
- Visual subtitles are independent from the graphical interface and occupy a
  reserved caption area rather than replacing the game screen.
- Full-screen presentation, scalable high-contrast layouts, mouse controls,
  desktop notifications, screenshots, and Windows voice commands.

### Online systems

- Global language channels, map chat, teams, private messages, persistent
  groups, movable message buffers, timestamps, withdrawal, blocking, reports,
  and support tickets.
- Positional voice chat plus exclusive team, map, channel, group, and private
  voice rooms.
- Persistent accounts, team roles and points, shops, credits, moderation,
  staff roles, administration logs, packet diagnostics, and live server
  maintenance tools.
- Data-driven weapons, ammunition, items, vehicles, maps, help, developer
  grants, and Armoury entries shared with the authoritative server.

## Getting started

### Packaged client

Keep the complete release together. The client executable needs the matching
`sounds.dat`, `lib`, and data directories.

1. Run `Infinite Warfare.exe`.
2. Complete the first-boot accessibility and input setup.
3. Create or select an account.
4. Select a server if necessary, then connect.

The in-game updater compares the local `version.txt` with the main branch on
GitHub, downloads the repository archive, replaces the installation after the
client exits, and restarts it. It does not require Git to be installed.

### Essential default controls

| Action | Default |
| --- | --- |
| Move / sprint | Arrow keys / Shift+arrow |
| Jump | Space |
| Fire | Left Control |
| Reload / unload | R / Shift+R |
| Ammunition report / fire mode | A / Shift+A |
| Select ammunition | Alt+R |
| Drawn weapon panel | Alt+A |
| Inventory / quickbar | I / Shift+I |
| Global / map / team chat | Slash / Backslash / Shift+Backslash |
| Groups / recent private contacts | Alt+Slash / Alt+Backslash |
| Voice transmission / room | Alt+O / Shift+V |
| Game menu / Options | Escape / F11 |
| Help / key practice | Shift+H / Shift+F1 |
| Full screen / screenshot | Control+Shift+F12 / Print Screen |

Most gameplay actions are rebindable. Named keymaps and `keyconfig.json` are
stored under the game's local application-data directory, not beside the
executable. The complete player and operator manual is
[readme.html](readme.html), and the in-game help is generated from the same
content databases used by gameplay.

## Running from source

The project targets **NVGT 0.90**. Clone the repository and run the client
entry point with NVGT:

```powershell
git clone https://github.com/shywolfee/infinite-warfare.git
cd infinite-warfare
& C:/nvgt/nvgt.exe "Infinite Warfare.nvgt"
```

Compile release-mode client and server binaries with:

```powershell
& C:/nvgt/nvgt.exe -c "Infinite Warfare.nvgt"
& C:/nvgt/nvgt.exe -c "iwserver/iwserver.nvgt"
```

The normal server builds as `iwserver/iwserver.exe`. The repository also
contains `iwserver/iwserver_physics.exe`, the ReactPhysics-enabled server
variant. Keep their matching runtime libraries with the executable being run.

To rebuild the sound archive after changing source audio:

```powershell
& C:/nvgt/nvgt.exe "pack_creator.nvgt"
```

When run from source, the developer-only release builder can compile the
client, build or verify `sounds.dat`, stage the required files, and create a
release zip. Server authorization is still required for developer and builder
features.

## Tests

Use the same NVGT installation that builds the game:

```powershell
& C:/nvgt/nvgt.exe tools/tests/wallet_regression.nvgt
& C:/nvgt/nvgt.exe tools/tests/client_regression_runner.nvgt
& C:/nvgt/nvgt.exe tools/tests/acoustic_regression_runner.nvgt
& C:/nvgt/nvgt.exe tools/tests/world_objects_regression.nvgt
python tools/tests/world_editor_regression.py
Push-Location iwserver
& C:/nvgt/nvgt.exe world_editor_regression_runner.nvgt
Pop-Location
python tools/build_maps.py
python tools/validate_maps.py
```

The regression programs use isolated temporary data. See
[tools/tests/README.md](tools/tests/README.md) for what each suite covers and
where its report is written.

## Repository layout

| Path | Purpose |
| --- | --- |
| `Infinite Warfare.nvgt` | Client entry point and core game loop |
| `includes/` | Client gameplay, interface, accessibility, and networking systems |
| `iwserver/iwserver.nvgt` | Authoritative server entry point |
| `iwserver/content/` | Data-driven maps, weapons, items, editor palettes, and fixtures |
| `iwserver/docs/` | Authored in-game help that is not generated from a database |
| `sounds/` | Source audio tree used to create `sounds.dat` |
| `lib/` | Runtime libraries, plugins, helpers, and notices |
| `tools/` | Import, validation, build, and regression utilities |
| `changes.txt` | Detailed player-facing release history |
| `readme.html` | Complete game manual |
| `version.txt` | Version checked by the GitHub updater |

Runtime accounts, server logs, administrator files, MOTD changes, and other
live server state do not belong in source-control commits. See
[AGENTS.md](AGENTS.md) for build, test, changelog, and commit-message rules.

## Diagnostics and support

- Use `/bug` in game to file a bug report and `/bugs` to review reports.
- Include the action, map, approximate time, expected result, and what
  actually happened.
- Unhandled client script errors create shareable reports under
  `iw/crash_logs` in local application data.
- `latest_client_session.log` records startup context for native or operating
  system failures that bypass script exception handling.
- Source builds include packet inspection, live server diagnostics, and the
  permission-controlled administration and world-editor panels.

## Development and lineage

Infinite Warfare is currently directed and developed agentically by
**Equinox_Equine**, using **GPT-5.6 Sol**, **Claude 4.8 Opus**, and
**Claude 5 Opus** for implementation, refactoring, testing, documentation,
content integration, and technical analysis.

This project was forked from a leaked copy of **Infinite Warfair 0.14**, made
by **Firegaming**, with **Max Vrenken** as developer and **Djonan Smid** as
sound designer. Those names describe the historical codebase and are not the
current development team. The game also incorporates source originating in
*Redspot: Blood and Peril* by **Sam Tupy**, credited for his original work and
ideas.

### Libraries and accessibility work

- **Blindpro** — NVGT Helpers
- **Ivan Soto** — NV_form
- **NVGT contributors and community** — engine, tools, and support

### Sound-resource acknowledgements

Sound resources used by gameplay include material associated with:

- Executioner's Rage
- Firefight
- Call of Duty: Modern Warfare
- Insurgency: Sandstorm
- Fortnite

Product names, game names, trademarks, and sound resources remain associated
with their respective creators and rights holders. Acknowledgement does not
imply their endorsement of Infinite Warfare.

## Changes

See [changes.txt](changes.txt) for the complete release history.
