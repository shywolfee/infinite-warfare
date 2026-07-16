"""The planetary surface - the very bottom of Coruscant, kilometres below the
city. A single floor spanning the whole map so that any fall, from any level,
eventually lands here. Pitch dark, howling, and studded with the colossal
support pylons that hold the city up."""
from lib import GROUND_TOP
import structures as S
import config as C


def build(m):
    m.section("THE PLANETARY SURFACE (bottom - catches every fall)")
    m.at_level(C.SURFACE)
    m.tile(0, C.MAXX, 0, C.MAXY, 0, 0, "rocks1")
    m.zone(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP,
           "the planetary surface of Coruscant, far below the city")
    m.src(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP, "wind2.ogg", -9)
    m.src(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP, "rumble.ogg", -14)
    m.seed(800, 800, 0)
    # A grid of vast support pylons rising out of the dark, holding up the city.
    n = 0
    for px in range(180, C.MAXX - 120, 360):
        for py in range(180, C.MAXY - 120, 360):
            n += 1
            m.tile(px, px + 40, py, py + 40, 0, 120, "wallstone")
            m.zone(px - 1, px - 1, py, py + 40, 0, GROUND_TOP, "a city support pylon")
            m.zone(px + 41, px + 41, py, py + 40, 0, GROUND_TOP, "a city support pylon")
            m.zone(px, px + 40, py - 1, py - 1, 0, GROUND_TOP, "a city support pylon")
            m.zone(px, px + 40, py + 41, py + 41, 0, GROUND_TOP, "a city support pylon")
    # A ruined scrap camp huddled at the base of one pylon.
    S.building_shell(m, "a surface scavengers' shelter", 620, 660, 620, 654,
                     floor_t="gravel1", wall_t="wallrock", ztop=14,
                     entrances=[("N", 636, 642)])
    m.zone(621, 659, 621, 653, 0, 11, "inside the scavengers' shelter")
    m.ispawn(240, 1360, 240, 1360, 0, 0, 6000, 8,
             ["rock", "empty_bucket", "health_potion", "frag_grenade"])
    m.poi(800, 800, 0, "the planetary surface")
    m.at_level(0)
