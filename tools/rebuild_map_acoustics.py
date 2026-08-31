"""Rebuild acoustic spaces and doorway portals for legacy IW maps.

The old maps predate independent acoustics. Their carefully authored zones are
used as the migration source: indoor names become enclosing spaces, exterior
names become open spaces, and every door/entrance zone becomes a portal.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "iwserver" / "content" / "maps"
INDOOR = ("room", "hall", "corridor", "office", "shop", "bank", "bunker",
          "interior", "cabin", "station", "temple", "warehouse", "hangar",
          "tunnel", "cave", "house", "apartment", "cathedral", "library",
          "clinic", "diner", "kitchen", "bedroom", "bathroom", "attic")
PORTAL = ("door", "entrance", "gateway", "airlock", "hatch")
OBJECT_ZONE = ("on top of", " wall", "railing", "desk", "chair", "table",
               "counter", "bed", "shelf", "crate", "panel", "ladder",
               "stairs", "roof", "window", "curb", "pavement", "sidewalk")


def classify(name, tile_hint=""):
    low = name.lower()
    enclosed = any(word in low for word in INDOOR)
    if "cave" in low: kind, material = "cave", "rock"
    elif "bunker" in low or "tunnel" in low: kind, material = "bunker", "stone"
    elif "corridor" in low or "hallway" in low: kind, material = "corridor", "concrete"
    elif "hangar" in low: kind, material = "hangar", "metal"
    elif "warehouse" in low: kind, material = "warehouse", "concrete"
    elif "street" in low or "road" in low or "avenue" in low: kind, material = "street", "concrete"
    elif "water" in low or "canal" in low or "sea" in low: kind, material = "water", "water"
    elif "grass" in low or "field" in low or "garden" in low: kind, material = "field", "grass"
    else: kind, material = ("room", "concrete") if enclosed else ("open", "ground")
    return enclosed, kind, material


def rebuild(path):
    raw = path.read_text(encoding="utf-8-sig").splitlines()
    base = [line for line in raw if not line.startswith(("space:", "openspace:", "portal:"))
            and line != "// Generated acoustic and occlusion layer"]
    while base and base[-1] == "":
        base.pop()
    records = []
    maxx = maxy = 100
    maxz = 30
    for line in base:
        if line.startswith("maxx:"): maxx = int(line.split(":", 1)[1])
        elif line.startswith("maxy:"): maxy = int(line.split(":", 1)[1])
        elif line.startswith("maxz:"): maxz = int(line.split(":", 1)[1])
    map_label = path.parent.name.replace("_", " ")
    records.append(f"openspace:0:{maxx}:0:{maxy}:-30:{maxz}:{map_label}:ground:open")
    for line in base:
        if not line.startswith("zone:"):
            continue
        p = line.split(":", 7)
        if len(p) < 8:
            continue
        coords, name = p[1:7], p[7]
        if any(word in name.lower() for word in OBJECT_ZONE):
            continue
        enclosed, kind, material = classify(name)
        if enclosed:
            records.append(":".join(["space", *coords, name, material, kind]))
        if any(word in name.lower() for word in PORTAL):
            records.append(":".join(["portal", *coords, name, "opening"]))
    base.extend(["", "// Generated acoustic and occlusion layer", *records])
    path.write_text("\n".join(base) + "\n", encoding="utf-8")
    return len(records)


if __name__ == "__main__":
    for map_path in sorted(ROOT.rglob("*.map")):
        if "battlegrounds" in map_path.parts:
            continue  # Shattersea's source generator authors richer spaces.
        print(f"{map_path.relative_to(ROOT)}: {rebuild(map_path)} acoustic records")
