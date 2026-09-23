"""What every weapon, item, surface and service is supposed to sound like, and
what is actually there.

The old audit only looked at string literals, which misses almost everything:
practically every sound this game plays has its filename built at runtime out
of a weapon's sound profile, a surface's recording family or a service's type.
A weapon with no fire sound is not a missing literal, it is a weapon that goes
click.

Run with --pack to check the shipped archive as well as the source folder.
They are not the same thing, and a recording in one and not the other works
perfectly on the machine it was authored on and nowhere else.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOUNDS = ROOT / "sounds"
WEAPONS = ROOT / "iwserver/content/weapons"
MAPS = ROOT / "iwserver/content/maps"

# category -> (suffix, severity). "required" means the action is silent
# without it; "wanted" means the game falls back to something reasonable.
# The server picks a bullet impact at random from three unless it knows the
# profile has a different number, so three is the contract. Ricochets and the
# distant report both have class-wide fallbacks, so they are not per-weapon.
GUN_CONTRACT = [
    ("fire1.ogg", "required"),
    ("draw.ogg", "required"), ("holster.ogg", "required"),
    ("empty.ogg", "required"), ("reload.ogg", "required"),
    ("reloadend.ogg", "required"), ("unload.ogg", "required"),
    ("hit1.ogg", "required"), ("hit2.ogg", "wanted"), ("hit3.ogg", "wanted"),
    ("fire2.ogg", "wanted"), ("fire3.ogg", "wanted"),
]
MANUAL_CONTRACT = [
    ("reload_open.ogg", "required"), ("reload_insert.ogg", "required"),
    ("reload_close.ogg", "required"), ("reload_cycle.ogg", "wanted"),
]
MELEE_CONTRACT = [
    ("fire1.ogg", "required"), ("draw.ogg", "required"),
    ("holster.ogg", "required"), ("hit1.ogg", "required"),
    ("hit2.ogg", "wanted"), ("hit3.ogg", "wanted"),
]
MANUAL_CLASSES = {"shotgun", "revolver", "grenade_launcher"}
# The weapon file writes the short token; the game says the long name and the
# recording is filed under the long name.
MODE_NAMES = {"semi": "semi-automatic", "auto": "full automatic",
              "burst": "burst", "scattershot": "scattershot",
              "focused": "focused"}


def load_pack_listing():
    """The archive's own file list, via the extractor the project ships."""
    listing = ROOT / "tools/pack_listing.txt"
    if listing.is_file():
        return {line.strip().lower() for line in listing.read_text(encoding="utf-8").splitlines() if line.strip()}
    return None


def parse_weapons():
    weapons = {}
    for path in sorted(WEAPONS.rglob("*.wpn")):
        props = {}
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line:
                key, _, value = line.partition("=")
                props[key.strip()] = value.strip()
        wid = path.stem
        weapons[wid] = {
            "id": wid,
            "name": props.get("name", wid),
            "class": props.get("wclass", ""),
            "melee": props.get("melee", "false") == "true",
            "profile": props.get("sound_profile") or wid,
            "modes": [m.strip() for m in props.get("fire_modes", "").split(",") if m.strip()],
            # The game calls a weapon manually fed when its class loads one
            # round at a time and it does not take a magazine. A drum-fed
            # shotgun is not asked to open its action.
            "manual": (props.get("wclass", "") in MANUAL_CLASSES
                       and props.get("is_magazine", "false") != "true"),
            "path": path.relative_to(ROOT),
        }
    return weapons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wanted", action="store_true",
                        help="also list recordings the game can manage without")
    args = parser.parse_args()

    have = {p.relative_to(SOUNDS).as_posix().lower() for p in SOUNDS.rglob("*")
            if p.is_file() and p.suffix.lower() in (".ogg", ".wav", ".flac", ".mp3")}
    pack = load_pack_listing()

    def present(name):
        return name.lower() in have

    missing = defaultdict(list)
    weapons = parse_weapons()
    for w in weapons.values():
        p = w["profile"]
        contract = list(MELEE_CONTRACT if w["melee"] else GUN_CONTRACT)
        if not w["melee"] and w["manual"]:
            contract += MANUAL_CONTRACT
        # A weapon with one fire mode never cycles, so it never asks for the
        # announcement that says which mode it is now in.
        if len(w["modes"]) > 1:
            for mode in w["modes"]:
                contract.append((f"mode_{MODE_NAMES.get(mode, mode)}.ogg", "required"))
        for suffix, severity in contract:
            if not present(p + suffix):
                missing[severity].append((f"{w['name']} ({w['class'] or 'melee'})",
                                          p + suffix))

    # Surfaces and ambience the maps ask for.
    for path in sorted(MAPS.rglob("*.map")):
        families, beds = set(), set()
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split(":")
            if parts[0] == "surface" and len(parts) > 2:
                families.add(parts[2])
            elif parts[0] == "src" and len(parts) > 7:
                beds.add(parts[7])
        for family in sorted(families):
            if family.startswith("wall"):
                if not present(family + ".ogg"):
                    missing["required"].append((path.stem, family + ".ogg"))
                continue
            for suffix, severity in (("step1.ogg", "required"), ("land.ogg", "required"),
                                     ("fall.ogg", "wanted")):
                if not present(family + suffix):
                    missing[severity].append((path.stem, family + suffix))
        for bed in sorted(beds):
            if not present(bed):
                missing["required"].append((path.stem, bed))

    for severity in ("required", "wanted"):
        if severity == "wanted" and not args.wanted:
            continue
        rows = sorted(set(missing[severity]))
        print(f"\n{len(rows)} {severity} recordings missing from sounds/")
        for owner, name in rows:
            print(f"  {name:<52} {owner}")

    if pack is not None:
        gaps = sorted(n for n in have if n not in pack)
        print(f"\n{len(gaps)} recordings in sounds/ but not in the shipped archive")
        for name in gaps[:60]:
            print("  " + name)
        if len(gaps) > 60:
            print(f"  ... and {len(gaps) - 60} more")

    print(f"\n{len(weapons)} weapons, {len(have)} recordings on disk.")
    return 1 if missing["required"] else 0


if __name__ == "__main__":
    sys.exit(main())
