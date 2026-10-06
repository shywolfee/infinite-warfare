"""Static checks for game mechanics that 0.5.6 found wired up wrongly.

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

assert not problems, "\n".join(problems)
print("PASS mechanics wiring: corpses, collectables, equipment, healing and anti-cheat")
