"""Check actual bindings, decoded audio, payload variety and import provenance."""
from __future__ import annotations

import array
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from content_sound_contract import content_references, properties
from repair_content_audio import plan, REVOICE

sounds = ROOT / "sounds"
failures = []


def check(ok, label):
    if not ok:
        failures.append(label)


check(subprocess.run([sys.executable, str(ROOT / "tools/audit_sounds.py")], capture_output=True).returncode == 0,
      "weapon, map, fixture, item and companion sound coverage")
for owner, name in content_references(ROOT):
    check((sounds / name).is_file(), owner+" -> "+name)

planned = plan()
for relative, bindings in planned["bindings"].items():
    actual = properties(ROOT / relative)
    for key, value in bindings.items():
        check(actual.get(key) == value, relative+": unconnected "+key)

manifest_path = sounds / "CONTENT_AUDIO_REPAIR.json"
check(manifest_path.is_file(), "missing repair provenance; run tools/repair_content_audio.py")
manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"jobs": []}
manifest_jobs = {job["destination"]: job for job in manifest["jobs"]}
decoded = {}
means = {}
for job in planned["jobs"]:
    name = job["destination"]
    asset = sounds / name
    if not asset.is_file():
        check(False, "missing imported sound "+name)
        continue
    provenance = manifest_jobs.get(name, {})
    check(provenance.get("sha256") == hashlib.sha256(asset.read_bytes()).hexdigest(), "stale sound provenance "+name)
    check(provenance.get("sources") == job["sources"] and provenance.get("operation") == job["operation"], "stale source recipe "+name)
    result = subprocess.run(["ffmpeg", "-v", "error", "-i", str(asset), "-ac", "1", "-ar", "24000", "-f", "f32le", "-"], capture_output=True)
    check(result.returncode == 0 and bool(result.stdout), "audio cannot decode "+name)
    samples = array.array("f", result.stdout)
    if not samples:
        continue
    peak = max(abs(s) for s in samples)
    rms = math.sqrt(sum(s*s for s in samples) / len(samples))
    check(all(math.isfinite(s) for s in samples) and rms>0.00001, "silent/invalid waveform "+name)
    check(peak<0.96, "clipped or insufficient peak headroom "+name)
    duration = len(samples)/24000
    means[name] = 20*math.log10(max(rms, 1e-12))
    decoded[name] = hashlib.sha256(result.stdout).hexdigest()
    if job["operation"] == "loop":
        check(1.29<=duration<=1.31, "wrong loop duration "+name)
        check(abs(samples[0]-samples[-1])<0.08, "audible discontinuity at loop seam "+name)

# The close payload is what distinguishes one grenade from another. Sharing
# a physically equivalent pin pull, cloth swish or distant foley is intentional.
close_names = [item+"_audio_explosion.ogg" for item in REVOICE]
close_hashes = [decoded.get(name) for name in close_names]
check(None not in close_hashes and len(set(close_hashes))==len(close_names), "revoiced grenades still share decoded close detonations")
for item in REVOICE:
    close = means.get(item+"_audio_explosion.ogg", -100)
    loop = means.get(item+"_audio_flight_loop.ogg", -100)
    check(loop<close-5, "flight cue masks detonation "+item)
check(decoded.get("executioners_rage/weapons/drones/auto_hover_drone_repaired/fly.wav") != decoded.get("executioners_rage/weapons/drones/bomber_hover_drone_repaired/fly.wav"), "drones still share flight audio")
client = (ROOT / "includes/item_mechanics.nvgt").read_text(encoding="utf-8")
server = (ROOT / "iwserver/includes/companions.nvgt").read_text(encoding="utf-8")
check('p.play_stationary(grenade_pin_audio(item)' in client, "pin_sound does not reach playback")
check('c.sound+"/activate"' in server and 'c.sound+"/fly"' in server and 'c.sound+"/impact"' in server, "companion audio folder is not used by playback")
for failure in failures:
    print("FAIL", failure)
print(f"{'FAIL' if failures else 'PASS'} content audio: {len(planned['jobs'])} decoded imports, {len(REVOICE)} distinct grenade detonations, {len(planned['bindings'])} connected content entries")
raise SystemExit(bool(failures))
