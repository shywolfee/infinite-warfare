"""The outside of Freya's Ascent, sitting on the landing field at Z 0. The hull
is modelled as a shell you can walk all the way around, with named faces, engine
nacelles at the stern, landing struts and the boarding ramp under the airlock."""
from lib import GROUND_TOP
import config as C

HULL_TOP = 55   # the hull rises to just below Deck 1


def build(m):
    m.section("FREYA'S ASCENT - exterior hull on the landing field")
    m.at_level(0)
    # The hull shell: a sealed ring of plating you cannot pass through (board via
    # the airlock only). Its inside belly holds the cargo hold and decks above.
    m.wall_y(C.HY2, C.HX1, C.HX2, HULL_TOP, "wallstone")
    m.wall_y(C.HY1, C.HX1, C.HX2, HULL_TOP, "wallstone")
    m.wall_x(C.HX1, C.HY1, C.HY2, HULL_TOP, "wallstone")
    m.wall_x(C.HX2, C.HY1, C.HY2, HULL_TOP, "wallstone")

    # Named exterior faces (one tile off the hull, on the field).
    _split_y(m, C.HX1 - 1, C.HY1, C.HY2, "the port hull of Freya's Ascent")
    _split_y(m, C.HX2 + 1, C.HY1, C.HY2, "the starboard hull of Freya's Ascent")
    _split_x(m, C.HY1 - 1, C.HX1, C.HX2, "the stern of Freya's Ascent")
    _split_x(m, C.HY2 + 1, C.HX1, C.HX2, "the bow of Freya's Ascent")

    # Engine nacelles projecting aft of the stern.
    for nx1, nx2, tag in ((C.HX1 + 18, C.HX1 + 66, "port"), (C.HX2 - 66, C.HX2 - 18, "starboard")):
        m.tile(nx1, nx2, C.HY1 - 40, C.HY1 - 1, 0, 42, "wallstone")
        m.zone(nx1 - 1, nx1 - 1, C.HY1 - 40, C.HY1 - 1, 0, GROUND_TOP, "the " + tag + " engine nacelle")
        m.zone(nx2 + 1, nx2 + 1, C.HY1 - 40, C.HY1 - 1, 0, GROUND_TOP, "the " + tag + " engine nacelle")
        m.zone(nx1, nx2, C.HY1 - 41, C.HY1 - 41, 0, GROUND_TOP, "the " + tag + " engine exhaust")
    m.poi((C.HX1 + C.HX2) // 2, C.HY1 - 42, 0, "the engines of Freya's Ascent")

    # Landing struts at the four corners.
    for sx, sy, tag in ((C.HX1 - 14, C.HY1 + 30, "port aft"), (C.HX2 + 6, C.HY1 + 30, "starboard aft"),
                        (C.HX1 - 14, C.HY2 - 40, "port forward"), (C.HX2 + 6, C.HY2 - 40, "starboard forward")):
        m.tile(sx, sx + 8, sy, sy + 10, 0, 30, "wallstone")
        m.zone(sx, sx + 8, sy - 1, sy - 1, 0, GROUND_TOP, "the " + tag + " landing strut")

    # The boarding ramp beneath the airlock, at the port-forward corner (north).
    m.tile(344, 384, C.HY2 + 1, C.HY2 + 16, 0, 0, "metal2")
    m.zone(344, 384, C.HY2 + 1, C.HY2 + 16, 0, GROUND_TOP, "the boarding ramp of Freya's Ascent")
    m.poi(364, C.HY2 + 20, 0, "the boarding ramp of Freya's Ascent")
    m.at_level(0)


def _split_y(m, x, y1, y2, base):
    third = (y2 - y1) // 3
    m.zone(x, x, y1, y1 + third, 0, GROUND_TOP, base + ", aft section")
    m.zone(x, x, y1 + third + 1, y2 - third - 1, 0, GROUND_TOP, base + " amidships")
    m.zone(x, x, y2 - third, y2, 0, GROUND_TOP, base + ", forward section")


def _split_x(m, y, x1, x2, base):
    third = (x2 - x1) // 3
    m.zone(x1, x1 + third, y, y, 0, GROUND_TOP, base + ", port side")
    m.zone(x1 + third + 1, x2 - third - 1, y, y, 0, GROUND_TOP, base + ", centreline")
    m.zone(x2 - third, x2, y, y, 0, GROUND_TOP, base + ", starboard side")
