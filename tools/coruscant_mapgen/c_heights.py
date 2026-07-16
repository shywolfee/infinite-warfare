"""Calacor Heights - a mid-city level of tidy avenues, hab-towers and cantinas,
where working Coruscanti live between the glamour above and the dark below."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("CALACOR HEIGHTS - mid-city residential level")
    m.at_level(C.HEIGHTS)
    m.tile(150, 1250, 150, 1250, 0, 0, "concrete2")
    m.zone(150, 1250, 150, 1250, 0, GROUND_TOP, "Calacor Heights, a mid-city level")
    m.src(150, 1250, 150, 1250, 0, GROUND_TOP, "wind1.ogg", -13)
    m.seed(700, 700, 0)
    m.poi(700, 700, 0, "Calacor Heights")

    # Avenues (this level is in good repair - full curbs and sidewalks).
    av = []
    av.append(S.street_ns(m, "Calacor Avenue", 400, 407, 180, 1220))
    av.append(S.street_ns(m, "Verith Street", 700, 707, 180, 1220))
    av.append(S.street_ns(m, " Leado Way".strip(), 1000, 1007, 180, 1220))
    cross = []
    cross.append(S.street_ew(m, "Heights Boulevard", 400, 407, 180, 1220))
    cross.append(S.street_ew(m, "Skylane Row", 800, 807, 180, 1220))
    for a in av:
        for c in cross:
            S.intersection(m, a, c)

    # A small plaza with a fall-hole guarded by railings you can still slip past.
    m.tile(760, 840, 720, 800, 0, 0, "concrete12")
    m.zone(760, 840, 720, 800, 0, GROUND_TOP, "Heights Plaza")
    S.hole(m, 790, 810, 750, 770, "the open lift-well at the centre of Heights Plaza")

    # Hab-towers (apartments) - the central turbolift rises through one of them.
    S.office_block(m, "Calacor Hab-Tower", 470, 560, 470, 560, floor_t="carpet1",
                   wall_t="wallbrick", n_per_side=3, start_no=1, entrance_side="S",
                   lobby_name="the hab-tower lobby")
    S.office_block(m, "Verith Hab-Block", 900, 990, 470, 560, floor_t="carpet1",
                   wall_t="wallbrick", n_per_side=3, start_no=1, entrance_side="S",
                   lobby_name="the hab-block lobby")

    # Shops and a cantina.
    S.shop(m, "the Heights Market", 470, 560, 900, 980, floor_t="tile1",
           wall_t="wallbrick", entrance_side="N", goods="market shelves")
    S.shop(m, "the Rusty Astromech Cantina", 900, 990, 900, 980, floor_t="hardwood2",
           wall_t="wallbrick", entrance_side="N", goods="cantina bottles")

    m.ispawn(200, 1200, 200, 1200, 0, 0, 3500, 10,
             ["health_potion", "energetic_potion_red", "energetic_potion_blue",
              "frag_grenade", "smoke_bomb", "empty_bucket"])
    m.at_level(0)
