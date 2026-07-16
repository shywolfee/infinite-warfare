"""Assemble the Coruscant map and write it out."""
import sys
from lib import Map
import config as C
import c_surface, c_underworld, c_works, c_heights, c_main, c_senate, c_skydeck
import c_extra, c_lifts, c_finish
from validate import validate


def build():
    m = Map("Coruscant", C.MAXX, C.MAXY, C.MAXZ)
    m.raw("mapname:Coruscant")
    m.raw("maxx:%d" % C.MAXX)
    m.raw("maxy:%d" % C.MAXY)
    m.raw("maxz:%d" % C.MAXZ)
    c_surface.build(m)
    c_underworld.build(m)
    c_works.build(m)
    c_heights.build(m)
    c_main.build(m)
    c_senate.build(m)
    c_skydeck.build(m)
    c_extra.build(m)
    c_lifts.build(m)
    c_finish.build(m)
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
    with open(sys.argv[1] if len(sys.argv) > 1 else "coruscant.map", "w") as f:
        f.write(out)
    print("wrote %d lines" % len(m.lines))
