"""Copy only item-event recordings named by the Redspot gameplay port.

Never substitute another recording when the Redspot source has no event.
The destination manifest records each source path for later audits.
"""
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("REDSPOT_SOURCE", Path.home() / "Downloads/redspot_old/redspot_old/redspot-main")) / "sounds"
DEST = ROOT / "sounds"
MANIFEST = DEST / "REDSPOT_ITEM_AUDIO_SOURCES.json"
PORT_FILES = [ROOT / "iwserver/includes" / name for name in (
    "redspot_items.nvgt", "redspot_bases.nvgt", "redspot_cameras.nvgt",
    "redspot_explosives.nvgt", "redspot_cargo.nvgt")]


def main() -> None:
    names = {"canisteruse", "spring_boots", "spring_bootsjump",
             "spring_bootsland", "spring_bootskill",
             "base_comp_bitcoin_insert", "base_comp_bitcoin_use"}
    for path in PORT_FILES:
        text = path.read_text(encoding="utf-8-sig")
        names.update(re.findall(r'\bplay\("([a-zA-Z0-9_]+)"', text))
        names.update(re.findall(r'play_s ([a-zA-Z0-9_]+)\.ogg', text))
    rows = []
    missing_source = []
    divergent = []
    for name in sorted(names):
        source = SOURCE / f"{name}.ogg"
        if not source.is_file():
            missing_source.append(name)
            continue
        target = DEST / source.name
        if target.exists() and target.read_bytes() != source.read_bytes():
            divergent.append(name)
            continue
        if not target.exists():
            shutil.copy2(source, target)
        rows.append({"destination": source.name, "source": f"sounds/{source.name}"})
    MANIFEST.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"{len(rows)} exact item-event recordings; {len(missing_source)} events absent from Redspot; {len(divergent)} mismatched existing recordings")
    for name in missing_source:
        print(f"NO SOURCE {name}.ogg")
    for name in divergent:
        print(f"MISMATCH {name}.ogg")
    if divergent:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
