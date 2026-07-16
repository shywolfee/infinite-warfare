"""East Meridian: Half-Moon Way, Albeon Way (Meridian International Airport),
Kensington Drive, the minor Jameson Close and Darkstone Ramble, two alleys and
the run-down Hollows neighbourhood."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("EAST MERIDIAN - main streets, minor roads and alleys")
    xw, xe = C.EAST_X1 + 4, C.EAST_X2 - 4

    # --- Main streets ---
    halfmoon = S.street_ns(m, "Half-Moon Way", 868, 875, 160, 952)
    kensington = S.street_ns(m, "Kensington Drive", 1100, 1107, 160, 952)
    albeon = S.street_ew(m, "Albeon Way", 960, 967, xw, xe)
    # --- Minor roads ---
    darkstone = S.street_ew(m, "Darkstone Ramble", 250, 257, 884, 1090, sidewalk=2)
    jameson = S.street_ns(m, "Jameson Close", 980, 985, 300, 468, sidewalk=2)
    for ns in (halfmoon, kensington):
        for ew in (albeon, darkstone):
            S.intersection(m, ns, ew)
    S.intersection(m, jameson, darkstone)

    # --- Two alleys (one leading into a bad neighbourhood) ---
    m.comment("Alleys")
    S.street_ew(m, "Gutter Lane", 360, 363, 902, 978, sidewalk=0, curb=False,
                road_t="gravel1")
    S.street_ns(m, "Ash Alley", 940, 943, 400, 452, sidewalk=0, curb=False,
                road_t="gravel1")
    m.src(895, 985, 300, 440, 0, GROUND_TOP, "wind2.ogg", -12)

    # ================= MERIDIAN INTERNATIONAL AIRPORT =================
    m.section("MERIDIAN INTERNATIONAL AIRPORT (off Albeon Way)")
    _terminal(m)
    _control_tower(m)
    _hangar(m)
    _airfield(m)

    # ================= THE HOLLOWS (run-down neighbourhood) ==========
    m.section("THE HOLLOWS - a run-down neighbourhood off Jameson Close")
    # cracked lane through the Hollows
    m.tile(902, 978, 400, 407, 0, 0, "cement")
    m.zone(902, 978, 400, 407, 0, GROUND_TOP, "Hollow Row (cracked and potholed)")
    m.src(895, 990, 380, 470, 0, GROUND_TOP, "wind2.ogg", -11)
    S.house(m, "2 Hollow Row", 902, 936, 412, 458, floor_t="hardwood",
            wall_t="wallwood", entrance_side="N", basement=True, railings="none")
    S.house(m, "4 Hollow Row", 944, 976, 412, 458, floor_t="hardwood",
            wall_t="wallwood", entrance_side="N", attic=True, railings="left")
    S.house(m, "1 Hollow Row", 902, 936, 340, 386, floor_t="hardwood",
            wall_t="wallwood", entrance_side="S", railings="right")
    m.ispawn(905, 975, 415, 455, 0, 0, 4000, 3,
             ["frag_grenade", "smoke_bomb", "empty_bucket", "rock"])

    # --- Kensington Drive commercial: a motel and a garage ---
    m.comment("Kensington Drive businesses")
    S.shop(m, "Darkstone Auto Garage", 1040, 1092, 300, 350, floor_t="concrete10",
           wall_t="wallbrick", entrance_side="S", goods="tool racks")
    S.office_block(m, "Kensington Motel", 1040, 1092, 700, 790, floor_t="carpet1",
                   wall_t="wallbrick", n_per_side=3, start_no=1, entrance_side="S",
                   lobby_name="the motel front desk")

    m.src(xw, xe, 160, 950, 0, GROUND_TOP, "wind1.ogg", -14)


def _terminal(m):
    m.comment("Airport terminal building")
    name = "Meridian International Airport"
    x1, x2, y1, y2 = 898, 1082, 980, 1076
    ex = (x1 + x2) // 2
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, name, x1, x2, y1, y2, floor_t="tile1", wall_t="wallbrick", ztop=18,
        entrances=[("S", ex - 12, ex - 6), ("S", ex + 6, ex + 12)])
    S.interior_fill(m, "the terminal concourse", ix1, ix2, iy1, iy2)
    # check-in hall (south)
    hall_y2 = iy1 + 24
    S.room(m, ix1, ix2, iy1, hall_y2, "the airport check-in hall")
    for cx in range(ix1 + 6, ix2 - 8, 20):
        S.counter(m, cx, cx + 12, iy1 + 6, iy1 + 7, "an airport check-in desk")
    S.doorway(m, ex - 6, ex - 5, iy1, iy1 + 1, name + " north door")
    # security checkpoint wall
    m.wall_y(hall_y2, ix1, ix2, ROOM_TOP, "wallbrick",
             [(ex - 3, ex + 3)])
    S.doorway(m, ex - 3, ex + 3, hall_y2, hall_y2, "the airport security checkpoint")
    # departures concourse (north of security)
    conc_y1 = hall_y2 + 1
    S.room(m, ix1, ix2, conc_y1, iy2, "the departures concourse")
    # baggage claim carousel in the concourse west end
    m.furniture(ix1 + 3, ix1 + 12, conc_y1 + 4, conc_y1 + 14, 3, "the baggage claim carousel", "metal2")
    # four gates as rooms along the north wall
    gate_wall_y = iy2 - 20
    m.wall_y(gate_wall_y, ix1, ix2, ROOM_TOP, "wallbrick",
             [(ix1 + 12, ix1 + 15), (ix1 + 55, ix1 + 58),
              (ix2 - 58, ix2 - 55), (ix2 - 15, ix2 - 12)])
    gates = [("Gate A1", ix1 + 1, ix1 + 40, ix1 + 12, ix1 + 15),
             ("Gate A2", ix1 + 44, ex - 2, ix1 + 55, ix1 + 58),
             ("Gate B1", ex + 2, ix2 - 44, ix2 - 58, ix2 - 55),
             ("Gate B2", ix2 - 40, ix2 - 1, ix2 - 15, ix2 - 12)]
    # partition walls between gates
    for _, gx1, gx2, _, _ in gates:
        pass
    m.wall_x(ix1 + 42, gate_wall_y + 1, iy2, ROOM_TOP, "wallbrick")
    m.wall_x(ex, gate_wall_y + 1, iy2, ROOM_TOP, "wallbrick")
    m.wall_x(ix2 - 42, gate_wall_y + 1, iy2, ROOM_TOP, "wallbrick")
    for gname, gx1, gx2, dx1, dx2 in gates:
        S.room(m, gx1, gx2, gate_wall_y + 1, iy2, "the airport " + gname + " lounge")
        S.doorway(m, dx1, dx2, gate_wall_y, gate_wall_y, "the airport " + gname + " doorway")
        for sx in range(gx1 + 2, gx2 - 3, 6):
            m.furniture(sx, sx + 3, iy2 - 3, iy2 - 2, 2, gname + " seating")
    m.src(ix1, ix2, iy1, iy2, 0, 18, "calm.ogg", -12)
    m.ispawn(ix1 + 2, ix2 - 2, conc_y1 + 2, gate_wall_y - 2, 0, 0, 5000, 4,
             ["health_potion", "energetic_potion_blue", "frag_grenade", "smoke_bomb"])
    m.poi(ex, iy1, 0, "Meridian International Airport")


def _control_tower(m):
    m.comment("Airport control tower")
    x1, x2, y1, y2 = 1092, 1112, 1000, 1020
    S.building_shell(m, "the airport control tower", x1, x2, y1, y2,
                     floor_t="concrete2", wall_t="wallbrick", ztop=48,
                     entrances=[("S", 1099, 1105)], wall_awareness=True)
    # internal climbing shaft to the cab at the top
    m.tile(x1 + 1, x1 + 2, y1 + 1, y2 - 1, 0, 49, "ladder1")
    m.zone(x1 + 1, x1 + 2, y1 + 1, y2 - 1, 0, 49, "the control tower stairs")
    m.tile(x1 + 3, x1 + 3, y1 + 1, y2 - 1, 0, 2, "wallfence")
    m.tile(x1 + 1, x2 - 1, y1 + 1, y2 - 1, 49, 49, "concrete2")
    m.zone(x1 + 1, x2 - 1, y1 + 1, y2 - 1, 49, 56, "the control tower cab")
    S.counter(m, x1 + 4, x2 - 2, y1 + 2, y1 + 3, "the control tower console")
    m.poi((x1 + x2) // 2, (y1 + y2) // 2, 49, "the airport control tower cab")


def _hangar(m):
    m.comment("Airport hangar")
    x1, x2, y1, y2 = 850, 894, 1000, 1072
    ix1, ix2, iy1, iy2 = S.building_shell(
        m, "the airport hangar", x1, x2, y1, y2, floor_t="concrete10",
        wall_t="metal2", ztop=30, entrances=[("S", (x1 + x2) // 2 - 8, (x1 + x2) // 2 + 8)],
        roof_access=("scaffolding", "W"))
    S.interior_fill(m, "the hangar floor", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2, "the hangar floor")
    m.furniture(ix1 + 2, ix1 + 6, iy1 + 4, iy2 - 4, 3, "a hangar tool bench", "metal2")
    m.ispawn(ix1 + 2, ix2 - 2, iy1 + 2, iy2 - 2, 0, 0, 6000, 2,
             ["repair_kit", "empty_bucket"])


def _airfield(m):
    m.comment("Runway, taxiway and apron")
    # apron between the terminal and the runway
    m.tile(852, 1146, 1078, 1090, 0, 0, "concrete10")
    m.zone(852, 1146, 1078, 1090, 0, GROUND_TOP, "the airport apron")
    # taxiway
    m.tile(852, 1146, 1091, 1094, 0, 0, "concrete5")
    m.zone(852, 1146, 1091, 1094, 0, GROUND_TOP, "the airport taxiway")
    # the runway (long east-west strip)
    m.tile(852, 1146, 1096, 1140, 0, 0, "concrete5")
    m.zone(852, 1146, 1096, 1140, 0, GROUND_TOP, "the airport runway")
    m.zone(852, 900, 1096, 1140, 0, GROUND_TOP, "the west threshold of the runway")
    m.zone(1100, 1146, 1096, 1140, 0, GROUND_TOP, "the east threshold of the runway")
    m.src(852, 1146, 1078, 1140, 0, GROUND_TOP, "wind1.ogg", -10)
    m.poi(999, 1118, 0, "the airport runway")
    m.ispawn(860, 1140, 1098, 1138, 0, 0, 7000, 3,
             ["frag_grenade", "smoke_bomb", "health_potion"])
