"""
Shattersea map generator - core library.

Coordinate system (matches the engine + Ghost Town map conventions):
  +X = east, +Y = north, +Z = up (vertical / jump height).
Mechanics that constrain the output:
  * Any tile whose type contains "wall" blocks movement at the player's Z.
  * A walkable spot MUST have a non-empty, non-"blank" tile at the player's
    feet Z or the player falls. So every zone the player can stand in needs a
    floor tile beneath it.
  * A doorway is a real GAP in the wall: no wall tile at the walking Z band
    (0..5), optionally a lintel (z6..top) above so it still reads as a wall
    when you jump. Jump rises at most 5 Z.
  * Ground/room zones therefore span >= 7 tiles on Z so a jump never pops you
    out of the zone. Furniture "on top" zones span exactly 7 (top+1..top+7).
"""

VALID_TILES = {
    "shallow", "sand", "concrete2", "concrete5", "concrete10", "concrete12",
    "hardwood", "hardwood2", "carpet1", "tile1", "tile2", "grass", "grass3",
    "gravel1", "rocks1", "stone", "cement", "metal2", "metal4", "metal5",
    "tunnel", "bridge", "plank", "ladder1", "blank", "water1", "wallbrick",
    "wallstone", "wallwood", "wallfence", "wallrock", "glass", "tree",
}

# Standard vertical bands.
GROUND_TOP = 8          # outdoor ground zone: z0..8 (9 tiles, > jump of 5)
ROOM_TOP = 11           # single-storey interior zone height
WALL_Z = 12             # ground-floor wall / ceiling height
FLOOR2_Z = 12           # second-floor deck sits at this Z
WALL2_Z = 24            # two-storey outer wall height
DOOR_OPEN = 5           # doorway open band is z0..5; lintel is z6..top


class Map:
    def __init__(self, name, maxx, maxy, maxz):
        self.name = name
        self.maxx, self.maxy, self.maxz = maxx, maxy, maxz
        self.lines = []
        self.errors = []
        self.base_z = 0
        self.seeds = []

    # ---- raw emitters -----------------------------------------------------
    def raw(self, s):
        self.lines.append(s)

    def comment(self, s=""):
        self.lines.append("// " + s if s else "")

    def section(self, title):
        self.lines.append("")
        self.lines.append("// " + "=" * 60)
        self.lines.append("// " + title)
        self.lines.append("// " + "=" * 60)

    def tile(self, x1, x2, y1, y2, z1, z2, t):
        if t not in VALID_TILES:
            self.errors.append("bad tile type: " + t)
        z1 += self.base_z; z2 += self.base_z
        self.lines.append("tile:%d:%d:%d:%d:%d:%d:%s" % (x1, x2, y1, y2, z1, z2, t))

    def zone(self, x1, x2, y1, y2, z1, z2, name):
        span = z2 - z1 + 1
        # Zones must give >=7 Z of headroom unless they are thin "on top of"
        # furniture caps (which are exactly 7) or vertical shafts.
        if span < 7:
            self.errors.append("zone <7 Z (%d): %s" % (span, name))
        z1 += self.base_z; z2 += self.base_z
        self.lines.append("zone:%d:%d:%d:%d:%d:%d:%s" % (x1, x2, y1, y2, z1, z2, name))

    def zone_raw(self, x1, x2, y1, y2, z1, z2, name):
        # For deliberate thin zones (furniture caps, railings) - no Z check.
        z1 += self.base_z; z2 += self.base_z
        self.lines.append("zone:%d:%d:%d:%d:%d:%d:%s" % (x1, x2, y1, y2, z1, z2, name))

    def src(self, x1, x2, y1, y2, z1, z2, sound, vol=-8):
        z1 += self.base_z; z2 += self.base_z
        self.lines.append("src:%d:%d:%d:%d:%d:%d:%s:%d" % (x1, x2, y1, y2, z1, z2, sound, vol))

    def ispawn(self, x1, x2, y1, y2, z1, z2, interval, maxitems, items):
        z1 += self.base_z; z2 += self.base_z
        self.lines.append("ispawn:%d:%d:%d:%d:%d:%d:%d:%d:%s"
                           % (x1, x2, y1, y2, z1, z2, interval, maxitems, ":".join(items)))

    def poi(self, x, y, z, name):
        self.lines.append("poi:%d:%d:%d:%s" % (x, y, z + self.base_z, name))

    def bunker(self, x, y, z, name):
        self.lines.append("bunker:%d:%d:%d:%s" % (x, y, z + self.base_z, name))

    # ---- turbolift (absolute Z; levels are (name, absolute_z)) -------------
    def turbolift(self, x1, x2, y1, y2, z1, z2, name, levels):
        """Declare a turbolift. levels = list of (level_name, absolute_z). The
        panel zone spans x1..x2,y1..y2,z1..z2 (absolute). Names must not contain
        ':' or ','."""
        parts = ["turbolift", str(x1), str(x2), str(y1), str(y2), str(z1), str(z2), name]
        for lname, lz in levels:
            parts.append("%s,%d" % (lname, lz))
        self.lines.append(":".join(parts))

    # ---- level / seed bookkeeping -----------------------------------------
    def at_level(self, z):
        """Set the base Z offset added to every subsequent emit. Use 0 for
        absolute-coordinate work (turbolift shafts, cross-level features)."""
        self.base_z = z

    def seed(self, x, y, z):
        """Record a known-walkable point so the validator can flood-fill this
        level for reachability."""
        self.seeds.append((x, y, z + self.base_z))

    # ---- composite ground helpers ----------------------------------------
    def ground(self, x1, x2, y1, y2, t, zonename, ztop=GROUND_TOP):
        """A filled walkable ground patch: floor tile at z0 + a named zone."""
        self.tile(x1, x2, y1, y2, 0, 0, t)
        self.zone(x1, x2, y1, y2, 0, ztop, zonename)

    def floor(self, x1, x2, y1, y2, t, z=0):
        self.tile(x1, x2, y1, y2, z, z, t)

    # ---- walls with doorway gaps -----------------------------------------
    def wall_x(self, x, y1, y2, ztop, wtype="wallbrick", gaps=None):
        """Vertical wall at constant x, spanning y1..y2, height 0..ztop.
        gaps: list of (gy1, gy2) openings left walkable at z0..DOOR_OPEN
        (a lintel wtype is kept above at DOOR_OPEN+1..ztop)."""
        want = gaps or []
        gaps = _clip(y1, y2, want)
        if len(gaps) < len(want):
            self.errors.append("wall_x x=%d y=%d..%d: a doorway gap fell outside the wall" % (x, y1, y2))
        for a, b in _subtract(y1, y2, gaps):
            self.tile(x, x, a, b, 0, ztop, wtype)
        for gy1, gy2 in gaps:
            if ztop > DOOR_OPEN:
                self.tile(x, x, gy1, gy2, DOOR_OPEN + 1, ztop, wtype)

    def wall_y(self, y, x1, x2, ztop, wtype="wallbrick", gaps=None):
        """Horizontal wall at constant y, spanning x1..x2, height 0..ztop."""
        want = gaps or []
        gaps = _clip(x1, x2, want)
        if len(gaps) < len(want):
            self.errors.append("wall_y y=%d x=%d..%d: a doorway gap fell outside the wall" % (y, x1, x2))
        for a, b in _subtract(x1, x2, gaps):
            self.tile(a, b, y, y, 0, ztop, wtype)
        for gx1, gx2 in gaps:
            if ztop > DOOR_OPEN:
                self.tile(gx1, gx2, y, y, DOOR_OPEN + 1, ztop, wtype)

    # ---- furniture --------------------------------------------------------
    def furniture(self, x1, x2, y1, y2, top, name, t="hardwood"):
        """A solid low object you can jump onto. Occupies z0..top; its cap
        zone spans exactly 7 Z so you stay in-zone while jumping on it."""
        self.tile(x1, x2, y1, y2, 0, top, t)
        self.zone_raw(x1, x2, y1, y2, 0, max(6, top), name)
        self.zone_raw(x1, x2, y1, y2, top + 1, top + 7, "on top of " + name)


def _clip(lo, hi, gaps):
    """Keep only the gaps (clamped) that actually intersect [lo,hi]."""
    out = []
    for g1, g2 in gaps:
        a, b = max(lo, g1), min(hi, g2)
        if a <= b:
            out.append((a, b))
    return out


def _subtract(lo, hi, gaps):
    """Return the sub-ranges of [lo,hi] left after removing gap ranges. Gaps are
    assumed already clipped to [lo,hi]."""
    points = sorted(gaps)
    segs = []
    cur = lo
    for g1, g2 in points:
        if g1 > cur:
            segs.append((cur, g1 - 1))
        cur = max(cur, g2 + 1)
    if cur <= hi:
        segs.append((cur, hi))
    return segs
