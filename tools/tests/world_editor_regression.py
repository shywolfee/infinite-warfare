"""Check the map the world editor's builders produce.

client_regression_runner.nvgt runs every builder in the world editor with
its default settings on a blank map and writes the result to
%LOCALAPPDATA%/Temp/IW-editor-test/editor_test.map, with spawn points on
every floor of the building, at the top of the stairs and on the bridge.
This script then checks that map two ways:

  1. the server's own line validator (map_line_check.nvgt), which decides
     whether an editor change is written at all;
  2. the raster validator (tools/validate_maps.py), which floods the
     geometry the way players walk it: doors that open, stairs that climb,
     upper floors and decks that can be reached.

Run the client regression first, then this.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NVGT = Path("C:/nvgt/nvgt.exe")
MAP = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp/IW-editor-test/editor_test.map"


def main():
    if not MAP.is_file():
        print(f"No editor test map at {MAP}; run client_regression_runner.nvgt first.")
        return 2
    report = MAP.with_name("line_check.txt")
    subprocess.run([str(NVGT), str(ROOT / "tools/tests/map_line_check.nvgt"), str(MAP), "editor_test", str(report)],
                   check=False, timeout=120)
    lines = report.read_text(encoding="utf-8") if report.is_file() else "FAILED: no line check report\n"
    print(lines.strip())
    raster = subprocess.run([sys.executable, str(ROOT / "tools/validate_maps.py"), str(MAP)],
                            capture_output=True, text=True, timeout=600)
    print(raster.stdout.strip())
    ok = "WHOLE MAP VALID" in lines and "Refused lines: 0 " in lines and "ERROR" not in raster.stdout and raster.returncode == 0
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
