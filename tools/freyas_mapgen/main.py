"""Assemble the Freya's Ascent map and write it out."""
import sys
from lib import Map
import config as C
import f_surface, f_ship_ext, f_cargo, f_decks, f_lifts, f_transitions, f_finish
from validate import validate


def build():
    m = Map("Freya's Ascent", C.MAXX, C.MAXY, C.MAXZ)
    m.raw("mapname:Freya's Ascent")
    m.raw("maxx:%d" % C.MAXX)
    m.raw("maxy:%d" % C.MAXY)
    m.raw("maxz:%d" % C.MAXZ)
    f_surface.build(m)
    f_ship_ext.build(m)
    f_cargo.build(m)
    f_decks.build(m)
    f_lifts.build(m)
    f_transitions.build(m)
    f_finish.build(m)
    m.at_level(0)
    return m


if __name__ == "__main__":
    m = build()
    problems, stats = validate(m)
    print(stats)
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems[:45]:
            print("  " + p)
    else:
        print("OK - no problems")
    out = "\r\n".join(m.lines) + "\r\n"
    with open(sys.argv[1] if len(sys.argv) > 1 else "freyas_ascent.map", "w") as f:
        f.write(out)
    print("wrote %d lines" % len(m.lines))
