"""Build missing/duplicated grenade and manual-action audio from local libraries.

This never edits content definitions or unrelated recordings. --plan emits the
proposed data-driven bindings for review; the default imports new audio only.
Targeted --refresh accepts only unchanged outputs owned by its manifest.
Recorded layers are mixed, not pitch-shifted copies used to feign variety.
The source libraries are personal-use inputs, not redistributed by this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOUNDS = ROOT / "sounds"
LIBRARIES = {
    "bf4": Path("D:/BF4 Audio_NoVO_NoLevels (by elementofprgress)/BF4 Audio"),
    "mw2": Path("D:/Call of Duty - Modern Warfare 2 .FF Files/Call of Duty - Modern Warfare 2 Sound, VO & Music/.FF Files"),
    "mw3": Path("D:/Call of Duty - Modern Warfare 3 .FF Files/Call of Duty - Modern Warfare 3 Sound, VO & Music/.FF Files"),
    "sandstorm": Path("D:/insurgency_sandstorm_soundfiles_(main+1.12-1.13)/output"),
    "raw": Path("D:/insurgency_sandstorm_soundfiles_(main+1.12-1.13)/Insurgency/Content/WwiseAudio/Windows"),
    "game": SOUNDS,
}
REVOICE = (
    "airburst_charge", "defensive_fragmentation_grenade", "m67_fragmentation_grenade",
    "mini_impact_charge", "rgd5_grenade", "an_m14_thermite_grenade",
    "cs_riot_grenade", "emp_disruption_grenade", "f1_defensive_grenade",
    "m18_red_smoke_grenade", "m7a3_gas_grenade", "m84_stun_grenade",
    "mk2_pineapple_grenade", "mk3a2_concussion_grenade", "rgd2_impact_grenade",
    "sticky_semtex_charge", "v40_mini_grenade", "molotov_cocktail",
)
ROLES = ("pin_sound", "throw_sound", "bounce_sound", "landing_sound",
         "explosion_sound", "distant_sound", "flight_loop")


def properties(path):
    return dict(line.split("=", 1) for line in path.read_text(encoding="utf-8-sig").splitlines() if "=" in line)


def recording(library, name):
    return f"{library}:{name}"


def raw(name):
    return recording("raw", "Weapon_Explosives/" + name + ".ogg")


def plan():
    bindings, jobs = {}, []

    def job(item, role, sources, operation="mix", gain=0):
        dest = f"{item}_audio_{role.removesuffix('_sound')}.ogg"
        jobs.append(dict(destination=dest, role=role, sources=sources,
                         operation=operation, gain=gain))
        return dest if role in {"flight_loop", "distant_sound"} else dest[:-4]

    for index, path in enumerate(sorted(p for p in (ROOT / "iwserver/content/items").rglob("*.item") if not p.stem.startswith("ars_"))):
        props = properties(path)
        if props.get("thrown") != "true":
            continue
        item = path.stem
        if item.startswith("ars_"):
            continue  # Owned and validated by the expanded arsenal importer.
        # Pin and throw are separate events. Do not replay a pin pull on release.
        pin = recording("bf4", f"Sound/Weapons/Handheld/M67/M67_Remove_Safety_Pin_Wave 0 0 {index % 5}.wav")
        pin_sources = [pin]
        if item == "molotov_cocktail":
            pin_sources = [recording("raw", "sandstorm_character_foli/molotov_lighter_open.ogg"), recording("raw", "sandstorm_character_foli/molotov_lighter_strike.ogg")]
        bindings[str(path.relative_to(ROOT)).replace("\\", "/")] = {
            "pin_sound": job(item, "pin_sound", pin_sources, "concat" if len(pin_sources)>1 else "mix")}
        target = bindings[str(path.relative_to(ROOT)).replace("\\", "/")]
        if item not in REVOICE:
            continue
        n = REVOICE.index(item)
        throw = recording("bf4", f"Sound/Weapons/Handheld/M67/M67_Throw_Wave {n % 4} 0 0.wav")
        if item == "molotov_cocktail":
            throw = recording("raw", "sandstorm_character_foli/molotov_throw_burning.ogg")
        bounce = recording("raw", f"Physics/grenade_bounce_{n % 6 + 1:02}.ogg")
        landing = raw(f"grenade_bounce_surface_dirt_{n % 6 + 1:02}")
        loop = recording("bf4", "Sound/Weapons/Projectiles/40mm_Projectile_loop_Wave 0 0 0.wav")
        effect = props.get("blast_effect", "blast")
        # Payload identity comes from real detonation recordings, never a mortar
        # boom for smoke, a fragmentation blast for fire, or a blast used as a loop.
        if effect == "flash":
            close = [raw(f"exp_flashbang_core_close_{n % 6 + 1:02}"), raw(f"exp_flashbang_tail_close_{n % 6 + 1:02}")]
            distant = [raw(f"exp_flashbang_core_indoor_distant_{n % 6 + 1:02}")]
        elif effect in {"smoke", "gas"}:
            close = [recording("bf4", f"Sound/Weapons/Handheld/M18/Smoke_Grenade_Explosion_Close {n % 5} 0 0.wav"), raw("smoke_grenade_burn")]
            distant = [raw(f"smokelauncher_round_explode_distant_{n % 4 + 1:02}")]
            loop = raw("smoke_grenade_burn")
        elif effect in {"thermite", "incendiary"}:
            close = [raw("incendiary_detonate"), raw(f"incendiary_loop_{n % 4 + 1:02}")]
            distant = [recording("bf4", f"Sound/Weapons/Handheld/M34/M34_Ingnition_Wave {n % 3} 0 {n % 2}.wav")]
            loop = raw(f"incendiary_loop_{n % 4 + 1:02}")
            if item == "molotov_cocktail":
                bounce = raw("molotov_glass_break_01")
                landing = raw("molotov_glass_break_02")
                close = [raw("molotov_glass_break_03"), raw("molotov_detonate")]
                distant = [raw("molotov_loop_end")]
                loop = raw("molotov_loop_04")
        elif effect in {"concussion", "emp"}:
            close = [recording("mw3", f"weapons/grenade/grenade_stun_a0{n % 2 + 1}.wav"), raw(f"exp_small_tail_close_{n % 15 + 1:02}")]
            distant = [raw(f"exp_small_core_distant_{n % 16 + 1:02}"), raw(f"exp_small_tail_distant_{n % 16 + 1:02}")]
        else:
            close = [raw(f"exp_small_core_close_{n % 6 + 1:02}"), raw(f"exp_small_tail_close_{n % 15 + 1:02}"), raw(f"shrapnel_debris_{n % 8 + 1:02}")]
            distant = [raw(f"exp_small_core_distant_{n % 16 + 1:02}"), raw(f"exp_small_tail_distant_{n % 16 + 1:02}")]
        # A hand grenade's travel cue is a quiet air passage, not a rocket engine.
        # Physical handling may share recordings between similar grenade bodies;
        # complete payload sets do not. No artificial pitch variation is added.
        target.update({
            "throw_sound": job(item, "throw_sound", [throw]),
            "bounce_sound": job(item, "bounce_sound", [bounce]),
            "landing_sound": job(item, "landing_sound", [landing]),
            "explosion_sound": job(item, "explosion_sound", close),
            "distant_sound": job(item, "distant_sound", distant, gain=-4),
            "flight_loop": job(item, "flight_loop", [loop], "loop", gain=-n * .15-(3 if item=="molotov_cocktail" else 0)),
        })

    for number, item in enumerate(("anti_vehicle_mine", "breaching_charge", "wide_area_sensor_mine")):
        target = {}
        if item == "anti_vehicle_mine":
            place = recording("bf4", "Sound/Weapons/Handheld/AT_Mine/AT_Mine_Drop_Wave 0 0 0.wav")
        elif item == "breaching_charge":
            place = recording("bf4", "Sound/Weapons/Handheld/C4/C4_Explosioves_Throw_Wave 0 1 0.wav")
        else:
            place = recording("bf4", "Sound/Weapons/Handheld/AT_Mine/AT_Mine_Drop_Wave 0 2 0.wav")
        target["place_sound"] = job(item, "place_sound", [place])
        close = recording("bf4", f"Sound/Explosions/ModularModel/Explosion_Detonation/Explosion_Detonations_IED_Close_Wave {number} 0 0.wav")
        distant = recording("bf4", f"Sound/Explosions/ModularModel/Explosion_Detonation/Explosion_Detonations_IED_Distant_Wave {number} 0 0.wav")
        target["explosion_sound"] = job(item, "explosion_sound", [close, raw(f"shrapnel_debris_{number+1:02}")])
        target["distant_sound"] = job(item, "distant_sound", [distant], gain=-4)
        bindings[f"iwserver/content/items/explosives/{item}.item"] = target
    bindings["iwserver/content/items/explosives/directional_mine.item"] = {
        "distant_sound": job("directional_mine", "distant_sound", [raw("exp_small_core_distant_16")], gain=-4)}

    for item, category, rotor in (
        ("auto_hover_drone", "equipment", recording("bf4", "Sound/Vehicles/Air/MAV/MAV_Engine_Close_Wave 0 0 0.wav")),
        ("bomber_hover_drone", "explosives", recording("raw", "Vehicle_Grenade_Drone/drone_strike_flyby_01.ogg")),
    ):
        folder = "weapons/drones/" + item + "_repaired"
        bindings[f"iwserver/content/items/{category}/{item}.item"] = {"companion_sound": folder}
        activate = recording("raw", "Vehicle_Grenade_Drone/drone_strike_grenade_release_01.ogg" if item == "auto_hover_drone" else "Vehicle_Grenade_Drone/drone_strike_grenade_release_02.ogg")
        jobs.append(dict(destination="executioners_rage/"+folder+"/activate.wav", role="handling", sources=[activate], operation="mix", gain=0))
        jobs.append(dict(destination="executioners_rage/"+folder+"/fly.wav", role="movement", sources=[rotor], operation="mix", gain=-3))
        for variant in range(1, 4):
            sources = [recording("raw", f"Physics/flesh_bullet_impact_{variant:02}.ogg")]
            if item == "bomber_hover_drone":
                sources = [raw(f"exp_small_core_close_{variant+3:02}"), raw(f"shrapnel_debris_{variant+3:02}")]
            jobs.append(dict(destination="executioners_rage/"+folder+f"/impact{variant}.wav", role="impact", sources=sources, operation="mix", gain=0))

    # Real cylinder/breech stages replace the silent manual reload paths. Reuse
    # within a firearm family is intentional, not a reason to invent fake foley.
    for profile, variant in (("anaconda_service_pistol", 1), ("anaconda_tactical_pistol", 2), ("mp412_tactical_pistol", 3)):
        for suffix, source in (
            ("reload_open", "MR73_foley_open_chamber.wav"),
            ("reload_insert", f"mr73_foley_round_insert_single_0{variant}.wav"),
            ("reload_close", "MR73_foley_close_chamber.wav"),
        ):
            jobs.append(dict(destination=profile+suffix+".ogg", role="handling", operation="mix", gain=0,
                             sources=[recording("sandstorm", "Weapon_MR73/handling/"+source)]))
    for profile in ("m79_guided_launcher", "m79_infantry_launcher"):
        for suffix, source in (("reload_open", "breach_open"), ("reload_insert", "shell_in"), ("reload_close", "breach_close")):
            jobs.append(dict(destination=profile+suffix+".ogg", role="handling", operation="mix", gain=0,
                             sources=[recording("sandstorm", f"Weapon_M79/handling/m79_foley_{source}.wav")]))
    jobs.append(dict(destination="dao12reload_cycle.ogg", role="handling", operation="mix", gain=0,
                     sources=[recording("sandstorm", "Weapon_MR73/handling/MR73_foley_cock_hammer_01.wav")]))

    # The server selects these hit variants unconditionally, unlike fire sounds
    # which the client enumerates. Missing hit2/hit3 really did produce silence.
    for index, profile in enumerate(("fn_fal_battle_rifle", "scar_h_battle_rifle", "laser_cannon", "laser_pistol",
                                    "laser_smg", "laser_sniper", "desert_eagle", "rpk_lmg", "vehicle_20mm_cannon",
                                    "vehicle_30mm_autocannon", "120mm_mortar", "er_rocket_launcher", "spas_12_shotgun",
                                    "awp_sniper_rifle", "mp7", "uzi", "flamethrower")):
        for variant in (2, 3):
            if profile == "flamethrower" and variant == 2:
                continue
            flesh = recording("raw", f"Physics/flesh_bullet_impact_{(index+variant) % 6+1:02}.ogg")
            sources = [flesh]
            if profile.startswith("laser") or profile == "flamethrower":
                sources = [recording("game", profile+"hit1.ogg"), flesh]
            elif profile in {"120mm_mortar", "er_rocket_launcher", "vehicle_20mm_cannon", "vehicle_30mm_autocannon"}:
                sources = [raw(f"shrapnel_debris_{index % 8+1:02}"), flesh]
            jobs.append(dict(destination=profile+f"hit{variant}.ogg", role="impact", operation="mix", gain=0, sources=sources))
    return dict(bindings=bindings, jobs=jobs)


def resolve(spec):
    library, relative = spec.split(":", 1)
    path = LIBRARIES[library] / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-1500:])
    return result


def render(job, output):
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for source in job["sources"]:
        args.extend(["-i", str(resolve(source))])
    # Equal-power components: detonation at full, reflection at -6 dB, debris
    # at -10 dB, then normalize the whole recording rather than each layer.
    filters = []
    for i in range(len(job["sources"])):
        filters.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=mono,asetpts=PTS-STARTPTS,volume={1 if i == 0 else .5 if i == 1 else .32}[s{i}]")
    if job["operation"] == "concat":
        filters.append("".join(f"[s{i}]" for i in range(len(job["sources"])))+f"concat=n={len(job['sources'])}:v=0:a=1[mix]")
    elif len(job["sources"]) > 1:
        filters.append("".join(f"[s{i}]" for i in range(len(job["sources"])))+f"amix=inputs={len(job['sources'])}:duration=longest:normalize=0[mix]")
    else:
        filters.append("[s0]anull[mix]")
    role = job["role"]
    level = -28 if job["operation"] == "loop" else -16 if role == "explosion_sound" else -20 if role == "distant_sound" else -23
    if job["operation"] == "loop":
        # Rotate a 1.4-second recorded section with a 100ms wrap crossfade.
        # Its new beginning/end meet at the same point in the original audio.
        filters.extend([
            "[mix]apad,atrim=0:1.4,asplit=2[body][tail]",
            "[body]atrim=0:1.3,asetpts=PTS-STARTPTS[b]",
            "[tail]atrim=1.3:1.4,asetpts=PTS-STARTPTS[t]",
            "[t][b]acrossfade=d=0.1:c1=tri:c2=tri[processed]",
        ])
    elif role == "movement":
        filters.append("[mix]apad,atrim=0:2.2,afade=t=in:d=0.04,afade=t=out:st=2.1:d=0.1[processed]")
    else:
        filters.append("[mix]anull[processed]")
    filters.append(f"[processed]loudnorm=I={level}:TP=-3:LRA=7,volume={job['gain']}dB[out]")
    args.extend(["-filter_complex", ";".join(filters), "-map", "[out]", "-ar", "48000"])
    args.extend(["-c:a", "pcm_s16le"] if output.suffix == ".wav" else ["-c:a", "libvorbis", "-q:a", "6"])
    args.append(str(output))
    run(args)
    run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--refresh", action="store_true", help="rebuild only unchanged files owned by the previous repair manifest")
    parser.add_argument("--only", nargs="*", help="limit rendering to these declared destinations")
    args = parser.parse_args()
    planned = plan()
    if args.plan:
        print(json.dumps(planned, indent=2))
        return 0
    if args.only and set(args.only) - {job["destination"] for job in planned["jobs"]}:
        parser.error("--only must name destinations declared in --plan")
    # Preflight every input before producing any outputs.
    for job in planned["jobs"]:
        for source in job["sources"]:
            resolve(source)
    previous_file = SOUNDS / "CONTENT_AUDIO_REPAIR.json"
    previous = json.loads(previous_file.read_text(encoding="utf-8")) if previous_file.exists() else {"jobs": []}
    owned = {job["destination"]: job["sha256"] for job in previous["jobs"]}
    receipts = {job["destination"]: job for job in previous["jobs"]}
    with tempfile.TemporaryDirectory(prefix="IW-audio-repair-") as temporary:
        for job in planned["jobs"]:
            destination = SOUNDS / job["destination"]
            if args.only and job["destination"] not in args.only:
                continue
            if destination.exists() and owned.get(job["destination"]) != hashlib.sha256(destination.read_bytes()).hexdigest():
                raise RuntimeError("Refusing to adopt or replace unowned or locally edited audio: " + str(destination))
            if destination.exists() and not args.refresh:
                if any(receipts[job["destination"]].get(key) != job.get(key) for key in ("sources", "role", "operation", "gain")):
                    raise RuntimeError("Recipe changed; use targeted --refresh for " + job["destination"])
                print("KEEP", job["destination"], flush=True)
                continue
            output = Path(temporary) / destination.name
            render(job, output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            output.replace(destination)
            # Record ownership after each successful import so interrupted runs
            # can resume without adopting an unrelated file with the same name.
            receipts[job["destination"]] = {**job, "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}
            previous_file.write_text(json.dumps({"bindings": planned["bindings"], "jobs": list(receipts.values())}, indent=2)+"\n", encoding="utf-8")
            print("IMPORTED", job["destination"], flush=True)
    # Generated audio provenance, not source-code editing.
    planned["jobs"] = [job for job in planned["jobs"] if (SOUNDS / job["destination"]).exists()]
    for job in planned["jobs"]:
        job["sha256"] = hashlib.sha256((SOUNDS / job["destination"]).read_bytes()).hexdigest()
    (SOUNDS / "CONTENT_AUDIO_REPAIR.json").write_text(json.dumps(planned, indent=2)+"\n", encoding="utf-8")
    (SOUNDS / "CONTENT_AUDIO_REPAIR_FILES.txt").write_text("\n".join(job["destination"] for job in planned["jobs"])+"\n", encoding="utf-8")
    print(f"Verified {len(planned['jobs'])} recordings; bindings cover {len(planned['bindings'])} content entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
