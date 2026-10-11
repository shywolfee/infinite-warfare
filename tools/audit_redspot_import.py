"""Check the Redspot content this game ships against the Redspot source it came from.

Redspot's own source is the authority for the weapon registry
(`server/weapons.json`), the item registry (`server/includes/items_db.nvgt`) and
the recordings under `sounds/weapons/<weapon>/`. This script reads both sides
and says, item by item and weapon by weapon, where the game has drifted from it.

An item is looked for anywhere under content/items and its offer anywhere under
content/marketplace, because where a file is filed is not a property of the
source; only what it says and what implements it are.

It exists because a previous import was written by hand instead of read from the
source: the weapon statistics were taken from the registry, but the recordings
the registry does not provide (the weapon's holster, its empty click, the end of
a reload, unloading) were filled in with another weapon's -- a pistol's slide
for every rifle. That is invisible in a game that runs and audible to anyone who
plays it, so the check has to be mechanical.

The same treatment is given to behaviour: every constant the port carries is
compared with the source's own (an item grabber that pressurizes for three
seconds where the source says 30013 ms), every package is compared with what
the source's open_package rolls, and every price with the source's items_db.
The explosives are still the largest known divergence: this engine resolves a
blast with its own overpressure model, so the per-object radius and damage the
source's explode() calls carry are not yet ported, only listed. The same is true
of the source's timed placements -- TIME_SANDBAG 3103 ms, TIME_LADDER 5192,
TIME_SPY_CAMERA 9020, TIME_SM2_MISSILE 5799, TIME_BULLET_BOMB 11222 and
TIME_BARRICADE_BOMB 15000, all of which hold the placer still for that long --
which is why those constants are not in CONSTANTS: the port places a sandbag at
once, and a check for a job that does not exist would only fail forever.

Run from this checkout with the Redspot source at REDSPOT_SOURCE (or the
sibling Downloads/redspot_old location). It needs no NVGT and no network.

    python tools/audit_redspot_import.py            # summary and failures
    python tools/audit_redspot_import.py --all      # every divergence, itemised

Exit status 0 when the shipped content matches the source, 1 when it does not.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get(
    "REDSPOT_SOURCE",
    str(Path.home() / "Downloads/redspot_old/redspot_old/redspot-main"),
))
WEAPONS = ROOT / "iwserver/content/weapons"
ITEMS = ROOT / "iwserver/content/items"
OFFERS = ROOT / "iwserver/content/marketplace"
SOUNDS = ROOT / "sounds"
MANIFEST = SOUNDS / "REDSPOT_AUDIO_SOURCES.json"

# Events this game's client plays by name that no recording in the Redspot
# registry provides. A file for one of them was invented by the import.
CRAFTED_CUES = ("holster", "empty", "reloadend", "unload", "reload_cycle",
                "reload_open", "reload_insert", "reload_close", "rico",
                "overheat", "vent", "jam")

# A handful of Redspot's items are found lying about its maps rather than
# bought, so its registry gives them no price. This game has no such map spawns
# to put them in, so it sells them rather than stranding them. The deviation is
# deliberate and is written down here so that it stays visible instead of
# becoming just another quiet difference from the source.
SOLD_WITHOUT_A_PRICE = {
    "bullet_bomb_locater", "claymore_remote", "fire_ball", "medal", "paintball",
    "robot", "stp429_mini_missile", "throwing_star", "water",
}

# Two more the source leaves lying about its own maps (map/killingground.map
# spawns both) and never sells. This game ships neither of those maps, so the
# only way to make them reachable at all is to sell them. The deviation is the
# missing map spawns, not the price.
SOLD_FROM_MAP_SPAWNS = {"antibiotic_canister", "smart_mine"}

# The source's own numbers, under whatever name this game gave them. The value
# is read from the source and compared, never trusted: a port that rounded the
# item grabber's 30013 ms into three seconds, gave a timebomb an hour where the
# source allows a minute, or rescaled a base's ceilings fails here. None means
# the name is the same in both trees.
CONSTANTS = {
    # server/includes/base.nvgt
    "BASE_WOOD_COST": None, "BASE_START_HEALTH": None, "BASE_MAX_HEALTH": None,
    "BASE_DOOR_HEALTH": None, "LOCKPICK_WINDOW_MS": None, "BASE_LOCKPICK_CLICKS": None,
    "BASE_MAX_LOCK_BOOSTS": None, "DOOR_OPEN_MS": None, "BASE_GENERATOR_X": None,
    "BASE_GENERATOR_Y": None, "BASE_GAS_PER_CAN": None, "BASE_MAX_GENERATOR_BOOSTS": None,
    "BASE_OS_VERSION": None, "BASE_COMPUTER_HEALTH": None, "BASE_FRIDGE_HEALTH": None,
    "BASE_STORAGE_HEALTH": None, "BASE_STORAGE_MAX_ITEMS": None,
    "BASE_STORAGE_MAX_AMMO": None, "BASE_FRIDGE_MAX_FOOD": None,
    "BASE_FRIDGE_MAX_COLD_FOOD": None, "BASE_MAX_GAS": None,
    "BASE_MACHINEGUN_MAX_AMMO": None, "BASE_MACHINEGUN_MAX_LIVE_MS": None,
    "BASE_MACHINEGUN_COOLDOWN_MS": None,
    # server/includes/item_use.nvgt, the clocks the long actions keep
    "TIME_BASE_BUILD": None, "TIME_ITEM_GRABBER": None, "TIME_ROCKET_BATTERY": None,
    "TIMEBOMB_MAX_SECONDS": None, "PACK_MAX_CONTENTS": None, "PACK_MAX_DEPTH": None,
    "TIME_HEALTH_MOVER": "REDSPOT_HEALTH_MOVER_MS",
    # server/includes/player.nvgt
    "ANTIBIOTIC_MAX_COURSES": "REDSPOT_ANTIBIOTIC_MAX_COURSES",
    "ANTIBIOTIC_SECONDS": "REDSPOT_ANTIBIOTIC_SECONDS",
    "ANTIBIOTIC_IMMUNITY_BASE": "REDSPOT_ANTIBIOTIC_IMMUNITY_BASE",
    "ANTIBIOTIC_IMMUNITY_GROWTH": "REDSPOT_ANTIBIOTIC_IMMUNITY_GROWTH",
    "ANTIBIOTIC_IMMUNITY_HALF": "REDSPOT_ANTIBIOTIC_IMMUNITY_HALF",
}

# Every canister bursts after the source's own TIME_CANISTER, which the item
# files carry as a fuse rather than as a constant.
CANISTERS = ("cyanide_canister", "teargas_canister", "oxygen_canister",
             "antibiotic_canister")

# What each package tips out, and how much of it, straight out of the source's
# open_package. A package that rolls a different range, or holds a different
# thing, is a package players will describe differently from the original.
PACKAGE_YIELDS = {
    "wood_pack": ("wood", 13, 18),
    "medal_pack": ("medal", 10, 15),
    "food_pack": ("food", 15, 25),
    "cold_food_pack": ("cold_food", 15, 25),
    "water_pack": ("water", 8, 14),
    "fire_ball_box": ("fire_ball", 8, 12),
    "throwing_star_volley": ("throwing_star", 10, 14),
    "spring_coil_pack": ("spring_coil", 10, 20),
    "matchbox": ("match", 10, 20),
    "paintball_pack": ("paintball", 8, 15),
    "empty_health_pod_pack": ("empty_health_pod", 10, 20),
}

# Items whose behaviour lives somewhere other than the item use path.
IMPLEMENTED_ELSEWHERE = {"corpse", "pack", "item_carying_projectile", "shipment", "robot"}

# A shipped item has to opt into some mechanic, and that mechanic has to be one
# the code actually reads. The first import shipped items whose behaviour was
# written fresh in the item file -- invented numbers under keys nothing looks
# at -- which is the failure this check exists to catch.
MECHANIC_KEYS = ("use_kind", "deployable", "throw_weapon", "pack_contents",
                 "provision", "turret_ammo_kind", "device_profile",
                 "companion_kind", "gadget", "contains")

# Two registry entries carry the names of weapons this game already had. The
# import left the existing files alone, so these two are Infinite Warfare's own
# weapons rather than Redspot's, and every recording under their names belongs
# to that other weapon. They are reported as one decision, not as noise.
COLLIDING = {"machete", "crossbow"}

# The decision taken on those two collisions, written down here so it stops
# being reported as an open question year after year. Both ids in this game are
# its own weapons: their files, their recordings, their shop entries and the
# players who already carry them. Redspot's registry entries for the same two
# names are therefore dropped rather than imported, because importing them would
# either rename this game's weapons out from under its players or leave Redspot's
# entry pretending to be something it is not. What is lost is two of the eighty
# weapons in the registry; what would be lost the other way is two weapons this
# game has shipped for years, so the port keeps its own and says so here.
DROPPED = {
    "machete": "this game's own machete keeps the name",
    "crossbow": "this game's own crossbow keeps the name",
}

# Reference field -> the weapon file key it becomes. Only the fields the game's
# loader honours are compared; a few registry fields (shield_damage,
# jam_chance) have no home in this engine and are reported separately.
REGISTRY_FIELDS = {
    "firetime": "firetime",
    "range": "range",
    "mindammage": "min_damage",
    "maxdammage": "max_damage",
    "spread": "spread",
    "speedtime": "speedtime",
}

# hit_effect -> the weapon file's on_hit. The import mapped three of the six
# effects Redspot uses.
EFFECTS = {"tase": "slow", "cyanide": "poison", "fire": "burn"}


def properties(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line and not line.startswith("#"))


def weapon_files() -> dict[str, Path]:
    return {path.stem: path for path in WEAPONS.rglob("*.wpn")}


def audit_weapons(report) -> None:
    registry = json.loads((SOURCE / "server/weapons.json").read_text(encoding="utf-8"))
    shipped = weapon_files()
    report.section(f"weapons: {len(registry)} in the Redspot registry")
    for wid, reference in registry.items():
        if wid not in shipped:
            report.fail(f"{wid}: no weapon file in {WEAPONS.relative_to(ROOT)}")
            continue
        if wid in COLLIDING:
            report.note(f"{wid}: the registry entry "
                        f"({reference['mindammage']}-{reference['maxdammage']} damage, {reference['firetime']} ms, "
                        f"range {reference['range']}) is dropped: {DROPPED[wid]}")
            continue
        props = properties(shipped[wid])
        for field, key in REGISTRY_FIELDS.items():
            want = str(reference[field])
            if props.get(key) != want:
                report.fail(f"{wid}: {key} is {props.get(key)!r}, the registry says {want}")
        want_walk = str(200 + reference["walk_time_impact"])
        if props.get("walktime") != want_walk:
            report.fail(f"{wid}: walktime is {props.get('walktime')!r}, the registry implies {want_walk}")
        want_modes = "auto" if reference["auto_fire"] else "semi"
        if want_modes not in (props.get("fire_modes") or ""):
            report.fail(f"{wid}: fire_modes is {props.get('fire_modes')!r}, the registry says {want_modes}")
        if str(reference["can_jump"]).lower() != props.get("can_jump"):
            report.fail(f"{wid}: can_jump is {props.get('can_jump')!r}, the registry says {str(reference['can_jump']).lower()}")
        # A weapon whose sound profile is not its own plays another weapon's
        # recordings, which is the failure this script was written to catch.
        if props.get("sound_profile", "") != wid:
            report.fail(f"{wid}: sound_profile is {props.get('sound_profile')!r}, so it borrows another weapon's recordings")
        effect = reference["hit_effect"]
        if effect in EFFECTS:
            if props.get("on_hit") != EFFECTS[effect]:
                report.fail(f"{wid}: on_hit is {props.get('on_hit')!r}, hit_effect {effect} means {EFFECTS[effect]!r}")
        elif effect in ("rocket", "grenade") and props.get("on_hit"):
            report.note(f"{wid}: hit_effect {effect} becomes on_hit {props['on_hit']!r}, which is this engine's own wording")

    # The recordings the registry names must be the recordings on disk, and
    # nothing else may sit under the weapon's name.
    report.section("weapon recordings")
    for wid, reference in registry.items():
        if wid in COLLIDING or wid not in shipped:
            continue
        profile = properties(shipped[wid]).get("sound_profile", wid)
        declared: set[str] = set()
        for kind, value in (("draw", reference["draw_sound"]), ("fire", reference["fire_sound"]),
                            ("hit", reference["hit_sound"]), ("reload", reference["reload_sound"]),
                            ("dist", reference["dist_sound"]), ("crit", reference["crit_sound"])):
            if value == "":
                continue
            # A prefix such as "weapons/knife/fire" means fire1.ogg, fire2.ogg...
            stem = Path(value).name
            stem = stem[:-4] if stem.endswith(".ogg") else stem
            declared.add(stem)
            directory = SOURCE / "sounds" / Path(value).parent
            variants = sorted(directory.glob(stem + "[0-9]*.ogg")) or [directory / (stem + ".ogg")]
            for source in variants:
                destination = SOUNDS / (profile + source.name)
                if not source.exists():
                    report.fail(f"{wid}: the registry names {value} but {source.relative_to(SOURCE)} is not in the source tree")
                elif not destination.exists():
                    report.fail(f"{wid}: {source.relative_to(SOURCE)} was never imported as {destination.name}")
        # The game picks an impact from as many recordings as it finds, so the
        # shared Redspot fallback (mischit1-5) has to be filed under the weapon
        # whose registry entry names no hit recording.
        if reference["hit_sound"] == "":
            for i in range(1, 6):
                if not (SOUNDS / f"{profile}hit{i}.ogg").exists():
                    report.fail(f"{wid}: the registry names no hit recording, so it needs the shared mischit{i} as {profile}hit{i}.ogg")
        # A group of sound events the game's client plays by name. Redspot never
        # recorded them, so a file for one of them was manufactured, and the one
        # place it could have come from is another weapon.
        for name in sorted(SOUNDS.glob(profile + "*.ogg")):
            suffix = name.stem[len(profile):]
            if suffix in CRAFTED_CUES and suffix not in declared:
                report.fail(f"{wid}: sounds/{name.name} is a {suffix} recording, which the Redspot registry does not name for this weapon")


def shipped_items() -> dict[str, Path]:
    """Every item file this game ships, wherever it is filed.

    The first version of this check looked only in content/items/redspot, which
    is where the first import happened to put things. Most of the Redspot items
    are filed by category -- explosives/, utility/, ammo/ -- so 36 items that
    were shipped were reported missing, and two that were genuinely missing
    (the spy camera and its controller) were hidden in the noise.
    """
    return {path.stem: path for path in ITEMS.rglob("*.item")}


def item_offers() -> dict[str, Path]:
    """Every supply offer, keyed by the item it sells rather than by file name."""
    found = {}
    for path in OFFERS.rglob("*.offer"):
        props = properties(path)
        item = props.get("item", "")
        if item and item not in found:
            found[item] = path
    return found


def source_constants() -> dict[str, str]:
    """Every const the source declares in the files this port came from."""
    found = {}
    for name in ("item_use.nvgt", "base.nvgt", "player.nvgt"):
        text = (SOURCE / "server/includes" / name).read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r'const\s+(?:int|double|string)\s+([A-Z0-9_]+)\s*=\s*([^;]+);', text):
            found.setdefault(match.group(1), match.group(2).strip().strip('"'))
    return found


def port_constants() -> dict[str, str]:
    """The same, as this game declares them."""
    found = {}
    for path in (ROOT / "iwserver").rglob("*.nvgt"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r'const\s+(?:int|double|string)\s+([A-Z0-9_]+)\s*=\s*([^;]+);', text):
            found.setdefault(match.group(1), match.group(2).strip().strip('"'))
    return found


def audit_behaviour(report) -> None:
    """The source's numbers and yields, against the port's own."""
    source = source_constants()
    port = port_constants()
    report.section(f"behaviour: {len(CONSTANTS)} of the source's own constants")
    for source_name, port_name in sorted(CONSTANTS.items()):
        if source_name not in source:
            report.fail(f"{source_name}: not declared anywhere under {SOURCE / 'server/includes'}"
                        " (the check is stale, not the port)")
            continue
        want = source[source_name]
        got = port.get(port_name or source_name)
        if got is None:
            report.fail(f"{source_name}={want}: {port_name or source_name} is not declared in this game")
        elif got != want:
            report.fail(f"{port_name or source_name} is {got}, the source's {source_name} is {want}")
        else:
            report.note(f"{port_name or source_name}={want} matches the source")
    # Canisters are activated on the ground, then burst after TIME_CANISTER.
    fuse = source.get("TIME_CANISTER")
    for name in CANISTERS:
        path = next(iter((ROOT / "iwserver/content/items").rglob(f"{name}.item")), None)
        if path is None:
            report.fail(f"{name}: no item file")
        elif properties(path).get("detonate_ms") != fuse:
            report.fail(f"{name}: detonate_ms is {properties(path).get('detonate_ms')!r}, "
                        f"the source's TIME_CANISTER is {fuse}")
    # What a package tips out, and how much of it.
    report.section(f"behaviour: {len(PACKAGE_YIELDS)} packages and their yields")
    shipped = shipped_items()
    for name, (inner, low, high) in sorted(PACKAGE_YIELDS.items()):
        path = shipped.get(name)
        if path is None:
            report.fail(f"{name}: the source sells it, this game does not ship it")
            continue
        wants = f"{inner}:{low}:{high}"
        declared = properties(path).get("pack_contents", "")
        if declared != wants:
            report.fail(f"{name}: pack_contents is {declared!r}, the source's open_package "
                        f"rolls {wants}")
        else:
            report.note(f"{name} gives {wants}, as the source rolls it")


def mechanic_sources() -> str:
    """The game's own code and content, for checking that a mechanic is read.

    A value is looked for in the sources and in the content files, because some
    of them name a weapon (`throw_weapon`) that lives in a .wpn file rather than
    in any line of code. An item whose own id appears in the code is handled by
    name, which is how a consumable like a jet's gas or a spring coil is read.
    """
    text = ""
    for root in (ROOT / "iwserver", ROOT / "includes"):
        for path in root.rglob("*.nvgt"):
            text += path.read_text(encoding="utf-8", errors="ignore")
    for pattern in ("*.wpn", "*.item", "*.offer", "*.object"):
        for path in (ROOT / "iwserver/content").rglob(pattern):
            text += path.read_text(encoding="utf-8", errors="ignore")
    return text


def check_mechanic(report, name: str, key: str, value: str, code: str,
                   items: dict[str, Path], weapons: set[str]) -> None:
    """One declared mechanic, checked against what actually reads it."""
    if value == "true":
        return
    if key == "throw_weapon":
        # The thrown thing is a weapon of its own; the code resolves it with
        # find_wpn_stats, so a missing weapon file is a thrown item that would
        # refuse to be thrown.
        if value not in weapons:
            report.fail(f"{name}: throws {value!r}, and no weapon file by that name exists")
        return
    if key == "pack_contents":
        # Either a fixed amount (one item, or a set that becomes two things) or a
        # range, which is the source's own shape for a package: it names the item
        # and the two ends of the amount it rolls.
        parts = value.split(":")
        inner = parts[0]
        if inner not in items:
            report.fail(f"{name}: opens into {inner!r}, which is not a shipped item")
            return
        if len(parts) not in (2, 3) or not all(part.isdigit() for part in parts[1:]):
            report.fail(f"{name}: pack_contents {value!r} is neither item:amount nor item:min:max")
            return
        amounts = [int(part) for part in parts[1:]]
        if not all(1 <= amount <= 500 for amount in amounts):
            report.fail(f"{name}: opens into {parts[1:]!r} items, and the item use path accepts 1 to 500")
        if len(amounts) == 2 and amounts[1] < amounts[0]:
            report.fail(f"{name}: pack_contents {value!r} rolls backwards")
        return
    if value in code or name in code:
        return
    report.fail(f"{name}: {key}={value!r} is not read by any server or client source")


def audit_items(report, everything: bool) -> None:
    text = (SOURCE / "server/includes/items_db.nvgt").read_text(encoding="utf-8")
    declared = {}
    for line in text.splitlines():
        match = re.match(r'\s*defitem\(\s*"([A-Za-z0-9_]+)"\s*,\s*([A-Z_]+)\s*,\s*(-?\d+)\s*,', line)
        if match:
            declared[match.group(1)] = (match.group(2), int(match.group(3)))
    templated = len(re.findall(r'defitem\(\s*"[^"]*"\s*\+', text))
    shipped = shipped_items()
    offers = item_offers()
    code = mechanic_sources()
    weapons = set(weapon_files())
    report.section(f"items: {len(declared)} declared in items_db.nvgt ({templated} generated from a template), {len(shipped)} shipped")
    for name, (category, price) in sorted(declared.items()):
        if name not in shipped:
            # Ammunition types and packs are generated from a template in the
            # source and are imported under their own names by the weapon
            # importer, so they are reported separately.
            if name.startswith("ammo_") or name.endswith("_pack"):
                report.note(f"{name} ({category}, ${price}): not shipped under this name")
            else:
                report.fail(f"{name} ({category}, ${price}): declared in the source, not shipped as an item")
            continue
        props = properties(shipped[name])
        # The item has to opt into a mechanic, and that mechanic has to appear in
        # the code that implements it. An item file full of keys nothing reads is
        # a stub, however convincing it looks.
        if name in IMPLEMENTED_ELSEWHERE:
            report.note(f"{name}: implemented by the cargo and loot code rather than the item use path")
        else:
            declared_keys = [key for key in MECHANIC_KEYS if props.get(key)]
            # An item read by name -- a jet's gas, a spring coil, the cardboard
            # box everything is packed in -- needs no key of its own, so the
            # absence of one is only a fault when nothing reads its name either.
            if not declared_keys and name not in code and not name.startswith("health_pod_"):
                report.fail(f"{name}: the item exists but declares no mechanic and nothing reads its name ({shipped[name].relative_to(ROOT)})")
            for key in declared_keys:
                check_mechanic(report, name, key, props[key], code, shipped, weapons)
        offer = offers.get(name)
        if price < 0 and offer is not None:
            if name in SOLD_WITHOUT_A_PRICE:
                report.note(f"{name}: the source gives it no price; this game sells it deliberately (see SOLD_WITHOUT_A_PRICE)")
            elif name in SOLD_FROM_MAP_SPAWNS:
                report.note(f"{name}: the source spawns it on its own maps instead of selling it; "
                            "this game ships none of those maps and sells it instead "
                            "(see SOLD_FROM_MAP_SPAWNS)")
            else:
                report.fail(f"{name}: the source does not sell it (price -1), but {offer.relative_to(ROOT)} offers it")
        if price >= 0 and offer is not None:
            offered = properties(offer).get("price")
            if offered != str(price):
                report.fail(f"{name}: offered at {offered} in {offer.relative_to(ROOT)}, the source sells it at {price}")
        report.note(f"{name}: shipped as {props.get('category')!r}, the source files it under {category}")
        if everything:
            report.note(f"    source help: {_help_text(text, name)}")


def _help_text(text: str, name: str) -> str:
    match = re.search(r'defitem\(\s*"' + re.escape(name) + r'",\s*[A-Z_]+,\s*-?\d+,\s*"[^"]*",\s*"([^"]*)"', text)
    return (match.group(1)[:110] + "...") if match else "(none)"


def audit_provenance(report) -> None:
    """What the import recorded about where each recording came from."""
    manifests = (MANIFEST, SOUNDS / "REDSPOT_EXPLOSIVE_AUDIO_SOURCES.json",
                 SOUNDS / "REDSPOT_ITEM_AUDIO_SOURCES.json")
    total = 0
    for manifest_path in manifests:
        if not manifest_path.exists():
            report.fail(f"{manifest_path.relative_to(ROOT)} is missing")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        total += len(manifest)
        for entry in manifest:
            origin = entry["source"].replace("\\", "/")
            target = SOUNDS / entry["destination"]
            if not origin.startswith("sounds/"):
                report.fail(f"{entry['destination']} has non-Redspot provenance: {origin}")
                continue
            source = SOURCE / origin
            if not source.is_file() or not target.is_file():
                report.fail(f"{entry['destination']} is missing its source or destination")
            elif source.suffix.lower() == target.suffix.lower() and source.read_bytes() != target.read_bytes():
                report.fail(f"{entry['destination']} does not match its named Redspot recording")
    report.section(f"recordings with Redspot provenance: {total}")


class Report:
    def __init__(self, everything: bool = False):
        self.failures: list[str] = []
        self.notes: list[str] = []
        self.everything = everything

    def section(self, title: str) -> None:
        print(f"\n{title}")

    def fail(self, message: str) -> None:
        self.failures.append(message)
        print(f"  FAIL {message}")

    def note(self, message: str) -> None:
        self.notes.append(message)
        if self.everything:
            print(f"  .... {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="list every divergence, not just the first few")
    args = parser.parse_args()
    if not (SOURCE / "server/weapons.json").exists():
        print(f"Redspot source not found at {SOURCE}. Set REDSPOT_SOURCE to the redspot checkout.")
        return 2
    report = Report(args.all)
    audit_weapons(report)
    audit_items(report, args.all)
    audit_behaviour(report)
    audit_provenance(report)
    print(f"\n{len(report.failures)} divergences from the Redspot source, {len(report.notes)} notes")
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
