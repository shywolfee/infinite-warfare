from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
WEAPONS=ROOT/"iwserver/content/weapons"
SOUNDS=ROOT/"sounds"
HEADLINE={"m14_ebr","ump45","pp2000","aa12","cm901","msr","pp90m1","rsass","mg36","stg44","ppsh41","fg42","gewehr43","type100"}
VARIANT_SUFFIXES=("_field_rifle","_modular_rifle","_compact_carbine","_personal_defence_weapon","_precision_rifle","_marksman_system","_support_weapon","_squad_automatic","_service_pistol","_tactical_pistol","_infantry_launcher","_guided_launcher","_underfolder_carbine")

paths={p.stem:p for p in WEAPONS.rglob("*.wpn")}
added=HEADLINE|{wid for wid in paths if wid.endswith(VARIANT_SUFFIXES) and not wid.startswith("er_")}
assert len(added)==90, f"expected 90 release weapons, found {len(added)}"
manifest=SOUNDS/"COD_WEAPON_AUDIO_SOURCES.tsv"
rows=manifest.read_text(encoding="utf-8-sig").splitlines()
assert len(rows)==901, f"expected header plus 900 provenance rows, found {len(rows)}"
for wid in sorted(added):
 props={line.partition("=")[0]:line.partition("=")[2] for line in paths[wid].read_text(encoding="utf-8").splitlines() if "=" in line}
 combined=(wid+" "+props.get("name","")).lower()
 assert "call of duty" not in combined and "modern warfare" not in combined and "cod_" not in combined, wid
 profile=props.get("sound_profile",wid)
 for suffix in ("fire1.ogg","draw.ogg","holster.ogg","empty.ogg","reload.ogg","reloadend.ogg","unload.ogg","hit1.ogg"):
  assert (SOUNDS/(profile+suffix)).is_file(), f"{wid}: missing {profile+suffix}"
print("PASS 0.5.4 weapon pack: 90 plausible firearm variants and complete sound lifecycles")
