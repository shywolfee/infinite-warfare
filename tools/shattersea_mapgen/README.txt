Shattersea map generator
=========================

This directory generates iwserver/content/maps/battlegrounds/main.map (the
Shattersea map). The map file is checked in, so you only need this if you want
to change the city and regenerate it.

Usage:
    cd tools/shattersea_mapgen
    python3 main.py ../../iwserver/content/maps/battlegrounds/main.map

main.py prints statistics and a list of problems. It must report:
    holes=0 unreachable=0 oob=0     and no bad tile / <7 Z warnings.

Files:
    lib.py          Map primitives (tiles, zones, walls with doorway gaps,
                    furniture with 7-Z "on top" caps). Enforces the mechanics:
                    every zone spans >=7 Z (a jump rises 5), a "wall" tile blocks
                    at the player's Z, and a doorway is a real gap in the wall.
    structures.py   Mid-level builders: streets (road/curb/sidewalk), buildings
                    (walls + entrances + wall-awareness zones + roofs), office
                    blocks, shops, houses (basements, attics, upper storeys,
                    staircases with railings, bilco bulkheads).
    config.py       The master geography (island, canal, bridges, districts).
    d_base.py       Ocean, island, beach, harbour, canal and the four bridges.
    d_north/south/east/west.py   The four quarters of Meridian.
    d_extra.py      A density pass of additional buildings.
    d_finish.py     Underground bunkers, citywide item spawns, deploy point.
    validate.py     Checks for fall holes (no floor under a walkable zone),
                    sub-7-Z zones, out-of-bounds, and reachability (a z0 flood
                    fill from the deploy point that catches any sealed building).

Coordinate system: +X east, +Y north, +Z up (vertical / jump height).
