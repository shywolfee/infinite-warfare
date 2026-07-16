"""Level 1313 - the Coruscant underworld. A grim shelf of the city that never
sees sky, riddled with gaps that drop away to the surface. Hard to reach: the
only lift down is a maintenance shaft in The Works, or you fall here."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("LEVEL 1313 - THE UNDERWORLD")
    m.at_level(C.UNDERWORLD)
    # The main shelf (partial - the void around it drops to the surface).
    m.tile(150, 900, 150, 900, 0, 0, "concrete10")
    m.zone(150, 900, 150, 900, 0, GROUND_TOP, "Level 1313, the Coruscant underworld")
    m.src(150, 900, 150, 900, 0, GROUND_TOP, "wind2.ogg", -11)
    m.src(150, 900, 150, 900, 0, GROUND_TOP, "cave1.ogg", -14)
    m.seed(500, 500, 0)
    m.poi(500, 500, 0, "Level 1313, the underworld")

    # A couple of holes in the deck that drop to the surface.
    S.hole(m, 640, 700, 640, 700, "a gap in the underworld deck")
    S.hole(m, 300, 340, 700, 760, "a broken section of decking")

    # Grimy through-ways (no curbs, cracked).
    S.street_ns(m, "Shadow Way", 480, 491, 170, 880, sidewalk=2, curb=False,
                road_t="cement", broken=True)
    S.street_ew(m, "the 1313 Concourse", 500, 511, 170, 880, sidewalk=2, curb=False,
                road_t="cement", broken=True)

    # The black market - a sprawling covered bazaar.
    m.comment("the underworld black market")
    bix = S.building_shell(m, "the underworld black market", 200, 320, 200, 320,
                           floor_t="concrete10", wall_t="wallstone", ztop=18,
                           entrances=[("N", 254, 266), ("E", 254, 266)])
    ix1, ix2, iy1, iy2 = bix
    S.interior_fill(m, "the black market floor", ix1, ix2, iy1, iy2)
    m.zone(ix1, ix2, iy1, iy2, 0, ROOM_TOP, "the black market floor")
    stall = 1
    for sx in range(ix1 + 4, ix2 - 8, 18):
        for sy in (iy1 + 6, iy2 - 10):
            m.furniture(sx, sx + 10, sy, sy + 3, 3, "black market stall %d" % stall, "hardwood")
            stall += 1
    m.src(ix1, ix2, iy1, iy2, 0, 18, "farm.ogg", -12)
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 4000, 5,
             ["frag_grenade", "smoke_bomb", "bomb_vest", "health_potion", "semtex_pack"])

    # A cantina.
    S.shop(m, "the Speeder-Wreck Cantina", 560, 640, 220, 300, floor_t="hardwood2",
           wall_t="wallstone", entrance_side="W", goods="cantina bottles")

    # Tenement blocks (no railings on the stairs down here).
    S.house(m, "a 1313 tenement", 700, 740, 250, 300, floor_t="concrete10",
            wall_t="wallstone", entrance_side="S", railings="none")
    S.house(m, "a collapsed hab-block", 760, 800, 250, 300, floor_t="concrete10",
            wall_t="wallstone", entrance_side="S", railings="none", basement=True)

    m.at_level(0)
