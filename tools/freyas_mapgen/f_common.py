"""Shared builder for a ship deck: a sealed hull section with an aft junction, a
forward junction, a central spine corridor and a row of compartments off each
side. Every compartment has a real doorway onto the spine, and the junctions
hold the turbolifts (added later). No open space anywhere."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def deck(m, dz, label, port_rooms, star_rooms):
    """port_rooms / star_rooms: lists of (room_name, furniture_or_None)."""
    m.at_level(dz)
    # deck floor
    m.tile(C.SX1, C.SX2, C.SY1, C.SY2, 0, 0, "metal5")
    # sealed hull perimeter (the only ways off a deck are the turbolifts)
    m.wall_y(C.SY2, C.SX1, C.SX2, ROOM_TOP, "wallstone")
    m.wall_y(C.SY1, C.SX1, C.SX2, ROOM_TOP, "wallstone")
    m.wall_x(C.SX1, C.SY1, C.SY2, ROOM_TOP, "wallstone")
    m.wall_x(C.SX2, C.SY1, C.SY2, ROOM_TOP, "wallstone")
    # fallback interior zone so nothing is ever unnamed
    m.zone(C.SX1 + 1, C.SX2 - 1, C.SY1 + 1, C.SY2 - 1, 0, ROOM_TOP, label + " interior")
    # aft and forward junctions
    m.zone(C.SX1 + 1, C.SX2 - 1, C.SJ_Y1 + 1, C.SJ_Y2, 0, ROOM_TOP, label + " aft junction")
    m.zone(C.SX1 + 1, C.SX2 - 1, C.NJ_Y1, C.NJ_Y2 - 1, 0, ROOM_TOP, label + " forward junction")
    # bulkheads between the junctions and the compartment section (spine doorway)
    m.wall_y(C.AFT_WALL, C.SX1, C.SX2, ROOM_TOP, "wallstone", [(C.SP_X1, C.SP_X2)])
    m.wall_y(C.FWD_WALL, C.SX1, C.SX2, ROOM_TOP, "wallstone", [(C.SP_X1, C.SP_X2)])
    S.doorway(m, C.SP_X1, C.SP_X2, C.AFT_WALL, C.AFT_WALL, label + " aft spine hatch")
    S.doorway(m, C.SP_X1, C.SP_X2, C.FWD_WALL, C.FWD_WALL, label + " forward spine hatch")
    # the spine corridor
    m.zone(C.SP_X1, C.SP_X2, C.MID_Y1, C.MID_Y2, 0, ROOM_TOP, label + " spine corridor")
    # supply lockers punctuating the spine
    m.furniture(C.SP_X1, C.SP_X1 + 1, C.MID_Y1 + 30, C.MID_Y1 + 33, 3, label + " spine locker", "metal2")
    m.furniture(C.SP_X2 - 1, C.SP_X2, C.MID_Y2 - 33, C.MID_Y2 - 30, 3, label + " spine locker", "metal2")

    _compartments(m, label, "port", C.SX1 + 1, C.SPINE_WW - 1, C.SPINE_WW, port_rooms)
    _compartments(m, label, "starboard", C.SPINE_EW + 1, C.SX2 - 1, C.SPINE_EW, star_rooms)

    m.seed(C.SP_X1 + 1, C.MID_Y1 + 5, 0)
    m.seed((C.SX1 + C.SX2) // 2, C.SJ_Y1 + 20, 0)
    m.seed((C.SX1 + C.SX2) // 2, C.NJ_Y2 - 20, 0)
    m.ispawn(C.SX1 + 4, C.SX2 - 4, C.MID_Y1 + 4, C.MID_Y2 - 4, 0, 0, 4000, 6,
             ["health_potion", "frag_grenade", "smoke_bomb", "energetic_potion_blue",
              "empty_bucket"])
    m.at_level(0)


def _compartments(m, label, side, rx1, rx2, spine_wall_x, rooms):
    """Lay a row of compartments along one side of the spine, each with a
    doorway in the spine wall. spine_wall_x is the shared wall column."""
    n = len(rooms)
    span = C.MID_Y2 - C.MID_Y1 + 1
    seg = span // n
    gaps = []
    for i, (rname, furn) in enumerate(rooms):
        ry1 = C.MID_Y1 + i * seg
        ry2 = C.MID_Y2 if i == n - 1 else C.MID_Y1 + (i + 1) * seg - 1
        rc = (ry1 + ry2) // 2
        m.zone(rx1, rx2, ry1, ry2, 0, ROOM_TOP, rname)
        gaps.append((rc - 1, rc + 1))
        S.doorway(m, spine_wall_x, spine_wall_x, rc - 1, rc + 1, rname + " hatch")
        # divider wall to the next compartment
        if i < n - 1:
            m.wall_y(ry2, rx1, spine_wall_x, ROOM_TOP, "wallstone")
        if furn:
            fx1 = rx1 + 2 if side == "port" else rx2 - 8
            m.furniture(fx1, fx1 + 6, rc - 2, rc + 1, 3, rname + " " + furn, "metal2")
    # the spine wall for this side, with every compartment doorway cut into it
    m.wall_x(spine_wall_x, C.MID_Y1, C.MID_Y2, ROOM_TOP, "wallstone", gaps)
