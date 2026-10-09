"""Validate new receiver identities, source recipes and decoded report levels."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import array
import hashlib
import json
import math
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def properties(path):
    return dict(line.split('=',1) for line in path.read_text(encoding='utf-8-sig').splitlines() if '=' in line)

weapons={p.stem:(p,properties(p)) for p in (ROOT/'iwserver/content/weapons').rglob('*.wpn')}
catalogue=json.loads((ROOT/'tools/expanded_arsenal.json').read_text(encoding='utf-8'))
recipes=json.loads((ROOT/'tools/expanded_arsenal_audio.json').read_text(encoding='utf-8'))['jobs']
receipts={j['destination']:j for j in json.loads((ROOT/'sounds/EXPANDED_ARSENAL_AUDIO.json').read_text(encoding='utf-8'))['jobs']}
names={}
for wid,(path,p) in weapons.items():
    folded=p['name'].casefold()
    assert folded not in names, f'Duplicate inventory label: {wid} and {names.get(folded)}'
    names[folded]=wid
for r in json.loads((ROOT/'tools/weapon_receiver_renames.json').read_text(encoding='utf-8')):
    assert r['old_id'] not in weapons and not (ROOT/r['old_path']).exists(), r
    assert weapons[r['id']][1]['name']==r['name'], r
    offer=properties(ROOT/'iwserver/content/marketplace/weapons'/f"{r['id']}.offer")
    assert offer['item']==r['id'] and offer['name']==r['name'], r
assert len(catalogue['weapons'])==197
for r in catalogue['weapons']:
    assert r['id'] in weapons and weapons[r['id']][1]['name']==r['name'], r['id']
    p=weapons[r['id']][1]
    assert p['sound_profile']==r['id'] and p['class_modes']=='false', r['id']
    owned=[j for j in recipes if j['destination'].startswith(r['id'])]
    assert any(s.startswith(r['library']+':'+r['bank']) for j in owned for s in j['sources']), r['id']
    if p['melee']=='false':
        reserve=ROOT/'iwserver/content/items/ammo'/f"{p['reserve_item']}.item"
        assert reserve.is_file() and properties(reserve)['category']=='Ammo', r['id']
for j in recipes:
    path=ROOT/'sounds'/j['destination']
    assert path.is_file(), path
    receipt=receipts[j['destination']]
    assert all(receipt[k]==v for k,v in j.items()), path
    assert receipt['sha256']==hashlib.sha256(path.read_bytes()).hexdigest(), path
    for source in j['sources']:
        lib,relative=source.split(':',1)
        assert (Path(catalogue['libraries'][lib])/relative).is_file(), source

def level(path,enforce_headroom=True):
    result=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True)
    assert result.returncode==0 and result.stdout, path
    samples=array.array('f',result.stdout)
    assert all(math.isfinite(v) for v in samples),path
    peak=max(abs(v) for v in samples)
    rms=math.sqrt(sum(v*v for v in samples)/len(samples))
    assert (not enforce_headroom or peak<.96) and rms>.00001,(path,peak,rms)
    return 20*math.log10(rms)

reports=[ROOT/'sounds'/j['destination'] for j in recipes if j['role']=='fire']
with ThreadPoolExecutor(max_workers=8) as pool:
    levels=list(pool.map(level,reports))
baseline=level(ROOT/'sounds/AK47fire1.ogg',False)
assert abs(sum(levels)/len(levels)-baseline)<8,(baseline,sum(levels)/len(levels))
print(f'PASS expanded arsenal: 197 weapons, 40 renamed receivers, {len(recipes)} hashed cues, {len(reports)} decoded reports; mean {sum(levels)/len(levels):.1f} dBFS versus existing rifle {baseline:.1f} dBFS')
