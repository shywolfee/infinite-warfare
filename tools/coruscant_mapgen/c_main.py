"""The Main Level - the Coruscant most people picture: CoCo Town's commerce
lanes, Monument Plaza with the peak of Umate breaking through the pavement, the
neon Uscru Entertainment District, Independence Center, and the Main Level
Spaceport. This is where you deploy."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("THE MAIN LEVEL (deploy here)")
    m.at_level(C.MAIN)
    m.tile(150, 1350, 150, 1350, 0, 0, "concrete2")
    m.zone(150, 1350, 150, 1350, 0, GROUND_TOP, "the Main Level of Coruscant")
    m.src(150, 1350, 150, 1350, 0, GROUND_TOP, "wind1.ogg", -14)
    m.seed(790, 720, 0)
    m.seed(400, 650, 0)
    m.seed(1100, 650, 0)
    m.seed(720, 1100, 0)
    m.seed(720, 400, 0)

    # ---- Monument Plaza + the peak of Umate (deploy point) ----
    m.comment("Monument Plaza and Umate")
    m.tile(680, 920, 640, 820, 0, 0, "concrete12")
    m.zone(680, 920, 640, 820, 0, GROUND_TOP, "Monument Plaza")
    m.src(680, 920, 640, 820, 0, GROUND_TOP, "calm.ogg", -10)
    # Umate: a rocky summit poking through the pavement, climbable to a peak.
    ux1, ux2, uy1, uy2 = 786, 826, 700, 740
    m.tile(ux1, ux2, uy1, uy2, 0, 10, "rocks1")
    m.zone(ux1, ux2, uy1, uy2, 0, GROUND_TOP, "the base of Umate")
    m.tile(ux1, ux1 + 1, uy1, uy2, 0, 11, "ladder1")   # a climbable path up
    m.zone(ux1, ux1 + 1, uy1, uy2, 0, 11, "the climb up Umate")
    m.tile(ux1 + 2, ux2, uy1, uy2, 11, 11, "rocks1")
    m.zone(ux1 + 2, ux2, uy1, uy2, 11, 18, "the summit of Umate, highest point on the Main Level")
    m.poi((ux1 + ux2) // 2, (uy1 + uy2) // 2, 11, "the summit of Umate")
    m.poi(800, 720, 0, "Monument Plaza")
    m.ispawn(690, 910, 650, 810, 0, 0, 4000, 5,
             ["health_potion", "energetic_potion_blue", "frag_grenade", "smoke_bomb"])

    # ---- CoCo Town (west) ----
    m.section("CoCo Town (Collective Commerce)")
    a1 = S.street_ns(m, "Collective Commerce Way", 300, 307, 380, 900)
    a2 = S.street_ns(m, "CoCo Lane", 480, 487, 380, 900)
    c1 = S.street_ew(m, "Dex's Row", 500, 507, 180, 560)
    c2 = S.street_ew(m, "Ando Prime Street", 760, 767, 180, 560)
    for a in (a1, a2):
        for c in (c1, c2):
            S.intersection(m, a, c)
    # A busy diner off Dex's Row.
    dix = S.building_shell(m, "the CoCo Town diner", 200, 280, 520, 560,
                           floor_t="tile2", wall_t="wallbrick",
                           entrances=[("N", 236, 244)])
    ix1, ix2, iy1, iy2 = dix
    S.interior_fill(m, "the diner floor", ix1, ix2, iy1, iy2)
    m.zone(ix1, ix2, iy1, iy2, 0, ROOM_TOP, "the diner floor")
    S.counter(m, ix1 + 2, ix2 - 10, iy1 + 4, iy1 + 5, "the diner serving counter")
    for bx in range(ix1 + 3, ix2 - 6, 8):
        m.furniture(bx, bx + 4, iy2 - 5, iy2 - 3, 2, "a diner booth")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 5000, 2,
             ["health_potion", "energetic_potion_red"])
    # Commerce blocks.
    S.office_block(m, "the Collective Commerce Exchange", 340, 440, 620, 760,
                   floor_t="tile1", wall_t="wallbrick", n_per_side=4, start_no=1,
                   entrance_side="S", lobby_name="the exchange trading floor",
                   front_counter=True)
    S.shop(m, "a CoCo Town droid shop", 200, 280, 620, 700, floor_t="concrete10",
           wall_t="wallbrick", entrance_side="E", goods="droid parts")
    S.shop(m, "a CoCo Town textiles stall", 200, 280, 720, 800, floor_t="hardwood",
           wall_t="wallbrick", entrance_side="E", goods="bolts of cloth")

    # ---- Uscru Entertainment District (east) ----
    m.section("Uscru Entertainment District")
    u1 = S.street_ns(m, "Uscru Boulevard", 1040, 1047, 380, 900)
    u2 = S.street_ew(m, "the Outlander Strip", 500, 507, 950, 1330)
    S.intersection(m, u1, u2)
    # The opera house - a grand hall.
    m.comment("the Galaxies Opera House")
    ox1, ox2, oy1, oy2 = 1080, 1300, 420, 660
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, "the Galaxies Opera House", ox1, ox2, oy1, oy2, floor_t="carpet1",
        wall_t="wallstone", ztop=40, entrances=[("W", 528, 552)])
    S.interior_fill(m, "the opera house foyer", ix1, ix2, iy1, iy2)
    m.zone(ix1, ix1 + 24, iy1, iy2, 0, ROOM_TOP, "the opera house foyer")
    m.wall_x(ix1 + 25, iy1, iy2, ROOM_TOP, "wallstone", [((iy1 + iy2) // 2 - 3, (iy1 + iy2) // 2 + 3)])
    S.doorway(m, ix1 + 25, ix1 + 25, (iy1 + iy2) // 2 - 3, (iy1 + iy2) // 2 + 3, "the auditorium doors")
    m.zone(ix1 + 26, ix2, iy1, iy2, 0, 30, "the opera house auditorium")
    for ry in range(iy1 + 6, iy2 - 20, 5):
        m.furniture(ix1 + 30, ix2 - 6, ry, ry + 1, 2, "a tier of opera seats")
    m.zone(ix2 - 40, ix2 - 2, iy2 - 18, iy2 - 2, 0, 30, "the opera house stage")
    m.src(ix1, ix2, iy1, iy2, 0, 40, "calm.ogg", -9)
    m.poi((ox1 + ox2) // 2, oy1, 0, "the Galaxies Opera House")
    # Nightclubs.
    S.shop(m, "the Outlander Club", 1080, 1160, 720, 820, floor_t="hardwood2",
           wall_t="wallbrick", entrance_side="W", goods="club sound rigs")
    S.shop(m, "a Uscru sabacc den", 1200, 1280, 720, 820, floor_t="hardwood2",
           wall_t="wallbrick", entrance_side="W", goods="sabacc tables")
    m.ispawn(1060, 1320, 420, 860, 0, 0, 4000, 6,
             ["energetic_potion_green", "energetic_potion_rainbow", "health_potion",
              "smoke_bomb", "frag_grenade"])

    # ---- Independence Center (north) ----
    m.section("Independence Center")
    m.tile(600, 1000, 980, 1300, 0, 0, "concrete12")
    m.zone(600, 1000, 980, 1300, 0, GROUND_TOP, "Independence Center, a grand civic plaza")
    m.src(600, 1000, 980, 1300, 0, GROUND_TOP, "calm.ogg", -11)
    # A mall building off the plaza.
    S.office_block(m, "the Independence Center mall", 640, 760, 1040, 1260,
                   floor_t="tile1", wall_t="wallbrick", n_per_side=6, start_no=1,
                   entrance_side="S", lobby_name="the mall atrium")
    S.office_block(m, "the Galactic Museum", 840, 960, 1040, 1260, floor_t="tile2",
                   wall_t="wallstone", n_per_side=6, start_no=1, entrance_side="S",
                   lobby_name="the museum rotunda")
    m.poi(800, 1140, 0, "Independence Center")
    m.ispawn(620, 980, 1000, 1280, 0, 0, 4000, 5,
             ["health_potion", "ultra_health_potion", "energetic_potion_blue"])

    # ---- Main Level Spaceport (east, by the spaceport turbolift) ----
    m.section("the Main Level Spaceport")
    _spaceport(m)

    # ---- Central transit hub (around the central turbolift) ----
    m.comment("the central transit hub")
    m.tile(740, 850, 740, 850, 0, 0, "metal2")
    m.zone(740, 850, 740, 850, 0, GROUND_TOP, "the Central Transit Hub")
    m.poi(795, 795, 0, "the Central Transit Hub")

    m.at_level(0)


def _spaceport(m):
    x1, x2, y1, y2 = 1060, 1330, 620, 900
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, "the Main Level Spaceport", x1, x2, y1, y2, floor_t="tile1",
        wall_t="metal2", ztop=24, entrances=[("W", 748, 772)])
    S.interior_fill(m, "the spaceport concourse", ix1, ix2, iy1, iy2)
    m.zone(ix1, ix2, iy1, iy2, 0, ROOM_TOP, "the spaceport concourse")
    for cx in range(ix1 + 8, ix2 - 40, 24):
        S.counter(m, cx, cx + 14, iy1 + 4, iy1 + 5, "a spaceport departures desk")
    # gate lounges along the north wall
    gate_wall = iy2 - 16
    m.wall_y(gate_wall, ix1, ix2 - 30, ROOM_TOP, "metal2",
             [(ix1 + 18, ix1 + 22), (ix1 + 70, ix1 + 74)])
    S.doorway(m, ix1 + 18, ix1 + 22, gate_wall, gate_wall, "spaceport gate 3 doorway")
    S.doorway(m, ix1 + 70, ix1 + 74, gate_wall, gate_wall, "spaceport gate 4 doorway")
    m.wall_x(ix1 + 45, gate_wall + 1, iy2, ROOM_TOP, "metal2")
    S.room(m, ix1, ix1 + 44, gate_wall + 1, iy2, "spaceport gate 3 lounge")
    S.room(m, ix1 + 46, ix2 - 30, gate_wall + 1, iy2, "spaceport gate 4 lounge")
    m.src(ix1, ix2, iy1, iy2, 0, 24, "calm.ogg", -12)
    m.poi(ix1, (iy1 + iy2) // 2, 0, "the Main Level Spaceport")
    m.ispawn(ix1 + 2, ix2 - 34, iy1 + 2, iy2 - 2, 0, 0, 5000, 4,
             ["health_potion", "frag_grenade", "smoke_bomb", "bomb_vest"])
