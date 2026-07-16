"""Validate a generated Map object for the mechanics that matter:
  * bad tile types and sub-7-Z zones (collected during generation),
  * fall holes: a ground zone with no z0 floor beneath it,
  * reachability: a ground zone that is sealed off from the deploy point."""
from collections import deque
import config as C

_SKIP_SUBSTR = ("on top of", "railing", "roof of", "bulkhead", " stairs",
                "ladder to", "ladder into", "stairs to", "staircase", "stairwell",
                "shaft", "elevator", "ramp", "control panel", "attic", "cab",
                "lantern room", "bunker", "hatch", "upstairs", "cellar")


def _skip(name):
    n = name.lower()
    return any(s in n for s in _SKIP_SUBSTR)


def validate(m, report_limit=25):
    problems = list(m.errors)
    W, H = m.maxx + 2, m.maxy + 2

    solid = bytearray(W * H)    # 1 = a standable tile at z0
    wall = bytearray(W * H)     # 1 = topmost z0 tile is a wall type
    tiles, zones = [], []
    for ln in m.lines:
        if ln.startswith("tile:"):
            p = ln.split(":")
            tiles.append(tuple(map(int, p[1:7])) + (p[7],))
        elif ln.startswith("zone:"):
            p = ln.split(":")
            zones.append(tuple(map(int, p[1:7])) + (":".join(p[7:]),))

    cx = lambda v: max(0, min(m.maxx, v))
    cy = lambda v: max(0, min(m.maxy, v))

    for (x1, x2, y1, y2, z1, z2, t) in tiles:
        if z1 <= 0 <= z2:
            s = 0 if t == "blank" else 1
            w = 1 if "wall" in t else 0
            for x in range(cx(x1), cx(x2) + 1):
                base = x * H
                for y in range(cy(y1), cy(y2) + 1):
                    solid[base + y] = s
                    wall[base + y] = w

    # fall holes
    holes = 0
    for (x1, x2, y1, y2, z1, z2, name) in zones:
        if not (z1 <= 0 <= z2) or _skip(name):
            continue
        bad = None
        for x in range(cx(x1), cx(x2) + 1):
            base = x * H
            for y in range(cy(y1), cy(y2) + 1):
                if not solid[base + y]:
                    bad = (x, y)
                    break
            if bad:
                break
        if bad:
            holes += 1
            if holes <= report_limit:
                problems.append("FALL HOLE in zone '%s' at %s" % (name, bad))

    # reachability flood fill at z0 from the deploy point
    walkable = lambda x, y: solid[x * H + y] and not wall[x * H + y]
    seen = bytearray(W * H)
    q = deque()
    sx, sy = (C.SPAWN_X1 + C.SPAWN_X2) // 2, (C.SPAWN_Y1 + C.SPAWN_Y2) // 2
    if walkable(sx, sy):
        seen[sx * H + sy] = 1
        q.append((sx, sy))
    else:
        problems.append("SPAWN not walkable at (%d,%d)" % (sx, sy))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx <= m.maxx and 0 <= ny <= m.maxy and not seen[nx * H + ny] and walkable(nx, ny):
                seen[nx * H + ny] = 1
                q.append((nx, ny))

    unreachable = 0
    for (x1, x2, y1, y2, z1, z2, name) in zones:
        if not (z1 <= 0 <= z2) or _skip(name):
            continue
        # is any cell of this zone walkable-and-reached?
        any_walk = False
        reached = False
        for x in range(cx(x1), cx(x2) + 1):
            base = x * H
            for y in range(cy(y1), cy(y2) + 1):
                if walkable(x, y):
                    any_walk = True
                    if seen[base + y]:
                        reached = True
                        break
            if reached:
                break
        if any_walk and not reached:
            unreachable += 1
            if unreachable <= report_limit:
                problems.append("UNREACHABLE zone '%s' (sealed from spawn)" % name)

    oob = 0
    for (x1, x2, y1, y2, z1, z2, name) in zones:
        if x1 < 0 or y1 < 0 or x2 > m.maxx or y2 > m.maxy or z2 > m.maxz:
            oob += 1
            if oob <= 10:
                problems.append("OOB zone '%s'" % name)

    return problems, {"tiles": len(tiles), "zones": len(zones), "holes": holes,
                      "unreachable": unreachable, "oob": oob}
