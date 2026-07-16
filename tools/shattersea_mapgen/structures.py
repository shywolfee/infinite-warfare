"""Mid-level structures built on the Map primitives in lib.py."""
from lib import Map, GROUND_TOP, ROOM_TOP, WALL_Z, FLOOR2_Z, WALL2_Z, DOOR_OPEN

SIDE_OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}


def door_gap(side, x1, x2, y1, y2, half=3):
    """Return (side, a, b) for an entrance centred on the correct wall: for N/S
    walls the gap is an X-range, for E/W walls it is a Y-range."""
    if side in ("N", "S"):
        c = (x1 + x2) // 2
    else:
        c = (y1 + y2) // 2
    return (side, c - half, c + half)


# ---------------------------------------------------------------------------
# Streets: a road with curbs and sidewalks on both sides, fully zoned.
# ---------------------------------------------------------------------------
def street_ns(m, name, road_x1, road_x2, y1, y2, sidewalk=3, curb=True,
              road_t="concrete5", sw_t="concrete2", broken=False):
    """North-south street. Returns dict with road bounds for intersections."""
    m.tile(road_x1, road_x2, y1, y2, 0, 0, road_t)
    m.zone(road_x1, road_x2, y1, y2, 0, GROUND_TOP, name)
    wx = road_x1
    ex = road_x2
    if curb:
        m.tile(road_x1 - 1, road_x1 - 1, y1, y2, 0, 0, "stone")
        m.zone(road_x1 - 1, road_x1 - 1, y1, y2, 0, GROUND_TOP, "west curb of " + name)
        m.tile(road_x2 + 1, road_x2 + 1, y1, y2, 0, 0, "stone")
        m.zone(road_x2 + 1, road_x2 + 1, y1, y2, 0, GROUND_TOP, "east curb of " + name)
        wx = road_x1 - 1
        ex = road_x2 + 1
    if sidewalk:
        swt = "cement" if broken else sw_t
        adj = " (cracked)" if broken else ""
        m.tile(wx - sidewalk, wx - 1, y1, y2, 0, 0, swt)
        m.zone(wx - sidewalk, wx - 1, y1, y2, 0, GROUND_TOP, "west sidewalk of " + name + adj)
        m.tile(ex + 1, ex + sidewalk, y1, y2, 0, 0, swt)
        m.zone(ex + 1, ex + sidewalk, y1, y2, 0, GROUND_TOP, "east sidewalk of " + name + adj)
    return {"orient": "ns", "x1": road_x1, "x2": road_x2, "y1": y1, "y2": y2, "name": name}


def street_ew(m, name, road_y1, road_y2, x1, x2, sidewalk=3, curb=True,
              road_t="concrete5", sw_t="concrete2", broken=False):
    """East-west street."""
    m.tile(x1, x2, road_y1, road_y2, 0, 0, road_t)
    m.zone(x1, x2, road_y1, road_y2, 0, GROUND_TOP, name)
    sy = road_y1
    ny = road_y2
    if curb:
        m.tile(x1, x2, road_y1 - 1, road_y1 - 1, 0, 0, "stone")
        m.zone(x1, x2, road_y1 - 1, road_y1 - 1, 0, GROUND_TOP, "south curb of " + name)
        m.tile(x1, x2, road_y2 + 1, road_y2 + 1, 0, 0, "stone")
        m.zone(x1, x2, road_y2 + 1, road_y2 + 1, 0, GROUND_TOP, "north curb of " + name)
        sy = road_y1 - 1
        ny = road_y2 + 1
    if sidewalk:
        swt = "cement" if broken else sw_t
        adj = " (cracked)" if broken else ""
        m.tile(x1, x2, sy - sidewalk, sy - 1, 0, 0, swt)
        m.zone(x1, x2, sy - sidewalk, sy - 1, 0, GROUND_TOP, "south sidewalk of " + name + adj)
        m.tile(x1, x2, ny + 1, ny + sidewalk, 0, 0, swt)
        m.zone(x1, x2, ny + 1, ny + sidewalk, 0, GROUND_TOP, "north sidewalk of " + name + adj)
    return {"orient": "ew", "x1": x1, "x2": x2, "y1": road_y1, "y2": road_y2, "name": name}


def intersection(m, a, b, road_t="concrete5"):
    """Overlay an intersection zone where two streets' roadways cross."""
    if a["orient"] == "ns":
        ns, ew = a, b
    else:
        ns, ew = b, a
    x1, x2 = ns["x1"], ns["x2"]
    y1, y2 = ew["y1"], ew["y2"]
    m.tile(x1, x2, y1, y2, 0, 0, road_t)
    m.zone(x1, x2, y1, y2, 0, GROUND_TOP,
           "intersection of " + ns["name"] + " and " + ew["name"])


# ---------------------------------------------------------------------------
# Buildings.
# ---------------------------------------------------------------------------
def building_shell(m, name, x1, x2, y1, y2, floor_t="tile1", wall_t="wallbrick",
                   ztop=WALL_Z, roof_t="concrete2", entrances=None,
                   roof_access=None, wall_awareness=True):
    """Emit floor, four perimeter walls (with entrance gaps), ceiling, roof and
    the four exterior wall-awareness zones. entrances = list of (side, a, b)
    where side in NSEW and a,b are the along-wall gap coordinates.
    roof_access: None, or ('ladder','N'/'S'/'E'/'W') to put an outdoor ladder up.
    Returns interior walkable bounds (ix1,ix2,iy1,iy2)."""
    entrances = entrances or [("S", (x1 + x2) // 2 - 4, (x1 + x2) // 2 + 4)]
    m.tile(x1, x2, y1, y2, 0, 0, floor_t)
    # gaps per side
    gN = [(a, b) for s, a, b in entrances if s == "N"]
    gS = [(a, b) for s, a, b in entrances if s == "S"]
    gE = [(a, b) for s, a, b in entrances if s == "E"]
    gW = [(a, b) for s, a, b in entrances if s == "W"]
    m.wall_y(y2, x1, x2, ztop, wall_t, gN)   # north wall
    m.wall_y(y1, x1, x2, ztop, wall_t, gS)   # south wall
    m.wall_x(x1, y1, y2, ztop, wall_t, gW)   # west wall
    m.wall_x(x2, y1, y2, ztop, wall_t, gE)   # east wall
    # ceiling + roof
    m.tile(x1, x2, y1, y2, ztop, ztop, wall_t)
    m.tile(x1, x2, y1, y2, ztop + 1, ztop + 1, roof_t)
    m.zone(x1, x2, y1, y2, ztop + 1, ztop + 8, "roof of " + name)
    # exterior wall awareness (one tile outside each wall)
    if wall_awareness:
        m.zone(x1 - 1, x1 - 1, y1, y2, 0, GROUND_TOP, name + " west wall")
        m.zone(x2 + 1, x2 + 1, y1, y2, 0, GROUND_TOP, name + " east wall")
        m.zone(x1, x2, y1 - 1, y1 - 1, 0, GROUND_TOP, name + " south wall")
        m.zone(x1, x2, y2 + 1, y2 + 1, 0, GROUND_TOP, name + " north wall")
    # entrance zones (just inside the gap)
    for s, a, b in entrances:
        if s == "N":
            m.zone_raw(a, b, y2 - 2, y2, 0, GROUND_TOP, name + " entrance")
        elif s == "S":
            m.zone_raw(a, b, y1, y1 + 2, 0, GROUND_TOP, name + " entrance")
        elif s == "E":
            m.zone_raw(x2 - 2, x2, a, b, 0, GROUND_TOP, name + " entrance")
        elif s == "W":
            m.zone_raw(x1, x1 + 2, a, b, 0, GROUND_TOP, name + " entrance")
    # optional exterior ladder onto the roof
    if roof_access:
        kind, side = roof_access
        if side == "N":
            lx = (x1 + x2) // 2
            m.tile(lx - 1, lx + 1, y2 + 1, y2 + 1, 0, ztop + 1, "ladder1")
            m.zone(lx - 1, lx + 1, y2 + 1, y2 + 1, 0, ztop + 1, kind + " to " + name + " roof")
        elif side == "S":
            lx = (x1 + x2) // 2
            m.tile(lx - 1, lx + 1, y1 - 1, y1 - 1, 0, ztop + 1, "ladder1")
            m.zone(lx - 1, lx + 1, y1 - 1, y1 - 1, 0, ztop + 1, kind + " to " + name + " roof")
        elif side == "E":
            ly = (y1 + y2) // 2
            m.tile(x2 + 1, x2 + 1, ly - 1, ly + 1, 0, ztop + 1, "ladder1")
            m.zone(x2 + 1, x2 + 1, ly - 1, ly + 1, 0, ztop + 1, kind + " to " + name + " roof")
        elif side == "W":
            ly = (y1 + y2) // 2
            m.tile(x1 - 1, x1 - 1, ly - 1, ly + 1, 0, ztop + 1, "ladder1")
            m.zone(x1 - 1, x1 - 1, ly - 1, ly + 1, 0, ztop + 1, kind + " to " + name + " roof")
    return (x1 + 1, x2 - 1, y1 + 1, y2 - 1)


def interior_fill(m, name, ix1, ix2, iy1, iy2, ztop=ROOM_TOP):
    """Fallback interior zone so no walkable interior tile is unnamed."""
    m.zone(ix1, ix2, iy1, iy2, 0, ztop, name)


def room(m, x1, x2, y1, y2, name, ztop=ROOM_TOP):
    m.zone(x1, x2, y1, y2, 0, ztop, name)


def corridor(m, x1, x2, y1, y2, name, ztop=ROOM_TOP):
    m.zone(x1, x2, y1, y2, 0, ztop, name)


def doorway(m, x1, x2, y1, y2, name):
    m.zone_raw(x1, x2, y1, y2, 0, GROUND_TOP, name)


def desk(m, x1, x2, y1, y2, name):
    m.furniture(x1, x2, y1, y2, 3, name, "hardwood")


def chair(m, x1, x2, y1, y2, name):
    m.furniture(x1, x2, y1, y2, 2, name, "hardwood")


def counter(m, x1, x2, y1, y2, name):
    m.furniture(x1, x2, y1, y2, 3, name, "hardwood")


def bed(m, x1, x2, y1, y2, name):
    m.furniture(x1, x2, y1, y2, 2, name, "hardwood2")


# ---------------------------------------------------------------------------
# Staircases: a ladder1 column you climb with Up/Down, inside a stairwell,
# optionally flanked by railings.
# ---------------------------------------------------------------------------
def staircase(m, x1, x2, y1, y2, zbot, ztop, name, railings="both",
              run="y"):
    """A stair shaft filling x1..x2,y1..y2 between zbot and ztop.
    run='y': ladder column laid along the west edge; railings on E/W sides.
    railings: 'both','left','right','none' (left=west, right=east)."""
    # the climb column
    if run == "y":
        m.tile(x1, x1, y1, y2, zbot, ztop, "ladder1")
    else:
        m.tile(x1, x2, y1, y1, zbot, ztop, "ladder1")
    m.zone(x1, x2, y1, y2, zbot, ztop, name)
    # low railings (wallfence) hugging the shaft sides
    left = railings in ("both", "left")
    right = railings in ("both", "right")
    railtop = zbot + 2
    if run == "y":
        if left:
            m.tile(x1, x1, y1, y2, zbot, railtop, "wallfence")
            m.zone(x1, x1, y1, y2, zbot, zbot + 7, name + " west railing")
        if right:
            m.tile(x2, x2, y1, y2, zbot, railtop, "wallfence")
            m.zone(x2, x2, y1, y2, zbot, zbot + 7, name + " east railing")


# ---------------------------------------------------------------------------
# Second floor / basement decks.
# ---------------------------------------------------------------------------
def add_floor2(m, name, x1, x2, y1, y2, deck_z=FLOOR2_Z, deck_t="hardwood"):
    """Lay a second-floor deck. The outer walls of the shell must reach above
    deck_z (build the shell with ztop=WALL2_Z)."""
    m.tile(x1 + 1, x2 - 1, y1 + 1, y2 - 1, deck_z, deck_z, deck_t)
    m.zone(x1 + 1, x2 - 1, y1 + 1, y2 - 1, deck_z, deck_z + ROOM_TOP, name)


def office_block(m, name, x1, x2, y1, y2, floor_t="tile1", wall_t="wallbrick",
                 n_per_side=3, entrance_side="S", start_no=101, ztop=WALL_Z,
                 roof_access=None, lobby_name=None, front_counter=False):
    """A building with a central north-south corridor and n offices per side,
    each with its own doorway, desk and chair. Mirrors the bank/office pattern."""
    ex = (x1 + x2) // 2
    if entrance_side not in ("N", "S"):  # lobby/corridor layout runs north-south
        m.errors.append("office_block %s: entrance side %s coerced to S" % (name, entrance_side))
        entrance_side = "S"
    ent = [door_gap(entrance_side, x1, x2, y1, y2, half=4)]
    ix1, ix2, iy1, iy2 = building_shell(m, name, x1, x2, y1, y2, floor_t, wall_t,
                                        ztop, entrances=ent, roof_access=roof_access)
    interior_fill(m, name + " interior", ix1, ix2, iy1, iy2)
    cx = (ix1 + ix2) // 2
    wcol, ecol = cx - 2, cx + 2          # corridor walls
    # A front lobby strip just inside the entrance.
    lobby_depth = 10
    if entrance_side == "S":
        ly1, ly2 = iy1, iy1 + lobby_depth
        cor_y1, cor_y2 = ly2 + 1, iy2
    else:
        ly1, ly2 = iy2 - lobby_depth, iy2
        cor_y1, cor_y2 = iy1, ly1 - 1
    room(m, ix1, ix2, ly1, ly2, lobby_name or (name + " lobby"))
    if front_counter:
        counter(m, cx - 12, cx + 12, (ly1 + ly2) // 2, (ly1 + ly2) // 2 + 1, name + " service counter")
    # lobby/corridor divider wall with one doorway
    m.wall_y(cor_y1 - 1, ix1, ix2, ROOM_TOP, wall_t, [(cx - 1, cx + 1)])
    doorway(m, cx - 1, cx + 1, cor_y1 - 1, cor_y1 - 1, name + " inner door")
    # corridor
    corridor(m, wcol + 1, ecol - 1, cor_y1, cor_y2, name + " main corridor")
    seg_h = (cor_y2 - cor_y1 + 1) // n_per_side
    wgaps, egaps = [], []
    no = start_no
    for i in range(n_per_side):
        oy1 = cor_y1 + i * seg_h
        oy2 = cor_y2 if i == n_per_side - 1 else cor_y1 + (i + 1) * seg_h - 1
        oc = (oy1 + oy2) // 2
        wgaps.append((oc - 1, oc + 1))
        egaps.append((oc - 1, oc + 1))
        # west office
        wname = "%s office %d" % (name, no)
        room(m, ix1, wcol - 1, oy1, oy2, wname)
        doorway(m, wcol, wcol, oc - 1, oc + 1, wname + " doorway")
        desk(m, ix1 + 2, ix1 + 7, oc - 1, oc + 1, wname + " desk")
        chair(m, ix1 + 4, ix1 + 5, oc + 2, oc + 3, wname + " chair")
        no += 1
        # east office
        ename = "%s office %d" % (name, no)
        room(m, ecol + 1, ix2, oy1, oy2, ename)
        doorway(m, ecol, ecol, oc - 1, oc + 1, ename + " doorway")
        desk(m, ix2 - 7, ix2 - 2, oc - 1, oc + 1, ename + " desk")
        chair(m, ix2 - 5, ix2 - 4, oc + 2, oc + 3, ename + " chair")
        no += 1
        # partition walls between offices
        if i < n_per_side - 1:
            m.wall_y(oy2, ix1, wcol - 1, ROOM_TOP, wall_t)
            m.wall_y(oy2, ecol + 1, ix2, ROOM_TOP, wall_t)
    # corridor walls with all the office doorway gaps
    m.wall_x(wcol, cor_y1, cor_y2, ROOM_TOP, wall_t, wgaps)
    m.wall_x(ecol, cor_y1, cor_y2, ROOM_TOP, wall_t, egaps)
    return (ix1, ix2, iy1, iy2)


def shop(m, name, x1, x2, y1, y2, floor_t="tile2", wall_t="wallbrick",
         entrance_side="S", ztop=WALL_Z, roof_access=None, back_room=True,
         goods="shelves"):
    """A small shop: sales floor with a counter, and a back store room through
    a door."""
    ex = (x1 + x2) // 2
    ix1, ix2, iy1, iy2 = building_shell(m, name, x1, x2, y1, y2, floor_t, wall_t,
                                        ztop, entrances=[door_gap(entrance_side, x1, x2, y1, y2, 3)],
                                        roof_access=roof_access)
    interior_fill(m, name + " interior", ix1, ix2, iy1, iy2)
    split = iy2 - (iy2 - iy1) // 3
    room(m, ix1, ix2, iy1, split - 1, name + " sales floor")
    counter(m, ix1 + 2, ix2 - 6, (iy1 + split) // 2, (iy1 + split) // 2 + 1, name + " counter")
    m.furniture(ix1 + 1, ix1 + 3, iy1 + 2, split - 2, 3, name + " " + goods, "hardwood")
    m.furniture(ix2 - 3, ix2 - 1, iy1 + 2, split - 2, 3, name + " " + goods, "hardwood")
    if back_room:
        m.wall_y(split, ix1, ix2, ROOM_TOP, wall_t, [(ex - 1, ex + 1)])
        doorway(m, ex - 1, ex + 1, split, split, name + " stockroom door")
        room(m, ix1, ix2, split + 1, iy2, name + " stockroom")
        m.furniture(ix1 + 1, ix1 + 3, split + 2, iy2 - 1, 3, name + " stock shelves", "hardwood")
    return (ix1, ix2, iy1, iy2)


def house(m, name, x1, x2, y1, y2, floor_t="carpet1", wall_t="wallwood",
          entrance_side="S", basement=False, attic=False, second_floor=False,
          railings="both", bilco=False, roof_access=None, driveway=None):
    """A dwelling: entry hall, living room, kitchen, one or two bedrooms and a
    bathroom, optionally with a basement, attic or upper storey."""
    ex = (x1 + x2) // 2
    ztop = WALL2_Z if second_floor else WALL_Z
    ix1, ix2, iy1, iy2 = building_shell(m, name, x1, x2, y1, y2, floor_t, wall_t,
                                        ztop, entrances=[door_gap(entrance_side, x1, x2, y1, y2, 2)],
                                        roof_access=roof_access)
    interior_fill(m, name + " interior", ix1, ix2, iy1, iy2)
    # central hall running north from the entrance
    hall_w = 2
    hx1, hx2 = ex - hall_w, ex + hall_w
    corridor(m, hx1, hx2, iy1, iy2, name + " hallway")
    midy = (iy1 + iy2) // 2
    # west rooms: living room (front) + kitchen (back)
    m.wall_x(hx1 - 1, iy1, iy2, ROOM_TOP, wall_t, [(iy1 + 3, iy1 + 5), (iy2 - 5, iy2 - 3)])
    doorway(m, hx1 - 1, hx1 - 1, iy1 + 3, iy1 + 5, name + " living room doorway")
    doorway(m, hx1 - 1, hx1 - 1, iy2 - 5, iy2 - 3, name + " kitchen doorway")
    m.wall_y(midy, ix1, hx1 - 1, ROOM_TOP, wall_t)
    room(m, ix1, hx1 - 2, iy1, midy - 1, name + " living room")
    m.furniture(ix1 + 1, ix1 + 5, iy1 + 1, iy1 + 3, 2, name + " sofa", "hardwood2")
    m.furniture(ix1 + 2, ix1 + 5, midy - 4, midy - 2, 2, name + " coffee table", "hardwood")
    room(m, ix1, hx1 - 2, midy + 1, iy2, name + " kitchen")
    counter(m, ix1 + 1, hx1 - 3, iy2 - 2, iy2 - 1, name + " kitchen counter")
    # east rooms: bedroom (front) + bathroom + bedroom (back)
    m.wall_x(hx2 + 1, iy1, iy2, ROOM_TOP, wall_t, [(iy1 + 3, iy1 + 5), (iy2 - 5, iy2 - 3)])
    doorway(m, hx2 + 1, hx2 + 1, iy1 + 3, iy1 + 5, name + " bedroom doorway")
    doorway(m, hx2 + 1, hx2 + 1, iy2 - 5, iy2 - 3, name + " back room doorway")
    m.wall_y(midy, hx2 + 1, ix2, ROOM_TOP, wall_t)
    room(m, hx2 + 2, ix2, iy1, midy - 1, name + " bedroom")
    bed(m, ix2 - 4, ix2 - 1, iy1 + 1, iy1 + 4, name + " bed")
    room(m, hx2 + 2, ix2, midy + 1, iy2, name + " back bedroom")
    bed(m, ix2 - 4, ix2 - 1, iy2 - 4, iy2 - 1, name + " bed")

    # vertical connections
    if basement:
        sh = (ix1 + 1, ix1 + 2, midy - 1, midy + 1)
        add_basement(m, name + " basement", ix1, ix2, iy1, iy2, sh,
                     railings=railings,
                     bilco=(x2 + 2, x2 + 3, y1 + 2, y1 + 4) if bilco else None)
        # cut the hall wall so the cellar stair is reachable from the hall
        doorway(m, hx1 - 1, hx1 - 1, midy - 1, midy + 1, name + " cellar door")
    if second_floor:
        staircase(m, hx1 - 1, hx1, iy2 - 4, iy2, 0, FLOOR2_Z, name + " staircase",
                  railings=railings)
        add_floor2(m, name + " upstairs landing", x1, x2, y1, y2)
    if attic and not second_floor:  # an attic and an upper storey would collide
        ax = ex
        m.tile(ax, ax, iy2 - 3, iy2, 0, WALL_Z, "ladder1")
        m.zone(ax, ax, iy2 - 3, iy2, 0, WALL_Z, name + " attic ladder")
        m.tile(ix1, ix2, iy1, iy2, WALL_Z, WALL_Z, "plank")
        m.zone(ix1, ix2, iy1, iy2, WALL_Z + 1, WALL_Z + ROOM_TOP, name + " attic")
        # a stack of crates up in the attic (raised solid block + cap zone)
        m.tile(ix1 + 1, ix1 + 3, iy1 + 1, iy1 + 3, WALL_Z + 1, WALL_Z + 3, "plank")
        m.zone_raw(ix1 + 1, ix1 + 3, iy1 + 1, iy1 + 3, WALL_Z + 4, WALL_Z + 10, "on top of " + name + " attic crates")
    if driveway:
        dx1, dx2, dy1, dy2 = driveway
        m.tile(dx1, dx2, dy1, dy2, 0, 0, "concrete10")
        m.zone(dx1, dx2, dy1, dy2, 0, GROUND_TOP, name + " driveway")
    return (ix1, ix2, iy1, iy2)


def add_basement(m, name, x1, x2, y1, y2, shaft, depth=14,
                 floor_t="concrete10", railings="both", bilco=None):
    """Dig a basement under a footprint. `shaft` = (sx1,sx2,sy1,sy2) location of
    the interior stair down (must sit inside x1..x2,y1..y2). `bilco` = (bx1,bx2,
    by1,by2) optional exterior bulkhead the player can climb out of into the yard.
    Returns basement floor Z."""
    bz = -depth
    # basement floor + containing walls (below ground only)
    m.tile(x1, x2, y1, y2, bz, bz, floor_t)
    m.tile(x1 - 1, x1 - 1, y1, y2, bz, -1, "wallstone")
    m.tile(x2 + 1, x2 + 1, y1, y2, bz, -1, "wallstone")
    m.tile(x1, x2, y1 - 1, y1 - 1, bz, -1, "wallstone")
    m.tile(x1, x2, y2 + 1, y2 + 1, bz, -1, "wallstone")
    m.zone(x1, x2, y1, y2, bz, bz + ROOM_TOP, name)
    # interior stair shaft down from the ground floor
    sx1, sx2, sy1, sy2 = shaft
    m.tile(sx1, sx2, sy1, sy2, bz, 0, "ladder1")
    m.zone(sx1, sx2, sy1, sy2, bz, 0, name + " stairs")
    if railings in ("both", "left"):
        m.tile(sx1 - 1, sx1 - 1, sy1, sy2, bz, bz + 2, "wallfence")
    if railings in ("both", "right"):
        m.tile(sx2 + 1, sx2 + 1, sy1, sy2, bz, bz + 2, "wallfence")
    # optional exterior bilco / bulkhead exit into the yard
    if bilco:
        bx1, bx2, by1, by2 = bilco
        m.tile(bx1, bx2, by1, by2, bz, 0, "ladder1")
        m.zone(bx1, bx2, by1, by2, bz, 0, name + " bulkhead")
        m.zone_raw(bx1, bx2, by1 - 1, by1 - 1, 0, GROUND_TOP, "cellar bulkhead doors")
    return bz
