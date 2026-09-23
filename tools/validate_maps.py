"""Check the built maps the way the game will read them.

This rasterizes the tiles in the order the map declares them, which is the only
way to catch the mistakes that matter: a doorway sealed by a wall written after
the room, a stair with a two-unit riser in it, a spawn inside a building, an
island nobody can walk to, a patch of floor with no zone on it so walking there
says nothing.

Rectangle-union coverage would pass all of those.
"""
from collections import deque
from math import ceil, floor
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "iwserver/content/maps"
SOUNDS = ROOT / "sounds"
FILES = [
    "freeforall/freeforall.map",
    "battlegrounds/main.map",
    "freyas_ascent/freyas_ascent.map",
    "habitat_alpha/habitat_alpha.map",
]

AIR, FLOOR, SOLID, CLIMB = 0, 1, 2, 3


def _registered_items():
    # Items are data files, one per item, named by id (see content/items).
    names = {path.stem for path in (ROOT / "iwserver/content/items").rglob("*.item")}
    names.update(re.findall(r'content_register\("([^"\n]+)"',
                            (ROOT / "includes/content_database.nvgt").read_text(encoding="utf-8")))
    for weapon in (ROOT / "iwserver/content/weapons").rglob("*.wpn"):
        names.update(re.findall(r"^reserve_item=(.+)$",
                                weapon.read_text(encoding="utf-8"), re.M))
    return names


def _sound_exists(name):
    path = SOUNDS / name
    if path.is_file():
        return True
    return any((SOUNDS / (name + ext)).is_file() for ext in (".ogg", ".wav"))


def _climbable(material):
    m = material.lower()
    return any(w in m for w in ("ladder", "rungs", "climb", "netting", "scaffold"))


def validate(relative, items):
    text = (MAPS / relative).read_text(encoding="utf-8")
    records = [line.split(":") for line in text.splitlines() if line and not line.startswith("//")]
    size = {p[0]: int(p[1]) + 1 for p in records if p[0] in ("maxx", "maxy", "maxz")}
    w, h, depth = size["maxx"], size["maxy"], size["maxz"]
    area = w * h
    grid = [bytearray(area) for _ in range(depth)]
    named = [bytearray(area) for _ in range(depth)]
    errors = []
    surfaces, materials_used = {}, set()
    objects, spawns, pois, fixtures, portals, beds = {}, [], [], [], [], []
    regions = []
    lifts = []

    def paint(target, bounds, value):
        a, b, c, d, e, f = (float(v) for v in bounds)
        a, b, c, d, e, f = ceil(a), floor(b), ceil(c), floor(d), ceil(e), floor(f)
        if a > b or c > d or e > f:
            return
        if not (0 <= a and b < w and 0 <= c and d < h and 0 <= e and f < depth):
            errors.append(f"out-of-bounds rectangle {bounds}")
            return
        stripe = bytes([value]) * (b - a + 1)
        for z in range(e, f + 1):
            row = target[z]
            for y in range(c, d + 1):
                row[y * w + a:y * w + b + 1] = stripe

    for p in records:
        kind = p[0]
        if kind == "surface":
            surfaces[p[1]] = p[2]
        elif kind == "tile":
            material = p[7]
            materials_used.add(material)
            if material == "blank":
                value = AIR
            elif _climbable(material):
                value = CLIMB
            elif "wall" in material or material in ("glass", "tree"):
                value = SOLID
            else:
                value = FLOOR
            paint(grid, p[1:7], value)
        elif kind == "zone":
            paint(named, p[1:7], 1)
        elif kind == "object":
            if int(p[1]) in objects:
                errors.append(f"duplicate object id {p[1]}")
            objects[int(p[1])] = p
            for sound in p[5:7]:
                if not _sound_exists(sound):
                    errors.append(f"missing object sound {sound}")
        elif kind == "spawn":
            spawns.append(tuple(int(v) for v in p[1:4]))
        elif kind == "poi":
            pois.append((*(int(v) for v in p[1:4]), p[4]))
        elif kind == "poiregion":
            regions.append(tuple(int(v) for v in p[1:7]) + (p[7],))
        elif kind == "fixture":
            fixtures.append((*(int(v) for v in p[2:5]), p[1], p[5]))
        elif kind == "portal":
            portals.append(p)
        elif kind == "src":
            beds.append(p[7])
        elif kind == "turbolift":
            lifts.append((tuple(int(v) for v in p[1:5]),
                          [int(f.split(",")[1]) for f in p[8:]]))

    # Object components are resolved solid-first, then walkable tops, which is
    # what the runtime does.
    parts = [p for p in records if p[0] == "objectpart"]
    for solid in ("0", "1"):
        for p in parts:
            if int(p[1]) not in objects:
                errors.append(f"orphan object part {p[1]}")
            if p[9] == solid:
                paint(grid, p[2:8], SOLID if solid == "1" else FLOOR)

    for material in sorted(materials_used - {"blank"}):
        if material not in surfaces:
            errors.append(f"material {material!r} has no surface line")
    for bed in sorted(set(beds)):
        if not _sound_exists(bed):
            errors.append(f"missing ambience bed {bed}")

    def stand(x, y, z):
        if not (0 <= x < w and 0 <= y < h and 0 <= z < depth - 2):
            return False
        i = y * w + x
        return grid[z][i] == FLOOR and grid[z + 1][i] == AIR and grid[z + 2][i] == AIR

    def occupiable(x, y, z):
        """Standing on a floor, or part-way up a climb."""
        if not (0 <= x < w and 0 <= y < h and 0 <= z < depth - 1):
            return False
        i = y * w + x
        if grid[z][i] == CLIMB:
            return True
        return stand(x, y, z)

    if len(spawns) < 12:
        errors.append(f"only {len(spawns)} spawns; twelve is the floor")
    for pos in spawns:
        if not stand(*pos):
            errors.append(f"unsafe spawn {pos}")

    # Flood the real walkable surface: one-unit steps, and any height along a
    # climb column.
    seen = [bytearray(area) for _ in range(depth)]
    start = next((s for s in spawns if stand(*s)), None)
    queue = deque()
    if start:
        queue.append(start)
        seen[start[2]][start[1] * w + start[0]] = 1
    while queue:
        x, y, z = queue.popleft()
        i = y * w + x
        # A lift you can stand on the panel of joins every level it serves.
        for (x1, x2, y1, y2), levels in lifts:
            if not (x1 <= x <= x2 and y1 <= y <= y2 and z in levels):
                continue
            for nz in levels:
                if nz != z and not seen[nz][i] and stand(x, y, nz):
                    seen[nz][i] = 1
                    queue.append((x, y, nz))
        if grid[z][i] == CLIMB:
            for nz in (z - 1, z + 1):
                if 0 <= nz < depth - 1 and not seen[nz][i] and occupiable(x, y, nz):
                    seen[nz][i] = 1
                    queue.append((x, y, nz))
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if not (0 < nx < w - 1 and 0 < ny < h - 1):
                continue
            j = ny * w + nx
            for nz in (z, z + 1, z - 1):
                if nz < 0 or nz >= depth - 1 or seen[nz][j]:
                    continue
                if not occupiable(nx, ny, nz):
                    continue
                seen[nz][j] = 1
                queue.append((nx, ny, nz))
                break

    for pos in spawns:
        if stand(*pos) and not seen[pos[2]][pos[1] * w + pos[0]]:
            errors.append(f"spawn {pos} is on an island of its own")
    for x, y, z, name in pois:
        if not occupiable(x, y, z):
            errors.append(f"landmark {name!r} at {(x, y, z)} is inside something")
        elif not seen[z][y * w + x]:
            errors.append(f"landmark {name!r} at {(x, y, z)} cannot be walked to")
    for a, b, c, d, e, f, name in regions:
        if not any(seen[z][y * w + x]
                   for z in range(e, min(f, depth - 1) + 1)
                   for y in range(c, d + 1)
                   for x in range(a, b + 1)
                   if occupiable(x, y, z)):
            errors.append(f"landmark region {name!r} has nothing walkable in it")
    for x, y, z, kind, label in fixtures:
        if not stand(x, y, z):
            errors.append(f"service {label!r} at {(x, y, z)} is inside something")
        elif not any(seen[z][(y + dy) * w + x + dx] for dx, dy in
                     ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, 0), (1, 0), (0, -1), (0, 1))):
            errors.append(f"service {label!r} cannot be reached")
        if not (SOUNDS / "executioners_rage/environment/objects" / kind).is_dir():
            errors.append(f"unknown service type {kind!r}")
    for p in portals:
        a, b, c, d, e, f = (int(v) for v in p[1:7])
        x, y = (a + b) // 2, (c + d) // 2
        if len(p) > 8 and p[8] == "window":
            continue  # a window is a portal with no hole, on purpose
        if not occupiable(x, y, e):
            errors.append(f"doorway {p[7]!r} at {(x, y, e)} is sealed")
        elif not seen[e][y * w + x]:
            errors.append(f"doorway {p[7]!r} at {(x, y, e)} leads nowhere reachable")

    unnamed = 0
    example = None
    for z in range(depth):
        row, zone_row = seen[z], named[z]
        for i, value in enumerate(row):
            if value and not zone_row[i]:
                unnamed += 1
                if example is None:
                    example = (i % w, i // w, z)
    if unnamed:
        errors.append(f"{unnamed} reachable positions have no zone, first at {example}")

    for p in records:
        if p[0] == "ispawn":
            for cx, cy, cz in ((int(p[1]), int(p[3]), int(p[5])),
                               (int(p[2]), int(p[4]), int(p[6]))):
                if not stand(cx, cy, cz):
                    errors.append(f"loot spawn corner {(cx, cy, cz)} is inside something")
                    break
            for item in p[9:]:
                if item not in items:
                    errors.append(f"unknown loot item {item}")

    reachable = sum(sum(row) for row in seen)
    print(f"{relative}: {reachable} reachable positions, {len(surfaces)} surfaces, "
          f"{len(pois) + len(regions)} landmarks, {len(objects)} objects, "
          f"{len(fixtures)} services, "
          f"{len(set(beds))} ambience beds, {len(spawns)} spawns")
    for error in errors[:40]:
        print("  ERROR:", error)
    if len(errors) > 40:
        print(f"  ... and {len(errors) - 40} more")
    return errors


if __name__ == "__main__":
    items = _registered_items()
    wanted = sys.argv[1:] or FILES
    failures = []
    for filename in wanted:
        if (MAPS / filename).is_file():
            failures.extend(validate(filename, items))
        else:
            print(f"{filename}: not built yet")
    raise SystemExit(1 if failures else 0)
