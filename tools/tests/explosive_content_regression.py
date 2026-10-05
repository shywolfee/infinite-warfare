from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEAPONS = ROOT / "iwserver/content/weapons"
ITEMS = ROOT / "iwserver/content/items/explosives"
SOUNDS = ROOT / "sounds"


def properties(path: Path) -> dict[str, str]:
    return {
        line.partition("=")[0]: line.partition("=")[2]
        for line in path.read_text(encoding="utf-8").splitlines()
        if "=" in line
    }


expected_categories = {
    "handguns",
    "grenade_launchers",
    "rocket_launchers",
    "mortars",
    "artillery",
}
assert expected_categories <= {path.name for path in WEAPONS.iterdir() if path.is_dir()}
assert not (WEAPONS / "explosives").exists(), "legacy mixed explosive folder remains"

explosive_weapons = [
    *sorted((WEAPONS / "grenade_launchers").glob("*.wpn")),
    *sorted((WEAPONS / "rocket_launchers").glob("*.wpn")),
    *sorted((WEAPONS / "mortars").glob("*.wpn")),
    *sorted((WEAPONS / "artillery").glob("*.wpn")),
]
required = {
    "projectile_kind",
    "explosive_radius",
    "blast_damage",
    "projectile_loop",
    "explosion_sound",
    "explosion_distant",
    "explosion_impact",
    "kill_label",
}
for path in explosive_weapons:
    props = properties(path)
    assert props.get("projectile_kind") == "shell", f"{path.name}: not a shell"
    assert required <= props.keys(), f"{path.name}: missing {required - props.keys()}"
    assert (SOUNDS / props["projectile_loop"]).is_file(), path.name
    assert (SOUNDS / props["explosion_distant"]).is_file(), path.name
    for key in ("explosion_sound", "explosion_impact"):
        assert (SOUNDS / f"{props[key]}.ogg").is_file(), f"{path.name}: {props[key]}"

new_grenades = {
    "mk3a2_concussion_grenade",
    "m84_stun_grenade",
    "an_m14_thermite_grenade",
    "cs_riot_grenade",
    "sticky_semtex_charge",
    "rgd2_impact_grenade",
    "emp_disruption_grenade",
    "f1_defensive_grenade",
    "v40_mini_grenade",
    "m18_red_smoke_grenade",
    "m7a3_gas_grenade",
    "mk2_pineapple_grenade",
}
for item_id in new_grenades:
    path = ITEMS / f"{item_id}.item"
    props = properties(path)
    assert props.get("thrown") == "true", item_id
    for key in ("flight_loop", "distant_sound"):
        assert (SOUNDS / props[key]).is_file(), f"{item_id}: {props[key]}"
    for key in ("throw_sound", "bounce_sound", "landing_sound", "explosion_sound"):
        assert (SOUNDS / f"{props[key]}.ogg").is_file(), f"{item_id}: {props[key]}"

server_weapon = (ROOT / "iwserver/includes/weapon.nvgt").read_text(encoding="utf-8")
assert "spawn_mortarbomb(w.x,w.y,w.z,w.map,w.cn,w.ammunition);" not in server_weapon
assert "w.projectile_loop" in server_weapon
print(
    f"PASS explosive content: {len(explosive_weapons)} launchers and "
    f"{len(new_grenades)} grenades are fully data-driven"
)
