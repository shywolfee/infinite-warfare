"""Ghost Town.

A city of about half a million people that everybody left. The grid is still
there, the lights are still on in places, and nothing has been cleared away.

The shape of it is deliberately ordinary, because an ordinary city is the one
thing a player can navigate from memory: six avenues running north, six streets
running east, and twenty-five blocks between them. Say "Meridian and Fourth"
over the radio and it means something. Every block is cut through by a service
alley, which is where you go when the crossroads are watched.

Districts, south to north:

  Dockside   the harbour, the quays, the cold store and the container yard
  Southbank  the fish market, the bus station and the timber yard
  Downtown   the towers on Meridian, the plaza, and the overhead transit line
  Old Quarter the covered market, the cathedral close and the narrow lanes
  Foundry    the works, the gasworks and the rail yard, east of Foundry Street
  Civic      the city hall, the library, the courthouse and the hospital
  Northgate  terraced housing and the corner shops that served it

The river runs down the western edge into the harbour, and three bridges cross
it. The transit viaduct runs above Fourth Street and you get onto it by stairs.
"""
from .builder import Map

W = D = 480
# Street grid. Each corridor is fifteen units: three of pavement, nine of road,
# three of pavement.
AVENUES = [  # north-south, (x1, x2, name)
    (28, 42, "Harbour Way"),
    (108, 122, "Meridian Avenue"),
    (188, 202, "Cathedral Street"),
    (268, 282, "Foundry Street"),
    (348, 362, "Eastgate Avenue"),
    (428, 442, "Orbital Road"),
]
STREETS = [  # east-west, (y1, y2, name)
    (28, 42, "Dockside Road"),
    (108, 122, "Fourth Street"),
    (188, 202, "Market Street"),
    (268, 282, "Civic Parade"),
    (348, 362, "Northgate Road"),
    (428, 442, "Orbital Road North"),
]
BLOCK = [(43 + 80 * i, 107 + 80 * i) for i in range(5)]

MEDICAL = ["coagulant_serum_bottle", "clotting_tablet_bottle", "er_mini_med_pack",
           "loose_pain_blocker_capsule"]
TOOLS = ["cleaning_patches", "bore_solvent", "gun_cleaning_kit", "repair_kit"]
AMMO_LIGHT = ["9x19mm_17_round_magazine", "5.56mm_stanag_magazine",
              "45_acp_12_round_magazine"]
AMMO_HEAVY = ["7.62x51mm_20_round_magazine", "12_gauge_shell_box",
              "7.62x39mm_30_round_magazine"]
CASH = ["er_small_credit_chip", "er_coke_can", "er_hot_fries"]
INDUSTRIAL = ["gasoline_can", "engine_oil", "vehicle_battery", "wiring_harness_kit"]


def build():
    m = Map("freeforall", "Ghost Town", W, D, height=48)
    _ground(m)
    _river(m)
    _grid(m)
    _dockside(m)
    _southbank(m)
    _downtown(m)
    _old_quarter(m)
    _foundry(m)
    _civic(m)
    _northgate(m)
    _viaduct(m)
    _fill_remaining_blocks(m)
    _spawns(m)
    return m.finish()


# ---------------------------------------------------------------------------
# The ground everything else is painted on.
def _ground(m):
    # Broad district beds first; streets and buildings are laid over them, and
    # what is left over is the back of a lot or a patch of waste ground.
    m.area((28, 479, 1, 27), "Dockside quay apron", "cracked asphalt", bed="harbour water")
    m.area((28, 479, 43, 107), "Southbank back lots", "cracked asphalt", bed="side street")
    m.area((28, 479, 123, 187), "Downtown back lots", "cracked asphalt", bed="city day")
    m.area((28, 479, 203, 267), "Old Quarter back lots", "cobbles", bed="city birds")
    m.area((28, 479, 283, 347), "Civic back lots", "paving slabs", bed="city hum")
    m.area((28, 479, 363, 427), "Northgate back lots", "worn pavement", bed="quiet street")
    m.area((28, 479, 443, 479), "Northern waste ground", "weeds", bed="grassland")
    m.area((443, 479, 1, 443), "Eastern waste ground", "weeds")


def _river(m):
    """The Alder runs down the western edge of the city into the harbour.

    It is a tidal river with a fordable channel rather than a canyon. The
    quayside stands one unit above the water, so stepping off it is a step you
    take without pressing anything and hear the moment you take it, and getting
    back up is the same step in reverse. Crossing the water is possible
    anywhere and loud everywhere; the jetties and the pontoon are the quiet way
    onto it, and the moored barges are the quiet way along it.
    """
    m.area((1, 21, 1, 479), "The Alder, main channel", "tidal water", z=0,
           kind="water", bed="river")
    m.area((1, 8, 46, 479), "The Alder, west shallows", "shallow water", z=0,
           kind="water")
    m.area((1, 21, 1, 45), "Harbour basin", "open sea", z=0, kind="water",
           bed="harbour water")
    m.plateau((22, 27, 1, 479), "Alder quayside walk", "paving slabs", 1,
              side="stone wall", kind="shore")
    m.ambience((22, 27, 1, 479), 1, 8, "harbour water")

    # Jetties out over the water, and a pontoon you can walk the length of.
    for y, name in ((70, "Cooper's Jetty"), (230, "Market Jetty"),
                    (390, "Northgate Jetty")):
        m.tile((9, 21, y, y + 4), 1, 1, "timber decking")
        m.zone((9, 21, y, y + 4), 1, 7, name)
        m.space((9, 21, y, y + 4), 1, 7, name, "wood", "shore", enclosed=False)
        m.poi(15, y + 2, 1, name)
    m.tile((9, 12, 120, 200), 1, 1, "timber decking")
    m.zone((9, 12, 120, 200), 1, 7, "Alder pontoon")
    m.space((9, 12, 120, 200), 1, 7, "Alder pontoon", "wood", "shore", enclosed=False)
    m.tile((13, 21, 156, 160), 1, 1, "timber decking")
    m.zone((13, 21, 156, 160), 1, 7, "Alder pontoon, shore brow")
    m.poi(11, 165, 1, "Alder pontoon")

    # Two barges, moored alongside.
    for y, name in ((132, "Barge Wren, moored"), (176, "Barge Hazel, moored")):
        m.tile((4, 8, y, y + 18), 1, 1, "ship deck")
        m.zone((4, 8, y, y + 18), 1, 6, name)
        m.space((4, 8, y, y + 18), 1, 6, name, "metal", "cabin", enclosed=False)
        m.tile((4, 8, y + 6, y + 11), 2, 4, "hull wall")
        m.poi(6, y + 2, 1, name)
    m.obj("crate", 5, 150, 1, "Barge cargo crate", 3, 4, 3)

    # A slipway, and a ladder for when you have gone in off the quay.
    m.ramp((22, 27, 298, 302), 1, 0, "Cooper's Slipway", axis="y",
           material="wet concrete", support="stone wall", kind="shore")
    m.poi(24, 298, 0, "Cooper's Slipway")
    m.ladder(22, 250, 0, 1, "Quayside access ladder", face=(23, 25, 249, 251))


def _grid(m):
    """Six avenues, six streets, thirty-six junctions and a name for every
    stretch in between."""
    for x1, x2, name in AVENUES:
        segments = []
        edges = [1] + [s[0] for s in STREETS] + [479]
        labels = _between_labels([s[2] for s in STREETS], "the quay", "the north gate")
        prev = 1
        for (sy1, sy2, sname), label in zip(STREETS, labels):
            segments.append((prev, sy1 - 1, label))
            prev = sy2 + 1
        segments.append((prev, 479, labels[-1].replace("south of ", "north of ")
                         if labels[-1].startswith("south of ") else "north end"))
        # Only the two main thoroughfares carry their own bed. The district
        # bands below do the rest, so a dozen loops are not all in earshot at
        # once on a pool of finite slots.
        bed = "busy street" if name == "Meridian Avenue" else None
        m.street(name, (x1, x2, 1, 479), axis="y", segments=segments, bed=bed)
    for y1, y2, name in STREETS:
        segments = []
        labels = _between_labels([a[2] for a in AVENUES], "the quay", "the eastern edge")
        prev = 28
        for (ax1, ax2, aname), label in zip(AVENUES, labels):
            segments.append((prev, ax1 - 1, label))
            prev = ax2 + 1
        segments.append((prev, 479, "east end"))
        bed = "busy street" if name == "Fourth Street" else None
        m.street(name, (28, 479, y1, y2), axis="x", segments=segments, bed=bed)
    for ax1, ax2, aname in AVENUES:
        for sy1, sy2, sname in STREETS:
            m.junction(f"{aname} and {sname}", (ax1, ax2, sy1, sy2),
                       crossings=[
                           ((ax1, ax2, sy1, sy1 + 2), "south crossing"),
                           ((ax1, ax2, sy2 - 2, sy2), "north crossing"),
                           ((ax1, ax1 + 2, sy1, sy2), "west crossing"),
                           ((ax2 - 2, ax2, sy1, sy2), "east crossing"),
                       ])


def _between_labels(names, first, last):
    out = [f"between {first} and {names[0]}"]
    for a, b in zip(names, names[1:]):
        out.append(f"between {a} and {b}")
    return out


# ---------------------------------------------------------------------------
def _alleys(m, col, row, name, surface="cracked asphalt"):
    """The service alley that crosses every block. Four parcels, a cross of
    alley between them, and a zone for each arm so you know which way you are
    walking when you cannot see the street."""
    x1, x2 = BLOCK[col]
    y1, y2 = BLOCK[row]
    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
    m.path(f"{name}, north alley", (mx - 1, mx + 1, my + 2, y2), surface)
    m.path(f"{name}, south alley", (mx - 1, mx + 1, y1, my - 2), surface)
    m.path(f"{name}, east alley", (mx + 2, x2, my - 1, my + 1), surface)
    m.path(f"{name}, west alley", (x1, mx - 2, my - 1, my + 1), surface)
    m.path(f"{name}, alley crossing", (mx - 1, mx + 1, my - 1, my + 1), surface)
    return _quads(col, row)


def _quads(col, row):
    x1, x2 = BLOCK[col]
    y1, y2 = BLOCK[row]
    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
    return {
        "sw": (x1, mx - 2, y1, my - 2),
        "se": (mx + 2, x2, y1, my - 2),
        "nw": (x1, mx - 2, my + 2, y2),
        "ne": (mx + 2, x2, my + 2, y2),
    }


# ---------------------------------------------------------------------------
def _dockside(m):
    """Block row 0 west: the harbour. Container stacks, a cold store you can
    get inside, and the harbourmaster's office on the quay."""
    q = _alleys(m, 0, 0, "Dock Yard", "rail ballast")
    m.block(q["sw"], 0, 9, "Number Two transit shed", wall="steel wall",
            roof="steel deck")
    m.block(q["ne"], 0, 7, "Container stack, north row", wall="steel wall",
            roof="steel deck")

    # Cold store: a real interior, cold and loud.
    a = q["se"]
    m.room((a[0], a[1], a[2], a[3]), 0, "Cold store, main chamber",
           floor="concrete floor", height=9, wall="steel wall", kind="warehouse")
    m.door((a[0] + 6, a[0] + 9, a[2], a[2]), 0, "Cold store loading door",
           floor="concrete floor")
    m.door((a[1], a[1], a[2] + 8, a[2] + 11), 0, "Cold store alley door",
           floor="concrete floor")
    m.window((a[0], a[0], a[2] + 14, a[2] + 17), 1, "Cold store west window")
    m.ambience((a[0] + 1, a[1] - 1, a[2] + 1, a[3] - 1), 0, 8, "warehouse")
    m.subzone((a[0] + 1, a[0] + 8, a[2] + 1, a[3] - 1), 0, "Cold store, racking aisle")
    m.subzone((a[1] - 8, a[1] - 1, a[2] + 1, a[3] - 1), 0, "Cold store, freight door end")
    m.obj("crate", a[0] + 3, a[2] + 4, 0, "Pallet of frozen stock", 6, 6, 4)
    m.obj("crate", a[0] + 3, a[2] + 14, 0, "Collapsed pallet stack", 6, 6, 3)
    m.obj("generator", a[1] - 6, a[3] - 7, 0, "Refrigeration plant", 5, 6, 4)
    m.fixture("fridge", a[0] + 12, a[2] + 8, 0, "Cold store sample fridge")
    m.loot((a[0] + 4, a[0] + 10, a[2] + 6, a[2] + 14), 0, TOOLS + INDUSTRIAL)
    m.poi(a[0] + 4, a[2] + 6, 0, "Cold store racking")

    # Harbourmaster, out on the quay apron south of Dockside Road.
    m.room((60, 86, 6, 24), 0, "Harbourmaster's office", floor="linoleum",
           height=5, wall="brick wall", kind="office")
    m.door((70, 73, 24, 24), 0, "Harbourmaster's door", floor="linoleum")
    m.window((60, 60, 12, 16), 1, "Harbourmaster's window")
    m.ambience((61, 85, 7, 23), 0, 5, "office")
    m.obj("table", 64, 10, 0, "Movements desk", 10, 5, 2)
    m.obj("bookcase", 80, 10, 0, "Tide tables", 3, 12, 5)
    m.fixture("computer1", 67, 19, 0, "Harbour traffic terminal")
    m.fixture("security_radio1", 82, 19, 0, "Harbour radio set")
    m.poi(70, 14, 0, "Harbourmaster's office")
    m.loot((62, 84, 8, 22), 0, CASH + TOOLS)

    m.poiregion((100, 240, 2, 26), 0, 6, "Dockside quay, deep-water berths")
    m.fixture("street_light", 150, 20, 0, "Quay floodlight")
    m.fixture("dumpster", 205, 12, 0, "Quay skip")
    m.obj("barrier", 120, 22, 0, "Quay edge barrier", 14, 2, 3)
    m.obj("tank", 260, 9, 0, "Bunkering tank", 8, 8, 6)
    m.ambience((28, 300, 1, 27), 0, 8, "scrapyard")


def _southbank(m):
    """Block row 0 centre and east: fish market, bus station, timber yard."""
    q = _alleys(m, 1, 0, "Fish Market block")
    a = q["nw"]
    m.room(a, 0, "Fish market hall", floor="wet concrete", height=8,
           wall="brick wall", kind="hall")
    m.door((a[0] + 8, a[0] + 13, a[3], a[3]), 0, "Fish market north doors",
           floor="wet concrete")
    m.door((a[1], a[1], a[2] + 6, a[2] + 10), 0, "Fish market side door",
           floor="wet concrete")
    m.window((a[0], a[0], a[2] + 4, a[2] + 8), 2, "Fish market clerestory")
    m.ambience((a[0] + 1, a[1] - 1, a[2] + 1, a[3] - 1), 0, 7, "shop")
    m.subzone((a[0] + 1, a[1] - 1, a[3] - 6, a[3] - 1), 0, "Fish market, north aisle")
    m.subzone((a[0] + 1, a[1] - 1, a[2] + 1, a[2] + 6), 0, "Fish market, gutting benches")
    m.obj("counter", a[0] + 3, a[2] + 3, 0, "Gutting bench", 20, 3, 2)
    m.obj("counter", a[0] + 3, a[2] + 9, 0, "Ice trough", 20, 3, 2)
    m.fixture("sink1", a[0] + 5, a[2] + 14, 0, "Market wash point")
    m.fixture("vending_machine", a[1] - 5, a[3] - 4, 0, "Market drinks machine")
    m.poi(a[0] + 5, a[2] + 5, 0, "Fish market gutting benches")
    m.loot(a, 0, CASH)
    m.block(q["ne"], 0, 6, "Ice house", wall="brick wall")
    m.block(q["sw"], 0, 5, "Net loft")
    m.block(q["se"], 0, 5, "Chandlery")

    # Bus station: an open shed rather than a block, so it reads as a place
    # you can walk through.
    x1, x2 = BLOCK[2]
    y1, y2 = BLOCK[0]
    m.area((x1, x2, y1, y2), "Southbank bus station forecourt", "new asphalt",
           kind="square", bed="station")
    for i, bay in enumerate(range(y1 + 6, y2 - 10, 12)):
        m.tile((x1 + 2, x2 - 2, bay, bay + 2), 0, 0, "paving slabs")
        m.zone((x1 + 2, x2 - 2, bay, bay + 2), 0, 7, f"Bus station, stand {i + 1}")
    m.room((x1 + 4, x1 + 30, y2 - 22, y2 - 2), 0, "Bus station concourse",
           floor="terrazzo", height=7, wall="glass curtain wall", kind="concourse")
    m.door((x1 + 12, x1 + 17, y2 - 22, y2 - 22), 0, "Concourse forecourt doors",
           floor="terrazzo")
    m.door((x1 + 30, x1 + 30, y2 - 14, y2 - 10), 0, "Concourse east door",
           floor="terrazzo")
    m.ambience((x1 + 5, x1 + 29, y2 - 21, y2 - 3), 0, 6, "station")
    m.obj("bench", x1 + 8, y2 - 18, 0, "Concourse bench", 12, 3, 4)
    m.obj("bench", x1 + 8, y2 - 10, 0, "Concourse bench, north", 12, 3, 4)
    m.fixture("kiosk", x1 + 26, y2 - 6, 0, "Bus station supply kiosk")
    m.fixture("vending_machine", x1 + 26, y2 - 18, 0, "Concourse drinks machine")
    m.fixture("post_box", x1 + 36, y2 - 6, 0, "Station post box")
    m.poi(x1 + 10, y2 - 12, 0, "Bus station concourse")
    m.loot((x1 + 6, x1 + 28, y2 - 20, y2 - 4), 0, CASH + MEDICAL)

    q = _alleys(m, 3, 0, "Timber yard", "packed dirt")
    m.block(q["sw"], 0, 6, "Timber drying sheds", wall="timber wall",
            roof="bare boards")
    m.block(q["nw"], 0, 6, "Sawmill", wall="timber wall", roof="bare boards")
    m.area(q["ne"], "Timber yard, stacked lengths", "bare boards")
    m.area(q["se"], "Timber yard, sawdust apron", "packed dirt")
    m.obj("crate", q["ne"][0] + 4, q["ne"][2] + 4, 0, "Banded timber stack", 10, 8, 4)
    m.obj("crate", q["ne"][0] + 4, q["ne"][2] + 16, 0, "Softwood stack", 10, 8, 3)
    m.fixture("scrap_yard1", q["se"][0] + 8, q["se"][2] + 8, 0, "Timber yard scrap pile")
    m.poi(q["ne"][0] + 6, q["ne"][2] + 10, 0, "Timber stacks")


def _downtown(m):
    """Meridian Avenue between Fourth and Market: the towers, the plaza, the
    bank, and the transit station under the viaduct."""
    # Plaza, open to the sky, with the towers on three sides.
    x1, x2 = BLOCK[1]
    y1, y2 = BLOCK[2]
    m.area((x1, x2, y1, y2), "Meridian Plaza", "polished marble", kind="square",
           bed="city day")
    m.block((x1, x1 + 24, y1, y1 + 24), 0, 30, "Alder Tower",
            wall="glass curtain wall", roof="steel deck")
    m.block((x2 - 24, x2, y1, y1 + 24), 0, 26, "Meridian House",
            wall="glass curtain wall", roof="steel deck")
    m.block((x2 - 24, x2, y2 - 24, y2), 0, 34, "Corvid Tower",
            wall="glass curtain wall", roof="steel deck")
    m.fixture("atrium_speaker", x1 + 32, y1 + 30, 0, "Plaza announcement speaker")
    m.fixture("wooden_planter", x1 + 30, y1 + 40, 0, "Plaza planter")
    m.fixture("street_light", x1 + 40, y1 + 20, 0, "Plaza light")
    m.obj("planter", x1 + 28, y1 + 32, 0, "Plaza planter bed", 6, 6, 2)
    m.obj("bench", x1 + 36, y1 + 32, 0, "Plaza bench", 10, 3, 4)
    m.poiregion((x1, x2, y1, y2), 0, 8, "Meridian Plaza")

    # The bank, north-west corner of the plaza: a hall you can hear the size of.
    bx1, by1 = x1, y2 - 24
    m.room((bx1, bx1 + 24, by1, y2), 0, "Alder Mutual banking hall",
           floor="polished marble", height=10, wall="stone wall", kind="hall")
    m.door((bx1 + 10, bx1 + 14, by1, by1), 0, "Banking hall doors",
           floor="polished marble")
    m.window((bx1 + 4, bx1 + 7, by1, by1), 3, "Banking hall street window")
    m.window((bx1 + 17, bx1 + 20, by1, by1), 3, "Banking hall west window")
    m.ambience((bx1 + 1, bx1 + 23, by1 + 1, y2 - 1), 0, 9, "bank hall")
    m.subzone((bx1 + 1, bx1 + 23, y2 - 7, y2 - 1), 0,
              "Banking hall, teller counters")
    m.subzone((bx1 + 1, bx1 + 23, by1 + 1, by1 + 8), 0,
              "Banking hall, public floor")
    m.obj("counter", bx1 + 3, y2 - 6, 0, "Teller counter", 18, 3, 2)
    m.obj("bench", bx1 + 4, by1 + 4, 0, "Waiting bench", 10, 3, 4)
    m.fixture("atm", bx1 + 20, by1 + 4, 0, "Banking hall cash machine")
    m.fixture("kiosk", bx1 + 20, by1 + 10, 0, "Bank supply terminal")
    m.poi(bx1 + 6, by1 + 6, 0, "Alder Mutual banking hall")
    m.loot((bx1 + 2, bx1 + 22, by1 + 2, y2 - 2), 0, CASH + MEDICAL, seconds=60)

    # Downtown south block: an office you can get into, and a car park you can
    # get onto the roof of.
    q = _alleys(m, 1, 1, "Meridian south block")
    a = q["nw"]
    m.room(a, 0, "Clearwater Assurance ground floor", floor="office carpet",
           height=6, wall="glass curtain wall", kind="office")
    m.door((a[0] + 6, a[0] + 10, a[3], a[3]), 0, "Assurance lobby doors",
           floor="office carpet")
    m.ambience((a[0] + 1, a[1] - 1, a[2] + 1, a[3] - 1), 0, 5, "office")
    m.obj("table", a[0] + 4, a[2] + 6, 0, "Reception desk", 12, 4, 2)
    m.obj("sofa", a[0] + 18, a[2] + 6, 0, "Lobby sofa", 8, 4, 4)
    m.fixture("computer2", a[0] + 6, a[2] + 16, 0, "Assurance workstation")
    m.poi(a[0] + 6, a[2] + 8, 0, "Clearwater Assurance lobby")
    m.loot(a, 0, CASH)

    b = q["ne"]
    m.area(b, "Meridian multi-storey, ground deck", "poured floor", kind="garage")
    m.zone((b[0], b[0] + 3, b[2], b[3]), 0, 7, "Multi-storey, ramp aisle")
    m.plateau((b[0] + 4, b[1], b[2] + 4, b[3]), "Meridian multi-storey, upper deck",
              "poured floor", 8, side="concrete wall", kind="garage")
    m.ramp((b[0], b[0] + 3, b[2] + 6, b[3] - 2), 0, 8,
           "Multi-storey access ramp", axis="y", material="steel ramp",
           support="concrete wall", kind="garage")
    m.ambience(b, 0, 10, "car park")
    m.fixture("parked_car1", b[0] + 2, b[2] + 2, 0, "Abandoned saloon")
    m.fixture("parked_car2", b[0] + 10, b[2] + 20, 8, "Abandoned estate, upper deck")
    m.poi(b[0] + 12, b[2] + 14, 8, "Multi-storey upper deck")
    m.block(q["sw"], 0, 14, "Fourth Street chambers")
    m.block(q["se"], 0, 12, "Meridian arcade, shuttered")

    # The transit station sits under the viaduct on Fourth Street.
    m.room((124, 150, 96, 106), 0, "Meridian transit ticket hall",
           floor="terrazzo", height=7, wall="stone wall", kind="concourse")
    m.door((134, 138, 106, 106), 0, "Ticket hall street doors", floor="terrazzo")
    m.door((150, 150, 99, 103), 0, "Ticket hall platform door", floor="terrazzo")
    m.ambience((125, 149, 97, 105), 0, 6, "station")
    m.obj("counter", 127, 99, 0, "Ticket window", 10, 3, 2)
    m.fixture("kiosk", 146, 99, 0, "Transit supply kiosk")
    m.poi(130, 101, 0, "Meridian transit ticket hall")
    m.stair((152, 158, 91, 107), 0, 12, "Meridian transit platform stair",
            axis="y", material="concrete stairs", kind="stairwell")


def _viaduct(m):
    """The overhead line. It runs above Fourth Street from the river to
    Eastgate, and it is the only way to cross the city without touching a
    junction."""
    deck = m.bridge((28, 442, 110, 120), 12, "Fourth Street viaduct", axis="x",
                    deck="steel grating", rail="railing wall",
                    piers=[(x, 114) for x in range(44, 440, 40)],
                    kind="bridge", bed="station")
    for i, x in enumerate(range(40, 441, 80)):
        m.zone((x, min(x + 79, 442), deck[2], deck[3]), 12, 18,
               f"Fourth Street viaduct, span {i + 1}")
    m.area((152, 176, 108, 122), "Meridian transit platform", "concrete pavement",
           z=12, kind="platform")
    m.tile((152, 176, 108, 122), 0, 11, "concrete wall")
    # The viaduct rails stop where the platform meets it; a rail across a
    # platform edge is a rail you cannot get past to board anything.
    m.air((152, 176, 110, 110), 13, 14)
    m.air((152, 176, 120, 120), 13, 14)
    m.poiregion((152, 176, 108, 122), 12, 18, "Meridian transit platform")
    m.obj("bench", 156, 112, 12, "Platform bench", 10, 3, 4)
    m.fixture("atrium_speaker", 170, 118, 12, "Platform announcer")
    m.stair((290, 296, 96, 108), 0, 12, "Foundry Street viaduct stair", axis="y",
            material="steel stairs", support="steel wall", kind="stairwell")
    m.area((288, 298, 109, 112), "Foundry Street viaduct landing", "steel grating",
           z=12, kind="platform")
    m.tile((288, 298, 109, 112), 0, 11, "steel wall")
    m.air((288, 298, 110, 110), 13, 14)
    m.ladder(430, 115, 0, 12, "Eastgate viaduct maintenance rungs",
             material="maintenance rungs", face=(429, 431, 114, 116))
    m.poi(200, 115, 12, "Fourth Street viaduct, above Cathedral Street")


def _old_quarter(m):
    """Cathedral Street and the covered market. Narrow, stone, and the one
    part of the city that predates the grid."""
    x1, x2 = BLOCK[2]
    y1, y2 = BLOCK[2]
    m.area((x1, x2, y1, y2), "Cathedral close", "granite setts", kind="courtyard",
           bed="city birds")
    m.room((x1 + 6, x1 + 46, y1 + 8, y2 - 8), 0, "Saint Ewald's nave",
           floor="flagstones", height=14, wall="stone wall", kind="chapel")
    m.door((x1 + 24, x1 + 28, y1 + 8, y1 + 8), 0, "Cathedral west door",
           floor="flagstones", height=4)
    m.door((x1 + 46, x1 + 46, y1 + 26, y1 + 30), 0, "Cathedral vestry door",
           floor="flagstones")
    m.window((x1 + 6, x1 + 6, y1 + 16, y1 + 20), 4, "Cathedral north light")
    m.window((x1 + 6, x1 + 6, y1 + 34, y1 + 38), 4, "Cathedral north light, second")
    m.ambience((x1 + 7, x1 + 45, y1 + 9, y2 - 9), 0, 13, "indoors")
    m.subzone((x1 + 7, x1 + 45, y1 + 9, y1 + 18), 0, "Saint Ewald's, west end")
    m.subzone((x1 + 7, x1 + 45, y2 - 18, y2 - 9), 0, "Saint Ewald's, chancel")
    m.obj("pew", x1 + 12, y1 + 16, 0, "Nave pew, south row", 26, 3, 4)
    m.obj("pew", x1 + 12, y1 + 24, 0, "Nave pew, second row", 26, 3, 4)
    m.obj("pew", x1 + 12, y1 + 32, 0, "Nave pew, third row", 26, 3, 4)
    m.obj("table", x1 + 20, y2 - 14, 0, "Altar table", 10, 4, 3)
    m.poi(x1 + 26, y1 + 12, 0, "Saint Ewald's nave")
    m.ladder(x1 + 8, y1 + 10, 0, 14, "Bell tower ladder", material="service ladder",
             face=(x1 + 9, x1 + 11, y1 + 9, y1 + 11))
    m.poi(x1 + 8, y1 + 10, 14, "Saint Ewald's bell stage")
    m.loot((x1 + 10, x1 + 42, y1 + 12, y2 - 12), 0, MEDICAL + CASH)

    # Covered market, on the block south of the close.
    q = _alleys(m, 2, 1, "Old Quarter lanes", "wet cobbles")
    a = q["nw"]
    m.room(a, 0, "Covered market, main span", floor="cobbles", height=11,
           wall="brick wall", kind="hall")
    m.door((a[0] + 10, a[0] + 16, a[3], a[3]), 0, "Market north entry", floor="cobbles")
    m.door((a[0] + 10, a[0] + 16, a[2], a[2]), 0, "Market south entry", floor="cobbles")
    m.door((a[1], a[1], a[2] + 10, a[2] + 14), 0, "Market lane entry", floor="cobbles")
    m.window((a[0], a[0], a[2] + 6, a[2] + 10), 5, "Market clerestory, west")
    m.ambience((a[0] + 1, a[1] - 1, a[2] + 1, a[3] - 1), 0, 10, "shop")
    m.subzone((a[0] + 1, a[0] + 10, a[2] + 1, a[3] - 1), 0, "Covered market, west row")
    m.subzone((a[1] - 10, a[1] - 1, a[2] + 1, a[3] - 1), 0, "Covered market, east row")
    m.obj("counter", a[0] + 3, a[2] + 4, 0, "Produce stall", 5, 14, 2)
    m.obj("counter", a[1] - 8, a[2] + 4, 0, "Butcher's stall", 5, 14, 2)
    m.obj("crate", a[0] + 12, a[3] - 8, 0, "Abandoned stock crate", 5, 5, 3)
    m.fixture("coke_machine", a[0] + 14, a[2] + 4, 0, "Market drinks machine")
    m.poi(a[0] + 5, a[2] + 8, 0, "Covered market west row")
    m.loot(a, 0, CASH + MEDICAL)
    m.block(q["ne"], 0, 8, "Lantern Row tenements")
    m.block(q["sw"], 0, 7, "Cooper's Yard workshops", wall="timber wall")
    m.block(q["se"], 0, 9, "Old Quarter almshouses")


def _foundry(m):
    """East of Foundry Street. The works, the gasworks, and the rail yard that
    served both."""
    q = _alleys(m, 3, 1, "Gasworks yard", "gravel")
    m.area(q["nw"], "Gasworks, retort house apron", "gravel")
    m.obj("tank", q["nw"][0] + 6, q["nw"][2] + 6, 0, "Number One gasholder", 14, 14, 8)
    m.obj("tank", q["nw"][0] + 6, q["nw"][2] + 20, 0, "Number Two gasholder", 12, 12, 7)
    m.block(q["ne"], 0, 10, "Gasworks retort house", wall="brick wall")
    m.block(q["sw"], 0, 6, "Gasworks stores")
    m.area(q["se"], "Gasworks, coal apron", "packed dirt")
    m.fixture("scrap_yard2", q["se"][0] + 8, q["se"][2] + 8, 0, "Coal apron scrap")
    m.ambience(q["nw"], 0, 8, "scrapyard")

    # The foundry itself: a hangar-sized interior with a gantry you can climb to.
    x1, x2 = BLOCK[3]
    y1, y2 = BLOCK[2]
    m.room((x1, x2, y1, y2), 0, "Alder Foundry, casting floor",
           floor="poured floor", height=16, wall="steel wall", kind="hangar")
    m.door((x1, x1, y1 + 20, y1 + 26), 0, "Foundry street doors", floor="poured floor",
           height=4)
    m.door((x1 + 26, x1 + 32, y2, y2), 0, "Foundry rail doors", floor="poured floor",
           height=4)
    m.window((x2, x2, y1 + 10, y1 + 14), 6, "Foundry east light")
    m.window((x2, x2, y1 + 40, y1 + 44), 6, "Foundry east light, second")
    m.ambience((x1 + 1, x2 - 1, y1 + 1, y2 - 1), 0, 15, "warehouse")
    m.subzone((x1 + 1, x1 + 20, y1 + 1, y2 - 1), 0, "Casting floor, moulding bays")
    m.subzone((x2 - 20, x2 - 1, y1 + 1, y2 - 1), 0, "Casting floor, furnace end")
    m.obj("workbench", x1 + 4, y1 + 8, 0, "Moulding bench", 14, 4, 2)
    m.obj("workbench", x1 + 4, y1 + 30, 0, "Pattern bench", 14, 4, 2)
    m.obj("generator", x2 - 14, y1 + 12, 0, "Induction furnace plant", 8, 8, 6)
    m.obj("tank", x2 - 14, y1 + 34, 0, "Quench tank", 8, 8, 4)
    m.fixture("table", x1 + 24, y1 + 20, 0, "Foundry maintenance bench")
    m.fixture("crate", x1 + 24, y1 + 34, 0, "Foundry parts crate")
    m.poi(x1 + 6, y1 + 10, 0, "Foundry moulding bays")
    m.loot((x1 + 4, x2 - 4, y1 + 4, y2 - 4), 0, TOOLS + INDUSTRIAL + AMMO_HEAVY,
           seconds=60, most=4)
    # Gantry: a grating walkway round two sides, reached by rungs.
    m.tile((x1 + 2, x2 - 2, y1 + 2, y1 + 4), 10, 10, "catwalk grating")
    m.zone((x1 + 2, x2 - 2, y1 + 2, y1 + 4), 10, 15, "Foundry gantry, south run")
    m.tile((x1 + 2, x1 + 4, y1 + 2, y2 - 2), 10, 10, "catwalk grating")
    m.zone((x1 + 2, x1 + 4, y1 + 5, y2 - 2), 10, 15, "Foundry gantry, west run")
    m.ladder(x1 + 3, y1 + 6, 0, 10, "Foundry gantry rungs", material="maintenance rungs",
             face=(x1 + 4, x1 + 6, y1 + 5, y1 + 7))
    m.poi(x1 + 3, y1 + 3, 10, "Foundry gantry")

    # Rail yard: sidings, a locomotive shed and a coaling stage.
    x1, x2 = BLOCK[4]
    roads = list(range(126, 184, 12)) + list(range(206, 264, 12))
    for i, y in enumerate(roads):
        m.area((x1, x2, y, y + 3), f"Rail yard, number {i + 1} road", "rail ballast")
        m.tile((x1, x2, y + 1, y + 2), 0, 0, "riveted steel")
    m.area((x1, x2, 264, 267), "Rail yard, headshunt", "rail ballast")
    m.area((x1, x2, 123, 125), "Rail yard, south throat", "rail ballast")
    m.ambience((x1, x2, 123, 267), 0, 8, "station")
    # The scrapyard is on the waste ground beyond the Orbital Road, where the
    # sidings run out.
    m.area((445, 478, 150, 260), "Eastgate scrapyard", "gravel", bed="scrapyard")
    m.obj("crate", 450, 160, 0, "Crushed body stack", 8, 8, 5)
    m.obj("tank", 462, 200, 0, "Drained tank", 8, 8, 5)
    m.fixture("scrap_yard2", 452, 240, 0, "Scrapyard press")
    m.fixture("scrap_yard1", 468, 176, 0, "Scrapyard grab")
    m.poiregion((445, 478, 150, 260), 0, 8, "Eastgate scrapyard")
    m.room((x1 + 4, x1 + 40, 205, 235), 0, "Locomotive shed", floor="poured floor",
           height=12, wall="brick wall", kind="hangar")
    m.door((x1 + 12, x1 + 20, 205, 205), 0, "Locomotive shed doors",
           floor="poured floor", height=4)
    m.ambience((x1 + 5, x1 + 39, 206, 234), 0, 11, "warehouse")
    m.obj("workbench", x1 + 8, 210, 0, "Fitters' bench", 16, 4, 2)
    m.obj("crate", x1 + 30, 226, 0, "Spares crate", 6, 6, 4)
    m.fixture("scrap_yard1", x1 + 30, 212, 0, "Shed scrap bin")
    m.poi(x1 + 10, 212, 0, "Locomotive shed")
    m.loot((x1 + 6, x1 + 38, 207, 233), 0, TOOLS + INDUSTRIAL)
    m.plateau((x1 + 46, x1 + 58, 140, 176), "Coaling stage", "steel grating", 10,
              side="steel wall", kind="platform")
    m.stair((x1 + 46, x1 + 58, 128, 139), 0, 10, "Coaling stage stair", axis="y",
            material="steel stairs", support="steel wall", kind="platform")
    m.poi(x1 + 50, 150, 10, "Coaling stage")


def _civic(m):
    """Civic Parade: city hall, library, courthouse, police station, hospital."""
    x1, x2 = BLOCK[1]
    y1, y2 = BLOCK[3]
    m.area((x1, x2, y1, y2), "City Hall square", "paving slabs", kind="square",
           bed="city day")
    m.room((x1 + 8, x1 + 48, y1 + 10, y2 - 10), 0, "City Hall, council chamber",
           floor="parquet", height=12, wall="stone wall", kind="hall")
    m.door((x1 + 26, x1 + 30, y1 + 10, y1 + 10), 0, "City Hall front doors",
           floor="parquet", height=4)
    m.door((x1 + 48, x1 + 48, y1 + 24, y1 + 28), 0, "City Hall east door",
           floor="parquet")
    m.window((x1 + 8, x1 + 8, y1 + 18, y1 + 22), 4, "Council chamber window")
    m.ambience((x1 + 9, x1 + 47, y1 + 11, y2 - 11), 0, 11, "bank hall")
    m.subzone((x1 + 9, x1 + 47, y1 + 11, y1 + 20), 0, "Council chamber, public gallery")
    m.subzone((x1 + 9, x1 + 47, y2 - 20, y2 - 11), 0, "Council chamber, benches")
    m.obj("pew", x1 + 14, y1 + 16, 0, "Public gallery bench", 22, 3, 4)
    m.obj("table", x1 + 20, y2 - 18, 0, "Council table", 14, 6, 2)
    m.fixture("atrium_speaker", x1 + 40, y1 + 16, 0, "Chamber public address")
    m.poi(x1 + 28, y1 + 14, 0, "City Hall council chamber")
    m.loot((x1 + 12, x1 + 44, y1 + 14, y2 - 14), 0, CASH)
    m.fixture("street_light", x1 + 58, y1 + 20, 0, "Square light")
    m.obj("headstone", x1 + 56, y1 + 40, 0, "War memorial", 5, 3, 6)
    m.poiregion((x1, x2, y1, y2), 0, 8, "City Hall square")

    q = _alleys(m, 2, 3, "Library block")
    a = q["sw"]
    m.room(a, 0, "Central Library reading room", floor="office carpet", height=9,
           wall="stone wall", kind="hall")
    m.door((a[0] + 10, a[0] + 14, a[2], a[2]), 0, "Library doors", floor="office carpet")
    m.window((a[0], a[0], a[2] + 8, a[2] + 12), 3, "Reading room window")
    m.ambience((a[0] + 1, a[1] - 1, a[2] + 1, a[3] - 1), 0, 8, "indoors")
    m.subzone((a[0] + 1, a[1] - 1, a[3] - 8, a[3] - 1), 0, "Reading room, stacks")
    m.obj("bookcase", a[0] + 3, a[3] - 7, 0, "Reference stack", 3, 14, 5)
    m.obj("bookcase", a[0] + 9, a[3] - 7, 0, "Periodicals stack", 3, 14, 5)
    m.obj("table", a[0] + 6, a[2] + 6, 0, "Reading table", 12, 5, 2)
    m.fixture("computer1", a[1] - 5, a[2] + 5, 0, "Library catalogue terminal")
    m.poi(a[0] + 6, a[2] + 8, 0, "Central Library reading room")
    m.loot(a, 0, CASH + TOOLS)
    m.block(q["nw"], 0, 11, "Crown Courts")
    m.block(q["ne"], 0, 8, "Registry offices")
    b = q["se"]
    m.room(b, 0, "Market Street police station, front office", floor="linoleum",
           height=6, wall="brick wall", kind="office")
    m.door((b[0] + 8, b[0] + 12, b[2], b[2]), 0, "Police station front door",
           floor="linoleum")
    m.door((b[1], b[1], b[2] + 10, b[2] + 14), 0, "Police station yard door",
           floor="linoleum")
    m.ambience((b[0] + 1, b[1] - 1, b[2] + 1, b[3] - 1), 0, 5, "police station")
    m.subzone((b[0] + 1, b[1] - 1, b[3] - 8, b[3] - 1), 0,
              "Police station, cell corridor")
    m.obj("counter", b[0] + 3, b[2] + 4, 0, "Front counter", 14, 3, 2)
    m.obj("locker", b[1] - 6, b[3] - 7, 0, "Equipment lockers", 4, 10, 5)
    m.fixture("security_radio1", b[0] + 6, b[3] - 5, 0, "Station radio")
    m.fixture("computer2", b[0] + 16, b[2] + 8, 0, "Station terminal")
    m.ambience((b[1] - 8, b[1] - 1, b[3] - 8, b[3] - 1), 0, 5, "armoury")
    m.poi(b[0] + 6, b[2] + 6, 0, "Police station front office")
    m.loot(b, 0, AMMO_LIGHT + AMMO_HEAVY, seconds=75, most=3)

    # Hospital, north-east of the parade.
    x1, x2 = BLOCK[3]
    y1, y2 = BLOCK[4]
    m.area((x1, x2, y1, y2), "Saint Ewald's Hospital forecourt", "new asphalt",
           kind="courtyard")
    m.room((x1 + 4, x1 + 34, y1 + 6, y2 - 6), 0, "Hospital, accident reception",
           floor="linoleum", height=7, wall="brick wall", kind="ward")
    m.room((x1 + 34, x1 + 60, y1 + 6, y1 + 30), 0, "Hospital, treatment bay",
           floor="linoleum", height=7, wall="brick wall", kind="ward")
    m.room((x1 + 34, x1 + 60, y1 + 30, y2 - 6), 0, "Hospital, observation ward",
           floor="linoleum", height=7, wall="brick wall", kind="ward")
    m.door((x1 + 16, x1 + 21, y1 + 6, y1 + 6), 0, "Hospital ambulance doors",
           floor="linoleum", height=4)
    m.door((x1 + 34, x1 + 34, y1 + 14, y1 + 18), 0, "Treatment bay doorway",
           floor="linoleum")
    m.door((x1 + 34, x1 + 34, y1 + 38, y1 + 42), 0, "Observation ward doorway",
           floor="linoleum")
    m.door((x1 + 44, x1 + 48, y1 + 30, y1 + 30), 0, "Ward connecting door",
           floor="linoleum")
    m.ambience((x1 + 5, x1 + 59, y1 + 7, y2 - 7), 0, 6, "hospital")
    m.obj("bench", x1 + 8, y1 + 12, 0, "Reception bench", 12, 3, 4)
    m.obj("counter", x1 + 8, y2 - 14, 0, "Triage counter", 14, 3, 2)
    m.obj("cabinet", x1 + 38, y1 + 10, 0, "Drug cabinet", 5, 3, 4)
    m.obj("bed", x1 + 38, y1 + 36, 0, "Observation cot", 5, 9, 4)
    m.fixture("hospital_bed", x1 + 46, y1 + 20, 0, "Treatment bay bed")
    m.fixture("hospital_defibolator", x1 + 52, y1 + 20, 0, "Treatment defibrillator")
    m.fixture("hospital_ventilator", x1 + 52, y1 + 38, 0, "Ward ventilator")
    m.fixture("instrument_prep", x1 + 46, y1 + 38, 0, "Instrument preparation bench")
    m.poi(x1 + 10, y1 + 10, 0, "Hospital accident reception")
    m.poi(x1 + 46, y1 + 20, 0, "Hospital treatment bay")
    m.loot((x1 + 6, x1 + 58, y1 + 8, y2 - 8), 0, MEDICAL, seconds=50, most=4)
    m.fixture("parked_car3", x1 + 68, y1 + 12, 0, "Abandoned ambulance")


def _northgate(m):
    """Terraced housing. Two streets of back-to-backs with a shared back lane,
    and the corner shop that served them."""
    for row in (3, 4):
        q = _alleys(m, 0, row, f"Northgate terraces, {'lower' if row == 3 else 'upper'} block",
                    "cobbles")
        for key, label in (("sw", "Alder Row"), ("se", "Foundry Row"),
                           ("nw", "Chapel Row"), ("ne", "Gasworks Row")):
            a = q[key]
            if key == "nw" and row == 4:
                continue
            m.block(a, 0, 7, f"{label}, {'lower' if row == 3 else 'upper'} terrace",
                    wall="brick wall", roof="worn pavement")
    # One house opened up, and the corner shop.
    q = _quads(0, 4)
    a = q["nw"]
    m.room((a[0], a[0] + 14, a[2], a[2] + 14), 0, "Number Fourteen, front room",
           floor="floorboards", height=5, wall="brick wall", kind="room")
    m.room((a[0], a[0] + 14, a[2] + 14, a[2] + 26), 0, "Number Fourteen, scullery",
           floor="ceramic tile", height=5, wall="brick wall", kind="kitchen")
    m.door((a[0] + 5, a[0] + 8, a[2], a[2]), 0, "Number Fourteen front door",
           floor="floorboards")
    m.door((a[0] + 5, a[0] + 8, a[2] + 14, a[2] + 14), 0, "Scullery doorway",
           floor="ceramic tile")
    m.door((a[0] + 5, a[0] + 8, a[2] + 26, a[2] + 26), 0, "Number Fourteen back door",
           floor="ceramic tile")
    m.window((a[0], a[0], a[2] + 4, a[2] + 8), 2, "Front room window")
    m.ambience((a[0] + 1, a[0] + 13, a[2] + 1, a[2] + 25), 0, 4, "house")
    m.obj("sofa", a[0] + 2, a[2] + 4, 0, "Front room sofa", 8, 4, 4)
    m.obj("counter", a[0] + 2, a[2] + 20, 0, "Scullery counter", 10, 3, 2)
    m.fixture("sink2", a[0] + 11, a[2] + 20, 0, "Scullery sink")
    m.fixture("tv", a[0] + 11, a[2] + 4, 0, "Front room television")
    m.poi(a[0] + 4, a[2] + 4, 0, "Number Fourteen front room")
    m.loot((a[0] + 2, a[0] + 12, a[2] + 2, a[2] + 24), 0, MEDICAL + CASH)
    m.block((a[0] + 16, a[1], a[2], a[3]), 0, 7, "Chapel Row, upper terrace")

    b = _quads(1, 4)["sw"]
    m.room((b[0], b[0] + 18, b[2], b[2] + 18), 0, "Northgate corner shop",
           floor="linoleum", height=5, wall="brick wall", kind="shop")
    m.door((b[0] + 7, b[0] + 11, b[2], b[2]), 0, "Corner shop door", floor="linoleum")
    m.window((b[0], b[0], b[2] + 4, b[2] + 10), 2, "Corner shop window")
    m.ambience((b[0] + 1, b[0] + 17, b[2] + 1, b[2] + 17), 0, 4, "small shop")
    m.obj("counter", b[0] + 2, b[2] + 14, 0, "Shop counter", 12, 3, 2)
    m.obj("bookcase", b[0] + 14, b[2] + 3, 0, "Shop shelving", 3, 10, 4)
    m.fixture("vending_machine", b[0] + 14, b[2] + 15, 0, "Corner shop machine")
    m.fixture("atm", b[0] + 4, b[2] + 4, 0, "Corner shop cash machine")
    m.poi(b[0] + 6, b[2] + 6, 0, "Northgate corner shop")
    m.loot((b[0] + 2, b[0] + 16, b[2] + 2, b[2] + 16), 0, CASH + MEDICAL)
    m.block((b[0] + 20, b[1], b[2], b[3]), 0, 6, "Northgate parade, shuttered units")

    # A park, because a city with no quiet place in it is a city with nowhere
    # to listen from.
    x1, x2 = BLOCK[2]
    y1, y2 = BLOCK[4]
    m.area((x1, x2, y1, y2), "Corvid Park", "clipped lawn", kind="open", bed="park")
    m.path("Corvid Park, main walk", (x1, x2, (y1 + y2) // 2 - 1, (y1 + y2) // 2 + 1),
           "gravel")
    m.path("Corvid Park, north walk", ((x1 + x2) // 2 - 1, (x1 + x2) // 2 + 1, y1, y2),
           "gravel")
    m.area((x1 + 40, x2 - 8, y1 + 40, y2 - 8), "Corvid Park, bandstand lawn",
           "long grass")
    m.plateau((x1 + 48, x1 + 58, y1 + 48, y1 + 58), "Corvid Park bandstand",
              "bare boards", 2, side="timber wall", kind="platform")
    m.stair((x1 + 44, x1 + 47, y1 + 50, y1 + 56), 0, 2, "Bandstand steps", axis="x",
            material="timber stairs", support="timber wall", kind="platform")
    m.fixture("tree1", x1 + 12, y1 + 12, 0, "Park plane tree")
    m.fixture("tree3", x1 + 50, y1 + 14, 0, "Park lime tree")
    m.fixture("streams", x1 + 20, y2 - 16, 0, "Park brook")
    m.obj("bench", x1 + 16, y1 + 30, 0, "Park bench", 10, 3, 4)
    m.obj("bench", x1 + 40, y2 - 20, 0, "Park bench, north walk", 10, 3, 4)
    m.poiregion((x1, x2, y1, y2), 0, 8, "Corvid Park")
    m.poi(x1 + 52, y1 + 52, 2, "Corvid Park bandstand")


# ---------------------------------------------------------------------------
# Everything the districts did not claim. Each block is still named for what
# it was, rather than being left as a hole in the map.
REMAINING = {
    (0, 1): ("Dock sheds", [("Number Four transit shed", 8, "steel wall"),
                            ("Number Five transit shed", 8, "steel wall"),
                            ("Bonded store", 10, "brick wall"),
                            ("Customs house", 9, "stone wall")]),
    (0, 2): ("Warehouse Row", [("Alder Wharf warehouse", 12, "brick wall"),
                               ("Nightingale warehouse", 11, "brick wall"),
                               ("Riverside bond", 10, "brick wall"),
                               ("Grain store", 14, "steel wall")]),
    (1, 3): None,  # City Hall square
    (2, 0): None,  # bus station
    (3, 3): ("Foundry offices", [("Foundry counting house", 9, "brick wall"),
                                 ("Drawing office", 8, "brick wall"),
                                 ("Works canteen", 6, "brick wall"),
                                 ("Pattern store", 7, "timber wall")]),
    (3, 4): None,  # hospital
    (4, 0): ("Eastgate depot", [("Bus depot", 9, "steel wall"),
                                ("Fuel store", 5, "steel wall"),
                                ("Depot workshops", 8, "steel wall"),
                                ("Drivers' block", 7, "brick wall")]),
    (4, 3): ("Southbank terraces", [("Quay Row", 6, "brick wall"),
                                    ("Ferry Row", 6, "brick wall"),
                                    ("Bridge Row", 6, "brick wall"),
                                    ("Tanner's Row", 6, "brick wall")]),
    (4, 4): ("Eastgate allotments", None),
    (3, 4): None,  # hospital
    (1, 4): None,
    (0, 3): None,
    (0, 4): None,
    (2, 4): None,
    (2, 3): None,
    (1, 2): None,
    (2, 2): None,
    (3, 2): None,
    (4, 2): None,
    (0, 0): None,
    (1, 0): None,
    (3, 0): None,
    (1, 1): None,
    (2, 1): None,
    (3, 1): None,
    (4, 1): None,  # rail yard
}


def _fill_remaining_blocks(m):
    for (col, row), spec in sorted(REMAINING.items()):
        if spec is None:
            continue
        name, parcels = spec
        if parcels is None:
            x1, x2 = BLOCK[col]
            y1, y2 = BLOCK[row]
            if name == "Eastgate allotments":
                m.area((x1, x2, y1, y2), name, "wet earth", bed="grassland")
                m.path(f"{name}, central path", (x1, x2, (y1 + y2) // 2 - 1,
                                                 (y1 + y2) // 2 + 1), "packed dirt")
                m.fixture("wooden_planter", x1 + 20, y1 + 20, 0, "Allotment cold frame")
                m.poiregion((x1, x2, y1, y2), 0, 8, name)
            elif name == "Eastgate scrapyard":
                m.area((x1, x2, y1, y2), name, "gravel", bed="scrapyard")
                m.obj("crate", x1 + 10, y1 + 10, 0, "Crushed body stack", 8, 8, 5)
                m.obj("tank", x1 + 30, y1 + 30, 0, "Drained tank", 8, 8, 5)
                m.fixture("scrap_yard2", x1 + 20, y1 + 40, 0, "Scrapyard press")
                m.poiregion((x1, x2, y1, y2), 0, 8, name)
            else:
                for i, y in enumerate(range(y1, y2 - 10, 12)):
                    m.area((x1, x2, y, y + 3), f"{name}, siding {i + 1}", "rail ballast")
                m.poiregion((x1, x2, y1, y2), 0, 8, name)
            continue
        q = _alleys(m, col, row, name)
        for key, (label, storeys, wall) in zip(("sw", "se", "nw", "ne"), parcels):
            m.block(q[key], 0, storeys, label, wall=wall)


def _spawns(m):
    """Sixteen, spread across every district, all on the street grid so the
    server can always find a clear one."""
    points = [
        (35, 60, 0), (35, 300, 0), (115, 70, 0), (115, 230, 0),
        (115, 400, 0), (195, 60, 0), (195, 160, 0), (195, 320, 0),
        (275, 100, 0), (275, 240, 0), (275, 420, 0), (355, 70, 0),
        (355, 200, 0), (355, 380, 0), (435, 140, 0), (435, 320, 0),
    ]
    for x, y, z in points:
        m.spawn(x, y, z)
    m.loot((110, 120, 60, 80), 0, MEDICAL + AMMO_LIGHT)
    m.loot((350, 360, 190, 210), 0, TOOLS + AMMO_HEAVY)
    m.loot((190, 200, 300, 330), 0, CASH + MEDICAL)
    m.bunker(115, 115, 0, "Meridian and Fourth")
    m.bunker(275, 275, 0, "Foundry Street and Civic Parade")
    m.bunker(35, 195, 0, "Harbour Way and Market Street")
    m.bunker(355, 355, 0, "Eastgate Avenue and Northgate Road")
