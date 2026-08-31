"""Audit literal audio references and exact duplicate assets without altering audio."""
from __future__ import annotations
import hashlib
import re
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOUNDS=ROOT/"sounds"
AUDIO_EXTENSIONS=(".ogg",".wav",".flac",".mp3")
SOURCE_GLOBS=("*.nvgt","*.txt","*.map")

assets={p.name.lower():p for p in SOUNDS.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS}
literal=re.compile(r'["\']([^"\']+\.(?:ogg|wav|flac|mp3))["\']',re.I)
references=defaultdict(list)
dynamic_suffixes={"close.ogg","draw.ogg","empty.ogg","equip.ogg","holster.ogg","land.ogg","open.ogg","reload.ogg","reload_close.ogg","reload_cycle.ogg","reload_insert.ogg","reload_open.ogg","reloadend.ogg","step1.ogg","unequip.ogg","unload.ogg","use.ogg"}
for pattern in SOURCE_GLOBS:
    for path in ROOT.rglob(pattern):
        if any(part in {".git","release","packs"} for part in path.parts):continue
        try:text=path.read_text(encoding="utf-8",errors="ignore")
        except OSError:continue
        for line_no,line in enumerate(text.splitlines(),1):
            for match in literal.finditer(line):
                name=match.group(1).replace("\\","/").split("/")[-1].lower()
                # Ignore packet commands and fragments from concatenated names.
                if " " in name or name.startswith("_") or name in dynamic_suffixes or name=="sound_pack_test.ogg":continue
                references[name].append(f"{path.relative_to(ROOT)}:{line_no}")

missing={name:sites for name,sites in references.items() if name not in assets}
hashes=defaultdict(list)
for path in assets.values():
    digest=hashlib.sha256(path.read_bytes()).hexdigest();hashes[digest].append(path.name)
duplicates=[sorted(names,key=str.lower) for names in hashes.values() if len(names)>1]

print(f"Audio assets: {len(assets)}")
print(f"Literal references: {len(references)}")
print(f"Missing literal assets: {len(missing)}")
for name,sites in sorted(missing.items()):print(f"MISSING {name} <- {', '.join(sites[:5])}")
print(f"Exact duplicate groups: {len(duplicates)}")
for names in sorted(duplicates,key=lambda group:group[0].lower()):print("DUPLICATE "+" | ".join(names))
