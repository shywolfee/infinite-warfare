"""Finishing pass: a little extra loot spread on the busiest levels and a couple
of orientation points of interest."""
import config as C

MAIN_LOOT = ["health_potion", "energetic_potion_red", "energetic_potion_blue",
             "frag_grenade", "smoke_bomb", "semtex_pack", "bomb_vest",
             "AK47_ammo_10_50", "glock17_ammo_10_40", "hk.g36_ammo_20_50"]


def build(m):
    m.section("CITYWIDE LOOT AND ORIENTATION")
    m.at_level(C.MAIN)
    m.ispawn(200, 1300, 200, 1300, 0, 0, 1200, 40, MAIN_LOOT)
    m.at_level(C.SENATE)
    m.ispawn(200, 1240, 200, 1240, 0, 0, 2500, 12,
             ["health_potion", "ultra_health_potion", "frag_grenade", "smoke_bomb"])
    m.at_level(C.SKYDECK)
    m.ispawn(220, 1240, 220, 1240, 0, 0, 2500, 12,
             ["health_potion", "energetic_potion_rainbow", "frag_grenade"])
    m.at_level(0)
    m.poi((C.SPAWN_X1 + C.SPAWN_X2) // 2, (C.SPAWN_Y1 + C.SPAWN_Y2) // 2, C.MAIN,
          "the Monument Plaza deploy point")
