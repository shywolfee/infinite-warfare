"""South Meridian: five main streets, three alleyways, two residential
cul-de-sacs, plus a diner, a fire station and a school."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("SOUTH MERIDIAN - streets, alleys, cul-de-sacs and houses")
    x1, x2 = C.CEN_X1 + 4, C.CEN_X2 - 4
    ylo = C.SOUTH_Y1 + 6
    yhi = C.SOUTH_Y2 - 4

    # --- Three north-south streets ---
    harlow = S.street_ns(m, "Harlow Street", 512, 519, ylo, yhi)
    sutton = S.street_ns(m, "Sutton Street", 636, 643, ylo, yhi)
    marsh = S.street_ns(m, "Marsh Lane", 752, 759, ylo, yhi)
    # --- Two east-west streets ---
    foundry = S.street_ew(m, "Foundry Street", 300, 307, x1, x2)
    elm = S.street_ew(m, "Elm Road", 452, 459, x1, x2)
    for ns in (harlow, sutton, marsh):
        for ew in (foundry, elm):
            S.intersection(m, ns, ew)

    # --- Three alleyways off three different streets (narrow, no sidewalks) ---
    m.comment("Alleyways")
    S.street_ew(m, "Tanner's Alley", 360, 363, 522, 575, sidewalk=0, curb=False,
                road_t="gravel1")
    S.street_ew(m, "Cinder Alley", 500, 503, 590, 634, sidewalk=0, curb=False,
                road_t="gravel1")
    m.src(590, 634, 498, 505, 0, GROUND_TOP, "wind2.ogg", -13)
    S.street_ew(m, "Copper Alley", 250, 253, 762, 815, sidewalk=0, curb=False,
                road_t="gravel1")

    # --- Wren Court cul-de-sac (off Foundry Street, heading south) ---
    m.comment("Wren Court cul-de-sac")
    _cul_de_sac(m, "Wren Court", 556, 563, 200, 296)
    S.house(m, "14 Wren Court", 498, 534, 208, 258, entrance_side="E",
            basement=True, bilco=True, railings="both",
            driveway=(535, 545, 220, 246))
    S.house(m, "17 Wren Court", 588, 624, 208, 258, entrance_side="W",
            second_floor=True, railings="both",
            driveway=(577, 587, 220, 246))

    # --- Sparrow Close cul-de-sac (off Elm Road, heading south) ---
    m.comment("Sparrow Close cul-de-sac")
    _cul_de_sac(m, "Sparrow Close", 700, 707, 360, 448)
    S.house(m, "3 Sparrow Close", 642, 678, 368, 418, entrance_side="E",
            attic=True, railings="both", driveway=(679, 689, 380, 406))
    S.house(m, "6 Sparrow Close", 732, 768, 368, 418, entrance_side="W",
            basement=True, railings="right", driveway=(721, 731, 380, 406))

    # --- Southgate Diner (on Foundry Street) ---
    m.comment("Southgate Diner")
    dix = S.building_shell(m, "Southgate Diner", 545, 605, 322, 360,
                           floor_t="tile2", wall_t="wallbrick",
                           entrances=[("S", 570, 578)])
    ix1, ix2, iy1, iy2 = dix
    S.interior_fill(m, "the diner floor", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2, "the diner floor")
    S.counter(m, ix1 + 2, ix2 - 8, iy2 - 4, iy2 - 3, "the diner counter")
    for bx in range(ix1 + 3, ix2 - 6, 8):
        m.furniture(bx, bx + 4, iy1 + 3, iy1 + 5, 2, "diner booth")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 5000, 2,
             ["health_potion", "energetic_potion_red"])

    # --- Meridian Fire Station (on Sutton Street) ---
    m.comment("Meridian Fire Station")
    fix = S.building_shell(m, "Meridian Fire Station", 662, 730, 322, 372,
                           floor_t="concrete10", wall_t="wallbrick",
                           entrances=[("S", 686, 706)], roof_access=("a ladder", "E"))
    ix1, ix2, iy1, iy2 = fix
    S.interior_fill(m, "the engine bay", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2 - 14, "the engine bay")
    mid = (ix1 + ix2) // 2
    m.wall_y(iy2 - 14, ix1, ix2, ROOM_TOP, "wallbrick", [(mid - 1, mid + 1)])
    S.doorway(m, mid - 1, mid + 1, iy2 - 14, iy2 - 14, "fire station rear door")
    S.room(m, ix1, ix2, iy2 - 13, iy2, "the firefighters' common room")
    S.counter(m, ix1 + 2, ix1 + 8, iy2 - 2, iy2 - 1, "the common room kitchenette")

    # --- Southbank School (classrooms via a corridor) ---
    m.comment("Southbank School")
    S.office_block(m, "Southbank School", 545, 620, 476, 566,
                   floor_t="tile1", wall_t="wallbrick", n_per_side=3,
                   start_no=1, entrance_side="N", lobby_name="the school entrance hall")
    m.tile(545, 620, 568, 588, 0, 0, "concrete5")
    m.zone(545, 620, 568, 588, 0, GROUND_TOP, "the Southbank School yard")
    m.ispawn(548, 616, 570, 586, 0, 0, 6000, 2, ["health_potion", "empty_bucket"])

    m.src(x1, x2, C.SOUTH_Y1, C.SOUTH_Y2, 0, GROUND_TOP, "wind1.ogg", -14)


def _cul_de_sac(m, name, rx1, rx2, y_bulb, y_connect):
    """A dead-end residential lane: a road stub from y_connect (a through street)
    south to y_bulb, ending in a turning bulb."""
    m.tile(rx1, rx2, y_bulb, y_connect, 0, 0, "concrete5")
    m.zone(rx1, rx2, y_bulb, y_connect, 0, GROUND_TOP, name)
    m.tile(rx1 - 3, rx1 - 1, y_bulb, y_connect, 0, 0, "concrete2")
    m.zone(rx1 - 3, rx1 - 1, y_bulb, y_connect, 0, GROUND_TOP, "west sidewalk of " + name)
    m.tile(rx2 + 1, rx2 + 3, y_bulb, y_connect, 0, 0, "concrete2")
    m.zone(rx2 + 1, rx2 + 3, y_bulb, y_connect, 0, GROUND_TOP, "east sidewalk of " + name)
    bx1, bx2 = rx1 - 14, rx2 + 14
    m.tile(bx1, bx2, y_bulb - 20, y_bulb - 1, 0, 0, "concrete5")
    m.zone(bx1, bx2, y_bulb - 20, y_bulb - 1, 0, GROUND_TOP,
           "the turning circle at the end of " + name)
    m.poi((rx1 + rx2) // 2, y_bulb, 0, name)
