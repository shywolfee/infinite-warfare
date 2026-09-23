"""Build every world map. Edit the layout modules, not the .map files."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "iwserver/content/maps"

TARGETS = {}


def _load():
    from mapgen import ghost_town
    TARGETS["freeforall/freeforall.map"] = ghost_town.build
    try:
        from mapgen import shattersea
        TARGETS["battlegrounds/main.map"] = shattersea.build
    except ImportError:
        pass
    try:
        from mapgen import freyas_ascent
        TARGETS["freyas_ascent/freyas_ascent.map"] = freyas_ascent.build
    except ImportError:
        pass
    try:
        from mapgen import coruscant
        TARGETS["habitat_alpha/habitat_alpha.map"] = coruscant.build
    except ImportError:
        pass


if __name__ == "__main__":
    _load()
    for filename, build in TARGETS.items():
        m = build()
        m.write(MAPS / filename)
        print(f"{filename}: {len(m.lines)} records, {m.zone_count} zones, "
              f"{m.poi_count} landmarks, {m.object_count} objects, "
              f"{m.fixture_count} services, {m.source_count} ambience beds, "
              f"{len(m.spawns)} spawns")
