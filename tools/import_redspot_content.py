"""Import Redspot weapon definitions and their own recorded sound lifecycle.

Run from this checkout with the original Redspot source tree available at
REDSPOT_SOURCE (or the sibling Downloads/redspot_old location). The source
weapon JSON remains authoritative; this script never overwrites existing
Infinite Warfare receivers or recordings.
"""
from __future__ import annotations

import json
import os
import shutil
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


def import_audio(weapons: dict) -> None:
    manifest = []
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
        # Redspot did not record every sound event this client's weapon
        # lifecycle plays. Supply each missing event from a matching existing
        # Infinite Warfare profile so drawing, empty firing and unloading are
        # always audible. Keep the fallback provenance in the same manifest.
        melee = weapons[identifier]["category"] == "melee"
        fallback = "machete" if melee else "glock17"
        for suffix in ("draw", "fire1", "hit1", "holster") if melee else (
            "draw", "fire1", "hit1", "reload", "empty", "holster",
            "reloadend", "unload"):
            destination = SOUNDS / (identifier + suffix + ".ogg")
            source = SOUNDS / (fallback + suffix + ".ogg")
            if not source.exists() and suffix == "hit1":
                source = SOUNDS / (fallback + "hit.ogg")
            if not source.exists():
                raise FileNotFoundError(source)
            if not destination.exists():
                shutil.copy2(source, destination)
            if not (directory / (suffix + ".ogg")).exists():
                manifest.append({"destination": destination.name,
                                 "source": "Infinite Warfare sounds/" + source.name})
        if weapons[identifier]["category"] == "shotgun" or identifier == "m79_grenade_launcher" or identifier == "sky_429_laser_shotgun":
            for suffix in ("reload_open", "reload_insert", "reload_close"):
                destination = SOUNDS / (identifier + suffix + ".ogg")
                source = SOUNDS / ("benelli_m4_shotgun" + suffix + ".ogg")
                if not destination.exists():
                    shutil.copy2(source, destination)
                if not (directory / (suffix + ".ogg")).exists():
                    manifest.append({"destination": destination.name,
                                     "source": "Infinite Warfare sounds/" + source.name})
        if identifier == "t1_rocket_launcher":
            for suffix in ("hit2", "hit3"):
                destination = SOUNDS / (identifier + suffix + ".ogg")
                if not destination.exists():
                    source = SOUNDS / (identifier + "hit1.ogg")
                    shutil.copy2(source, destination)
                if not (directory / (suffix + ".ogg")).exists():
                    manifest.append({"destination": destination.name,
                                     "source": str((directory / "hit1.ogg").relative_to(SOURCE))})
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
        for event in ("draw", "empty", "holster", "reload", "reloadend", "unload"):
            source = SOUNDS / ("crossbow" + event + ".ogg")
            destination = SOUNDS / f"redspot_{identifier}_projectile{event}.ogg"
            if not destination.exists():
                shutil.copy2(source, destination)
            manifest.append({"destination": destination.name,
                             "source": "Infinite Warfare sounds/" + source.name})
    robot_sounds = SOUNDS / "redspot_robot"
    robot_sounds.mkdir(exist_ok=True)
    for event, original in {"activate": "robotstart", "fly": "robotstart",
                            "fire": "robotfire", "impact1": "robothit1",
                            "impact2": "robothit2", "impact3": "robothit3"}.items():
        source = SOURCE / "sounds" / f"{original}.ogg"
        destination = robot_sounds / f"{event}.ogg"
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": str(destination.relative_to(SOUNDS)).replace("\\", "/"),
                         "source": str(source.relative_to(SOURCE))})
    for event, original in (("start", "itemgrabberstart"), ("fire", "itemgrabberfire")):
        source = SOURCE / "sounds" / f"{original}.ogg"
        destination = SOUNDS / f"redspot_item_grabber_{event}.ogg"
        if not destination.exists():
            shutil.copy2(source, destination)
        manifest.append({"destination": destination.name,
                         "source": str(source.relative_to(SOURCE))})
    for event, original in (("explode", "corpse_bomb"), ("dist", "mass_bombdist")):
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
    (SOUNDS / "REDSPOT_AUDIO_SOURCES.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    weapons = json.loads((SOURCE / "server/weapons.json").read_text(encoding="utf-8"))
    if len(weapons) != 80:
        raise ValueError("Unexpected Redspot weapon registry size")
    for identifier, source in weapons.items():
        import_weapon(identifier, source)
    import_ammo(weapons)
    import_audio(weapons)
    print("Imported Redspot weapon definitions, compatible ammunition and sound recordings")


if __name__ == "__main__":
    main()
