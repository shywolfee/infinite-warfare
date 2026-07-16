"""The turbolifts that stitch Coruscant's levels together. Each is a car with a
control panel at every level it serves; stand on the panel and press Shift+P to
choose a destination. Level names here carry no commas or colons (the map format
uses those as separators)."""
import structures as S
import config as C


def build(m):
    m.section("TURBOLIFTS")

    # The Grand Central Turbolift - reaches every level.
    central = [
        ("the Skydeck", C.SKYDECK),
        ("the Senate District", C.SENATE),
        ("the Main Level", C.MAIN),
        ("Calacor Heights", C.HEIGHTS),
        ("The Works", C.WORKS),
        ("Level 1313 - the underworld", C.UNDERWORLD),
        ("the planetary surface", C.SURFACE),
    ]
    x1, x2, y1, y2 = C.CENTRAL_LIFT
    S.turbolift_tower(m, "the Grand Central Turbolift", x1, x2, y1, y2, central)
    m.poi((x1 + x2) // 2, (y1 + y2) // 2, C.MAIN, "the Grand Central Turbolift")

    # The Spaceport Turbolift - upper three levels.
    spaceport = [
        ("the Skydeck spaceport", C.SKYDECK),
        ("the Senate District", C.SENATE),
        ("the Main Level Spaceport", C.MAIN),
    ]
    x1, x2, y1, y2 = C.SPACEPORT_LIFT
    S.turbolift_tower(m, "the Spaceport Turbolift", x1, x2, y1, y2, spaceport)
    m.poi((x1 + x2) // 2, (y1 + y2) // 2, C.MAIN, "the Spaceport Turbolift")

    # The Underlevel Maintenance Turbolift - the only lift down to 1313.
    under = [
        ("The Works", C.WORKS),
        ("Level 1313 - the underworld", C.UNDERWORLD),
        ("the planetary surface", C.SURFACE),
    ]
    x1, x2, y1, y2 = C.UNDER_LIFT
    S.turbolift_tower(m, "the Underlevel Maintenance Turbolift", x1, x2, y1, y2, under)
    m.poi((x1 + x2) // 2, (y1 + y2) // 2, C.WORKS, "the Underlevel Maintenance Turbolift")
