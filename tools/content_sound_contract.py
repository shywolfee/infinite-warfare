"""Resolve content audio as the game does, including defaults and ER paths."""
from __future__ import annotations

import re
from pathlib import Path


def properties(path):
    return dict(line.split("=", 1) for line in path.read_text(encoding="utf-8-sig").splitlines() if "=" in line and not line.startswith("#"))


def audio_file(value):
    return value if Path(value).suffix.lower() in {".ogg", ".wav", ".mp3", ".flac"} else value + ".ogg"


def world_effect(value):
    match = re.search(r"#(\d+)$", value)
    variants = [value[:match.start()] + str(i) for i in range(1, int(match[1])+1)] if match else [value]
    return ["executioners_rage/" + variant + ".wav" for variant in variants]


def content_references(root):
    for path in sorted((root / "iwserver/content/items").rglob("*.item")):
        props = properties(path)
        prefix = props.get("sound_prefix", path.stem)
        flight = props.get("thrown") == "true" or props.get("launched") == "true"
        deployed = props.get("deployable") == "true"
        defaults = {}
        if flight:
            defaults.update(throw_sound=prefix+"_throw", bounce_sound=prefix+"_bounce",
                            landing_sound=props.get("bounce_sound", prefix+"_bounce"),
                            flight_loop=prefix+"_flight_loop.ogg")
        if flight or deployed:
            defaults.update(explosion_sound=prefix+"_explode", distant_sound=prefix+"_dist.ogg")
        if deployed:
            defaults["place_sound"] = prefix + "_place"
        for key, value in {**defaults, **props}.items():
            if not value:
                continue
            if key in {"gadget_sound", "provision_sound", "provision_sound2"}:
                for name in world_effect(value):
                    yield str(path.relative_to(root))+":"+key, name
            elif key in {"pin_sound", "throw_sound", "bounce_sound", "landing_sound", "explosion_sound",
                         "distant_sound", "flight_loop", "place_sound", "countdown_sound", "trigger_sound",
                         "detonate_sound", "hit_sound"}:
                yield str(path.relative_to(root))+":"+key, audio_file(value)
        if props.get("use_kind") == "companion":
            if props.get("companion_kind") == "chimp":
                family = "animals/chimpanzee"
                sounds = [f"phrases/vocal{i}" for i in range(1, 5)] + [f"phrases/attack{i}" for i in range(1, 6)] + [f"combat/impact{i}" for i in range(1, 4)]
            else:
                family = props.get("companion_sound", "weapons/drones/" + path.stem)
                sounds = ["activate", "fly"] + [f"impact{i}" for i in range(1, 4)]
            for suffix in sounds:
                yield str(path.relative_to(root))+":companion", world_effect(family+"/"+suffix)[0]
    for path in sorted((root / "iwserver/content/weapons").rglob("*.wpn")):
        for key, value in properties(path).items():
            if value and key in {"projectile_loop", "explosion_sound", "explosion_distant", "explosion_impact"}:
                yield str(path.relative_to(root))+":"+key, audio_file(value)
    for path in sorted((root / "iwserver/content/objects").rglob("*.object")):
        props = properties(path)
        folder = props.get("sound", "")
        if not folder:
            continue
        keys = {"contact_sound": props.get("contact_sound", "collide")}
        if float(props.get("health", "0")) > 0:
            keys["destroy_sound"] = props.get("destroy_sound", "dest")
        for key, value in keys.items():
            if value:
                yield str(path.relative_to(root))+":"+key, world_effect(folder+"/"+value)[0]
        for i in range(1, int(props.get("impact_sounds", "0"))+1):
            yield str(path.relative_to(root))+":impact", world_effect(folder+"/impact"+str(i))[0]
        for key in ("explode_sound", "explode_distant"):
            if props.get(key):
                yield str(path.relative_to(root))+":"+key, audio_file(props[key])
