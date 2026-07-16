"""Finishing pass: a little extra loot and orientation."""
import config as C


def build(m):
    m.section("ORIENTATION AND EXTRA LOOT")
    m.at_level(C.DECK3)
    m.ispawn(C.SX1 + 4, C.SX2 - 4, C.MID_Y1 + 4, C.MID_Y2 - 4, 0, 0, 4000, 4,
             ["health_potion", "ultra_health_potion", "energetic_potion_red"])
    m.at_level(0)
    m.poi((C.SPAWN_X1 + C.SPAWN_X2) // 2, (C.SPAWN_Y1 + C.SPAWN_Y2) // 2, C.SPAWN_Z,
          "the Deck 1 deploy point")
