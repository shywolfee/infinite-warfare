"""Check that weapon definitions agree with the ammunition they use.

0.5.4 stamped 76 firearm and launcher variants from five templates, so a Barrett fired
.308 from a 10-round magazine, a Desert Eagle shared Glock magazines and an
AT4 launched 40 mm grenades. These checks catch that whole class of mistake.
"""
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEAPONS = ROOT / "iwserver/content/weapons"


def properties(path: Path) -> dict[str, str]:
    return {
        line.partition("=")[0]: line.partition("=")[2]
        for line in path.read_text(encoding="utf-8").splitlines()
        if "=" in line
    }


weapons = {path.stem: properties(path) for path in WEAPONS.rglob("*.wpn")}
problems: list[str] = []

def calibre(props: dict[str, str]) -> str:
    return props["ammo_type"].split(" ")[0]


# A detachable magazine, belt or tube is one physical thing: everything that
# takes it must fire the same calibre. Fuel and energy cells are not
# cartridges, so they are left out.
by_reserve: dict[str, list[str]] = defaultdict(list)
for wid, props in weapons.items():
    if props.get("is_magazine") == "true" and "reserve_item" in props and props.get("ammo_display", "rounds") == "rounds":
        by_reserve[props["reserve_item"]].append(wid)
for reserve, users in by_reserve.items():
    calibres = {calibre(weapons[w]) for w in users}
    if len(calibres) > 1:
        problems.append(f"{reserve} is shared by different calibres: {sorted(calibres)}")

# Loose rounds (belts of revolver rounds, shell boxes, grenade bandoliers) can
# feed weapons of different capacity, but never of different calibre.
by_loose: dict[str, set[str]] = defaultdict(set)
for wid, props in weapons.items():
    if props.get("is_magazine") == "false" and "reserve_item" in props:
        by_loose[props["reserve_item"]].add(calibre(props))
for reserve, calibres in by_loose.items():
    if len(calibres) > 1:
        problems.append(f"{reserve} feeds different calibres: {sorted(calibres)}")

# One calibre, one projectile diameter.
diameters: dict[str, set[float]] = defaultdict(set)
for wid, props in weapons.items():
    if props.get("projectile_kind", "bullet") == "bullet" and "diameter_mm" in props and "ammo_type" in props:
        diameters[props["ammo_type"]].add(round(float(props["diameter_mm"]), 1))
for calibre, values in diameters.items():
    if max(values) - min(values) > 0.5:
        problems.append(f"{calibre} is modelled with diameters {sorted(values)}")

# Rocket launchers fire rockets, not grenades, and reach further than a pistol.
for wid, props in weapons.items():
    if props.get("wclass") == "rocket_launcher":
        if "grenade_bandolier" in props.get("reserve_item", ""):
            problems.append(f"{wid} is fed with grenades")
        if int(props["range"]) < 80:
            problems.append(f"{wid} has a {props['range']}-tile range")
        if float(props.get("diameter_mm", "84")) < 60:
            problems.append(f"{wid} launches a {props['diameter_mm']} mm projectile")

# The variant names must describe the weapon, not the importer's labels.
for wid, props in weapons.items():
    name = props["name"]
    if "Guided" in name and props.get("wclass") == "grenade_launcher":
        problems.append(f"{wid}: an unguided grenade launcher is called {name!r}")
    if name.startswith("M2 .50") and props.get("wclass") != "light_machine_gun":
        problems.append(f"{wid}: {name!r} is not an M2 heavy machine gun")

assert not problems, "\n".join(problems)
print(f"PASS weapon data: {len(weapons)} weapons agree with their ammunition")
