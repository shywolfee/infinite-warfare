"""Master geography for Coruscant - a planet-spanning ecumenopolis rendered as a
deeply vertical stack of city levels. +X east, +Y north, +Z up.

The city is built as a series of platforms floating at different Z. You spawn on
the Main Level, roughly a thousand tiles up; the city climbs above you to the
skydecks and drops far below you to the lawless underworld and the never-seen
planetary surface. Walk off an unguarded edge and you fall to whatever level
lies beneath - which is how you reach some places. Turbolifts (Shift+P on a
control panel) are the proper way between levels."""

MAXX, MAXY, MAXZ = 1600, 1600, 2000

# Level base heights (absolute Z of each platform's deck).
SURFACE = 12       # the planetary surface: pitch dark, catches every fall
UNDERWORLD = 150   # Level 1313 - the Coruscant underworld
WORKS = 440        # The Works - abandoned industrial level
HEIGHTS = 730      # Calacor Heights - mid-city residential
MAIN = 1020        # Main Level - CoCo Town, Monument Plaza, Uscru (spawn)
SENATE = 1330      # the Senate & Federal District (upper level)
SKYDECK = 1630     # the skydecks and the upper spaceport

LEVELS = [
    ("the planetary surface", SURFACE),
    ("Level 1313, the underworld", UNDERWORLD),
    ("The Works", WORKS),
    ("Calacor Heights", HEIGHTS),
    ("the Main Level", MAIN),
    ("the Senate District", SENATE),
    ("the Skydeck", SKYDECK),
]

# Turbolift shaft footprints (kept constant across the levels each one serves so
# the shaft lines up vertically).
CENTRAL_LIFT = (786, 802, 786, 802)   # serves every level
SPACEPORT_LIFT = (1146, 1162, 786, 802)  # Main, Senate, Skydeck
UNDER_LIFT = (360, 376, 360, 376)     # Works, Underworld, Surface (hard to reach)

# Deploy point: Monument Plaza on the Main Level (west of Umate, clear ground).
SPAWN_X1, SPAWN_X2 = 700, 768
SPAWN_Y1, SPAWN_Y2 = 660, 698
SPAWN_Z = MAIN
