"""Destructible-object presets, read from the file the server also reads."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRESETS = json.loads((ROOT / "iwserver/content/object_presets.json").read_text(encoding="utf-8"))
