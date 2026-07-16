"""West Meridian: the waterfront. Oceanfront Drive runs from the Ivory Bridge
down to the docks, with four side streets. Home to the harbour, fishing piers,
the Fishing Bureau, the Crescent Market, Old Mill's Park and a closed
restaurant with a basement."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("WEST MERIDIAN - the waterfront")

    # --- Oceanfront Drive: from the Ivory Bridge south landing to the docks ---
    ocean = S.street_ns(m, "Oceanfront Drive", 296, 305, 200, 606)
    # Four side streets spilling west off Oceanfront Drive toward the water
    wharf = S.street_ew(m, "Wharf Street", 250, 257, 176, 292, sidewalk=2)
    netmaker = S.street_ew(m, "Netmaker Row", 350, 357, 176, 292, sidewalk=2)
    saltgrass = S.street_ew(m, "Saltgrass Street", 450, 457, 176, 292, sidewalk=2)
    gull = S.street_ew(m, "Gull Street", 540, 547, 200, 292, sidewalk=2)
    for ew in (wharf, netmaker, saltgrass, gull):
        S.intersection(m, ocean, ew)
    m.poi(300, 606, 0, "the Ivory Bridge landing on Oceanfront Drive")

    # --- Harbour and docks ---
    m.section("Meridian Harbour, the docks and the fishing piers")
    # harbour water west of the docks
    m.tile(60, 179, 180, 340, 0, 0, "water1")
    m.zone(60, 179, 180, 340, 0, GROUND_TOP, "Meridian Harbour")
    m.src(60, 179, 180, 340, 0, GROUND_TOP, "ocean.ogg", -7)
    # the docks: a plank platform along the waterfront
    m.tile(182, 292, 196, 244, 0, 0, "plank")
    m.zone(182, 292, 196, 244, 0, GROUND_TOP, "the Meridian Docks")
    m.src(182, 292, 196, 244, 0, GROUND_TOP, "waves2.ogg", -6)
    m.poi(237, 220, 0, "the Meridian Docks")
    m.ispawn(186, 288, 200, 240, 0, 0, 5000, 3,
             ["empty_bucket", "health_potion", "rock", "bag"])
    # three fishing piers reaching west into the harbour
    _pier(m, "the North Fishing Pier", 70, 180, 206, 212)
    _pier(m, "the Central Fishing Pier", 70, 180, 258, 264)
    _pier(m, "the South Fishing Pier", 70, 180, 310, 316)

    # --- The Fishing Bureau ---
    m.comment("The Fishing Bureau")
    bix = S.building_shell(m, "the Fishing Bureau", 196, 252, 262, 312,
                           floor_t="hardwood2", wall_t="wallwood",
                           entrances=[("E", 282, 290)])
    ix1, ix2, iy1, iy2 = bix
    S.interior_fill(m, "the Fishing Bureau office", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2, "the Fishing Bureau office")
    S.counter(m, ix1 + 2, ix1 + 3, iy1 + 2, iy2 - 2, "the licence counter")
    S.desk(m, ix2 - 7, ix2 - 2, (iy1 + iy2) // 2, (iy1 + iy2) // 2 + 1, "the harbourmaster's desk")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 6000, 2,
             ["health_potion", "empty_bucket"])

    # --- The Crescent Market (Meridian's largest marketplace) ---
    m.section("The Crescent Market")
    _crescent_market(m)

    # --- Old Mill's Park (dilapidated, near the docks) ---
    m.section("Old Mill's Park (dilapidated)")
    _old_mills_park(m)

    # --- The closed restaurant with a basement ---
    m.section("The Gilded Perch (a closed restaurant)")
    _gilded_perch(m)

    # --- North of the canal: Harbourview warehouses and the lighthouse ---
    m.section("Harbourview - warehouses north of the canal")
    hv = S.street_ns(m, "Harbourview Road", 300, 307, 700, 1140)
    m.comment("Harbourview warehouses")
    _warehouse(m, "the North Harbour Warehouse", 196, 286, 760, 860)
    _warehouse(m, "the Saltworks Warehouse", 196, 286, 900, 1000)
    S.shop(m, "the Harbourview Chandlery", 330, 392, 780, 830, floor_t="hardwood",
           wall_t="wallwood", entrance_side="W", goods="chandlery shelves")
    # the lighthouse at the far north-west tip
    m.comment("Cape Meridian Lighthouse")
    lx1, lx2, ly1, ly2 = 170, 190, 1080, 1100
    S.building_shell(m, "Cape Meridian Lighthouse", lx1, lx2, ly1, ly2,
                     floor_t="stone", wall_t="wallstone", ztop=60,
                     entrances=[("E", 1088, 1093)])
    m.tile(lx1 + 1, lx1 + 2, ly1 + 1, ly2 - 1, 0, 61, "ladder1")
    m.zone(lx1 + 1, lx1 + 2, ly1 + 1, ly2 - 1, 0, 61, "the lighthouse stairs")
    m.tile(lx1 + 3, lx1 + 3, ly1 + 1, ly2 - 1, 0, 2, "wallfence")
    m.tile(lx1 + 1, lx2 - 1, ly1 + 1, ly2 - 1, 61, 61, "metal2")
    m.zone(lx1 + 1, lx2 - 1, ly1 + 1, ly2 - 1, 61, 68, "the lighthouse lantern room")
    m.src(lx1, lx2, ly1, ly2, 0, 68, "wind2.ogg", -8)
    m.poi((lx1 + lx2) // 2, (ly1 + ly2) // 2, 61, "Cape Meridian Lighthouse")

    m.src(C.WEST_X1, C.WEST_X2, C.ISL_Y1, C.ISL_Y2, 0, GROUND_TOP, "ocean.ogg", -13)


def _pier(m, name, x1, x2, y1, y2):
    m.tile(x1, x2, y1, y2, 0, 0, "plank")
    m.zone(x1, x2, y1, y2, 0, GROUND_TOP, name)
    m.tile(x1, x2, y1 - 1, y1 - 1, 0, 3, "wallfence")
    m.tile(x1, x2, y2 + 1, y2 + 1, 0, 3, "wallfence")
    m.zone(x1, x2, y1 - 2, y1 - 2, 0, GROUND_TOP, name + " south railing")
    m.zone(x1, x2, y2 + 2, y2 + 2, 0, GROUND_TOP, name + " north railing")
    m.src(x1, x2, y1, y2, 0, GROUND_TOP, "waves2.ogg", -6)
    m.poi(x1 + 6, (y1 + y2) // 2, 0, name)


def _crescent_market(m):
    name = "the Crescent Market"
    x1, x2, y1, y2 = 330, 448, 360, 474
    ex = (x1 + x2) // 2
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, name, x1, x2, y1, y2, floor_t="concrete12", wall_t="wallbrick",
        ztop=20, entrances=[("E", (y1 + y2) // 2 - 4, (y1 + y2) // 2 + 4),
                            ("S", ex - 3, ex + 3), ("N", ex - 3, ex + 3)],
        roof_access=("a ladder", "W"))
    S.interior_fill(m, "the market hall", ix1, ix2, iy1, iy2)
    # central north-south aisle
    aisle_x1, aisle_x2 = ex - 4, ex + 4
    S.corridor(m, aisle_x1, aisle_x2, iy1, iy2, "the central aisle of the Crescent Market")
    m.src(ix1, ix2, iy1, iy2, 0, 20, "farm.ogg", -9)
    # rows of stalls on each side of the aisle
    stallno = 1
    for row_y in range(iy1 + 4, iy2 - 8, 16):
        for sxa, sxb in ((ix1 + 2, aisle_x1 - 2), (aisle_x2 + 2, ix2 - 2)):
            m.furniture(sxa, sxb, row_y, row_y + 3, 3,
                        "market stall %d" % stallno, "hardwood")
            stallno += 1
    m.poi(ex, iy1, 0, "the Crescent Market")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 4000, 5,
             ["health_potion", "energetic_potion_red", "energetic_potion_green",
              "empty_bucket", "bag", "box"])


def _old_mills_park(m):
    x1, x2, y1, y2 = 330, 446, 196, 336
    m.tile(x1, x2, y1, y2, 0, 0, "grass")
    m.zone(x1, x2, y1, y2, 0, GROUND_TOP, "Old Mill's Park (overgrown and dilapidated)")
    m.src(x1, x2, y1, y2, 0, GROUND_TOP, "forest.ogg", -9)
    # a broken, weed-choked path
    m.tile(x1 + 10, x1 + 14, y1, y2, 0, 0, "cement")
    m.zone(x1 + 10, x1 + 14, y1, y2, 0, GROUND_TOP, "the cracked park path")
    # scattered trees and a couple of broken benches
    for tx, ty in ((x1 + 30, y1 + 30), (x1 + 70, y1 + 90), (x1 + 95, y1 + 40),
                   (x1 + 45, y1 + 110)):
        m.tile(tx, tx, ty, ty, 0, 8, "tree")
        m.zone(tx, tx, ty, ty, 0, GROUND_TOP, "an overgrown tree in Old Mill's Park")
    m.furniture(x1 + 20, x1 + 26, y1 + 60, y1 + 61, 2, "a broken park bench")
    # the ruined mill, with a cellar you can drop into
    mix = S.building_shell(m, "the ruined old mill", x2 - 40, x2 - 4, y2 - 40, y2 - 4,
                           floor_t="plank", wall_t="wallstone", ztop=14,
                           entrances=[("S", x2 - 26, x2 - 18)])
    ix1, ix2, iy1, iy2 = mix
    S.interior_fill(m, "the ruined mill floor", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2, "the ruined mill floor")
    S.add_basement(m, "the old mill cellar", ix1, ix2, iy1, iy2,
                   shaft=(ix1 + 1, ix1 + 2, (iy1 + iy2) // 2 - 1, (iy1 + iy2) // 2 + 1),
                   railings="none")
    S.doorway(m, ix1 + 1, ix1 + 2, (iy1 + iy2) // 2 - 1, (iy1 + iy2) // 2 + 1,
              "the mill cellar hatch")
    m.poi((x1 + x2) // 2, (y1 + y2) // 2, 0, "Old Mill's Park")


def _gilded_perch(m):
    name = "the Gilded Perch"
    x1, x2, y1, y2 = 336, 404, 500, 556
    # boarded-up front on Saltgrass side; the only way in is the service door
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, name, x1, x2, y1, y2, floor_t="tile2", wall_t="wallbrick", ztop=14,
        entrances=[("N", x1 + 6, x1 + 10)])
    S.interior_fill(m, "the shuttered dining room", ix1, ix2, iy1, iy2)
    S.zone_note = None
    m.zone_raw(x1 + 20, x2 - 6, y1 - 1, y1 - 1, 0, GROUND_TOP,
               "the boarded-up front of the Gilded Perch")
    m.zone_raw(x1 + 6, x1 + 10, y2 + 1, y2 + 1, 0, GROUND_TOP,
               "the restaurant service entrance")
    # dining room (front) and kitchen (back), split by a wall with a door
    split = iy1 + (iy2 - iy1) // 2
    S.room(m, ix1, ix2, split + 1, iy2, "the shuttered dining room")
    for bx in range(ix1 + 3, ix2 - 4, 10):
        m.furniture(bx, bx + 4, split + 4, split + 6, 2, "a dust-covered table")
    ex = (ix1 + ix2) // 2
    m.wall_y(split, ix1, ix2, ROOM_TOP, "wallbrick", [(ex - 1, ex + 1)])
    S.doorway(m, ex - 1, ex + 1, split, split, "the kitchen doorway")
    S.room(m, ix1, ix2, iy1, split - 1, "the restaurant kitchen")
    S.counter(m, ix1 + 2, ix2 - 8, iy1 + 2, iy1 + 3, "the kitchen line")
    # a staircase down from the kitchen into the basement
    S.add_basement(m, "the restaurant basement", ix1, ix2, iy1, iy2,
                   shaft=(ix2 - 2, ix2 - 1, iy1 + 2, iy1 + 5), depth=14,
                   railings="both")
    # wine racks down in the basement (raised block at basement level + cap)
    m.tile(ix1 + 2, ix1 + 6, iy1 + 2, iy1 + 8, -14, -12, "hardwood")
    m.zone_raw(ix1 + 2, ix1 + 6, iy1 + 2, iy1 + 8, -14, -8, "the wine racks")
    m.zone_raw(ix1 + 2, ix1 + 6, iy1 + 2, iy1 + 8, -11, -5, "on top of the wine racks")
    m.src(ix1, ix2, iy1, iy2, 0, 14, "wind2.ogg", -12)
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, -14, -14, 6000, 3,
             ["health_potion", "frag_grenade", "smoke_bomb"])
    m.poi((x1 + x2) // 2, y2, 0, "the Gilded Perch (closed)")


def _warehouse(m, name, x1, x2, y1, y2):
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, name, x1, x2, y1, y2, floor_t="concrete10", wall_t="metal2", ztop=24,
        entrances=[("W", (y1 + y2) // 2 - 4, (y1 + y2) // 2 + 4)],
        roof_access=("a ladder", "N"))
    S.interior_fill(m, name + " floor", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2, name + " floor")
    for cx in range(ix1 + 4, ix2 - 6, 14):
        m.furniture(cx, cx + 8, iy1 + 4, iy2 - 4, 4, "stacked cargo crates", "plank")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 6000, 3,
             ["box", "bag", "empty_bucket", "rock"])
