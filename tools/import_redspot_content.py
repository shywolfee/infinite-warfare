"""Import Redspot weapon definitions and their own recorded sound lifecycle.

Run from this checkout with the original Redspot source tree available at
REDSPOT_SOURCE (or the sibling Downloads/redspot_old location). The source
weapon JSON remains authoritative; this script never overwrites existing
Infinite Warfare receivers or recordings.

The recordings are the registry's own: a draw, a fire prefix, a hit prefix, and
where the registry names them a distant report, a reload and a critical hit.
Nothing else is invented. Redspot is silent for a holster, an empty chamber, the
end of a reload and unloading, so this import is silent for them too; the first
run of this script filled them in from glock17 and machete, which is why a
Redspot rifle used to holster with a pistol's slide. `--prune` deletes those
borrowed recordings, and tools/audit_redspot_import.py fails if one returns.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get(
    "REDSPOT_SOURCE",
    str(Path.home() / "Downloads/redspot_old/redspot_old/redspot-main"),
))
WEAPONS = ROOT / "iwserver/content/weapons"
ITEMS = ROOT / "iwserver/content/items/ammo"
OFFERS = ROOT / "iwserver/content/marketplace"
SOUNDS = ROOT / "sounds"
MANIFEST = SOUNDS / "REDSPOT_AUDIO_SOURCES.json"

CATEGORIES = {
    "melee": "melee_blunt", "thrown": "archery", "energy": "energy",
    "chemical": "incendiary", "pistol": "handguns", "shotgun": "shotguns",
    "rifle": "assault_rifles", "sniper": "sniper_rifles",
    "explosive": "rocket_launchers",
}

AMMO_PACKS = {
    "9mm_bullet": (60, 10), "5.56mm_bullet": (60, 15),
    "7.62mm_bullet": (60, 20), ".357_magnum_bullet": (36, 15),
    "12.7mm_bullet": (30, 100), "stp12_bullet": (40, 20),
    "m1_rocket": (6, 10), "gas": (120, 10),
    "battery": (150, 5), "40mm_grenade": (8, 25),
    "bolt": (30, 15), "throwing_knife": (30, 15),
    "taser_cartridge": (5, 30), "cyanide_cartridge": (15, 40),
}


def ffmpeg(args: list[str]) -> None:
    """Run ffmpeg, the way the other importers in tools/ do."""
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def display(identifier: str) -> str:
    return identifier.replace("_", " ").replace("&", "and").title()


def serialize(values: dict) -> str:
    return "".join(f"{key}={value}\n" for key, value in values.items())


def import_weapon(identifier: str, source: dict) -> None:
    if identifier in {"machete", "crossbow"}:
        return
    category = source["category"]
    folder = CATEGORIES[category]
    if category == "melee":
        folder = "melee_short_blade" if any(
            word in identifier for word in ("knife", "dagger", "scalpel", "blade")
        ) else "melee_long_blade" if any(
            word in identifier for word in ("sword", "sabre", "machete", "axe")
        ) else "melee_blunt"
    if identifier == "m79_grenade_launcher":
        folder = "grenade_launchers"
    if identifier == "cannon":
        folder = "artillery"
    wclass = folder.rstrip("s")
    wclass = {
        "handgun": "pistol", "shotgun": "shotgun", "assault_rifle": "assault_rifle",
        "sniper_rifle": "sniper_rifle", "rocket_launcher": "rocket_launcher",
        "artillery": "explosive", "melee_short_blade": "melee_short_blade",
        "melee_long_blade": "melee_long_blade", "melee_blunt": "melee_blunt",
    }.get(wclass, wclass)
    if identifier == "taser" or identifier == "cyanide_pistol":
        wclass = "energy"
    if identifier == "flameburst_mini_flame_thrower":
        wclass = "incendiary"
    if identifier in ("blz83_portable_machine_gun", "browning_m2_heavy_50_cal_machinegun", "m134_minigun", "nak_nk1000_decimater"):
        wclass = "light_machine_gun"
    if identifier == "modern_sub_machine_gun_carbine":
        wclass = "submachine_gun"
    if identifier == "sky_429_laser_shotgun":
        wclass = "shotgun"
    fire_count = len(list((SOURCE / "sounds/weapons" / identifier).glob("fire[0-9]*.ogg")))
    values = {
        "name": "Redspot M79 Grenade Launcher" if identifier == "m79_grenade_launcher" else display(identifier), "melee": str(category == "melee").lower(),
        "firetime": source["firetime"], "walktime": 200 + source["walk_time_impact"],
        "speedtime": source["speedtime"], "range": source["range"],
        "min_damage": source["mindammage"], "max_damage": source["maxdammage"],
        "spread": source["spread"], "wclass": wclass,
        "sound_profile": identifier,
        "fire_sound_variants": max(1, fire_count),
        "fire_modes": "auto" if source["auto_fire"] else "semi",
        "class_modes": "false", "can_jump": str(source["can_jump"]).lower(),
    }
    if category != "melee" and source["ammo_type"] != "none":
        ammo = source["ammo_type"]
        values.update({
            "ammo_type": "cannonball" if ammo == "cannon_ball" else ammo.replace("_", " "),
            "feed_device": f"{source['capacity']}-round feed",
            "capacity": source["capacity"],
            "reserve_item": "cannon_ball" if ammo == "cannon_ball" else "ammo_" + ammo,
            "reserve_label": "rounds", "is_magazine": "false",
            "starting_reserve": source["initial_ammo"],
            "reload_ms": source["reloadtime"], "ammo_display": "rounds",
        })
    effect = source["hit_effect"]
    if effect == "tase":
        values.update(on_hit="slow", effect_ms=10000)
    elif effect == "cyanide":
        values.update(on_hit="poison")
    elif effect == "fire":
        values.update(on_hit="burn")
    if identifier == "cannon":
        values.update(projectile_kind="shell", muzzle_velocity=60,
                      gravity=9.81, drag=.012, explosive_radius=10,
                      blast_damage=1200, explosion_sound="firefight_cannon_ball_explode",
                      explosion_distant="firefight_cannon_ball_dist.ogg",
                      explosion_impact="firefight_cannon_ball_explode",
                      projectile_loop="firefight_cannon_ball_flight_loop.ogg",
                      kill_label="Redspot cannon")
    if identifier == "m79_grenade_launcher":
        values.update(projectile_kind="shell", muzzle_velocity=34,
                      gravity=11, drag=.025, explosive_radius=8,
                      blast_damage=700, explosion_sound="fraggrenadeexplode",
                      explosion_distant="fraggrenadedist.ogg",
                      explosion_impact="fraggrenadeexplode",
                      projectile_loop="firefight_cannon_ball_flight_loop.ogg",
                      kill_label="Redspot M79 grenade")
    if identifier == "t1_rocket_launcher":
        values.update(projectile_kind="shell", muzzle_velocity=70,
                      gravity=2.8, drag=.009, explosive_radius=13,
                      blast_damage=1000,
                      explosion_sound="firefight_conventional_missile_explode",
                      explosion_distant="firefight_conventional_missile_dist.ogg",
                      explosion_impact="firefight_conventional_missile_explode",
                      projectile_loop="firefight_conventional_missile_flight_loop.ogg",
                      kill_label="Redspot T1 rocket")
    path = WEAPONS / folder / (identifier + ".wpn")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize(values), encoding="utf-8")
    offer = OFFERS / "weapons" / (identifier + ".offer")
    offer.write_text(serialize({
        "name": values["name"], "category": "Weapons: " + folder.replace("_", " "),
        "summary": "Redspot weapon with its own handling, ammunition and recorded effects.",
        "item": identifier, "quantity": 1,
        "price": max(25, source["price"] * 20 if source["price"] >= 0 else 250),
        "max_order": 5, "enabled": "true",
    }), encoding="utf-8")


def import_ammo(weapons: dict) -> None:
    required = {w["ammo_type"] for w in weapons.values()} - {"none", "cannon_ball"}
    for ammo in sorted(required):
        reserve = "ammo_" + ammo
        item = ITEMS / (reserve + ".item")
        if item.exists():
            continue
        amount, price = AMMO_PACKS[ammo]
        item.write_text(serialize({
            "name": display(ammo) + " Rounds", "category": "Ammo",
            "summary": f"Loose {display(ammo)} ammunition for compatible Redspot weapons.",
            "give_amount": amount,
        }), encoding="utf-8")
        offer = OFFERS / "ammo" / (reserve + ".offer")
        offer.write_text(serialize({
            "name": display(ammo) + " Rounds", "category": "Ammo",
            "summary": f"{amount} loose rounds of {display(ammo)} ammunition.",
            "item": reserve, "quantity": amount, "price": price * 20,
            "max_order": 20, "enabled": "true",
        }), encoding="utf-8")


def import_audio(weapons: dict) -> list[dict]:
    manifest: list[dict] = []
    for identifier in weapons:
        if identifier in {"machete", "crossbow"}:
            continue
        directory = SOURCE / "sounds/weapons" / identifier
        for source in sorted(directory.glob("*.ogg")):
            destination = SOUNDS / (identifier + source.name)
            if not destination.exists():
                shutil.copy2(source, destination)
            manifest.append({"destination": destination.name,
                             "source": str(source.relative_to(SOURCE))})
        # Nothing is borrowed for the events the registry leaves unnamed. A
        # weapon Redspot never holstered a recording for does not holster with
        # another weapon's slide: it is silent, and so is this import.
        #
        # The one replacement Redspot makes itself is the impact sound. Where
        # the registry names no hit recording, play_weapon_hit falls back to the
        # shared mischit1-5, so those are what gets filed under the weapon.
        if weapons[identifier]["hit_sound"] == "":
            for index in (1, 2, 3, 4, 5):
                source = SOURCE / "sounds" / ("mischit" + str(index) + ".ogg")
                destination = SOUNDS / (identifier + "hit" + str(index) + ".ogg")
                # Overwritten even if a previous import put another weapon's
                # impact under this name.
                shutil.copy2(source, destination)
                manifest.append({"destination": destination.name,
                                 "source": str(source.relative_to(SOURCE))})
    for name in ("parachute_open.ogg", "parachute_close.ogg",
                 "spring_bootsjump.ogg", "spring_bootsland.ogg",
                 "propulsion_jet.ogg", "propulsion_jetfail.ogg",
                 *(f"lockpick{i}.ogg" for i in range(1, 11)),
                 "lockpicksuccess.ogg"):
        matches = list((SOURCE / "sounds").rglob(name))
        if len(matches) != 1:
            raise ValueError(f"Expected one Redspot mobility cue for {name}")
        destination = SOUNDS / name
        if not destination.exists():
            shutil.copy2(matches[0], destination)
        manifest.append({"destination": name,
                         "source": str(matches[0].relative_to(SOURCE))})
    for directory in [SOURCE / "sounds/combos", *(
        SOURCE / "sounds/weapons" / move for move in (
            "light_punch", "punch", "heavy_punch", "light_kick", "kick",
            "heavy_kick", "grab", "throw", "slam"))]:
        for source in sorted(directory.glob("*.ogg")):
            destination = SOUNDS / ("redspot_" + (
                source.name if directory.name == "combos" else
                directory.name + "_" + source.name))
            if not destination.exists():
                shutil.copy2(source, destination)
            manifest.append({"destination": destination.name,
                             "source": str(source.relative_to(SOURCE))})
    horn = SOURCE / "sounds/horn.ogg"
    destination = SOUNDS / "redspot_horn.ogg"
    if not destination.exists():
        shutil.copy2(horn, destination)
    manifest.append({"destination": destination.name,
                     "source": str(horn.relative_to(SOURCE))})
    thrown_cues = {
        "poison_dart": ("objectthrow.ogg", "poisonhit.ogg"),
        "antibiotic_dart": ("objectthrow.ogg", "antibiotic.ogg"),
        "throwing_star": ("throwing_starthrow.ogg", "throwing_star.ogg"),
        "fire_ball": ("fire_ballthrow.ogg", "fire_ballhit.ogg"),
        "paintball": ("paintball_throw.ogg", "paintball_hit.ogg"),
        "small_projectile": ("smallprojectilefire.ogg", "smallprojectilehit.ogg"),
        "poisoned_small_projectile": ("smallprojectilefire.ogg", "smallprojectilehit.ogg"),
        "tasing_small_projectile": ("smallprojectilefire.ogg", "smallprojectilehit.ogg"),
        "tasing_poisoned_small_projectile": ("smallprojectilefire.ogg", "smallprojectilehit.ogg"),
        "stat_pingger": ("pingstart.ogg", "smallprojectilehit.ogg"),
    }
    for identifier, (fire, hit) in thrown_cues.items():
        for event, filename in [("fire1", fire), *(
            (f"hit{i}", hit) for i in range(1, 4))]:
            source = SOURCE / "sounds" / filename
            destination = SOUNDS / f"redspot_{identifier}_projectile{event}.ogg"
            if not destination.exists():
                shutil.copy2(source, destination)
            manifest.append({"destination": destination.name,
                             "source": str(source.relative_to(SOURCE))})
        # A thrown device is not a weapon: Redspot plays the throw and the
        # impact and nothing else. The draw, empty, holster and reload cues a
        # previous import copied from the crossbow are left out, and --prune
        # removes them.

    # Every companion is sounded the same way: the server tells clients to play
    # "executioners_rage/<companion_sound>/<event>.wav" (see
    # iwserver/includes/world_sound.nvgt). Redspot's robot recordings are Oggs,
    # so they are re-encoded rather than copied, and filed where the game looks.
    # The first import left them as sounds/redspot_robot/*.ogg, which nothing
    # ever asks for, so the robot deployed silently.
    robot = SOUNDS / "executioners_rage/redspot_robot"
    robot.mkdir(parents=True, exist_ok=True)
    for event, original in (("activate", "robotstart"), ("fly", "robotstart"),
                            ("impact1", "robothit1"), ("impact2", "robothit2"),
                            ("impact3", "robothit3")):
        source = SOURCE / "sounds" / (original + ".ogg")
        destination = robot / (event + ".wav")
        if not destination.exists() or source.stat().st_mtime > destination.stat().st_mtime:
            ffmpeg(["-i", str(source), "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "1", str(destination)])
        manifest.append({"destination": "executioners_rage/redspot_robot/" + event + ".wav",
                         "source": str(source.relative_to(SOURCE))})
    # The folder the first import created instead, now that it has been moved.
    stale_robot = SOUNDS / "redspot_robot"
    if stale_robot.is_dir():
        shutil.rmtree(stale_robot)
    for event, original in (("start", "itemgrabberstart"), ("fire", "itemgrabberfire")):
        source = SOURCE / "sounds" / f"{original}.ogg"
        destination = SOUNDS / f"redspot_item_grabber_{event}.ogg"
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    # Redspot plays corpse_bomb.ogg both when the bomb goes off and as its
    # distant report (player.nvgt: play("corpse_bomb") then
    # send_dist_sound_at("corpse_bomb.ogg")); mass_bombdist belongs to the mass
    # bomb and was borrowed here by mistake.
    for event, original in (("explode", "corpse_bomb"), ("dist", "corpse_bomb")):
        source = SOURCE / "sounds" / f"{original}.ogg"
        destination = SOUNDS / f"redspot_corpse_bomb_{event}.ogg"
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    for destination_name, original in (
        ("redspot_rocket_battery_use.ogg", "rocket_batteryuse.ogg"),
        ("redspot_rocket_battery_explode.ogg", "rocket_battery.ogg"),
        ("redspot_rocket_battery_dist.ogg", "rocket_batterydist.ogg"),
        ("redspot_stp429_launch.ogg", "stp429_launch.ogg"),
        ("redspot_stp429_explode.ogg", "stp429_explode.ogg"),
        ("redspot_stp429_dist.ogg", "stp429_explode_dist.ogg")):
        source = SOURCE / "sounds" / original
        destination = SOUNDS / destination_name
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    for event, original in (("fire", "base_machinegun_ext"),
                            ("dist", "base_machinegun_dist"),
                            ("hit1", "base_machinegun_impact"),
                            ("hit2", "base_machinegun_impact"),
                            ("hit3", "base_machinegun_impact")):
        source = SOURCE / "sounds" / f"{original}.ogg"
        destination = SOUNDS / f"redspot_base_machinegun_{event}.ogg"
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    noise = SOURCE / "sounds/sound_grenade.ogg"
    destination = SOUNDS / "redspot_sound_grenade_noise.ogg"
    if not destination.exists():
        shutil.copy2(noise, destination)
    manifest.append({"destination": destination.name,
                     "source": str(noise.relative_to(SOURCE))})
    for event, original in (("loop", "item_carying_projectile"),
                            ("fire", "item_carying_projectilefire"),
                            ("deploy", "item_carying_projectiledeploy"),
                            ("destroy", "smallprojectilesmash")):
        source = SOURCE / "sounds" / f"{original}.ogg"
        destination = SOUNDS / f"redspot_item_cargo_{event}.ogg"
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    for source in sorted((SOURCE / "sounds").glob("spy_camera*.ogg")):
        destination = SOUNDS / ("redspot_" + source.name)
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    distant = SOURCE / "sounds/spy_camera_explosion_dist.ogg"
    destination = SOUNDS / "redspot_spy_camera_dist.ogg"
    if not destination.exists():
        shutil.copy2(distant, destination)
    manifest.append({"destination": destination.name,
                     "source": str(distant.relative_to(SOURCE))})
    return manifest


def import_base_audio() -> list[dict]:
    """Redspot's recordings for its own base, which the base port plays.

    The base is a map of its own with a door, a generator, a fridge, a storage
    area and a machinegun in it, and Redspot recorded a cue for almost every
    thing each of them does: 133 files, all of them named `base_*`. The weapon
    import brought across only the recordings a weapon or a gadget referenced,
    so every one of these was missing and the ported base would have run
    silently. They are copied under the names the Redspot code plays.

    Only this checkout's own `sounds` folder counts. The source tree also holds
    a copy of another WarCry game whose own `sounds` folder carries 132 files
    with the same names, and those are not what this port reads.
    """
    manifest: list[dict] = []
    sources = sorted((SOURCE / "sounds").glob("base_*.ogg"))
    sources += sorted((SOURCE / "sounds").glob("base_*.wav"))
    if len(sources) != 133:
        raise ValueError(f"Expected 133 Redspot base recordings, found {len(sources)}")
    for source in sources:
        destination = SOUNDS / source.name
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    return manifest


def import_structure_audio() -> list[dict]:
    """Redspot's recordings for sandbag walls and charged shields.

    Sandbags are a structure with a recording for every way one is met -- being
    built, taking a bullet, taking a blast, coming down -- and the wall tile
    they put on the map has its own thump. Shields announce themselves, absorb a
    shot and break. None of them was named by a weapon or by the base import, so
    the port played a wooden wall where a sandbag stood and was silent when a
    shield was raised or spent. They are copied under the names the Redspot code
    plays.
    """
    manifest: list[dict] = []
    names = [f"sandbag_bullet{i}.ogg" for i in range(1, 11)]
    names += ["sandbag_destroy.ogg", "sandbag_hit.ogg", "sandbag_impact.ogg",
              "sandbag_place.ogg", "sandbag_repair.ogg",
              "sandbag_throwing_star.ogg", "wallsandbag.ogg",
              "shieldbreak.ogg", "shieldextract.ogg", "shieldhit.ogg",
              "shieldon.ogg",
              # The port's own device, structure and mobility cues. Each is
              # played by name from the ported Redspot code, and none of them
              # was named by the weapon import, so each was silent.
              "airtank.ogg", "antibiotic.ogg", "box_open.ogg",
              "gas_maskbreathe.ogg", "health_mover_start.ogg",
              "health_mover_stop.ogg", "itemgrabberstart.ogg",
              "itemgrabberfire.ogg", "rocket_batteryuse.ogg",
              "stp429_launch.ogg", "stp429_warn.ogg",
              "ladder_collapse.ogg", "ladder_place.ogg"]
    for name in names:
        source = SOURCE / "sounds" / name
        if not source.is_file():
            raise ValueError(f"Expected a Redspot recording for {name}")
        destination = SOUNDS / name
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    return manifest


def merge_manifest(new: list[dict]) -> None:
    """Adds entries to sounds/REDSPOT_AUDIO_SOURCES.json without losing any."""
    recorded = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else []
    known = {entry["destination"] for entry in recorded}
    for entry in new:
        if entry["destination"] not in known:
            recorded.append(entry)
            known.add(entry["destination"])
    MANIFEST.write_text(json.dumps(recorded, indent=2) + "\n", encoding="utf-8")


def prune(manifest: list[dict]) -> int:
    """Delete the recordings an earlier import borrowed from Infinite Warfare.

    The manifest left by the first import says which destination files came from
    this game rather than from Redspot. Anything the current manifest no longer
    accounts for is one of them, so it goes: the weapons are silent for those
    events, exactly as Redspot is. Nothing Redspot recorded is ever removed.
    """
    previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else []
    accounted = {entry["destination"] for entry in manifest}
    removed = 0
    for entry in previous:
        if entry["destination"] in accounted:
            continue
        if not entry["source"].startswith("Infinite Warfare sounds/"):
            continue
        path = SOUNDS / entry["destination"]
        if path.exists():
            path.unlink()
            removed += 1
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prune", action="store_true",
                        help="also delete recordings an earlier import borrowed from Infinite Warfare")
    parser.add_argument("--base-sounds", action="store_true",
                        help="import Redspot's 264 base recordings and stop; leaves weapons alone")
    parser.add_argument("--structure-sounds", action="store_true",
                        help="import Redspot's sandbag and shield recordings and stop; leaves weapons alone")
    args = parser.parse_args()
    if args.structure_sounds:
        structure = import_structure_audio()
        merge_manifest(structure)
        print(f"Imported {len(structure)} Redspot structure and shield recordings")
        return
    if args.base_sounds:
        base = import_base_audio()
        merge_manifest(base)
        print(f"Imported {len(base)} Redspot base recordings")
        return
    weapons = json.loads((SOURCE / "server/weapons.json").read_text(encoding="utf-8"))
    if len(weapons) != 80:
        raise ValueError("Unexpected Redspot weapon registry size")
    for identifier, source in weapons.items():
        import_weapon(identifier, source)
    import_ammo(weapons)
    manifest = import_audio(weapons)
    if args.prune:
        print(f"Removed {prune(manifest)} recordings borrowed from Infinite Warfare")
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Imported Redspot weapon definitions, compatible ammunition and {len(manifest)} recordings")


if __name__ == "__main__":
    main()
