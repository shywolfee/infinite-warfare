"""Validate a multi-level Coruscant Map:
  * bad tile types and sub-7-Z zones (collected during generation),
  * fall holes: a standable zone with no floor tile at its own base level,
  * reachability: per level plane, flood-fill from recorded seeds and report any
    zone on that plane that is walkable but sealed off,
  * out-of-bounds."""
from collections import deque

_SKIP_SUBSTR = ("on top of", "railing", "roof of", "bulkhead", " stairs",
                "ladder to", "ladder into", "stairs to", "staircase", "stairwell",
                "shaft", "elevator", "ramp", "control panel", "attic", "cab",
                "lantern room", "bunker", "hatch", "upstairs", "cellar",
                " car (", " doors", "turbolift", "open shaft", "the void")


def _skip(name):
    n = name.lower()
    return any(s in n for s in _SKIP_SUBSTR)


def validate(m, report_limit=30):
    problems = list(m.errors)
    W, H = m.maxx + 2, m.maxy + 2
    cx = lambda v: max(0, min(m.maxx, v))
    cy = lambda v: max(0, min(m.maxy, v))

    tiles, zones = [], []
    for ln in m.lines:
        if ln.startswith("tile:"):
            p = ln.split(":")
            tiles.append(tuple(map(int, p[1:7])) + (p[7],))
        elif ln.startswith("zone:"):
            p = ln.split(":")
            zones.append(tuple(map(int, p[1:7])) + (":".join(p[7:]),))

    plane_cache = {}

    def planes(z):
        if z in plane_cache:
            return plane_cache[z]
        solid = bytearray(W * H)
        wall = bytearray(W * H)
        for (x1, x2, y1, y2, z1, z2, t) in tiles:
            if z1 <= z <= z2:
                s = 0 if t == "blank" else 1
                w = 1 if "wall" in t else 0
                for x in range(cx(x1), cx(x2) + 1):
                    base = x * H
                    for y in range(cy(y1), cy(y2) + 1):
                        solid[base + y] = s
                        wall[base + y] = w
        plane_cache[z] = (solid, wall)
        return plane_cache[z]

    def effective_zone(x, y, z):
        # The zone a standing player actually hears is the last one declared
        # that covers the cell (get_zone_at semantics).
        for (x1, x2, y1, y2, z1, z2, name) in reversed(zones):
            if x1 <= x <= x2 and y1 <= y <= y2 and z1 <= z <= z2:
                return name
        return None

    # fall holes: a standable zone must have a floor at the plane the player
    # stands on (its base Z), unless a deliberate shaft is layered over it.
    holes = 0
    for (x1, x2, y1, y2, z1, z2, name) in zones:
        if _skip(name):
            continue
        solid, _ = planes(z1)
        bad = None
        for x in range(cx(x1), cx(x2) + 1):
            base = x * H
            for y in range(cy(y1), cy(y2) + 1):
                if not solid[base + y]:
                    ez = effective_zone(x, y, z1)
                    if ez is None or not _skip(ez):
                        bad = (x, y)
                        break
            if bad:
                break
        if bad:
            holes += 1
            if holes <= report_limit:
                problems.append("FALL HOLE in zone '%s' at %s z=%d" % (name, bad, z1))

    # reachability per plane, seeded from recorded walkable points
    seeds_by_z = {}
    for (sx, sy, sz) in m.seeds:
        seeds_by_z.setdefault(sz, []).append((sx, sy))

    unreachable = 0
    for pz, seeds in seeds_by_z.items():
        solid, wall = planes(pz)
        walk = lambda x, y: solid[x * H + y] and not wall[x * H + y]
        seen = bytearray(W * H)
        q = deque()
        for (sx, sy) in seeds:
            if 0 <= sx <= m.maxx and 0 <= sy <= m.maxy and walk(sx, sy) and not seen[sx * H + sy]:
                seen[sx * H + sy] = 1
                q.append((sx, sy))
        while q:
            x, y = q.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx <= m.maxx and 0 <= ny <= m.maxy and not seen[nx * H + ny] and walk(nx, ny):
                    seen[nx * H + ny] = 1
                    q.append((nx, ny))
        for (x1, x2, y1, y2, z1, z2, name) in zones:
            if z1 != pz or _skip(name):
                continue
            any_walk = reached = False
            for x in range(cx(x1), cx(x2) + 1):
                base = x * H
                for y in range(cy(y1), cy(y2) + 1):
                    if walk(x, y):
                        any_walk = True
                        if seen[base + y]:
                            reached = True
                            break
                if reached:
                    break
            if any_walk and not reached:
                unreachable += 1
                if unreachable <= report_limit:
                    problems.append("UNREACHABLE zone '%s' z=%d" % (name, pz))

    oob = 0
    for (x1, x2, y1, y2, z1, z2, name) in zones:
        # Negative Z is legal (basements, cellars dug below a surface level).
        if x1 < 0 or y1 < 0 or x2 > m.maxx or y2 > m.maxy or z2 > m.maxz or z1 < -m.maxz:
            oob += 1
            if oob <= 10:
                problems.append("OOB zone '%s' (%d,%d,%d,%d,%d,%d)" % (name, x1, x2, y1, y2, z1, z2))

    return problems, {"tiles": len(tiles), "zones": len(zones), "holes": holes,
                      "unreachable": unreachable, "oob": oob, "planes": len(plane_cache)}
