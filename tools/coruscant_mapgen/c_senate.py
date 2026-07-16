"""The Senate & Federal District - an upper, monumental level of processional
boulevards, the great Senate Rotunda, the Republic Executive Building and rows of
ministry offices."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("THE SENATE & FEDERAL DISTRICT - upper monumental level")
    m.at_level(C.SENATE)
    m.tile(150, 1250, 150, 1250, 0, 0, "concrete12")
    m.zone(150, 1250, 150, 1250, 0, GROUND_TOP, "the Senate District of Coruscant")
    m.src(150, 1250, 150, 1250, 0, GROUND_TOP, "calm.ogg", -12)
    m.src(150, 1250, 150, 1250, 0, GROUND_TOP, "wind1.ogg", -15)
    m.seed(700, 700, 0)

    # Processional boulevards.
    b1 = S.street_ns(m, "the Avenue of the Core Worlds", 690, 705, 180, 1220, sidewalk=5)
    b2 = S.street_ew(m, "the Senate Processional", 690, 705, 180, 1220, sidewalk=5)
    S.intersection(m, b1, b2)

    # The Senate Rotunda - a huge domed chamber.
    m.comment("the Senate Rotunda")
    rx1, rx2, ry1, ry2 = 560, 840, 800, 1080
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, "the Senate Rotunda", rx1, rx2, ry1, ry2, floor_t="tile1",
        wall_t="wallstone", ztop=60, entrances=[("S", 690, 710)])
    S.interior_fill(m, "the Senate chamber floor", ix1, ix2, iy1, iy2)
    m.zone(ix1, ix2, iy1, iy2, 0, 40, "the Senate chamber")
    # concentric rings of delegation pods (jump-up furniture) around a podium
    cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
    m.furniture(cx - 3, cx + 3, cy - 3, cy + 3, 4, "the Chancellor's podium", "metal2")
    ring = 1
    for r in range(24, 120, 26):
        m.furniture(cx - r - 6, cx - r, cy - 8, cy + 8, 3, "senate delegation pods (ring %d)" % ring, "metal2")
        m.furniture(cx + r, cx + r + 6, cy - 8, cy + 8, 3, "senate delegation pods (ring %d)" % ring, "metal2")
        ring += 1
    m.src(ix1, ix2, iy1, iy2, 0, 40, "calm.ogg", -10)
    m.poi(cx, cy, 0, "the Senate Rotunda")
    m.ispawn(ix1 + 4, ix2 - 4, iy1 + 4, iy2 - 4, 0, 0, 6000, 4,
             ["health_potion", "ultra_health_potion", "energetic_potion_rainbow"])

    # The Republic Executive Building (two-storey ministry).
    S.office_block(m, "the Republic Executive Building", 900, 1010, 800, 940,
                   floor_t="hardwood", wall_t="wallstone", n_per_side=4, start_no=1,
                   entrance_side="S", lobby_name="the executive rotunda")

    # Ministry office rows along the processional.
    S.office_block(m, "the Ministry of Trade", 300, 380, 800, 900, floor_t="hardwood",
                   wall_t="wallstone", n_per_side=3, start_no=1, entrance_side="S",
                   lobby_name="the ministry foyer")
    S.office_block(m, "the Ministry of Justice", 300, 380, 950, 1050, floor_t="hardwood",
                   wall_t="wallstone", n_per_side=3, start_no=1, entrance_side="N",
                   lobby_name="the ministry foyer")

    # A guarded observation terrace with a fall-off edge to the level below.
    m.tile(560, 840, 300, 380, 0, 0, "tile1")
    m.zone(560, 840, 300, 380, 0, GROUND_TOP, "the Senate observation terrace")
    S.edge_railing(m, "the terrace railing", 560, 840, 300, 380, "S")
    m.poi(700, 700, 0, "the Senate District")
    m.at_level(0)
