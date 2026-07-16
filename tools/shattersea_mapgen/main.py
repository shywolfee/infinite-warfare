"""Assemble the full Shattersea map and write it out."""
import sys
from lib import Map
import config as C
import d_base, d_north, d_south, d_east, d_west, d_extra, d_finish
from validate import validate


def build():
    m = Map("Shattersea", C.MAXX, C.MAXY, C.MAXZ)
    m.raw("mapname:Shattersea")
    m.raw("maxx:%d" % C.MAXX)
    m.raw("maxy:%d" % C.MAXY)
    m.raw("maxz:%d" % C.MAXZ)
    d_base.build(m)
    d_north.build(m)
    d_south.build(m)
    d_east.build(m)
    d_west.build(m)
    d_extra.build(m)
    d_finish.build(m)
    return m


if __name__ == "__main__":
    m = build()
    problems, stats = validate(m)
    print(stats)
    if problems:
        print("PROBLEMS (%d):" % len(problems))
        for p in problems[:40]:
            print("  " + p)
    else:
        print("OK - no problems")
    out = "\r\n".join(m.lines) + "\r\n"
    with open(sys.argv[1] if len(sys.argv) > 1 else "shattersea.map", "w") as f:
        f.write(out)
    print("wrote %d lines" % len(m.lines))
