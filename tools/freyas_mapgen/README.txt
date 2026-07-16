Freya's Ascent map generator
============================

Generates iwserver/content/maps/freyas_ascent/freyas_ascent.map. The map file is
checked in; you only need this if you want to change the ship or the planet and
regenerate it.

Usage:
    cd tools/freyas_mapgen
    python3 main.py ../../iwserver/content/maps/freyas_ascent/freyas_ascent.map

main.py must report: holes=0 unreachable=0 oob=0 and no warnings.

Freya's Ascent is a vertical, enclosed ship. It reuses the shared
lib.py/structures.py (level offset via m.at_level, turbolift_tower, house/shop/
office_block) and adds one thing: the transition emitter (m.transition), which
writes the transition: directive the client reads for the Shift+L airlock.

Layout constants live in config.py. Files: f_surface (Aesir VI - field, forest,
river, hill+cabin, village), f_ship_ext (the outside of the hull), f_cargo (the
cargo hold), f_common (the shared deck builder) + f_decks (the seven decks),
f_lifts (the forward and aft turbolifts), f_transitions (the airlock and its two
transitions) and f_finish. validate.py checks fall holes, per-level reachability
from recorded seeds, sub-7-Z zones and bounds (negative Z is allowed for the
surface cellars).

The transition and turbolift mechanics themselves are client code: parsing in
includes/map.nvgt and the Shift+L / Shift+P handlers in Infinite Warfare.nvgt.
