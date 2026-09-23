"""Coruscant.

A slice of the Galactic City, taken through the Senate District and cut all the
way down to the undercity, because the only honest way to build Coruscant is
vertically. The whole planet is one city and its geography is levels: what
matters about a place here is how far above the original surface it is, and
whether anyone up top has thought about it in the last thousand years.

Six levels, top to bottom, with the canon in the right relationship:

  1313   the undercity. No daylight has reached it in millennia. The Crimson
         Corridor runs through it and nothing that lives down here came from
         above by choice.
  1315   the Works. The industrial district that built the upper levels and was
         abandoned when they were finished. Vent shafts, dead foundries, and
         the only unsealed route between the undercity and the upper levels.
  2500   CoCo Town, the Collective Commerce District. Dex's Diner is here, and
         so is everyone who actually makes anything.
  3204   the Uscru Entertainment District. The Outlander Club and the Galaxies
         Opera House, one street apart and facing away from each other.
  5127   the Senate District proper: the Senate Rotunda under its dome, the
         Republic Executive Building, and Monument Plaza with Umate standing in
         the middle of it -- the peak of the only mountain on Coruscant still
         sticking out of the city, and the one piece of the original planet you
         can put your hand on.
  5127   the Jedi Temple precinct, on its own ziggurat across the skylane, with
         the Room of a Thousand Fountains inside it and five spires above.

  skylane  the traffic lanes, above everything, crossed on maintenance gantries

Getting between levels is turbolifts, the same as it is in the fiction, plus
the vent shafts in the Works for anyone who does not want to be seen using one.
"""
from .builder import Map

W = D = 400

UNDER, WORKS, COCO, USCRU, SENATE, SKYLANE = 0, 26, 54, 84, 116, 146

LEVEL = {
    UNDER: "Level 1313", WORKS: "The Works", COCO: "CoCo Town",
    USCRU: "The Uscru District", SENATE: "The Senate District",
    SKYLANE: "the skylanes",
}

STREET = ["er_small_credit_chip", "er_hot_fries", "loose_pain_blocker_capsule"]
MEDICAL = ["coagulant_serum_bottle", "trauma_repair_serum_bottle",
           "er_mid_med_pack"]
TECH = ["nanomatic_components", "salvage_scanner", "neural_intrusion_device",
        "wiring_harness_kit"]
TOOLS = ["repair_kit", "cleaning_patches", "gunsmith_multitool"]
AMMO = ["5.7x28mm_50_round_magazine", "9x19mm_17_round_magazine",
        "4.6x30mm_40_round_magazine"]
RARE = ["er_large_credit_chip", "er_overdrive_amplifier", "hightech_grapple",
        "reconnaissance_ring"]

# Every level is a solid slab with the level above resting on it, so the map
# is genuinely stacked rather than six fields side by side.
SLAB = {WORKS: UNDER, COCO: WORKS, USCRU: COCO, SENATE: USCRU}


def build():
    m = Map("habitat_alpha", "Coruscant", W, D, height=200)
    _levels(m)
    _fabric(m)
    _undercity(m)
    _works(m)
    _coco(m)
    _uscru(m)
    _senate(m)
    _temple(m)
    _skylanes(m)
    # Last, so that no street, path or plaza laid by a district can be written
    # over a lift hall or take the rungs out of a vent shaft.
    _turbolifts(m)
    _vent_shafts(m)
    _spawns(m)
    return m.finish()


# ---------------------------------------------------------------------------
def _levels(m):
    """Six stacked slabs. Each is a floor with the next one's underside as its
    ceiling, which is exactly what living on Coruscant is like."""
    m.area((1, 399, 1, 399), "Level 1313", "wet concrete", z=UNDER,
           kind="street", bed="dead zone")
    m.quarters((4, 396, 4, 396), UNDER, "Level 1313", cols=6, rows=6,
               suffix="sector")
    for z, below in SLAB.items():
        # The slab: solid from just above the level below up to this level.
        m.tile((1, 399, 1, 399), below + 9, z - 1, "duracrete wall")
        m.area((1, 399, 1, 399), LEVEL[z], "duracrete", z=z, kind="street")
        m.quarters((4, 396, 4, 396), z, LEVEL[z], cols=6, rows=6,
                   suffix="sector")
    m.ambience((1, 399, 1, 399), WORKS, WORKS + 8, "warehouse")
    m.ambience((1, 399, 1, 399), COCO, COCO + 8, "busy street")
    m.ambience((1, 399, 1, 399), USCRU, USCRU + 8, "city night")
    m.ambience((1, 399, 1, 399), SENATE, SENATE + 8, "city day")



# Everything each level has already committed to. The fabric goes everywhere
# else, because a level of Coruscant that is four hundred units of empty plaza
# is not Coruscant, it is a car park.
RESERVED = {
    UNDER: [(1, 399, 182, 216), (102, 138, 12, 388), (262, 298, 12, 388),
            (132, 208, 212, 268), (292, 364, 92, 148), (32, 108, 272, 338)],
    WORKS: [(1, 399, 142, 178), (22, 128, 212, 328), (142, 268, 192, 288),
            (282, 378, 222, 308)],
    COCO: [(1, 399, 172, 218), (92, 138, 1, 399), (132, 204, 204, 252),
           (212, 308, 212, 278), (32, 104, 232, 298)],
    USCRU: [(1, 399, 172, 218), (132, 278, 112, 184), (262, 388, 212, 338)],
    SENATE: [(62, 198, 62, 198), (222, 328, 52, 148), (152, 268, 242, 358),
             (272, 399, 222, 388), (1, 399, 1, 40), (40, 58, 30, 70),
             (344, 358, 40, 62), (110, 130, 330, 350), (186, 206, 194, 214),
             (50, 70, 74, 94)],
}
FABRIC = {
    WORKS: ("stack", "steel wall", "steel deck", (8, 14)),
    COCO: ("block", "duracrete wall", "duracrete", (10, 20)),
    USCRU: ("tower", "composite wall", "duracrete", (14, 26)),
    SENATE: ("tower", "glass curtain wall", "polished marble", (20, 34)),
}
FABRIC_NAMES = {
    WORKS: ["Reclamation stack", "Conveyor stack", "Slag stack", "Dead stack",
            "Blower stack", "Sealed stack"],
    COCO: ["Commerce block", "Guild block", "Freight block", "Artisan block",
           "Shipwright block", "Foundry block"],
    USCRU: ["Neon tower", "Skysign tower", "Holo tower", "Cantina tower",
            "Gambling tower", "Revel tower"],
    SENATE: ["Legation tower", "Ministry tower", "Chancery tower",
             "Consular tower", "Registry tower", "Protocol tower"],
}


def _clear(r, reserved):
    x1, x2, y1, y2 = r
    for ax1, ax2, ay1, ay2 in reserved:
        if x1 <= ax2 and x2 >= ax1 and y1 <= ay2 and y2 >= ay1:
            return False
    return True


def _fabric(m):
    """Lay a street grid and a block of building on every level, everywhere the
    authored districts have not already claimed."""
    for z, (kind, wall, roof, (low, high)) in FABRIC.items():
        reserved = RESERVED[z]
        avenue = "Skyway" if z == SENATE else ("Underway" if z == WORKS else "Row")
        for i, x in enumerate((60, 180, 300)):
            m.street(f"{_nth(i + 1).capitalize()} {avenue}", (x, x + 22, 1, 399),
                     axis="y", z=z, surface="duracrete", pavement="plascrete",
                     pavement_width=4,
                     segments=[(1, 140, "the southern reach"),
                               (141, 260, "the middle reach"),
                               (261, 399, "the northern reach")])
        count = 0
        for gx in range(6, 400, 60):
            for gy in range(6, 400, 60):
                r = (gx, gx + 44, gy, gy + 44)
                if r[1] > 398 or r[3] > 398:
                    continue
                if not _clear((r[0] - 3, r[1] + 3, r[2] - 3, r[3] + 3), reserved):
                    continue
                if any(x <= r[1] and x + 22 >= r[0] for x in (60, 180, 300)):
                    continue
                storeys = low + ((gx // 60 + gy // 60) % (high - low + 1))
                name = FABRIC_NAMES[z][count % len(FABRIC_NAMES[z])]
                count += 1
                m.block(r, z, storeys, f"{name} {count}", wall=wall, roof=roof)
                m.zone((r[0] - 3, r[1] + 3, r[2] - 3, r[2] - 1), z, z + 7,
                       f"{name} {count}, southern frontage")
                m.zone((r[0] - 3, r[1] + 3, r[3] + 1, r[3] + 3), z, z + 7,
                       f"{name} {count}, northern frontage")
                m.zone((r[0] - 3, r[0] - 1, r[2], r[3]), z, z + 7,
                       f"{name} {count}, western frontage")
                m.zone((r[1] + 1, r[1] + 3, r[2], r[3]), z, z + 7,
                       f"{name} {count}, eastern frontage")


# The three public turbolift shafts. They are in the same place on every level,
# which is how a building works and also how a player learns a map.
SHAFTS = [
    ("Western turbolift", (40, 54, 40, 54)),
    ("Central turbolift", (192, 206, 192, 206)),
    ("Eastern turbolift", (344, 358, 44, 58)),
]
STOPS = [(LEVEL[z], z) for z in (UNDER, WORKS, COCO, USCRU, SENATE)]


def _turbolifts(m):
    for name, r in SHAFTS:
        for z in (UNDER, WORKS, COCO, USCRU, SENATE):
            m.air(r, z, z + 8)
            m.room(r, z, f"{name}, {LEVEL[z]}", floor="steel plate", height=7,
                   wall="steel wall", kind="concourse", roof_zone=False)
            m.door((r[1], r[1], r[2] + 5, r[3] - 5), z, f"{name} door, {LEVEL[z]}",
                   floor="steel plate")
            m.turbolift((r[0] + 1, r[1] - 1, r[2] + 1, r[3] - 1), z, z + 6,
                        name, STOPS)
            m.poi(r[0] + 3, r[2] + 3, z, f"{name}, {LEVEL[z]}")
        m.ambience((r[0] + 1, r[1] - 1, r[2] + 1, r[3] - 1), UNDER, SENATE + 8,
                   "machinery hum")


def _vent_shafts(m):
    """The other way up. Two shafts of maintenance rungs run the full height of
    the Works and one continues to CoCo Town. Nobody maintains them, they are
    the reason the undercity is not sealed, and every meaningful thing that
    happens on this map happens because they exist."""
    for x, y, top, name in ((120, 300, COCO, "the Ledgerway shaft"),
                            (280, 100, WORKS, "the Blackpipe shaft")):
        m.air((x - 2, x + 2, y - 2, y + 2), UNDER, top + 8)
        for z in (UNDER, WORKS, COCO):
            if z > top:
                continue
            m.tile((x - 2, x + 2, y - 2, y + 2), z, z, "steel grating")
            m.zone((x - 2, x + 2, y - 2, y + 2), z, z + 6,
                   f"Head of {name}, {LEVEL[z]}")
            m.portal((x - 2, x + 2, y - 2, y + 2), z, z + 3,
                     f"{name}, {LEVEL[z]}")
        m.ladder(x, y, UNDER, top, f"Maintenance rungs, {name}",
                 material="maintenance rungs", face=(x + 1, x + 3, y - 1, y + 1))
        m.space((x - 2, x + 2, y - 2, y + 2), UNDER, top + 6, name, "metal",
                "tunnel")
        m.ambience((x - 2, x + 2, y - 2, y + 2), UNDER, top + 6, "corridor")
        m.poi(x + 2, y, UNDER, f"Foot of {name}")
        m.poi(x + 2, y, top, f"Head of {name}")


# ---------------------------------------------------------------------------
def _undercity(m):
    z = UNDER
    m.path("The Crimson Corridor", (1, 399, 190, 208), "wet concrete", z=z,
           kind="alley", bed="dead zone")
    for i, x in enumerate(range(20, 380, 60)):
        m.zone((x, x + 59, 190, 208), z, z + 7,
               f"The Crimson Corridor, the {_nth(i + 1)} stretch")
    m.path("Ledgerway", (110, 130, 20, 380), "cracked asphalt", z=z, kind="alley")
    m.path("Blackpipe Row", (270, 290, 20, 380), "cracked asphalt", z=z,
           kind="alley")
    m.poiregion((1, 399, 190, 208), z, z + 8, "The Crimson Corridor")

    m.room((140, 200, 220, 260), z, "The sump market", floor="wet concrete",
           height=8, wall="duracrete wall", kind="hall")
    m.door((164, 174, 220, 220), z, "Sump market doorway", floor="wet concrete",
           height=4)
    m.door((140, 140, 236, 244), z, "Sump market west doorway", floor="wet concrete")
    m.ambience((141, 199, 221, 259), z, z + 7, "shop")
    m.subzone((141, 170, 221, 259), z, "Sump market, the west aisle")
    m.subzone((174, 199, 221, 259), z, "Sump market, the east aisle")
    for i, y in enumerate(range(226, 254, 12)):
        m.obj("counter", 146, y, z, f"Sump stall {i + 1}", 16, 3, 2)
        m.obj("counter", 180, y, z, f"Sump stall {i + 4}", 14, 3, 2)
    m.fixture("kiosk", 196, 224, z, "Sump market supply terminal")
    m.fixture("coke_machine", 144, 256, z, "Sump market dispenser")
    m.poi(144, 224, z, "The sump market")
    m.loot((144, 196, 224, 256), z, STREET + TECH, most=4)

    m.room((300, 356, 100, 140), z, "The Blackpipe clinic", floor="linoleum",
           height=7, wall="duracrete wall", kind="ward")
    m.door((300, 300, 114, 122), z, "Blackpipe clinic door", floor="linoleum")
    m.ambience((301, 355, 101, 139), z, z + 6, "hospital")
    m.subzone((301, 328, 101, 139), z, "Blackpipe clinic, the cots")
    m.obj("bed", 304, 104, z, "Clinic cot", 5, 9, 4)
    m.obj("bed", 314, 104, z, "Clinic cot, second", 5, 9, 4)
    m.obj("cabinet", 340, 104, z, "Clinic press", 5, 3, 4)
    m.fixture("hospital_bed", 336, 130, z, "Blackpipe treatment bed")
    m.fixture("hospital_coagulator", 346, 130, z, "Blackpipe coagulator")
    m.poi(304, 132, z, "The Blackpipe clinic")
    m.loot((304, 352, 104, 136), z, MEDICAL, most=4)

    m.room((40, 100, 280, 330), z, "The drop shop", floor="poured floor",
           height=9, wall="steel wall", kind="workshop")
    m.door((64, 74, 280, 280), z, "Drop shop shutter", floor="poured floor",
           height=4)
    m.ambience((41, 99, 281, 329), z, z + 8, "scrapyard")
    m.obj("workbench", 46, 286, z, "Stripping bench", 20, 4, 2)
    m.obj("workbench", 46, 312, z, "Rewiring bench", 20, 4, 2)
    m.obj("locker", 88, 300, z, "Parts lockers", 6, 12, 5)
    m.fixture("scrap_yard2", 76, 322, z, "Drop shop press")
    m.fixture("computer2", 76, 288, z, "Drop shop slicer terminal")
    m.poi(46, 296, z, "The drop shop")
    m.loot((44, 96, 284, 326), z, TECH + TOOLS + AMMO, seconds=90, most=4)
    m.bunker(200, 199, z, "The Crimson Corridor")


def _nth(n):
    return ["first", "second", "third", "fourth", "fifth", "sixth"][min(n - 1, 5)]


def _works(m):
    z = WORKS
    m.path("The Works, main conveyor road", (1, 399, 150, 170), "steel plate", z=z)
    m.path("The Works, the coolant court", (30, 120, 220, 320), "poured floor", z=z)
    m.poiregion((30, 120, 220, 320), z, z + 8, "The coolant court")
    m.obj("tank", 40, 230, z, "Drained coolant reservoir", 20, 20, 8)
    m.obj("tank", 40, 270, z, "Second reservoir, breached", 20, 20, 8)
    m.fixture("scrap_yard1", 100, 300, z, "Coolant court scrap")

    m.room((150, 260, 200, 280), z, "Foundry Nine, the casting floor",
           floor="poured floor", height=16, wall="steel wall", kind="hangar")
    m.door((198, 212, 200, 200), z, "Foundry Nine doors", floor="poured floor",
           height=5)
    m.door((150, 150, 230, 240), z, "Foundry Nine west door", floor="poured floor")
    m.window((260, 260, 214, 224), z + 6, "Foundry Nine east light")
    m.ambience((151, 259, 201, 279), z, z + 15, "warehouse")
    m.subzone((151, 200, 201, 279), z, "Casting floor, the cold end")
    m.subzone((210, 259, 201, 279), z, "Casting floor, the furnace end")
    m.obj("generator", 220, 208, z, "Number Nine furnace, dead", 14, 14, 8)
    m.obj("generator", 220, 250, z, "Number Ten furnace, dead", 14, 14, 8)
    m.obj("workbench", 158, 210, z, "Pattern bench", 18, 4, 2)
    m.obj("crate", 158, 260, z, "Sealed ingot crate", 8, 8, 4)
    m.fixture("crate", 184, 260, z, "Foundry supply crate")
    m.poi(156, 206, z, "Foundry Nine casting floor")
    m.loot((156, 254, 206, 274), z, TOOLS + TECH + AMMO, seconds=75, most=4)
    # The crane rail, high over the casting floor.
    m.tile((156, 254, 236, 242), z + 10, z + 10, "catwalk grating")
    m.zone((156, 254, 236, 242), z + 10, z + 15, "Foundry Nine, the crane rail")
    m.ladder(155, 239, z, z + 10, "Crane rail rungs", material="maintenance rungs",
             face=(156, 158, 238, 240))
    m.poi(162, 239, z + 10, "Foundry Nine crane rail")

    m.room((290, 370, 230, 300), z, "The Works, pumping gallery",
           floor="steel grating", height=10, wall="steel wall", kind="plant")
    m.door((320, 332, 230, 230), z, "Pumping gallery doors", floor="steel grating",
           height=4)
    m.ambience((291, 369, 231, 299), z, z + 9, "machinery hum")
    m.obj("generator", 296, 236, z, "Atmosphere pump one", 10, 10, 6)
    m.obj("generator", 296, 262, z, "Atmosphere pump two", 10, 10, 6)
    m.obj("screen", 350, 240, z, "Gallery control board", 3, 12, 4)
    m.fixture("computer1", 358, 260, z, "Pumping gallery terminal")
    m.poi(296, 290, z, "The Works pumping gallery")
    m.loot((294, 366, 234, 296), z, TECH + TOOLS, most=3)
    m.bunker(200, 160, z, "The Works conveyor road")


def _coco(m):
    z = COCO
    m.street("Coruscant Avenue", (1, 399, 180, 210), axis="x", z=z,
             surface="new asphalt", pavement="paving slabs", pavement_width=5,
             bed="busy street",
             segments=[(1, 100, "the western end"), (101, 200, "at Dex's"),
                       (201, 300, "the workshops"), (301, 399, "the eastern end")])
    m.street("Ledgerway", (100, 130, 1, 399), axis="y", z=z,
             surface="asphalt", pavement="paving slabs", pavement_width=5,
             segments=[(1, 179, "south of Coruscant Avenue"),
                       (211, 399, "north of Coruscant Avenue")])
    m.junction("Coruscant Avenue and Ledgerway", (100, 130, 180, 210), z=z,
               surface="new asphalt",
               crossings=[((100, 130, 180, 184), "southern crossing"),
                          ((100, 130, 206, 210), "northern crossing")])

    # Dex's Diner, which is a booth, a counter and a door, and is famous for
    # being exactly that.
    m.room((140, 196, 212, 244), z, "Dex's Diner", floor="linoleum", height=6,
           wall="glass curtain wall", kind="shop")
    m.door((162, 170, 212, 212), z, "Dex's Diner door", floor="linoleum")
    m.window((140, 140, 222, 234), z + 2, "Dex's Diner window")
    m.ambience((141, 195, 213, 243), z, z + 5, "diner")
    m.subzone((141, 195, 213, 226), z, "Dex's Diner, the booths")
    m.subzone((141, 195, 230, 243), z, "Dex's Diner, the counter")
    m.obj("counter", 144, 236, z, "The counter", 40, 3, 2)
    m.obj("table", 146, 216, z, "Booth one", 10, 5, 2)
    m.obj("table", 162, 216, z, "Booth two", 10, 5, 2)
    m.obj("table", 178, 216, z, "Booth three", 10, 5, 2)
    m.fixture("coke_machine", 190, 240, z, "Diner cooler")
    m.fixture("kiosk", 144, 216, z, "Diner supply terminal")
    m.poi(146, 222, z, "Dex's Diner")
    m.loot((144, 192, 216, 240), z, STREET + MEDICAL, most=3)

    m.room((220, 300, 220, 270), z, "Collective Commerce machine shops",
           floor="poured floor", height=10, wall="duracrete wall", kind="workshop")
    m.door((252, 262, 220, 220), z, "Machine shop shutters", floor="poured floor",
           height=4)
    m.door((300, 300, 240, 250), z, "Machine shop yard door", floor="poured floor")
    m.window((220, 220, 236, 246), z + 3, "Machine shop light")
    m.ambience((221, 299, 221, 269), z, z + 9, "warehouse")
    m.subzone((221, 258, 221, 269), z, "Machine shops, the west bay")
    m.subzone((264, 299, 221, 269), z, "Machine shops, the east bay")
    m.obj("workbench", 226, 226, z, "Repulsor teardown bench", 24, 4, 2)
    m.obj("workbench", 226, 256, z, "Calibration bench", 24, 4, 2)
    m.obj("locker", 286, 234, z, "Calibrated parts lockers", 6, 20, 5)
    m.fixture("table", 268, 226, z, "Machine shop service bench")
    m.poi(226, 232, z, "Collective Commerce machine shops")
    m.loot((226, 296, 226, 266), z, TOOLS + TECH, most=4)

    m.room((40, 96, 240, 290), z, "CoCo Town medcentre", floor="linoleum",
           height=7, wall="duracrete wall", kind="ward")
    m.door((62, 72, 240, 240), z, "Medcentre doors", floor="linoleum", height=4)
    m.ambience((41, 95, 241, 289), z, z + 6, "hospital")
    m.obj("bed", 44, 246, z, "Medcentre cot", 5, 9, 4)
    m.obj("bed", 54, 246, z, "Medcentre cot, second", 5, 9, 4)
    m.obj("cabinet", 86, 246, z, "Bacta press", 5, 3, 4)
    m.fixture("hospital_bed", 80, 280, z, "Medcentre treatment bed")
    m.fixture("hospital_ventilator", 88, 280, z, "Medcentre ventilator")
    m.fixture("instrument_prep", 48, 280, z, "Medcentre instrument bench")
    m.poi(44, 274, z, "CoCo Town medcentre")
    m.loot((44, 92, 244, 286), z, MEDICAL, most=4)
    m.fixture("atm", 136, 190, z, "Coruscant Avenue credit terminal")
    m.bunker(115, 195, z, "Coruscant Avenue and Ledgerway")


def _uscru(m):
    z = USCRU
    m.street("Vos Gesal Street", (1, 399, 180, 210), axis="x", z=z,
             surface="wet concrete", pavement="paving slabs", pavement_width=5,
             bed="city night",
             segments=[(1, 130, "the west end"), (131, 240, "the club front"),
                       (241, 399, "the opera end")])
    m.poiregion((1, 399, 180, 210), z, z + 8, "Vos Gesal Street")

    # The Outlander Club: a long bar, a gaming floor, and a back door onto the
    # street that everybody in the fiction ends up going out of at speed.
    m.room((140, 230, 120, 176), z, "The Outlander Club, the gaming floor",
           floor="thin carpet", height=9, wall="composite wall", kind="hall")
    m.room((230, 270, 120, 176), z, "The Outlander Club, the long bar",
           floor="thin carpet", height=9, wall="composite wall", kind="shop")
    m.door((178, 190, 176, 176), z, "Outlander Club street doors",
           floor="thin carpet", height=4)
    m.door((230, 230, 140, 154), z, "Outlander Club bar arch", floor="thin carpet")
    m.door((246, 256, 176, 176), z, "Outlander Club back door", floor="thin carpet")
    m.window((140, 140, 140, 156), z + 3, "Outlander Club window")
    m.ambience((141, 269, 121, 175), z, z + 8, "arcade")
    m.subzone((141, 185, 121, 175), z, "Gaming floor, the west tables")
    m.subzone((189, 229, 121, 175), z, "Gaming floor, the east tables")
    m.subzone((231, 269, 121, 140), z, "The long bar, the far end")
    for i, x in enumerate(range(146, 226, 26)):
        m.obj("table", x, 130, z, f"Sabacc table {i + 1}", 14, 6, 2)
        m.obj("table", x, 156, z, f"Sabacc table {i + 4}", 14, 6, 2)
    m.obj("counter", 236, 126, z, "The long bar", 5, 44, 2)
    m.obj("sofa", 258, 130, z, "Club booth", 8, 4, 4)
    m.fixture("coke_machine", 262, 168, z, "Club dispenser")
    m.fixture("atrium_speaker", 200, 124, z, "Club sound stack")
    m.poi(146, 126, z, "The Outlander Club gaming floor")
    m.poi(238, 168, z, "The Outlander Club long bar")
    m.loot((144, 266, 124, 172), z, STREET + RARE, seconds=75, most=4)

    # The Galaxies Opera House: the auditorium, the boxes above it, and the
    # foyer that faces the other way from the club on purpose.
    m.room((270, 380, 220, 300), z, "Galaxies Opera House, the auditorium",
           floor="carpet", height=20, wall="stone wall", kind="hall")
    m.room((270, 380, 300, 330), z, "Galaxies Opera House, the foyer",
           floor="polished marble", height=9, wall="stone wall", kind="atrium")
    m.door((318, 332, 330, 330), z, "Opera House doors", floor="polished marble",
           height=5)
    m.door((318, 332, 300, 300), z, "Auditorium doors", floor="carpet", height=4)
    m.window((270, 270, 308, 322), z + 3, "Opera House foyer window")
    m.ambience((271, 379, 221, 299), z, z + 19, "indoors")
    m.ambience((271, 379, 301, 329), z, z + 8, "bank hall")
    m.subzone((271, 379, 221, 250), z, "Auditorium, the stage end")
    m.subzone((271, 379, 254, 299), z, "Auditorium, the stalls")
    for i, y in enumerate(range(258, 296, 10)):
        m.obj("pew", 280, y, z, f"Stalls, row {i + 1}", 90, 3, 4)
    m.fixture("atrium_speaker", 276, 226, z, "Auditorium address")
    m.poi(276, 254, z, "Galaxies Opera House auditorium")
    m.poi(276, 304, z, "Galaxies Opera House foyer")
    m.loot((276, 376, 304, 326), z, RARE + STREET, most=3)
    # The boxes, reached by a stair off the foyer. This is the seat Palpatine
    # watches from, and it looks straight down the auditorium.
    m.stair((370, 378, 302, 316), z + 12, z, "Opera House box stair", axis="y",
            material="stone stairs", support="stone wall", kind="stairwell",
            base=z)
    m.deck((350, 378, 288, 301), z + 12, "Opera House, the box landing",
           material="carpet", kind="corridor")
    m.deck((300, 352, 288, 298), z + 12, "Galaxies Opera House, the boxes",
           material="carpet", kind="platform")
    m.obj("sofa", 306, 290, z + 12, "Box seating", 12, 4, 4)
    m.poi(324, 292, z + 12, "Galaxies Opera House boxes")
    m.bunker(200, 195, z, "Vos Gesal Street")


def _senate(m):
    z = SENATE
    m.area((1, 399, 1, 399), "The Senate District, the esplanade",
           "polished marble", z=z, kind="square", bed="city day")
    m.quarters((4, 396, 4, 396), z, "The Senate District esplanade",
               cols=4, rows=4, suffix="walk")

    # The Rotunda: a round building made of rectangles, which is a drum of
    # wall with a single ring of doors into a chamber you can hear the size of.
    cx, cy = 130, 130
    m.room((cx - 56, cx + 56, cy - 56, cy + 56), z, "The Senate Rotunda, the floor",
           floor="polished marble", height=26, wall="stone wall", kind="hall")
    for label, r in (("south", (cx - 6, cx + 6, cy - 56, cy - 56)),
                     ("north", (cx - 6, cx + 6, cy + 56, cy + 56)),
                     ("west", (cx - 56, cx - 56, cy - 6, cy + 6)),
                     ("east", (cx + 56, cx + 56, cy - 6, cy + 6))):
        m.door(r, z, f"Rotunda {label} doors", floor="polished marble", height=5)
    m.ambience((cx - 55, cx + 55, cy - 55, cy + 55), z, z + 25, "bank hall")
    m.subzone((cx - 55, cx - 20, cy - 55, cy + 55), z, "Rotunda floor, the west arc")
    m.subzone((cx + 20, cx + 55, cy - 55, cy + 55), z, "Rotunda floor, the east arc")
    m.subzone((cx - 20, cx + 20, cy - 20, cy + 20), z, "Rotunda floor, the well")
    m.obj("table", cx - 6, cy - 6, z, "The Chancellor's podium", 12, 12, 4)
    for i, ring in enumerate((26, 38, 50)):
        m.obj("pew", cx - ring, cy - ring + 2, z, f"Delegation pods, ring {i + 1}",
              ring * 2, 3, 4)
        m.obj("pew", cx - ring, cy + ring - 4, z,
              f"Delegation pods, ring {i + 1}, far side", ring * 2, 3, 4)
    m.fixture("atrium_speaker", cx + 30, cy + 30, z, "Rotunda address system")
    m.poi(cx - 40, cy - 40, z, "The Senate Rotunda floor")
    m.poiregion((cx - 56, cx + 56, cy - 56, cy + 56), z, z + 26,
                "The Senate Rotunda")
    m.loot((cx - 50, cx + 50, cy - 50, cy + 50), z, RARE, seconds=120, most=3)

    # The Republic Executive Building, next door and joined to it by a bridge.
    m.room((230, 320, 60, 140), z, "Republic Executive Building, the great hall",
           floor="polished marble", height=14, wall="stone wall", kind="atrium")
    m.door((268, 282, 140, 140), z, "Executive Building doors",
           floor="polished marble", height=5)
    m.window((320, 320, 86, 100), z + 4, "Executive Building east window")
    m.ambience((231, 319, 61, 139), z, z + 13, "bank hall")
    m.subzone((231, 274, 61, 139), z, "Executive great hall, the west side")
    m.subzone((278, 319, 61, 139), z, "Executive great hall, the east side")
    m.obj("counter", 236, 66, z, "Reception desk", 24, 4, 2)
    m.obj("bookcase", 236, 130, z, "Archive racks", 3, 8, 5)
    m.obj("bench", 290, 70, z, "Petitioners' bench", 14, 3, 4)
    m.fixture("computer1", 310, 70, z, "Executive records terminal")
    m.fixture("post_box", 310, 132, z, "Executive despatch")
    m.poi(238, 70, z, "Republic Executive Building great hall")
    m.loot((236, 316, 66, 136), z, RARE + MEDICAL, most=3)

    # Monument Plaza, and Umate: the peak of the only mountain on Coruscant
    # that still comes through the city, and the one piece of the original
    # planet anybody can touch.
    m.area((160, 260, 250, 350), "Monument Plaza", "granite setts", z=z,
           kind="square", bed="city day")
    m.plateau((196, 224, 286, 314), "Umate, the exposed peak", "bare rock", z + 6,
              side="rock wall", kind="mountain", base=z)
    m.stair((188, 195, 292, 308), z, z + 6, "Umate viewing steps", axis="x",
            material="stone stairs", support="rock wall", kind="mountain",
            base=z)
    m.poi(206, 300, z + 6, "Umate, the exposed peak")
    m.poiregion((160, 260, 250, 350), z, z + 8, "Monument Plaza")
    m.fixture("wooden_planter", 170, 260, z, "Plaza planter")
    m.fixture("street_light", 250, 260, z, "Plaza light")
    m.obj("bench", 168, 330, z, "Plaza bench", 12, 3, 4)
    m.obj("bench", 244, 330, z, "Plaza bench, east", 12, 3, 4)
    m.loot((164, 256, 254, 346), z, STREET + RARE, most=3)
    m.bunker(210, 260, z, "Monument Plaza")


def _temple(m):
    """The Jedi Temple, on its own ziggurat across the skylane from the Senate.

    A ziggurat is four setbacks, so it is four plateaus with a stair up each
    face; the Room of a Thousand Fountains is inside the second setback and is
    the loudest quiet place on the map."""
    z = SENATE
    steps = [(0, (280, 396, 230, 380)), (8, (292, 384, 242, 368)),
             (16, (304, 372, 254, 356)), (24, (316, 360, 266, 344))]
    for lift, r in steps:
        m.plateau(r, f"The Jedi Temple, the {_setback(lift)}", "granite setts",
                  z + lift, side="stone wall", kind="square", base=z)
    for i, (lift, r) in enumerate(steps[1:], start=1):
        low = steps[i - 1][0]
        m.stair((332, 344, r[2] - 11, r[2] - 1), z + low, z + lift,
                f"Temple steps to the {_setback(lift)}", axis="y",
                material="stone stairs", support="stone wall", kind="square",
                base=z + low)
    m.poiregion((280, 396, 230, 380), z, z + 40, "The Jedi Temple precinct")
    m.ambience((280, 396, 230, 380), z, z + 34, "still air")

    # The Temple's interior is on the ziggurat top, not buried inside a
    # terrace: a sixteen-high hall carved at the second setback would punch
    # straight up through the third and take the stair to it with it.
    top = z + 24
    m.room((318, 358, 306, 340), top, "The Temple, the processional hall",
           floor="polished marble", height=14, wall="stone wall", kind="hall")
    m.door((332, 344, 306, 306), top, "Temple processional doors",
           floor="polished marble", height=5)
    m.window((318, 318, 316, 330), top + 4, "Processional hall west light")
    m.ambience((319, 357, 307, 339), top, top + 13, "indoors")
    m.subzone((319, 357, 307, 320), top, "Processional hall, the entrance")
    m.subzone((319, 357, 326, 339), top, "Processional hall, the far end")
    m.obj("pew", 322, 314, top, "Meditation bench", 32, 3, 4)
    m.obj("pew", 322, 332, top, "Meditation bench, far", 32, 3, 4)
    m.poi(322, 310, top, "The Temple processional hall")
    m.loot((322, 354, 310, 336), top, RARE, seconds=120, most=2)

    m.room((318, 358, 268, 302), top, "The Room of a Thousand Fountains",
           floor="wet cobbles", height=14, wall="stone wall", kind="atrium")
    m.door((332, 344, 302, 302), top, "Fountain room doors", floor="wet cobbles",
           height=4)
    m.window((358, 358, 278, 292), top + 4, "Fountain room east light")
    m.ambience((319, 357, 269, 301), top, top + 13, "fountain")
    m.subzone((319, 337, 269, 301), top, "The Fountains, the western basins")
    m.subzone((339, 357, 269, 301), top, "The Fountains, the eastern basins")
    m.area((322, 334, 274, 296), "The Fountains, the long basin", "shallow water",
           z=top, kind="water")
    m.area((342, 354, 274, 296), "The Fountains, the second basin", "shallow water",
           z=top, kind="water")
    m.fixture("streams", 338, 284, top, "The Fountains")
    m.fixture("tree1", 338, 272, top, "Fountain room tree")
    m.poi(338, 298, top, "The Room of a Thousand Fountains")
    m.loot((336, 340, 272, 298), top, MEDICAL + RARE, most=3)

    # Five spires, standing on the third terrace round the ziggurat top, with
    # a ladder up the tallest. Its crown is the highest thing on the map.
    base = z + 16
    for i, (x, y, h) in enumerate(((312, 262, 40), (364, 262, 40), (312, 348, 40),
                                   (364, 348, 40), (338, 350, 54))):
        m.tile((x - 4, x + 4, y - 4, y + 4), base, base + h - 1, "stone wall")
        m.tile((x - 4, x + 4, y - 4, y + 4), base + h, base + h, "granite setts")
        m.zone((x - 4, x + 4, y - 4, y + 4), base + h, base + h + 5,
               f"Temple spire {i + 1}, the crown")
    # Only the central spire has a ladder; the other four are things you walk
    # into and hear, not places you can get to.
    m.poi(338, 350, base + 54, "The Temple central spire")
    m.ladder(333, 350, base, base + 54, "Temple central spire ladder",
             material="service ladder", face=(330, 332, 349, 351))
    m.ambience((330, 346, 342, 358), base + 54, base + 60, "high wind")
    m.bunker(338, 320, top, "The Jedi Temple precinct")


def _setback(lift):
    return {0: "outer precinct", 8: "second terrace", 16: "third terrace",
            24: "ziggurat top"}[lift]


def _skylanes(m):
    """The traffic lanes, above everything. In the fiction they are full of
    speeders; here they are the gantries that maintain them, which is the only
    part a person on foot could ever be on."""
    z = SKYLANE
    for i, y in enumerate((80, 200, 320)):
        deck = m.bridge((1, 399, y, y + 8), z, f"Skylane {_nth(i + 1)} gantry",
                        axis="x", deck="catwalk grating", rail="railing wall",
                        piers=[(x, y + 4) for x in range(40, 400, 40)],
                        pier_material="steel wall", bed="high wind")
        for j, x in enumerate(range(1, 400, 100)):
            m.zone((x, min(x + 99, 399), deck[2], deck[3]), z, z + 6,
                   f"Skylane {_nth(i + 1)} gantry, span {j + 1}")
    m.bridge((192, 200, 80, 320), z, "Skylane interchange gantry", axis="y",
             deck="catwalk grating", rail="railing wall",
             piers=[(196, y) for y in range(100, 320, 40)],
             pier_material="steel wall")
    # An interchange whose rails cross the gantries it is meant to interchange
    # with is three separate gantries and a sealed corridor. Cut the rails at
    # each crossing.
    for y in (80, 200, 320):
        m.air((192, 200, y, y + 8), z + 1, z + 2)
        m.air((192, 200, y, y + 8), z, z)
        m.tile((192, 200, y, y + 8), z, z, "catwalk grating")
        m.zone((192, 200, y, y + 8), z, z + 6, "Skylane interchange, the crossing")
    # Up from the Senate District on maintenance rungs, in three places.
    for x, y in ((60, 84), (196, 204), (120, 340)):
        # No air carve here. The rung column is laid as tiles and punches
        # through whatever it passes; carving round it instead takes the
        # esplanade out from under its foot and the gantry deck out from
        # under its head.
        m.ladder(x, y, SENATE, z, f"Skylane maintenance rungs at {x}, {y}",
                 material="maintenance rungs", face=(x + 1, x + 3, y - 1, y + 1))
        m.poi(x + 2, y, SENATE, f"Foot of the skylane rungs at {x}, {y}")
    m.poi(196, 200, z, "Skylane interchange")
    m.poiregion((1, 399, 80, 328), z, z + 6, "The skylanes")


def _spawns(m):
    points = [
        (60, 60, UNDER), (200, 199, UNDER), (340, 200, UNDER), (80, 300, UNDER),
        (60, 160, WORKS), (200, 160, WORKS), (340, 160, WORKS),
        (60, 195, COCO), (200, 195, COCO), (340, 195, COCO),
        (60, 195, USCRU), (200, 195, USCRU), (340, 195, USCRU),
        (60, 320, SENATE), (240, 330, SENATE), (130, 200, SENATE),
        (300, 180, SENATE), (340, 240, SENATE),
    ]
    for x, y, z in points:
        m.spawn(x, y, z)
