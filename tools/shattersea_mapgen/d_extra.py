"""A density pass: extra buildings filling out blocks in each district so the
city reads as dense and lived-in. All placements sit in empty blocks between
the streets laid down by the district modules."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S


def build(m):
    m.section("NORTH MERIDIAN - additional buildings")
    # Police station (east of Beacon Street)
    S.office_block(m, "Meridian Police Station", 770, 820, 786, 876,
                   floor_t="concrete10", wall_t="wallstone", n_per_side=2,
                   start_no=1, entrance_side="S", lobby_name="the police front desk")
    # The Meridian Theatre (north of the plaza)
    tix = S.building_shell(m, "the Meridian Theatre", 656, 744, 1058, 1130,
                           floor_t="carpet1", wall_t="wallbrick", ztop=22,
                           entrances=[("S", 692, 708)])
    ix1, ix2, iy1, iy2 = tix
    S.interior_fill(m, "the theatre lobby", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy1 + 12, "the theatre lobby")
    S.counter(m, ix1 + 3, ix1 + 12, iy1 + 4, iy1 + 5, "the box office")
    mid = (ix1 + ix2) // 2
    m.wall_y(iy1 + 12, ix1, ix2, ROOM_TOP, "wallbrick", [(mid - 2, mid + 2)])
    S.doorway(m, mid - 2, mid + 2, iy1 + 12, iy1 + 12, "the auditorium doors")
    S.room(m, ix1, ix2, iy1 + 13, iy2 - 12, "the theatre auditorium")
    for ry in range(iy1 + 16, iy2 - 14, 4):
        m.furniture(ix1 + 2, ix2 - 2, ry, ry + 1, 2, "a row of theatre seats")
    S.room(m, ix1, ix2, iy2 - 11, iy2, "the theatre stage")
    m.src(ix1, ix2, iy1, iy2, 0, 22, "calm.ogg", -11)
    # Kingsway Hotel (north-west)
    S.office_block(m, "the Kingsway Hotel", 486, 560, 1058, 1140,
                   floor_t="carpet1", wall_t="wallbrick", n_per_side=3,
                   start_no=1, entrance_side="S", lobby_name="the hotel lobby",
                   roof_access=("a ladder", "W"))

    m.section("SOUTH MERIDIAN - additional buildings")
    # St. Mark's Chapel
    cix = S.building_shell(m, "St. Mark's Chapel", 664, 718, 474, 540,
                           floor_t="tile2", wall_t="wallstone", ztop=18,
                           entrances=[("S", 686, 692)])
    ix1, ix2, iy1, iy2 = cix
    S.interior_fill(m, "the chapel", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2, "the chapel")
    for py in range(iy1 + 4, iy2 - 6, 5):
        m.furniture(ix1 + 1, ix1 + 4, py, py + 1, 2, "chapel pew")
        m.furniture(ix2 - 4, ix2 - 1, py, py + 1, 2, "chapel pew")
    S.counter(m, ix1 + 6, ix2 - 6, iy2 - 3, iy2 - 2, "the chapel altar")
    # Southbank Clinic
    S.office_block(m, "the Southbank Clinic", 545, 620, 474, 560,
                   floor_t="tile1", wall_t="wallbrick", n_per_side=3, start_no=1,
                   entrance_side="S", lobby_name="the clinic waiting room")
    m.ispawn(548, 616, 478, 500, 0, 0, 5000, 3,
             ["health_potion", "ultra_health_potion", "life_injection"])
    # Two more houses on Harlow Street
    S.house(m, "8 Harlow Street", 476, 508, 176, 220, entrance_side="E",
            attic=True, railings="both")
    S.house(m, "10 Harlow Street", 476, 508, 232, 276, entrance_side="E",
            basement=True, railings="both")

    m.section("EAST MERIDIAN - additional buildings")
    # Half-Moon Way businesses
    S.shop(m, "the Half-Moon Diner", 836, 862, 500, 560, floor_t="tile2",
           wall_t="wallbrick", entrance_side="E", goods="diner supplies")
    S.shop(m, "East Meridian Post Office", 836, 862, 600, 660,
           floor_t="concrete10", wall_t="wallbrick", entrance_side="E",
           goods="sorting shelves")
    S.office_block(m, "Half-Moon Chambers", 890, 964, 500, 590, floor_t="hardwood",
                   wall_t="wallbrick", n_per_side=3, start_no=1, entrance_side="S",
                   lobby_name="the chambers foyer")
    # Airport long-stay car park (east of the terminal)
    m.tile(1088, 1146, 984, 1074, 0, 0, "concrete10")
    m.zone(1088, 1146, 984, 1074, 0, GROUND_TOP, "the airport long-stay car park")
    for i, py in enumerate(range(988, 1068, 12)):
        m.zone(1092, 1116, py, py + 9, 0, GROUND_TOP, "car park bay %d" % (i * 2 + 1))
        m.zone(1120, 1144, py, py + 9, 0, GROUND_TOP, "car park bay %d" % (i * 2 + 2))

    m.section("WEST MERIDIAN - additional buildings")
    # A boathouse and a seafood market near the docks
    bix = S.building_shell(m, "the Meridian Boathouse", 196, 256, 400, 448,
                           floor_t="plank", wall_t="wallwood", ztop=16,
                           entrances=[("E", 420, 428)], roof_access=("a ladder", "S"))
    ix1, ix2, iy1, iy2 = bix
    S.interior_fill(m, "the boathouse", ix1, ix2, iy1, iy2)
    S.room(m, ix1, ix2, iy1, iy2, "the boathouse")
    m.furniture(ix1 + 2, ix2 - 2, iy1 + 2, iy1 + 8, 3, "an upturned rowing boat", "plank")
    S.shop(m, "the Meridian Fish Market", 330, 420, 196, 240, floor_t="tile2",
           wall_t="wallbrick", entrance_side="N", goods="fish stalls")
    # A row of small waterfront cottages on Gull Street
    S.house(m, "1 Gull Street", 196, 228, 560, 600, floor_t="hardwood",
            wall_t="wallwood", entrance_side="N", railings="both")
    S.house(m, "3 Gull Street", 236, 268, 560, 600, floor_t="hardwood",
            wall_t="wallwood", entrance_side="N", attic=True, railings="both")
