"""Regression checks for build 93's Battlefield-derived content expansion."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
VEHICLES = ROOT / "iwserver/content/vehicles"
WEAPONS = ROOT / "iwserver/content/weapons"
EXPLOSIVES = ROOT / "iwserver/content/items/explosives"
SOUNDS = ROOT / "sounds"


def fields(path):
    return dict(line.split("=", 1) for line in path.read_text(encoding="utf-8").splitlines()
                if "=" in line)


vehicle_files = list(VEHICLES.rglob("*.vehicle"))
new_vehicle_names = {
    "Recon Quad ATV", "Utility UTV", "Heavy Cargo Truck", "Armed Technical",
    "Infantry Fighting Vehicle", "Personal Watercraft",
    "Rigid-hull Inflatable Boat", "Armoured Patrol Boat",
    "Light Utility Helicopter", "Attack Helicopter", "Multirole Fighter",
    "Tactical Transport Aircraft",
}
records = {fields(path).get("name"): fields(path) for path in vehicle_files}
assert new_vehicle_names <= records.keys()
assert {records[name]["travel_domain"] for name in new_vehicle_names} == {"land", "water", "air"}
assert records["Multirole Fighter"]["class"] == "fixed_wing"
assert records["Attack Helicopter"]["class"] == "rotary_wing"
assert records["Heavy Cargo Truck"]["cargo_kind"] == "truck bed"
for name in new_vehicle_names:
    record = records[name]
    seats = int(record["seats"])
    assert len(record["seat_roles"].split(",")) == seats
    assert len(record["seat_weapons"].split(",")) == seats
    assert all(float(record[key]) > 0 for key in ("length", "width", "height"))

weapon_ids = ("bar1918", "dao12", "g3a3", "m240b", "ntw20")
for weapon_id in weapon_ids:
    matches = list(WEAPONS.rglob(f"{weapon_id}.wpn"))
    assert len(matches) == 1
    record = fields(matches[0])
    assert record["sound_profile"] == weapon_id
    for suffix in ("fire1.ogg", "fire2.ogg", "fire3.ogg", "dist.ogg", "draw.ogg",
                   "reload.ogg", "empty.ogg", "holster.ogg", "reloadend.ogg",
                   "unload.ogg", "hit1.ogg", "hit2.ogg", "hit3.ogg", "rico.ogg",
                   "supressedfire1.ogg", "supressedfire2.ogg",
                   "supressedfire3.ogg", "supresseddist.ogg"):
        sound = SOUNDS / f"{weapon_id}{suffix}"
        assert sound.stat().st_size > 1000
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name",
             "-of", "default=nw=1:nk=1", str(sound)], capture_output=True, text=True,
            check=True,
        )
        assert "vorbis" in probe.stdout

explosive_ids = {
    "m67_fragmentation_grenade", "rgd5_grenade",
    "defensive_fragmentation_grenade", "mini_impact_charge",
    "anti_vehicle_mine", "wide_area_sensor_mine", "breaching_charge",
    "airburst_charge",
}
for explosive_id in explosive_ids:
    record = fields(EXPLOSIVES / f"{explosive_id}.item")
    assert record["category"] == "Explosives"
    assert "blast_radius" in record and "blast_damage" in record
    assert "thrown" in record or "deployable" in record

print("PASS Battlefield content: 12 vehicles, 5 weapons, 8 explosives and sound sets")
