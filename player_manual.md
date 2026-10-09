# Infinite Warfare

Version 0.5.9.3 · Build 103

An open-source, audio-first online action game for Windows and Android, with an optional modern top-down visual interface, HUD, minimap, forms, subtitles and keyboard.

This manual describes the current game rather than retired prototypes. Exact weapon, ammunition, attachment, armour, item, and vehicle statistics come from the live database and are available through Dynamic Help and the Dynamic Armoury.

## 1. Quick start

1. Run `Infinite Warfare.exe`. The first-boot wizard configures essential interface, audio, platform, keyboard, mouse, and touch choices.

1. Create or select an account, configure the server address if necessary, and connect.

1. Use the lobby to chat, browse players, inspect the armoury, read help, manage your account, or deploy into a map.

1. Move with the arrow keys, fire with `Ctrl`, reload with `R`, and open inventory with `I`. Press `Alt+F` to switch Dashboard and Inventory mode. In Dashboard mode, `Tab` opens game options and `Alt+G` returns to game control. `Escape` goes back inside menus or opens the leave/resume choices during gameplay. `F11` opens Options without leaving the match.

Deployment provides a random melee weapon, sidearm, primary weapon, sensible ammunition, healing supplies and explosives. Automatic quickbar assignment is optional.

Unsure what a key does? Press `Shift+F1` for key practice. Press `Shift+H` for the in-game help browser.

## 2. Menus and accessibility

Interfaces use NV_form. `Tab` and `Shift+Tab` move between controls; arrow keys operate the focused list, field or setting. `Enter` activates and `Escape` goes back. Categorized forms use left and right on the category strip. `Ctrl+Tab` moves to the next category and its first option; `Ctrl+Shift+Tab` moves to the previous one. Named form groups support `Alt+Arrow` navigation where present.

Audio-form navigation and activation sounds are optional; dashboard sounds can be disabled independently. Forms continue pumping network and game state while open. Help, release notes, announcements and this manual use Markdown documents. `Up` and `Down` read lines, `H` jumps to headings, `K` jumps to links and `F7` opens the heading/link elements list. `Shift` reverses quick navigation. `Ctrl+Alt+Arrow` reads table cells. `Enter` follows a focused web link and `Tab` leaves the document without losing its reading position.

### Dashboard touch gestures

- Top band, three-finger hold opens the dashboard.
- Top band, three-finger triple-tap and hold switches Dashboard and Inventory mode.
- Bottom band, two-finger swipe down returns to the game keyboard area.
- Two-finger swipe right or left moves between form controls.

The gesture manager can rebind these actions. Form gestures navigate the focused screen; gameplay gestures resume in the game keyboard area.

### Visual interface, subtitles and keyboard

The optional modern visual interface renders gameplay from above. Authored terrain, walls, ladders, dynamic objects, vehicles, nearby players and projectiles share the world view; the HUD shows weapon, ammunition, fire mode, stamina and position; and the minimap places points of interest and the active waypoint within the real map bounds. Menus and forms use category tabs, control cards, visible focus and value states, and a contextual detail panel.

Visual subtitles are a separate option. They put spoken game messages in a compact box above the HUD rather than replacing or covering the game view. The optional visual keyboard displays a full QWERTY layout, typed text, the focused key, Shift and Caps Lock state. On Android it follows the functional explore-by-touch or analogue keyboard live. All three settings can be changed independently under **Options, Accessibility**.

`Ctrl+Shift+F12` toggles full screen. `Print Screen` saves a PNG in the `screenshots` folder beside the running client without blocking gameplay.

### Input-box speech

While typing, `F1` toggles speaking typed characters, `F2` toggles speaking completed words, and `F3` toggles the caps-lock beep.

## 3. Default controls

Configurable actions can be changed under **Options, Keyboard, Key binding editor**. Named keymaps live in the game application-data folder. Duplicate names, identical profiles, and unchanged profiles are rejected.

| Area | Defaults |
| --- | --- |
| Movement | `Arrow keys` move; hold `Shift` to sprint; `Space` jumps; `Alt+Z` sits or stands; `Page Up`/`Page Down` move vertically where supported. |
| Turning and aim | `Q`/`E` turn; add Shift for fine turning. `S`/`X` aim vertically. `Alt+[`/`Alt+]` select a target region; `Alt+T` returns to the whole body. |
| Combat | `Ctrl` fires; `R` reloads; `Shift+R` unloads; `A` reports ammunition/action state; `Shift+A` changes fire mode; `Alt+A` opens the drawn weapon panel. |
| Weapon mechanics | `Alt+N` operates a class-specific control; `Alt+Shift+A` inspects handling. `Alt+Y` opens/closes a manual action; `Alt+I` inserts a round; `Alt+Shift+Y` cycles a pump; `Alt+Shift+G` ejects while open. |
| Inventory | `I` opens inventory; `Tab`/`Shift+Tab` cycle items; `K`/`Shift+K` cycle nonempty categories. `Shift+Enter` uses an item and `Alt+Enter` opens database help. |
| Item mechanics | `Alt+Shift+K` reports mechanics and recommendations; `Alt+Shift+L` removes one transferable pill. |
| Status | `H` health; `V` stamina/effects; `Alt+B` buffs/debuffs; `F` facing; `C` coordinates; `B` zone; `M` nearby content; `P` nearby players; `J` points of interest. |
| Server information | `F1` players; `F2` message of the day; `F3` ping statistics; `F4` uptime and traffic. |
| Menus | `Escape` game menu; `F11` Options; `Shift+H` Help; `Alt+E` Equipment; `Alt+S` Support; `Shift+I` quickbar and abilities. |
| Staff | `Ctrl+Shift+F8` opens the Administrator Panel when authorized. `Shift+D` opens source/developer tools where permitted. |

Key practice recognizes the exact modifier chord and describes configurable bindings and contextual controls without confusing a plain key with its Shift, Alt, or Control variant.

## 4. Combat and weapons

Combat is server-authoritative and projectile based. Firearms use weapon-specific velocity, flight time, drag, gravity, dispersion, recoil, penetration, range, and damage. Projectiles follow slopes and ramps in three dimensions. Shotguns emit individual pellets; explosives and thrown items have their own physics; bows, crossbows, mortars, energy weapons, fuel weapons, powered tools, and melee classes have distinct mechanics and audio.

Players have continuous, facing-aware models containing separate skull, neck, torso, pelvis, arm, and leg volumes. Projectiles strike the actual volume they intersect, and only armour covering that region can mitigate the hit. One-shot damage is prevented. A silent five-second spawn grace period ends early when the protected player initiates a damaging action.

### Handling and ammunition

- A weapon exposes only states that apply to it. Conventional firearms do not pretend to use energy cells.

- Fire modes, attachments, bracing, recoil, safeties, stocks, bipods, bolt cycling, and charge strength apply to the relevant weapons. Each weapon takes one ammunition, its own calibre.

- Revolvers and individually fed shotguns require their proper sequence. Break actions chamber on close, tube-fed pumps must be cycled, and detachable-magazine shotguns reload normally.

- Shells, cartridges, bolts, cells, magazines, belts, and other feed devices are real inventory objects. Extended magazines change real capacity.

The weapon panel is live: damage, range, capacity, projectile count, velocity, spread, recoil, fire mode, attachments, and applicable handling states update with the current configuration.

### Movement and stamina

Movement uses momentum and simulated gravity while retaining predictable one-coordinate navigation. Sprinting has consistent speed and does not consume stamina, although extremely heavy weapons can prevent it. Stamina is reserved for melee attacks. Sitting slows movement, accelerates recovery, limits heavy weapons, and restricts jumping.

## 5. Inventory, equipment, and items

The inventory is a live categorized form. Up/Down browse, Page Up/Page Down move ten entries, Home/End jump to boundaries, and typing several letters performs prefix navigation. Left/Right or Tab/Shift+Tab move among categories that contain items. The Applications key opens a contextual action panel.

`Alt+Up`/`Alt+Down` reorder one position, `Alt+Home` moves first, `Alt+End` moves last, `Space` gives one item to a selected player within ten tiles, and `Backspace` drops one seven tiles ahead. Grenades retain their Enter-to-pull-pin and Enter-again-to-throw cooking workflow.

Categories include weapons, ammo, explosives, healing, armour, armour repair, vehicle supplies, attachments, holsters, team items, tools, electronics, containers, and equipment. Partial magazines, cells, boxes, linked belts, belt boxes, bandoliers, quivers, shell cases, and crates preserve their remaining load.

### Equipment and quickbar

Equipment has dedicated armour and utility locations. One compatible piece occupies each slot. Armour protects its actual body region, loses durability, contributes weight, and can be patched only within its material and repair limits.

`Shift+I` opens the quickbar and equipment-ability manager. It reports each ability's source, description, cooldown, and remaining time; can clear assignments for the current session; and can automatically bind a practical loadout while explaining every choice.

### Consumables and fixtures

Liquid medicines show ounces remaining; pill bottles show pills remaining. Doses, duration, toxicity, interactions, and overdose are simulated. Retired energy potions and energy drinks are removed from saved inventories rather than lingering as unusable items.

ATMs, vending machines, refrigerators, medical beds, salvage sources, sinks, streams, and workshops are map fixtures, not deployable inventory kits. They have server-owned stock, proximity checks, bounded output, and appropriate map locations.

## 6. Vehicles

Vehicles are solid moving world objects with type-specific dimensions, health, armour, wheels, roof surfaces, acceleration, braking, speed, fuel, passenger capacity, and collision behavior. Players may walk around them, jump onto their roofs, be carried at safe speed, be thrown off by hard acceleration or aircraft launch, and be injured by an impact.

**Vehicles do not have walkable simulated interiors.** Opening a door permits entry with the vehicle command; it does not replace map tiles with a cabin or let a player walk through the body. This deliberately replaces the older, unreliable interior experiment.

| Control | Action |
| --- | --- |
| `O` | Open or close a door while within five tiles. |
| `V` | Enter the nearest open vehicle and take an available seat, or exit. |
| `U` | Open or close the current seat window. |
| `Up/Down` | Hold to accelerate or brake; release both to coast. In an automatic, hold Down at a standstill to reverse. |
| `Shift+Up/Shift+Down` | Change gear in a vehicle with a manual gearbox. |
| `Left/Right` | Steer while moving; steering is sharper at low speed. Tracked vehicles can pivot at a standstill. |
| `Ctrl` | Fire the mounted weapon of your seat, if it has one. |
| `Alt+Left/Right` | Change seats. Only the driver controls movement. |
| `Alt+Shift+V` | Open the nearby workshop for inspection, fuel, service, repair, refit, and customization. |

Windows must be open to fire from a seat, and melee attacks cannot be used from a vehicle. Heavy weapons cannot be fired from inside at all; rocket backblast, flamethrowers and mortars inside a cabin go as badly as you would expect. Firing from a moving vehicle spoils your aim, and firing while driving spoils your driving. A grenade thrown with the window open goes out of the window carrying the vehicle's speed; with it closed it goes off inside, after a three-second confirmation. Fuel type and quantity matter. Fuel can be consumed, transferred, siphoned, contaminated, or misfuelled; service and refits affect live performance. Vehicles take projectile and collision damage, including damage caused by their owner.

## 7. Maps and world systems

Every place on every map has a name: streets are named by the stretch you are on and which pavement, rooms by what they are and which end of them, open ground by its bearing. The coordinates key tells you your position, the surface under your feet, and how far it is down to the next thing below; `B` names the zone you are in, and works while sprinting. Stairs and ramps are walked; ladders and rungs are climbed with the up and down keys; lifts are ridden from their panel. Every map carries its own ambience, which you can hear change as you move from street to room to river.

| Map | Bounds | Character |
| --- | --- | --- |
| Ghost Town | 480 by 480 | An abandoned modern city: six avenues and six streets, every stretch and kerb named, a service alley through every block, the River Alder, the Fourth Street viaduct, and districts from the harbour to the terraces. |
| Shattersea | 560 by 560 | Nine islands joined by twelve bridges in a sea six below every quay: a fishing harbour, a lighthouse, salt pans, a cargo wharf, a guildhall, a glassworks, a cliff with a funicular, cisterns and an aqueduct, and a drowned old city. |
| Freya's Ascent | 300 by 300, 156 high | A city on six terraces up a mountain, joined by switchback stairs, a goods lift, tunnels and maintenance rungs, with a waterfall down the eastern face and the Folkvangr Spindle ring in orbit above. |
| Coruscant | 400 by 400, 200 high | Six stacked levels of the Galactic City, from Level 1313 through the Works, CoCo Town and the Uscru District to the Senate District and the Jedi Temple, joined by turbolifts and vent shafts. |

### Finding people and places

Everything that tells you where something is uses the same words: the straight-line distance in tiles, a clock-face bearing where twelve o'clock is the way you are facing, and how far above or below you it is. `M` lists items and chests within thirty tiles, nearest first.

`P` works like a motion tracker. Anyone within eight tiles shows up whatever they are doing. Further out, a player shows up only while they give themselves away: moving in the last second and a half, out to thirty tiles, or firing in the last three seconds, out to sixty -- or thirty with a suppressor. Someone standing still and holding their fire beyond eight tiles does not show at all, and neither will you. Teammates always show, out to sixty tiles. Each contact says whether it is moving, firing or still.

`J` lists the map's points of interest, nearest first. Press `Enter` on one and a beacon sounds from that place, more often as you get closer, until you arrive. Open the list again to stop or to pick somewhere else.

`T` chooses a player to track. While you track someone a beep sounds from where they are every couple of seconds: a high tone when they are above you, a low one below, and a plain one on your level. `W` tells you exactly where they are. A teammate can be tracked anywhere. Anyone else gives off a beacon only while `P` would show them -- close by, moving or firing -- and goes quiet when they keep still out of range. Invisible players cannot be tracked, and you are told when your target goes down, changes map or leaves.

### Acoustics, terrain, and destruction

Environmental reverb has been removed. Occlusion remains: positional sound traces walls and authored portals, applies bounded attenuation and low-pass filtering, and can be disabled independently in Audio Options. Interface and notification sounds are not positional world sounds.

Ramps and stairs create continuous three-dimensional terrain for movement and projectiles. Destructible furniture has material resistance, shape, floor surface, and health shared by client and server. Destroyed furniture stays removed until map reload or server restart and never creates unlimited loot.

Bunkers use authored entrances, staged construction, capacity, structural condition, power, filtration, supply, access, and tactical interaction rather than acting as generic empty boxes.

## 8. Teams, shops, and credits

The Team form shows only actions allowed by membership, role, and delegated permission. Owners can invite and remove members, appoint managers, control shop authority, and manage a shared point pool. Team kills contribute points. Team text and voice rooms are available.

The team shop sells supplies and Duo Plane, Humvee, APC, and Tank kits. Each vehicle type has its own team-wide five-minute purchase timer. Online teammates can appear as translocator destinations, using either a cell or team points where permitted.

Credits are persistent account data. Use `/credits` to read your balance. Credit chips can be scanned anywhere and deposited at a working ATM within range. The server saves the wallet transaction before consuming a chip or delivering a purchase. The online shop is categorized and purchases from the saved balance.

## 9. Chat, buffers, and voice

| Default | Destination |
| --- | --- |
| `/` | Global chat in the selected language channel. |
| `\` | Current map or mode chat. |
| `Shift+\` | Team chat. |
| `Alt+/` | Message your quick-chat group (or choose a group). |
| `Alt+Shift+/` | Your groups and invitations. |
| `Alt+\` | Recent private-message contacts and compose box. |

Global chat offers forty language channels plus Unfiltered through `/channel`. Messages receive server timestamps; a Notifications option can hide them locally without removing the audit record. `/withdraw` retracts the latest message for ten seconds while immediately preserving a staff audit copy. `/block`, `/unblock`, and `/blocked` manage persistent blocks.

Groups are chat rooms you make with other players, kept on the server between sessions. You can be in up to five. `Alt+Shift+/` lists your groups, any invitations waiting for you, and Create a group. Each group opens to its members, their roles and who is online. The owner and moderators invite people (who accept or decline) and remove members; the owner also appoints moderators, hands the group on, renames or disbands it; anyone can leave. `Alt+/` speaks in your quick-chat group, the only group you are in, or one you choose. Every change in a group has its own sound, heard in Learn the game's sounds, and goes into the groups buffer; each group's messages have their own buffer. Typed `/group chat`, `/group create`, `/group leave` and `/group accept` also work.

`Alt+Shift+B` opens the buffer manager, where buffers can be reordered without losing their state.

Commands require complete names. Unknown commands are reported; ambiguous prefixes list their matches. `Alt+C` opens the command menu. Useful commands include `/changes`, `/bug`, `/bugs`, `/feedback`, `/report`, `/team info`, `/team shop`, and `/bunkers`.

### Live voice chat

- `Alt+O` transmits according to push-to-talk or toggle mode.

- `Shift+V` enters or leaves an exclusive non-positional voice room. Leave one room before joining another. Ordinary positional voice is not a room.

- `Shift+F7` opens voice settings.

- `Alt+Shift+O` toggles hearing your own transmitted voice.

Voice settings include input/output devices, isolated microphone testing, self-monitoring, transmission mode, and quality. Selecting an input device does not permanently loop it to output.

### Windows voice commands

Voice control is opt-in and separate from live voice chat. Configure a wake phrase or press the rebindable `Ctrl+Shift+F9` default to listen directly. Distinct cues indicate listening, capture completion, and processing. Commands are deliberately read-only, such as status, health, ammunition, inventory, nearby items, points of interest, buffer movement, and repeating a message.

## 10. Android and touch-screen play

Touch input uses top, middle, and bottom bands in landscape. Portrait mode rotates them into left, centre, and right thirds while retaining logical bindings. Gestures are rebindable, resettable, and stored in a gesture configuration JSON.

- One-finger menu swipes move; double tap activates; two-finger tap goes back; two-finger up/down jumps to the first/last option.

- In audio forms, two-finger right acts as Tab and two-finger left as Shift+Tab.

- Contextual gesture help lists only actions relevant to the current form, menu, map, vehicle, or keyboard.

- Gesture practice announces the band, gesture, and function. Its in-game gesture toggles practice on and off.

- Middle-band movement drags suppress a pending aim swipe, reducing accidental aim changes.

- Explore by touch waits for a nearly stationary 450-millisecond hold before announcing controls.

- Full-screen touch bands can cover a laptop display so edge taps cannot activate another window.

The optional built-in keyboard supports QWERTY explore-by-touch (drag to hear, lift to type) and an analogue grid navigated by swipes and double tap. Both provide Shift, Caps Lock, Backspace, punctuation, Space, and Done.

## 11. Dynamic help, armoury, and practice

The help browser presents categories, topics, and read-only content as nested audio forms. System concepts remain authored documentation; weapons, ammunition, attachments, armour, items, and vehicles are rendered from the live database. `Alt+Enter` opens the same documentation for the current inventory entry.

The lobby Dynamic Armoury browses registered content, displays compatibility and live statistics, and previews authored sounds with nonblocking play/pause controls while retaining the underlying form.

Key practice is available from Information or `Shift+F1`. Gesture practice is available from Information and through its in-game gesture. Learn Game Sounds focuses on important recognition cues rather than listing every sound learned naturally through play.

## 12. Staff and server operation

Authorized staff can open the categorized Administrator Panel from the game menu or with `Ctrl+Shift+F8`. The server checks every action. Roles are administrator, moderator, support, and builder; developers can assign or remove them in game.

- **Moderation:** warnings, bans, kicks, account records, player reports, blocks, and combat-logout records.

- **Support:** tickets, bug reports, feedback, account service, and player assistance.

- **Builders:** the world editor.

- **Administration:** staff roster, authorization, communications, server controls, reboot timers, confirmed shutdown, permanent admin log, and garbage collection.

`/accounts` opens an account list and detailed record. Other gated commands include `/warn`, `/warnings`, `/ban`, `/unban`, `/bans`, `/reports`, `/adminlog`, `/gc`, `/staff`, `/staffrole`, and `/unstaff`.

Logout is rejected for 30 seconds after taking damage and 20 seconds after dealing damage. A disconnected combatant remains as a temporary combat ghost. Packet queues, automatic-fire updates, chat history, stale state, and explicit staff garbage collection are bounded to control lag without changing mechanics.

### World editor

Builders, administrators and developers open the world editor with `Alt+Shift+P`. It shows everything defined where you stand; builds streets, buildings with floors, stairs, doors and windows, whole districts, squares, parks, water, stairs, ramps, ladders, bridges, walls and doorways, placed relative to you and named, with every zone, acoustic space and ambience made for you; and it builds from a plain description such as "a three storey brick building called Harbour Flats to my left". You can mark an area and build into it, browse and edit every element on the map by name, set the map's title, lobby listing and size, undo and redo with a history, go to any map or make a new one, and edit item and weapon files and have the server reload them without restarting. Every change is validated, backed up and applied for everyone at once. The full guide is `iwserver/docs/world_editor.txt`.

## 13. Source builds, sound packs, and releases

The project targets NVGT 0.90. The server is `iwserver.exe`.

When running `Infinite Warfare.nvgt` from source, the Administrator Panel exposes **Compress a release build**. It asks before replacement, compiles the client, verifies or optionally builds `sounds.dat`, stages the executable, sound pack, recursive `lib` directory, changelog, and README, then creates `release.zip` with progress and a final result.

Check for updates compares the version you are running with the one on GitHub. If a newer version is published, the game closes and its updater downloads only the files that changed (Git is not needed), checks each one, removes files the game no longer uses, and starts the game again. If anything goes wrong, every file is put back as it was, and the game tells you what happened when it next starts; the details are in `updater/last_update.log`. Keep client and server versions synchronized when protocols or persistent formats change.

Repository status, on the main menu, shows the game's public GitHub repository from inside the game: an overview, how your copy compares with GitHub commit by commit, what is new in releases you do not have yet, recent commits with every file they changed, branches, pull requests and issues with their comments, releases, contributors, automated checks, languages and recent activity. Enter opens a line, `Alt+B` opens it in your browser, `Alt+C` copies it with its link, `Alt+M` loads more and `Alt+R` fetches it again. GitHub allows 60 requests an hour from one connection without signing in; each screen uses one or two, replies are reused for five minutes, and the request allowance section shows how many are left.

Sign in from Your GitHub account, at the top of Repository status, for 5000 requests an hour and to use your account: star, watch or fork the repository, open issues, comment, read your notifications about it and, if you may change the repository, close and reopen issues and pull requests and merge them. `Alt+A` lists what you can do on the current screen. Sign in with a personal access token: the game opens GitHub's token page with the right permissions chosen, and you paste the token in. Your sign-in stays in the game's settings folder on your computer and is only sent to GitHub; signing out deletes it.

## 14. Files and troubleshooting

- Preferences, keymaps, `keyconfig.json`, and gesture bindings are stored in local application data. Legacy local files are migrated with a notice.

- Unhandled script exceptions create a shareable log under `iw/crash_logs` in local application data. `latest_client_session.log` provides startup breadcrumbs for native failures.

- Connection failures clear transient state before retrying, preventing a recovered server from inheriting a half-open session.

- In play, `Alt+Home`/`Alt+End` select a volume mixer and `Home`/`End` adjust it in five-percent steps.

- Own projectile loops and flybys and world occlusion have separate Audio options. Environmental reverb no longer exists.

- Use `/bug` to submit a reproducible issue and `/bugs` to review its status. Include the action, map, approximate time, and crash log when available.

The live database is authoritative for content statistics and compatibility. Use Dynamic Help or the Dynamic Armoury instead of old external item lists.

## Credits and acknowledgements

Infinite Warfare is developed agentically by **Equinox_Equine**, using **GPT-5.6 Sol**, **Claude 4.8 Opus**, and **Claude 5 Opus**.

This project was forked from a leaked copy of **Infinite Warfair 0.14**, originally produced by **Firegaming**, with **Max Vrenken** as developer and **Djonan Smid** as sound designer. Those are historical credits for the source project, not the current development team.

**Blindpro** is credited for NVGT Helpers, and **Ivan Soto** is credited for NV_form. Sound-resource acknowledgements include **Executioner's Rage**, **Firefight**, **Call of Duty: Modern Warfare**, **Insurgency: Sandstorm**, and **Fortnite**. Product names, trademarks, and sound resources remain associated with their respective creators and rights holders; acknowledgement does not imply endorsement.

Manual revised for version 0.5.9.3, build 103.
