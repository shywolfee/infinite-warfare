"""Freya's Ascent.

A city built up the side of a mountain called Freya's Tears, on a world that is
not ours, under a habitat that is not on the world at all.

The mountain is a stepped thing: six terraces cut one above the other, each set
back from the one below so that what is left in front of it is the lower
terrace's shelf. That is the whole geography. There is no "across town" here,
only above you and below you, and there are exactly four ways to move between
them:

  the switchback stairs   long, in the open, and they zigzag so no one flight
                          holds the whole climb
  the goods lift          five stops, fast, and the obvious place to be met
  the goods adits         the tunnels that connect the lift to each shelf; the
                          lowest one runs a hundred and forty units through the
                          rock with nothing in it
  the maintenance rungs   straight up the cliff face between shelves, slow and
                          completely exposed

Going up:

    0    The Roots            the landing field, the freight hall, the bar
   14    Lowreach             cut-rock housing and the catchment basin
   30    The Stitchworks      the ropeworks and the foundry that feed the climb
   48    Middlehold           market, hostel, infirmary: the middle of everything
   66    The Cataract Terrace where the Tears come down, and the mill they drive
   86    Highreach            administration, the observatory, thin cold air
  110    The Crown            the anchor the tether is bolted to
  140    Folkvangr Spindle    a ring in orbit, reached only by the tether climber

The Tears fall down the eastern face and land on each shelf in turn as you
climb, so the sound of them is always somewhere to your east and always a
little quieter than it was. They are the one thing here that tells you how high
you are without asking.
"""
from .builder import Map

W = D = 300

ROOTS, LOWREACH, STITCH, MIDDLE, CATARACT, HIGH, CROWN, SPINDLE = (
    0, 14, 30, 48, 66, 86, 110, 140)

# Each terrace is set back from the one below it. The band between a terrace's
# southern edge and the next terrace's southern edge is its usable shelf, and
# so are the strips down each side.
TERRACE = {
    LOWREACH: (30, 272, 84, 272),
    STITCH: (48, 254, 112, 268),
    MIDDLE: (66, 236, 140, 262),
    CATARACT: (84, 218, 168, 256),
    HIGH: (102, 200, 196, 250),
    CROWN: (120, 182, 224, 244),
}
NAME = {
    ROOTS: "The Roots", LOWREACH: "Lowreach", STITCH: "The Stitchworks",
    MIDDLE: "Middlehold", CATARACT: "The Cataract Terrace", HIGH: "Highreach",
    CROWN: "The Crown", SPINDLE: "Folkvangr Spindle",
}
ORDER = [LOWREACH, STITCH, MIDDLE, CATARACT, HIGH, CROWN]

MEDICAL = ["coagulant_serum_bottle", "medigel_tonic_bottle", "er_mid_med_pack",
           "loose_clotting_tablet"]
TOOLS = ["repair_kit", "cleaning_patches", "nanomatic_components", "blade_oil"]
CLIMB_KIT = ["hightech_grapple", "grapple_line_cartridge", "binoculars"]
AMMO = ["5.56mm_stanag_magazine", "9x19mm_17_round_magazine",
        "7.62x51mm_20_round_magazine"]
TRADE = ["er_small_credit_chip", "er_snickers_bar", "er_electrolyte_water"]
RARE = ["er_large_credit_chip", "er_overdrive_amplifier", "salvage_scanner"]


def build():
    m = Map("freyas_ascent", "Freya's Ascent", W, D, height=156)
    _foreland(m)
    _terraces(m)
    _stairs(m)
    _rungs(m)
    _lift(m)
    _the_tears(m)
    _roots(m)
    _lowreach(m)
    _stitchworks(m)
    _middlehold(m)
    _cataract(m)
    _highreach(m)
    _crown(m)
    _spindle(m)
    _spawns(m)
    return m.finish()


# ---------------------------------------------------------------------------
def _foreland(m):
    m.area((1, 299, 1, 299), "The Roots, moraine foreland", "loose scree",
           z=ROOTS, kind="mountain", bed="cold wind")
    m.quarters((4, 296, 4, 82), ROOTS, "The Roots", cols=3, rows=2,
               suffix="foreland")


def _terraces(m):
    """Cut the mountain. Each terrace is solid rock below and open above."""
    for z in ORDER:
        r = TERRACE[z]
        label = NAME[z]
        m.plateau(r, label, "bare rock", z, side="cliff wall", kind="mountain")
        m.zone((r[0], r[1], r[2], r[2] + 2), z, z + 7, f"{label}, the brink")
        m.zone((r[0], r[0] + 2, r[2], r[3]), z, z + 7, f"{label}, western edge")
        m.zone((r[1] - 2, r[1], r[2], r[3]), z, z + 7, f"{label}, eastern edge")
        m.zone((r[0], r[1], r[3] - 2, r[3]), z, z + 7, f"{label}, the back wall")
    # The shelf of each terrace is the strip its successor did not take, so it
    # is named after the terrace you are standing on rather than the one above.
    for i, z in enumerate(ORDER):
        r = TERRACE[z]
        above = TERRACE[ORDER[i + 1]] if i + 1 < len(ORDER) else None
        label = NAME[z]
        if above is None:
            m.quarters((r[0] + 3, r[1] - 3, r[2] + 3, r[3] - 3), z, label,
                       cols=3, rows=1)
            continue
        m.quarters((r[0], r[1], r[2], above[2] - 1), z, f"{label}, the shelf",
                   cols=4, rows=1, suffix="shelf")
        m.zone((r[0], above[0] - 1, above[2], r[3]), z, z + 7,
               f"{label}, the western walk")
        m.zone((above[1] + 1, r[1], above[2], r[3]), z, z + 7,
               f"{label}, the eastern walk")
        m.zone((r[0], r[1], above[3] + 1, r[3]), z, z + 7,
               f"{label}, behind the cliff")


def _stairs(m):
    """One flight per terrace, alternating side to side. A switchback is what a
    mountain road is, and it also means no single flight is the whole climb."""
    flights = [
        (ROOTS, LOWREACH, 150, 60, 83, "The Roots to Lowreach"),
        (LOWREACH, STITCH, 220, 88, 111, "Lowreach to the Stitchworks"),
        (STITCH, MIDDLE, 90, 116, 139, "The Stitchworks to Middlehold"),
        (MIDDLE, CATARACT, 190, 144, 167, "Middlehold to the Cataract"),
        (CATARACT, HIGH, 112, 172, 195, "The Cataract to Highreach"),
        (HIGH, CROWN, 150, 199, 223, "Highreach to the Crown"),
    ]
    for low, high, x, y1, y2, name in flights:
        m.stair((x, x + 12, y1, y2), low, high, f"{name}, switchback stair",
                axis="y", material="stone stairs", support="cliff wall",
                kind="mountain", head=8)
        m.poi(x + 2, y1 + 1, low, f"Foot of the {name} stair")
        m.poi(x + 2, y2, high, f"Head of the {name} stair")


def _rungs(m):
    """Straight up the cliff face, on the western side, one pitch per shelf.

    The column sits in the upper terrace's edge tile, so you approach it from
    the shelf below and step off it onto the shelf above."""
    for i in range(len(ORDER)):
        high = ORDER[i]
        low = ORDER[i - 1] if i else ROOTS
        x = TERRACE[high][0]
        y = 234 if high == CROWN else 230
        if not (TERRACE[high][2] <= y <= TERRACE[high][3]):
            continue
        if low != ROOTS and not (TERRACE[low][2] <= y <= TERRACE[low][3]):
            continue
        m.ladder(x, y, low, high,
                 f"Maintenance rungs, {NAME[low]} to {NAME[high]}",
                 material="maintenance rungs", face=(x - 3, x - 1, y - 1, y + 1))
        m.poi(x - 2, y, low, f"Foot of the rungs to {NAME[high]}")


# The goods lift sits inside the mountain on the western side, where every
# terrace from Lowreach up still has rock above it, and reaches each shelf
# through a tunnel. The tunnels get longer the further down you go.
SHAFT = (88, 100, 200, 212)
# level -> (west end, east end, y1, y2, where the rock starts). West of the
# rock the adit is an open cutting along the terrace's western walk; east of it
# the adit is a tunnel bored under the terrace above.
ADITS = {
    CATARACT: None,                 # the shelf is right outside the door
    MIDDLE: (66, 87, 204, 208, 84),
    STITCH: (48, 87, 204, 208, 66),
    LOWREACH: (30, 87, 204, 208, 48),
}


def _lift(m):
    stops = [(NAME[z], z) for z in (ROOTS, LOWREACH, STITCH, MIDDLE, CATARACT)]
    for z in (ROOTS, LOWREACH, STITCH, MIDDLE, CATARACT):
        m.air(SHAFT, z, z + 8)
        m.room(SHAFT, z, f"Goods lift hall, {NAME[z]}", floor="steel plate",
               height=7, wall="steel wall", kind="concourse", roof_zone=False)
        m.turbolift((SHAFT[0] + 1, SHAFT[1] - 1, SHAFT[2] + 1, SHAFT[3] - 1),
                    z, z + 6, "Freya's Tears goods lift", stops)
        m.poi(SHAFT[0] + 3, SHAFT[2] + 3, z, f"Goods lift hall, {NAME[z]}")
    m.ambience((SHAFT[0] + 1, SHAFT[1] - 1, SHAFT[2] + 1, SHAFT[3] - 1),
               ROOTS, CATARACT + 8, "machinery hum")
    m.obj("bench", SHAFT[0] + 2, SHAFT[3] - 4, MIDDLE, "Lift hall bench", 8, 3, 4)
    m.fixture("vending_machine", SHAFT[1] - 3, SHAFT[3] - 3, STITCH,
              "Lift hall provisions machine")

    # The Cataract hall opens straight onto its own shelf.
    m.door((SHAFT[0], SHAFT[0], 204, 208), CATARACT, "Goods lift door, the Cataract",
           floor="steel plate")

    for z, adit in ADITS.items():
        if adit is None:
            continue
        x1, x2, y1, y2, rock = adit
        m.air((x1, x2, y1, y2), z, z + 5)
        m.tile((x1, x2, y1, y2), z, z, "steel plate")
        # Walls only where the adit is actually inside the mountain. Walling
        # the open stretch too would make the whole corridor a dead end whose
        # one entrance is the cliff edge.
        m.tile((rock, x2, y1 - 1, y1 - 1), z, z + 4, "rock wall")
        m.tile((rock, x2, y2 + 1, y2 + 1), z, z + 4, "rock wall")
        m.zone((x1, rock - 1, y1, y2), z, z + 4, f"Goods adit cutting, {NAME[z]}")
        m.zone((rock, x2, y1, y2), z, z + 4, f"Goods adit, {NAME[z]}")
        m.space((rock, x2, y1, y2), z, z + 4, f"Goods adit, {NAME[z]}", "stone",
                "tunnel")
        m.ambience((rock, x2, y1, y2), z, z + 4, "corridor")
        m.door((x2, x2, y1 + 1, y2 - 1), z, f"Goods lift door, {NAME[z]}",
               floor="steel plate")
        m.portal((rock, rock, y1, y2), z, z + 3, f"Goods adit mouth, {NAME[z]}")
        m.poi(rock - 2, (y1 + y2) // 2, z, f"Goods adit mouth, {NAME[z]}")

    # The long one. A hundred and forty units of tunnel from the foot of the
    # mountain to the lift, with nothing in it and nowhere to turn off.
    m.air((92, 96, 60, 199), ROOTS, ROOTS + 5)
    m.tile((92, 96, 60, 199), ROOTS, ROOTS, "steel plate")
    m.tile((91, 91, 60, 199), ROOTS, ROOTS + 4, "rock wall")
    m.tile((97, 97, 60, 199), ROOTS, ROOTS + 4, "rock wall")
    for i, y in enumerate(range(60, 200, 28)):
        m.zone((92, 96, y, min(y + 27, 199)), ROOTS, ROOTS + 4,
               f"The long adit, {_furlong(i)}")
    m.space((92, 96, 60, 199), ROOTS, ROOTS + 4, "The long adit", "stone", "tunnel")
    m.ambience((92, 96, 60, 199), ROOTS, ROOTS + 4, "cave")
    m.door((92, 96, 199, 199), ROOTS, "Long adit inner door", floor="steel plate")
    m.portal((92, 96, 60, 60), ROOTS, ROOTS + 3, "Long adit mouth")
    m.poi(94, 62, ROOTS, "The long adit mouth")
    m.poi(94, 190, ROOTS, "The long adit, inner end")


def _furlong(i):
    return ["the mouth", "the first bend", "the second bend", "the halfway mark",
            "the fourth stretch", "the shoring", "the inner end"][min(i, 6)]


def _the_tears(m):
    """The fall lands on a different shelf at every level, always to the east.

    Each pool sits in the eastern walk of the terrace below the one whose face
    it is falling from, which is exactly where a waterfall coming off a step
    would land."""
    falls = [(ROOTS, 274, 280), (LOWREACH, 258, 266), (STITCH, 240, 248),
             (MIDDLE, 222, 230), (CATARACT, 204, 212), (HIGH, 186, 194)]
    for z, x1, x2 in falls:
        m.area((x1, x2, 200, 230), f"Freya's Tears, the pool at {NAME[z]}",
               "shallow water", z=z, kind="water", bed="waterfall")
        m.zone((x1 - 3, x1 - 1, 200, 230), z, z + 7,
               f"Freya's Tears, the ledge at {NAME[z]}")
        m.poi(x1 - 2, 214, z, f"Freya's Tears at {NAME[z]}")
    m.area((262, 292, 20, 60), "The Roots, tailwater pool", "standing water",
           z=ROOTS, kind="water", bed="small waterfall")
    m.poi(276, 40, ROOTS, "The tailwater pool")
    m.fixture("streams", 270, 50, ROOTS, "The tailwater inflow")


# ---------------------------------------------------------------------------
def _roots(m):
    m.area((60, 240, 28, 74), "The Roots, landing field", "plascrete", z=ROOTS,
           kind="open", bed="open air")
    for i, x in enumerate(range(70, 220, 30)):
        m.tile((x, x + 18, 34, 52), ROOTS, ROOTS, "duracrete")
        m.zone((x, x + 18, 34, 52), ROOTS, ROOTS + 7, f"Landing field, pad {i + 1}")
    m.poiregion((60, 240, 28, 74), ROOTS, ROOTS + 8, "The Roots landing field")
    m.fixture("street_light", 64, 60, ROOTS, "Landing field mast light")

    m.room((36, 100, 6, 30), ROOTS, "Freight hall", floor="poured floor",
           height=12, wall="steel wall", kind="warehouse")
    m.door((62, 72, 30, 30), ROOTS, "Freight hall doors", floor="poured floor",
           height=4)
    m.door((100, 100, 14, 20), ROOTS, "Freight hall east door", floor="poured floor")
    m.window((36, 36, 14, 20), ROOTS + 4, "Freight hall west light")
    m.ambience((37, 99, 7, 29), ROOTS, ROOTS + 11, "warehouse")
    m.subzone((37, 66, 7, 29), ROOTS, "Freight hall, inbound bay")
    m.subzone((72, 99, 7, 29), ROOTS, "Freight hall, outbound bay")
    m.obj("crate", 42, 10, ROOTS, "Palletised climb rations", 8, 8, 4)
    m.obj("crate", 42, 20, ROOTS, "Sealed ore drum", 8, 8, 4)
    m.obj("workbench", 76, 10, ROOTS, "Manifest bench", 14, 4, 2)
    m.obj("locker", 90, 22, ROOTS, "Freight crew lockers", 4, 6, 5)
    m.fixture("crate", 70, 24, ROOTS, "Freight supply crate")
    m.fixture("computer1", 84, 24, ROOTS, "Manifest terminal")
    m.poi(40, 12, ROOTS, "Freight hall inbound bay")
    m.loot((40, 96, 9, 27), ROOTS, TOOLS + TRADE, most=4)

    # The bar at the bottom of the mountain, which is where everybody who is
    # not climbing today is.
    m.room((160, 214, 6, 30), ROOTS, "The Last Warm Room", floor="floorboards",
           height=6, wall="timber wall", kind="shop")
    m.door((182, 190, 30, 30), ROOTS, "Bar door", floor="floorboards")
    m.window((160, 160, 14, 20), ROOTS + 2, "Bar window")
    m.ambience((161, 213, 7, 29), ROOTS, ROOTS + 5, "bar")
    m.subzone((161, 213, 7, 14), ROOTS, "The Last Warm Room, the counter")
    m.obj("counter", 164, 9, ROOTS, "The bar", 30, 3, 2)
    m.obj("table", 166, 20, ROOTS, "Bar table", 8, 5, 2)
    m.obj("table", 184, 20, ROOTS, "Bar table, window side", 8, 5, 2)
    m.fixture("coke_machine", 208, 20, ROOTS, "Bar cooler")
    m.fixture("tv", 208, 10, ROOTS, "Bar screen")
    m.poi(166, 22, ROOTS, "The Last Warm Room")
    m.loot((164, 210, 9, 27), ROOTS, TRADE + MEDICAL)
    m.fixture("atm", 246, 40, ROOTS, "Landing field credit post")
    m.bunker(150, 50, ROOTS, "The Roots landing field")


def _lowreach(m):
    z = LOWREACH
    m.path("Lowreach, the cut", (34, 268, 104, 110), "flagstones", z=z)
    # Housing cut straight into the rock: a row of rooms off one passage.
    for i, x in enumerate(range(50, 230, 34)):
        m.room((x, x + 26, 84, 102), z, f"Lowreach, number {i + 1} cut",
               floor="screed", height=5, wall="rock wall", kind="cabin")
        m.door((x + 11, x + 15, 102, 102), z, f"Number {i + 1} cut door",
               floor="screed")
        m.ambience((x + 1, x + 25, 85, 101), z, z + 4, "flat")
        m.obj("bed", x + 3, 88, z, f"Number {i + 1} bunk", 5, 9, 4)
        m.obj("cabinet", x + 18, 88, z, f"Number {i + 1} press", 5, 3, 4)
        m.loot((x + 3, x + 23, 86, 100), z, TRADE + MEDICAL, most=2)
    m.poi(54, 88, z, "Lowreach, number one cut")

    # Catchment basin and intake house, on the eastern walk.
    m.area((256, 271, 120, 196), "Lowreach, catchment basin", "standing water",
           z=z, kind="water", bed="fountain")
    m.zone((255, 255, 120, 196), z, z + 7, "Lowreach, catchment bund")
    m.room((255, 271, 236, 266), z, "Lowreach intake house", floor="steel plate",
           height=8, wall="stone wall", kind="plant")
    m.door((260, 266, 236, 236), z, "Intake house door", floor="steel plate")
    m.window((271, 271, 256, 262), z + 2, "Intake house east window")
    m.ambience((256, 270, 237, 265), z, z + 7, "machinery hum")
    m.obj("generator", 258, 240, z, "Number One intake pump", 6, 6, 5)
    m.obj("generator", 258, 252, z, "Number Two intake pump", 6, 6, 5)
    m.fixture("computer2", 268, 244, z, "Intake terminal")
    m.poi(259, 262, z, "Lowreach intake house")
    m.loot((266, 269, 238, 264), z, TOOLS, most=2)
    m.fixture("atm", 120, 107, z, "Lowreach credit post")
    m.bunker(150, 107, z, "Lowreach, the cut")


def _stitchworks(m):
    z = STITCH
    m.path("The Stitchworks, the gallery", (52, 250, 132, 138), "steel plate", z=z)
    m.room((56, 140, 112, 130), z, "The ropeworks, spinning floor",
           floor="poured floor", height=12, wall="steel wall", kind="hangar")
    m.door((94, 104, 130, 130), z, "Ropeworks doors", floor="poured floor", height=4)
    m.door((56, 56, 118, 124), z, "Ropeworks west door", floor="poured floor")
    m.window((140, 140, 118, 124), z + 4, "Ropeworks east light")
    m.ambience((57, 139, 113, 129), z, z + 11, "warehouse")
    m.subzone((57, 98, 113, 129), z, "Spinning floor, west walk")
    m.subzone((102, 139, 113, 129), z, "Spinning floor, east walk")
    m.obj("workbench", 62, 116, z, "Spinning bench", 24, 4, 2)
    m.obj("workbench", 62, 124, z, "Splicing bench", 24, 4, 2)
    m.obj("generator", 108, 116, z, "Rope drive", 10, 10, 5)
    m.obj("crate", 124, 122, z, "Coiled tether line", 8, 6, 4)
    m.fixture("table", 100, 126, z, "Ropeworks service bench")
    m.poi(60, 120, z, "The ropeworks spinning floor")
    m.loot((60, 136, 115, 127), z, TOOLS + CLIMB_KIT, most=4)
    # A catwalk over the spinning floor, up the rungs at its western end.
    m.tile((60, 136, 120, 122), z + 8, z + 8, "catwalk grating")
    m.zone((60, 136, 120, 122), z + 8, z + 12, "Ropeworks, spinning-floor catwalk")
    m.ladder(60, 121, z, z + 8, "Ropeworks catwalk rungs",
             material="maintenance rungs", face=(61, 63, 120, 122))
    m.poi(66, 121, z + 8, "Ropeworks catwalk")

    m.room((160, 248, 112, 130), z, "The Stitchworks foundry", floor="poured floor",
           height=14, wall="brick wall", kind="hangar")
    m.door((196, 206, 130, 130), z, "Foundry doors", floor="poured floor", height=4)
    m.window((248, 248, 118, 124), z + 5, "Foundry east light")
    m.ambience((161, 247, 113, 129), z, z + 13, "warehouse")
    m.subzone((161, 202, 113, 129), z, "Foundry, the furnace bank")
    m.subzone((208, 247, 113, 129), z, "Foundry, the pouring floor")
    m.obj("generator", 166, 116, z, "Number One furnace", 10, 10, 6)
    m.obj("generator", 182, 116, z, "Number Two furnace", 10, 10, 6)
    m.obj("tank", 214, 116, z, "Quench tank", 8, 8, 4)
    m.obj("workbench", 228, 124, z, "Fettling bench", 14, 4, 2)
    m.fixture("scrap_yard1", 240, 126, z, "Foundry slag heap")
    m.poi(164, 126, z, "The Stitchworks foundry")
    m.loot((164, 244, 115, 127), z, TOOLS + AMMO, most=3)
    m.bunker(150, 136, z, "The Stitchworks gallery")


def _middlehold(m):
    z = MIDDLE
    m.area((128, 212, 142, 166), "Middlehold market square", "granite setts", z=z,
           kind="square", bed="busy street")
    m.poiregion((128, 212, 142, 166), z, z + 8, "Middlehold market square")
    for i, x in enumerate(range(134, 208, 18)):
        m.obj("counter", x, 146, z, f"Market stall {i + 1}", 12, 3, 2)
    m.fixture("vending_machine", 132, 162, z, "Market provisions machine")
    m.fixture("atm", 208, 162, z, "Middlehold credit post")
    m.fixture("post_box", 208, 144, z, "Middlehold post")

    m.room((70, 122, 142, 166), z, "Middlehold hostel, common room",
           floor="floorboards", height=6, wall="stone wall", kind="hall")
    m.door((92, 100, 166, 166), z, "Hostel front door", floor="floorboards")
    m.window((70, 70, 150, 158), z + 2, "Common room window")
    m.ambience((71, 121, 143, 165), z, z + 5, "house")
    m.subzone((71, 96, 143, 165), z, "Hostel, the fire end")
    m.obj("table", 76, 146, z, "Hostel long table", 16, 5, 2)
    m.obj("sofa", 76, 158, z, "Common room couch", 10, 4, 4)
    m.obj("bed", 104, 146, z, "Hostel bunk", 5, 9, 4)
    m.obj("bed", 114, 146, z, "Hostel bunk, second", 5, 9, 4)
    m.fixture("fridge", 116, 160, z, "Hostel cold press")
    m.poi(74, 150, z, "Middlehold hostel common room")
    m.loot((74, 118, 145, 163), z, TRADE + MEDICAL + CLIMB_KIT, most=4)

    m.room((219, 235, 232, 260), z, "Middlehold infirmary", floor="linoleum",
           height=7, wall="stone wall", kind="ward")
    m.door((224, 230, 232, 232), z, "Infirmary door", floor="linoleum")
    m.window((235, 235, 242, 248), z + 2, "Infirmary east window")
    m.ambience((220, 234, 233, 259), z, z + 6, "hospital")
    m.subzone((220, 234, 233, 246), z, "Infirmary, the cots")
    m.obj("bed", 222, 234, z, "Infirmary cot", 5, 9, 4)
    m.obj("bed", 230, 234, z, "Infirmary cot, second", 5, 9, 4)
    m.obj("cabinet", 230, 256, z, "Drug press", 4, 3, 4)
    m.fixture("hospital_bed", 226, 250, z, "Infirmary treatment bed")
    m.fixture("hospital_coagulator", 232, 250, z, "Infirmary coagulator")
    m.fixture("instrument_prep", 222, 250, z, "Instrument bench")
    m.poi(224, 246, z, "Middlehold infirmary")
    m.loot((221, 233, 235, 257), z, MEDICAL, most=4)
    m.bunker(170, 155, z, "Middlehold market square")


def _cataract(m):
    z = CATARACT
    m.area((100, 190, 184, 194), "The Cataract Terrace, the spray walk",
           "wet cobbles", z=z, kind="open", bed="waterfall")
    m.poiregion((100, 190, 184, 194), z, z + 8, "The Cataract spray walk")
    m.room((110, 176, 168, 182), z, "The Cataract mill, wheel hall",
           floor="wet concrete", height=12, wall="stone wall", kind="plant")
    m.door((136, 146, 182, 182), z, "Mill doors", floor="wet concrete", height=4)
    m.door((176, 176, 172, 178), z, "Mill east door", floor="wet concrete")
    m.window((110, 110, 172, 178), z + 4, "Mill west light")
    m.ambience((111, 175, 169, 181), z, z + 11, "fountain")
    m.subzone((111, 142, 169, 181), z, "Wheel hall, the race")
    m.subzone((146, 175, 169, 181), z, "Wheel hall, the gearing")
    m.obj("generator", 114, 170, z, "The wheel", 12, 10, 8)
    m.obj("generator", 150, 170, z, "Mill gearing", 10, 10, 6)
    m.obj("workbench", 164, 176, z, "Millwright bench", 10, 4, 2)
    m.fixture("table", 132, 178, z, "Mill service bench")
    m.fixture("streams", 128, 170, z, "Mill tailrace")
    m.poi(116, 178, z, "The Cataract mill wheel hall")
    m.loot((114, 172, 171, 179), z, TOOLS + RARE, most=3)

    # The gantry out over the eastern drop: the most exposed place on the map
    # and the only one you can hear the whole climb from.
    m.deck((196, 216, 178, 186), z + 6, "The Cataract gantry",
           material="catwalk grating", bed="waterfall")
    m.air((195, 195, 181, 183), z, z + 10)
    m.ladder(195, 182, z, z + 6, "Cataract gantry rungs",
             material="maintenance rungs", face=(192, 194, 181, 183))
    m.poi(206, 182, z + 6, "The Cataract gantry")
    m.bunker(150, 190, z, "The Cataract spray walk")


def _highreach(m):
    z = HIGH
    m.area((106, 196, 212, 222), "Highreach, the approach", "flagstones", z=z,
           kind="square", bed="high wind")
    m.room((106, 150, 196, 210), z, "Highreach administration",
           floor="office carpet", height=7, wall="stone wall", kind="office")
    m.door((124, 130, 210, 210), z, "Administration door", floor="office carpet")
    m.window((106, 106, 200, 206), z + 2, "Administration window")
    m.ambience((107, 149, 197, 209), z, z + 6, "office")
    m.obj("table", 110, 200, z, "Registrar's desk", 12, 5, 2)
    m.obj("bookcase", 140, 200, z, "Climb records", 3, 8, 5)
    m.fixture("computer1", 118, 206, z, "Administration terminal")
    m.fixture("atrium_speaker", 146, 206, z, "Highreach address speaker")
    m.poi(112, 206, z, "Highreach administration")
    m.loot((110, 146, 199, 207), z, TRADE + RARE, most=3)

    m.room((160, 198, 196, 210), z, "Highreach observatory", floor="steel plate",
           height=10, wall="steel wall", kind="hall")
    m.door((174, 180, 210, 210), z, "Observatory door", floor="steel plate")
    m.window((198, 198, 200, 206), z + 4, "Observatory east light")
    m.ambience((161, 197, 197, 209), z, z + 9, "still air")
    m.obj("table", 164, 200, z, "Plate table", 10, 5, 2)
    m.obj("screen", 190, 200, z, "Tracking board", 3, 8, 4)
    m.obj("workbench", 164, 206, z, "Optical bench", 12, 3, 2)
    m.fixture("computer2", 192, 206, z, "Observatory terminal")
    m.poi(166, 198, z, "Highreach observatory")
    m.loot((163, 195, 198, 208), z, RARE + TOOLS, seconds=90, most=2)
    m.bunker(150, 218, z, "Highreach approach")


def _crown(m):
    z = CROWN
    m.area((122, 180, 226, 242), "The Crown, the anchor floor", "diamond plate",
           z=z, kind="platform", bed="gale")
    m.poiregion((122, 180, 226, 242), z, z + 8, "The Crown anchor floor")
    m.obj("tank", 126, 228, z, "The tether anchor", 14, 12, 10)
    m.obj("generator", 126, 236, z, "Anchor tensioner", 8, 5, 5)
    m.fixture("computer2", 144, 240, z, "Tether control terminal")
    m.fixture("security_radio1", 144, 228, z, "Crown radio")
    m.loot((124, 178, 228, 240), z, RARE + AMMO, seconds=120, most=3)

    # The tether climber. There is no walking route to the Spindle, which is
    # the point of it being in orbit.
    shaft = (166, 178, 228, 240)
    m.air(shaft, z, SPINDLE + 8)
    m.room(shaft, z, "Tether climber, Crown station", floor="hull plating",
           height=7, wall="hull wall", kind="concourse", roof_zone=False)
    m.door((shaft[0], shaft[0], 232, 236), z, "Climber door, the Crown",
           floor="hull plating")
    stops = [("the Crown", CROWN), ("Folkvangr Spindle", SPINDLE)]
    m.turbolift((shaft[0] + 1, shaft[1] - 1, shaft[2] + 1, shaft[3] - 1),
                z, z + 6, "Tether climber", stops)
    m.ambience((shaft[0] + 1, shaft[1] - 1, shaft[2] + 1, shaft[3] - 1),
               z, SPINDLE + 8, "machinery hum")
    m.poi(shaft[0] + 3, 231, z, "Tether climber, Crown station")


CX, CY = 172, 234
INNER, OUTER = 24, 34


def _spindle(m):
    """Folkvangr Spindle: a ring habitat directly above the Crown.

    Eight runs of corridor joined end to end, four spokes to a hub, four
    compartments off the ring, and nothing outside it. It is an octagon because
    the map format is rectangles and an octagon is what rectangles make when
    you want a ring. Walking the whole way round takes about as long as
    climbing two terraces, which is the point."""
    z = SPINDLE
    cx, cy = CX, CY
    runs = [
        ("the southern arc", (cx - INNER, cx + INNER, cy - OUTER, cy - INNER)),
        ("the northern arc", (cx - INNER, cx + INNER, cy + INNER, cy + OUTER)),
        ("the western arc", (cx - OUTER, cx - INNER, cy - INNER, cy + INNER)),
        ("the eastern arc", (cx + INNER, cx + OUTER, cy - INNER, cy + INNER)),
        ("the south-west bend", (cx - OUTER, cx - INNER, cy - OUTER, cy - INNER)),
        ("the south-east bend", (cx + INNER, cx + OUTER, cy - OUTER, cy - INNER)),
        ("the north-west bend", (cx - OUTER, cx - INNER, cy + INNER, cy + OUTER)),
        ("the north-east bend", (cx + INNER, cx + OUTER, cy + INNER, cy + OUTER)),
    ]
    for name, r in runs:
        m.tile(r, z, z, "hull plating")
        m.air(r, z + 1, z + 6)
        m.zone(r, z, z + 6, f"Folkvangr Spindle, {name}")
        m.space(r, z, z + 6, f"Folkvangr Spindle, {name}", "metal", "corridor")
    # Rails on both sides, which is what makes it a ring rather than a floor
    # with a hole in it.
    m.tile((cx - OUTER - 1, cx + OUTER + 1, cy - OUTER - 1, cy - OUTER - 1), z, z + 4, "hull wall")
    m.tile((cx - OUTER - 1, cx + OUTER + 1, cy + OUTER + 1, cy + OUTER + 1), z, z + 4, "hull wall")
    m.tile((cx - OUTER - 1, cx - OUTER - 1, cy - OUTER, cy + OUTER), z, z + 4, "hull wall")
    m.tile((cx + OUTER + 1, cx + OUTER + 1, cy - OUTER, cy + OUTER), z, z + 4, "hull wall")

    spokes = [
        ("south spoke", (cx - 3, cx + 3, cy - INNER, cy - 11)),
        ("north spoke", (cx - 3, cx + 3, cy + 11, cy + INNER)),
        ("west spoke", (cx - INNER, cx - 11, cy - 3, cy + 3)),
        ("east spoke", (cx + 11, cx + INNER, cy - 3, cy + 3)),
    ]
    for name, r in spokes:
        m.tile(r, z, z, "steel grating")
        m.air(r, z + 1, z + 5)
        m.zone(r, z, z + 5, f"Folkvangr Spindle, {name}")
        m.space(r, z, z + 5, f"Folkvangr Spindle, {name}", "metal", "corridor")

    m.room((cx - 12, cx + 12, cy - 12, cy + 12), z, "Folkvangr Spindle, the hub",
           floor="hull plating", height=9, wall="hull wall", kind="atrium",
           roof_zone=False)
    m.door((cx - 2, cx + 2, cy - 12, cy - 12), z, "Hub south door", floor="hull plating")
    m.door((cx - 2, cx + 2, cy + 12, cy + 12), z, "Hub north door", floor="hull plating")
    m.door((cx - 12, cx - 12, cy - 2, cy + 2), z, "Hub west door", floor="hull plating")
    m.door((cx + 12, cx + 12, cy - 2, cy + 2), z, "Hub east door", floor="hull plating")
    m.ambience((cx - 11, cx + 11, cy - 11, cy + 11), z, z + 8, "station")
    m.obj("bench", cx - 9, cy - 9, z, "Hub bench", 8, 3, 4)
    m.obj("screen", cx + 6, cy - 9, z, "Hub arrivals board", 3, 6, 4)
    m.fixture("atrium_speaker", cx, cy + 8, z, "Hub announcer")
    m.fixture("kiosk", cx - 8, cy + 8, z, "Hub supply terminal")
    m.poi(cx - 8, cy - 4, z, "Folkvangr Spindle hub")
    m.loot((cx - 10, cx + 10, cy - 10, cy + 10), z, RARE + MEDICAL, seconds=90, most=3)

    # The Crown station arrives on the ring's eastern arc.
    m.door((cx + INNER + 4, cx + INNER + 4, cy - 2, cy + 2), z,
           "Climber door, the Spindle", floor="hull plating")

    compartments = [
        ("Spindle wardroom", (cx - 22, cx - 4, cy - OUTER + 1, cy - INNER - 1),
         "matting", "room", "indoors"),
        ("Spindle hydroponics", (cx + 4, cx + 22, cy - OUTER + 1, cy - INNER - 1),
         "matting", "room", "indoors"),
        ("Spindle sick bay", (cx - 22, cx - 4, cy + INNER + 1, cy + OUTER - 1),
         "linoleum", "ward", "hospital"),
        ("Spindle machine deck", (cx + 4, cx + 22, cy + INNER + 1, cy + OUTER - 1),
         "steel grating", "plant", "machinery hum"),
    ]
    for name, r, floor, kind, bed in compartments:
        m.room(r, z, name, floor=floor, height=7, wall="hull wall", kind=kind,
               roof_zone=False)
        mid = (r[0] + r[1]) // 2
        south = r[2] < cy
        edge = r[3] if south else r[2]
        m.door((mid - 2, mid + 2, edge, edge), z, f"{name} door", floor=floor)
        m.ambience((r[0] + 1, r[1] - 1, r[2] + 1, r[3] - 1), z, z + 6, bed)
        m.poi(r[0] + 3, (r[2] + r[3]) // 2, z, name)
        m.loot((r[0] + 2, r[1] - 2, r[2] + 2, r[3] - 2), z, RARE + TOOLS, most=2)
    m.obj("table", cx - 20, cy - OUTER + 4, z, "Wardroom table", 12, 4, 2)
    m.obj("planter", cx + 6, cy - OUTER + 4, z, "Hydroponics tray", 8, 4, 2)
    m.obj("bed", cx - 20, cy + INNER + 3, z, "Sick bay cot", 5, 6, 4)
    m.obj("generator", cx + 6, cy + INNER + 3, z, "Reactor coupling", 6, 5, 5)
    m.fixture("hospital_ventilator", cx - 8, cy + INNER + 5, z, "Sick bay ventilator")
    m.fixture("computer1", cx + 18, cy + INNER + 5, z, "Machine deck terminal")
    m.poiregion((cx - OUTER, cx + OUTER, cy - OUTER, cy + OUTER), z, z + 8,
                "Folkvangr Spindle")
    m.ambience((cx - OUTER, cx + OUTER, cy - OUTER, cy + OUTER), z, z + 8, "still air")


def _spawns(m):
    points = [
        (30, 20, ROOTS), (150, 20, ROOTS), (260, 20, ROOTS), (20, 150, ROOTS),
        (280, 150, ROOTS), (20, 280, ROOTS),
        (40, 96, LOWREACH), (250, 96, LOWREACH),
        (56, 136, STITCH), (244, 136, STITCH),
        (72, 160, MIDDLE), (230, 160, MIDDLE),
        (92, 190, CATARACT), (210, 190, CATARACT),
        (110, 218, HIGH), (192, 218, HIGH),
        (150, 232, CROWN),
    ]
    for x, y, z in points:
        m.spawn(x, y, z)
