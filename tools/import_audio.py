"""Import recordings into sounds/ from the reference libraries.

Every import is declared in a table: destination, source, and what to do to it.
That matters more than it sounds. The three worst audio defects this project
has had were all import accidents -- a rap emote imported over a shotgun, a
five-second peak-level clip used as a UI cue, and eight footstep variants
numbered six to thirteen so nothing ever found step one -- and all three are
the kind of thing you only catch if the import is written down somewhere you
can read it back.

So: nothing is copied by hand, every destination is loudness-normalized to the
same target, and the table is written out beside the audio as provenance.

Usage:
    python tools/import_audio.py                 # apply the table
    python tools/import_audio.py --list          # show what it would do
    python tools/import_audio.py --force         # redo imports already present
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOUNDS = ROOT / "sounds"
TABLE = ROOT / "tools/audio_import_table.tsv"
PROVENANCE = SOUNDS / "IMPORTED_AUDIO_SOURCES.tsv"

LIBRARIES = {
    "fortnite_weapons": Path(r"C:/Users/gagel/Downloads/Fortnite Weapons"),
    "sandstorm_raw": Path(r"D:/insurgency_sandstorm_soundfiles_(main+1.12-1.13)/Insurgency/Content/WwiseAudio/Windows"),
    "fortnite_items": Path(r"C:/Users/gagel/Downloads/Fortnite Items"),
    "sandstorm": Path(r"D:/insurgency_sandstorm_soundfiles_(main+1.12-1.13)/output"),
    "bf4": Path(r"D:/BF4 Audio_NoVO_NoLevels (by elementofprgress)/BF4 Audio"),
    "bfv": Path(r"D:/BFV Alpha Audio"),
    "bf2042": Path(r"D:/battlefield2042"),
    "bf4ui": Path(r"D:/BF4 Audio_NoVO_NoLevels (by elementofprgress)/BF4 Audio/Sound/UI"),
    "i2": Path(r"C:/i2sound"),
    "cod4ui": Path(r"D:/Call of Duty 4 - Modern Warfare .FF Files/Call of Duty 4 Modern Warfare Sound, VO & Music/.FF Files/user_interface"),
    "mw2ui": Path(r"D:/Call of Duty - Modern Warfare 2 .FF Files/Call of Duty - Modern Warfare 2 Sound, VO & Music/.FF Files/user_interface"),
    "mw3ui": Path(r"D:/Call of Duty - Modern Warfare 3 .FF Files/Call of Duty - Modern Warfare 3 Sound, VO & Music/.FF Files/user_interface"),
    "bf2042ui": Path(r"D:/battlefield2042/2042_20260213/2042/Common/Sound/UI"),
    "halo5ui": Path(r"D:/Halo 5_Ultimate_Sound_Pack_V4.2/User_Interface"),
    "doki": Path(r"D:/Doki Doki UI Sounds/Doki Doki UI Sounds"),
    "sandstorm_menu": Path(r"D:/insurgency_sandstorm_soundfiles_(main+1.12-1.13)/Insurgency/Content/WwiseAudio/Windows/sandstorm_menu_sounds"),
    # The game's own recordings, for when the right sound already exists and
    # only its level or length is wrong.
    "game": ROOT / "sounds",
}

# Everything the game plays is mixed against everything else, so everything
# imported arrives at the same loudness. -18 LUFS with 2 dB of true-peak
# headroom is the target the weapon draws were normalized to in 0.5.1.1.
LOUDNESS = "I=-18:TP=-2:LRA=11"


def ffmpeg(args):
    result = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:400])


def resolve(spec):
    library, _, relative = spec.partition(":")
    if library not in LIBRARIES:
        raise KeyError(f"unknown library {library!r}")
    path = LIBRARIES[library] / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def do_copy(entry, destination):
    source = resolve(entry["source"])
    filters = f"loudnorm={LOUDNESS}"
    if entry.get("gain"):
        filters += f",volume={entry['gain']}dB"
    args = ["-i", str(source)]
    if entry.get("start"):
        args = ["-ss", entry["start"]] + args
    if entry.get("length"):
        args += ["-t", entry["length"]]
    args += ["-af", filters, "-c:a", "libvorbis", "-q:a", "6", "-ac", "1", str(destination)]
    ffmpeg(args)


def do_concat(entry, destination):
    sources = [resolve(s.strip()) for s in entry["source"].split("|")]
    args = []
    for s in sources:
        args += ["-i", str(s)]
    chain = "".join(f"[{i}:a]" for i in range(len(sources)))
    filters = f"{chain}concat=n={len(sources)}:v=0:a=1[c];[c]loudnorm={LOUDNESS}[out]"
    args += ["-filter_complex", filters, "-map", "[out]",
             "-c:a", "libvorbis", "-q:a", "6", "-ac", "1", str(destination)]
    ffmpeg(args)



# Interface cues are measured differently from everything else. Loudness
# normalization integrates over several seconds and a menu tick lasts fifty
# milliseconds, so the measured level of a click is mostly the measured level of
# nothing. Cues are instead matched on their mean level while sounding, with the
# silence either side cut off first, and capped in length: a cue you have to
# wait for before pressing the next key is a cue that is in the way.
CUE_MEAN = -20.0


# Six, not three: Vorbis adds about three decibels of overshoot to a sharp
# transient, so a click limited at -3 dB before encoding decodes at full scale.
CUE_PEAK = -6.0


def measure(path, trim_below=None):
    """Mean and peak level in dBFS, optionally with leading silence removed."""
    chain = "volumedetect"
    if trim_below is not None:
        chain = f"silenceremove=start_periods=1:start_threshold={trim_below}dB," + chain
    result = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", chain,
                             "-f", "null", "-"], capture_output=True, text=True)
    mean = peak = None
    for line in result.stderr.splitlines():
        if "mean_volume:" in line:
            mean = float(line.split("mean_volume:")[1].split("dB")[0])
        if "max_volume:" in line:
            peak = float(line.split("max_volume:")[1].split("dB")[0])
    if mean is None or peak is None:
        raise RuntimeError(f"could not measure {path}")
    return mean, peak


def do_cue(entry, destination):
    source = resolve(entry["source"])
    _, raw_peak = measure(source)
    # Silence is judged against the sound's own peak, not against an absolute
    # floor: a quiet recording of a click is still a click, and a fixed -50 dB
    # threshold trimmed the whole of one away.
    floor = raw_peak - 45.0
    mean, peak = measure(source, trim_below=floor)
    target = float(entry.get("level", CUE_MEAN))
    # Match the mean, but never at the price of the peak. Pushing a thin click
    # up to a loud mean lands it in the limiter and it comes out as a crack.
    gain = min(target - mean, CUE_PEAK - peak)
    length = entry.get("length", "1.2")
    filters = (f"silenceremove=start_periods=1:start_threshold={floor}dB,"
               f"atrim=0:{length},volume={gain:.2f}dB,"
               # ffmpeg's limiter re-normalizes its output to full scale unless
               # told not to, which is how the first pass made every cue crack.
               "alimiter=limit=0.5:attack=0.1:release=20:level=disabled")
    fade = entry.get("fade")
    if fade:
        filters += f",afade=t=out:st={max(float(length) - float(fade), 0):.3f}:d={fade}"
    ffmpeg(["-i", str(source), "-af", filters, "-c:a", "libvorbis", "-q:a", "6",
            "-ac", "1", str(destination)])


OPERATIONS = {"copy": do_copy, "concat": do_concat, "cue": do_cue}


def table():
    """destination -> how to make it.

    `source` is `library:relative/path`, or several of those separated by `|`
    for a concat. `why` is written into the provenance file and is the only
    record of what a recording is doing in this game.
    """
    fw = "fortnite_weapons"
    fi = "fortnite_items"
    ss = "sandstorm"
    br = "modes/battle_royale"
    rows = [
        # --- the DR Resonance Projector had a fire sound and nothing else ----
        dict(dest="er_drgundraw.ogg", op="copy",
             source=f"{fw}:{br}/Assault Weapons/Pulse Rifle/Pulse Rifle (Equip).ogg",
             why="energy weapon brought up; the projector had no draw at all"),
        dict(dest="er_drgunholster.ogg", op="copy",
             source=f"{fw}:{br}/Submachine Guns/Kymera Ray Gun/Kymera Ray Gun (Drop 01).ogg",
             why="energy weapon put away"),
        dict(dest="er_drgunempty.ogg", op="copy",
             source=f"{fw}:{br}/Assault Weapons/Pulse Rifle/Pulse Rifle (Shoot - Low Ammo).ogg",
             why="energy weapon out of charge"),
        dict(dest="er_drgunreload.ogg", op="concat",
             source=(f"{fw}:LTM_weapons/Marvel/Stark Industries Energy Rifle/Stark Industries Energy Rifle (Reload - Start).ogg|"
                     f"{fw}:LTM_weapons/Marvel/Stark Industries Energy Rifle/Stark Industries Energy Rifle (Reload - Insert).ogg|"
                     f"{fw}:LTM_weapons/Marvel/Stark Industries Energy Rifle/Stark Industries Energy Rifle (Reload - End).ogg"),
             why="one continuous cell change, built from the three stages"),
        dict(dest="er_drgunreloadend.ogg", op="copy",
             source=f"{fw}:LTM_weapons/Marvel/Stark Industries Energy Rifle/Stark Industries Energy Rifle (Reload - End).ogg",
             why="the last click of the cell change"),
        dict(dest="er_drgununload.ogg", op="copy",
             source=f"{fw}:LTM_weapons/Marvel/Stark Industries Energy Rifle/Stark Industries Energy Rifle (Reload - Start).ogg",
             why="cell taken back out"),
        dict(dest="er_drgundist.ogg", op="copy",
             source=f"{fw}:{br}/Assault Weapons/Pulse Rifle/Pulse Rifle (Shoot - Hipfire - Distant 01).ogg",
             why="the projector heard from across a street"),
        # --- the service pistol could be holstered but not drawn -------------
        dict(dest="er_service_pistoldraw.ogg", op="copy",
             source=f"{fw}:{br}/Pistols/Ranger Pistol/Ranger Pistol (Equip 01).ogg",
             why="sidearm brought up; it had a holster sound and no draw"),
        # --- the bottle could be drawn but not put away ----------------------
        dict(dest="er_glass_bottleholster.ogg", op="copy",
             source=f"{ss}:Weapon_M9/handling/m9_foley_mag_out_arm_movement.wav",
             why="cloth and arm movement; a bottle going away makes no mechanism noise"),
        # --- the chainsaw had every sound except starting it ------------------
        dict(dest="chainsawreload.ogg", op="concat",
             source=(f"{ss}:Weapon_M249/handling/m249_foley_foley_belt_pull.wav|"
                     f"{ss}:Weapon_M249/handling/m249_foley_boltcharge.wav"),
             why="pull start: handling foley standing in for a two-stroke prime"),
    ]
    return rows



# ---------------------------------------------------------------------------
# The rest of the table is derived rather than written out, because a hundred
# and eight hand-written rows is a hundred and eight chances to paste the wrong
# path. Each weapon class says what its own mechanism sounds like, and the
# generator fills in whichever of those recordings the audit says is silent.

SS = "sandstorm"
FW = "fortnite_weapons"
BR = "modes/battle_royale"
PHYSICS = "sandstorm_raw:Physics"

# class -> what the last motion of a reload is on that kind of weapon.
RELOAD_END = {
    "pistol": f"{SS}:Weapon_M1911/handling/m1911_foley_slide_release.wav",
    "revolver": f"{SS}:Weapon_MR73/handling/MR73_foley_close_chamber.wav",
    "assault_rifle": f"{SS}:Weapon_M16A4/handling/m16_foley_boltrelease.wav",
    "battle_rifle": f"{SS}:Weapon_FnFal/handling/fal_foley_charging_handle_release.wav",
    "submachine_gun": f"{SS}:Weapon_MP5/handling/mp5_foley_bolt_unlock.wav",
    "light_machine_gun": f"{SS}:Weapon_M249/handling/m249_foley_lid_close.wav",
    "shotgun": f"{SS}:Weapon_Model870/handling/model870_foley_close_slide.wav",
    "sniper_rifle": f"{SS}:Weapon_M24/handling/m24_foley_bolt_forward_reload_end.wav",
    "grenade_launcher": f"{SS}:Weapon_M79/handling/m79_foley_breach_close.wav",
    "explosive": f"{SS}:Weapon_M79/handling/m79_foley_breach_close.wav",
    "energy": f"{FW}:LTM_weapons/Marvel/Stark Industries Energy Rifle/Stark Industries Energy Rifle (Reload - End).ogg",
    "archery": f"{SS}:Weapon_M24/handling/m24_foley_bolt_latch.wav",
    "tool": f"{SS}:Weapon_MP5/handling/mp5_foley_bolt_lock.wav",
}

# class -> taking the feed device back out again.
UNLOAD = {
    "pistol": f"{SS}:Weapon_M1911/handling/m1911_foley_mag_out.wav",
    "revolver": f"{SS}:Weapon_MR73/handling/MR73_foley_open_chamber.wav",
    "assault_rifle": f"{SS}:Weapon_M16A4/handling/m16_foley_mag_out.wav",
    "battle_rifle": f"{SS}:Weapon_FnFal/handling/fal_foley_mag_out.wav",
    "submachine_gun": f"{SS}:Weapon_MP5/handling/mp5_foley_mag_out.wav",
    "light_machine_gun": f"{SS}:Weapon_M249/handling/m249_foley_lid_open.wav",
    "shotgun": f"{SS}:Weapon_Model870/handling/model870_foley_open_slide.wav",
    "sniper_rifle": f"{SS}:Weapon_M24/handling/m24_foley_bolt_back.wav",
    "grenade_launcher": f"{SS}:Weapon_M79/handling/m79_foley_shell_out.wav",
    "explosive": f"{SS}:Weapon_M79/handling/m79_foley_shell_out.wav",
    "energy": f"{FW}:LTM_weapons/Marvel/Stark Industries Energy Rifle/Stark Industries Energy Rifle (Reload - Start).ogg",
    "archery": f"{SS}:Weapon_M24/handling/m24_foley_bolt_unlatch.wav",
    "tool": f"{SS}:Weapon_MP5/handling/mp5_foley_bolt_lock.wav",
}

# class -> one detent of the fire selector.
SELECTOR = {
    "pistol": f"{SS}:Weapon_M1911/handling/m1911_foley_safety.wav",
    "revolver": f"{SS}:Weapon_M1911/handling/m1911_foley_safety.wav",
    "assault_rifle": f"{SS}:Weapon_M16A4/handling/m16_foley_fire_select.wav",
    "battle_rifle": f"{SS}:Weapon_M16A4/handling/m16_foley_fire_select.wav",
    "submachine_gun": f"{SS}:Weapon_MP5/handling/mp5_foley_fire_select.wav",
    "light_machine_gun": f"{SS}:Weapon_M16A4/handling/m16_foley_fire_select.wav",
    "shotgun": f"{SS}:Weapon_Model870/handling/model870_foley_safety.wav",
    "sniper_rifle": f"{SS}:Weapon_M24/handling/m24_foley_safety.wav",
    "grenade_launcher": f"{SS}:Weapon_M79/handling/m79_foley_breach_unlock.wav",
    "explosive": f"{SS}:Weapon_M79/handling/m79_foley_breach_unlock.wav",
    "energy": f"{FW}:{BR}/Assault Weapons/Pulse Rifle/Pulse Rifle (ADS - In).ogg",
    "archery": f"{SS}:Weapon_M24/handling/m24_foley_safety.wav",
    "tool": f"{SS}:Weapon_MP5/handling/mp5_foley_fire_select.wav",
}

# How many detents each mode is, counting from the safe position. This is the
# one piece of invention here and it earns its place: you can tell which mode
# the selector just landed on by counting the clicks, without being told.
MODE_CLICKS = {"semi-automatic": 1, "burst": 2, "full automatic": 3,
               "scattershot": 2, "focused": 1}

# Bullets going into people. Ten recordings, handed out by a hash of the
# profile so a given weapon always sounds the same and two weapons rarely
# sound alike.
FLESH = [f"{PHYSICS}/flesh_bullet_impact_{n:02d}.ogg" for n in range(1, 11)]
ENERGY_IMPACT = [
    f"{FW}:{BR}/Submachine Guns/Kymera Ray Gun/Kymera Ray Gun (Impact {n:02d}).ogg"
    for n in range(1, 13)
]
BLAST_IMPACT = [
    f"{FW}:{BR}/Explosive Weapons/Rocket Launcher/Rocket Launcher (v11.00 - Explosion - Close 0{n}).ogg"
    for n in range(1, 4)
]


def derived_table(missing):
    """`missing` is [(profile, wclass, suffix)] from the audit."""
    rows = []
    for profile, wclass, suffix in missing:
        key = wclass if wclass in RELOAD_END else "tool"
        seed = sum(ord(c) for c in profile)
        if suffix == "reloadend.ogg":
            rows.append(dict(dest=profile + suffix, op="copy", source=RELOAD_END[key],
                             why=f"last motion of a {wclass or 'weapon'} reload"))
        elif suffix == "unload.ogg":
            rows.append(dict(dest=profile + suffix, op="copy", source=UNLOAD[key],
                             why=f"feed device out of a {wclass or 'weapon'}"))
        elif suffix.startswith("mode_"):
            mode = suffix[5:-4]
            clicks = MODE_CLICKS.get(mode, 1)
            rows.append(dict(dest=profile + suffix, op="concat",
                             source="|".join([SELECTOR[key]] * clicks),
                             why=f"selector to {mode}: {clicks} detent"
                                 + ("s" if clicks > 1 else "")))
        elif suffix.startswith("hit"):
            index = int(suffix[3]) - 1
            if wclass == "energy":
                bank = ENERGY_IMPACT
            elif wclass in ("explosive", "grenade_launcher"):
                bank = BLAST_IMPACT
            else:
                bank = FLESH
            rows.append(dict(dest=profile + suffix, op="copy",
                             source=bank[(seed + index) % len(bank)],
                             why="round into a body"
                                 if bank is FLESH else "round into a target"))
    return rows


def audit_gaps():
    """Ask the audit what is silent, in the form the generator wants."""
    sys.path.insert(0, str(ROOT / "tools"))
    import audit_sounds

    have = {p.relative_to(SOUNDS).as_posix().lower() for p in SOUNDS.rglob("*")
            if p.is_file() and p.suffix.lower() in (".ogg", ".wav", ".flac", ".mp3")}
    gaps = []
    for w in audit_sounds.parse_weapons().values():
        contract = list(audit_sounds.MELEE_CONTRACT if w["melee"] else audit_sounds.GUN_CONTRACT)
        if not w["melee"] and w["manual"]:
            contract += audit_sounds.MANUAL_CONTRACT
        if len(w["modes"]) > 1:
            for mode in w["modes"]:
                name = audit_sounds.MODE_NAMES.get(mode, mode)
                contract.append((f"mode_{name}.ogg", "required"))
        for suffix, severity in contract:
            if severity != "required":
                continue
            if (w["profile"] + suffix).lower() in have:
                continue
            gaps.append((w["profile"], "melee" if w["melee"] else w["class"], suffix))
    # A profile can be shared by several weapons; import it once.
    return sorted(set(gaps))



def load_table():
    """The table is a file, not a computation.

    It was a computation to begin with -- work out what is silent, then fill
    it -- and that is exactly wrong for a record: the moment an import
    succeeds, the gap closes and the row that explains where the recording came
    from disappears with it. Deriving new rows is a separate, explicit step.
    """
    if not TABLE.is_file():
        return []
    rows = []
    with TABLE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            entry = dict(dest=row["destination"], op=row["operation"],
                         source=row["source"], why=row["why"])
            for pair in (row.get("options") or "").split(";"):
                if "=" in pair:
                    key, _, value = pair.partition("=")
                    entry[key.strip()] = value.strip()
            rows.append(entry)
    return rows


OPTION_KEYS = ("level", "length", "fade", "gain", "start")


def save_table(rows):
    with TABLE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["destination", "operation", "source", "why", "options"])
        for row in sorted(rows, key=lambda r: r["dest"]):
            options = ";".join(f"{k}={row[k]}" for k in OPTION_KEYS if row.get(k))
            writer.writerow([row["dest"], row["op"], row["source"], row["why"], options])


def merge(existing, additions):
    seen = {row["dest"] for row in existing}
    return existing + [row for row in additions if row["dest"] not in seen]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="show the table and stop")
    parser.add_argument("--force", action="store_true", help="redo imports already present")
    parser.add_argument("--derive", action="store_true",
                        help="look for newly silent actions and add them to the table")
    args = parser.parse_args()

    rows = load_table()
    if args.derive:
        rows = merge(rows, table() + derived_table(audit_gaps()))
        save_table(rows)
        print(f"table now holds {len(rows)} imports")
    if args.list:
        for entry in rows:
            mark = "have" if (SOUNDS / entry["dest"]).is_file() else "MISSING"
            print(f"{mark:<8} {entry['dest']:<36} {entry['op']:<7} {entry['source'][:90]}")
        return 0

    for name, path in LIBRARIES.items():
        if not path.is_dir():
            print(f"note: library {name} is not mounted at {path}")

    done, skipped, failed = 0, 0, 0
    written = []
    for entry in rows:
        destination = SOUNDS / entry["dest"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_file() and not args.force:
            skipped += 1
            written.append(entry)
            continue
        try:
            OPERATIONS[entry["op"]](entry, destination)
        except Exception as error:  # noqa: BLE001 - report and carry on
            failed += 1
            print(f"FAILED {entry['dest']}: {error}")
            continue
        done += 1
        written.append(entry)
        print(f"imported {entry['dest']}")

    # The provenance shipped beside the audio is the whole table, not just
    # what this run happened to touch.
    shutil.copyfile(TABLE, PROVENANCE)

    print(f"\n{done} imported, {skipped} already present, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
