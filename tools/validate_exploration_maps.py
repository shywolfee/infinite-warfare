"""Enforce complete, local navigation and floor coverage on playable terrain."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAPS=ROOT/"iwserver"/"content"/"maps"
SPECS={
    "battlegrounds/main.map":[(0,1040,0,1040,0)],
    "habitat_alpha/habitat_alpha.map":[(40,1240,40,1240,z) for z in (0,120,300,500)],
    "freyas_ascent/freyas_ascent.map":[(0,1000,0,1200,0),(90,910,300,490,8),(120,880,540,730,16),(150,850,780,970,24),(190,810,1020,1170,32),(170,390,410,525,-16),(410,590,410,525,-16),(610,830,410,525,-16),(260,460,570,690,-16),(540,740,570,690,-16),(390,410,455,480,-16),(590,610,455,480,-16),(350,650,525,570,-16)],
    "freeforall/freeforall.map":[(0,1100,0,700,0)],
    "battleroyale/battleroyale.map":[(0,500,0,500,0)],
}
GENERIC={"open field","the battle royale map","works level","civic level","sky level","greater freya valley","new aurelia"}

def records(lines,kind):
    out=[]
    for line in lines:
        fields=line.split(":")
        if fields[0]==kind and len(fields)>=8:
            out.append((int(fields[1]),int(fields[2]),int(fields[3]),int(fields[4]),int(float(fields[5])),int(float(fields[6])),fields[7].strip()))
    return out

def cover(rects,x1,x2,y1,y2,z):
    width=x2-x1+1; height=y2-y1+1; painted=bytearray(width*height)
    for rx1,rx2,ry1,ry2,rz1,rz2,_ in rects:
        if not rz1<=z<=rz2:continue
        ax1=max(x1,rx1);ax2=min(x2,rx2);ay1=max(y1,ry1);ay2=min(y2,ry2)
        if ax1>ax2 or ay1>ay2:continue
        stripe=b"\1"*(ax2-ax1+1)
        for y in range(ay1,ay2+1):
            start=(y-y1)*width+ax1-x1;painted[start:start+len(stripe)]=stripe
    return painted.count(0)

for relative,areas in SPECS.items():
    path=MAPS/relative;lines=path.read_text(encoding="utf-8").splitlines()
    zones=records(lines,"zone");tiles=records(lines,"tile")
    bad=[name for *_,name in zones if name.lower() in GENERIC]
    if bad:raise SystemExit(f"{relative}: generic zones remain: {sorted(set(bad))}")
    for area in areas:
        missing_zone=cover(zones,*area);missing_floor=cover(tiles,*area)
        if missing_zone or missing_floor:raise SystemExit(f"{relative} area {area}: {missing_zone} unnamed, {missing_floor} without floor")
    print(f"{relative}: {len(areas)} exploration areas fully floored and locally named")
