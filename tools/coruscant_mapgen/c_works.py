"""The Works - a vast abandoned industrial level, all cooling towers, cargo
sheds and dead power plants. Its maintenance shaft is the only turbolift down to
the underworld, which is why 1313 is so hard to reach."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("THE WORKS - abandoned industrial level")
    m.at_level(C.WORKS)
    m.tile(150, 1050, 150, 1050, 0, 0, "concrete10")
    m.zone(150, 1050, 150, 1050, 0, GROUND_TOP, "The Works, an abandoned industrial level")
    m.src(150, 1050, 150, 1050, 0, GROUND_TOP, "rumble.ogg", -12)
    m.src(150, 1050, 150, 1050, 0, GROUND_TOP, "wind1.ogg", -14)
    m.seed(600, 600, 0)
    m.poi(600, 600, 0, "The Works")

    # Fall-holes down to the underworld shelf.
    S.hole(m, 500, 560, 500, 560, "a rusted-out hole in the factory floor")
    S.hole(m, 820, 880, 820, 900, "a torn gap between gantries")

    # Freight roads.
    r1 = S.street_ew(m, "the Foundry Causeway", 480, 491, 170, 1030, sidewalk=2, road_t="cement")
    r2 = S.street_ns(m, "Reactor Road", 600, 611, 170, 1030, sidewalk=2, road_t="cement")
    S.intersection(m, r2, r1)

    # Cargo sheds (big open warehouses).
    _shed(m, "Foundry Shed Aurek", 200, 320, 200, 320)
    _shed(m, "Foundry Shed Besh", 200, 320, 700, 820)
    _shed(m, "the derelict power plant", 700, 900, 200, 360, tall=True)

    # A dead spaceport landing platform on The Works.
    m.comment("the disused Works freight port")
    m.tile(680, 1020, 620, 1010, 0, 0, "metal2")
    m.zone(680, 1020, 620, 1010, 0, GROUND_TOP, "the disused Works freight port")
    for i, (px, py) in enumerate([(720, 680), (860, 680), (720, 860), (860, 860)]):
        m.zone(px, px + 90, py, py + 90, 0, GROUND_TOP, "freight landing pad %d" % (i + 1))
    m.src(680, 1020, 620, 1010, 0, GROUND_TOP, "wind1.ogg", -11)
    m.ispawn(690, 1010, 630, 1000, 0, 0, 6000, 4,
             ["repair_kit", "empty_bucket", "frag_grenade", "health_potion", "box"])

    m.at_level(0)


def _shed(m, name, x1, x2, y1, y2, tall=False):
    ztop = 34 if tall else 24
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, name, x1, x2, y1, y2, floor_t="concrete10", wall_t="metal2", ztop=ztop,
        entrances=[("S", (x1 + x2) // 2 - 8, (x1 + x2) // 2 + 8)],
        roof_access=("a maintenance ladder", "E"))
    S.interior_fill(m, name + " floor", ix1, ix2, iy1, iy2)
    m.zone(ix1, ix2, iy1, iy2, 0, ROOM_TOP, name + " floor")
    for cx in range(ix1 + 6, ix2 - 10, 20):
        m.furniture(cx, cx + 12, iy1 + 6, iy2 - 6, 4, "stacked machinery", "metal2")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 7000, 3,
             ["box", "rock", "repair_kit", "empty_bucket"])
