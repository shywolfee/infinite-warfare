"""Ground-up generators for Shattersea, Coruscant, Freya's Ascent and Battle Royale.

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
    # 970 by 970 authored island versus the former 410 by 410 city: more than
    # four times the playable area. Water deliberately has no ambient source.
    m=Map("battlegrounds",1040,1040,100); m.section("THE SHATTERSEA AND GREATER NEW AURELIA")
    m.ground(0,1040,0,1040,0,"shallow","the quiet Shattersea","water")
    m.ground(25,1015,25,1015,0,"sand","New Aurelia beach","beach")
    districts=[(55,495,55,495,"Southwatch Ward"),(545,985,55,495,"Eastwater Ward"),(55,495,545,985,"Lantern Ward"),(545,985,545,985,"Northwall Ward")]
    for x1,x2,y1,y2,n in districts:m.ground(x1,x2,y1,y2,0,"concrete2",n,"plaza")
    m.section("NAMED NEW AURELIA BLOCKS AND TERRAIN")
    # These blocks cover every non-canal city coordinate continuously; streets
    # emitted below override them with a still more precise location.
    xbands=[(55,209),(210,374),(375,544),(545,714),(715,879),(880,985)]
    ybands=[(55,199),(200,349),(350,449),(450,495),(545,599),(600,759),(760,919),(920,985)]
    colnames=["Tidegate","Saltglass","Lantern","Founders","Crown","Breakwater"]
    rownames=["South Strand","Mariners","Market","Canalside South","Canalside North","Civic","Stormglass","North Strand"]
    block_mats=["concrete2","cement","stone","tile2","concrete3","hardwood2"]
    for row,(y1,y2) in enumerate(ybands):
        for col,(x1,x2) in enumerate(xbands):
            block=rownames[row]+", "+colnames[col]+" precinct"
            m.ground(x1,x2,y1,y2,0,block_mats[(row+col)%len(block_mats)],block,"courtyard" if (row+col)%4==0 else "plaza")
            if (row*len(xbands)+col)%7==0:m.poi((x1+x2)//2,(y1+y2)//2,0,block+" public square")
    m.section("THE CROWN CANAL, FIVE BRIDGES AND THE CITY GRID")
    m.ground(55,985,500,540,0,"water1","the Crown Canal","water")
    north_south=[(120,"Tideway"),(300,"Lantern Avenue"),(520,"Founders Road"),(740,"Crown Boulevard"),(920,"Breakwater Drive")]
    east_west=[(120,"South Quay Road"),(300,"Market Street"),(440,"Canal Approach"),(600,"Civic Way"),(760,"Stormglass Avenue"),(920,"Northwall Road")]
    for x,n in north_south:m.street_ns(x,55,985,n)
    for y,n in east_west:m.street_ew(y,55,985,n)
    for x,n in north_south:
        m.ground(x-6,x+6,500,540,3,"bridge",n+" Crown Canal bridge","bridge")
        m.ramp(x-6,x+6,486,499,0,3,n+" south bridge ramp","stone")
        m.ramp(x-6,x+6,541,554,3,0,n+" north bridge ramp","stone")
    m.section("TWENTY-EIGHT COMPLETE CITY INTERIORS")
    buildings=[
      (145,255,155,245,"Saltglass Exchange","office"),(335,455,155,245,"Mariners Clinic","clinic"),(565,685,155,245,"Southwatch Armoury","armoury"),(775,885,155,245,"Ash and Anchor Tavern","bar"),
      (145,255,335,415,"Tideglass Conservatory","hall"),(335,455,335,415,"Aurelia Technical College","office"),(565,685,335,415,"Eastwater Foundry","factory"),(775,885,335,415,"Breakwater Firehouse","base"),
      (145,255,625,715,"Northwall Apartments","apartment"),(335,455,625,715,"Aurelia Library","hall"),(565,685,625,715,"Storm Market","shop"),(775,885,625,715,"Harbour Warehouse","warehouse"),
      (145,255,795,885,"Lantern Opera House","hall"),(335,455,795,885,"Crown Medical Centre","clinic"),(565,685,795,885,"Northwatch Barracks","base"),(775,885,795,885,"Breakwater Hotel","apartment"),
      (145,255,455,490,"West Canal Customs","office"),(335,455,455,490,"Ferrymaster Hall","hall"),(565,685,455,490,"Crown Workshops","factory"),(775,885,455,490,"East Lock Station","control"),
      (145,255,550,585,"Lantern Ferry Terminal","control"),(335,455,550,585,"Canal Archive","office"),(565,685,550,585,"Glassworks Arcade","shop"),(775,885,550,585,"North Lock Exchange","office"),
      (65,105,155,245,"Tideway Signal House","control"),(935,975,155,245,"Eastwater Lifeboat House","store"),(65,105,795,885,"Lantern Gatehouse","base"),(935,975,795,885,"Northwall Weather Station","control")]
    for x1,x2,y1,y2,n,k in buildings:m.room(x1,x2,y1,y2,0,12,n,"tile1","wallbrick",k,"S" if y1<500 else "N")
    m.section("RAISED CIVIC LANDMARKS")
    m.ground(460,580,365,425,5,"stone","the elevated Founders Memorial","plaza"); m.ramp(490,550,345,364,0,5,"Founders Memorial south ramp","stone"); m.poi(520,395,5,"Founders Memorial")
    m.ground(460,580,815,875,4,"stone","the Beacon Court","courtyard"); m.ramp(490,550,795,814,0,4,"Beacon Court south ramp","stone"); m.poi(520,845,4,"Beacon Court")
    for x1,x2,y1,y2,n in districts:m.ispawn(x1,x2,y1,y2,0,LOOT)
    m.poi(520,580,0,"New Aurelia central deploy point"); return m


def coruscant():
    # 1280 square is exactly four times the old 640-square footprint. Four
    # complete levels replace the old broad deck fallbacks with 144 individually
    # named and materially varied precincts.
    m=Map("habitat_alpha",1280,1280,620); m.section("FOUR COMPLETE CORUSCANT CITY LEVELS")
    levels=[("Undercity Foundations",0),("Works Level",120),("Civic Level",300),("Sky Level",500)]
    roads=[160,400,640,880,1120]
    plots=[(40,145),(175,385),(415,625),(655,865),(895,1105),(1135,1240)]
    coverage=[(40,239),(240,439),(440,639),(640,839),(840,1039),(1040,1240)]
    level_data=[
      (["Ash","Pylon","Cinder","Drain","Vault","Shadow"],["Reach","Ward","Conduit","Basin","Maze","Shelf"],["reclamation depot","pressure station","salvage hall","coolant works","shelter clinic","power vault"],"rocks1","wallstone"),
      (["Furnace","Droid","Turbine","Freight","Reactor","Foundry"],["Works","Exchange","Yard","Concourse","Sector","Annex"],["droid foundry","machine hall","freight office","reactor control","workers clinic","tool exchange"],"metal4","wallmetal"),
      (["Archive","Judicial","Senate","Monument","Embassy","Republic"],["Quarter","Forum","Promenade","District","Court","Terrace"],["public archive","judicial chamber","civic exchange","security bureau","medical ministry","assembly rotunda"],"concrete2","wallstone"),
      (["Orbital","Diplomatic","Aurora","Celestial","Executive","Skyline"],["Port","Residence","Gallery","Overlook","Spire","Garden"],["orbital customs","diplomatic salon","sky observatory","landing control","aerial clinic","executive gallery"],"metal2","wallmetal")]
    kinds=["factory","control","warehouse","office","clinic","hall"]
    mats=["metal2","stone","tile1","metal4","hardwood","concrete2"]
    for li,(lname,z) in enumerate(levels):
        row_names,col_names,roles,base_mat,wall=level_data[li]
        m.section(lname.upper()+" PRECINCT FABRIC")
        m.tile(40,1240,40,1240,z,z,base_mat)
        for row,(cy1,cy2) in enumerate(coverage):
            for col,(cx1,cx2) in enumerate(coverage):
                x1,x2=plots[col];y1,y2=plots[row]
                precinct=lname+", "+row_names[row]+" "+col_names[col]
                material=mats[(row+col+li)%len(mats)]
                m.ground(cx1,cx2,cy1,cy2,z,material,precinct,"courtyard" if (row+col)%3==0 else "plaza")
                if (row+col)%2==0:
                    role=roles[(row*2+col)%len(roles)]
                    m.room(x1+10,x2-10,y1+10,y2-10,z,14,precinct+" "+role,material,wall,kinds[(row+col+li)%len(kinds)],"S" if row<3 else "N")
                else:
                    rise=2+(row+col)%4; court=precinct+" raised "+("market" if li<2 else "garden" if li==3 else "memorial court")
                    m.ground(x1+18,x2-18,y1+28,y2-18,z+rise,"metal5" if li<2 else "stone",court,"platform")
                    cx=(x1+x2)//2;m.ramp(cx-12,cx+12,y1+8,y1+27,z,z+rise,court+" approach",material);m.poi(cx,(y1+y2)//2,z+rise,court)
        m.section(lname.upper()+" TRANSIT GRID")
        ns_names=["Aurora Spine","Republic Axis","Centax Way","Hydian Avenue","Corellian Causeway"]
        ew_names=["Senate Traverse","Monument Row","Orbital Road","Foundry Cross","Galactic Promenade"]
        for x,n in zip(roads,ns_names):m.street_ns(x,40,1240,lname+", "+n,z)
        for y,n in zip(roads,ew_names):m.street_ew(y,40,1240,lname+", "+n,z)
        m.ground(616,664,616,664,z+5,"metal5",lname+", Republic Axis transit forum","platform")
        m.ramp(628,652,591,615,z,z+5,lname+", forum south approach","metal4");m.ramp(628,652,665,689,z+5,z,lname+", forum north approach","metal4")
        m.ispawn(40,1240,40,1240,z,LOOT);m.src(40,1240,40,1240,z,z+8,"city.ogg",-22)
    m.section("REPUBLIC AXIS GRAND TURBOLIFT")
    m.turbolift(632,648,600,616,0,500,"Republic Axis grand turbolift",levels)
    for n,z in levels:m.portal(632,648,600,600,z,z+5,n+" turbolift doors")
    m.poi(640,640,305,"Coruscant Civic Level deploy point"); return m


def freya():
    # Five broad tiers and a multi-chamber undercroft provide over three times
    # the former authored footprint while preserving deliberate vertical travel.
    m=Map("freyas_ascent",1000,1200,140); m.section("GREATER FREYA VALLEY")
    m.tile(0,1000,0,1200,0,0,"grass3"); m.src(0,1000,0,1200,0,8,"forest.ogg",-18)
    wilderness=[
      (0,329,0,299,"southwestern birch foothills","grass2"),(330,669,0,299,"southern Freya meadow","grass3"),(670,1000,0,299,"southeastern hunter woods","forest"),
      (0,329,300,599,"western pine ravines","forest"),(330,669,300,599,"Pinewatch lower slopes","dirt"),(670,1000,300,599,"eastern granite shelf","rocks1"),
      (0,329,600,899,"western shield woods","forest"),(330,669,600,899,"Shieldmaiden high meadow","grass2"),(670,1000,600,899,"Valkyrie eastern crags","rocks1"),
      (0,329,900,1200,"northwestern snow line","snow"),(330,669,900,1200,"Citadel crown slopes","stone"),(670,1000,900,1200,"northeastern wind ridge","snow")]
    for x1,x2,y1,y2,n,mat in wilderness:m.ground(x1,x2,y1,y2,0,mat,n,"forest" if "wood" in n or "pine" in n else "field");m.poi((x1+x2)//2,(y1+y2)//2,0,n)
    m.section("THE FIVE ASCENDING SETTLEMENTS")
    terraces=[(60,940,60,250,0,"Lower Settlement"),(90,910,300,490,8,"Pinewatch Terrace"),(120,880,540,730,16,"Shieldmaiden Terrace"),(150,850,780,970,24,"Valkyrie Terrace"),(190,810,1020,1170,32,"Freya Citadel")]
    building_roles=[("western lodge","house","hardwood","wallwood"),("craft hall","factory","stone","wallstone"),("assembly hall","hall","hardwood","wallstone"),("provision house","store","stone","wallstone"),("eastern guard house","base","stone","wallstone")]
    for i,(x1,x2,y1,y2,z,name) in enumerate(terraces):
        m.ground(x1,x2,y1,y2,z,"stone",name,"courtyard"); m.poi((x1+x2)//2,(y1+y2)//2,z,name)
        sector_width=(x2-x1+1)//5
        sector_names=["western homesteads","craft quarter","gathering green","provision quarter","eastern watch"]
        sector_mats=["hardwood2","stone","grass2","tile2","rocks1"]
        for sector in range(5):
            sx1=x1+sector*sector_width;sx2=x2 if sector==4 else sx1+sector_width-1
            m.ground(sx1,sx2,y1,y2,z,sector_mats[sector],name+", "+sector_names[sector],"courtyard")
        m.street_ew((y1+y2)//2,x1,x2,name+" high street",z)
        if i:
            prev=terraces[i-1]
            m.ramp(460,540,prev[3]+1,y1-1,prev[4],z,name+" grand ascent","stone")
            m.ramp(760,800,prev[3]+1,y1-1,prev[4],z,name+" eastern trail","rocks1")
        plots=[(x1+20,x1+135,y1+20,y1+80),(x1+175,x1+300,y1+20,y1+80),((x1+x2)//2-65,(x1+x2)//2+65,y1+105,y2-15),(x2-300,x2-175,y1+20,y1+80),(x2-135,x2-20,y1+20,y1+80)]
        for p,role in zip(plots,building_roles):
            (rx1,rx2,ry1,ry2),(suffix,kind,floor,wall)=p,role
            m.room(rx1,rx2,ry1,ry2,z,12,name+" "+suffix,floor,wall,kind,"S" if ry1<(y1+y2)//2 else "N")
        m.ispawn(x1,x2,y1,y2,z,LOOT)
    m.section("ROOTVAULT CAVERN NETWORK")
    chambers=[(170,390,410,525,"Rootvault western grotto"),(410,590,410,525,"Rootvault great chamber"),(610,830,410,525,"Rootvault eastern grotto"),(260,460,570,690,"Rootvault crystal hall"),(540,740,570,690,"Rootvault deep stores")]
    for x1,x2,y1,y2,n in chambers:
        m.tile(x1,x2,y1,y2,-16,-16,"rocks1"); m.zone(x1,x2,y1,y2,-16,-5,n); m.space(x1,x2,y1,y2,-16,-5,n,"rock","cave",True); m.tile(x1,x2,y1,y2,-4,-4,"wallstone"); m.poi((x1+x2)//2,(y1+y2)//2,-16,n)
    passages=[(390,410,455,480,"Rootvault west passage"),(590,610,455,480,"Rootvault east passage"),(350,650,525,570,"Rootvault descending gallery")]
    for x1,x2,y1,y2,n in passages:m.ground(x1,x2,y1,y2,-16,"rocks1",n,"cave");m.space(x1,x2,y1,y2,-16,-5,n,"rock","cave",True)
    m.src(410,590,410,525,-16,-5,"drip.ogg",-16)
    m.ramp(460,540,490,539,8,-16,"the Rootvault descending passage","rocks1"); m.portal(460,540,539,539,-16,8,"the Rootvault cave mouth")
    m.poi(500,125,0,"Freya Valley deploy point"); return m


def battle_royale():
    m=Map("battleroyale",500,500,100);m.section("NAMED COASTAL APPROACHES")
    waters=[(0,249,0,249,"Southwest shoals"),(250,500,0,249,"Southeast tidal reach"),(0,249,250,500,"Northwest reef water"),(250,500,250,500,"Northeast channel")]
    for x1,x2,y1,y2,n in waters:m.ground(x1,x2,y1,y2,0,"water",n,"water")
    m.ground(15,485,15,485,0,"sand","the island beach ring","beach")
    districts=[(35,245,35,245,"Southwest landing quarter","grass2"),(255,465,35,245,"Southeast orchard quarter","grass3"),(35,245,255,465,"Northwest quarry quarter","rocks1"),(255,465,255,465,"Northeast village quarter","dirt")]
    for x1,x2,y1,y2,n,mat in districts:m.ground(x1,x2,y1,y2,0,mat,n,"courtyard")
    m.section("ISLAND ROADS AND INTERIORS")
    for x,n in [(125,"Landing Road"),(250,"Island Spine"),(375,"Orchard Road")]:m.street_ns(x,35,465,n)
    for y,n in [(125,"South Beach Road"),(250,"Ridge Traverse"),(375,"North Village Road")]:m.street_ew(y,35,465,n)
    buildings=[(55,105,55,105,"Coast Guard Store","store"),(145,210,55,105,"Southwest Infirmary","clinic"),(290,355,55,105,"Orchard Supply Hall","store"),(395,445,55,105,"Weather Station","control"),(55,105,290,350,"Quarry Office","office"),(145,210,290,350,"Stonecutters Hall","factory"),(290,355,290,350,"Village Assembly House","hall"),(395,445,290,350,"Northeast Barracks","base"),(55,105,395,445,"Reef Watch House","control"),(145,210,395,445,"Northwest Lodge","house"),(290,355,395,445,"Island Market","shop"),(395,445,395,445,"Channel Clinic","clinic")]
    for x1,x2,y1,y2,n,k in buildings:m.room(x1,x2,y1,y2,0,11,n,"tile1","wallstone",k,"S" if y1<250 else "N")
    m.ground(185,315,180,320,6,"stone","Crown Ridge","plaza");m.ramp(225,275,155,179,0,6,"Crown Ridge south path","rocks1");m.ramp(225,275,321,345,6,0,"Crown Ridge north path","rocks1");m.poi(250,250,6,"Crown Ridge lookout")
    for x1,x2,y1,y2,n,mat in districts:m.ispawn(x1,x2,y1,y2,0,LOOT)
    return m


if __name__ == "__main__":
    outputs=[(shattersea(),MAPS/"battlegrounds"/"main.map"),(coruscant(),MAPS/"habitat_alpha"/"habitat_alpha.map"),(freya(),MAPS/"freyas_ascent"/"freyas_ascent.map"),(battle_royale(),MAPS/"battleroyale"/"battleroyale.map")]
    for m,path in outputs:m.write(path);print(f"{path.relative_to(ROOT)}: {len(m.lines)} entirely new records")
