"""Base layer: the Shattersea, the island, beach, harbour, canal and bridges."""
from lib import GROUND_TOP
import config as C


def build(m):
    m.section("BASE LAYER: The Shattersea (open water everywhere)")
    m.tile(0, C.MAXX, 0, C.MAXY, 0, 0, "shallow")
    m.tile(0, C.MAXX, 0, C.MAXY, -100, -1, "wallrock")
    m.zone(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP, "the open water of the Shattersea")
    m.src(0, C.MAXX, 0, C.MAXY, 0, GROUND_TOP, "ocean1.ogg", -10)

    m.section("MERIDIAN ISLAND: beach ring and district base ground")
    # Beach ring (sand) around the whole island.
    m.tile(C.ISL_X1 - C.BEACH, C.ISL_X2 + C.BEACH, C.ISL_Y1 - C.BEACH, C.ISL_Y2 + C.BEACH, 0, 0, "sand")
    m.zone(C.ISL_X1 - C.BEACH, C.ISL_X2 + C.BEACH, C.ISL_Y1 - C.BEACH, C.ISL_Y2 + C.BEACH, 0, GROUND_TOP, "the beach ringing Meridian island")
    # Named beach segments for orientation.
    m.zone(C.ISL_X1 - C.BEACH, C.ISL_X1 - 1, C.ISL_Y1 - C.BEACH, C.ISL_Y2 + C.BEACH, 0, GROUND_TOP, "the western beach of Meridian")
    m.zone(C.ISL_X2 + 1, C.ISL_X2 + C.BEACH, C.ISL_Y1 - C.BEACH, C.ISL_Y2 + C.BEACH, 0, GROUND_TOP, "the eastern beach of Meridian")
    m.zone(C.ISL_X1 - C.BEACH, C.ISL_X2 + C.BEACH, C.ISL_Y2 + 1, C.ISL_Y2 + C.BEACH, 0, GROUND_TOP, "the northern beach of Meridian")
    m.zone(C.ISL_X1 - C.BEACH, C.ISL_X2 + C.BEACH, C.ISL_Y1 - C.BEACH, C.ISL_Y1 - 1, 0, GROUND_TOP, "the southern beach of Meridian")
    m.src(C.ISL_X1 - C.BEACH, C.ISL_X2 + C.BEACH, C.ISL_Y2, C.ISL_Y2 + C.BEACH, 0, GROUND_TOP, "beach.ogg", -6)
    m.src(C.ISL_X1 - C.BEACH, C.ISL_X2 + C.BEACH, C.ISL_Y1 - C.BEACH, C.ISL_Y1, 0, GROUND_TOP, "beach.ogg", -6)

    # District base ground (detailed content overlays these later).
    m.comment("West Meridian base ground")
    m.ground(C.WEST_X1, C.WEST_X2, C.ISL_Y1, C.ISL_Y2, "concrete2", "the waterfront flats of West Meridian")
    m.comment("South Meridian base ground")
    m.ground(C.CEN_X1, C.CEN_X2, C.SOUTH_Y1, C.SOUTH_Y2, "concrete2", "the streets of South Meridian")
    m.comment("North Meridian base ground")
    m.ground(C.CEN_X1, C.CEN_X2, C.NORTH_Y1, C.NORTH_Y2, "concrete2", "the streets of North Meridian")
    m.comment("East Meridian base ground")
    m.ground(C.EAST_X1, C.EAST_X2, C.ISL_Y1, C.ISL_Y2, "concrete2", "the eastern reaches of East Meridian")

    m.section("THE OLD ANCHORHOLD CANAL and the four bridges")
    # The canal cuts east-west across the whole island.
    m.tile(C.ISL_X1, C.ISL_X2, C.CANAL_Y1, C.CANAL_Y2, 0, 0, "water1")
    m.zone(C.ISL_X1, C.ISL_X2, C.CANAL_Y1, C.CANAL_Y2, 0, GROUND_TOP, "the Old Anchorhold Canal")
    m.src(C.ISL_X1, C.ISL_X2, C.CANAL_Y1, C.CANAL_Y2, 0, GROUND_TOP, "stream2.ogg", -6)
    # Stone quays lining both banks.
    m.tile(C.ISL_X1, C.ISL_X2, C.CANAL_Y2 + 1, C.CANAL_Y2 + 3, 0, 0, "stone")
    m.zone(C.ISL_X1, C.ISL_X2, C.CANAL_Y2 + 1, C.CANAL_Y2 + 3, 0, GROUND_TOP, "the north quay of the Anchorhold Canal")
    m.tile(C.ISL_X1, C.ISL_X2, C.CANAL_Y1 - 3, C.CANAL_Y1 - 1, 0, 0, "stone")
    m.zone(C.ISL_X1, C.ISL_X2, C.CANAL_Y1 - 3, C.CANAL_Y1 - 1, 0, GROUND_TOP, "the south quay of the Anchorhold Canal")

    def bridge(xr, name):
        x1, x2 = xr
        by1, by2 = C.CANAL_Y1 - 4, C.CANAL_Y2 + 4
        m.tile(x1, x2, by1, by2, 0, 0, "bridge")
        m.zone(x1, x2, by1, by2, 0, GROUND_TOP, name)
        # fence railings along both long sides
        m.tile(x1, x1, by1, by2, 0, 3, "wallfence")
        m.tile(x2, x2, by1, by2, 0, 3, "wallfence")
        m.zone(x1 - 1, x1 - 1, by1, by2, 0, GROUND_TOP, name + " west railing")
        m.zone(x2 + 1, x2 + 1, by1, by2, 0, GROUND_TOP, name + " east railing")
        m.src(x1, x2, by1, by2, 0, GROUND_TOP, "stream2.ogg", -7)
        m.poi((x1 + x2) // 2, (by1 + by2) // 2, 0, name)

    bridge(C.BRIDGE_IVORY_X, "the Ivory Bridge")
    bridge(C.BRIDGE_REDMYR_X, "the Redmyr Bridge")
    bridge(C.BRIDGE_OLDSMITH_X, "the Old Smith's Bridge")
    bridge(C.BRIDGE_ANCHOR_X, "the Anchorhold Bridge")

    m.poi((C.ISL_X1 + C.ISL_X2) // 2, (C.ISL_Y1 + C.ISL_Y2) // 2, 0, "the heart of Meridian")
