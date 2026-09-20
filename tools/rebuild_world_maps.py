"""Canonical world builder. No geometry from the superseded maps is imported.

Run from any directory with Python 3. Preset components are baked into map data
so clients and servers use exactly the same shapes and destruction IDs.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAPS=ROOT/'iwserver/content/maps'
PRESETS=json.loads((ROOT/'iwserver/content/object_presets.json').read_text(encoding='utf-8'))
LOOT=['cleaning_patches','9x19mm_17_round_magazine','5.56mm_stanag_magazine','er_small_credit_chip']

class Map:
    def __init__(self,name,width,depth,height=80):
        self.name,self.width,self.depth=name,width,depth
        self.lines=[f'mapname:{name}',f'maxx:{width}',f'maxy:{depth}',f'maxz:{height}','fixtures:authored']
        self.object_count=0;self.doors=[]
    def emit(self,kind,*args):self.lines.append(':'.join(map(str,(kind,*args))))
    def tile(self,x1,x2,y1,y2,z1,z2,material):self.emit('tile',x1,x2,y1,y2,z1,z2,material)
    def zone(self,x1,x2,y1,y2,z1,z2,name):self.emit('zone',x1,x2,y1,y2,z1,z2,name)
    def ground(self,rect,name,material='stone',z=0):
        if z:self.tile(*rect,0,z-1,'wallstone')
        self.tile(*rect,z,z,material);self.zone(*rect,z,z+7,name)
        self.emit('openspace',*rect,z,z+7,name,material,'open')
    def poi(self,x,y,z,name):self.emit('poi',x,y,z,name)
    def spawn(self,x,y,z=0):self.emit('spawn',x,y,z)
    def loot(self,x,y,z=0):self.emit('ispawn',x,x,y,y,z,z,45000,3,*LOOT)
    def fixture(self,kind,x,y,z,name):self.emit('fixture',kind,x,y,z,name)
    def object(self,preset,x,y,z,name,w=4,d=2,h=2,turn=0):
        self.object_count+=1;p=PRESETS[preset];oid=self.object_count
        self.emit('object',oid,p['health'],p['bullet'],p['blast'],p['hit'],p['break'],name)
        for a,b,c,e,f,g,mat,solid in p['parts']:
            if turn%4==1:a,b,c,e=1-e,1-c,a,b
            elif turn%4==2:a,b,c,e=1-b,1-a,1-e,1-c
            elif turn%4==3:a,b,c,e=c,e,1-b,1-a
            coords=[round(x+a*w,3),round(x+b*w,3),round(y+c*d,3),round(y+e*d,3),round(z+f*h,3),round(z+g*h,3)]
            self.emit('objectpart',oid,*coords,mat,solid)
    def room(self,r,z,name,floor='tile1',height=6,wall='wallbrick'):
        a,b,c,d=r
        self.tile(*r,z,z+height,'blank');self.tile(*r,z,z,floor)
        self.tile(a,a,c,d,z,z+height-1,wall);self.tile(b,b,c,d,z,z+height-1,wall)
        self.tile(a,b,c,c,z,z+height-1,wall);self.tile(a,b,d,d,z,z+height-1,wall)
        self.tile(*r,z+height,z+height,'concrete5')
        self.zone(a+1,b-1,c+1,d-1,z,z+height-1,name)
        self.emit('space',a+1,b-1,c+1,d-1,z,z+height-1,name,wall.removeprefix('wall'),'room')
        self.zone(*r,z+height,z+height+4,name+' roof');self.poi(a+3,c+3,z,name)
    def door(self,x1,x2,y1,y2,z,name,floor='tile1'):self.doors.append((x1,x2,y1,y2,z,name,floor))
    def path(self,r,name,mat='gravel',z=0):self.ground(r,name,mat,z)
    def ramp(self,r,low,high,name,mat='stone',axis='y'):
        a,b,c,d=r;length=d-c if axis=='y' else b-a
        assert length>=abs(high-low),name
        for step in range(length+1):
            z=round(low+(high-low)*step/length)
            r1=(a,b,c+step,c+step) if axis=='y' else (a+step,a+step,c,d)
            if z>0:self.tile(*r1,0,z-1,'wallstone')
            self.tile(*r1,z,z,mat)
        self.zone(*r,min(low,high),max(low,high)+5,name)
        self.emit('openspace',*r,min(low,high),max(low,high)+5,name,mat,'platform')
    def finish(self):
        for a,b,c,d,z,name,floor in self.doors:
            self.tile(a,b,c,d,z,z+3,'blank');self.tile(a,b,c,d,z,z,floor)
            self.zone(a,b,c,d,z,z+3,name);self.emit('portal',a,b,c,d,z,z+3,name,'opening')
        self.tile(0,0,0,self.depth,0,80,'wallstone');self.tile(self.width,self.width,0,self.depth,0,80,'wallstone')
        self.tile(0,self.width,0,0,0,80,'wallstone');self.tile(0,self.width,self.depth,self.depth,0,80,'wallstone')
        return self
    def write(self,path):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('\n'.join(self.lines)+'\n',encoding='utf-8',newline='\n')

def worlds():
    from world_layouts import shattersea,freya,coruscant,ghost_town
    return {'battlegrounds/main.map':shattersea(Map),'freyas_ascent/freyas_ascent.map':freya(Map),'habitat_alpha/habitat_alpha.map':coruscant(Map),'freeforall/freeforall.map':ghost_town(Map)}

if __name__=='__main__':
    for filename,m in worlds().items():
        m.write(MAPS/filename)
        print(f'{filename}: {len(m.lines)} records, {m.object_count} destructible objects')
