# Infinite Warfare

Infinite Warfare is an audio-first multiplayer action game. Explore three-dimensional
maps, fight with firearms and specialist weapons, drive vehicles, and coordinate with
other players through text and positional voice chat. Spoken menus and spatial sound
support play without graphics; an optional top-down view adds a HUD, minimap, subtitles,
and visual controls.

**Current version: 0.5.10, build 104.** The game is in active alpha. Features and
balance are still changing, and updates may require replacing saved data.

[Player manual](player_manual.md) | [Release notes](changes.txt) | [Report an
issue](https://github.com/shywolfee/infinite-warfare/issues)

## Start playing

Use a complete client package with its matching `sounds.dat`, runtime libraries, and
data files. A Git checkout alone does not include the sound archive or source
recordings.

1. Extract the complete package into one folder and launch `Infinite Warfare.exe` on
  Windows.
2. Follow the first-run accessibility and input setup.
3. Create or select an account, check the server address, and connect.
4. Open Help with **Shift+H** or try key practice with **Shift+F1**.

The client also includes Android touch controls, gesture practice, and an on-screen
keyboard. The Windows executable does not run on Android; Android needs a
platform-specific build.

### Default keyboard controls

| Action | Keys |
| --- | --- |
| Move / sprint | Arrow keys / Shift+arrow |
| Jump | Space |
| Fire | Left Control |
| Reload / unload | R / Shift+R |
| Check ammunition / change fire mode | A / Shift+A |
| Open the weapon panel | Alt+A |
| Open inventory / quickbar | I / Shift+I |
| Open the game menu / options | Escape / F11 |
| Open help / key practice | Shift+H / Shift+F1 |

Most gameplay controls can be rebound. The [player manual](player_manual.md) covers
aiming, manual weapon actions, chat, voice, vehicles, equipment, and touch gestures.
In-game help includes information generated from the current weapon and item
definitions.

## What you can do

- **Fight with distinct weapon types.** Firearms, shotguns, bows, blasters, launchers,
  melee weapons, and explosives have different handling. Combat includes projectile
  travel, gravity, cover, armour, recoil, and manual loading where appropriate.
- **Explore maps with height and cover.** Ghost Town, Shattersea, Freya's Ascent, and
  Coruscant include ramps, buildings, water, points of interest, and destructible
  objects. Sound cues help locate players and navigate the world.
- **Use vehicles and equipment.** Vehicles have seats, doors, fuel, damage, and repairs.
  Armour, medical supplies, field devices, and deployable companions provide additional
  ways to play.
- **Play and communicate together.** Teams, persistent groups, private messages,
  language channels, positional voice, and separate voice rooms support coordination.
- **Choose your interface.** Use spoken forms and keyboard or touch input, or enable the
  optional visual presentation. Subtitles and interface sounds have separate settings.

Version 0.5.10 adds 197 weapons drawn from classic tactical, galactic, and mercenary
arsenals, plus seven explosive items. The ammunition correction gives compatible weapons
shared reserves and removes the `ars_` prefix from their inventory IDs. See the [release
notes](changes.txt) for the full changes and save-compatibility requirements.

## Updates

The main menu's **Check for updates** reads the published version from this repository's
`main` branch. On Windows, the updater downloads changed repository files, verifies
them, removes retired files, and restarts the client. It restores touched files if the
update fails. Git is not required for this process.

Audio is distributed separately from Git: a repository update cannot supply an ignored
`sounds.dat`. Keep the client, server content, and sound pack matched to the release.
The ammo and ID correction does not need another sound-pack rebuild, but existing saves
need their old weapon and reserve IDs replaced.

**Repository status** in the main menu lets you browse commits, issues, and other GitHub
activity. The [release notes](changes.txt) describe player-visible changes in version
order.

## Build and run from source

Development uses [NVGT](https://nvgt.dev/) and the project's Windows plugins and runtime
libraries. The source targets the NVGT 0.90 API family; use the same engine installation
for builds and regression tests. Python is needed for the validation and content tools,
and FFmpeg for audio import and decoding tests.

Clone the repository:

```powershell
git clone https://github.com/shywolfee/infinite-warfare.git
cd infinite-warfare
```

Compile the client and server, adjusting the NVGT path if necessary:

```powershell
& C:/nvgt/nvgt.exe -c "Infinite Warfare.nvgt"
& C:/nvgt/nvgt.exe -c "iwserver/iwserver.nvgt"
```

This produces `Infinite Warfare.exe` and `iwserver/iwserver.exe`. To run the client
directly from source, omit `-c`. The client still needs the matching sound archive and
runtime libraries.

Run the server from its own directory so it can find its content and local state:

```powershell
Push-Location iwserver
try {
    & C:/nvgt/nvgt.exe iwserver.nvgt
} finally {
    Pop-Location
}
```

For staff tools and server administration, see the [player and operator
manual](player_manual.md#12-staff-and-server-operation). Keep accounts, administrator
files, MOTD changes, and logs local.

### Sound assets

Source recordings and `sounds.dat` are ignored by Git. Obtain the required audio
separately before trying to play or run the audio suites. Import tools under `tools/`
describe their source libraries and keep provenance records; some require recordings
from local external libraries.

With a populated `sounds/` directory, build the archive using:

```powershell
& C:/nvgt/nvgt.exe pack_creator.nvgt /s
```

Deploy the resulting archive alongside the matching client. Credits acknowledge the
source creators; they do not grant permission to redistribute their recordings.

## Validate changes

Follow [AGENTS.md](AGENTS.md) for changelog, build, test, and commit requirements.
Before committing, compile both entry points and run the regression suites described in
[tools/tests/README.md](tools/tests/README.md). That guide identifies the required
runners, dependencies, and report locations.

Useful content checks include:

```powershell
python tools/tests/weapon_data_regression.py
python tools/tests/expanded_arsenal_regression.py
python tools/tests/release_0593_regression.py
```

The expanded-arsenal check needs the local recordings, import receipts, source
libraries, and FFmpeg. These three checks supplement the full suite.

After moving or deleting shipped files, update the removal manifest:

```powershell
python tools/update_retired_files.py
```

Record player-visible changes in `changes.txt`. Keep each release or coherent fix in a
separate commit with a Conventional Commits summary and a body explaining what changed,
why, validation, and any deployment or save-data requirements. Do not commit server
state, logs, or generated builds other than the tracked client executable.

## Find your way around the source

| Path | Contents |
| --- | --- |
| `Infinite Warfare.nvgt`, `includes/` | Client entry point, gameplay, interfaces, and accessibility |
| `iwserver/iwserver.nvgt`, `iwserver/includes/` | Server simulation, networking, and services |
| `iwserver/content/` | Weapon, item, vehicle, map, and other content definitions |
| `iwserver/docs/` | Authored in-game help |
| `tools/` | Content imports, builds, validators, and regression suites |
| `lib/` | Runtime libraries, helpers, plugins, and notices |
| `updater/` | Windows updater and retired-file manifest |
| `player_manual.md` | Player and operator manual |
| `changes.txt`, `version.txt` | Release history and published version |

## Report a problem

Use `/bug` in game or [open a GitHub
issue](https://github.com/shywolfee/infinite-warfare/issues). Include your version, the
map or menu involved, steps to reproduce the problem, and what you expected to happen.
Attach a relevant error report when available.

Client script errors are recorded under `iw/crash_logs` in local application data.
`latest_client_session.log` records startup context, and `updater/last_update.log`
records update attempts.

## Credits and project history

Current development is directed by **Equinox_Equine**, with AI coding tools used for
implementation, testing, and documentation.

This project descends from a leaked copy of **Infinite Warfair 0.14** by **Firegaming**,
with **Max Vrenken** credited for development and **Djonan Smid** for sound design. It
also contains source originating in **Redspot: Blood and Peril** by **Sam Tupy**. These
credits describe the project's origins, not its current development team.

Additional thanks to **Blindpro** for NVGT Helpers, **Ivan Soto** for NV_form, and the
**NVGT contributors and community** for the engine and supporting tools.

Audio sources include material associated with Executioner's Rage, Firefight, Call of
Duty, Insurgency: Sandstorm, Fortnite, Counter-Strike, Star Wars Battlefront II, Team
Fortress 2, and Battlefield. Names and recordings belong to their respective creators
and rights holders; their inclusion does not imply endorsement.
