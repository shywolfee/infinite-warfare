"""Install Redspot explosives supported by IW's ballistic blast simulation."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path.home() / "Downloads/redspot_old/redspot_old/redspot-main/sounds"
ITEMS = ROOT / "iwserver/content/items/explosives"
OFFERS = ROOT / "iwserver/content/marketplace/explosives"
SOUNDS = ROOT / "sounds"

# kind, price, damage, radius, fuse/arming, payload, launch/place sound,
# detonation sound, distant sound, extra properties.
CONTENT = {
    "match": ("thrown", 1, 5, 1, 700, "incendiary", "match_throw", "match_fire", "fire_bombdist", {"launch_speed": 4, "cloud_ms": 20000, "cloud_radius": 1.5}),
    "hand_grenade": ("thrown", 25, 380, 5, 2500, "", "grenadethrow", "grenadeexplode", "grenadedist", {}),
    "pipe_bomb": ("thrown", 50, 500, 7, 5000, "", "pipebombthrow", "pipebombfire", "pipebombdist", {}),
    "bottle_bomb": ("thrown", 25, 800, 7, 6500, "", "bottle_bombthrow", "bottle_bomb", "bottle_bombdist", {"launch_speed": 22}),
    "sticky_bomb": ("thrown", 25, 550, 7, 5000, "", "sticky_bombthrow", "sticky_bombfire", "sticky_bombdist", {"sticky": "true"}),
    "sound_grenade": ("thrown", 70, 0, 8, 2500, "deafen", "sound_grenadethrow", "sound_grenadeexplode", "sound_grenadedist", {"effect_duration_ms": 10000}),
    "fire_bomb": ("thrown", 50, 220, 6, 2800, "incendiary", "fire_bombthrow", "fire_bomb", "fire_bombdist", {"cloud_ms": 25000, "cloud_radius": 5}),
    "cyanide_canister": ("thrown", 35, 0, 6, 2200, "gas", "canisteruse", "canister", "canisterdist", {"cloud_ms": 25000, "cloud_radius": 6}),
    "teargas_canister": ("thrown", 25, 0, 6, 2200, "gas", "canisteruse", "canister", "canisterdist", {"cloud_ms": 18000, "cloud_radius": 6}),
    "oxygen_canister": ("thrown", 5, 0, 6, 1800, "oxygen", "canisteruse", "canister", "canisterdist", {}),
    "antibiotic_canister": ("thrown", 30, 0, 6, 1800, "antibiotic", "canisteruse", "canister", "canisterdist", {}),
    "mine": ("deployable", 5, 330, 4, 1000, "", "mineplace", "minefire", "minedist", {"sensor_radius": 1.1, "detonate_ms": 3600000}),
    "smart_mine": ("deployable", 50, 450, 5, 1000, "", "smart_mine_use", "smart_mine", "minedist", {"sensor_radius": 1.1}),
    "timebomb": ("deployable", 20, 850, 10, 500, "", "timebombplace", "timebombfire", "timebombdist", {"sensor_kind": "timer", "detonate_ms": 10000}),
    "mass_bomb": ("deployable", 75, 3000, 24, 500, "", "mass_bombplace", "mass_bomb", "mass_bombdist", {"sensor_kind": "timer", "detonate_ms": 10000}),
    "suicide_bomb": ("deployable", 150, 1000, 10, 250, "", "suicide_bombuse", "suicide_bomb", "suicide_bombdist", {"sensor_kind": "timer", "detonate_ms": 700}),
    "barricade_bomb": ("deployable", 75, 4000, 20, 15000, "", "barricade_bombplace", "barricade_bomb", "barricade_bombdist", {"sensor_kind": "delayed", "sensor_radius": 15, "trigger_delay_ms": 3000, "trigger_sound": "redspot_barricade_bomb_beep"}),
    "concussive_grenade": ("deployable", 60, 0, 15, 500, "concussion", "concussive_grenadestart", "concussive_grenade", "concussive_grenadedist", {"sensor_kind": "timer", "detonate_ms": 3000, "effect_duration_ms": 6000}),
    "stun_grenade": ("deployable", 50, 0, 4, 500, "concussion", "stun_grenade_start", "stun_grenade_explode", "stun_grenade_dist", {"sensor_kind": "timer", "detonate_ms": 3000, "effect_duration_ms": 15000}),
    "bullet_bomb": ("deployable", 75, 3000, 12, 3000, "", "bullet_bombplace", "bullet_bomb", "bullet_bombdist", {"sensor_kind": "timer", "shootable": "true", "shoot_health": 500}),
    "dynamite": ("deployable", 50, 1500, 10, 1000, "", "dynamite_place", "dynamite_explode", "dynamite_explodedist", {"sensor_kind": "timer", "shootable": "true", "shoot_health": 100}),
    "dynamite_detonator": ("deployable", 10, 0, 1, 1000, "", "dynamite_detonaterplace", "dynamite_detonate", "dynamite_explodedist", {"sensor_kind": "timer", "shootable": "true", "shoot_health": 50}),
    "satellite_bomb": ("deployable", 35, 3800, 25, 1000, "", "sat_bomb_place", "sat_bomb_explode", "sat_bomb_explode_dist", {"sensor_kind": "timer", "use_kind": "redspot_special_explosive", "blast_damage_min": 1500}),
    "sm2_missile": ("deployable", 50, 1300, 12, 1000, "", "sm2_missile_place", "sm2_missile_explode", "sm2_missile_explodedist", {"sensor_kind": "timer"}),
    "sm2_missile_plate": ("deployable", 10, 0, 1, 1000, "", "sm2_missile_plate_place", "sm2_missile_activate", "sm2_missile_explodedist", {"sensor_radius": 1.2}),
    "redspot_claymore": ("deployable", 75, 1500, 7, 1000, "", "mineplace", "minefire", "minedist", {"sensor_kind": "timer"}),
    "programmable_timebomb": ("deployable", 25, 850, 10, 1000, "", "timebombplace", "timebombfire", "timebombdist", {"sensor_kind": "timer", "use_kind": "redspot_special_explosive"}),
}


def install() -> None:
    provenance = []
    for identifier, (kind, price, damage, radius, delay, payload,
                     launch, detonation, distant, extra) in CONTENT.items():
        name = identifier.replace("_", " ").title()
        props = {"name": name, "category": "Explosives",
                 "summary": f"Redspot {name.lower()} using IW's ballistic blast and payload rules.",
                 "give_amount": 1, "disposable": "true",
                 "use_kind": "redspot_explosive", kind: "true",
                 "blast_damage": damage, "blast_radius": radius,
                 "fragments": 0 if payload else 400,
                 "throw_sound" if kind == "thrown" else "place_sound": f"redspot_{identifier}_launch",
                 "explosion_sound": f"redspot_{identifier}_explode",
                 "distant_sound": f"redspot_{identifier}_dist.ogg",
                 "hit_sound": "fraggrenadehit",
                 "bounce_sound": "fraggrenadeboink",
                 "landing_sound": "fraggrenadeland"}
        if payload:
            props["blast_effect"] = payload
        if kind == "thrown":
            props.update(fuse_ms=delay, fuse_variance_ms=0,
                         flight_loop="explosive_shell_flight_loop.ogg")
        else:
            props["arming_ms"] = delay
        if identifier in {"cyanide_canister", "teargas_canister",
                          "oxygen_canister", "antibiotic_canister"}:
            # Redspot activates canisters at the user's feet; they hiss for
            # TIME_CANISTER (2220 ms) and then burst. They are never thrown.
            for key in ("thrown", "throw_sound", "fuse_ms", "fuse_variance_ms",
                        "flight_loop", "hit_sound", "bounce_sound", "landing_sound"):
                props.pop(key, None)
            props.update(deployable="true", place_sound="canisteruse",
                         detonate_ms=2220)
        if identifier == "satellite_bomb":
            props.update(fragments=0, place_sound="sat_bomb_place",
                         explosion_sound="sat_bomb_explode",
                         distant_sound="sat_bomb_explode_dist.ogg",
                         hit_sound="sat_bomb_impact")
            props.pop("bounce_sound", None)
            props.pop("landing_sound", None)
        if identifier == "sm2_missile":
            props["place_sound"] = "redspot_sm2_missile_place"
        props.update(extra)
        (ITEMS / f"{identifier}.item").write_text(
            "".join(f"{key}={value}\n" for key, value in props.items()), encoding="utf-8")
        (OFFERS / f"{identifier}.offer").write_text(
            f"name={name}\ncategory=Explosives\nsummary={props['summary']}\n"
            f"item={identifier}\nquantity=1\nprice={price}\nmax_order=20\nenabled=true\n",
            encoding="utf-8")
        for event, sound in (("launch", launch), ("explode", detonation), ("dist", distant)):
            source = SOURCE / f"{sound}.ogg"
            target_name = "redspot_sm2_missile_place.ogg" if identifier == "sm2_missile" and event == "launch" else f"redspot_{identifier}_{event}.ogg"
            target = SOUNDS / target_name
            if not target.exists():
                shutil.copy2(source, target)
            provenance.append({"destination": target.name,
                               "source": str(source.relative_to(SOURCE.parent))})
    beep = SOURCE / "barricade_bombbeep.ogg"
    target = SOUNDS / "redspot_barricade_bomb_beep.ogg"
    if not target.exists():
        shutil.copy2(beep, target)
    provenance.append({"destination": target.name,
                       "source": str(beep.relative_to(SOURCE.parent))})
    for destination_name, original in (("redspot_bullet_bomb_hit.ogg", "bullet_bombhit.ogg"),
                                       ("redspot_sm2_missile_launch.ogg", "sm2_missile_launch.ogg")):
        source = SOURCE / original
        target = SOUNDS / destination_name
        if not target.exists():
            shutil.copy2(source, target)
        provenance.append({"destination": target.name,
                           "source": str(source.relative_to(SOURCE.parent))})
    for name in ("canisteruse", "sat_bomb_set", "sat_bomb_remote",
                 "sat_bomb_place", "sat_bomb_impact", "sat_bomb_explode",
                 "sat_bomb_explode_dist"):
        source = SOURCE / f"{name}.ogg"
        target = SOUNDS / source.name
        if not target.exists():
            shutil.copy2(source, target)
        provenance.append({"destination": target.name,
                           "source": str(source.relative_to(SOURCE.parent))})
    (SOUNDS / "REDSPOT_EXPLOSIVE_AUDIO_SOURCES.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    install()
