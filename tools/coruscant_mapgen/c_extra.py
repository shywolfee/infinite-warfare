"""Density pass: extra streets, plazas and buildings on every level so Coruscant
reads as the packed, endless metropolis it should be."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    # ---- Main Level extras ----
    m.section("MAIN LEVEL - additional districts")
    m.at_level(C.MAIN)
    # More CoCo Town commerce lanes.
    l1 = S.street_ns(m, "Trandoshan Row", 180, 187, 950, 1300)
    l2 = S.street_ew(m, "Weequay Walk", 1000, 1007, 190, 470)
    S.shop(m, "a CoCo Town spice stall", 220, 300, 1040, 1120, floor_t="hardwood",
           wall_t="wallbrick", entrance_side="E", goods="spice jars")
    S.shop(m, "a CoCo Town cantina", 220, 300, 1150, 1230, floor_t="hardwood2",
           wall_t="wallbrick", entrance_side="E", goods="cantina bottles")
    S.office_block(m, "the CoCo Town Precinct", 340, 430, 980, 1120, floor_t="concrete10",
                   wall_t="wallstone", n_per_side=4, start_no=1, entrance_side="S",
                   lobby_name="the precinct front desk")
    # A landscaped garden plaza.
    m.tile(180, 460, 180, 340, 0, 0, "grass3")
    m.zone(180, 460, 180, 340, 0, GROUND_TOP, "the Skydome Botanical Garden")
    m.src(180, 460, 180, 340, 0, GROUND_TOP, "forest.ogg", -10)
    for tx, ty in ((220, 220), (300, 260), (380, 300), (260, 320), (420, 220)):
        m.tile(tx, tx, ty, ty, 0, 9, "tree")
        m.zone(tx, tx, ty, ty, 0, GROUND_TOP, "an ornamental tree in the botanical garden")
    m.poi(320, 260, 0, "the Skydome Botanical Garden")
    # South-central hab-blocks.
    S.office_block(m, "Monument Hab-Block A", 560, 650, 200, 340, floor_t="carpet1",
                   wall_t="wallbrick", n_per_side=4, start_no=1, entrance_side="N",
                   lobby_name="the hab-block lobby")
    S.office_block(m, "Monument Hab-Block B", 700, 790, 200, 340, floor_t="carpet1",
                   wall_t="wallbrick", n_per_side=4, start_no=1, entrance_side="N",
                   lobby_name="the hab-block lobby")
    # More Uscru venues.
    S.shop(m, "the Coruscant Neon Arcade", 1080, 1160, 200, 300, floor_t="hardwood2",
           wall_t="wallbrick", entrance_side="N", goods="arcade cabinets")
    S.shop(m, "a Uscru chef's noodle bar", 1200, 1280, 200, 300, floor_t="tile2",
           wall_t="wallbrick", entrance_side="N", goods="noodle vats")

    # ---- Calacor Heights extras ----
    m.section("CALACOR HEIGHTS - additional buildings")
    m.at_level(C.HEIGHTS)
    S.office_block(m, "Leado Hab-Tower", 200, 290, 900, 1040, floor_t="carpet1",
                   wall_t="wallbrick", n_per_side=4, start_no=1, entrance_side="S",
                   lobby_name="the hab-tower lobby")
    S.office_block(m, "the Heights Clinic", 1080, 1160, 470, 560, floor_t="tile1",
                   wall_t="wallbrick", n_per_side=3, start_no=1, entrance_side="S",
                   lobby_name="the clinic waiting room")
    S.shop(m, "a Heights droid repair shop", 1080, 1160, 900, 980, floor_t="concrete10",
           wall_t="wallbrick", entrance_side="S", goods="droid parts")
    S.house(m, "a Heights townhouse", 200, 240, 470, 520, floor_t="carpet1",
            wall_t="wallbrick", entrance_side="E", second_floor=True, railings="both")
    S.house(m, "a Heights townhouse", 260, 300, 470, 520, floor_t="carpet1",
            wall_t="wallbrick", entrance_side="E", attic=True, railings="both")

    # ---- Senate District extras ----
    m.section("SENATE DISTRICT - additional ministries")
    m.at_level(C.SENATE)
    S.office_block(m, "the Ministry of Finance", 900, 980, 1000, 1140, floor_t="hardwood",
                   wall_t="wallstone", n_per_side=4, start_no=1, entrance_side="N",
                   lobby_name="the ministry foyer")
    S.office_block(m, "the Republic Archives", 300, 380, 300, 440, floor_t="tile2",
                   wall_t="wallstone", n_per_side=4, start_no=1, entrance_side="N",
                   lobby_name="the archive rotunda")
    m.tile(900, 1080, 300, 440, 0, 0, "concrete12")
    m.zone(900, 1080, 300, 440, 0, GROUND_TOP, "the Memorial Plaza of the Republic")
    m.src(900, 1080, 300, 440, 0, GROUND_TOP, "calm.ogg", -11)
    m.poi(990, 370, 0, "the Memorial Plaza of the Republic")

    # ---- Skydeck extras ----
    m.section("SKYDECK - additional towers")
    m.at_level(C.SKYDECK)
    S.shop(m, "the Skydeck fine-dining restaurant", 300, 380, 640, 720,
           floor_t="hardwood", wall_t="wallbrick", entrance_side="N", goods="banquet tables")
    S.office_block(m, "the Skydeck Observatory", 1000, 1080, 640, 780, floor_t="tile1",
                   wall_t="wallbrick", n_per_side=3, start_no=1, entrance_side="N",
                   lobby_name="the observatory foyer")

    # ---- The Works extras ----
    m.section("THE WORKS - additional sheds")
    m.at_level(C.WORKS)
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, "Foundry Shed Cresh", 380, 470, 700, 820, floor_t="concrete10",
        wall_t="metal2", ztop=26, entrances=[("N", 420, 432)],
        roof_access=("a maintenance ladder", "E"))
    S.interior_fill(m, "Foundry Shed Cresh floor", ix1, ix2, iy1, iy2)
    m.zone(ix1, ix2, iy1, iy2, 0, ROOM_TOP, "Foundry Shed Cresh floor")
    for cx in range(ix1 + 6, ix2 - 10, 20):
        m.furniture(cx, cx + 12, iy1 + 6, iy2 - 6, 4, "stacked machinery", "metal2")

    # ---- Underworld extras ----
    m.section("LEVEL 1313 - additional structures")
    m.at_level(C.UNDERWORLD)
    S.house(m, "a 1313 flophouse", 560, 600, 400, 450, floor_t="concrete10",
            wall_t="wallstone", entrance_side="N", railings="none", basement=True)
    S.shop(m, "a 1313 scrap dealer", 640, 720, 400, 470, floor_t="concrete10",
           wall_t="wallstone", entrance_side="N", goods="scrap heaps")
    m.at_level(0)
