"""Rasterized collision/connectivity checks, not just rectangle-union coverage.

Checks the emitted map files, including ordered air carving, headroom,
destructible components, all spawns, landmarks, room access and service access.
"""
from collections import deque
from math import ceil, floor
from pathlib import Path
import json
import re
ROOT=Path(__file__).resolve().parents[1]
MAPS=ROOT/'iwserver/content/maps'
FILES=['battlegrounds/main.map','freyas_ascent/freyas_ascent.map','habitat_alpha/habitat_alpha.map','freeforall/freeforall.map']

def validate(relative):
    lines=(MAPS/relative).read_text(encoding='utf-8').splitlines()
    records=[s.split(':') for s in lines if s and not s.startswith('//')]
    size={p[0]:int(p[1])+1 for p in records if p[0] in ('maxx','maxy','maxz')}
    w,h,depth=size['maxx'],size['maxy'],size['maxz'];area=w*h
    grid=[bytearray(area) for _ in range(depth)]
    named=[bytearray(area) for _ in range(depth)]
    surfaces={};objects={};spawns=[];pois=[];fixtures=[];doors=[];errors=[]
    def paint(target,bounds,value):
        a,b,c,d,e,f=map(float,bounds)
        a,b,c,d,e,f=ceil(a),floor(b),ceil(c),floor(d),ceil(e),floor(f)
        if not (0<=a<=b<w and 0<=c<=d<h and 0<=e<=f<depth):
            if a>b or c>d or e>f:return
            errors.append(f'Out-of-bounds rectangle {bounds}');return
        stripe=bytes([value])*(b-a+1)
        for z in range(e,f+1):
            for y in range(c,d+1):target[z][y*w+a:y*w+b+1]=stripe
    registered=set(re.findall(r'content_register\("([^"\n]+)"',(ROOT/'includes/content_database.nvgt').read_text(encoding='utf-8')))
    for weapon in (ROOT/'iwserver/content/weapons').rglob('*.wpn'):
        registered.update(re.findall(r'^reserve_item=(.+)$',weapon.read_text(encoding='utf-8'),re.M))
    for p in records:
        kind=p[0]
        if kind=='tile':
            material=p[7];surfaces[material]=True
            value=0 if material=='blank' else (2 if 'wall' in material or material in ('glass','tree') else 1)
            paint(grid,p[1:7],value)
        elif kind=='zone':paint(named,p[1:7],1)
        elif kind=='object':
            assert int(p[1]) not in objects,'Duplicate object ID'
            objects[int(p[1])]=p
            for sound in p[5:7]:
                path=ROOT/'sounds'/sound
                if not path.suffix:path=path.with_suffix('.ogg')
                if not path.is_file():errors.append(f'Missing object sound {path}')
        elif kind=='spawn':spawns.append(tuple(map(int,p[1:4])))
        elif kind=='poi':pois.append((*map(int,p[1:4]),p[4]))
        elif kind=='fixture':fixtures.append((*map(int,p[2:5]),p[5]))
        elif kind=='portal':doors.append(p)
    # Runtime overlays are evaluated solid-first per object, then surfaces.
    parts=[p for p in records if p[0]=='objectpart']
    for solid in ('0','1'):
        for p in parts:
            if int(p[1]) not in objects:errors.append('Orphan objectpart '+p[1])
            if p[9]==solid:paint(grid,p[2:8],2 if solid=='1' else 1)
    def walkable(x,y,z):
        if not(0<=x<w and 0<=y<h and 0<=z<depth-2):return False
        i=y*w+x
        return grid[z][i]==1 and grid[z+1][i]==0 and grid[z+2][i]==0
    assert len(spawns)>=12,relative+' requires twelve authored spawns'
    for pos in spawns:
        if not walkable(*pos):errors.append(f'Unsafe spawn {pos}')
    # Flood actual foot positions with one-unit stair/ramp transitions.
    seen=[bytearray(area) for _ in range(depth)]
    valid=[p for p in spawns if walkable(*p)]
    queue=deque(valid[:1])
    if queue:
        x,y,z=queue[0];seen[z][y*w+x]=1
    while queue:
        x,y,z=queue.popleft()
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if not(0<nx<w-1 and 0<ny<h-1):continue
            i=ny*w+nx
            for nz in (z,z+1,z-1):
                if nz<0 or nz>=depth-2 or seen[nz][i] or not walkable(nx,ny,nz):continue
                seen[nz][i]=1;queue.append((nx,ny,nz));break
    for x,y,z in spawns:
        if not seen[z][y*w+x]:errors.append(f'Disconnected spawn {(x,y,z)}')
    for x,y,z,name in pois:
        if not walkable(x,y,z):errors.append(f'Blocked POI {name} {(x,y,z)}')
        elif not seen[z][y*w+x]:errors.append(f'Unreachable POI {name} {(x,y,z)}')
    for x,y,z,name in fixtures:
        if not walkable(x,y,z):errors.append(f'Blocked fixture {name} {(x,y,z)}')
        if not any(0<=x+dx<w and 0<=y+dy<h and seen[z][(y+dy)*w+x+dx] for dx,dy in ((-2,0),(2,0),(0,-2),(0,2))):errors.append(f'Unreachable fixture {name}')
    for p in doors:
        a,b,c,d,e,f=map(int,p[1:7]);x,y=(a+b)//2,(c+d)//2
        if not walkable(x,y,e):errors.append(f'Blocked doorway {p[7]} {(x,y,e)}')
        elif not seen[e][y*w+x]:errors.append(f'Unreachable doorway {p[7]} {(x,y,e)}')
    unnamed=sum(1 for z in range(depth) for i,value in enumerate(seen[z]) if value and not named[z][i])
    if unnamed:errors.append(f'{unnamed} reachable floor positions without zones')
    for p in records:
        if p[0]=='ispawn':
            pos=(int(p[1]),int(p[3]),int(p[5]))
            if not walkable(*pos):errors.append(f'Unsafe loot spawn {pos}')
            for item in p[9:]:
                if item not in registered:errors.append(f'Unknown loot item {item}')
        elif p[0]=='fixture':
            if not (ROOT/'sounds/executioners_rage/environment/objects'/p[1]).is_dir():errors.append(f'Unknown service type {p[1]}')
    print(f'{relative}: {len(pois)} landmarks, {len(objects)} objects, {len(fixtures)} services, {sum(map(sum,seen))} connected floor positions')
    for error in errors:print('  ERROR:',error)
    return errors

if __name__=='__main__':
    errors=[]
    for filename in FILES:errors.extend(validate(filename))
    raise SystemExit(bool(errors))
