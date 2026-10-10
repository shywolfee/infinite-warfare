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
    assert p['sound_profile']=='ars_'+r['id'] and p['class_modes']=='false', r['id']
    owned=[j for j in recipes if j['destination'].startswith(p['sound_profile'])]
    assert any(s.startswith(r['library']+':'+r['bank']) for j in owned for s in j['sources']), r['id']
    assert not r['id'].startswith('ars_'), r['id']
    assert p == {k: str(v) for k, v in r['properties'].items()}, r['id']
    if p['melee']=='false':
        assert not p['reserve_item'].endswith('_reserve'), r['id']
        reserve=ROOT/'iwserver/content/items/ammo'/f"{p['reserve_item']}.item"
        assert reserve.is_file() and properties(reserve)['category']=='Ammo', r['id']
# Exercise compatibility against existing receivers, not just catalogue copies.
expected = {
    'akm_laminate_rifle': '7.62x39mm_30_round_magazine',
    'benelli_m3_super_90': '12_gauge_shell_box',
    'benelli_m1014_joint_service': '12_gauge_shell_box',
    'underboss_heavy_revolver': '.357_magnum_ammo_belt',
    'arcwright_wrist_cannon': 'pulse_cell',
    'dragonheart_pressure_flamer': 'fuel_canister',
    'mercyfield_rescue_crossbow': 'bolt_quiver',
    'butchers_flight_cleaver': 'throwing_blade_quiver',
}
for wid, reserve in expected.items():
    assert weapons[wid][1]['reserve_item'] == reserve, wid
for wid, ammo in {
    'adrenaline_needle_gun': 'medical syringe',
    'bloodline_injector_carbine': 'medical syringe',
    'sunburst_flare_launcher': 'signal flare',
    'ember_signal_launcher': 'signal flare',
    'ravenwood_war_bow': 'hunting arrow',
    'recon_dart_projector': 'recon dart',
    'broadside_ball_cannon': 'cannonball',
}.items():
    assert weapons[wid][1]['ammo_type'] == ammo, wid
containers = {}
for wid, (_, p) in weapons.items():
    if p.get('is_magazine') == 'true' and p.get('ammo_display') != 'fuel':
        containers.setdefault(p['reserve_item'], set()).add(int(p['capacity']))
assert all(len(capacities) == 1 for capacities in containers.values()), containers
assert weapons['dl_44_heavy_blaster'][1]['reserve_item'] != weapons['a180_modular_blaster'][1]['reserve_item']
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
