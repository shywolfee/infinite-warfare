"""The cargo hold - a single tall bay in the belly of the ship, one level below
Deck 1. It is not counted among the seven decks. Both turbolifts reach it."""
from lib import ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("THE CARGO HOLD (below Deck 1)")
    m.at_level(C.CARGO)
    m.tile(C.SX1, C.SX2, C.SY1, C.SY2, 0, 0, "metal5")
    m.wall_y(C.SY2, C.SX1, C.SX2, ROOM_TOP, "wallstone")
    m.wall_y(C.SY1, C.SX1, C.SX2, ROOM_TOP, "wallstone")
    m.wall_x(C.SX1, C.SY1, C.SY2, ROOM_TOP, "wallstone")
    m.wall_x(C.SX2, C.SY1, C.SY2, ROOM_TOP, "wallstone")
    m.zone(C.SX1 + 1, C.SX2 - 1, C.SY1 + 1, C.SY2 - 1, 0, ROOM_TOP, "the cargo hold")
    # named bays fore and aft
    mid = (C.SY1 + C.SY2) // 2
    m.zone(C.SX1 + 1, C.SX2 - 1, mid + 1, C.SY2 - 1, 0, ROOM_TOP, "the forward cargo bay")
    m.zone(C.SX1 + 1, C.SX2 - 1, C.SY1 + 1, mid, 0, ROOM_TOP, "the aft cargo bay")
    m.src(C.SX1, C.SX2, C.SY1, C.SY2, 0, ROOM_TOP, "rumble.ogg", -14)
    # rows of lashed-down cargo containers forming aisles you weave through
    n = 1
    for cx in range(C.SX1 + 20, C.SX2 - 40, 46):
        for cy in range(C.SY1 + 30, C.SY2 - 60, 120):
            m.furniture(cx, cx + 30, cy, cy + 80, 4, "cargo container %d" % n, "metal2")
            n += 1
    m.seed((C.SX1 + C.SX2) // 2, C.SY1 + 15, 0)
    m.seed((C.SX1 + C.SX2) // 2, C.SY2 - 15, 0)
    m.poi((C.SX1 + C.SX2) // 2, mid, 0, "the cargo hold")
    m.ispawn(C.SX1 + 4, C.SX2 - 4, C.SY1 + 4, C.SY2 - 4, 0, 0, 5000, 6,
             ["box", "bag", "rock", "empty_bucket", "health_potion", "repair_kit"])
    m.at_level(0)
