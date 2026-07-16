"""Master geography for the Shattersea map (Meridian city).

+X east, +Y north. The island sits in the Shattersea. Meridian is split into
four quarters that meet at the middle; the Old Anchorhold Canal runs east-west
across the whole island dividing the northern quarters from the southern ones.
Four named bridges cross the canal."""

MAXX, MAXY, MAXZ = 1300, 1300, 120

# Island interior (inside the beach ring).
ISL_X1, ISL_X2 = 150, 1150
ISL_Y1, ISL_Y2 = 150, 1150
BEACH = 34  # beach ring width

# Old Anchorhold Canal - east/west waterway through the middle.
CANAL_Y1, CANAL_Y2 = 612, 688

# East/West band split.
WEST_X1, WEST_X2 = 150, 468      # West Meridian (waterfront)
CEN_X1, CEN_X2 = 472, 828        # North & South Meridian live here
EAST_X1, EAST_X2 = 832, 1150     # East Meridian (airport)

# North / South halves of the central band.
SOUTH_Y1, SOUTH_Y2 = 150, 610
NORTH_Y1, NORTH_Y2 = 690, 1150

# Bridges over the canal (x centres, each a road crossing).
BRIDGE_IVORY_X = (232, 260)      # Ivory Bridge  (west, feeds Oceanfront Drive)
BRIDGE_REDMYR_X = (548, 576)     # Redmyr Bridge (central-west)
BRIDGE_OLDSMITH_X = (724, 752)   # Old Smith's Bridge (central-east)
BRIDGE_ANCHOR_X = (966, 994)     # Anchorhold Bridge (east)

# Player deploy point (North Meridian, Meridian Plaza, north of the fountain).
SPAWN_X1, SPAWN_X2 = 660, 705
SPAWN_Y1, SPAWN_Y2 = 990, 1016
