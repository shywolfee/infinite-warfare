"""Validate shipped Markdown structure and compatibility filenames."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
topics = sorted((ROOT / "iwserver/docs").glob("*.txt"))
documents = topics + [ROOT / "player_manual.md", ROOT / "rules.txt",
                      ROOT / "iwserver/content/items/README.txt",
                      ROOT / "iwserver/content/objects/README.txt"]
assert len(topics) >= 33, "served documentation topics are missing"
for path in documents:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].startswith("# "), f"{path}: missing Markdown title"
    assert len(lines) > 2 and lines[1] == "", f"{path}: title needs a blank line"
    for index, line in enumerate(lines):
        if re.match(r"^#{1,6} ", line):
            assert index == 0 or lines[index - 1] == "", f"{path}:{index + 1}: heading needs preceding blank line"
            assert index + 1 == len(lines) or lines[index + 1] == "", f"{path}:{index + 1}: heading needs following blank line"
    assert "<table" not in text and "<h1" not in text, f"{path}: unconverted HTML"

changes = (ROOT / "changes.txt").read_text(encoding="utf-8")
assert changes.startswith("# Infinite Warfare release notes\n\n")
assert "## New in 0.5.9.2, build 102 (2026-10-08)\n\n- " in changes
assert "## Hotfix for 0.5.7" in changes, "historical hotfix grouping lost"
assert not re.search(r"^(?:New in |Hotfix for )", changes, re.M)
manual = (ROOT / "player_manual.md").read_text(encoding="utf-8")
assert "| Control | Action |\n| --- | --- |" in manual
assert "## 1. Quick start" in manual and "### Dashboard touch gestures" in manual
assert "player_manual.md" in (ROOT / "includes/release_tools.nvgt").read_text(encoding="utf-8")
assert "player_manual.md" in (ROOT / "updater/iw-update.ps1").read_text(encoding="utf-8")
assert "f.add_markdown" in (ROOT / "includes/menu.nvgt").read_text(encoding="utf-8")
print(f"PASS Markdown: {len(topics)} served help topics, manual, rules, schema and release history")
