"""Aesir VI - a verdant forested world. The ship rests on a landing field; a
river winds through the forest, a wooded hill carries a cabin, and a small
village has grown up beside the field with houses, a control tower and a branch
of the Galactic Interstellar Bureau."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("AESIR VI - the forested surface")
    m.at_level(0)
    # base: forest everywhere (so nothing is ever unnamed or unfloored)
    m.tile(0, C.MAXX, 0, C.MAXY, 0, 0, "grass")
    m.zone(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP, "the forests of Aesir VI")
    m.src(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP, "forest.ogg", -10)
    m.src(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP, "birds3.ogg", -13)
    m.seed(440, 100, 0)          # on the field, south of the ship
    m.seed(820, 500, 0)          # in the village

    # scattered trees through the forest fringes
    for tx in range(30, C.MAXX - 20, 70):
        for ty in range(30, C.MAXY - 20, 90):
            if 150 < tx < 740 and 120 < ty < 920:
                continue  # keep the landing field clear
            m.tile(tx, tx, ty, ty, 0, random_h(tx, ty), "tree")
            m.zone(tx, tx, ty, ty, 0, GROUND_TOP, "a tall conifer in the forest")

    # --- The landing field ---
    m.comment("the landing field")
    m.tile(150, 740, 120, 920, 0, 0, "concrete10")
    m.zone(150, 740, 120, 920, 0, GROUND_TOP, "the landing field on Aesir VI")
    m.poi(440, 140, 0, "the landing field")
    m.ispawn(160, 730, 130, 200, 0, 0, 5000, 4,
             ["health_potion", "energetic_potion_green", "frag_grenade", "smoke_bomb"])

    # --- The river through the forest, with a footbridge ---
    m.comment("the river")
    m.tile(60, 92, 0, C.MAXY, 0, 0, "water1")
    m.zone(60, 92, 0, C.MAXY, 0, GROUND_TOP, "the river running through the forest")
    m.src(60, 92, 0, C.MAXY, 0, GROUND_TOP, "stream2.ogg", -7)
    m.tile(56, 96, 496, 504, 0, 0, "plank")
    m.zone(56, 96, 496, 504, 0, GROUND_TOP, "the log footbridge over the river")
    m.tile(56, 56, 496, 504, 0, 3, "wallfence")
    m.tile(96, 96, 496, 504, 0, 3, "wallfence")
    m.poi(76, 500, 0, "the log footbridge")

    # --- The wooded hill and the cabin on top ---
    m.comment("the wooded hill and cabin")
    hx1, hx2, hy1, hy2 = 24, 140, 600, 740
    m.tile(hx1, hx2, hy1, hy2, 0, 23, "grass")             # the hill body
    m.zone(hx1 - 1, hx1 - 1, hy1, hy2, 0, GROUND_TOP, "the foot of the wooded hill")
    m.tile(hx1, hx1 + 2, hy1, hy2, 0, 24, "ladder1")       # the path up
    m.zone(hx1, hx1 + 2, hy1, hy2, 0, 24, "the path up the wooded hill")
    m.tile(hx1 + 3, hx2, hy1, hy2, 24, 24, "grass")        # the hilltop clearing
    m.zone(hx1 + 3, hx2, hy1, hy2, 24, 24 + GROUND_TOP, "the top of the wooded hill")
    # a low fence around the hilltop so you don't tumble off (except the path)
    m.tile(hx2, hx2, hy1, hy2, 24, 27, "wallfence")
    m.tile(hx1 + 3, hx2, hy1, hy1, 24, 27, "wallfence")
    m.tile(hx1 + 3, hx2, hy2, hy2, 24, 27, "wallfence")
    m.at_level(24)
    S.house(m, "the hilltop cabin", 50, 96, 640, 700, floor_t="hardwood",
            wall_t="wallwood", entrance_side="S", attic=True, railings="both")
    m.poi(72, 670, 0, "the hilltop cabin")
    m.at_level(0)

    # --- The village beside the field ---
    m.comment("the village")
    m.tile(760, 900, 340, 660, 0, 0, "gravel1")
    m.zone(760, 900, 340, 660, 0, GROUND_TOP, "the village square")
    m.src(760, 900, 340, 660, 0, GROUND_TOP, "wind1.ogg", -13)
    S.house(m, "a settler's house", 770, 806, 360, 410, floor_t="hardwood",
            wall_t="wallwood", entrance_side="N", railings="both", second_floor=True)
    S.house(m, "a settler's house", 860, 896, 360, 410, floor_t="hardwood",
            wall_t="wallwood", entrance_side="N", railings="both", basement=True)
    _control_tower(m)
    _gib_branch(m)
    m.poi(830, 500, 0, "the village on Aesir VI")
    m.at_level(0)


def random_h(a, b):
    return 5 + (a * 7 + b * 3) % 6   # a stable pseudo-random tree height 5..10


def _control_tower(m):
    m.comment("the spaceport control tower")
    x1, x2, y1, y2 = 770, 796, 560, 586
    S.building_shell(m, "the control tower", x1, x2, y1, y2, floor_t="concrete2",
                     wall_t="wallstone", ztop=44, entrances=[("N", 779, 786)])
    m.tile(x1 + 1, x1 + 2, y1 + 1, y2 - 1, 0, 45, "ladder1")
    m.zone(x1 + 1, x1 + 2, y1 + 1, y2 - 1, 0, 45, "the control tower stairs")
    m.tile(x1 + 3, x1 + 3, y1 + 1, y2 - 1, 0, 2, "wallfence")
    m.tile(x1 + 1, x2 - 1, y1 + 1, y2 - 1, 45, 45, "concrete2")
    m.zone(x1 + 1, x2 - 1, y1 + 1, y2 - 1, 45, 45 + ROOM_TOP, "the control tower cab")
    S.counter(m, x1 + 4, x2 - 2, y1 + 2, y1 + 3, "the control tower console")
    m.poi((x1 + x2) // 2, (y1 + y2) // 2, 45, "the control tower cab")


def _gib_branch(m):
    m.comment("the GIB branch")
    S.office_block(m, "the GIB branch office", 840, 900, 560, 650,
                   floor_t="tile1", wall_t="wallstone", n_per_side=3, start_no=1,
                   entrance_side="N", lobby_name="the GIB lobby")
    m.poi(870, 560, 0, "the Galactic Interstellar Bureau branch")
