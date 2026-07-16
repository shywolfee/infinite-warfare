"""North Meridian: six main streets around Meridian Plaza, plus the civic core
(bank, city hall, cathedral, library, apartments and shops)."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("NORTH MERIDIAN - streets, plaza and civic core")
    x1, x2 = C.CEN_X1 + 4, C.CEN_X2 - 4
    yb = C.NORTH_Y1 + 6
    yt = C.ISL_Y2 - 6

    # --- Three north-south avenues ---
    kings = S.street_ns(m, "Kingsway", 520, 527, yb, yt)
    merid = S.street_ns(m, "Meridian Avenue", 636, 643, yb, yt)
    beacon = S.street_ns(m, "Beacon Street", 748, 755, yb, yt)
    # --- Three east-west streets ---
    cath = S.street_ew(m, "Cathedral Row", 760, 767, x1, x2)
    plaza_st = S.street_ew(m, "Plaza Street", 896, 903, x1, x2)
    northgate = S.street_ew(m, "Northgate Road", 1032, 1039, x1, x2)
    for ns in (kings, merid, beacon):
        for ew in (cath, plaza_st, northgate):
            S.intersection(m, ns, ew)

    # --- Meridian Plaza (north-central) ---
    m.comment("Meridian Plaza")
    px1, px2, py1, py2 = 580, 712, 916, 1024
    m.tile(px1, px2, py1, py2, 0, 0, "concrete12")
    m.zone(px1, px2, py1, py2, 0, GROUND_TOP, "Meridian Plaza")
    m.src(px1, px2, py1, py2, 0, GROUND_TOP, "calm.ogg", -8)
    # central fountain
    fx1, fx2, fy1, fy2 = 636, 656, 962, 982
    m.tile(fx1, fx2, fy1, fy2, 0, 0, "water1")
    m.zone(fx1, fx2, fy1, fy2, 0, GROUND_TOP, "the fountain at the centre of Meridian Plaza")
    m.src(fx1, fx2, fy1, fy2, 0, GROUND_TOP, "waves2.ogg", -8)
    m.poi((fx1 + fx2) // 2, (fy1 + fy2) // 2, 0, "the Meridian Plaza fountain")
    # benches around the plaza
    for bx in (596, 690):
        m.furniture(bx, bx + 6, 930, 931, 2, "plaza bench")
        m.furniture(bx, bx + 6, 1010, 1011, 2, "plaza bench")
    m.ispawn(px1 + 4, px2 - 4, py1 + 4, py2 - 4, 0, 0, 4000, 4,
             ["health_potion", "energetic_potion_blue", "smoke_bomb", "frag_grenade"])

    # --- First Meridian Bank (hero building, south-west block) ---
    m.comment("First Meridian Bank")
    S.office_block(m, "First Meridian Bank", 548, 622, 786, 878,
                   floor_t="tile1", n_per_side=3, entrance_side="S",
                   lobby_name="the bank lobby", front_counter=True,
                   roof_access=("a ladder", "N"))
    m.ispawn(552, 618, 790, 800, 0, 0, 5000, 3,
             ["health_potion", "frag_grenade", "smoke_bomb", "bunker_key"])

    # --- Meridian City Hall (south-east block, two storeys) ---
    m.comment("Meridian City Hall")
    S.office_block(m, "Meridian City Hall", 662, 736, 786, 880,
                   floor_t="hardwood", wall_t="wallstone", n_per_side=3,
                   entrance_side="S", lobby_name="the city hall rotunda")
    m.poi(699, 786, 0, "Meridian City Hall")

    # --- Meridian Cathedral (on Cathedral Row, west block) ---
    m.comment("Meridian Cathedral")
    cix = S.building_shell(m, "Meridian Cathedral", 486, 512, 712, 748,
                           floor_t="tile2", wall_t="wallstone", ztop=20,
                           entrances=[("N", 496, 502)],
                           roof_access=None)
    ix1, ix2, iy1, iy2 = cix
    S.interior_fill(m, "the cathedral nave", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2 - 8, "the cathedral nave")
    for py in range(iy1 + 3, iy2 - 10, 5):
        m.furniture(ix1 + 1, ix1 + 4, py, py + 1, 2, "cathedral pew")
        m.furniture(ix2 - 4, ix2 - 1, py, py + 1, 2, "cathedral pew")
    mid = (ix1 + ix2) // 2
    m.wall_y(iy2 - 8, ix1, ix2, ROOM_TOP, "wallstone", [(mid - 1, mid + 1)])
    S.doorway(m, mid - 1, mid + 1, iy2 - 8, iy2 - 8, "cathedral chancel doorway")
    S.room(m, ix1, ix2, iy2 - 7, iy2, "the cathedral chancel")
    S.counter(m, ix1 + 3, ix2 - 3, iy2 - 3, iy2 - 2, "the cathedral altar")
    m.src(ix1, ix2, iy1, iy2, 0, 20, "calm.ogg", -10)

    # --- Northside Apartments (north-west of plaza, two storeys) ---
    m.comment("Northside Apartments")
    S.office_block(m, "Northside Apartments", 486, 560, 928, 1020,
                   floor_t="carpet1", wall_t="wallbrick", n_per_side=3,
                   start_no=1, entrance_side="S", lobby_name="the apartment lobby",
                   roof_access=("a ladder", "W"))

    # --- Meridian Library (east of plaza) ---
    m.comment("Meridian Library")
    lix = S.building_shell(m, "Meridian Library", 726, 800, 928, 1010,
                           floor_t="hardwood2", wall_t="wallbrick",
                           entrances=[("W", 962, 970)],
                           roof_access=None)
    ix1, ix2, iy1, iy2 = lix
    S.interior_fill(m, "the library reading room", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2, "the library reading room")
    for sx in range(ix1 + 3, ix2 - 4, 9):
        m.furniture(sx, sx + 4, iy1 + 3, iy2 - 3, 3, "library bookshelves", "hardwood")
    S.counter(m, ix1 + 2, ix1 + 8, iy2 - 3, iy2 - 2, "the library front desk")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 6000, 2,
             ["health_potion", "energetic_potion_green"])

    # --- Shops along Cathedral Row ---
    m.comment("Cathedral Row shops")
    S.shop(m, "Meridian Pharmacy", 545, 605, 700, 748, entrance_side="N",
           goods="pharmacy shelves")
    S.shop(m, "Beacon Grocery", 662, 730, 700, 748, entrance_side="N",
           floor_t="tile1", goods="grocery shelves")
    S.shop(m, "Northgate Hardware", 766, 820, 700, 750, entrance_side="W",
           floor_t="concrete10", goods="tool racks")

    m.src(x1, x2, C.NORTH_Y1, C.ISL_Y2, 0, GROUND_TOP, "wind1.ogg", -14)
