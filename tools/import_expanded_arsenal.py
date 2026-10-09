"""Render the reviewed arsenal recipes from the owner's local sound libraries.

No copyrighted source recordings are committed. Unowned or locally modified
outputs are never overwritten. Interrupted imports resume from hashed receipts.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOUNDS = ROOT / 'sounds'
CATALOGUE = ROOT / 'tools/expanded_arsenal.json'
RECIPES = ROOT / 'tools/expanded_arsenal_audio.json'
RECEIPTS = SOUNDS / 'EXPANDED_ARSENAL_AUDIO.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def resolve(source, libraries):
    library, relative = source.split(':', 1)
    path = libraries[library] / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path

def render(job, output, libraries):
    args = ['ffmpeg', '-v', 'error', '-y', '-threads', '1']
    for source in job['sources']:
        args += ['-i', str(resolve(source, libraries))]
    filters = [f'[{i}:a]aformat=sample_rates=48000:channel_layouts=mono,asetpts=PTS-STARTPTS[s{i}]'
               for i in range(len(job['sources']))]
    inputs = ''.join(f'[s{i}]' for i in range(len(job['sources'])))
    if job['operation'] == 'concat':
        filters.append(inputs+f'concat=n={len(job["sources"])}:v=0:a=1[mix]')
    elif len(job['sources']) > 1:
        filters.append(inputs+f'amix=inputs={len(job["sources"])}:duration=longest:normalize=0[mix]')
    else:
        filters.append('[s0]anull[mix]')
    if job['operation'] == 'pulse':
        filters.append('[mix]atrim=0:0.16,afade=t=out:st=0.13:d=0.03[body]')
    else:
        filters.append('[mix]anull[body]')
    level = -18 if job['role'] in {'fire', 'explosion_sound'} else -22 if job['role'] == 'distant_sound' else -25
    filters.append(f'[body]loudnorm=I={level}:TP=-2:LRA=7,alimiter=limit=0.85:level=false[out]')
    args += ['-filter_complex_threads', '1', '-filter_complex', ';'.join(filters),
             '-map', '[out]', '-ar', '48000', '-c:a', 'libvorbis', '-q:a', '6', str(output)]
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(job['destination']+': '+result.stderr[-1000:])
    checked = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 'null', '-'], capture_output=True)
    if checked.returncode or output.stat().st_size < 100:
        raise RuntimeError('Invalid rendered audio: '+job['destination'])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--refresh', action='store_true', help='rebuild changed recipes only, and only for unchanged owned outputs')
    args = parser.parse_args()
    recipes = json.loads(RECIPES.read_text(encoding='utf-8'))['jobs']
    libraries = {k: Path(v) for k,v in json.loads(CATALOGUE.read_text(encoding='utf-8'))['libraries'].items()}
    if args.plan:
        print(f'{len(recipes)} authored cues; '+', '.join(f'{k}: {v}' for k,v in libraries.items()))
        return
    if not 1 <= args.workers <= 16:
        parser.error('--workers must be between 1 and 16')
    old = json.loads(RECEIPTS.read_text(encoding='utf-8')) if RECEIPTS.exists() else {'jobs': []}
    receipts = {j['destination']: j for j in old['jobs']}
    pending = []
    for job in recipes:
        for source in job['sources']:
            resolve(source, libraries)
        dest = SOUNDS / job['destination']
        if dest.exists():
            owned = receipts.get(job['destination'], {})
            if owned.get('sha256') != digest(dest):
                raise RuntimeError('Refusing to replace unowned, edited or stale audio: '+str(dest))
            if any(owned.get(k) != v for k,v in job.items()):
                if not args.refresh:
                    raise RuntimeError('Recipe changed; use --refresh for '+str(dest))
                pending.append(job)
        else:
            pending.append(job)
    print(f'Resume: {len(recipes)-len(pending)} verified, {len(pending)} to render', flush=True)
    with tempfile.TemporaryDirectory(prefix='IW-arsenal-') as temp, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(render, job, Path(temp)/job['destination'], libraries): job for job in pending}
        for number, future in enumerate(as_completed(futures), 1):
            job = futures[future]
            future.result()
            output = Path(temp)/job['destination']
            output.replace(SOUNDS/job['destination'])
            receipts[job['destination']] = {**job, 'sha256': digest(SOUNDS/job['destination'])}
            receipt_temp = RECEIPTS.with_suffix('.tmp')
            receipt_temp.write_text(json.dumps({'jobs': list(receipts.values())})+'\n', encoding='utf-8')
            receipt_temp.replace(RECEIPTS)
            if number % 25 == 0 or number == len(pending):
                print(f'Rendered {number}/{len(pending)}: {job["destination"]}', flush=True)
    (SOUNDS/'EXPANDED_ARSENAL_AUDIO_FILES.txt').write_text('\n'.join(j['destination'] for j in recipes)+'\n', encoding='utf-8')
    print('All reviewed recordings rendered and decoded successfully.', flush=True)

if __name__ == '__main__':
    main()
