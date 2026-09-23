"""Shattersea.

Nine islands in a sea that behaves nothing like ours. The world has two moons
and the tide runs four times a day, hard enough that the old city on the
north-eastern rock floods twice between dawn and dusk. Everything here is built
on the high ground and joined by bridges, and everyone who lives here knows the
tide clock on the Guildhall by ear.

The islands, and the one thing each is for:

  Kelphaven        the fishing harbour, the drying lofts, the lifeboat station
  Cinder Rock      a volcanic plug with the lighthouse and the tide siren on it
  Saltmere         evaporation terraces and the saltworks
  Spindlewharf     the cargo island: cranes, transit sheds, the container yard
  Guildhall Isle   the civic middle, where eight of the bridges meet
  Glasswick        the glassworks, the furnaces and the sand quarry
  Roostcliff       cliff-top terraces above a seabird colony, and a funicular
  Thornwater       the freshwater cisterns and the pumping station
  The Drown        what is left of the old city, tidal, and worth the risk

The sea is six below every quay. You can go in and you can swim, and both are
loud; getting out again means finding one of the slipways or ladders, which is
why the bridges are the route and the water is the gamble.
"""
from .builder import Map

W = D = 560
SEA = 0          # the sea floor you end up standing on if you go in
QUAY = 6         # every island's ground level
BRIDGE = 6       # bridges are level with the quays, so no ramps

FISH = ["er_fried_pig_skins", "er_electrolyte_water", "er_small_credit_chip"]
MEDICAL = ["coagulant_serum_bottle", "clotting_tablet_bottle", "er_mini_med_pack"]
TOOLS = ["cleaning_patches", "repair_kit", "rust_remover", "chain_lubricant"]
SALVAGE = ["nanomatic_components", "wiring_harness_kit", "vehicle_battery",
           "salvage_scanner"]
AMMO = ["12_gauge_shell_box", "9x19mm_17_round_magazine",
        "7.62x39mm_30_round_magazine"]
RARE = ["er_large_credit_chip", "er_super_med_pack", "hightech_grapple",
        "reconnaissance_ring"]

# Each island: identifier -> (x1, x2, y1, y2)
ISLANDS = {
    "kelphaven": (40, 160, 40, 160),
    "cinder": (215, 315, 24, 120),
    "saltmere": (380, 520, 48, 168),
    "spindlewharf": (24, 150, 215, 345),
    "guildhall": (210, 350, 205, 355),
    "glasswick": (400, 536, 220, 350),
    "roostcliff": (40, 170, 400, 528),
    "thornwater": (230, 340, 410, 530),
    "drown": (395, 525, 395, 530),
}


def build():
    m = Map("battlegrounds", "Shattersea", W, D, height=48)
    _sea(m)
    _kelphaven(m)
    _cinder(m)
    _saltmere(m)
    _spindlewharf(m)
    _guildhall(m)
    _glasswick(m)
    _roostcliff(m)
    _thornwater(m)
    _drown(m)
    _bridges(m)
    _spawns(m)
    return m.finish()


def _sea(m):
    m.area((1, 559, 1, 559), "The Shatter, open water", "open sea", z=SEA,
           kind="water", bed="heavy surf")
    # Named water, so a swimmer is somewhere rather than nowhere.
    for name, (x1, x2, y1, y2) in ISLANDS.items():
        label = _title(name)
        m.zone((max(x1 - 14, 1), min(x2 + 14, 559), max(y1 - 14, 1), min(y2 + 14, 559)),
               SEA, SEA + 5, f"The Shatter, off {label}")
    m.zone((170, 400, 170, 400), SEA, SEA + 5, "The Shatter, the inner sound")
    # Named water, in four-by-four sectors, so a swimmer is somewhere.
    m.quarters((1, 559, 1, 559), SEA, "The Shatter", head=5, cols=4, rows=4,
               suffix="reach")
    m.ambience((150, 420, 150, 420), SEA, QUAY + 8, "surf")
    m.ambience((1, 559, 1, 60), SEA, QUAY + 8, "ocean")
    m.ambience((1, 559, 500, 559), SEA, QUAY + 8, "distant sea")


def _title(key):
    return {
        "kelphaven": "Kelphaven", "cinder": "Cinder Rock", "saltmere": "Saltmere",
        "spindlewharf": "Spindlewharf", "guildhall": "Guildhall Isle",
        "glasswick": "Glasswick", "roostcliff": "Roostcliff",
        "thornwater": "Thornwater", "drown": "the Drown",
    }[key]


def _island(m, key, surface, kind="open", bed=None, shore="rock wall"):
    """Raise an island out of the sea and give its shoreline its own zone.

    The shore strip matters: it is the last thing between you and a six-unit
    drop into water, and it is the only place a slipway or a ladder can be."""
    x1, x2, y1, y2 = ISLANDS[key]
    label = _title(key)
    m.tile((x1, x2, y1, y2), SEA, QUAY - 1, shore)
    m.area((x1, x2, y1, y2), label, surface, z=QUAY, kind=kind, bed=bed)
    m.quarters((x1 + 3, x2 - 3, y1 + 3, y2 - 3), QUAY, label)
    m.zone((x1, x2, y1, y1 + 2), QUAY, QUAY + 7, f"{label}, southern shore")
    m.zone((x1, x2, y2 - 2, y2), QUAY, QUAY + 7, f"{label}, northern shore")
    m.zone((x1, x1 + 2, y1, y2), QUAY, QUAY + 7, f"{label}, western shore")
    m.zone((x2 - 2, x2, y1, y2), QUAY, QUAY + 7, f"{label}, eastern shore")
    return x1, x2, y1, y2


def _slipway(m, key, x, y, axis, name):
    """A way back out of the water. Six units of wet concrete, laid as one-unit
    steps so you walk up it rather than operating it."""
    if axis == "y":
        r = (x, x + 3, y, y + 7)
    else:
        r = (x, x + 7, y, y + 3)
    m.air(r, SEA, QUAY + 3)
    m.ramp(r, QUAY, SEA, name, axis=axis, material="wet concrete",
           support="stone wall", kind="shore")
    m.poi(x + 1, y, QUAY, name)


def _kelphaven(m):
    x1, x2, y1, y2 = _island(m, "kelphaven", "shingle", kind="shore", bed="surf")
    m.path("Kelphaven, harbour road", (x1 + 6, x2 - 6, 96, 102), "wet cobbles")
    m.path("Kelphaven, net lane", (96, 102, y1 + 6, y2 - 6), "wet cobbles")
    m.area((x1 + 6, 94, y1 + 6, 94), "Kelphaven, drying ground", "packed dirt", z=QUAY)
    m.area((104, x2 - 6, y1 + 6, 94), "Kelphaven, boat park", "shingle", z=QUAY,
           kind="shore")

    # The lifeboat station: a shed over a slipway, which is the one building on
    # this island that had to stay standing.
    m.room((104, 140, 104, 134), QUAY, "Lifeboat station, boathouse",
           floor="timber decking", height=8, wall="timber wall", kind="hangar")
    m.door((116, 122, 104, 104), QUAY, "Boathouse slipway doors",
           floor="timber decking", height=4)
    m.door((140, 140, 116, 120), QUAY, "Boathouse side door", floor="timber decking")
    m.window((104, 104, 124, 128), QUAY + 2, "Boathouse west window")
    m.ambience((105, 139, 105, 133), QUAY, QUAY + 7, "warehouse")
    m.subzone((105, 139, 126, 133), QUAY, "Boathouse, crew room end")
    m.obj("workbench", 108, 128, QUAY, "Lifeboat maintenance bench", 14, 4, 2)
    m.obj("locker", 132, 126, QUAY, "Crew kit lockers", 4, 8, 5)
    m.obj("crate", 110, 110, QUAY, "Flare stores", 5, 5, 3)
    m.fixture("security_radio1", 136, 108, QUAY, "Lifeboat station radio")
    m.poi(110, 112, QUAY, "Lifeboat station boathouse")
    m.loot((106, 138, 106, 132), QUAY, MEDICAL + TOOLS)

    # Drying lofts: a raised timber deck you walk under and onto.
    m.plateau((44, 90, 44, 90), "Kelphaven drying lofts", "old boards", QUAY + 5,
              side="timber wall", kind="platform")
    m.stair((90, 96, 60, 70), QUAY, QUAY + 5, "Drying loft stair", axis="y",
            material="timber stairs", support="timber wall", kind="platform")
    m.obj("crate", 50, 50, QUAY + 5, "Stacked crab pots", 6, 6, 4)
    m.obj("crate", 70, 74, QUAY + 5, "Net bales", 6, 6, 3)
    m.poi(58, 58, QUAY + 5, "Kelphaven drying lofts")

    m.room((44, 78, 104, 130), QUAY, "Kelphaven fish auction",
           floor="wet concrete", height=7, wall="stone wall", kind="hall")
    m.door((56, 62, 104, 104), QUAY, "Auction hall doors", floor="wet concrete")
    m.door((78, 78, 114, 118), QUAY, "Auction hall lane door", floor="wet concrete")
    m.ambience((45, 77, 105, 129), QUAY, QUAY + 6, "shop")
    m.obj("counter", 48, 108, QUAY, "Auction slab", 16, 3, 2)
    m.obj("counter", 48, 120, QUAY, "Ice slab", 16, 3, 2)
    m.fixture("vending_machine", 72, 126, QUAY, "Auction hall machine")
    m.fixture("sink1", 50, 126, QUAY, "Auction wash point")
    m.poi(50, 112, QUAY, "Kelphaven fish auction")
    m.loot((46, 76, 106, 128), QUAY, FISH + MEDICAL)

    _slipway(m, "kelphaven", 144, 36, "y", "Kelphaven slipway")
    m.ladder(x1, 120, SEA, QUAY, "Kelphaven harbour ladder", face=(x1 + 1, x1 + 3, 119, 121))
    m.fixture("street_light", 100, 60, QUAY, "Harbour road light")
    m.fixture("dumpster", 130, 98, QUAY, "Harbour road skip")


def _cinder(m):
    x1, x2, y1, y2 = _island(m, "cinder", "bare rock", kind="shore", bed="high wind")
    # A volcanic plug: it steps up in three shelves to the light.
    m.plateau((x1 + 14, x2 - 14, y1 + 12, y2 - 12), "Cinder Rock, lower shelf",
              "loose scree", QUAY + 6, side="cliff wall", kind="mountain")
    m.plateau((x1 + 30, x2 - 30, y1 + 26, y2 - 26), "Cinder Rock, upper shelf",
              "bare rock", QUAY + 14, side="cliff wall", kind="mountain")
    m.stair((x1 + 6, x1 + 13, y1 + 30, y1 + 42), QUAY, QUAY + 6,
            "Cinder Rock, lower path", axis="y", material="stone stairs",
            support="cliff wall", kind="mountain")
    m.stair((x1 + 16, x1 + 29, y1 + 48, y1 + 56), QUAY + 6, QUAY + 14,
            "Cinder Rock, upper path", axis="x", material="stone stairs",
            support="cliff wall", kind="mountain")

    m.room((x1 + 38, x1 + 62, y1 + 36, y1 + 60), QUAY + 14, "Lighthouse engine room",
           floor="steel plate", height=8, wall="stone wall", kind="plant")
    m.door((x1 + 46, x1 + 50, y1 + 36, y1 + 36), QUAY + 14, "Lighthouse door",
           floor="steel plate")
    m.window((x1 + 38, x1 + 38, y1 + 44, y1 + 48), QUAY + 16, "Engine room window")
    m.ambience((x1 + 39, x1 + 61, y1 + 37, y1 + 59), QUAY + 14, QUAY + 21, "machinery hum")
    m.obj("generator", x1 + 42, y1 + 40, QUAY + 14, "Lighthouse engine", 8, 8, 5)
    m.obj("workbench", x1 + 54, y1 + 52, QUAY + 14, "Keeper's bench", 6, 4, 2)
    m.fixture("security_radio1", x1 + 58, y1 + 40, QUAY + 14, "Lighthouse radio")
    m.poi(x1 + 44, y1 + 40, QUAY + 14, "Lighthouse engine room")
    m.ladder(x1 + 40, y1 + 38, QUAY + 14, QUAY + 22, "Lighthouse ladder",
             material="service ladder")
    m.deck((x1 + 36, x1 + 64, y1 + 34, y1 + 62), QUAY + 22, "Lighthouse gallery")
    m.poi(x1 + 44, y1 + 44, QUAY + 22, "Lighthouse gallery")
    m.ambience((x1 + 36, x1 + 64, y1 + 34, y1 + 62), QUAY + 22, QUAY + 30, "gale")
    m.loot((x1 + 40, x1 + 60, y1 + 38, y1 + 58), QUAY + 14, TOOLS + RARE, seconds=90,
           most=2)

    # The tide siren, which is the island's whole point.
    m.fixture("atrium_speaker", x1 + 70, y1 + 20, QUAY + 6, "Cinder Rock tide siren")
    m.poi(x1 + 70, y1 + 22, QUAY + 6, "Cinder Rock tide siren")
    _slipway(m, "cinder", x1 + 4, y1 + 4, "y", "Cinder Rock landing steps")


def _saltmere(m):
    x1, x2, y1, y2 = _island(m, "saltmere", "clay", kind="open", bed="birds")
    # Evaporation terraces: shallow pans stepping up away from the sea. Each is
    # ankle deep, and each sounds completely different from the clay between.
    for i in range(4):
        z = QUAY + i
        pan = (x1 + 10 + i * 6, x2 - 10 - i * 6, y1 + 14 + i * 14, y1 + 40 + i * 14)
        if i:
            m.tile(pan, QUAY, z - 1, "stone wall")
        m.area(pan, f"Saltmere, number {i + 1} pan", "shallow water", z=z, kind="water")
        m.zone((pan[0], pan[1], pan[2], pan[2] + 1), z, z + 6,
               f"Saltmere, number {i + 1} pan, south bund")
        if i:
            m.stair((pan[0] - 4, pan[0] - 1, pan[2] + 4, pan[2] + 6), z - 1, z,
                    f"Saltmere, number {i} bund step", axis="x",
                    material="stone stairs", support="stone wall", kind="open")
    m.path("Saltmere, tram track", (x2 - 22, x2 - 16, y1 + 6, y2 - 6), "rail ballast",
           z=QUAY)

    m.room((x1 + 12, x1 + 52, y2 - 44, y2 - 10), QUAY, "Saltworks, boiling house",
           floor="screed", height=10, wall="brick wall", kind="workshop")
    m.room((x1 + 52, x1 + 84, y2 - 44, y2 - 26), QUAY, "Saltworks, store",
           floor="screed", height=8, wall="brick wall", kind="warehouse")
    m.door((x1 + 26, x1 + 32, y2 - 44, y2 - 44), QUAY, "Boiling house doors",
           floor="screed", height=4)
    m.door((x1 + 52, x1 + 52, y2 - 38, y2 - 34), QUAY, "Salt store doorway",
           floor="screed")
    m.door((x1 + 84, x1 + 84, y2 - 38, y2 - 34), QUAY, "Salt store loading door",
           floor="screed")
    m.window((x1 + 12, x1 + 12, y2 - 30, y2 - 26), QUAY + 3, "Boiling house window")
    m.ambience((x1 + 13, x1 + 51, y2 - 43, y2 - 11), QUAY, QUAY + 9, "warehouse")
    m.subzone((x1 + 13, x1 + 51, y2 - 20, y2 - 11), QUAY, "Boiling house, pan floor")
    m.obj("tank", x1 + 18, y2 - 22, QUAY, "Brine pan", 10, 10, 4)
    m.obj("generator", x1 + 34, y2 - 40, QUAY, "Boiler", 8, 8, 5)
    m.obj("crate", x1 + 58, y2 - 40, QUAY, "Sacked salt", 6, 6, 4)
    m.fixture("table", x1 + 44, y2 - 36, QUAY, "Saltworks service bench")
    m.poi(x1 + 20, y2 - 20, QUAY, "Saltworks boiling house")
    m.loot((x1 + 14, x1 + 82, y2 - 42, y2 - 12), QUAY, TOOLS + FISH)
    _slipway(m, "saltmere", x1 + 4, y1 + 6, "y", "Saltmere landing steps")
    m.fixture("wooden_planter", x2 - 30, y1 + 10, QUAY, "Saltmere marker post")


def _spindlewharf(m):
    x1, x2, y1, y2 = _island(m, "spindlewharf", "concrete pavement", bed="scrapyard")
    m.path("Spindlewharf, crane road", (x1 + 4, x2 - 4, 276, 284), "asphalt", z=QUAY)
    m.area((x1 + 6, x2 - 6, y1 + 6, 272), "Spindlewharf, container yard",
           "concrete pavement", z=QUAY, kind="open")
    # Container stacks you can walk between and, in two places, onto.
    for i, x in enumerate(range(x1 + 12, x2 - 20, 26)):
        m.block((x, x + 18, y1 + 12, y1 + 40), QUAY, 7,
                f"Container stack {chr(65 + i)}", wall="steel wall", roof="steel deck")
        m.zone((x - 6, x - 1, y1 + 12, y1 + 40), QUAY, QUAY + 7,
               f"Spindlewharf, lane {chr(65 + i)}")
    m.ladder(x1 + 11, y1 + 20, QUAY, QUAY + 7, "Container stack A rungs",
             material="maintenance rungs", face=(x1 + 8, x1 + 10, y1 + 19, y1 + 21))
    m.poi(x1 + 14, y1 + 20, QUAY + 7, "Container stack A roof")

    m.room((x1 + 8, x1 + 62, 292, 336), QUAY, "Number One transit shed",
           floor="warehouse floor", height=12, wall="steel wall", kind="warehouse")
    m.door((x1 + 24, x1 + 34, 292, 292), QUAY, "Transit shed doors",
           floor="warehouse floor", height=4)
    m.door((x1 + 62, x1 + 62, 308, 314), QUAY, "Transit shed east door",
           floor="warehouse floor")
    m.window((x1 + 8, x1 + 8, 320, 326), QUAY + 4, "Transit shed west light")
    m.ambience((x1 + 9, x1 + 61, 293, 335), QUAY, QUAY + 11, "warehouse")
    m.subzone((x1 + 9, x1 + 30, 293, 335), QUAY, "Transit shed, west bay")
    m.subzone((x1 + 40, x1 + 61, 293, 335), QUAY, "Transit shed, east bay")
    m.obj("crate", x1 + 14, 300, QUAY, "Bonded pallet", 8, 8, 4)
    m.obj("crate", x1 + 14, 318, QUAY, "Bonded pallet, second", 8, 8, 4)
    m.obj("workbench", x1 + 44, 300, QUAY, "Cargo inspection bench", 12, 4, 2)
    m.obj("locker", x1 + 54, 326, QUAY, "Dock lockers", 4, 8, 5)
    m.fixture("crate", x1 + 36, 326, QUAY, "Shed supply crate")
    m.fixture("kiosk", x1 + 52, 296, QUAY, "Wharf supply terminal")
    m.poi(x1 + 16, 302, QUAY, "Number One transit shed")
    m.loot((x1 + 10, x1 + 60, 294, 334), QUAY, SALVAGE + TOOLS, most=4)

    # The crane gantry: a grating walk twelve above the yard.
    # The gantry runs north of the container stacks, over the crane road.
    for px in range(x1 + 14, x2 - 8, 24):
        m.tile((px, px + 1, 263, 264), QUAY, QUAY + 11, "steel wall")
    m.deck((x1 + 8, x2 - 8, 262, 266), QUAY + 12, "Wharf crane gantry",
           material="catwalk grating")
    m.ladder(x1 + 7, 264, QUAY, QUAY + 12, "Crane gantry rungs",
             material="maintenance rungs", face=(x1 + 4, x1 + 6, 263, 265))
    m.poi(x1 + 20, 264, QUAY + 12, "Wharf crane gantry")
    m.ambience((x1 + 8, x2 - 8, 262, 266), QUAY + 12, QUAY + 20, "high wind")
    _slipway(m, "spindlewharf", x1 + 4, 340, "y", "Spindlewharf slipway")


def _guildhall(m):
    x1, x2, y1, y2 = _island(m, "guildhall", "granite setts", kind="square",
                             bed="city day")
    m.area((x1 + 30, x2 - 30, y1 + 30, y2 - 30), "Guildhall Square", "flagstones",
           z=QUAY, kind="square")
    m.path("Guildhall Isle, southern approach", (274, 286, y1, y1 + 30), "granite setts",
           z=QUAY)
    m.path("Guildhall Isle, northern approach", (274, 286, y2 - 30, y2), "granite setts",
           z=QUAY)
    m.path("Guildhall Isle, western approach", (x1, x1 + 30, 274, 286), "granite setts",
           z=QUAY)
    m.path("Guildhall Isle, eastern approach", (x2 - 30, x2, 274, 286), "granite setts",
           z=QUAY)

    m.room((248, 312, 248, 312), QUAY, "The Guildhall, great hall",
           floor="polished marble", height=16, wall="stone wall", kind="hall")
    m.door((274, 282, 248, 248), QUAY, "Guildhall south doors",
           floor="polished marble", height=4)
    m.door((274, 282, 312, 312), QUAY, "Guildhall north doors",
           floor="polished marble", height=4)
    m.door((248, 248, 274, 282), QUAY, "Guildhall west doors",
           floor="polished marble", height=4)
    m.window((312, 312, 256, 262), QUAY + 5, "Great hall east light")
    m.window((312, 312, 296, 302), QUAY + 5, "Great hall east light, second")
    m.ambience((249, 311, 249, 311), QUAY, QUAY + 15, "bank hall")
    m.subzone((249, 311, 249, 268), QUAY, "Great hall, south end")
    m.subzone((249, 311, 292, 311), QUAY, "Great hall, the dais")
    m.subzone((249, 268, 269, 291), QUAY, "Great hall, west aisle")
    m.subzone((292, 311, 269, 291), QUAY, "Great hall, east aisle")
    m.obj("pew", 256, 258, QUAY, "Guild bench, south", 40, 3, 4)
    m.obj("pew", 256, 268, QUAY, "Guild bench, second", 40, 3, 4)
    m.obj("table", 268, 300, QUAY, "The masters' table", 22, 6, 3)
    m.fixture("atrium_speaker", 300, 254, QUAY, "Great hall tide clock")
    m.fixture("atm", 254, 306, QUAY, "Guildhall credit desk")
    m.poi(258, 254, QUAY, "The Guildhall great hall")
    m.poi(280, 300, QUAY, "The masters' table")
    m.loot((252, 308, 252, 308), QUAY, RARE + MEDICAL, seconds=90, most=3)
    m.poiregion((x1 + 30, x2 - 30, y1 + 30, y2 - 30), QUAY, QUAY + 8, "Guildhall Square")

    # The bell stage, up the outside of the hall.
    m.plateau((239, 246, 244, 256), "Guildhall bell stage", "old boards", QUAY + 17,
              side="stone wall", kind="platform")
    m.ladder(247, 250, QUAY, QUAY + 17, "Guildhall bell ladder",
             material="service ladder", face=(244, 246, 249, 251))
    m.poi(242, 250, QUAY + 17, "Guildhall bell stage")

    # Market stalls on the square, and the harbour office.
    for i, x in enumerate(range(244, 316, 18)):
        m.obj("counter", x, 232, QUAY, f"Market stall {i + 1}", 12, 3, 2)
    m.fixture("vending_machine", 238, 236, QUAY, "Square provisions machine")
    m.fixture("post_box", 322, 236, QUAY, "Guildhall post box")
    m.room((218, 244, 320, 348), QUAY, "Harbour office", floor="floorboards",
           height=6, wall="timber wall", kind="office")
    m.door((228, 232, 320, 320), QUAY, "Harbour office door", floor="floorboards")
    m.ambience((219, 243, 321, 347), QUAY, QUAY + 5, "office")
    m.obj("table", 222, 326, QUAY, "Tide ledger desk", 10, 5, 2)
    m.obj("bookcase", 236, 326, QUAY, "Chart shelves", 3, 14, 5)
    m.fixture("computer1", 224, 342, QUAY, "Harbour office terminal")
    m.poi(222, 326, QUAY, "Harbour office")
    m.loot((220, 242, 322, 346), QUAY, MEDICAL + TOOLS)
    _slipway(m, "guildhall", 216, 208, "y", "Guildhall Isle landing steps")


def _glasswick(m):
    x1, x2, y1, y2 = _island(m, "glasswick", "gravel", bed="scrapyard")
    m.area((x1 + 8, x1 + 60, y1 + 8, y1 + 70), "Glasswick, sand quarry", "deep sand",
           z=QUAY, kind="open")
    m.stair((x1 + 62, x1 + 74, y1 + 30, y1 + 36), QUAY, QUAY + 4,
            "Quarry haul road", axis="x", material="gravel", support="earth wall",
            kind="open")
    m.plateau((x1 + 74, x2 - 8, y1 + 8, y1 + 70), "Glasswick, quarry rim",
              "gravel", QUAY + 4, side="earth wall")

    m.room((x1 + 16, x1 + 78, y2 - 78, y2 - 20), QUAY, "Glassworks, furnace floor",
           floor="poured floor", height=14, wall="brick wall", kind="hangar")
    m.room((x1 + 78, x1 + 110, y2 - 78, y2 - 50), QUAY, "Glassworks, annealing lehr",
           floor="poured floor", height=9, wall="brick wall", kind="workshop")
    m.room((x1 + 78, x1 + 110, y2 - 50, y2 - 20), QUAY, "Glassworks, packing floor",
           floor="poured floor", height=9, wall="brick wall", kind="warehouse")
    m.door((x1 + 40, x1 + 48, y2 - 78, y2 - 78), QUAY, "Furnace floor doors",
           floor="poured floor", height=4)
    m.door((x1 + 78, x1 + 78, y2 - 66, y2 - 60), QUAY, "Lehr doorway",
           floor="poured floor")
    m.door((x1 + 88, x1 + 94, y2 - 50, y2 - 50), QUAY, "Packing floor doorway",
           floor="poured floor")
    m.door((x1 + 110, x1 + 110, y2 - 40, y2 - 34), QUAY, "Packing floor yard door",
           floor="poured floor")
    m.window((x1 + 16, x1 + 16, y2 - 60, y2 - 54), QUAY + 5, "Furnace floor light")
    m.ambience((x1 + 17, x1 + 77, y2 - 77, y2 - 21), QUAY, QUAY + 13, "warehouse")
    m.subzone((x1 + 17, x1 + 40, y2 - 77, y2 - 21), QUAY, "Furnace floor, west bank")
    m.subzone((x1 + 54, x1 + 77, y2 - 77, y2 - 21), QUAY, "Furnace floor, east bank")
    m.obj("generator", x1 + 22, y2 - 70, QUAY, "Number One furnace", 10, 10, 6)
    m.obj("generator", x1 + 22, y2 - 44, QUAY, "Number Two furnace", 10, 10, 6)
    m.obj("workbench", x1 + 58, y2 - 70, QUAY, "Blowing bench", 14, 4, 2)
    m.obj("display_case", x1 + 84, y2 - 44, QUAY, "Finished ware case", 6, 4, 5)
    m.obj("crate", x1 + 96, y2 - 30, QUAY, "Packing crate", 6, 6, 4)
    m.fixture("table", x1 + 66, y2 - 30, QUAY, "Glassworks service bench")
    m.fixture("scrap_yard1", x1 + 100, y2 - 30, QUAY, "Cullet heap")
    m.poi(x1 + 24, y2 - 68, QUAY, "Glassworks number one furnace")
    m.poi(x1 + 86, y2 - 44, QUAY, "Glassworks annealing lehr")
    m.loot((x1 + 20, x1 + 106, y2 - 74, y2 - 24), QUAY, TOOLS + SALVAGE, most=4)

    # Catwalk over the furnace floor.
    m.tile((x1 + 20, x1 + 74, y2 - 50, y2 - 46), QUAY + 9, QUAY + 9, "catwalk grating")
    m.zone((x1 + 20, x1 + 74, y2 - 50, y2 - 46), QUAY + 9, QUAY + 14,
           "Glassworks, furnace catwalk")
    m.ladder(x1 + 19, y2 - 48, QUAY, QUAY + 9, "Furnace catwalk rungs",
             material="maintenance rungs", face=(x1 + 20, x1 + 22, y2 - 49, y2 - 47))
    m.poi(x1 + 30, y2 - 48, QUAY + 9, "Glassworks furnace catwalk")
    _slipway(m, "glasswick", x2 - 12, y1 + 6, "y", "Glasswick landing steps")


def _roostcliff(m):
    x1, x2, y1, y2 = _island(m, "roostcliff", "long grass", bed="birds")
    m.plateau((x1 + 24, x2 - 10, y1 + 24, y2 - 10), "Roostcliff, cliff top",
              "clipped lawn", QUAY + 18, side="cliff wall", kind="open")
    m.zone((x1 + 24, x1 + 27, y1 + 24, y2 - 10), QUAY + 18, QUAY + 25,
           "Roostcliff, cliff edge")
    m.ambience((x1, x1 + 24, y1, y2), QUAY, QUAY + 20, "birds")
    m.ambience((x1 + 24, x2, y1 + 24, y2), QUAY + 18, QUAY + 26, "high wind")

    # A lift in this engine moves you up and down one shaft; it does not carry
    # you sideways. So the funicular is a tower against the cliff face with its
    # two halls stacked exactly on top of each other, which is also how you
    # would actually build one.
    shaft = (56, 70, 436, 450)
    m.tile(shaft, SEA, QUAY + 17, "cliff wall")
    m.room(shaft, QUAY, "Roostcliff funicular, lower hall", floor="steel plate",
           height=7, wall="steel wall", kind="concourse")
    m.door((shaft[0], shaft[0], 441, 445), QUAY, "Lower hall door",
           floor="steel plate")
    m.room(shaft, QUAY + 18, "Roostcliff funicular, upper hall", floor="steel plate",
           height=7, wall="steel wall", kind="concourse")
    m.door((shaft[1], shaft[1], 441, 445), QUAY + 18, "Upper hall door",
           floor="steel plate")
    levels = [("the shore", QUAY), ("the cliff top", QUAY + 18)]
    m.turbolift((shaft[0] + 1, shaft[1] - 1, shaft[2] + 1, shaft[3] - 1),
                QUAY, QUAY + 6, "Roostcliff funicular", levels)
    m.turbolift((shaft[0] + 1, shaft[1] - 1, shaft[2] + 1, shaft[3] - 1),
                QUAY + 18, QUAY + 24, "Roostcliff funicular", levels)
    m.ambience((shaft[0] + 1, shaft[1] - 1, shaft[2] + 1, shaft[3] - 1),
               QUAY, QUAY + 25, "machinery hum")
    m.poi(shaft[0] + 3, 441, QUAY, "Roostcliff funicular lower hall")
    m.poi(shaft[1] - 3, 441, QUAY + 18, "Roostcliff funicular upper hall")
    m.obj("bench", shaft[0] + 3, 447, QUAY, "Funicular waiting bench", 8, 3, 4)
    m.fixture("vending_machine", shaft[1] - 3, 447, QUAY, "Funicular drinks machine")

    # And a long way round on foot, for when the lift is watched.
    m.stair((x1 + 30, x1 + 38, y1 + 8, y1 + 29), QUAY, QUAY + 18,
            "Roostcliff cliff path", axis="y", material="stone stairs",
            support="cliff wall", kind="mountain")

    for i, y in enumerate(range(y1 + 44, y2 - 30, 28)):
        m.room((x1 + 40, x1 + 88, y, y + 22), QUAY + 18,
               f"Roostcliff terrace, number {i + 1}", floor="floorboards", height=6,
               wall="stone wall", kind="room")
        m.door((x1 + 56, x1 + 60, y, y), QUAY + 18,
               f"Terrace number {i + 1} front door", floor="floorboards")
        m.window((x1 + 40, x1 + 40, y + 8, y + 12), QUAY + 20,
                 f"Terrace number {i + 1} window")
        m.ambience((x1 + 41, x1 + 87, y + 1, y + 21), QUAY + 18, QUAY + 23, "house")
        m.obj("sofa", x1 + 44, y + 4, QUAY + 18, f"Terrace {i + 1} sofa", 8, 4, 4)
        m.obj("bed", x1 + 76, y + 12, QUAY + 18, f"Terrace {i + 1} bed", 6, 9, 4)
        m.loot((x1 + 44, x1 + 84, y + 4, y + 18), QUAY + 18, MEDICAL + FISH, most=2)
    m.fixture("tree2", x1 + 100, y2 - 40, QUAY + 18, "Cliff-top thorn")
    m.fixture("well_speaker", x1 + 110, y1 + 60, QUAY + 18, "Cliff-top rain gauge")
    m.poiregion((x1 + 24, x2 - 10, y1 + 24, y2 - 10), QUAY + 18, QUAY + 26,
                "Roostcliff cliff top")
    _slipway(m, "roostcliff", x1 + 4, y1 + 4, "y", "Roostcliff landing steps")


def _thornwater(m):
    x1, x2, y1, y2 = _island(m, "thornwater", "packed dirt", bed="woodland")
    m.area((x1 + 8, x2 - 8, y1 + 8, y1 + 48), "Thornwater, lower cistern",
           "standing water", z=QUAY, kind="water")
    m.ambience((x1 + 8, x2 - 8, y1 + 8, y1 + 48), QUAY, QUAY + 8, "fountain")
    m.plateau((x1 + 8, x2 - 8, y1 + 56, y1 + 92), "Thornwater, upper cistern bund",
              "flagstones", QUAY + 5, side="stone wall")
    m.area((x1 + 14, x2 - 14, y1 + 62, y1 + 86), "Thornwater, upper cistern",
           "standing water", z=QUAY + 5, kind="water")
    m.stair((x1 + 8, x1 + 16, y1 + 49, y1 + 55), QUAY, QUAY + 5,
            "Cistern bund stair", axis="y", material="stone stairs",
            support="stone wall", kind="open")

    m.room((x1 + 20, x1 + 60, y2 - 46, y2 - 12), QUAY, "Thornwater pumping station",
           floor="steel plate", height=11, wall="brick wall", kind="plant")
    m.door((x1 + 34, x1 + 42, y2 - 46, y2 - 46), QUAY, "Pumping station doors",
           floor="steel plate", height=4)
    m.door((x1 + 60, x1 + 60, y2 - 32, y2 - 26), QUAY, "Pumping station side door",
           floor="steel plate")
    m.window((x1 + 20, x1 + 20, y2 - 26, y2 - 20), QUAY + 4, "Pumping station window")
    m.ambience((x1 + 21, x1 + 59, y2 - 45, y2 - 13), QUAY, QUAY + 10, "machinery hum")
    m.subzone((x1 + 21, x1 + 59, y2 - 22, y2 - 13), QUAY, "Pumping station, switch end")
    m.obj("generator", x1 + 26, y2 - 40, QUAY, "Number One pump", 8, 8, 5)
    m.obj("generator", x1 + 26, y2 - 26, QUAY, "Number Two pump", 8, 8, 5)
    m.obj("screen", x1 + 46, y2 - 20, QUAY, "Pressure board", 3, 10, 4)
    m.fixture("computer2", x1 + 52, y2 - 40, QUAY, "Pumping station terminal")
    m.fixture("streams", x1 + 14, y1 + 30, QUAY, "Cistern inflow")
    m.poi(x1 + 28, y2 - 38, QUAY, "Thornwater pumping station")
    m.loot((x1 + 24, x1 + 56, y2 - 42, y2 - 16), QUAY, TOOLS + SALVAGE)

    # The aqueduct: a covered channel carrying water south, and a walk on top.
    m.tile((x2 - 30, x2 - 22, y1, y2), QUAY, QUAY + 5, "stone wall")
    m.area((x2 - 30, x2 - 22, y1, y2), "Thornwater aqueduct, parapet walk",
           "flagstones", z=QUAY + 6, kind="bridge")
    m.stair((x2 - 21, x2 - 15, y1 + 20, y1 + 28), QUAY, QUAY + 6,
            "Aqueduct parapet stair", axis="y", material="stone stairs",
            support="stone wall", kind="open")
    m.stair((x2 - 38, x2 - 31, y1 + 20, y1 + 28), QUAY, QUAY + 6,
            "Aqueduct parapet stair, west side", axis="y", material="stone stairs",
            support="stone wall", kind="open")
    # An arch through it at ground level, because an aqueduct that walls the
    # island in half is just a wall with a name.
    m.air((x2 - 30, x2 - 22, y1 + 100, y1 + 106), QUAY, QUAY + 3)
    m.tile((x2 - 30, x2 - 22, y1 + 100, y1 + 106), QUAY, QUAY, "flagstones")
    m.zone((x2 - 30, x2 - 22, y1 + 100, y1 + 106), QUAY, QUAY + 3,
           "Thornwater aqueduct, the arch")
    m.portal((x2 - 30, x2 - 22, y1 + 100, y1 + 106), QUAY, QUAY + 3,
             "Thornwater aqueduct, the arch")
    m.poi(x2 - 26, y1 + 60, QUAY + 6, "Thornwater aqueduct parapet")
    _slipway(m, "thornwater", x1 + 4, y1 + 4, "y", "Thornwater landing steps")


def _drown(m):
    """The old city. It is two below everything else, which on a world with
    this tide means it is under water twice a day, and it is the only place on
    the map where the good equipment still is."""
    x1, x2, y1, y2 = ISLANDS["drown"]
    m.tile((x1, x2, y1, y2), SEA, QUAY - 2, "rock wall")
    m.area((x1, x2, y1, y2), "The Drown, flooded streets", "shallow water",
           z=QUAY - 1, kind="water", bed="waterfall")
    z = QUAY - 1
    m.zone((x1, x2, y1, y1 + 2), z, z + 7, "The Drown, southern edge")
    m.zone((x1, x1 + 2, y1, y2), z, z + 7, "The Drown, western edge")
    # The old grid, still legible under the water.
    for i, x in enumerate(range(x1 + 12, x2 - 12, 30)):
        m.path(f"The Drown, {_ordinal(i + 1)} street", (x, x + 6, y1 + 6, y2 - 6),
               "wet cobbles", z=z)
    for i, y in enumerate(range(y1 + 16, y2 - 16, 34)):
        m.path(f"The Drown, {_ordinal(i + 1)} way", (x1 + 6, x2 - 6, y, y + 6),
               "wet cobbles", z=z)

    # Three ruins you can get inside, each with its roof still on.
    ruins = [
        ("The Drown, old exchange", (x1 + 20, x1 + 56, y1 + 26, y1 + 58), "marble"),
        ("The Drown, old infirmary", (x1 + 66, x1 + 104, y1 + 28, y1 + 56), "ceramic tile"),
        ("The Drown, old armoury", (x1 + 40, x1 + 84, y1 + 80, y1 + 116), "steel plate"),
    ]
    for name, r, floor in ruins:
        m.room(r, z, name, floor=floor, height=8, wall="stone wall", kind="cave")
        mid = (r[0] + r[1]) // 2
        m.door((mid - 3, mid + 3, r[2], r[2]), z, f"{name}, breached wall",
               floor=floor, height=4)
        m.window((r[1], r[1], r[2] + 8, r[2] + 12), z + 2, f"{name}, broken window")
        m.ambience((r[0] + 1, r[1] - 1, r[2] + 1, r[3] - 1), z, z + 7, "cave")
        m.poi(r[0] + 4, r[2] + 4, z, name)
        m.loot((r[0] + 3, r[1] - 3, r[2] + 3, r[3] - 3), z, RARE + AMMO, seconds=120,
               most=3)
    m.obj("counter", x1 + 24, y1 + 32, z, "Exchange counter, collapsed", 16, 3, 2)
    m.obj("bed", x1 + 72, y1 + 34, z, "Infirmary cot", 5, 9, 4)
    m.obj("locker", x1 + 46, y1 + 86, z, "Armoury lockers", 4, 14, 5)
    m.obj("crate", x1 + 66, y1 + 104, z, "Sealed ordnance crate", 6, 6, 4)
    m.fixture("hospital_bed", x1 + 88, y1 + 46, z, "Infirmary bed, still standing")
    m.fixture("computer2", x1 + 78, y1 + 86, z, "Armoury records terminal")

    # The one dry place: a tower stump you can climb.
    m.plateau((x2 - 40, x2 - 22, y2 - 40, y2 - 22), "The Drown, tower stump",
              "bare rock", QUAY + 10, side="stone wall", kind="platform")
    m.ladder(x2 - 41, y2 - 32, z, QUAY + 10, "Tower stump ladder",
             material="service ladder", face=(x2 - 44, x2 - 42, y2 - 33, y2 - 31))
    m.poi(x2 - 32, y2 - 32, QUAY + 10, "The Drown, tower stump")
    m.ambience((x2 - 40, x2 - 22, y2 - 40, y2 - 22), QUAY + 10, QUAY + 18, "gale")
    m.poiregion((x1, x2, y1, y2), z, z + 8, "The Drown")
    # Getting out of the Drown: the water here is two below the bridges.
    m.zone((x1, x2, y2 - 2, y2), z, z + 7, "The Drown, northern edge")
    m.zone((x2 - 2, x2, y1, y2), z, z + 7, "The Drown, eastern edge")


def _ordinal(n):
    return {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(n, f"number {n}")


# ---------------------------------------------------------------------------
# Eight bridges radiate from Guildhall Isle and four more join neighbours, so
# there is always a second way round.
SPANS = [
    ("Kelphaven Bridge", (160, 210, 96, 104), "x", [(172, 99), (190, 99)]),
    ("Cinder Bridge", (255, 263, 120, 205), "y", [(258, 140), (258, 175)]),
    ("Saltmere Bridge", (315, 380, 100, 108), "x", [(336, 103), (358, 103)]),
    ("Wharf Bridge", (150, 210, 276, 284), "x", [(168, 279), (190, 279)]),
    ("Glasswick Bridge", (350, 400, 276, 284), "x", [(366, 279), (384, 279)]),
    ("Roostcliff Bridge", (166, 210, 452, 460), "x", [(180, 455), (196, 455)]),
    ("Thornwater Bridge", (275, 283, 355, 410), "y", [(278, 372), (278, 392)]),
    ("Drown Bridge", (338, 396, 440, 448), "x", [(352, 443), (374, 443)]),
    # The peripheral spans.
    ("Kelphaven to Spindlewharf", (86, 94, 160, 215), "y", [(89, 178), (89, 198)]),
    ("Saltmere to Glasswick", (455, 463, 168, 220), "y", [(458, 184), (458, 204)]),
    ("Spindlewharf to Roostcliff", (86, 94, 345, 400), "y", [(89, 362), (89, 384)]),
    ("Thornwater to the Drown", (340, 395, 466, 474), "x", [(356, 469), (374, 469)]),
]


def _bridges(m):
    for name, r, axis, piers in SPANS:
        m.bridge(r, BRIDGE, name, axis=axis, deck="steel deck", rail="railing wall",
                 piers=piers, pier_material="stone wall", bed="surf")
        mid = ((r[0] + r[1]) // 2, (r[2] + r[3]) // 2)
        m.poi(mid[0], mid[1], BRIDGE, f"{name}, midspan")


def _spawns(m):
    for x, y, z in ((100, 60, QUAY), (70, 120, QUAY), (250, 40, QUAY),
                    (420, 80, QUAY), (60, 250, QUAY), (120, 320, QUAY),
                    (240, 230, QUAY), (320, 330, QUAY), (440, 250, QUAY),
                    (500, 320, QUAY), (50, 420, QUAY), (120, 460, QUAY + 18),
                    (260, 440, QUAY), (300, 520, QUAY), (440, 410, QUAY - 1),
                    (500, 500, QUAY - 1)):
        m.spawn(x, y, z)
    m.bunker(280, 280, QUAY, "Guildhall Square")
    m.bunker(100, 100, QUAY, "Kelphaven harbour road")
    m.bunker(80, 280, QUAY, "Spindlewharf container yard")
    m.bunker(460, 280, QUAY, "Glasswick furnace yard")
    m.bunker(280, 470, QUAY, "Thornwater cisterns")
