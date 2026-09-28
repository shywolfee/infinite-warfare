"""Destructible-object presets, one JSON file per editable preset."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRESET_ROOT = ROOT / "iwserver/content/object_presets"
PRESETS = {
    path.stem: json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(PRESET_ROOT.glob("*.json"))
}
