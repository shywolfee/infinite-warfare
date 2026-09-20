# Infinite Warfare

Infinite Warfare is an open-source, audio-first online action game for Windows and Android. It combines detailed projectile combat, accessibility-focused interfaces, touch gestures, live communication, physical vehicles, and large explorable maps. A stripped-down, high-contrast visual layer supplements the audio experience for players with residual vision.

Current release: **0.5.1.2, build 85**

> Infinite Warfare is in active alpha development. Expect unfinished systems, balance changes, bugs, server downtime, and data resets before a final release.

## Development

Infinite Warfare is developed by **Equinox_Equine** using an agentic-development workflow.

Agentic intelligence used during development:

- **GPT-5.6 Sol**
- **Claude 4.8 Opus**
- **Claude 5 Opus**

The models assist with implementation, refactoring, testing, documentation, content integration, and technical analysis. Equinox_Equine directs the project and its development.

### Project lineage

This project was forked from a leaked copy of **Infinite Warfair 0.14**, originally produced by **Firegaming**, with **Max Vrenken** as developer and **Djonan Smid** as sound designer. That historical attribution describes the codebase from which this project was forked; it does not describe the current development team.

## Highlights

- Server-authoritative projectile combat with flight time, gravity, drag, penetration, dispersion, recoil, and weapon-specific ballistics.
- Facing-aware player models with separate head, neck, torso, pelvis, arm, and leg hit regions.
- Manual revolver, break-action, tube-fed, bolt-action, energy-weapon, heavy-weapon, melee, maintenance, and ammunition mechanics.
- Dynamic weapons, ammunition, attachments, armour, items, vehicles, help, and armoury databases.
- Categorized inventory, equipment slots, quickbars, equipment abilities, persistent credits, online shops, and team systems.
- Solid physical vehicles with fuel, damage, collision, roof riding, seat controls, service, repair, refitting, and customization.
- Four rebuilt maps: Shattersea, Coruscant, Ghost Town, and Freya's Ascent.
- Destructible world objects, ramps, elevation, acoustic occlusion, contextual fixtures, and detailed bunkers.
- Global language channels, map chat, team chat, private messages, group chat, movable buffers, message withdrawal, blocking, reports, and live voice chat.
- NV_form interfaces, keyboard practice, dynamic help, low-vision graphics, Android gestures, explore by touch, and built-in touch keyboards.
- Role-based administration, moderation, support, building tools, diagnostics, packet inspection, crash logs, and server maintenance.
- Optional ReactPhysics-enabled dedicated server alongside the regular server.

## Getting started

### Packaged client

1. Obtain the complete release package. The executable requires the matching sounds.dat and lib directory.
2. Run Infinite Warfare.exe.
3. Complete the first-boot accessibility and input wizard.
4. Create or select an account, configure the server address if needed, and connect.

The repository tracks the compiled client and source, but a working distribution must retain all packaged runtime libraries and the sound archive.

### Essential controls

| Action | Default |
| --- | --- |
| Move | Arrow keys |
| Sprint | Shift plus a movement key |
| Jump | Space |
| Fire | Control |
| Reload / unload | R / Shift+R |
| Ammunition report / fire mode | A / Shift+A |
| Select ammunition | Alt+R |
| Drawn weapon panel | Alt+A |
| Inventory | I |
| Quickbar and abilities | Shift+I |
| Game menu | Escape |
| Options | F11 |
| Help | Shift+H |
| Key practice | Shift+F1 |
| Full screen | Control+Shift+F12 |

Most actions are rebindable, and named keymap profiles are stored in the game's application-data directory.

For the complete controls, systems, accessibility, touch, staff, and troubleshooting guide, open [readme.html](readme.html).

## Chat and voice

| Destination | Default |
| --- | --- |
| Global/language chat | Slash |
| Current map or mode | Backslash |
| Team | Shift+Backslash |
| Group | Alt+Slash |
| Recent private messages | Alt+Backslash |
| Buffer manager | Alt+Shift+B |
| Voice transmission | Alt+O |
| Enter or leave a voice room | Shift+V |
| Voice settings | Shift+F7 |

The game includes forty language channels plus Unfiltered, server timestamps, group buffers, persistent blocking, message withdrawal with staff auditing, player reports, positional voice, and exclusive non-positional voice rooms.

## Building from source

The project targets **NVGT 0.90**.

Primary entry points:

- Infinite Warfare.nvgt — client
- iwserver/iwserver.nvgt — dedicated server
- pack_creator.nvgt — sound archive builder

Produced server binaries are intentionally distinguished:

- iwserver.exe — regular dedicated server
- iwserver_physics.exe — ReactPhysics-enabled dedicated server

When the client is running directly from source, authorized developer tools include a release builder that compiles the client, verifies or creates sounds.dat, stages the executable and dependencies, and creates the release archive.

## Repository guide

| Path | Purpose |
| --- | --- |
| includes/ | Client systems and shared interface code |
| iwserver/ | Authoritative server, content, maps, and documentation |
| iwserver/content/ | Dynamic weapons, maps, and other game content |
| iwserver/docs/ | In-game authored help topics |
| sounds/ | Source audio tree used by the sound pack builder |
| lib/ | Runtime libraries, helpers, and third-party notices |
| tools/ | Validation and regression utilities |
| changes.txt | Detailed chronological changelog |
| readme.html | Complete player and operator manual |
| version.txt | Version used by the GitHub updater |

## Bug reports and diagnostics

Use /bug in game to submit an issue and /bugs to review its status. Include the action being performed, map, approximate time, and reproduction steps.

Unhandled script exceptions create a shareable report in the local application-data iw/crash_logs directory. latest_client_session.log contains startup information for failures that occur outside normal script exception handling.

## Credits and acknowledgements

### Development

- **Equinox_Equine** — project direction and agentic development
- **GPT-5.6 Sol** — agentic development intelligence
- **Claude 4.8 Opus** — agentic development intelligence
- **Claude 5 Opus** — agentic development intelligence

### Original Infinite Warfair 0.14

- **Firegaming** — original project
- **Max Vrenken** — original developer
- **Djonan Smid** — original sound designer

Infinite Warfare was forked from a leaked copy of that 0.14 codebase. These are historical credits, not the current development team.

### Libraries and accessibility helpers

- **Blindpro** — NVGT Helpers
- **Ivan Soto** — NV_form
- **NVGT contributors and community** — engine, tooling, and technical support

### Sound-resource acknowledgements

Sound resources used in the project include material sourced from or designed for:

- **Executioner's Rage**
- **Firefight**
- **Call of Duty: Modern Warfare**
- **Insurgency: Sandstorm**
- **Fortnite**

All product names, game names, trademarks, and sound resources remain associated with their respective creators and rights holders. Inclusion in this acknowledgement does not imply endorsement of Infinite Warfare by those parties.

## Changelog

See [changes.txt](changes.txt) for the full release history and implementation notes.
