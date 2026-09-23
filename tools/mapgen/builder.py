"""Map primitives.

A map is a text file of colon-separated rectangles. Nobody writes ten thousand
of those by hand and keeps them consistent, so the maps here are described in
terms a person can hold in their head -- a street, a room, a doorway, a flight
of stairs -- and the rectangles fall out.

The rules these helpers exist to enforce, because they are the ones that get
forgotten on the fortieth room of a map:

  * A room writes a floor, four walls, a roof, a named interior zone AND an
    acoustic space in one call. A room with no acoustic space sounds like open
    ground, which is worse than not having the room.
  * A doorway writes the hole in the wall, the portal sound travels through,
    AND a zone of its own. All three or none: a portal with no hole is a wall
    you can hear through, and a hole with no portal is a door you cannot find
    by ear.
  * A street writes the carriageway, both pavements and a kerb zone between
    each pavement and the road, because stepping off a kerb is exactly the
    sort of thing you cannot see.
  * A junction exists because walking out of one street into another with
    nothing in between means the moment where you could have turned passes
    unannounced.
  * A flight of stairs is a stack of one-unit surfaces, which is what makes it
    something you walk up rather than something you operate.
  * Every material used gets a surface line, so the client never has to guess.

Coordinates are whole units. X is east, Y is north, Z is up. Rectangles are
inclusive at both ends. Later records win, so a map lays a road down and then
paints a kerb over part of it.
"""
from __future__ import annotations

from .palette import AMBIENCE, FIXTURE_KINDS, KINDS, PRESET_NAMES, SURFACES

AIR = "blank"


def _rect(r):
    x1, x2, y1, y2 = r
    assert x1 <= x2 and y1 <= y2, f"inside-out rectangle {r}"
    return x1, x2, y1, y2


class Map:
    def __init__(self, ident, title, width, depth, height=64):
        self.ident = ident
        self.title = title
        self.width = width
        self.depth = depth
        self.height = height
        self.lines: list[str] = []
        self.used_surfaces: set[str] = set()
        self.deferred: list[tuple] = []
        self.object_count = 0
        self.source_count = 0
        self.spawns: list[tuple] = []
        self.poi_count = 0
        self.zone_count = 0
        self.fixture_count = 0
        self._objects_emitted = 0
        self.pending: list[tuple] = []
        self.unplaced: list[str] = []
        self.lifts: list[tuple] = []

    # -- raw emission ----------------------------------------------------
    def emit(self, kind, *args):
        parts = [kind] + [str(a) for a in args]
        for p in parts[1:]:
            assert ":" not in p, f"colon in {kind} field: {p!r}"
        self.lines.append(":".join(parts))

    def note_surface(self, material):
        if material == AIR:
            return material
        assert material in SURFACES, f"unknown surface {material!r}"
        self.used_surfaces.add(material)
        return material

    # -- layers ----------------------------------------------------------
    def tile(self, r, z1, z2, material):
        x1, x2, y1, y2 = _rect(r)
        self.emit("tile", x1, x2, y1, y2, z1, z2, self.note_surface(material))

    def air(self, r, z1, z2):
        x1, x2, y1, y2 = _rect(r)
        self.emit("tile", x1, x2, y1, y2, z1, z2, AIR)

    def zone(self, r, z1, z2, name):
        x1, x2, y1, y2 = _rect(r)
        assert name, "a zone with no name is a zone that says nothing"
        self.zone_count += 1
        self.emit("zone", x1, x2, y1, y2, z1, z2, name)

    def space(self, r, z1, z2, label, material, kind, enclosed=True):
        x1, x2, y1, y2 = _rect(r)
        assert kind in KINDS, f"unknown acoustic kind {kind!r}"
        self.emit("space" if enclosed else "openspace",
                  x1, x2, y1, y2, z1, z2, label, material, kind)

    def portal(self, r, z1, z2, name):
        x1, x2, y1, y2 = _rect(r)
        self.emit("portal", x1, x2, y1, y2, z1, z2, name, "opening")

    def ambience(self, r, z1, z2, bed):
        """A looping bed that fills its own rectangle rather than sitting at a
        point in the middle of it. A river that is a speaker in the middle of a
        river is a thing you walk past; a river that fills its banks is a thing
        you can walk along and navigate by."""
        x1, x2, y1, y2 = _rect(r)
        assert bed in AMBIENCE, f"unknown ambience bed {bed!r}"
        self.source_count += 1
        self.emit("src", x1, x2, y1, y2, z1, z2, AMBIENCE[bed], self.source_count)

    # -- destinations ----------------------------------------------------
    # Landmarks, services, loot and spawns are held back until the geometry is
    # finished and then settled against the map as the game will actually read
    # it. Placing them by eye means a landmark inside the counter it was meant
    # to describe, and that is exactly the sort of mistake nobody can see.
    def poi(self, x, y, z, name):
        self.poi_count += 1
        self.pending.append(("poi", x, y, z, name, None))

    def poiregion(self, r, z1, z2, name):
        x1, x2, y1, y2 = _rect(r)
        self.poi_count += 1
        self.emit("poiregion", x1, x2, y1, y2, z1, z2, name)

    def spawn(self, x, y, z=0):
        self.pending.append(("spawn", x, y, z, "", None))

    def loot(self, r, z, items, seconds=45, most=3):
        """Scatter `most` separate one-square item spawns inside the rectangle.

        One spawn point with a stack limit puts everything in a heap on a
        single square; separate points mean an item somewhere in the room,
        which is the thing worth searching a room for. Each point is settled
        against the finished geometry, so none of them can end up inside the
        counter they were meant to be beside."""
        x1, x2, y1, y2 = _rect(r)
        assert items, "a loot spawn with no table spawns nothing"
        for i in range(most):
            fx = (i * 2 + 1) / (most * 2)
            fy = ((i * 3 + 1) % (most * 2) + 1) / (most * 2 + 1)
            x = int(x1 + (x2 - x1) * fx)
            y = int(y1 + (y2 - y1) * fy)
            self.pending.append(("loot", x, y, z, "", (items, seconds, 1)))

    def fixture(self, kind, x, y, z, label):
        assert kind in FIXTURE_KINDS, f"unknown service {kind!r}"
        self.fixture_count += 1
        self.pending.append(("fixture", x, y, z, label, kind))

    def bunker(self, x, y, z, name):
        self.emit("bunker", x, y, z, name)

    def turbolift(self, r, z1, z2, name, levels):
        """A lift panel. `levels` is a list of (label, z).

        The lift moves you up and down one shaft and does not carry you
        sideways, so every level it serves has to be standable at the same x
        and y. Declaring the panel at each level is what makes the lift work in
        both directions."""
        x1, x2, y1, y2 = _rect(r)
        fields = [f"{label},{z}" for label, z in levels]
        self.lifts.append((x1, x2, y1, y2, [z for _, z in levels]))
        self.emit("turbolift", x1, x2, y1, y2, z1, z2, name, *fields)

    def transition(self, r, z1, z2, dest, label):
        x1, x2, y1, y2 = _rect(r)
        dx, dy, dz = dest
        self.emit("transition", x1, x2, y1, y2, z1, z2, dx, dy, dz, label)

    # -- destructible furniture -------------------------------------------
    def obj(self, preset, x, y, z, name, w=4, d=2, h=2, turn=0):
        assert preset in PRESET_NAMES, f"unknown preset {preset!r}"
        self.object_count += 1
        self.deferred.append(("object", preset, x, y, z, name, w, d, h, turn))
        return self.object_count

    # -- composite: outdoor ------------------------------------------------
    def area(self, r, name, material, z=0, kind="open", head=7, bed=None):
        """Open ground. Tile, zone and an open acoustic space in one call."""
        self.tile(r, z, z, material)
        self.zone(r, z, z + head, name)
        self.space(r, z, z + head, name, material, kind, enclosed=False)
        if bed:
            self.ambience(r, z, z + head, bed)

    def plateau(self, r, name, material, z, side="rock wall", kind="open", head=7,
                base=0):
        """Ground raised above `base`, with solid sides so getting up it is a
        stair or a climb rather than a step.

        `base` matters on a map with levels under it. Filling from nought is
        right for a headland standing in the sea and catastrophic for a
        ziggurat standing on the fifth thousandth floor of a city: it fills the
        five thousand floors below it with rock."""
        if z > base:
            self.tile(r, base, z - 1, side)
        self.area(r, name, material, z, kind, head)

    def deck(self, r, z, name, material="steel grating", kind="platform",
             head=6, bed=None):
        """A floor in the air, held up by whatever is already holding it up.

        This is not a plateau. A plateau fills everything under itself with
        rock, which is right for a headland and catastrophic for the gallery
        round a lighthouse -- it buries the lighthouse."""
        self.tile(r, z, z, material)
        self.air(r, z + 1, z + head)
        self.zone(r, z, z + head, name)
        self.space(r, z, z + head, name, "metal", kind, enclosed=False)
        if bed:
            self.ambience(r, z, z + head, bed)

    def block(self, r, z, height, name, wall="brick wall", roof="concrete pavement"):
        """A building you cannot enter: solid to walk into, with a roof that
        exists so anything standing on a neighbouring roof does not fall into
        a hole. Cheap, and most of a city is this."""
        self.tile(r, z, z + height - 1, wall)
        self.tile(r, z + height, z + height, roof)
        self.zone(r, z + height, z + height + 4, name + ", roof")

    # -- composite: streets -------------------------------------------------
    def street(self, name, r, axis, z=0, surface="asphalt",
               pavement="concrete pavement", pavement_width=3, segments=None,
               bed=None, kind="street"):
        """A street is five zones wide: two pavements, two kerbs, a road.

        `r` is the whole corridor including both pavements. `segments` is a
        list of (from, to, label) along the axis so a long street is named by
        the stretch you are on rather than end to end.
        """
        x1, x2, y1, y2 = _rect(r)
        pw = pavement_width
        if axis == "x":
            lo, hi = x1, x2
            near = (x1, x2, y1, y1 + pw - 1)
            far = (x1, x2, y2 - pw + 1, y2)
            road = (x1, x2, y1 + pw, y2 - pw)
            near_kerb = (x1, x2, y1 + pw - 1, y1 + pw - 1)
            far_kerb = (x1, x2, y2 - pw + 1, y2 - pw + 1)
            near_name, far_name = "south pavement", "north pavement"
            near_kerb_name, far_kerb_name = "south kerb", "north kerb"
        else:
            lo, hi = y1, y2
            near = (x1, x1 + pw - 1, y1, y2)
            far = (x2 - pw + 1, x2, y1, y2)
            road = (x1 + pw, x2 - pw, y1, y2)
            near_kerb = (x1 + pw - 1, x1 + pw - 1, y1, y2)
            far_kerb = (x2 - pw + 1, x2 - pw + 1, y1, y2)
            near_name, far_name = "west pavement", "east pavement"
            near_kerb_name, far_kerb_name = "west kerb", "east kerb"

        self.tile((x1, x2, y1, y2), z, z, pavement)
        self.tile(road, z, z, surface)
        self.space((x1, x2, y1, y2), z, z + 8, name, "concrete", kind, enclosed=False)
        if bed:
            self.ambience((x1, x2, y1, y2), z, z + 8, bed)

        if segments is None:
            segments = [(lo, hi, "")]
        for a, b, label in segments:
            if a > b:
                continue  # two streets meeting leaves no stretch between them
            where = f"{name}, {label}" if label else name
            def cut(box):
                bx1, bx2, by1, by2 = box
                if axis == "x":
                    return (max(bx1, a), min(bx2, b), by1, by2)
                return (bx1, bx2, max(by1, a), min(by2, b))
            self.zone(cut(road), z, z + 8, f"{where}, carriageway")
            self.zone(cut(near), z, z + 8, f"{where}, {near_name}")
            self.zone(cut(far), z, z + 8, f"{where}, {far_name}")
            self.zone(cut(near_kerb), z, z + 8, f"{where}, {near_kerb_name}")
            self.zone(cut(far_kerb), z, z + 8, f"{where}, {far_kerb_name}")

    def junction(self, name, r, z=0, surface="asphalt", crossings=(), kind="square"):
        """Where two streets meet. Its own tile, its own zone, and a zone for
        each marked crossing, because a crossing you cannot find is a crossing
        that is not there."""
        self.tile(r, z, z, surface)
        self.zone(r, z, z + 8, name)
        self.space(r, z, z + 8, name, "concrete", kind, enclosed=False)
        for box, label in crossings:
            self.zone(box, z, z + 8, f"{name}, {label}")

    def path(self, name, r, material="paving slabs", z=0, kind="alley", bed=None):
        """A lane, alley, towpath or track: one surface, one zone, no kerbs."""
        self.area(r, name, material, z, kind, bed=bed)

    # -- composite: buildings ----------------------------------------------
    def room(self, r, z, name, floor="ceramic tile", height=6, wall="brick wall",
             kind="room", roof="concrete pavement", roof_zone=True, material=None):
        """Floor, four walls, roof, interior zone and acoustic space."""
        x1, x2, y1, y2 = _rect(r)
        assert x2 - x1 >= 2 and y2 - y1 >= 2, f"room {name!r} has no interior"
        self.air(r, z, z + height)
        self.tile(r, z, z, floor)
        self.tile((x1, x1, y1, y2), z, z + height - 1, wall)
        self.tile((x2, x2, y1, y2), z, z + height - 1, wall)
        self.tile((x1, x2, y1, y1), z, z + height - 1, wall)
        self.tile((x1, x2, y2, y2), z, z + height - 1, wall)
        self.tile(r, z + height, z + height, roof)
        inner = (x1 + 1, x2 - 1, y1 + 1, y2 - 1)
        self.zone(inner, z, z + height - 1, name)
        self.space(inner, z, z + height - 1, name,
                   material or _absorption(wall), kind, enclosed=True)
        if roof_zone:
            self.zone(r, z + height, z + height + 4, f"{name}, roof")

    COMPASS = {
        (0, 0): "south-west", (1, 0): "south", (2, 0): "south-east",
        (0, 1): "west", (1, 1): "middle", (2, 1): "east",
        (0, 2): "north-west", (1, 2): "north", (2, 2): "north-east",
    }

    def quarters(self, r, z, name, head=7, cols=3, rows=3, suffix="quarter"):
        """Cut a large open area into named parts.

        A four-hundred-square island with one zone on it tells you which island
        you are on and nothing else. Any open space big enough to get lost in
        gets its bearings written onto it, so "Kelphaven, north-west quarter" is
        something you can say over a radio and something somebody can walk to.
        """
        x1, x2, y1, y2 = _rect(r)
        for cx in range(cols):
            for cy in range(rows):
                ax = x1 + (x2 - x1 + 1) * cx // cols
                bx = x1 + (x2 - x1 + 1) * (cx + 1) // cols - 1
                ay = y1 + (y2 - y1 + 1) * cy // rows
                by = y1 + (y2 - y1 + 1) * (cy + 1) // rows - 1
                if ax > bx or ay > by:
                    continue
                key = (cx if cols > 1 else 1, cy if rows > 1 else 1)
                where = self.COMPASS.get((min(key[0], 2), min(key[1], 2)), "middle")
                label = f"{name}, the {where}" if where == "middle" else f"{name}, {where} {suffix}"
                self.zone((ax, bx, ay, by), z, z + head, label)

    def subzone(self, r, z, name, height=5):
        """Part of a room named separately: the counter end of a bar, the
        window side of an office, the foot of a stair."""
        self.zone(r, z, z + height, name)

    def door(self, r, z, name, floor="ceramic tile", height=3):
        """The hole, the portal and the zone. Deferred so that a wall written
        after the room cannot silently seal it."""
        self.deferred.append(("door", _rect(r), z, name, floor, height))

    def window(self, r, z, name, material="window wall", height=2):
        """Sound goes through, you do not. Deferred for the same reason."""
        self.deferred.append(("window", _rect(r), z, name, material, height))

    # -- composite: getting up and down --------------------------------------
    def stair(self, r, low, high, name, axis="y", material="concrete stairs",
              support="concrete wall", kind="stairwell", head=6, base=0):
        """A stack of one-unit surfaces, which is what a stair is to anything
        that walks. Each tread is its own level, so the kerb rule carries you
        up it without pressing anything."""
        x1, x2, y1, y2 = _rect(r)
        length = (y2 - y1) if axis == "y" else (x2 - x1)
        rise = abs(high - low)
        assert length >= rise, f"{name}: {length} treads cannot climb {rise}"
        for step in range(length + 1):
            z = round(low + (high - low) * step / length)
            tread = (x1, x2, y1 + step, y1 + step) if axis == "y" else (x1 + step, x1 + step, y1, y2)
            # Headroom first. A stair cut into a hillside or down a quay wall is
            # a hole through solid ground, and without this the tread is laid at
            # the bottom of a shaft you cannot stand up in.
            self.air(tread, z + 1, z + head)
            if z > base:
                self.tile(tread, base, z - 1, support)
            self.tile(tread, z, z, material)
        lo, hi = min(low, high), max(low, high)
        self.zone(r, lo, hi + head, name)
        self.space(r, lo, hi + head, name, _absorption(support), kind,
                   enclosed=(kind in ("stairwell", "corridor", "room")))

    def ramp(self, r, low, high, name, axis="y", material="ramp surface",
             support="concrete wall", kind="street", head=7, base=0):
        """Mechanically a stair; named a ramp because that is what it is, and
        given a surface that sounds like one."""
        self.stair(r, low, high, name, axis, material, support, kind, head, base)

    def ladder(self, x, y, z1, z2, name, material="access ladder", face=None):
        """A climb. The column is its own surface, so the client knows it is a
        climb and the automatic one-unit step refuses to take it sideways."""
        self.tile((x, x, y, y), z1, z2, material)
        self.zone((x, x, y, y), z1, z2, name)
        if face:
            self.zone(face, z1, z1 + 4, f"{name}, foot")

    def bridge(self, r, z, name, axis="y", deck="steel deck", rail="railing wall",
               piers=(), pier_material="concrete wall", kind="bridge", bed=None):
        """An elevated deck with rails and piers, rather than a solid block of
        rock filling its bounding box. You can walk under it."""
        x1, x2, y1, y2 = _rect(r)
        for px, py in piers:
            self.tile((px, px + 1, py, py + 1), 0, z - 1, pier_material)
        self.tile(r, z, z, deck)
        if axis == "y":
            self.tile((x1, x1, y1, y2), z + 1, z + 2, rail)
            self.tile((x2, x2, y1, y2), z + 1, z + 2, rail)
            walk = (x1 + 1, x2 - 1, y1, y2)
        else:
            self.tile((x1, x2, y1, y1), z + 1, z + 2, rail)
            self.tile((x1, x2, y2, y2), z + 1, z + 2, rail)
            walk = (x1, x2, y1 + 1, y2 - 1)
        self.zone(walk, z, z + 6, name)
        self.space(r, z, z + 6, name, "metal", kind, enclosed=False)
        if bed:
            self.ambience(r, z, z + 6, bed)
        return walk

    # -- output --------------------------------------------------------------
    def finish(self):
        # Doors and windows go in after every room, so a shared wall written
        # later cannot seal an opening written earlier.
        for item in self.deferred:
            if item[0] == "door":
                _, r, z, name, floor, height = item
                self.air(r, z, z + height)
                self.tile(r, z, z, floor)
                self.zone(r, z, z + height, name)
                self.portal(r, z, z + height, name)
            elif item[0] == "window":
                _, r, z, name, material, height = item
                self.tile(r, z, z + height - 1, material)
                x1, x2, y1, y2 = r
                self.emit("portal", x1, x2, y1, y2, z, z + height - 1, name, "window")
            elif item[0] == "object":
                _, preset, x, y, z, name, w, d, h, turn = item
                self._emit_object(preset, x, y, z, name, w, d, h, turn)
        self._settle_placements()
        # The edge of the world.
        edge = "rock wall"
        self.tile((0, 0, 0, self.depth), 0, self.height, edge)
        self.tile((self.width, self.width, 0, self.depth), 0, self.height, edge)
        self.tile((0, self.width, 0, 0), 0, self.height, edge)
        self.tile((0, self.width, self.depth, self.depth), 0, self.height, edge)
        assert not self.unplaced, chr(10).join(["could not place:"] + self.unplaced)
        assert len(self.spawns) >= 12, f"{self.ident}: needs twelve authored spawns"
        return self

    # -- settling ------------------------------------------------------------
    # Offsets tried in order: stay put, then outward a ring at a time, then a
    # level up or down. A landmark that has to move more than a few units was
    # put somewhere wrong and says so rather than quietly relocating.
    _NUDGE = [(0, 0)] + [(dx, dy) for ring in range(1, 9)
                         for dx in range(-ring, ring + 1)
                         for dy in range(-ring, ring + 1)
                         if max(abs(dx), abs(dy)) == ring]

    def _raster(self):
        w, h, d = self.width + 1, self.depth + 1, self.height + 1
        grid = [bytearray(w * h) for _ in range(d)]
        for line in self.lines:
            parts = line.split(":")
            if parts[0] == "tile":
                x1, x2, y1, y2, z1, z2 = (int(v) for v in parts[1:7])
                material = parts[7]
                if material == "blank":
                    value = 0
                elif any(word in material for word in
                         ("ladder", "rungs", "climb", "netting", "scaffold")):
                    value = 3  # a climb: occupiable at any height, not a floor
                elif "wall" in material:
                    value = 2
                else:
                    value = 1
            elif parts[0] == "objectpart":
                x1, x2 = int(float(parts[2])), int(float(parts[3]))
                y1, y2 = int(float(parts[4])), int(float(parts[5]))
                z1, z2 = int(float(parts[6])), int(float(parts[7]))
                value = 2 if parts[9] == "1" else 1
            else:
                continue
            if x1 > x2 or y1 > y2 or z1 > z2:
                continue
            x1, y1, z1 = max(x1, 0), max(y1, 0), max(z1, 0)
            x2, y2, z2 = min(x2, w - 1), min(y2, h - 1), min(z2, d - 1)
            stripe = bytes([value]) * (x2 - x1 + 1)
            for z in range(z1, z2 + 1):
                row = grid[z]
                for y in range(y1, y2 + 1):
                    row[y * w + x1:y * w + x2 + 1] = stripe
        return grid, w, h, d

    def _settle_placements(self):
        """Put every landmark, service, loot point and spawn on a square that
        is genuinely standable and genuinely connected to the rest of the map.

        The connectivity half matters more than it sounds. A two-by-four pocket
        behind a shop counter, walled in by a bookcase on one side and the shop
        wall on the other, is a perfectly good place to stand and a completely
        useless place to put a vending machine, and there is no way to notice
        that by reading the coordinates."""
        if not self.pending:
            return
        grid, w, h, d = self._raster()

        def stands(x, y, z):
            if not (0 <= x < w and 0 <= y < h and 0 <= z < d - 2):
                return False
            i = y * w + x
            return grid[z][i] == 1 and grid[z + 1][i] == 0 and grid[z + 2][i] == 0

        # Spawns go down first, on open ground, and seed the flood.
        placed = {}
        order = [p for p in self.pending if p[0] == "spawn"] +                 [p for p in self.pending if p[0] != "spawn"]
        seed = None
        for item in order:
            if item[0] != "spawn":
                continue
            spot = self._nearest(stands, item[1], item[2], item[3])
            if spot is None:
                self.unplaced.append(f"  spawn near {(item[1], item[2], item[3])}")
                continue
            placed[id(item)] = spot
            if seed is None:
                seed = spot

        reachable = self._flood(grid, w, h, d, seed, stands, self.lifts) if seed else set()

        def connected(x, y, z):
            return stands(x, y, z) and (x, y, z) in reachable

        for item in order:
            kind, x, y, z, label, extra = item
            if kind == "spawn":
                spot = placed.get(id(item))
                if spot is None:
                    continue
                if spot not in reachable:
                    self.unplaced.append(f"  spawn at {spot} is on an island")
                    continue
            else:
                spot = self._nearest(connected, x, y, z)
                if spot is None:
                    self.unplaced.append(f"  {kind} {label!r} near {(x, y, z)}")
                    continue
            sx, sy, sz = spot
            if kind == "poi":
                self.emit("poi", sx, sy, sz, label)
            elif kind == "fixture":
                self.emit("fixture", extra, sx, sy, sz, label)
            elif kind == "spawn":
                self.spawns.append(spot)
                self.emit("spawn", sx, sy, sz)
            elif kind == "loot":
                items, seconds, most = extra
                self.emit("ispawn", sx, sx, sy, sy, sz, sz,
                          seconds * 1000, most, *items)

    def _nearest(self, ok, x, y, z):
        for nz in (z, z + 1, z - 1):
            for dx, dy in self._NUDGE:
                if ok(x + dx, y + dy, nz):
                    return (x + dx, y + dy, nz)
        return None

    @staticmethod
    def _flood(grid, w, h, d, seed, stands, lifts=()):
        """Every square you can walk to from the seed, taking one-unit steps,
        climbing any climbable column, and riding any lift whose panel you can
        stand on."""
        from collections import deque
        seen = {seed}
        queue = deque([seed])
        while queue:
            x, y, z = queue.popleft()
            i = y * w + x
            for x1, x2, y1, y2, levels in lifts:
                if not (x1 <= x <= x2 and y1 <= y <= y2 and z in levels):
                    continue
                for nz in levels:
                    if nz != z and (x, y, nz) not in seen and stands(x, y, nz):
                        seen.add((x, y, nz))
                        queue.append((x, y, nz))
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1), (x, y)):
                j = ny * w + nx
                levels = (z - 1, z, z + 1) if (nx, ny) != (x, y) else range(max(z - 1, 0), min(z + 2, d - 2))
                for nz in levels:
                    if nz < 0 or nz >= d - 2 or (nx, ny, nz) in seen:
                        continue
                    if grid[nz][j] != 3 and not stands(nx, ny, nz):
                        continue
                    seen.add((nx, ny, nz))
                    queue.append((nx, ny, nz))
                    if (nx, ny) != (x, y):
                        break
        return seen

    def render(self):
        header = [
            f"mapname:{self.ident}",
            f"title:{self.title}",
            f"maxx:{self.width}",
            f"maxy:{self.depth}",
            f"maxz:{self.height}",
            "fixtures:authored",
        ]
        header += [f"surface:{m}:{SURFACES[m]}" for m in sorted(self.used_surfaces)]
        return "\n".join(header + self.lines) + "\n"

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8", newline="\n")



    def _emit_object(self, preset, x, y, z, name, w, d, h, turn):
        from .presets import PRESETS
        self._objects_emitted += 1
        oid = self._objects_emitted
        p = PRESETS[preset]
        self.emit("object", oid, p["health"], p["bullet"], p["blast"],
                  p["hit"], p["break"], name)
        for a, b, c, e, f, g, mat, solid in p["parts"]:
            if turn % 4 == 1:
                a, b, c, e = 1 - e, 1 - c, a, b
            elif turn % 4 == 2:
                a, b, c, e = 1 - b, 1 - a, 1 - e, 1 - c
            elif turn % 4 == 3:
                a, b, c, e = c, e, 1 - b, 1 - a
            self.emit("objectpart", oid,
                      round(x + a * w, 3), round(x + b * w, 3),
                      round(y + c * d, 3), round(y + e * d, 3),
                      round(z + f * h, 3), round(z + g * h, 3), mat, solid)


def _absorption(wall):
    """What a boundary is made of, in the terms the acoustics use: metal and
    tile ring, carpet and cloth swallow, concrete and stone sit between."""
    w = wall.lower()
    for word, answer in (("steel", "metal"), ("hull", "metal"), ("shutter", "metal"),
                         ("glass", "glass"), ("timber", "wood"), ("hoarding", "wood"),
                         ("curtain", "cloth"), ("hedge", "cloth"),
                         ("chainlink", "metal"), ("railing", "metal"),
                         ("earth", "dirt"), ("rock", "stone"), ("cliff", "stone"),
                         ("composite", "plastic")):
        if word in w:
            return answer
    return "concrete"