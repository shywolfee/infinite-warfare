"""The Skydeck - the highest inhabited level, where the upper spaceport, luxury
sky-towers and an open observation deck catch the thin daylight above the smog."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("THE SKYDECK - upper spaceport and sky-towers")
    m.at_level(C.SKYDECK)
    m.tile(200, 1250, 200, 1250, 0, 0, "metal2")
    m.zone(200, 1250, 200, 1250, 0, GROUND_TOP, "the Skydeck of Coruscant")
    m.src(200, 1250, 200, 1250, 0, GROUND_TOP, "wind1.ogg", -9)
    m.seed(760, 760, 0)

    # The upper spaceport concourse.
    m.comment("the Coruscant Skyport")
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, "the Coruscant Skyport", 560, 900, 560, 820, floor_t="tile1",
        wall_t="metal2", ztop=24, entrances=[("S", 716, 744)])
    S.interior_fill(m, "the skyport concourse", ix1, ix2, iy1, iy2)
    m.zone(ix1, ix2, iy1, iy2, 0, ROOM_TOP, "the skyport concourse")
    for cx in range(ix1 + 10, ix2 - 14, 26):
        S.counter(m, cx, cx + 14, iy1 + 6, iy1 + 7, "a skyport ticketing desk")
    gate = 1
    gate_wall = iy2 - 18
    m.wall_y(gate_wall, ix1, ix2, ROOM_TOP, "metal2",
             [(ix1 + 20, ix1 + 24), (ix2 - 24, ix2 - 20)])
    S.doorway(m, ix1 + 20, ix1 + 24, gate_wall, gate_wall, "skyport gate 1 doorway")
    S.doorway(m, ix2 - 24, ix2 - 20, gate_wall, gate_wall, "skyport gate 2 doorway")
    m.wall_x((ix1 + ix2) // 2, gate_wall + 1, iy2, ROOM_TOP, "metal2")
    S.room(m, ix1, (ix1 + ix2) // 2 - 1, gate_wall + 1, iy2, "the skyport gate 1 lounge")
    S.room(m, (ix1 + ix2) // 2 + 1, ix2, gate_wall + 1, iy2, "the skyport gate 2 lounge")
    m.src(ix1, ix2, iy1, iy2, 0, 24, "calm.ogg", -12)
    m.poi((ix1 + ix2) // 2, iy1, 0, "the Coruscant Skyport")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 5000, 4,
             ["health_potion", "energetic_potion_rainbow", "frag_grenade", "smoke_bomb"])

    # Open landing pads north of the port (fall off the edge - a long way down).
    m.tile(560, 900, 830, 1010, 0, 0, "metal2")
    m.zone(560, 900, 830, 1010, 0, GROUND_TOP, "the skyport landing apron")
    for i, px in enumerate(range(580, 880, 100)):
        m.zone(px, px + 80, 850, 990, 0, GROUND_TOP, "sky landing pad %d" % (i + 1))
    S.edge_railing(m, "the apron railing", 560, 900, 830, 1010, "N")
    m.src(560, 900, 830, 1010, 0, GROUND_TOP, "wind2.ogg", -8)

    # Luxury sky-towers with a rooftop observation deck.
    S.office_block(m, "the Skydeck Spire", 300, 380, 400, 540, floor_t="carpet1",
                   wall_t="wallbrick", n_per_side=4, start_no=1, entrance_side="S",
                   lobby_name="the spire lobby")
    S.office_block(m, "the Umate Sky-Tower", 1000, 1080, 400, 540, floor_t="carpet1",
                   wall_t="wallbrick", n_per_side=4, start_no=1, entrance_side="S",
                   lobby_name="the tower lobby")

    # The observation deck (open, exposed).
    m.tile(560, 900, 300, 420, 0, 0, "tile2")
    m.zone(560, 900, 300, 420, 0, GROUND_TOP, "the Skydeck observation deck")
    S.edge_railing(m, "the observation railing", 560, 900, 300, 420, "S")
    m.poi(730, 360, 0, "the Skydeck observation deck")
    m.at_level(0)
