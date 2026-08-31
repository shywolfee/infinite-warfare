"""Ground-up generators for Shattersea, Coruscant and Freya's Ascent.

This deliberately shares no layout data with the retired generators.  Each
composite writes geometry, a radio-useful zone, acoustics, portals and POIs as
separate layers, following Fireteam Requiem's map construction rules.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "iwserver" / "content" / "maps"
OPEN = "blank"


class Map:
    def __init__(self, name, mx, my, mz):
        self.lines = [f"mapname:{name}", f"maxx:{mx}", f"maxy:{my}", f"maxz:{mz}"]
    def section(self, s): self.lines += ["", "// " + "="*64, "// " + s, "// " + "="*64]
    def tile(self,x1,x2,y1,y2,z1,z2,t): self.lines.append(f"tile:{x1}:{x2}:{y1}:{y2}:{z1}:{z2}:{t}")
    def zone(self,x1,x2,y1,y2,z1,z2,n): self.lines.append(f"zone:{x1}:{x2}:{y1}:{y2}:{z1}:{z2}:{n}")
    def space(self,x1,x2,y1,y2,z1,z2,n,mat,kind,enclosed=True): self.lines.append(f"{'space' if enclosed else 'openspace'}:{x1}:{x2}:{y1}:{y2}:{z1}:{z2}:{n}:{mat}:{kind}")
    def portal(self,x1,x2,y1,y2,z1,z2,n): self.lines.append(f"portal:{x1}:{x2}:{y1}:{y2}:{z1}:{z2}:{n}:opening")
    def poi(self,x,y,z,n): self.lines.append(f"poi:{x}:{y}:{z}:{n}")
    def src(self,x1,x2,y1,y2,z1,z2,s,v): self.lines.append(f"src:{x1}:{x2}:{y1}:{y2}:{z1}:{z2}:{s}:{v}")
    def ispawn(self,x1,x2,y1,y2,z,items): self.lines.append(f"ispawn:{x1}:{x2}:{y1}:{y2}:{z}:{z}:1200:24:{':'.join(items)}")
    def turbolift(self,x1,x2,y1,y2,z1,z2,name,levels): self.lines.append(":".join(["turbolift",str(x1),str(x2),str(y1),str(y2),str(z1),str(z2),name]+[f"{n},{z}" for n,z in levels]))
    def ground(self,x1,x2,y1,y2,z,mat,name,kind="open"):
        self.tile(x1,x2,y1,y2,z,z,mat); self.zone(x1,x2,y1,y2,z,z+8,name); self.space(x1,x2,y1,y2,z,z+8,name,mat,kind,False)
    def room(self,x1,x2,y1,y2,z,height,name,floor="tile1",wall="wallbrick",kind="room",door="S"):
        self.tile(x1,x2,y1,y2,z,z,floor); self.zone(x1+1,x2-1,y1+1,y2-1,z,z+height-1,name); self.space(x1+1,x2-1,y1+1,y2-1,z,z+height-1,name,wall.replace("wall","") or "concrete",kind,True)
        c=(x1+x2)//2; d1,d2=c-1,c+1
        if door=="S":
            self.tile(x1,d1-1,y1,y1,z,z+height,wall); self.tile(d2+1,x2,y1,y1,z,z+height,wall); self.tile(d1,d2,y1,y1,z+4,z+height,wall); self.portal(d1,d2,y1,y1,z,z+3,name+" entrance")
        else:
            self.tile(x1,d1-1,y2,y2,z,z+height,wall); self.tile(d2+1,x2,y2,y2,z,z+height,wall); self.tile(d1,d2,y2,y2,z+4,z+height,wall); self.portal(d1,d2,y2,y2,z,z+3,name+" entrance")
        self.tile(x1,x1,y1,y2,z,z+height,wall); self.tile(x2,x2,y1,y2,z,z+height,wall)
        if door=="S": self.tile(x1,x2,y2,y2,z,z+height,wall)
        else: self.tile(x1,x2,y1,y1,z,z+height,wall)
        self.tile(x1,x2,y1,y2,z+height,z+height,wall); self.zone(x1,x2,y1,y2,z+height+1,z+height+8,"roof of "+name); self.poi((x1+x2)//2,(y1+y2)//2,z,name)
    def street_ns(self,x,y1,y2,name,z=0):
        self.ground(x-4,x+4,y1,y2,z,"concrete5",name,"street"); self.ground(x-7,x-5,y1,y2,z,"cement","west pavement of "+name,"street"); self.ground(x+5,x+7,y1,y2,z,"cement","east pavement of "+name,"street")
    def street_ew(self,y,x1,x2,name,z=0):
        self.ground(x1,x2,y-4,y+4,z,"concrete5",name,"street"); self.ground(x1,x2,y-7,y-5,z,"cement","south pavement of "+name,"street"); self.ground(x1,x2,y+5,y+7,z,"cement","north pavement of "+name,"street")
    def ramp(self,x1,x2,y1,y2,z1,z2,name,surface="stone"):
        rise=z2-z1; levels=abs(rise)+1; along_x=(x2-x1)>(y2-y1); length=(x2-x1+1 if along_x else y2-y1+1)
        if length<levels:
            if along_x:x2+=levels-length
            else:y2+=levels-length
            length=levels
        base,extra=divmod(length,levels); cut=x1 if along_x else y1; direction=1 if rise>=0 else -1
        for i in range(levels):
            n=base+(i<extra); lo,hi=cut,cut+n-1; z=z1+direction*i
            if along_x:self.tile(lo,hi,y1,y2,z,z,surface)
            else:self.tile(x1,x2,lo,hi,z,z,surface)
            if z>min(z1,z2):
                if along_x:self.tile(lo,hi,y1,y2,z-1,z-1,"wallstone")
                else:self.tile(x1,x2,lo,hi,z-1,z-1,"wallstone")
            cut=hi+1
        self.zone(x1,x2,y1,y2,min(z1,z2),max(z1,z2)+7,name); self.space(x1,x2,y1,y2,min(z1,z2),max(z1,z2)+7,name,surface,"platform",False)
    def write(self,path):
        path.parent.mkdir(parents=True,exist_ok=True)
        # Keep generated output byte-stable across Windows and Unix checkouts.
        with path.open("w",encoding="utf-8",newline="\n") as output:
            output.write("\n".join(self.lines)+"\n")


LOOT=["frag_grenade","smoke_bomb","nanocyte_reconstruction_solution","AK47_ammo_10_50","glock17_ammo_10_40","weapon_cleaning_solvent"]


def shattersea():
    m=Map("battlegrounds",520,520,80); m.section("THE SHATTERSEA AND NEW AURELIA ISLAND")
    m.ground(0,520,0,520,0,"shallow","the Shattersea","water"); m.src(0,520,0,520,0,8,"ocean1.ogg",-14)
    m.ground(35,485,35,485,0,"sand","New Aurelia beach","beach"); m.ground(55,465,55,465,0,"concrete2","New Aurelia","plaza")
    m.section("CANALS, STREETS AND NAMED JUNCTIONS")
    m.ground(55,465,246,274,0,"water1","the Crown Canal","water")
    for x,n in [(105,"Tideway"),(205,"Lantern Avenue"),(315,"Founders Road"),(415,"Breakwater Drive")]: m.street_ns(x,55,465,n)
    for y,n in [(105,"South Quay Road"),(195,"Market Street"),(325,"Civic Way"),(415,"Northwall Road")]: m.street_ew(y,55,465,n)
    for x in (105,205,315,415):
        m.ground(x-5,x+5,246,274,2,"bridge","a Crown Canal bridge","bridge"); m.ramp(x-5,x+5,235,245,0,2,"south bridge approach","stone"); m.ramp(x-5,x+5,275,285,2,0,"north bridge approach","stone")
    m.section("FOUR COMPLETE DISTRICTS")
    buildings=[(65,135,125,175,"Saltglass Exchange","office"),(145,195,125,175,"Mariners Clinic","clinic"),(225,295,125,175,"Southwatch Armoury","armoury"),(335,395,125,175,"Ash & Anchor Tavern","bar"),(65,135,345,395,"Northwall Apartments","apartment"),(145,215,345,405,"Aurelia Library","hall"),(235,305,345,405,"Storm Market","shop"),(335,435,345,405,"Harbour Warehouse","warehouse"),(65,135,285,315,"Canal Customs House","office"),(145,215,285,315,"Ferrymaster's Hall","hall"),(305,365,285,315,"Crown Workshops","factory"),(385,445,285,315,"East Lock Station","control")]
    for x1,x2,y1,y2,n,k in buildings:m.room(x1,x2,y1,y2,0,12,n,"tile1","wallbrick",k,"S" if y1<260 else "N")
    m.ground(225,295,205,235,4,"stone","the elevated Founders Memorial","plaza"); m.ramp(245,275,196,204,0,4,"Founders Memorial south ramp","stone"); m.poi(260,220,4,"Founders Memorial")
    m.ispawn(55,465,55,465,0,LOOT); m.poi(260,300,0,"New Aurelia central deploy point"); return m


def coruscant():
    m=Map("habitat_alpha",640,640,520); m.section("THE ABYSS AND THREE INDEPENDENT CITY DECKS")
    m.ground(0,640,0,640,0,"rocks1","the lightless Coruscant undercity","void"); m.src(0,640,0,640,0,8,"rumble.ogg",-16)
    levels=[("Works Level",60),("Civic Level",220),("Sky Level",380)]
    for li,(lname,z) in enumerate(levels):
        lo,hi=40,600; m.ground(lo,hi,lo,hi,z,"metal4",lname,"platform"); m.src(lo,hi,lo,hi,z,z+8,"city.ogg",-18)
        for x,n in [(130,"Aurora Spine"),(320,"Republic Axis"),(510,"Centax Way")]:m.street_ns(x,lo,hi,lname+", "+n,z)
        for y,n in [(130,"Senate Traverse"),(320,"Monument Row"),(510,"Orbital Road")]:m.street_ew(y,lo,hi,lname+", "+n,z)
        names=[["Droid Foundry","Transit Machine Hall","Power Regulation Vault","Underdeck Clinic"],["Republic Archive","Judicial Hall","Galactic Exchange","Civic Security Bureau"],["Orbital Customs","Diplomatic Residence","Skyline Observatory","Executive Landing Control"]][li]
        kinds=[["factory","garage","reactor","clinic"],["hall","hall","office","base"],["control","apartment","hall","control"]][li]
        plots=[(55,115,150,205),(145,205,335,395),(335,395,150,205),(430,585,335,395)]
        for (x1,x2,y1,y2),n,k in zip(plots,names,kinds):m.room(x1,x2,y1,y2,z,12,lname+", "+n,"metal2","wallmetal",k)
        m.ground(270,370,270,370,z+5,"metal5",lname+", the raised transit forum","platform"); m.ramp(300,340,250,269,z,z+5,lname+", forum south ramp","metal4"); m.ramp(300,340,371,390,z+5,z,lname+", forum north ramp","metal4")
        m.ispawn(lo,hi,lo,hi,z,LOOT)
    m.section("TURBOLIFT SHAFTS AND OPEN LANDING PORTALS")
    m.turbolift(312,328,300,316,60,380,"Republic Axis grand turbolift",levels)
    for n,z in levels:m.portal(312,328,300,300,z,z+5,n+" turbolift doors")
    m.poi(320,335,220,"Coruscant civic deploy point"); return m


def freya():
    m=Map("freyas_ascent",560,680,100); m.section("FREYA VALLEY")
    m.ground(0,560,0,680,0,"grass3","Freya Valley","valley"); m.src(0,560,0,680,0,8,"forest.ogg",-14)
    for x,n in [(110,"Pilgrim Trail"),(280,"Freya Road"),(450,"Hunter's Track")]:m.street_ns(x,20,650,n)
    m.section("THE FOUR ASCENDING TERRACES")
    terraces=[(40,520,70,180,0,"Lower Settlement"),(70,490,220,330,8,"Pinewatch Terrace"),(100,460,370,480,16,"Shieldmaiden Terrace"),(140,420,520,630,24,"Freya Citadel")]
    for i,(x1,x2,y1,y2,z,name) in enumerate(terraces):
        m.ground(x1,x2,y1,y2,z,"stone",name,"courtyard"); m.poi((x1+x2)//2,(y1+y2)//2,z,name)
        if i:
            prev=terraces[i-1]; m.ramp(250,310,prev[3]+1,y1-1,prev[4],z,name+" main ascent","stone")
        m.room(x1+15,x1+85,y1+15,y1+65,z,11,name+" lodge","hardwood","wallwood","house")
        m.room(x2-100,x2-15,y1+15,y1+70,z,12,name+" storehouse","stone","wallstone","store")
        m.room(x1+120,x1+205,y2-70,y2-15,z,14,name+" guard hall","stone","wallstone","base","N")
        m.ispawn(x1,x2,y1,y2,z,LOOT)
    m.section("CAVES BENEATH THE ASCENT")
    m.ground(170,390,390,500,-12,"rocks1","the Rootvault Caverns","cave"); m.space(170,390,390,500,-12,-2,"the Rootvault Caverns","rock","cave",True); m.src(170,390,390,500,-12,-2,"drip.ogg",-12)
    m.ramp(210,245,370,389,16,-12,"the Rootvault descending passage","rocks1"); m.portal(210,245,389,389,-12,16,"the Rootvault cave mouth")
    m.poi(280,125,0,"Freya Valley deploy point"); return m


if __name__ == "__main__":
    outputs=[(shattersea(),MAPS/"battlegrounds"/"main.map"),(coruscant(),MAPS/"habitat_alpha"/"habitat_alpha.map"),(freya(),MAPS/"freyas_ascent"/"freyas_ascent.map")]
    for m,path in outputs:m.write(path);print(f"{path.relative_to(ROOT)}: {len(m.lines)} entirely new records")
