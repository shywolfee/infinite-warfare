"""Static checks for game mechanics that 0.5.6 and 0.5.7 found wired up wrongly.

Each of these looked fine in review and silently never worked: a service loop
that was never called, a variable name inside a string literal, a branch
nested where it could not be reached. None needs NVGT or the sound pack.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
server = (ROOT / "iwserver/iwserver.nvgt").read_text(encoding="utf-8")
server_includes = {p.name: p.read_text(encoding="utf-8") for p in (ROOT / "iwserver/includes").glob("*.nvgt")}
client = (ROOT / "Infinite Warfare.nvgt").read_text(encoding="utf-8")
ammo = (ROOT / "includes/ammo.nvgt").read_text(encoding="utf-8")
problems: list[str] = []

# Collectable items (corpse tokens, storage drops) need their loop serviced.
if "citemloop();" not in server:
    problems.append("citemloop() is never called, so dropped items cannot be collected")

# A variable name inside quotes sends the literal text to the client.
for name, text in {"iwserver.nvgt": server, **server_includes}.items():
    for match in re.finditer(r'"give parsed\[', text):
        problems.append(f"{name}: sends the literal text 'parsed[' as an item id")

# Corpses must carry the dead player's things, not an empty dictionary.
corpse = server_includes["corpse.nvgt"]
if "fill_corpse" not in corpse or 'parsed[0]=="corpse_inventory"' not in server:
    problems.append("corpses are not filled from the dying client's inventory")
if "report_corpse_inventory();" not in client:
    problems.append("the client does not report its inventory when it dies")

# The ring branch must be reachable in equip_item.
equip = ammo[ammo.index("void equip_item("):ammo.index("void unequip_item(")]
medical = equip[equip.index('slot == "medical"'):]
depth = 0
for index, char in enumerate(medical):
    if char == "{":
        depth += 1
    elif char == "}":
        depth -= 1
        if depth == 0:
            if 'slot=="ring"' in medical[:index]:
                problems.append("equip_item handles rings inside the medical-slot branch")
            break

# WireNet heals must be limited by server-held charges.
heal = server[server.index('parsed[0]=="wirenet_heal"'):server.index('parsed[0]=="bioscan"')]
if "wirenet_charges" not in heal:
    problems.append("wirenet_heal heals without server-side charges")

# Removed handlers that healed without an item must stay gone.
if 'parsed[0]=="use_potion"' in server:
    problems.append("the unused use_potion handler, which healed without an item, is back")

# Anti-cheat removals must disconnect the peer.
if server.count("players.remove_at(index);\n}\n}\nelse") and "was removed by anti-cheat" in server:
    problems.append("an anti-cheat removal leaves the peer connected")

# 0.5.7: one ammunition per calibre, no maintenance, no physics server.
handling = (ROOT / "includes/weapon_handling.nvgt").read_text(encoding="utf-8")
for word in ("ammunition_loads", "cycle_weapon_ammunition"):
    if word in ammo or word in client:
        problems.append(f"alternate ammunition ({word}) is back")
for word in ("heat", "fouling", "maintain_weapon", "jam_chance"):
    if re.search(rf"\b{word}", handling):
        problems.append(f"weapon_handling.nvgt still models {word}")
if list((ROOT / "iwserver/content/items").glob("weapon_maintenance/*.item")):
    problems.append("weapon maintenance items are back")
for name, text in {"iwserver.nvgt": server, **server_includes}.items():
    if "server_physics" in text:
        problems.append(f"{name}: calls the removed physics server")

# Vehicle use of weapons is data: every value must be one the server knows.
allowed = {"", "normal", "forbidden", "cabin_detonation", "cabin_fire", "backblast"}
grenade = server_includes["grenade.nvgt"]
for path in (ROOT / "iwserver/content/weapons").rglob("*.wpn"):
    props = dict(line.split("=", 1) for line in path.read_text(encoding="utf-8").splitlines() if "=" in line)
    use = props.get("vehicle_use", "").strip()
    if use not in allowed:
        problems.append(f"{path.name}: unknown vehicle_use {use!r}")
    if use and use != "normal" and f'"{use}"' not in grenade:
        problems.append(f"{path.name}: vehicle_use {use} has no server handling")
if "vehicle_weapon_mishap(" not in server:
    problems.append("firing from a vehicle skips vehicle_weapon_mishap")

# Only the driver may move a vehicle.
for packet in ("veh_turn", "veh_move"):
    start = server.index(f'parsed[0]=="{packet}"')
    if "authoritative_vehicle_driver_is" not in server[start:start + 600]:
        problems.append(f"{packet} is accepted from anyone, not only the driver")

# Every vehicle file describes its drivetrain.
for path in (ROOT / "iwserver/content/vehicles").rglob("*.vehicle"):
    text = path.read_text(encoding="utf-8")
    for key in ("transmission=", "gears=", "turning_radius=", "reverse_speed="):
        if key not in text:
            problems.append(f"{path.name}: missing {key}")

# Arena maps are unlisted and have a spectator gallery; arenas leave cleanly.
for path in (ROOT / "iwserver/content/maps").glob("*/arena_*.map"):
    text = path.read_text(encoding="utf-8")
    if "listed:false" not in text:
        problems.append(f"{path.name} is listed as an ordinary map")
    if "Spectator gallery" not in text:
        problems.append(f"{path.name} has no spectator gallery")
removals = server.count("players.remove_at(")
gone = server.count("arena_player_gone(players[")
if gone < removals:
    problems.append(f"{removals - gone} player removals in iwserver.nvgt leave arena membership behind")

# 0.5.7 shipped calling vehicle_fire_mounted_weapon() after its definition
# was lost in the driving rewrite, so the client would not compile. Every
# vehicle function the game calls must be defined somewhere in the client.
client_sources = client + "".join(p.read_text(encoding="utf-8", errors="replace") for p in (ROOT / "includes").glob("*.nvgt"))
defined = set(re.findall(r"^\s*[\w@\[\]]+\s+(vehicle_\w+|distract_driver)\s*\(", client_sources, re.M))
called = set(re.findall(r"\b(vehicle_\w+|distract_driver)\s*\(", re.sub(r'"(\\.|[^"\\\n])*"', '""', client_sources)))
defined |= set(re.findall(r"\bclass\s+(\w+)", client_sources))
for name in sorted(called - defined):
    problems.append(f"the client calls {name}() but never defines it")

assert not problems, "\n".join(problems)
print("PASS mechanics wiring: corpses, collectables, equipment, healing, anti-cheat, ammunition, vehicles and arenas")
