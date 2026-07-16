"""The airlock on Deck 1's north side and the transitions that let you step
between the ship's interior (up on Deck 1) and the planet surface (down on the
landing field). Press Shift+L inside a transition zone to travel."""
from lib import GROUND_TOP, ROOM_TOP
import structures as S
import config as C


def build(m):
    m.section("THE AIRLOCK AND ITS TRANSITIONS (Shift+L)")
    # The airlock chamber, built into the port-forward corner of Deck 1's
    # forward junction (clear of the forward turbolift on the centreline).
    m.at_level(C.DECK1)
    ax1, ax2, ay1, ay2 = 336, 392, 800, 826
    m.wall_x(ax1, ay1, ay2, ROOM_TOP, "wallstone")
    m.wall_x(ax2, ay1, ay2, ROOM_TOP, "wallstone")
    m.wall_y(ay2, ax1, ax2, ROOM_TOP, "wallstone")
    m.wall_y(ay1, ax1, ax2, ROOM_TOP, "wallstone", [(358, 368)])
    m.zone(ax1 + 1, ax2 - 1, ay1 + 1, ay2 - 1, 0, ROOM_TOP, "the Deck 1 airlock")
    S.doorway(m, 358, 368, ay1, ay1, "the airlock inner hatch")
    m.zone_raw(350, 380, 820, 825, 0, GROUND_TOP, "the airlock outer hatch")
    m.at_level(0)

    # Interior -> surface: step down the boarding ramp onto Aesir VI.
    m.transition(350, 380, 818, 826, C.DECK1, C.DECK1 + GROUND_TOP,
                 364, 864, 0,
                 "You cycle the airlock and step down the ramp onto Aesir VI.")
    # Surface -> interior: climb the ramp and cycle back aboard.
    m.transition(348, 382, 858, 867, 0, GROUND_TOP,
                 364, 814, C.DECK1,
                 "You climb the ramp and cycle the airlock back aboard Freya's Ascent.")
    m.poi(364, 864, 0, "the airlock of Freya's Ascent")
