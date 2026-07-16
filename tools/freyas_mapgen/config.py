"""Freya's Ascent - a starship landed on Aesir VI, a verdant forested world.

The ship is enclosed and vertical: a cargo hold and seven stacked decks, joined
by a turbolift at the north (forward) and south (aft) end of every deck. The
whole hull is also modelled on the outside, sitting on a landing field, so you
can walk right around it. The only way between the interior and the planet is the
airlock on Deck 1's north side: press Shift+L there to step down onto Aesir VI
(and again outside to climb back aboard).

+X east, +Y north, +Z up. The planet surface is Z 0; the decks float above it."""

MAXX, MAXY, MAXZ = 920, 1000, 220

# Ship interior footprint (a deck's outline) and the outer hull footprint.
SX1, SX2 = 330, 550
SY1, SY2 = 250, 830
HX1, HX2 = 306, 574
HY1, HY2 = 226, 854

# Deck heights (absolute Z of each floor). The cargo hold is separate, below
# Deck 1; it is not one of the seven decks.
SURFACE = 0
CARGO = 40
DECK1, DECK2, DECK3, DECK4, DECK5, DECK6, DECK7 = 60, 80, 100, 120, 140, 160, 180
DECK_Z = [DECK1, DECK2, DECK3, DECK4, DECK5, DECK6, DECK7]

# Every turbolift serves the cargo hold and all seven decks.
LIFT_STOPS = [
    ("the cargo hold", CARGO),
    ("Deck 1", DECK1),
    ("Deck 2", DECK2),
    ("Deck 3", DECK3),
    ("Deck 4", DECK4),
    ("Deck 5", DECK5),
    ("Deck 6", DECK6),
    ("Deck 7 - the bridge", DECK7),
]

# Interior layout bands (shared by every deck), contiguous from aft to forward:
#   aft junction | aft wall(296) | compartments | fwd wall(784) | fwd junction
SJ_Y1, SJ_Y2 = 251, 295        # aft (south) junction
AFT_WALL = 296
MID_Y1, MID_Y2 = 297, 783      # compartment section
FWD_WALL = 784
NJ_Y1, NJ_Y2 = 785, 829        # forward (north) junction
SP_X1, SP_X2 = 434, 446        # central spine corridor
SPINE_WW, SPINE_EW = 433, 447  # spine side walls

# Turbolift cars (constant footprint across every level they serve).
LIFT_N = (428, 452, 798, 824)  # forward turbolift, opens south into the junction
LIFT_S = (428, 452, 256, 282)  # aft turbolift, opens north into the junction

# Airlock (Deck 1, north) and the field point you step out onto.
AIRLOCK = (418, 462, 806, 826)
AIRLOCK_EXIT = (438, 442, 862)         # where Shift+L in the airlock drops you
AIRLOCK_RETURN_ZONE = (426, 454, 858, 868)  # field zone that boards the ship
AIRLOCK_INSIDE = (440, 816, DECK1)     # where Shift+L outside puts you back

# Deploy point: Deck 1 aft junction.
SPAWN_X1, SPAWN_X2 = 360, 520
SPAWN_Y1, SPAWN_Y2 = 260, 288
SPAWN_Z = DECK1
