"""Independent navigation/acoustic layer for Shattersea.

Geometry is emitted by the district builders.  This pass names the large-scale
landmarks and open acoustic volumes without flattening the fine room/street
zones that players use for radio navigation.
"""
import config as C
from lib import GROUND_TOP


def build(m):
    m.section("SEMANTIC LAYER: district landmarks and outdoor acoustics")
    m.poi_region(C.WEST_X1, C.WEST_X2, C.ISL_Y1, C.ISL_Y2, 0, C.MAXZ, "West Meridian")
    m.poi_region(C.CEN_X1, C.CEN_X2, C.SOUTH_Y1, C.SOUTH_Y2, 0, C.MAXZ, "South Meridian")
    m.poi_region(C.CEN_X1, C.CEN_X2, C.NORTH_Y1, C.NORTH_Y2, 0, C.MAXZ, "North Meridian")
    m.poi_region(C.EAST_X1, C.EAST_X2, C.ISL_Y1, C.ISL_Y2, 0, C.MAXZ, "East Meridian")
    m.openspace(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP, "the Shattersea coast", "water", "coastal_open_air")
    m.openspace(C.ISL_X1, C.ISL_X2, C.CANAL_Y1, C.CANAL_Y2, 0, GROUND_TOP, "the Old Anchorhold Canal", "stone", "water")
