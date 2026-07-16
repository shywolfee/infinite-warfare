Coruscant map generator
========================

Generates iwserver/content/maps/habitat_alpha/habitat_alpha.map (the Coruscant
map - the directory and network mode id stay "habitat_alpha"; only the content
and the display name changed). The map file is checked in; you only need this if
you want to change the city and regenerate it.

Usage:
    cd tools/coruscant_mapgen
    python3 main.py ../../iwserver/content/maps/habitat_alpha/habitat_alpha.map

main.py must report: holes=0 unreachable=0 oob=0 and no warnings.

Coruscant is a vertical city: platforms float at very different Z. The shared
lib.py/structures.py (from the Shattersea generator) gain three things here:

    m.at_level(z)   sets a base-Z offset added to every subsequent emit, so the
                    ordinary street/building/house helpers can be reused to build
                    a whole level in local coordinates.
    turbolift_tower a car with a control panel and doorway at each level it
                    serves, plus the turbolift: directive the client reads.
    hole / platform deliberate fall-through openings and floating decks, so
                    walking off an edge drops you to the level below.

Level heights live in config.py. Files: c_surface, c_underworld, c_works,
c_heights, c_main, c_senate, c_skydeck (the levels), c_extra (a density pass),
c_lifts (the turbolifts) and c_finish (loot + orientation). validate.py checks
fall holes, per-level reachability from recorded seeds, sub-7-Z zones and bounds.

The turbolift mechanic itself is client code: parsing in includes/map.nvgt and
the Shift+P menu / movement in Infinite Warfare.nvgt.
